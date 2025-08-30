import importlib
from functools import partial

from ewoksjob import client
from marshmallow import Schema
from marshmallow import ValidationError

from ..import_utils import unavailable_class
from ..import_utils import unavailable_module

try:
    import gevent
except ImportError as ex:
    gevent = unavailable_module(ex)

try:
    from bliss.common import event
except ImportError as ex:
    event = unavailable_module(ex)

try:
    from bliss.config.channels import Cache
except ImportError as ex:
    Cache = unavailable_class(ex)


from ..persistent.parameters import RedisDictWrapper


def _get_active_tasks(worker_queue: str) -> int:
    """Get the number of active tasks for the worker currently consuming `worker_queue`"""
    from celery import current_app

    worker_queues = current_app.control.inspect().active_queues()
    if not worker_queues:
        return 0
    for worker_id, queues in worker_queues.items():
        for queue in queues:
            if queue["name"] == worker_queue:
                break
    inspect = current_app.control.inspect()

    workers = inspect.active()
    if worker_id in workers:
        return len(workers[worker_id])

    return 0


def resolve_dictwrapper(value) -> dict:
    if isinstance(value, RedisDictWrapper):
        return dict(value)
    return value


class DaiquiriProcessor:
    """
    - plugin: bliss
      package: blissoda.daiquiri.bliss_object
      class: DaiquiriProcessor
      name: daiquiri_processor
      processor_package: blissoda.id13.daiquiri_xrpd_processor
      processor_class: DaiquiriXrpdProcessor
      processor_class_options:
        enable_plotter: false
    """

    def _validate(self, field: str, value) -> bool:
        schema = self._processor.parameters_schema()
        schema.load({field: value})

    def __dir__(self):
        return super().__dir__() + list(self._parameters.keys())

    def __getattr__(self, key):
        try:
            value = self.__dict__["_parameters"][key].value
            return resolve_dictwrapper(value)
        except KeyError:
            pass

        return super().__getattr__(key)

    def __setattr__(self, key, value):
        try:
            if key in self._parameters:
                self._validate(key, value)
                setattr(self._processor, key, value)
                self._parameters[key].value = value
                return
        except ValidationError as e:
            raise AttributeError(
                f"Invalid value for `{key}`: `{value}`. {','.join(e.messages[key])}"
            )
        except Exception:
            pass

        return super().__setattr__(key, value)

    def __enabled_changed(self, value):
        event.send(self, "enabled", value)

    def __state_changed(self, value):
        event.send(self, "state", value)

    def _parameter_changed(self, property_key, value):
        event.send(self, property_key, value)

    def _create_callback(self, parameter_key):
        return partial(self._parameter_changed, parameter_key)

    def __init__(self, name, config):
        self.name = name
        processor_package = importlib.import_module(config["processor_package"])
        processor_class = getattr(processor_package, config["processor_class"])
        self._processor = processor_class(**config.get("processor_class_options", {}))

        self._task = gevent.spawn(self._monitor_task)

        self._enabled = Cache(
            self,
            "enabled",
            default_value=self._processor._enabled,
            callback=self.__enabled_changed,
        )

        self._state = Cache(
            self,
            "state",
            default_value="UNKNOWN",
            callback=self.__state_changed,
        )

        schema = self._processor.parameters_schema()
        self._parameters = {}
        self._callbacks = {}
        for parameter_key in schema._declared_fields.keys():
            if parameter_key == "enabled":
                continue
            self._callbacks[parameter_key] = self._create_callback(parameter_key)
            self._parameters[parameter_key] = Cache(
                self,
                parameter_key,
                default_value=resolve_dictwrapper(
                    getattr(self._processor, parameter_key)
                ),
                callback=self._callbacks[parameter_key],
            )

    def __info__(self):
        # Background task failed
        if not self._task:
            self._task.get()

        info_str = "Daiquiri Processor\n"
        info_str += f"  State: {self.state}\n"
        info_str += f"  Enabled: {self.enabled}\n"
        info_str += "  Parameters:\n"
        for param_key, param_value in self._parameters.items():
            info_str += f"    {param_key}: {param_value.value}\n"
        return info_str

    def _monitor_task(self):
        while True:
            workers = client.get_workers()
            online = "OFFLINE"
            if self._processor.queue:
                if self._processor.queue in workers:
                    online = "READY"

                tasks = _get_active_tasks(self._processor.queue)
                if tasks:
                    online = "PROCESSING"
            else:
                if len(workers):
                    online = "READY"

            if online == "READY":
                if not self._enabled.value:
                    online = "DISABLED"

            if online != self._state.value:
                self._state.value = online

            gevent.sleep(5)

    @property
    def state(self):
        return self._state.value

    @property
    def enabled(self):
        return self._enabled.value

    @enabled.setter
    def enabled(self, value):
        if value:
            self._processor.enable()
        else:
            self._processor.disable()
        self._enabled.value = value

    @property
    def parameters_schema(self) -> Schema:
        return self._processor.parameters_schema

    def reprocess(self, kwargs):
        return self._processor.reprocess(kwargs)

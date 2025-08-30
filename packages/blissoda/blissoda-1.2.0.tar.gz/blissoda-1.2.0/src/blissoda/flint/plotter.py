from ..import_utils import unavailable_module
from . import WithFlintAccess

try:
    import gevent
except ImportError as ex:
    gevent = unavailable_module(ex)


class BasePlotter(WithFlintAccess):
    def __init__(self, max_plots) -> None:
        super().__init__()
        self._max_plots = max_plots
        self._tasks = []

    @property
    def number_of_scans(self):
        """Maximum number of scans to be plotted"""
        return self._max_plots

    @number_of_scans.setter
    def number_of_scans(self, value):
        self._max_plots = max(value, 0)

    def handle_workflow_result(self):
        raise NotImplementedError()

    def _spawn(self, *args, **kw):
        task = gevent.spawn(*args, **kw)
        self._tasks.append(task)
        self.purge_tasks()

    def purge_tasks(self) -> int:
        """Remove references to tasks that have finished."""
        self._tasks = [t for t in self._tasks if t]
        return len(self._tasks)

    def kill_tasks(self) -> int:
        """Kill all tasks."""
        gevent.killall(self._tasks)
        return self.purge_tasks()

    def replot(self, **retry_options) -> None:
        raise NotImplementedError()

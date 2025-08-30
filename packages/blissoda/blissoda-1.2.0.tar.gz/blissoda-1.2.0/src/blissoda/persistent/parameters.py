import logging
from collections.abc import MutableMapping
from copy import deepcopy
from dataclasses import dataclass
from itertools import zip_longest
from pprint import pformat
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Union

import numpy

from ..bliss_globals import current_session
from ..import_utils import is_available
from ..utils.deprecate import WithDeprecatedClassAttributes

try:
    from bliss.common.utils import autocomplete_property
except ImportError:
    autocomplete_property = property

_ERROR = None
try:
    from bliss.config.settings import HashObjSetting
except ImportError:
    try:
        from blissdata.settings import HashObjSetting
    except ImportError as ex:
        _ERROR = ex

        class HashObjSetting(MutableMapping):
            def __init__(self, name: str):
                logger.warning(
                    "Persistency is disabled because of this error: %s", _ERROR
                )
                self.__data: Dict[Any, Any] = dict()

            def __getitem__(self, key: Any) -> Any:
                return self.__data[key]

            def __setitem__(self, key: Any, value: Any) -> None:
                self.__data[key] = value

            def __delitem__(self, key: Any) -> None:
                del self.__data[key]

            def __iter__(self) -> Iterator[Any]:
                return iter(self.__data)

            def __len__(self) -> int:
                return len(self.__data)

            def get_all(self) -> dict:
                return deepcopy(self._data)


logger = logging.getLogger(__name__)


@dataclass
class ParameterInfo:
    name: str
    category: str = "parameters"
    hidden: Optional[bool] = None
    doc: Optional[str] = None
    deprecated_names: Optional[List[str]] = None
    validator: Optional[Callable] = None

    def __post_init__(self):
        if self.hidden is None:
            self.hidden = self.name.startswith("_")


class ParameterValue(NamedTuple):
    value: Any
    doc: Optional[str] = None


class WithPersistentParameters(WithDeprecatedClassAttributes):
    """Adds parameters as properties that will be stored in Redis

    .. code:: python

        class MyClass(WithPersistentParameters, parameters=["a", "b"])
            pass

        myobj = MyClass()
        myobj.a = 10
        myobj.b = None  # remove
    """

    _PARAMETERS: Dict[str, ParameterInfo] = dict()
    _HAS_BLISS: bool = is_available(current_session)

    def __init__(self, **defaults) -> None:
        if self._HAS_BLISS:
            session_name = current_session.name
        else:
            session_name = "nosession"
        self._parameters = HashObjSetting(
            f"blissoda:{session_name}:{self.__class__.__name__}"
        )
        self._init_parameters(defaults)

    def _init_parameters(self, defaults: dict) -> None:
        for name, param in self._PARAMETERS.items():
            self._remove_deprecated_parameters(name, param.deprecated_names)
        for name, value in defaults.items():
            if self._get_parameter(name) is None:
                self._set_parameter(name, value)

    def __init_subclass__(
        cls,
        parameters: Optional[List[Union[str, Mapping, ParameterInfo]]] = None,
        **kw,
    ) -> None:
        super().__init_subclass__(**kw)

        parameters = parameters or list()
        new_parameters = list()
        for p in parameters:
            if isinstance(p, str):
                p = ParameterInfo(name=p)
            elif isinstance(p, Mapping):
                p = ParameterInfo(**p)
            new_parameters.append(p)
        new_parameters = {p.name: p for p in new_parameters}

        cls._PARAMETERS = {**cls._PARAMETERS, **new_parameters}

        for name, param in new_parameters.items():
            _add_parameter_property(cls, name, param.validator)
            for deprecated_name in param.deprecated_names or list():
                _add_deprecated_parameter_property(
                    cls, deprecated_name, name, param.validator
                )

    def __dir__(self) -> Iterable[str]:
        return list(super().__dir__()) + [
            name for name, param in self._PARAMETERS.items() if not param.hidden
        ]

    def _info_categories(self) -> Dict[str, dict]:
        categories = dict()
        all_values = self._parameters.get_all()
        for name, param in self._PARAMETERS.items():
            if param.hidden:
                continue
            category = categories.setdefault(param.category, dict())
            value = all_values.get(name, None)
            category[name] = ParameterValue(value=value, doc=param.doc)
        return categories

    def __info__(self) -> str:
        return "\n" + "\n\n".join(
            [
                f"{name.capitalize()}:\n {_format_info_category(category)}"
                for name, category in self._info_categories().items()
                if category
            ]
        )

    def _get_parameter(self, name: str):
        v = self._parameters.get(name)
        if isinstance(v, dict):
            return RedisDictWrapper(name, self._parameters.get, self._set_parameter)
        return v

    def _set_parameter(self, name: str, value):
        if isinstance(value, RemoteDictWrapper):
            value = value.to_dict()
        self._parameters[name] = value

    def _del_parameter(self, name: str):
        self._parameters[name] = None

    def _remove_deprecated_parameters(
        self, name: str, deprecated_names: Optional[List[str]]
    ) -> None:
        if not deprecated_names:
            return

        value = self._parameters.get(name)

        for deprecated_name in deprecated_names:
            deprecated_value = self._parameters.get(deprecated_name)
            if deprecated_value is not None:
                self._del_parameter(deprecated_name)
            if value is None:
                value = deprecated_value
                self._set_parameter(name, value)

    def _raise_when_missing(self, *names):
        for name in names:
            if self._get_parameter(name) is None:
                raise AttributeError(f"parameter '{name}' is not set")


def _add_parameter_property(cls, name: str, validator: Optional[Callable]) -> None:
    """Add a property to a `WithPersistentParameters` instance which sets and
    gets a persistent parameter.
    """
    if hasattr(cls, name):
        return

    def getter(self):
        return self._get_parameter(name)

    method = autocomplete_property(getter)
    setattr(cls, name, method)

    if validator is None:

        def setter(self, value):
            self._set_parameter(name, value)

    elif not callable(validator):
        raise TypeError(f"Validator for {name} is not callable")

    else:

        def setter(self, value):
            validated_value = validator(value)
            self._set_parameter(name, validated_value)

    method = getattr(cls, name).setter(setter)
    setattr(cls, name, method)


def _add_deprecated_parameter_property(
    cls, old_name: str, new_name: str, validator: Optional[Union[type, Callable]]
) -> None:
    """Add a property to a `WithPersistentParameters` instance which sets and
    gets a persistent parameter with a deprecated name.
    """
    if hasattr(cls, old_name):
        return

    def getter(self):
        logger.warning(
            f"'{old_name}' is deprecated and will be removed in a future version. Use '{new_name}' instead."
        )
        return self._get_parameter(new_name)

    method = autocomplete_property(getter)
    setattr(cls, old_name, method)

    if validator is None:

        def setter(self, value):
            logger.warning(
                f"'{old_name}' is deprecated and will be removed in a future version. Use '{new_name}' instead."
            )
            self._set_parameter(new_name, value)

    elif not callable(validator):
        raise TypeError(f"Validator for {old_name} is not callable")

    else:

        def setter(self, value):
            logger.warning(
                f"'{old_name}' is deprecated and will be removed in a future version. Use '{new_name}' instead."
            )
            validated_value = validator(value)
            self._set_parameter(new_name, validated_value)

    method = getattr(cls, old_name).setter(setter)
    setattr(cls, old_name, method)


class RemoteDictWrapper(MutableMapping):
    """Whenever you get, set or delete the value, the entire dictionary is pushed/pull from a remote source"""

    def __dir__(self) -> Iterable[str]:
        return list(super().__dir__()) + list(self)

    def _get_all(self) -> dict:
        raise NotImplementedError

    def _set_all(self, value: Mapping) -> dict:
        raise NotImplementedError

    def to_dict(self) -> dict:
        return self._get_all()

    def __str__(self):
        return str(self._get_all())

    def __repr__(self):
        return repr(self._get_all())

    def __getitem__(self, key: str) -> Any:
        value = self._get_all()[key]
        if isinstance(value, dict):
            value = MemoryDictWrapper(self, key)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        adict = self._get_all()
        if isinstance(value, RemoteDictWrapper):
            value = value.to_dict()
        adict[key] = value
        return self._set_all(adict)

    def __delitem__(self, key: str) -> None:
        adict = self._get_all()
        del adict[key]
        return self._set_all(adict)

    def __iter__(self) -> Iterator[Any]:
        return self._get_all().__iter__()

    def __len__(self) -> int:
        return self._get_all().__len__()


class RedisDictWrapper(RemoteDictWrapper):
    def __init__(self, name: str, getter: Callable, setter: Callable) -> None:
        self._name = name
        self._getter = getter
        self._setter = setter

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_name", "_getter", "_setter"):
            return super().__setattr__(name, value)
        self[name] = value

    def _get_all(self) -> dict:
        adict = self._getter(self._name)
        if adict is None:
            return dict()
        return adict

    def _set_all(self, value: Mapping) -> None:
        self._setter(self._name, value)


class MemoryDictWrapper(RemoteDictWrapper):
    def __init__(self, parent: RemoteDictWrapper, name: str):
        self._parent = parent
        self._name = name

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_name", "_parent"):
            return super().__setattr__(name, value)
        self[name] = value

    def _get_all(self) -> dict:
        return self._parent._get_all()[self._name]

    def _set_all(self, value: Mapping) -> None:
        self._parent[self._name] = value


def _format_info_category(category: Dict) -> str:
    if not category:
        return ""

    rows: List[List[List[str]]] = list()
    for name, pvalue in category.items():
        ldoc = []
        if isinstance(pvalue, ParameterValue):
            value = pvalue.value
            if pvalue.doc:
                ldoc = str(pvalue.doc or "")
                ldoc = [ldoc[i : i + 60] for i in range(0, len(ldoc), 60)]
        else:
            value = pvalue
        lvalue = pformat(value, width=60).split("\n")
        rows.append([[str(name)], lvalue, ldoc])

    lengths = numpy.array(
        [[max(len(s) for s in lines) if lines else 0 for lines in row] for row in rows]
    )
    fmt = "   ".join(["{{:<{}}}".format(n) for n in lengths.max(axis=0)])

    lines = [
        fmt.format(*svalues)
        for row in rows
        for svalues in zip_longest(*row, fillvalue="")
    ]

    return "\n ".join(lines)

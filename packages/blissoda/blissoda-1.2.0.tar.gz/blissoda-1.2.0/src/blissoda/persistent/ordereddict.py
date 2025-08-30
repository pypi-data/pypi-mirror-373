import json
import logging
import pickle
from collections import OrderedDict
from collections.abc import MutableMapping
from copy import deepcopy
from typing import Any
from typing import Dict
from typing import Iterator
from typing import Union

_ERROR = None
try:
    from blissdata.settings import OrderedHashObjSetting
except ImportError:
    try:
        from bliss.config.settings import OrderedHashObjSetting
    except ImportError as ex:
        _ERROR = ex

        class OrderedHashObjSetting(MutableMapping):
            def __init__(self, name: str):
                logger.warning(
                    "Persistency is disabled because of this error: %s", _ERROR
                )
                self.__data: Dict[Any, Any] = OrderedDict()

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


class PersistentOrderedDict(OrderedHashObjSetting):
    def __init__(self, redis_key: str, serializer: str = "json"):
        dumps, loads = _SERIALIZERS[serializer]
        super().__init__(
            redis_key, read_type_conversion=loads, write_type_conversion=dumps
        )


def _json_loads(serialized_value: Union[bytes, Any]) -> Any:
    # Called twice on the same data for bliss<2
    if isinstance(serialized_value, bytes):
        try:
            return json.loads(serialized_value)
        except Exception:
            pass
    return serialized_value


def _pickle_loads(serialized_value: Union[bytes, Any]) -> Any:
    # Called twice on the same data for bliss<2
    if isinstance(serialized_value, bytes):
        try:
            return pickle.loads(serialized_value)
        except Exception:
            pass
    return serialized_value


def _json_dumps(python_value: Any) -> str:
    return json.dumps(python_value)


def _pickle_dumps(python_value: Any) -> bytes:
    return pickle.dumps(python_value)


_SERIALIZERS = {
    "json": (_json_dumps, _json_loads),
    "pickle": (_pickle_dumps, _pickle_loads),
}

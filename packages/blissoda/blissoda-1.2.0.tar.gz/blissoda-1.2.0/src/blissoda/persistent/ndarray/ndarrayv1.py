import pickle
from typing import Dict
from typing import List
from typing import Union

import numpy

from ...import_utils import unavailable_function

try:
    from bliss.config.conductor.client import get_redis_proxy
except ImportError as ex:
    get_redis_proxy = unavailable_function(ex)


class PersistentNdArray:
    def __init__(self, redis_key: str) -> None:
        self._connection = get_redis_proxy(db=0)
        self._name = redis_key

    def append(self, value: numpy.ndarray) -> None:
        self._connection.xadd(self._name, _encode(value[numpy.newaxis, ...]))

    def extend(self, value: numpy.ndarray) -> None:
        self._connection.xadd(self._name, _encode(value))

    def __getitem__(self, idx) -> Union[numpy.ndarray, List[numpy.ndarray]]:
        if idx == 0:
            adict = self._connection.xrange(self._name, count=1)[0][1]
            return _decode(adict)[0]
        if idx == -1:
            adict = self._connection.xrevrange(self._name, count=1)[0][1]
            return _decode(adict)[-1]
        arr = [_decode(adict) for _, adict in self._connection.xrange(self._name)]
        if arr:
            arr = numpy.concatenate(arr)
        else:
            arr = numpy.array([])
        if isinstance(idx, tuple) and not idx:
            return arr
        return arr[idx]

    def remove(self) -> None:
        self._connection.delete(self._name)


def _encode(data: numpy.ndarray) -> Dict[bytes, bytes]:
    return {b"data": pickle.dumps(data)}


def _decode(data: Dict[bytes, bytes]) -> numpy.ndarray:
    return pickle.loads(data[b"data"])

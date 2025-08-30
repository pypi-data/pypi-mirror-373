from typing import List
from typing import Union

import numpy

from ...import_utils import unavailable_class

try:
    from blissdata.data.events.channel import ChannelDataEvent
    from blissdata.streaming import DataStream
except ImportError as ex:
    ChannelDataEvent = unavailable_class(ex)
    DataStream = unavailable_class(ex)


class PersistentNdArray:
    def __init__(self, redis_key: str) -> None:
        self._datastream = DataStream(redis_key)

    def append(self, value: numpy.ndarray) -> None:
        self._datastream.add_event(_encode(value[numpy.newaxis, ...]))

    def extend(self, value: numpy.ndarray) -> None:
        self._datastream.add_event(_encode(value))

    def __getitem__(self, idx) -> Union[numpy.ndarray, List[numpy.ndarray]]:
        if idx == 0:
            events = self._datastream.range(count=1)
            if not events:
                raise IndexError("index out of range")
            adict = events[0][1]
            return _decode(adict)[0]
        if idx == -1:
            events = self._datastream.rev_range(count=1)
            if not events:
                raise IndexError("index out of range")
            adict = events[0][1]
            return _decode(adict)[-1]

        events = self._datastream.range()
        if events:
            event = ChannelDataEvent.merge(events)
            arr = _data_from_event(event)
        else:
            arr = numpy.array([])
        if idx == ():
            return arr
        return arr[idx]

    def remove(self) -> None:
        self._datastream.clear()


def _encode(data: numpy.ndarray) -> ChannelDataEvent:
    desc = {"shape": data.shape[1:], "dtype": data.dtype}
    return ChannelDataEvent(data, desc)


def _decode(data: dict) -> numpy.ndarray:
    event = ChannelDataEvent(raw=data)
    return _data_from_event(event)


def _data_from_event(event: ChannelDataEvent) -> numpy.ndarray:
    if event.npoints == 1:
        return event.data[numpy.newaxis, ...]
    return event.data

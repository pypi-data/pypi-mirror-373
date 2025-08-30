import enum
import logging

import numpy

from . import attenuator

logger = logging.getLogger(__name__)


class BlObject:
    def __init__(self, parent=None):
        self.parent = parent

    def __getattr__(self, name):
        return getattr(self.parent, name)

    @property
    def oyield(self):
        """A value between 0 and 1"""
        return 1

    @property
    def rate(self):
        """Hz"""
        return self.parent.rate * self.oyield


class Source:
    def __init__(self):
        self.rate = 1e7  # Hz

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, value):
        self._rate = value


class Mono(BlObject):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.energy = 70  # keV

    @property
    def position(self):
        return self.energy

    @position.setter
    def position(self, value):
        self.energy = value


class Attenuator(BlObject):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bits = 0

    @property
    def oyield(self):
        return attenuator.SiO2trans(self.energy, self.bits)


class DiffractingSample(BlObject):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.oyield = 1

    @property
    def oyield(self):
        return self._oyield

    @oyield.setter
    def oyield(self, value):
        self._oyield = value


class LimaDetector(BlObject):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.tframe = 0.2  # sec
        self.dynamic_range = 1 << 20
        self.damage_rate = 5e6  # Hz
        self._last_image = None
        self.noise = True
        self.shape = 11, 10

    @property
    def proxy(self) -> "LimaProxy":
        return LimaProxy(self)

    def ct(self, expo_time=1):
        # Devide exposure time in frames
        nframes = expo_time / self.tframe
        expo_left = expo_time - int(nframes) * self.tframe
        nframes = int(nframes)
        frame_times = [self.tframe] * nframes + [expo_left]

        # Generate frames
        frames, fmax, rmax = zip(
            *(self._generate_frame(tframe) for tframe in frame_times)
        )

        # Sum frames
        self._last_image = sum(frames)

        # Warn about exceeding dynamic range
        fmax = sorted(set(fmax) - {None})
        if fmax:
            logger.warning(f"dynamic range exceeded ({fmax[-1]} cts/frame)")

        # Raise error when damaging the detector
        rmax = sorted(set(rmax) - {None})
        if rmax:
            raise RuntimeError(f"detector damaged at {rmax[-1]:e} Hz")

    def _generate_frame(self, tframe):
        # Generate frame
        counts = int(self.rate * tframe + 0.5)
        if self.noise:
            frame = numpy.random.poisson(counts, size=self.shape)
            fmax = frame.max()
        else:
            frame = numpy.full(self.shape, counts)
            fmax = counts
        if tframe:
            rmax = fmax / tframe
        else:
            rmax = 0
        if fmax >= self.dynamic_range:
            frame = numpy.clip(frame, 0, self.dynamic_range - 1)
        else:
            fmax = None
        if rmax <= self.damage_rate:
            rmax = None
        return frame, fmax, rmax

    @property
    def last_image(self):
        return self._last_image


class LimaProxy:
    def __init__(self, detector: LimaDetector) -> None:
        self._detector = detector

    @property
    def last_image(self):
        # proxy attribute
        return self._detector._last_image

    @property
    def video_last_image(self):
        # proxy attribute
        return self._detector._last_image


class _ShutterState(enum.Enum):
    OPEN = "Open"
    CLOSED = "Closed"


class Shutter:
    def __init__(self, **kw):
        super().__init__(**kw)
        self.state = _ShutterState.OPEN

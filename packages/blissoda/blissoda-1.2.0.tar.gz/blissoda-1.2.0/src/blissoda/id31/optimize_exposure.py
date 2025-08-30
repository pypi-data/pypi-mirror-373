r"""Optimize exposure conditions (time and attenuator) based
on a measurement

* $I_m$: measured diffracted intensity (maximum pixel value)
* $I_d$: desired diffracted intensity (maximum pixel value)
* $R$: diffraction count rate (Hz, maximum pixel value per second)
* $T(E,n)$: transmission at energy $E$ and attenuator position $n$

.. math::

    \begin{align}
    I_m &= R * tframe * nframe_m * T(E,n_m) \\
    I_d &= R * tframe * nframe_d * T(E,n_d)
    \end{align}

Solve the following equation to $n_d$ and $nframe_d$

.. math::

    \frac{nframe_d * T(E,n_d)} = \frac{I_d * nframe_m * T(E,n_m)}{I_m}
"""

from contextlib import contextmanager
from functools import lru_cache
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Union

import numpy

from ..bliss_globals import setup_globals
from ..import_utils import UnavailableObject
from ..import_utils import unavailable_function
from .utils import ensure_shutter_open

try:
    from scipy.ndimage import gaussian_filter
except ImportError as ex:
    gaussian_filter = unavailable_function(ex)

try:
    from id31 import attenuator as id31_attenuator
except ImportError as ex:
    id31_attenuator = UnavailableObject(ex)

try:
    try:
        from blissdata.lima import image_utils

        lima_image = None
    except ImportError:
        image_utils = None
        from blissdata.data import lima_image
except ImportError:
    lima_image = None
    image_utils = None


class ExposureCondition(NamedTuple):
    att_position: int
    expo_time: float


def optimize_exposure_condition(
    detector,
    tframe: float = 0.2,
    default_att_position: Optional[int] = None,
    desired_counts: float = 1e5,
    dynamic_range: int = 1 << 20,
    min_counts_per_frame: float = 1000,
    nframes_measure: int = 1,
    nframes_default: int = 3,
    reduce_desired_deviation: bool = True,
    expose_with_integral_frames: bool = False,
    maxint_sigma: float = 0,
    optimize_attenuator: bool = True,
    mask: Optional[numpy.ndarray] = None,
) -> ExposureCondition:
    """Optimize the attenuator and return the optimal exposure time.

    :param detector: lima detector object
    :param tframe: time of a single frame in accumulation mode
    :param default_att_position: start the optimization with this attenuator position
    :param desired_counts: we want to be close to this maximum pixel value
    :param dynamic_range: full well of the detector
    :param min_counts_per_frame: we need at least these counts to even start optimizing
    :param nframes_measure: number of frames used for optimization measurements
    :param nframes_default: try modify attenuators for this number of frames
    :param reduce_desired_deviation: reduce deviation from the desired counts
    :param expose_with_integral_frames: exposure time is n x frame time with n integral or not
    :param maxint_sigma: gaussian smoothing sigma in pixels before getting the maximum frame intensity
    :param optimize_attenuator: Whether to change or not the attenuator during the optimization
    :param mask: Mask to apply to images during exposure time optimization
    :returns: optimal exposure condition
    """
    Imax_perframe = dynamic_range - 1
    Id = desired_counts
    att_position_max = 31
    att_position_start = _get_attenuator_position()

    with _diode_range_context():
        if default_att_position is None:
            att_position = att_position_start
        else:
            att_position = default_att_position
            if att_position != att_position_start:
                _set_attenuator_position(att_position)

        # Make sure we are BELOW the dynamic range of the detector
        Im_perframe = _get_max_intensity_per_frame(
            detector, tframe, nframes_measure, mask=mask
        )
        if optimize_attenuator:
            while Im_perframe >= Imax_perframe and att_position < att_position_max:
                att_position += 1
                _set_attenuator_position(att_position)
                Im_perframe = _get_max_intensity_per_frame(
                    detector, tframe, nframes_measure, mask=mask
                )

        if Im_perframe >= Imax_perframe:
            # We are at full attenuation and full dynamic range.
            # Decreasing the frame time would be an option but
            # ID31 keeps it fixed.
            print(
                f"Optimized exposure: expo_time={tframe} sec, attenuator={att_position}"
            )
            return ExposureCondition(att_position, tframe)

        if optimize_attenuator:
            # Make sure we have some counts to make the calculations
            # further on more reliable
            while Im_perframe < min_counts_per_frame and att_position:
                att_position -= 1
                _set_attenuator_position(att_position)
                _prev = Im_perframe
                Im_perframe = _get_max_intensity_per_frame(
                    detector, tframe, nframes_measure, mask=mask
                )
                if Im_perframe >= Imax_perframe:
                    att_position += 1
                    Im_perframe = _prev
                    break

        # Calculate transmissions T(E,n_d) of all attenuators
        transmissions = _attenuator_transmisions(_get_energy_value())

        # Calculate the conditions to reach the desired counts
        condition = _calculate_optional_conditions(
            transmissions,
            att_position,
            Im_perframe,
            Id,
            tframe=tframe,
            nframes_default=nframes_default,
            reduce_desired_deviation=reduce_desired_deviation,
            expose_with_integral_frames=expose_with_integral_frames,
            optimize_attenuator=optimize_attenuator,
        )

        _set_attenuator_position(condition.att_position)
        return condition


def optimal_exposure_conditions(
    mot,
    start,
    stop,
    intervals,
    detector,
    tframe: float = 0.2,
    nframes_measure: int = 1,
    nframes_default: int = 3,
    desired_counts: float = 1e5,
    reduce_desired_deviation: bool = True,
    expose_with_integral_frames: bool = False,
    maxint_sigma: float = 2,
) -> List[ExposureCondition]:
    """Return the optimal attenuator and exposure time for each motor position.
    Measurements are done at the current attenuator position.

    :param mot:
    :param start:
    :param stop:
    :param intervals:
    :param detector: lima detector object
    :param tframe: time of a single frame in accumulation mode
    :param desired_counts: we want to be close to this maximum pixel value
    :param nframes_measure: number of frames used for optimization measurements
    :param nframes_default: try modify attenuators for this number of frames
    :param reduce_desired_deviation: reduce deviation from the desired counts
    :param expose_with_integral_frames: exposure time is n x frame time with n integral or not
    :param maxint_sigma: gaussian smoothing sigma in pixels before getting the maximum frame intensity
    :returns: list of optimal exposure conditions
    """
    Id = desired_counts
    att_position = _get_attenuator_position()

    Im_perframe_per_position = _get_max_intensity_per_frame_per_position(
        mot,
        start,
        stop,
        intervals,
        detector,
        tframe=tframe,
        nframes=nframes_measure,
        sigma=maxint_sigma,
    )

    transmissions = _attenuator_transmisions(_get_energy_value())

    return [
        _calculate_optional_conditions(
            transmissions,
            att_position,
            Im_perframe,
            Id,
            tframe=tframe,
            nframes_default=nframes_default,
            reduce_desired_deviation=reduce_desired_deviation,
            expose_with_integral_frames=expose_with_integral_frames,
        )
        for Im_perframe in Im_perframe_per_position
    ]


def _calculate_optional_conditions(
    transmissions,
    att_position,
    Im_perframe,
    Id,
    tframe: float = 0.2,
    nframes_default: int = 3,
    reduce_desired_deviation: bool = True,
    expose_with_integral_frames: bool = False,
    optimize_attenuator: bool = True,
) -> ExposureCondition:
    # Calculate all possible intensities with nframe_d=nframes_default
    #  I = R * tframe * nframes_default * T(E,n_d)
    Rtframe = Im_perframe / transmissions[att_position]  # R * tframe
    if optimize_attenuator:
        Ichoices = Rtframe * nframes_default * transmissions
        att_position = numpy.argmin(abs(Ichoices - Id))

    if att_position != 0:
        if reduce_desired_deviation:
            # Reduce the deviation from Id by solving this to nframes_d
            #  I_d = R * tframe * nframes_d * T(E,n_d)
            nframe_d = Id / (Rtframe * transmissions[att_position])
            if expose_with_integral_frames:
                expo_time = _round_number(nframe_d) * tframe
            else:
                expo_time = _round_number(nframe_d * tframe, ndecimals=1)
        else:
            expo_time = nframes_default * tframe
    else:
        # No attenuator: increase exposure time
        #  I_d = R * tframe * nframes
        nframe_d = Id / Rtframe
        if expose_with_integral_frames:
            expo_time = _round_number(nframe_d) * tframe
        else:
            expo_time = _round_number(nframe_d * tframe, ndecimals=1)

    expected_max_counts = Rtframe / tframe * expo_time * transmissions[att_position]
    print(
        f"Optimal exposure conditions: expo_time={expo_time} sec, attenuator={att_position}, expected max counts={expected_max_counts}"
    )
    return ExposureCondition(att_position=att_position, expo_time=expo_time)


def _set_attenuator_position(att_position: int) -> None:
    """SiO2 thickness (cm) ~= 1.25 * att_position. Does not adapt the diode ranges accordingly."""
    setup_globals.atten.bits = att_position


def _get_attenuator_position() -> int:
    return setup_globals.atten.bits


def _get_energy_value() -> float:
    """keV"""
    return setup_globals.energy.position


@lru_cache(maxsize=1)
def _attenuator_transmisions(energy: float):
    att_position_max = 31
    return id31_attenuator.SiO2trans(energy, numpy.arange(att_position_max + 1))


@contextmanager
def _diode_range_context():
    """Adapt the diode ranges according to the attenuator position."""
    try:
        yield
    finally:
        setup_globals.att(setup_globals.atten.bits)


def _round_number(nframes: Union[float, int], ndecimals: int = 0) -> Union[float, int]:
    if ndecimals:
        m = 10**ndecimals
        return max(int(nframes * m + 0.5) / m, 1 / m)
    else:
        return max(int(nframes + 0.5), 1)


def _get_max_intensity_per_frame(
    detector,
    tframe: float = 0.2,
    nframes: int = 1,
    sigma: float = 0,  # rockit is most likely enabled
    mask: Optional[numpy.ndarray] = None,
) -> float:
    ensure_shutter_open()  # shutter can be closed by Pilatus protection
    try:
        setup_globals.ct(tframe * nframes, detector)
    except RuntimeError as e:
        if "Pilatus protection" in str(e):
            print(f"_get_max_intensity_per_frame failed: {e}")
            return float("inf")
        raise

    # This is slower:
    # setup_globals.fshopen()
    # setup_globals.limatake(tframe, nbframes=nframes)
    # setup_globals.fshclose()

    if image_utils is not None:
        frame = image_utils.read_video_last_image(detector.proxy).array
    else:
        frame, _ = lima_image.read_video_last_image(detector.proxy)
    maxint = _get_frame_max_intensity(frame, sigma=sigma, mask=mask) / nframes
    return maxint


def _get_max_intensity_per_frame_per_position(
    mot,
    start,
    stop,
    intervals,
    detector,
    tframe: float = 0.2,
    nframes: int = 1,
    sigma: float = 2,  # rockit is cannot be enabled
) -> List[float]:
    count_time = tframe * nframes
    ensure_shutter_open()
    scan = setup_globals.ascan(
        mot, start, stop, intervals, count_time, detector, save=False
    )

    data = scan.get_data()
    frames = data[detector.name + ":image"]
    maxint = [
        _get_frame_max_intensity(frame, sigma=sigma) / nframes for frame in frames
    ]
    return maxint


def _get_frame_max_intensity(
    frame, sigma: float = 2, mask: Optional[numpy.ndarray] = None
) -> float:
    if mask is not None:
        if mask.shape != frame.shape:
            print(
                "WARNING: Optimization mask does not match detector image: Ignoring it!"
            )
        else:
            frame = numpy.where(mask == 0, frame, 0)

    if sigma > 0:
        return gaussian_filter(frame, sigma=sigma).max()
    return frame.max()

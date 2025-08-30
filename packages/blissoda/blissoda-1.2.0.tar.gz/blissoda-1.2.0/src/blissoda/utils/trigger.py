import functools
from typing import Callable
from typing import Optional
from typing import Union

from ..import_utils import unavailable_class
from ..import_utils import unavailable_function
from ..import_utils import unavailable_type

try:
    from bliss.scanning.scan_meta import get_user_scan_meta
except ImportError as ex:
    get_user_scan_meta = unavailable_function(ex)

try:
    from bliss.scanning.scan import Scan as BlissScanType
except ImportError as ex:
    BlissScanType = unavailable_type(ex)

try:
    from bliss.scanning.scan_meta import META_TIMING
except ImportError as ex:
    META_TIMING = unavailable_class(ex)

try:
    from bliss.scanning.scan_state import ScanState
except ImportError as ex:
    ScanState = unavailable_class(ex)

TriggerType = Callable[[BlissScanType], Optional[dict]]

_SCAN_META_CATEGORY = "workflows"


def enable_processing_trigger(
    processing_id: str,
    trigger: TriggerType,
    timing: Union[str, META_TIMING],
):
    """
    Execute `trigger` when the scan reaches a certain stage (PREPARED by default).

    When `trigger` returns a dictionary it will merged with the dictionary of
    all other trigger functions in the Bliss session and saved in HDF5 under
    the "/x.y/workflows" group. The dictionary follows the convention accepted
    by the `dicttonx` method from the silx library.

    The `processing_id` needs to be unique within a Bliss session.
    """
    if isinstance(timing, str):
        try:
            timing = META_TIMING[timing.upper()]
        except KeyError:
            raise KeyError(
                f"timing must be one of {META_TIMING.__members__.values()}"
            ) from None
    elif not isinstance(timing, META_TIMING):
        raise TypeError(
            f"'timing' must be of type 'str' or 'META_TIMING', got '{type(timing)}'"
        )

    scan_meta_obj = get_user_scan_meta()
    if _SCAN_META_CATEGORY not in scan_meta_obj.categories_names():
        scan_meta_obj.add_categories({_SCAN_META_CATEGORY})
        meta_category = getattr(scan_meta_obj, _SCAN_META_CATEGORY)
        # Make category available for all timings (filter in the `_trigger_on_timing` wrapper)
        for t in META_TIMING.__members__.values():
            meta_category.timing |= t
        meta_category.set("@NX_class", {"@NX_class": "NXcollection"})
    else:
        meta_category = getattr(scan_meta_obj, _SCAN_META_CATEGORY)

    if meta_category.is_set(processing_id):
        raise RuntimeError(
            f"Another processor has already registered the processing id '{processing_id}'"
        )

    trigger_on_state = _trigger_on_timing(timing)(trigger)
    meta_category.set(processing_id, trigger_on_state)


def disable_processing_trigger(processing_id: str):
    scan_meta_obj = get_user_scan_meta()
    if _SCAN_META_CATEGORY not in scan_meta_obj.categories_names():
        return
    meta_category = getattr(scan_meta_obj, _SCAN_META_CATEGORY)
    if meta_category.is_set(processing_id):
        meta_category.remove(processing_id)


def _trigger_on_timing(timing: META_TIMING):
    def _decorator(trigger: TriggerType):
        @functools.wraps(trigger)
        def _wrapper(scan=None):
            if scan is None:
                return
            current_timing = _get_meta_timing(scan)
            if timing & current_timing:
                # The processing was enabled for this timing
                return trigger(scan)

        return _wrapper

    return _decorator


def _get_meta_timing(scan: BlissScanType) -> META_TIMING:
    if scan.state < ScanState.PREPARING:
        return META_TIMING.START
    if scan.state == ScanState.PREPARING:
        return META_TIMING.PREPARED
    return META_TIMING.END

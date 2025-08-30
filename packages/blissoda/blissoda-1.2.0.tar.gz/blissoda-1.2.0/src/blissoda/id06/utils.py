from typing import List

import numpy
from silx.io.url import DataUrl

from ..import_utils import unavailable_type

try:
    from bliss.scanning.scan import Scan as BlissScanType
except ImportError as ex:
    BlissScanType = unavailable_type(ex)


def _gonio2pyFAI(angles: numpy.ndarray) -> numpy.ndarray:
    """Convert goniometer angles (clockwise, origin at the top, in degree 0-360) to azimuthal angles
    in pyFAI's coordinate system (counter-clockwise, origin at horizontal, radians -pi+pi)
    """
    return numpy.deg2rad((angles - 90 + 180) % 360 - 180)


def get_data_url(scan: BlissScanType, lima_name: str) -> str:
    filename = scan.scan_info.get("filename")
    scan_number = scan.scan_info.get("scan_nb")
    data_url = DataUrl(
        file_path=filename, data_path=f"/{scan_number}.1/measurement/{lima_name}"
    )
    return data_url.path()


def get_positions(start: float, step: float, npts: int) -> List[float]:
    # Shift positions by step / 2 so that bins land in the middle of two positions
    new_start = start + step / 2
    gonio_positions = numpy.arange(new_start, new_start + npts * step, step)
    return _gonio2pyFAI(gonio_positions).tolist()


def is_multigeometry(scan: BlissScanType) -> bool:
    return scan.scan_info.get("type") == "fscan" and scan.scan_info["save"]

from pathlib import Path

from ..bliss_globals import current_session
from ..processor import BlissScanType
from ..utils.directories import get_filename


def export_filename_prefix(scan: BlissScanType, lima_name: str) -> str:
    scan_filename = Path(get_filename(scan))
    scan_nb = scan.scan_info.get("scan_nb")
    return f"{scan_filename.stem}_{scan_nb:04d}_{lima_name}"


def get_current_filename() -> str:
    return current_session.scan_saving.filename

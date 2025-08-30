import logging
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set
from typing import Tuple

import numpy
from silx.io import h5py_utils
from silx.utils.retry import RetryError
from silx.utils.retry import RetryTimeoutError

from .models import XrpdFieldName
from .models import XrpdPlotInfo
from .utils import get_axis_data

logger = logging.getLogger(__name__)


def create_plot_info(
    scan_name: str,
    lima_name: str,
    radial_label: str,
    azim_label: Optional[str],
    plot_data: Dict[XrpdFieldName, numpy.ndarray],
    hdf5_url: Optional[str] = None,
) -> XrpdPlotInfo:
    plot_info = XrpdPlotInfo(
        scan_name=scan_name,
        lima_name=lima_name,
        radial_label=radial_label,
        azim_label=azim_label,
        hdf5_url=hdf5_url,
        field_names=list(plot_data.keys()),
    )
    plot_info.save()
    for field_name, field_data in plot_data.items():
        plot_info.get_data_array(field_name).extend(field_data)

    return plot_info


def get_plots_to_remove(max_len: int) -> List[XrpdPlotInfo]:
    all_plots = get_plots()

    if max_len <= 0:
        return all_plots

    remove: List[XrpdPlotInfo] = list()
    keep_scans: Set[str] = set()
    for plot_info in all_plots[::-1]:
        scan_name = plot_info.scan_name
        if len(keep_scans) == max_len and scan_name not in keep_scans:
            remove.append(plot_info)
        else:
            keep_scans.add(scan_name)

    return remove


def delete_plot_info(plot_info: XrpdPlotInfo) -> None:
    plot_info.delete_data_arrays()
    XrpdPlotInfo.delete(plot_info.pk)


def get_curve_data(
    plot_key: str, **retry_options
) -> Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray], XrpdPlotInfo]:
    """Get the data from the results of the last processed point of the scan."""
    plot_info = XrpdPlotInfo.get(plot_key)

    try:
        x = plot_info.get_data_array("radial")[()]
    except IndexError:
        return None, None, plot_info

    y = _get_last_integrated_intensity(plot_info, **retry_options)
    return x, y, plot_info


def append_image_data(
    plot_key: str,
    current_data: Optional[numpy.ndarray] = None,
    **retry_options,
) -> Tuple[Optional[numpy.ndarray], Optional[numpy.ndarray], XrpdPlotInfo]:
    """Add new data (if any) to the current data (if any)"""
    plot_info = XrpdPlotInfo.get(plot_key)
    try:
        x = plot_info.get_data_array("radial")[()]
    except IndexError:
        return None, None, plot_info

    if plot_info.hdf5_url:
        if current_data is None:
            idx = tuple()
        else:
            idx = slice(len(current_data), None)
        try:
            y = _get_data_from_file(plot_info.hdf5_url, idx=idx, **retry_options)
        except RetryTimeoutError:
            y = None
        else:
            if current_data is not None:
                y = numpy.vstack([current_data, y])
    else:
        y = plot_info.get_data_array("intensity")[()]

    return x, y, plot_info


def _get_last_integrated_intensity(plot_info: XrpdPlotInfo, **retry_options):
    if plot_info.hdf5_url:
        try:
            return _get_data_from_file(plot_info.hdf5_url, idx=-1, **retry_options)
        except RetryTimeoutError:
            return None

    try:
        return plot_info.get_data_array("intensity")[-1]
    except IndexError:
        return None


def get_2d_integration_data(plot_key: str, **retry_options) -> Tuple[
    Optional[numpy.ndarray],
    Optional[numpy.ndarray],
    Optional[numpy.ndarray],
    XrpdPlotInfo,
]:
    plot_info = XrpdPlotInfo.get(plot_key)

    try:
        x = plot_info.get_data_array("radial")[()]
        y = plot_info.get_data_array("azimuthal")[()]
    except IndexError:
        return None, None, None, plot_info

    intensity = _get_last_integrated_intensity(plot_info, **retry_options)
    return x, y, intensity, plot_info


@h5py_utils.retry()
def _get_data_from_file(hdf5_url: str, idx=tuple()):
    filename, dsetname = hdf5_url.split("::")
    with h5py_utils.File(filename) as root:
        try:
            return root[dsetname][idx]
        except KeyError as e:
            raise RetryError(str(e))


def get_plots() -> List[XrpdPlotInfo]:
    return sorted(
        [XrpdPlotInfo.get(pk) for pk in XrpdPlotInfo.all_pks()],
        key=lambda p: p.timestamp,
    )


def delete_old_entries(current_session) -> int:
    """Delete Redis entries from an older blissoda version"""
    db = XrpdPlotInfo._meta.database
    old_keys = db.keys(f"blissoda:{current_session.name}:Plotter*")
    for key in old_keys:
        XrpdPlotInfo._meta.database.delete(key)
    return len(old_keys)


class XrpdNXDataInfo(NamedTuple):
    radial_label: str
    azim_label: Optional[str]
    plot_data: Dict[XrpdFieldName, numpy.ndarray]
    intensity_url: str


@h5py_utils.retry()
def get_xrpd_nxdata_info(nxdata_url: str) -> XrpdNXDataInfo:
    """Returns NXdata radial axis info and HDF5 URL of the intensity dataset"""
    plot_data: Dict[XrpdFieldName, numpy.ndarray] = dict()

    filename, nxdata_name = nxdata_url.split("::")
    with h5py_utils.File(filename, mode="r") as f:
        try:
            nxdata = f[nxdata_name]
            radial_name = nxdata.attrs["axes"][-1]
            radial_label, radial_data = get_axis_data(nxdata, radial_name)
            plot_data["radial"] = radial_data

            signal = nxdata[nxdata.attrs["signal"]]
            if signal.ndim > 2:
                azim_name = nxdata.attrs["axes"][-2]
                azim_label, azim_data = get_axis_data(nxdata, azim_name)
                plot_data["azimuthal"] = azim_data
            else:
                azim_label = None
        except KeyError as e:
            raise RetryError(str(e))

        return XrpdNXDataInfo(
            radial_label=radial_label,
            azim_label=azim_label,
            plot_data=plot_data,
            intensity_url=f"{filename}::{signal.name}",
        )

from typing import Tuple

import h5py
import numpy
from silx.utils.retry import RetryError


def axis_label(name: str, units: str):
    return f"{name} ({units})"


def get_axis_data(nxdata: h5py.Group, name: str) -> Tuple[str, numpy.ndarray]:
    dset = nxdata[name]
    assert isinstance(dset, h5py.Dataset)
    units = dset.attrs["units"]
    assert isinstance(units, str)

    return axis_label(name, units), dset[()]


def find_pyFAI_generated_process(parent: h5py.Group) -> str:
    for grp in parent.values():
        if (
            isinstance(grp, h5py.Group)
            and "program" in grp
            and grp["program"][()].decode() == "pyFAI"
        ):
            return grp.name

    raise KeyError(
        f"Could not find a pyFAI-generated process in {parent.file.filename}::{parent.name}"
    )


def get_integrated_nxdata(root: h5py.File, scan) -> h5py.Group:
    scan_dsetname = f'/{scan.scan_info.get("scan_nb")}.1'

    try:
        scan_dset = root[scan_dsetname]
        nxprocess = find_pyFAI_generated_process(scan_dset)

        nxdata = root[f"{nxprocess}/integrated"]
    except KeyError as e:
        raise RetryError(str(e))
    assert isinstance(nxdata, h5py.Group)

    return nxdata

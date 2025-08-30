"""
Utilities for the EXAFS scans.

- Continuous scans: `energy scan framework <https://gitlab.esrf.fr/bliss/energy_scan>`_ which
  uses the `fast scan framework <https://gitlab.esrf.fr/bliss/fscan>`_.

- Step scans: `BM23 step energy scan framework <https://gitlab.esrf.fr/bm23/bm23/-/blob/master/bm23/BM23scanExafs.py>`_.
"""

from typing import Union

from ..import_utils import unavailable_type

try:
    from bliss.scanning.scan import Scan as BlissScanType
except ImportError as ex:
    BlissScanType = unavailable_type(ex)

try:
    from fscan.trigscan import TrigScanCustomRunner as TrigScanCustomRunnerType
except ImportError as ex:
    TrigScanCustomRunnerType = unavailable_type(ex)


ScanType = Union[BlissScanType, TrigScanCustomRunnerType]


def is_multi_xas_scan(scan: ScanType) -> bool:
    try:
        # fscan.trigscan.TrigScanPars in case of TrigScanCustomRunnerType
        return scan.pars.nscans > 1
    except AttributeError:
        return False


def multi_xas_subscan_size(scan: ScanType) -> int:
    try:
        # fscan.trigscan.TrigScanPars in case of TrigScanCustomRunnerType
        return scan.pars.npoints + 1

        # "npoints" is a badly chosen variable name.
        # It should be called "nsteps" and `size = nstep + 1`.
    except AttributeError:
        return 0

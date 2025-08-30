from typing import Any
from typing import Dict
from typing import Optional

from ..exafs import scan_utils
from ..exafs.processor import ExafsProcessor


class Bm23ExafsProcessor(ExafsProcessor):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("workflow", "/users/opd23/ewoks/online.ows")
        defaults.setdefault("_scan_type", "trigscan")
        counters = defaults.setdefault("_counters", dict())
        counters.setdefault(
            "cont",
            {
                "mu_name": "mu_trans",
                "energy_name": "energy_cenc",
                "energy_unit": "keV",
            },
        )
        counters.setdefault(
            "step",
            {
                "mu_name": "mu_trans",
                "energy_name": "eneenc",
                "energy_unit": "keV",
            },
        )
        counters.setdefault(
            "trigscan",
            {
                "mu_name": "mu_trans",
                "energy_name": "energy_enc",
                "energy_unit": "keV",
            },
        )

        super().__init__(config=config, defaults=defaults)

    def _scan_type_from_scan(self, scan: scan_utils.ScanType) -> Optional[str]:
        if "exafs_step" in getattr(scan, "name", ""):
            return "step"
        elif "exafs_cont" in getattr(scan, "name", ""):
            return "cont"
        elif "trigscan" in getattr(scan, "_scan_name", ""):
            return "trigscan"

    def _multi_xas_scan(self, scan: scan_utils.ScanType) -> bool:
        return True
        # return scan_utils.is_multi_xas_scan(scan)

    def _multi_xas_subscan_size(self, scan: scan_utils.ScanType) -> int:
        return scan_utils.multi_xas_subscan_size(scan)

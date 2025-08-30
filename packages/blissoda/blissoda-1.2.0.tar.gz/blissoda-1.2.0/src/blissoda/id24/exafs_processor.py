from typing import Any
from typing import Dict
from typing import Optional

from ..exafs import scan_utils
from ..exafs.processor import ExafsProcessor


class Id24ExafsProcessor(ExafsProcessor):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("workflow", "/users/opid24/ewoks/online.ows")
        defaults.setdefault("_scan_type", "escan")
        counters = defaults.setdefault("_counters", dict())
        counters.setdefault(
            "escan",
            {
                "mu_name": "mu_trans",
                "energy_name": "energy_enc",
                "energy_unit": "keV",
            },
        )

        super().__init__(config=config, defaults=defaults)

    def _scan_type_from_scan(
        self, scan: scan_utils.TrigScanCustomRunnerType
    ) -> Optional[str]:
        return "escan"

    def _multi_xas_scan(self, scan: scan_utils.TrigScanCustomRunnerType) -> bool:
        return True
        # return scan_utils.is_multi_xas_scan(scan)

    def _multi_xas_subscan_size(self, scan: scan_utils.TrigScanCustomRunnerType) -> int:
        return scan_utils.multi_xas_subscan_size(scan)

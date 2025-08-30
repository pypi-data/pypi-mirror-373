import json
import os
from typing import Any
from typing import Dict
from typing import Optional

from ..bliss_globals import current_session
from ..bm02.xrpd_processor import Bm02XrpdProcessor
from ..utils import directories
from .calib import DEFAULT_CALIB


class DemoBm02XrpdProcessor(Bm02XrpdProcessor):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("queue", "celery")
        defaults.setdefault("lima_names", ["difflab6"])
        defaults.setdefault(
            "integration_options",
            {
                "difflab6": {
                    "method": "no_csr_cython",
                    "nbpt_rad": 4096,
                    "unit": "q_A^-1",
                }
            },
        )
        defaults.setdefault(
            "empty_cell_subtraction_options",
            {
                "difflab6": {
                    "enabled": False,
                    "cell_pattern_url": None,
                    "empty_cell_factor": 1,
                }
            },
        )

        super().__init__(config=config, defaults=defaults)

        if self._HAS_BLISS:
            self._ensure_pyfai_config_filename()

    def _ensure_pyfai_config_filename(self):
        root_dir = directories.get_processed_dir(current_session.scan_saving.filename)
        cfgfile = os.path.join(root_dir, "config", "pyfaicalib.json")
        if not os.path.exists(cfgfile):
            poni = DEFAULT_CALIB
            os.makedirs(os.path.dirname(cfgfile), exist_ok=True)
            with open(cfgfile, "w") as f:
                json.dump(poni, f)
        self.config_filename = {"difflab6": cfgfile}


bm02_xrpd_processor = DemoBm02XrpdProcessor()

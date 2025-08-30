import json
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..bliss_globals import current_session
from ..bliss_globals import setup_globals
from ..persistent.parameters import ParameterInfo
from ..utils import directories
from ..xrpd.processor import XrpdProcessor
from .calib import DEFAULT_CALIB


class DemoXrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("config_filename", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("lima_names", ["difflab6"])
        defaults.setdefault(
            "integration_options",
            {
                "method": "no_csr_cython",
                "nbpt_rad": 4096,
                "unit": "q_nm^-1",
            },
        )

        super().__init__(config=config, defaults=defaults)
        if self._HAS_BLISS:
            self._ensure_config_filename()

        self.queue = "celery"

    def get_integrate_inputs(
        self, scan, lima_name: str, task_identifier: str
    ) -> List[dict]:
        self._ensure_config_filename()
        inputs = super().get_integrate_inputs(scan, lima_name, task_identifier)
        is_even = not bool(
            setup_globals.difflab6.image.width % 2
        )  # lima-camera-simulator<1.9.10 does not support odd image widths
        inputs.append(
            {"task_identifier": task_identifier, "name": "demo", "value": is_even}
        )
        return inputs

    def _ensure_config_filename(self):
        if self.config_filename:
            return
        root_dir = self._get_config_dir(current_session.scan_saving.filename)
        cfgfile = os.path.join(root_dir, "pyfaicalib.json")
        os.makedirs(os.path.dirname(cfgfile), exist_ok=True)
        poni = DEFAULT_CALIB
        with open(cfgfile, "w") as f:
            json.dump(poni, f)
        self.config_filename = cfgfile

    def _get_demo_result_dir(self, dataset_filename: str) -> str:
        root_dir = directories.get_processed_dir(dataset_filename)
        return os.path.join(root_dir, "demo", "xrpd")

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        root_dir = self._get_demo_result_dir(dataset_filename)
        return os.path.join(root_dir, "workflows")

    def _get_config_dir(self, dataset_filename: str) -> str:
        root_dir = self._get_demo_result_dir(dataset_filename)
        return os.path.join(root_dir, "config")

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.config_filename

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        return self.integration_options.to_dict()


xrpd_processor = DemoXrpdProcessor()

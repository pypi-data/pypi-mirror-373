import json
import os
from pprint import pprint
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..bliss_globals import current_session
from ..bliss_globals import setup_globals
from ..id22.stscan_processor import StScanProcessor
from ..id22.xrpd_processor import Id22XrpdProcessor
from ..utils import directories
from .calib import DEFAULT_CALIB


class DemoStScanProcessor(StScanProcessor):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        if self._HAS_BLISS:
            root_dir = directories.get_processed_dir(
                current_session.scan_saving.filename
            )
            root_dir = os.path.join(root_dir, "demo", "id22", "config")

            defaults.setdefault(
                "_convert_workflow",
                os.path.join(root_dir, "convert.json"),
            )
            defaults.setdefault(
                "_rebinsum_workflow",
                os.path.join(root_dir, "rebinsum.json"),
            )
            defaults.setdefault(
                "_extract_workflow",
                os.path.join(root_dir, "extract.json"),
            )

        super().__init__(config=config, defaults=defaults)

    def _submit_job(self, workflow, inputs, convert_destination, **kw):
        print("\nSubmit workfow")
        print(workflow)
        print("Inputs:")
        pprint(inputs)
        print("Save for provenance:")
        pprint(convert_destination)
        print("Options:")
        pprint(kw)

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        return os.path.join(directories.get_workflows_dir(dataset_filename), "id22")


class DemoId22XrpdProcessor(Id22XrpdProcessor):
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
                "method": "no_csr_cython",
                "nbpt_rad": 4096,
                "unit": "q_nm^-1",
            },
        )

        super().__init__(config=config, defaults=defaults)
        if self._HAS_BLISS:
            self._ensure_config_filename()

    def get_integrate_1d_inputs(self, scan, lima_name: str) -> List[dict]:
        inputs = super().get_integrate_1d_inputs(scan, lima_name)
        is_even = not bool(
            setup_globals.difflab6.image.width % 2
        )  # lima-camera-simulator<1.9.10 does not support odd image widths
        inputs.append(
            {"task_identifier": "Integrate1D", "name": "demo", "value": is_even}
        )
        return inputs

    def _ensure_config_filename(self):
        if self.pyfai_config:
            return
        root_dir = self._get_config_dir(current_session.scan_saving.filename)
        cfgfile = os.path.join(root_dir, "pyfaicalib.json")
        os.makedirs(os.path.dirname(cfgfile), exist_ok=True)
        poni = DEFAULT_CALIB
        with open(cfgfile, "w") as f:
            json.dump(poni, f)
        self.pyfai_config = cfgfile

    def _get_demo_result_dir(self, dataset_filename: str) -> str:
        root_dir = directories.get_processed_dir(dataset_filename)
        return os.path.join(root_dir, "demo", "id22")

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        root_dir = self._get_demo_result_dir(dataset_filename)
        return os.path.join(root_dir, "workflows")

    def _get_config_dir(self, dataset_filename: str) -> str:
        root_dir = self._get_demo_result_dir(dataset_filename)
        return os.path.join(root_dir, "config")


stscan_processor = DemoStScanProcessor()
id22_xrpd_processor = DemoId22XrpdProcessor()

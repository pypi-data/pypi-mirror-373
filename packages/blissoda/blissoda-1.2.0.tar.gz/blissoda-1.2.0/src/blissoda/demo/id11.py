import json
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..bliss_globals import current_session
from ..bliss_globals import setup_globals
from ..id11.xrpd_processor import Id11XrpdProcessor
from ..resources import resource_filename
from ..utils import directories
from .calib import DEFAULT_CALIB


class DemoId11XrpdProcessor(Id11XrpdProcessor):
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
                "unit": "q_A^-1",
            },
        )

        super().__init__(config=config, defaults=defaults)

        if self._HAS_BLISS:
            self._ensure_pyfai_config_filename()
            self._ensure_pdf_config_filename()

    def get_integrate_inputs(
        self, scan, lima_name: str, task_identifier: str
    ) -> List[dict]:
        inputs = super().get_integrate_inputs(scan, lima_name, task_identifier)
        is_even = not bool(
            setup_globals.difflab6.image.width % 2
        )  # lima-camera-simulator<1.9.10 does not support odd image widths
        inputs.append(
            {"task_identifier": task_identifier, "name": "demo", "value": is_even}
        )
        return inputs

    def _ensure_pyfai_config_filename(self):
        root_dir = self._get_config_dir(current_session.scan_saving.filename)
        cfgfile = os.path.join(root_dir, "difflab6", "pyfaicalib.json")
        if not os.path.exists(cfgfile):
            poni = DEFAULT_CALIB
            os.makedirs(os.path.dirname(cfgfile), exist_ok=True)
            with open(cfgfile, "w") as f:
                json.dump(poni, f)
        self.pyfai_config_directory = root_dir

    def _ensure_pdf_config_filename(self):
        src_pdf_config_file = resource_filename("demo", "pdf_config.cfg")
        root_dir = self._get_config_dir(current_session.scan_saving.filename)
        dest_pdf_config_file = os.path.join(root_dir, "pdf_config.cfg")
        if not os.path.exists(dest_pdf_config_file):
            with open(src_pdf_config_file, "r") as src:
                os.makedirs(os.path.dirname(dest_pdf_config_file), exist_ok=True)
                with open(dest_pdf_config_file, "w") as dest:
                    src_contents = src.read()
                    dest.write(src_contents)
                    dest.write(
                        f'backgroundfile = {resource_filename("demo", "background.xy")}'
                    )
        self.pdf_config_file = dest_pdf_config_file

    def _get_demo_result_dir(self, dataset_filename: str) -> str:
        root_dir = directories.get_processed_dir(dataset_filename)
        return os.path.join(root_dir, "demo", "id11")

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        root_dir = self._get_demo_result_dir(dataset_filename)
        return os.path.join(root_dir, "workflows")

    def _get_config_dir(self, dataset_filename: str) -> str:
        root_dir = self._get_demo_result_dir(dataset_filename)
        return os.path.join(root_dir, "config")


id11_xrpd_processor = DemoId11XrpdProcessor()

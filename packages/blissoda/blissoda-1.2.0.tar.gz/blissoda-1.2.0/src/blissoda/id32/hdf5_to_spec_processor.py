import json
import logging
import os
import pathlib
from typing import Any
from typing import Dict
from typing import Optional

from ewoksjob.client import submit

from ..bliss_globals import current_session
from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessor
from ..resources import resource_filename
from ..utils.directories import get_dataset_processed_dir

logger = logging.getLogger(__name__)


class ID32Hdf5ToSpecProcessor(
    BaseProcessor,
    parameters=[
        ParameterInfo("save_single_scans", category="workflows"),
    ],
):
    QUEUE = "lid32xmcd2"
    WORKFLOW_FILENAME = "convert_hdf5_to_spec.json"

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("trigger_at", "END")
        defaults.setdefault("save_single_scans", True)

        super().__init__(config=config, defaults=defaults)

    def _get_workflow(self) -> dict:
        with open(resource_filename("id32", self.WORKFLOW_FILENAME), "r") as wf:
            return json.load(wf)

    def _get_workflow_inputs(self, scan) -> list:
        return [
            {
                "name": "scan_numbers",
                "value": [scan.scan_info.get("scan_nb")],
            },
            {
                "name": "save_single_scans",
                "value": self.save_single_scans,
            },
            {
                "name": "input_file",
                "value": self._get_scan_filename(scan),
            },
            {
                "name": "output_path",
                "value": self._get_scan_processed_directory(scan),
            },
        ]

    def _get_scan_filename(self, scan) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def _get_scan_processed_directory(self, scan) -> str:
        return get_dataset_processed_dir(self._get_scan_filename(scan))

    def _get_workflow_destination(self, scan) -> str:
        """Builds the path where the workflow JSON will be saved."""
        filename = self._get_scan_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        root = self._get_scan_processed_directory(scan)
        stem = os.path.splitext(os.path.basename(filename))[0]
        wf_path = os.path.join(root, "workflows")
        pathlib.Path(wf_path).mkdir(parents=True, exist_ok=True)
        basename = f"{stem}_{scan_nb:04d}_make_specfile.json"
        return os.path.join(wf_path, basename)

    def _trigger_workflow_on_new_scan(self, scan) -> None:
        if not scan.scan_info["save"]:
            return

        workflow = self._get_workflow()
        inputs = self._get_workflow_inputs(scan)
        kwargs = {"inputs": inputs, "outputs": [{"all": False}]}
        kwargs["convert_destination"] = self._get_workflow_destination(scan)

        _ = submit(args=(workflow,), kwargs=kwargs, queue=self.QUEUE)

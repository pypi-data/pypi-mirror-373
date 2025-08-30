import logging
import os
from typing import Any
from typing import Dict
from typing import Optional

from ewoksjob.client import get_future
from ewoksjob.client import submit

from ..bliss_globals import current_session
from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessor
from ..processor import BlissScanType
from ..utils.directories import get_dataset_processed_dir
from .plotter import Id02Plotter

logger = logging.getLogger(__name__)


class Id02BaseProcessor(
    BaseProcessor,
    parameters=[
        ParameterInfo("queue", category="workflows", deprecated_names=["worker"]),
        ParameterInfo("number_of_scans", category="plotting"),
    ],
    deprecated_class_attributes={"DEFAULT_WORKER": "DEFAULT_QUEUE"},
):
    DEFAULT_QUEUE = None

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("queue", self.DEFAULT_QUEUE)
        defaults.setdefault("number_of_scans", 4)

        super().__init__(config=config, defaults=defaults)

        self._preset = self._set_up_preset()

        self._plotter = Id02Plotter(number_of_scans=self.number_of_scans)
        self._plotter.replot()

    def _set_up_preset(self):
        raise NotImplementedError()

    def scan_requires_processing(self, scan: BlissScanType) -> bool:
        return scan.scan_info["save"]

    def get_workflow(self, scan: BlissScanType) -> dict:
        dets = [d.name for d in self._preset.getDetectors(scan)]
        return self._preset.buildWorkflow(dets)

    def get_inputs(self, scan: BlissScanType) -> list:
        dets = [d.name for d in self._preset.getDetectors(scan)]
        return self._preset.getInputs(scan, dets)

    def get_filename(self, scan: BlissScanType) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def scan_processed_directory(self, scan: BlissScanType) -> str:
        return get_dataset_processed_dir(self.get_filename(scan))

    def workflow_destination(self, scan: BlissScanType) -> str:
        filename = self.get_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        root = self.scan_processed_directory(scan)
        stem = os.path.splitext(os.path.basename(filename))[0]
        basename = f"{stem}_{scan_nb:04d}.json"
        return os.path.join(root, basename)

    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> Optional[Any]:
        if not self.scan_requires_processing(scan):
            return None

        workflow = self.get_workflow(scan)
        kwargs = {"inputs": self.get_inputs(scan), "outputs": [{"all": False}]}
        if scan.scan_info.get("save"):
            kwargs["convert_destination"] = self.workflow_destination(scan)

        future = submit(args=(workflow,), kwargs=kwargs, queue=self.queue)

        # TODO: Handle plotting with Flint
        future = get_future(future.uuid)

        return future

import logging
import os
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from ewoksjob.client import get_future
from ewoksjob.client import submit

from ..bliss_globals import current_session
from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessor
from ..processor import BlissScanType
from ..utils import directories

_logger = logging.getLogger(__name__)


class SinogramProcessor(
    BaseProcessor,
    parameters=[
        ParameterInfo("sleep_time", category="sinogram"),
        ParameterInfo("deltabeta", category="sinogram"),
        ParameterInfo("backends", category="sinogram"),
        ParameterInfo("cor_backend", category="sinogram"),
        # TODO: Param should be common?
        ParameterInfo("queue", category="workflows"),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("_enabled", True)
        defaults.setdefault("sleep_time", 0)
        defaults.setdefault("deltabeta", 200)
        defaults.setdefault("backends", "nabu,silx")
        defaults.setdefault("cor_backend", "bliss-cor8")

        # Set tomo wide defaults
        defaults.setdefault("trigger_at", "END")
        defaults.setdefault("queue", "tomo_sinogram")

        super().__init__(config=config, defaults=defaults)

    # TODO: Should move to common location
    def workflow_destination(self, scan: BlissScanType) -> str:
        filename = self.get_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        root = self.scan_processed_directory(scan)
        stem = os.path.splitext(os.path.basename(filename))[0]
        basename = f"{stem}_{scan_nb:04d}.json"
        return os.path.join(root, basename)

    # TODO: Should move to common location
    def master_output_filename(self, scan: BlissScanType) -> str:
        """Filename which can be used to inspect the results after the processing."""
        filename = self.get_filename(scan)
        root = self.scan_processed_directory(scan)
        basename = os.path.basename(filename)
        return os.path.join(root, basename)

    # TODO: Should move to common location
    def get_filename(self, scan: BlissScanType) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    # TODO: Common
    def scan_processed_directory(self, scan: BlissScanType) -> str:
        return directories.get_dataset_processed_dir(self.get_filename(scan))

    def get_sinogram_inputs(
        self,
        sleep_time: Optional[float] = None,
        axisposition: Optional[float] = None,
        deltabeta: Optional[float] = None,
        backends: Optional[str] = None,
        cor_backend: Optional[str] = None,
    ):
        def arg_else_prop(arg, prop):
            return arg if arg is not None else prop

        params = {
            "sleep_time": arg_else_prop(sleep_time, self.sleep_time),
            "axisposition": axisposition,
            "deltabeta": arg_else_prop(deltabeta, self.deltabeta),
            "backends": arg_else_prop(backends, self.backends),
            "cor_backend": arg_else_prop(cor_backend, self.cor_backend),
        }

        inputs = [
            {
                "task_identifier": "SinogramReconstruction",
                "name": p,
                "value": v,
            }
            for p, v in params.items()
        ]

        return inputs

    def get_inputs(self, scan) -> List[dict]:
        filename = self.get_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        inputs = [
            {
                "task_identifier": "SinogramReconstruction",
                "name": "filename",
                "value": filename,
            },
            {
                "task_identifier": "SinogramReconstruction",
                "name": "output_filename",
                "value": self.master_output_filename(scan),
            },
            {
                "task_identifier": "SinogramReconstruction",
                "name": "scan",
                "value": scan_nb,
            },
        ]
        inputs += self.get_sinogram_inputs()
        return inputs

    def get_reprocess_inputs(
        self,
        datacollectionid: int,
        filename: str,
        deltabeta: Optional[float],
        axisposition: Optional[float],
        overwrite: bool = False,
    ) -> List[dict]:

        process_root = directories.get_dataset_processed_dir(filename)
        if os.path.exists(process_root):
            job_uuid = str(uuid.uuid4())
            process_root = f"{process_root}_{job_uuid}"
            os.makedirs(process_root)

        basename = os.path.basename(filename)

        inputs = [
            {
                "task_identifier": "SinogramReconstruction",
                "name": "dataCollectionId",
                "value": datacollectionid,
            },
            {
                "task_identifier": "SinogramReconstruction",
                "name": "filename",
                "value": filename,
            },
            {
                "task_identifier": "SinogramReconstruction",
                "name": "output_filename",
                "value": os.path.join(process_root, basename),
            },
        ]
        inputs += self.get_sinogram_inputs(
            deltabeta=deltabeta, axisposition=axisposition
        )
        return inputs

    def get_submit_arguments(self, scan: BlissScanType) -> dict:
        return {
            "inputs": self.get_inputs(scan),
            "outputs": [{"all": False}],
        }

    def get_workflow(self):
        return {
            "graph": {
                "id": "tomo-sinogram-reconstruction",
                "label": "tomo sinogram reconstruction",
            },
            "nodes": [
                {
                    "id": "SinogramReconstruction",
                    "task_type": "class",
                    "task_identifier": "tomovis.ewoks.tomo_sinogram_reconstruction.TomoSinogramReconstruction",
                }
            ],
            "links": [],
        }

    def _trigger_workflow_on_new_scan(self, scan):
        _logger.debug("Trigger workflow on new scan")
        return self.on_new_scan_metadata(scan)

    def scan_requires_processing(self, scan: BlissScanType) -> bool:
        channels = scan.scan_info.get("channels", {})
        sinogram_chan = channels.get("sinogram") is not None
        rotation_chan = channels.get("rotation") is not None
        translation_chan = channels.get("translation") is not None
        sinogram = sinogram_chan and rotation_chan and translation_chan
        return sinogram

    def on_new_scan_metadata(self, scan) -> Optional[dict]:
        metadata, _ = self._on_new_scan(scan)
        return metadata

    def _on_new_scan(self, scan) -> Tuple[Optional[dict], Optional[Any]]:
        _logger.debug("_on_new_scan")

        if not self.scan_requires_processing(scan):
            return None, None

        workflow = self.get_workflow()
        kwargs = self.get_submit_arguments(scan)
        if scan.scan_info.get("save"):
            kwargs["convert_destination"] = self.workflow_destination(scan)

        _logger.debug("Execute workflow\n%s\nArgs:\n%s", workflow, kwargs)
        _logger.debug("Queue: %s", self.queue)

        future = submit(args=(workflow,), kwargs=kwargs, queue=self.queue)
        future = get_future(future.uuid)

        return None, future

    def reprocess(
        self,
        params: Dict[str, Any],
    ):
        _logger.debug("Reprocess: %s", params)

        datacollectionid = params.pop("datacollectionid")
        deltabeta = params.pop("deltabeta")
        axisposition = params.pop("axisposition")
        filename = params.pop("filename")
        overwrite = params.pop("overwrite", False)
        if len(params) != 0:
            _logger.error("Unexpected reprocess parameters: %s", params)

        workflow = self.get_workflow()
        kwargs = {
            "inputs": self.get_reprocess_inputs(
                axisposition=axisposition,
                deltabeta=deltabeta,
                filename=filename,
                datacollectionid=datacollectionid,
                overwrite=overwrite,
            ),
            "outputs": [{"all": False}],
        }

        future = submit(args=(workflow,), kwargs=kwargs, queue=self.queue)
        future = get_future(future.uuid)

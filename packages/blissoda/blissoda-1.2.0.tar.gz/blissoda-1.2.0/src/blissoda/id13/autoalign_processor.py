import os
import shutil
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from ewoksjob.client import submit

from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessor
from ..resources import resource_filename
from ..utils import directories
from ..xrpd.processor import _get_scan_memory_url


class Id13AutoAlignProcessor(
    BaseProcessor,
    parameters=[
        ParameterInfo("counter_name", category="AutoAlign"),
        ParameterInfo("motor1_name", category="AutoAlign"),
        ParameterInfo("motor2_name", category="AutoAlign"),
        ParameterInfo("workflow_autoalign", category="AutoAlign"),
        ParameterInfo("model_filename", category="AutoAlign"),
        ParameterInfo("queue", category="workflows", deprecated_names=["worker"]),
    ],
):
    DEFAULT_WORKFLOW_AUTOALIGN: Optional[str] = resource_filename(
        "id13", "autoalign_nn.json"
    )
    QUEUE_TORCH = "lid13gpu3_torch_ppf"
    MODEL_FILENAME = "/data/id13/inhouse/Nicolas/Test_python/cnn_siemens_align/cnn_center_siemens.pth"

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("_plotting_enabled", False)
        defaults.setdefault("counter_name", "")
        defaults.setdefault("motor1_name", "")
        defaults.setdefault("motor2_name", "")
        defaults.setdefault("workflow_autoalign", self.DEFAULT_WORKFLOW_AUTOALIGN)
        defaults.setdefault("queue", self.QUEUE_TORCH)
        defaults.setdefault("model_filename", self.MODEL_FILENAME)

        super().__init__(config=config, defaults=defaults)

    def trigger_workflow_on_new_scan(self, scan):
        return self.on_new_scan_metadata(scan)

    def on_new_scan_metadata(self, scan) -> Optional[dict]:
        metadata, _ = self._on_new_scan(scan)
        return metadata

    def get_autoalign_inputs(self, dmesh_scan):
        inputs = [
            {
                "task_identifier": "AutoAlign",
                "name": "motor1_name",
                "value": self.motor1_name,
            },
            {
                "task_identifier": "AutoAlign",
                "name": "motor2_name",
                "value": self.motor2_name,
            },
            {
                "task_identifier": "AutoAlign",
                "name": "counter_name",
                "value": self.counter_name,
            },
            {
                "task_identifier": "AutoAlign",
                "name": "scan_memory_url",
                "value": _get_scan_memory_url(scan=dmesh_scan),
            },
            {
                "task_identifier": "AutoAlign",
                "name": "model_filename",
                "value": self.model_filename,
            },
        ]
        return inputs

    def get_inputs(self, scan) -> List[dict]:
        return self.get_autoalign_inputs(dmesh_scan=scan)

    def get_submit_arguments(self, scan) -> dict:
        return {
            "inputs": self.get_inputs(scan),
            "outputs": [{"all": False}],
        }

    def get_workflow(self, scan) -> Optional[str]:
        """Get the workflow to execute for the scan and ensure it is located
        in the proposal directory for user reference and worker accessibility.
        """
        script_dir = os.path.join(
            scan.scan_info["filename"].split("RAW_DATA")[0], "SCRIPTS"
        )
        workflow_path = os.path.join(script_dir, "autoalign_nn.json")
        if not os.path.exists(workflow_path):
            shutil.copy(self.workflow_autoalign, workflow_path)
            self.workflow_autoalign = workflow_path
        return self.workflow_autoalign

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        return directories.get_workflows_dir(dataset_filename)

    def _on_new_scan(self, scan) -> Tuple[Optional[dict], Optional[Any]]:
        future = None
        workflow = self.get_workflow(scan)
        kwargs = self.get_submit_arguments(scan)
        # Trigger workflow from the current process.
        future = submit(args=(workflow,), kwargs=kwargs, queue=self.queue)
        return future

import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ewoksjob.client import submit

from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessor
from ..processor import BlissScanType

_DEFAULT_SCAN_PARS: Dict[str, Any] = {}


class TiffFilesProcessor(
    BaseProcessor,
    parameters=[
        ParameterInfo("queue", category="workflows", deprecated_names=["worker"]),
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo(
            "lima_name",
            category="TiffFiles",
            doc="Name of the detector used for the conversion",
        ),
        ParameterInfo(
            "scan_parameters",
            category="TiffFiles",
            doc="Derived from scan_info",
        ),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        # default trigger at end of scan
        defaults.setdefault("trigger_at", "END")
        defaults.setdefault("workflow", "")
        defaults.setdefault("lima_name", "eiger")
        # initialize empty scan parameters
        defaults.setdefault("scan_parameters", _DEFAULT_SCAN_PARS)

        super().__init__(config=config, defaults=defaults)

    def update_scan_parameters(self, scan: BlissScanType = None) -> Dict[str, Any]:
        scan_parameters: Dict[str, Any] = {}
        if scan is not None:
            # HDF5 input file from LIMA
            scan_number = scan.scan_number
            image_path = scan.scan_saving.images_path.format(
                scan_number=scan_number,
                img_acq_device=self.lima_name if hasattr(self, "lima_name") else "",
            )
            # typically the first frame file
            scan_parameters["images"] = [f"{image_path}0000.h5"]
            # output base name and folder
            processed_dir = os.path.dirname(
                scan_parameters["images"][0].replace("RAW_DATA", "PROCESSED_DATA")
            )
            # folder where TIFFs will be created
            output_folder = os.path.join((processed_dir), "xdi")
            scan_parameters["output"] = output_folder
        self.scan_parameters.update(scan_parameters)
        return scan_parameters

    def get_inputs(self, scan: BlissScanType) -> List[Dict[str, Any]]:
        # ensure scan_parameters are up to date
        params = self.update_scan_parameters(scan)
        inputs: List[Dict[str, Any]] = [
            {
                "task_identifier": "TiffFiles",
                "name": "images",
                "value": params["images"],
            },
            {
                "task_identifier": "TiffFiles",
                "name": "output",
                "value": params["output"],
            },
        ]
        if self.lima_name:
            inputs.append(
                {
                    "task_identifier": "TiffFiles",
                    "name": "detector_name",
                    "value": self.lima_name,
                }
            )
        return inputs

    def workflow_destination(self, scan) -> str:
        scan_number = scan.scan_info.get("scan_nb", 0)
        dataset_name = os.path.basename(os.path.dirname(scan.scan_saving.filename))
        return os.path.join(
            self.scan_parameters["output"], f"{dataset_name}_{scan_number}.json"
        )

    def get_submit_arguments(self, scan: BlissScanType) -> Dict[str, Any]:
        return {"inputs": self.get_inputs(scan), "outputs": [{"all": "False"}]}

    def run_conversion(self, scan: BlissScanType) -> None:
        kw = self.get_submit_arguments(scan)
        # destination for workflow metadata
        kw["convert_destination"] = self.workflow_destination(scan)
        submit(args=(self.workflow,), kwargs=kw, queue=self.queue)

    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> None:
        # trigger only for fscan-type scans
        if "dmesh" in scan.scan_info.get("type", ""):
            self.run_conversion(scan)

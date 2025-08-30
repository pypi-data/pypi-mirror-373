from typing import List
from typing import Optional

from marshmallow import fields

from ..daiquiri.mixin import DaiquiriProcessorMixin
from ..daiquiri.mixin import ExposedParameter
from ..daiquiri.validators import exists_list
from ..daiquiri.validators import exists_valid_json
from ..persistent.parameters import ParameterInfo
from ..resources import resource_filename
from ..utils import directories
from .processor import BlissScanType
from .processor import FluoProcessor


class DaiquiriFluoProcessor(
    FluoProcessor,
    DaiquiriProcessorMixin,
    parameters=[ParameterInfo("notification_queue", category="daiquiri")],
):
    DEFAULT_WORKFLOW: Optional[str] = resource_filename(
        "fluo", "daiquiri_xrfmap_single_detector.json"
    )

    EXPOSED_PARAMETERS = [
        ExposedParameter(
            parameter="workflow",
            field_type=fields.Str,
            title="Current workflow",
            field_options={"validate": exists_valid_json},
        ),
        ExposedParameter(
            parameter="pymca_configs",
            field_type=fields.List,
            title="PyMCA Config File(s)",
            field_options={"validate": exists_list},
            field_args=[fields.Str()],
        ),
        ExposedParameter(
            parameter="quantification",
            field_type=fields.Bool,
            title="Quantification",
        ),
    ]

    def scan_requires_processing(self, scan) -> bool:
        """Only execute this workflow if there is a `daiquiri_datacollectionid` in the `scan_info`"""
        requires_processing = super().scan_requires_processing(scan) and bool(
            scan.scan_info.get("daiquiri_datacollectionid")
        )
        return requires_processing

    def get_daiquiri_inputs(self, scan: BlissScanType, workflow: str):
        task_identifier = "StartJob"
        return [
            {
                "task_identifier": task_identifier,
                "name": "dataCollectionId",
                "value": scan.scan_info.get("daiquiri_datacollectionid"),
            },
            {
                "task_identifier": task_identifier,
                "name": "output_filename",
                "value": directories.master_output_filename(scan),
            },
            {
                "task_identifier": task_identifier,
                "name": "workflow",
                "value": workflow,
            },
            {
                "task_identifier": task_identifier,
                "name": "config",
                "value": {
                    "pymca_configs": ",".join(self.pymca_configs),
                },
            },
            {
                "task_identifier": "NotifyBeamline",
                "name": "beamline",
                "value": self.notification_queue,
            },
        ]

    def get_workflow_and_inputs(self, scan: BlissScanType) -> List[dict]:
        """Merge in daiquiri StartJob options"""
        workflow, inputs = super().get_workflow_and_inputs(scan)
        inputs += self.get_daiquiri_inputs(scan, workflow)

        workflow = "daiquiri_" + workflow.replace(".ows", ".json")
        return workflow, inputs

    def get_submit_arguments(self, scan: BlissScanType, inputs: List[dict]) -> dict:
        """Need ppf for error handling"""
        args = super().get_submit_arguments(scan, inputs)
        args["engine"] = "ppf"
        return args

from typing import List
from typing import Optional

from marshmallow import fields

from ..daiquiri.mixin import DaiquiriProcessorMixin
from ..daiquiri.mixin import ExposedParameter
from ..daiquiri.validators import exists_valid_json
from ..resources import resource_filename
from .xrpd_processor import Id13XrpdProcessor


class DaiquiriXrpdProcessor(Id13XrpdProcessor, DaiquiriProcessorMixin):
    DEFAULT_WORKFLOW: Optional[str] = resource_filename("id13", "daiquiri_juno.json")

    EXPOSED_PARAMETERS = [
        ExposedParameter(
            parameter="current_workflow",
            field_type=fields.Str,
            title="Last triggered workflow",
            field_options={"validate": exists_valid_json},
        ),
        ExposedParameter(
            parameter="pyfai_config",
            field_type=fields.Str,
            title="PyFAI Config File",
            field_options={"validate": exists_valid_json},
        ),
        ExposedParameter(
            parameter="do_diffmap",
            field_type=fields.Bool,
            title="Enable Diffmap",
        ),
        ExposedParameter(
            parameter="average_reference",
            field_type=fields.Str,
            title="Name of the reference (standard)",
        ),
        ExposedParameter(
            parameter="do_average",
            field_type=fields.Bool,
            title="Enable Average",
        ),
        ExposedParameter(
            parameter="do_stackedf",
            field_type=fields.Bool,
            title="Enable StackEDF (XRDUA)",
        ),
        ExposedParameter(
            parameter="do_background_removal",
            field_type=fields.Bool,
            title="Background Removal (SPI)",
        ),
        ExposedParameter(
            parameter="do_cnmf",
            field_type=fields.Bool,
            title="CNMF (SPI)",
        ),
        ExposedParameter(
            parameter="do_phase_inference",
            field_type=fields.Bool,
            title="Phase Inference (SPI)",
        ),
        ExposedParameter(
            parameter="integration_options",
            field_type=fields.Dict,
            field_options={"keys": fields.Str()},
            title="PyFAI Options",
        ),
    ]

    def scan_requires_processing(self, scan) -> bool:
        """Only execute this workflow if there is a `daiquiri_datacollectionid` in the `scan_info`"""
        requires_processing = super().scan_requires_processing(scan) and bool(
            scan.scan_info.get("daiquiri_datacollectionid")
        )
        return requires_processing

    def get_daiquiri_inputs(self, scan, lima_name):
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
                "value": self.master_output_filename(scan),
            },
            {
                "task_identifier": task_identifier,
                "name": "workflow",
                "value": self.get_workflow(scan),
            },
            {
                "task_identifier": task_identifier,
                "name": "config",
                "value": {
                    "pyfai_config": self.get_config_filename(lima_name),
                    "integrate_options": self.get_integration_options(lima_name),
                },
            },
        ]

    def get_inputs(self, scan, lima_name: str) -> List[dict]:
        """Merge in daiquiri StartJob options"""
        inputs = super().get_inputs(scan, lima_name)
        inputs += self.get_daiquiri_inputs(scan, lima_name)
        return inputs

    def get_submit_arguments(self, scan, lima_name) -> dict:
        """Need ppf for error handling"""
        args = super().get_submit_arguments(scan, lima_name)
        args["engine"] = "ppf"
        return args

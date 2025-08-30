from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..bliss_globals import current_session
from ..persistent.parameters import ParameterInfo
from ..processor import BlissScanType
from ..resources import resource_filename
from ..utils import validators
from ..xrpd.processor import XrpdProcessor
from .utils import get_data_url
from .utils import get_positions
from .utils import is_multigeometry


class Id06XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config", category="PyFai", validator=validators.is_file),
        ParameterInfo("integration_options", category="PyFai"),
        ParameterInfo("goniometer_file", category="PyFai"),
        ParameterInfo("multigeometry_workflow", category="workflows"),
    ],
):
    MULTIGEOMETRY_WORKFLOW = resource_filename(
        "id06", "integrate_2dmultigeometry_with_saving.json"
    )

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("multigeometry_enabled", False)
        defaults.setdefault("step", 10)
        defaults.setdefault("multigeometry_workflow", self.MULTIGEOMETRY_WORKFLOW)

        super().__init__(config=config, defaults=defaults)

    def _get_workflow(self, scan: BlissScanType) -> str:
        if is_multigeometry(scan):
            return self.multigeometry_workflow

        return (
            self.workflow_with_saving
            if scan.scan_info["save"]
            else self.workflow_without_saving
        )

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.pyfai_config

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        integration_options = self.integration_options
        if integration_options:
            return integration_options.to_dict()
        return None

    def get_inputs(self, scan, lima_name: str) -> List[dict]:
        inputs = super().get_inputs(scan, lima_name)
        if is_multigeometry(scan):
            inputs += self._get_multigeometry_inputs(scan, lima_name)
        return inputs

    def _get_multigeometry_inputs(
        self, scan: BlissScanType, lima_name: str
    ) -> List[dict]:
        task_identifier = "Integrate2DMultiGeometry"
        multigeometry_inputs = [
            {
                "task_identifier": task_identifier,
                "name": "goniometer_file",
                "value": self._get_parameter("goniometer_file"),
            },
            {
                "task_identifier": task_identifier,
                "name": "positions",
                "value": self._get_positions(),
            },
            {
                "task_identifier": task_identifier,
                "name": "images",
                "value": get_data_url(scan, lima_name),
            },
        ]
        return multigeometry_inputs

    def _get_positions(self) -> List[float]:
        fscan_parameters = current_session.setup_globals.fscan.pars
        return get_positions(
            start=fscan_parameters.start_pos,
            step=fscan_parameters.step_size,
            npts=fscan_parameters.npoints,
        )

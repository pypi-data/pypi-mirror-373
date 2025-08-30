from typing import List

from marshmallow import fields

from ..daiquiri.mixin import DaiquiriProcessorMixin
from ..daiquiri.mixin import ExposedParameter
from .sinogram_processor import SinogramProcessor


class DaiquiriSinogramProcessor(SinogramProcessor, DaiquiriProcessorMixin):
    EXPOSED_PARAMETERS = [
        ExposedParameter(
            parameter="sleep_time",
            field_type=fields.Int,
            title="Sleep Time",
        ),
        ExposedParameter(
            parameter="deltabeta",
            field_type=fields.Float,
            title="Delta/beta",
        ),
        ExposedParameter(
            parameter="backends",
            field_type=fields.Str,
            title="Reconstruc. Backends",
        ),
        ExposedParameter(
            parameter="cor_backend",
            field_type=fields.Str,
            title="CoR Backend",
        ),
    ]

    def get_daiquiri_inputs(self, scan):
        task_identifier = "SinogramReconstruction"
        datacollectionid = scan.scan_info.get("daiquiri", {}).get("datacollectionid")
        if datacollectionid is None:
            return []
        return [
            {
                "task_identifier": task_identifier,
                "name": "dataCollectionId",
                "value": datacollectionid,
            },
        ]

    def get_inputs(self, scan) -> List[dict]:
        """Merge in daiquiri options"""
        inputs = super().get_inputs(scan)
        inputs += self.get_daiquiri_inputs(scan)
        return inputs

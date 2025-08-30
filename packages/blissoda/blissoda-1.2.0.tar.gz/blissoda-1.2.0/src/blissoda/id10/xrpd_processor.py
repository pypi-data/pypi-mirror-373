from typing import Optional

from ..persistent.parameters import ParameterInfo
from ..xrpd.processor import XrpdProcessor


class Id10XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
    ],
):
    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.pyfai_config

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        integration_options = self.integration_options
        if integration_options:
            return integration_options.to_dict()
        return None

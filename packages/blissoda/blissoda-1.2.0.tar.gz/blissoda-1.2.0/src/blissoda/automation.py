import logging
import warnings
from typing import Any
from typing import Dict
from typing import Optional

from .persistent.parameters import WithPersistentParameters
from .utils.classes import NoMethodAssignment

logger = logging.getLogger(__name__)


class BlissAutomationObject(WithPersistentParameters, NoMethodAssignment):
    """A Bliss object for automation (data processing and/or acquisition).

    It has persistent parameters in Redis and configuration in Beacon.

    The Beacon configuration is expected to use the
    `generic plugin <https://bliss.gitlab-pages.esrf.fr/bliss/master/config_plugins.html#plugin-generic>`_.

    For example:

    .. code: yaml

        - name: my_processor
            plugin: generic
            class: MyProcessor
            package: blissoda.mycategory.my_processor
            default_parameters:
              param1: value1
              param2: value2

    `config["default_parameters"]` has priority over `defaults`.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> None:
        config = config or {}
        defaults = defaults or {}
        beacon_defaults = config.get("default_parameters", {})
        defaults = {**defaults, **beacon_defaults}

        super().__init__(**defaults)

        self._config = config

    @classmethod
    def _merge_defaults(
        cls,
        deprecated_defaults: Dict[str, Any],
        defaults: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if deprecated_defaults:
            warning = f"{cls.__name__}(**defaults) is deprecated, use {cls.__name__}(defaults={{...}})"
            logger.warning(warning)
            warnings.warn(warning, DeprecationWarning, stacklevel=2)

        if defaults:
            return {**deprecated_defaults, **defaults}
        else:
            return deprecated_defaults

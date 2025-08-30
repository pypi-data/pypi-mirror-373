from ..import_utils import unavailable_class
from .processor import Id02BaseProcessor

try:
    from id02.acquisition.xpcs_preset import ID02DynamixProcessingPreset
except ImportError as ex:
    ID02DynamixProcessingPreset = unavailable_class(ex)


class Id02XpcsProcessor(Id02BaseProcessor):
    DEFAULT_WORKER = "xpcs"

    def _set_up_preset(self):
        return ID02DynamixProcessingPreset()

from ..import_utils import unavailable_class
from .processor import Id02BaseProcessor

try:
    from id02.acquisition.saxs_preset import ID02DahuProcessingPreset
except ImportError as ex:
    ID02DahuProcessingPreset = unavailable_class(ex)


class Id02SaxsProcessor(Id02BaseProcessor):
    DEFAULT_QUEUE = "saxs"

    def _set_up_preset(self):
        return ID02DahuProcessingPreset()

from typing import Any
from typing import Dict
from typing import Optional

from ..bliss_globals import setup_globals
from ..import_utils import UnavailableObject
from ..import_utils import is_available
from ..streamline.scanner import StreamlineScanner

try:
    from streamline_changer.sample_changer import SampleChanger
except ImportError as ex:
    streamline_changer = UnavailableObject(ex)


class StreamlineSesScanner(StreamlineScanner):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ):
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("sample_changer_name", "streamline_sc")

        super().__init__(config=config, defaults=defaults)

    def measure_sample(self, *args, has_qrcode: bool = True, **kwargs):
        return None

    def _get_calibration(self):
        return {"non_empty": None}

    def _newsample(self, sample_name: str):
        print("NEW SAMPLE:", sample_name)


if is_available(setup_globals):
    streamline_sc = SampleChanger(
        setup_globals.streamline_translation, setup_globals.streamline_wago
    )
else:
    streamline_sc = UnavailableObject(ImportError)

streamline_scanner = StreamlineSesScanner()

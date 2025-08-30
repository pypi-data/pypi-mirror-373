import json
import os
from typing import Any
from typing import Dict
from typing import Generator
from typing import Optional
from typing import Tuple

from ..bliss_globals import current_session
from ..bliss_globals import setup_globals
from ..utils import directories
from .calib import DEFAULT_CALIB


class DemoStreamlineScannerMixIn:
    """Mix-in class for demo StreamlineScanner class.

    Usage:

    .. code-block::

       class DemoStreamlineScanner(DemoStreamlineScannerMixIn, StreamlineScanner):
           pass
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ):
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        self._mock_sample_changer = MockSampleChanger()
        defaults.setdefault("queue", "celery")
        defaults.setdefault("detector_name", "difflab6")
        defaults.setdefault("calibrant", "LaB6")
        defaults.setdefault("sample_changer_name", "streamline_sc")
        defaults.setdefault(
            "integration_options",
            {
                "method": "no_csr_cython",
                "integrator_name": "sigma_clip_ng",
                "extra_options": {"max_iter": 3, "thres": 0},
                "error_model": "azimuthal",  # hybrid gives weird results
                "nbpt_rad": 4096,
                "unit": "q_nm^-1",
            },
        )
        defaults.setdefault("rockit_distance", 0.0)

        super().__init__(config=config, defaults=defaults)

    def calib(self, *args, sample_index=0, **kwargs):
        return super().calib(*args, sample_index=sample_index, **kwargs)

    def init_workflow(self, with_autocalibration: bool = True):
        self._ensure_pyfai_config()
        return super().init_workflow(with_autocalibration=with_autocalibration)

    def _ensure_pyfai_config(self):
        """Set the pyfai_config variable and ensure the file exists."""
        pyfai_config = self.pyfai_config
        if not pyfai_config:
            root_dir = self._get_config_dir(current_session.scan_saving.filename)
            pyfai_config = os.path.join(root_dir, "pyfaicalib.json")

        if os.path.exists(pyfai_config):
            return

        os.makedirs(os.path.dirname(pyfai_config), exist_ok=True)
        poni = DEFAULT_CALIB
        with open(pyfai_config, "w") as f:
            json.dump(poni, f)

        self.pyfai_config = pyfai_config

    def _get_demo_result_dir(self, dataset_filename: str) -> str:
        root_dir = directories.get_processed_dir(dataset_filename)
        return os.path.join(root_dir, "demo", "streamline")

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        root_dir = self._get_demo_result_dir(dataset_filename)
        return os.path.join(root_dir, "workflows")

    def _get_config_dir(self, dataset_filename: str) -> str:
        root_dir = self._get_demo_result_dir(dataset_filename)
        return os.path.join(root_dir, "config")

    def run(self, *args, **kwargs):
        self._ensure_pyfai_config()  # in case the file was deleted
        args = (*args, setup_globals.difflab6)
        super().run(*args, **kwargs)

    @property
    def sample_changer(self):
        return self._mock_sample_changer

    def _job_arguments(self, *args, **kw):
        args, kwargs = super()._job_arguments(*args, **kw)
        is_even = not bool(
            setup_globals.difflab6.image.width % 2
        )  # lima-camera-simulator<1.9.10 does not support odd image widths
        kwargs["inputs"].append(
            {"task_identifier": "Integrate1D", "name": "demo", "value": is_even}
        )
        return args, kwargs

    def _get_workflow_upload_parameters(self, *args) -> None:
        return None


class MockQrReader:
    QRCODE_NOT_READABLE = "QRCODE_NOT_READABLE"


class MockSampleChanger:
    def __init__(self, number_of_samples: int = 16) -> None:
        translation = MockSampleTranslation()

        self._vibration_speed = 0
        self._translation = translation
        self._number_of_samples = number_of_samples
        self._allowed_sample_indices = tuple(range(number_of_samples))
        self._qrreader = MockQrReader()

        # should be in Redis but good enough for a demo
        self._nholders_in_tray = 2
        self._loaded = False
        self._holder_counter = 0

        start = 0
        stop = number_of_samples - 1
        intervals = number_of_samples - 1
        self._ascan_arguments = translation, start, stop, intervals

    @property
    def qrreader(self) -> MockQrReader:
        return self._qrreader

    def ascan_arguments(self) -> Tuple[Any, float, float, int]:
        return self._ascan_arguments

    def fill_tray(self, n=2) -> None:
        self._nholders_in_tray = n

    def qr_read(self, **_) -> str:
        if not self._loaded:
            return self.qrreader.QRCODE_NOT_READABLE
        position = self._translation.position
        sample_index = int(position)
        on_sample = abs(position - sample_index) < 0.01
        if not on_sample or sample_index not in self._allowed_sample_indices:
            return self.qrreader.QRCODE_NOT_READABLE
        return f"holder{self._holder_counter}_sample{sample_index:02d}_lab6"

    def select_sample(self, sample_index: int, **qrread_options) -> str:
        for qr_response in self.iterate_samples([sample_index], **qrread_options):
            return qr_response

    def select_sample_without_qr(self, sample_index) -> str:
        return self.select_sample(sample_index)

    def iterate_samples(
        self, sample_indices=None, **qrread_options
    ) -> Generator[str, None, None]:
        if not sample_indices:
            sample_indices = range(self._number_of_samples)
        for i in sample_indices:
            self.translation.position = i
            yield self.qr_read(**qrread_options)

    def iterate_samples_without_qr(
        self, sample_indices=None
    ) -> Generator[str, None, None]:
        yield from self.iterate_samples(sample_indices=sample_indices)

    def eject_old_baguette(self) -> None:
        if not self._loaded:
            print("Streamline sample changer: nothing loaded")
            return
        self._loaded = False
        self.translation.position = 20

    def load_baguette_with_homing(self) -> None:
        if self._loaded:
            print("Streamline sample changer: already loaded")
            return
        if self._nholders_in_tray == 0:
            print("Streamline sample changer: no more holders in tray")
            return
        self._nholders_in_tray = self._nholders_in_tray - 1
        self._loaded = True
        self._holder_counter += 1
        self.translation.position = 0

    def has_remaining_baguettes(self) -> bool:
        return bool(self._nholders_in_tray)

    @property
    def number_of_remaining_baguettes(self) -> int:
        return self._nholders_in_tray

    @property
    def translation(self):
        return self._translation

    @property
    def vibration_speed(self):
        return self._vibration_speed

    @vibration_speed.setter
    def vibration_speed(self, speed):
        print("SETTING VIBRATION SPEED TO", speed)
        if speed < 0 or speed > 100:
            raise RuntimeError(
                "Speed for the fluidization system out of range (0-100, as in %)"
            )
        self._vibration_speed = speed

    def tune_qrreader(self, force=False) -> str:
        return self.qr_read()

    def tune_qrreader_for_baguette(self) -> None:
        pass


class MockSampleTranslation:
    def __init__(self) -> None:
        self._position = 0

    def on(self):
        pass

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        print("Move streamline_translation from", self._position, "to", value)
        self._position = value

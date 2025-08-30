from contextlib import contextmanager
from typing import Any
from typing import Dict
from typing import Generator
from typing import Optional

import fabio
import numpy
from ewoksutils.task_utils import task_inputs

from ..bliss_globals import setup_globals
from ..persistent.parameters import ParameterInfo
from ..streamline.scanner import StreamlineScanner
from ..utils import validators
from . import optimize_exposure
from .utils import ensure_shutter_open


class Id31StreamlineScanner(
    StreamlineScanner,
    parameters=[
        ParameterInfo(
            "optimize_pixel_value", category="exposure/attenuator", validator=float
        ),
        ParameterInfo(
            "optimize_nb_frames", category="exposure/attenuator", validator=int
        ),
        ParameterInfo(
            "optimize_max_exposure_time",
            category="exposure/attenuator",
            validator=float,
        ),
        ParameterInfo("default_attenuator", category="exposure/attenuator"),
        ParameterInfo("attenuator_name", category="names"),
        ParameterInfo("newflat", category="Flat-field", validator=validators.is_file),
        ParameterInfo("oldflat", category="Flat-field", validator=validators.is_file),
        ParameterInfo("flat_enabled", category="Flat-field", validator=bool),
        ParameterInfo("optimize_exposure_per", category="robust vs. speed"),
        ParameterInfo("rockit_distance", category="sample changer"),
        ParameterInfo(
            "optimize_attenuator",
            category="exposure/attenuator",
            validator=bool,
        ),
        ParameterInfo("optimize_mask_file", category="exposure/attenuator"),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ):
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("workflow", "streamline_without_calib_with_flat.json")
        defaults.setdefault("detector_name", "p3")
        defaults.setdefault("attenuator_name", "atten")
        defaults.setdefault("sample_changer_name", "streamline_sc")
        defaults.setdefault(
            "integration_options",
            {
                "method": "no_csr_ocl_gpu",
                "integrator_name": "sigma_clip_ng",
                "extra_options": {"max_iter": 3, "thres": 0},
                "error_model": "azimuthal",  # hybrid gives weird results
                "nbpt_rad": 4096,
                "unit": "q_nm^-1",
            },
        )
        defaults.setdefault("flat_enabled", True)
        defaults.setdefault("newflat", "/data/id31/inhouse/P3/flats.mat")
        defaults.setdefault("oldflat", "/data/id31/inhouse/P3/flats_old.mat")
        defaults.setdefault("optimize_pixel_value", 1e5)
        defaults.setdefault("optimize_nb_frames", 3)
        defaults.setdefault("optimize_max_exposure_time", 4)
        defaults.setdefault("optimize_exposure_per", "baguette")
        defaults.setdefault("rockit_distance", 0.07)
        defaults.setdefault("optimize_attenuator", True)
        defaults.setdefault("optimize_mask_file", None)

        super().__init__(config=config, defaults=defaults)

        self._exposure_conditions = list()
        self._fixed_attenuator_position = None
        self._optimize_mask_array: Optional[numpy.ndarray] = None
        self._update_optimize_mask(self.optimize_mask_file)

    @property
    def optimize_exposure_per(self) -> Optional[str]:
        return self._get_parameter("optimize_exposure_per")

    @optimize_exposure_per.setter
    def optimize_exposure_per(self, value: Optional[str]):
        if value not in (None, "sample", "baguette"):
            raise ValueError("Allowed values are 'sample', 'baguette' or None")
        self._set_parameter("optimize_exposure_per", value)

    @property
    def optimize_mask_file(self) -> Optional[str]:
        return self._get_parameter("optimize_mask_file")

    @optimize_mask_file.setter
    def optimize_mask_file(self, filename: Optional[str]):
        self._update_optimize_mask(filename)

    def _update_optimize_mask(self, filename: Optional[str]):
        if not filename:
            self._optimize_mask_array = None
            self._set_parameter("optimize_mask_file", None)
            return

        try:
            self._optimize_mask_array = fabio.open(filename).data
        except Exception:
            print(f"Error: cannot load optimize_mask_file {filename}, reseting it!")
            self._optimize_mask_array = None
            self._set_parameter("optimize_mask_file", None)
            return

        self._set_parameter("optimize_mask_file", filename)

    @contextmanager
    def run_context(self):
        setup_globals.shopen(
            check_pilatus=False
        )  # check_pilatus = False when the detector was just started
        with super().run_context():
            yield

    def load(self):
        super().load()
        if self.optimize_exposure_per == "baguette":
            self.determine_exposure_conditions()

    def measure_sample(
        self, count_time: float = 1, *args, has_qrcode: bool = True, **kwargs
    ):
        with rockit(self.sample_changer.translation, self.rockit_distance):
            with self._optimize_sample_exposure(
                count_time, has_qrcode=has_qrcode
            ) as expo_time:
                if has_qrcode:
                    expo_time_max = self.optimize_max_exposure_time
                else:
                    expo_time_max = count_time
                expo_time = min(expo_time, expo_time_max)

                if not self.dryrun:
                    ensure_shutter_open()
                try:
                    return super().measure_sample(expo_time, *args, **kwargs)
                except RuntimeError as e:
                    if "Pilatus protection" in str(e):
                        print(
                            f"Skip because of measurement error: {e}. Open shutter again"
                        )
                        return
                    raise

    def determine_exposure_conditions(self):
        """Pre-define optimal conditions: ascan at fixed attenuator position"""
        detector = getattr(setup_globals, self.detector_name)
        if self.default_attenuator is None:
            attenuator = getattr(setup_globals, self.attenuator_name)
            self.default_attenuator = attenuator.bits
        else:
            setup_globals.att(self.default_attenuator)
        self._exposure_conditions = optimize_exposure.optimal_exposure_conditions(
            *self.sample_changer.ascan_arguments(),
            detector,
            tframe=0.2,
            desired_counts=self.optimize_pixel_value,
            nframes_measure=1,
            nframes_default=self.optimize_nb_frames,
            reduce_desired_deviation=True,
            expose_with_integral_frames=False,
        )

    def determine_exposure_conditions_individually(self):
        """Pre-define optimal conditions: ct on each sample with adapted attenuator
        if the default attenuator position gives too much or too little counts"""
        detector = getattr(setup_globals, self.detector_name)
        attenuator = getattr(setup_globals, self.attenuator_name)
        att_value = attenuator.bits
        exposure_conditions = list()
        try:
            for _ in self.sample_changer.iterate_samples_without_qr():
                exposure_conditions.append(self._optimize_exposure_condition(detector))
        finally:
            setup_globals.att(att_value)
        self._exposure_conditions = exposure_conditions

    @contextmanager
    def _optimize_sample_exposure(
        self, count_time: float, has_qrcode: bool = True
    ) -> Generator[float, None, None]:
        """Selecting the optimal measurement conditions and returning the corresponding
        exposure time for the current sample."""

        if not self.optimize_exposure_per:
            # Optimization is disabled
            yield count_time

        elif self.optimize_exposure_per == "baguette":
            # Select pre-defined optimization
            count_time = self._set_exposure_condition()
            yield count_time

        elif not has_qrcode:
            # No QR-code probably means no sample so do not waste time optimizing
            yield count_time

        else:
            # Optimize condition for this sample individually
            detector = getattr(setup_globals, self.detector_name)
            attenuator = getattr(setup_globals, self.attenuator_name)
            att_value = attenuator.bits
            try:
                condition = self._optimize_exposure_condition(detector)
                yield condition.expo_time
            finally:
                setup_globals.att(att_value)

    def _set_exposure_condition(self) -> float:
        if not self._exposure_conditions:
            self.determine_exposure_conditions()
        sample_index = self.sample_changer.current_sample_index
        condition = self._exposure_conditions[sample_index]
        print(f"Pre-defined optimal exposure conditions: {condition}")
        setup_globals.att(condition.att_position)
        return condition.expo_time

    def _optimize_exposure_condition(
        self, detector
    ) -> optimize_exposure.ExposureCondition:
        return optimize_exposure.optimize_exposure_condition(
            detector,
            tframe=0.2,
            default_att_position=self.default_attenuator,
            desired_counts=self.optimize_pixel_value,
            dynamic_range=1 << 20,
            min_counts_per_frame=0,  # take 100
            nframes_measure=1,
            nframes_default=self.optimize_nb_frames,
            reduce_desired_deviation=True,
            expose_with_integral_frames=False,
            optimize_attenuator=self.optimize_attenuator,
            mask=self._optimize_mask_array,
        )

    def init_workflow(self, with_autocalibration: bool = False) -> None:
        if with_autocalibration:
            self.workflow = "streamline_with_calib_with_flat.json"
        else:
            self.workflow = "streamline_without_calib_with_flat.json"

        print(f"Active data processing workflow: {self.workflow}")

    def _job_arguments(self, scan_info, processed_metadata: dict):
        args, kwargs = super()._job_arguments(scan_info, processed_metadata)
        detector_name = self.detector_name

        kwargs["inputs"] += task_inputs(
            task_identifier="FlatFieldFromEnergy",
            inputs={
                "newflat": self.newflat,
                "oldflat": self.oldflat,
                "energy": getattr(setup_globals, self.energy_name).position,
                "enabled": self.flat_enabled and detector_name == "p3",
            },
        )

        # Rely on StreamlineScanner to set url and bliss_scan_url as for other SaveNexusPattern1D tasks
        kwargs["inputs"] += task_inputs(
            task_identifier="SaveNexusPattern1D",
            label="save_q_no_sigmaclip_hdf5",
            inputs={
                "nxprocess_name": f"{detector_name}_integrate_q_no_sigmaclip",
                "nxmeasurement_name": f"{detector_name}_integrated_q_no_sigmaclip",
                "metadata": {
                    f"{detector_name}_integrate_q_no_sigmaclip": {
                        "configuration": {"workflow": self.workflow}
                    }
                },
            },
        )

        # Use workflows from ewoksid31 module
        kwargs["load_options"] = {"root_module": "ewoksid31.workflows"}

        return args, kwargs


@contextmanager
def rockit(motor, distance):
    if distance:
        try:
            with setup_globals.rockit(motor, distance):
                print("ROCKING ON")
                yield
        finally:
            print("ROCKING OFF")
    else:
        print("ROCKING DISABLED")
        yield

"""
.. code-block:: python

    DEMO_SESSION [1]: from blissoda.demo.streamline_scanner import streamline_scanner,sample_changer
    DEMO_SESSION [2]: streamline_scanner.eject()
    DEMO_SESSION [3]: streamline_scanner.load()
    DEMO_SESSION [4]: streamline_scanner.calib(1, sample_index=0)
    DEMO_SESSION [5]: streamline_scanner.run(0.1)
"""

import os
import re
import shutil
from contextlib import contextmanager
from numbers import Number
from typing import Any
from typing import Dict
from typing import Generator
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import numpy
from esrf_ontologies import technique
from ewoksjob.client import submit
from ewoksutils.task_utils import task_inputs

from ..automation import BlissAutomationObject
from ..bliss_globals import current_session
from ..bliss_globals import setup_globals
from ..persistent.parameters import ParameterInfo
from ..resources import resource_filename
from ..utils import directories
from ..utils import validators

try:
    from bliss.common.logtools import elog_print
except ImportError:
    elog_print = print


class ScanInfo(NamedTuple):
    filename: str
    scan_nb: int

    @property
    def url(self):
        return f"{self.filename}::/{self.scan_nb}.1"


class StreamlineScanner(
    BlissAutomationObject,
    parameters=[
        ParameterInfo("workflow", category="data processing"),
        ParameterInfo("queue", category="data processing", validator=str),
        ParameterInfo("sample_changer_name", category="names"),
        ParameterInfo("detector_name", category="names", validator=str),
        ParameterInfo("energy_name", category="names"),
        ParameterInfo("calibration_scans", category="calibration"),
        ParameterInfo("calibration_motor", category="calibration"),
        ParameterInfo("image_slice", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
        ParameterInfo("pyfai_config", category="PyFai", validator=validators.is_file),
        ParameterInfo("calibrant", category="calibration"),
        ParameterInfo("trigger_workflows", category="data processing", validator=bool),
        ParameterInfo("vibration_speed_during_scan", category="sample changer"),
        ParameterInfo("verify_qrcode", category="robust vs. speed", validator=bool),
        ParameterInfo(
            "skip_when_no_qr_code", category="robust vs. speed", validator=bool
        ),
        ParameterInfo("autotune_qrreader_per", category="robust vs. speed"),
        ParameterInfo("dryrun", category="testing", validator=bool),
        ParameterInfo("calib_ring_detector_name", category="calibration"),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("queue", "online")
        defaults.setdefault("image_slice", 0)
        defaults.setdefault("trigger_workflows", True)
        defaults.setdefault("vibration_speed_during_scan", 40)
        defaults.setdefault("dryrun", False)
        defaults.setdefault("verify_qrcode", False)
        defaults.setdefault("skip_when_no_qr_code", False)
        defaults.setdefault("autotune_qrreader_per", "baguette")

        super().__init__(config=config, defaults=defaults)

        self._technique_metadata = technique.get_technique_metadata("XRPD")

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()
        try:
            sample_changer = self.sample_changer
        except (AttributeError, KeyError):
            return categories
        categories["status"] = {
            "# sample holders left": sample_changer.number_of_remaining_baguettes,
            "selected sample": int(sample_changer.translation.position),
            "vibration speed (%)": sample_changer.vibration_speed,
            "automatic calibration": self.workflow_has_calib,
            "calibration": "OFF",
            "flat-field": "OFF",
        }
        if self.workflow_has_calib:
            categories["status"]["calibration"] = self._get_calibration().get("image")
        if self.workflow_has_flatfield:
            categories["status"]["flat-field"] = "ON"
        return categories

    @property
    def autotune_qrreader_per(self) -> Optional[str]:
        return self._get_parameter("autotune_qrreader_per")

    @autotune_qrreader_per.setter
    def autotune_qrreader_per(self, value: Optional[str]):
        if value not in (None, "sample", "baguette"):
            raise ValueError("Allowed values are 'sample', 'baguette' or None")
        self._set_parameter("autotune_qrreader_per", value)

    def measure_sample(self, *args, has_qrcode: bool = True, **kwargs):
        if self.dryrun:
            print("Dry-run: skip measurement")
        else:
            return setup_globals.sct(*args, **kwargs)

    @property
    def sample_changer(self):
        self._raise_when_missing("sample_changer_name")
        return current_session.env_dict[self.sample_changer_name]

    def eject(self):
        self.sample_changer.translation.on()
        self.sample_changer.eject_old_baguette()
        print(
            "\n\nNumber of remaining sample holders:",
            self.sample_changer.number_of_remaining_baguettes,
        )

    def load(self):
        self.sample_changer.translation.on()
        self.sample_changer.load_baguette_with_homing()
        if self.autotune_qrreader_per == "baguette":
            self.tune_qrreader_for_baguette()

    def run(
        self,
        *scan_args,
        nholders: Optional[int] = None,
        use_qr_code: bool = True,
        current_holder: bool = False,
        sample_indices: Optional[Tuple[int]] = None,
        **scan_kwargs,
    ):
        if self.workflow_has_calib and not self._get_calibration():
            raise RuntimeError("measure a calibration standard first")
        if self.trigger_workflows:
            if not self.workflow:
                raise RuntimeError("initialize a workflow first")
            if self.pyfai_config and not os.path.exists(self.pyfai_config):
                raise RuntimeError("the pyFAI configuration file no longer exists")

        with self.run_context():
            if current_holder:
                self.load()
                self._run_holder(
                    scan_args,
                    scan_kwargs,
                    use_qr_code=use_qr_code,
                    sample_indices=sample_indices,
                )
            elif nholders is None:
                while self.sample_changer.has_remaining_baguettes():
                    self.eject()
                    self.load()
                    self._run_holder(
                        scan_args,
                        scan_kwargs,
                        use_qr_code=use_qr_code,
                        sample_indices=sample_indices,
                    )
                self.eject()
            else:
                for _ in range(nholders):
                    self.eject()
                    self.load()
                    self._run_holder(
                        scan_args,
                        scan_kwargs,
                        use_qr_code=use_qr_code,
                        sample_indices=sample_indices,
                    )
                self.eject()

    def _run_holder(
        self,
        scan_args: tuple,
        scan_kwargs: dict,
        use_qr_code: bool = True,
        sample_indices: Optional[Tuple[int]] = None,
    ):
        if use_qr_code:
            itfunc = self.sample_changer.iterate_samples
        else:
            itfunc = self.sample_changer.iterate_samples_without_qr

        print("")
        print("========== RUN HOLDER ==========")
        for qrcode in itfunc(
            sample_indices=sample_indices,
            autoTuningAllowed=self.autotune_qrreader_per == "sample",
        ):
            print()
            self._process_sample(qrcode, scan_args, scan_kwargs)
        print("================================")

    def calib(
        self,
        *scan_args,
        sample_index: Optional[int] = None,
        use_qr_code: bool = True,
        **scan_kwargs,
    ):
        if sample_index is None:
            raise ValueError("argument 'sample_index' not provided")
        with self.run_context():
            qrcode = self._select_sample(sample_index, use_qr_code=use_qr_code)
            self._process_sample(qrcode, scan_args, scan_kwargs, is_calibration=True)

    def select_sample(self, sample_index: int, use_qr_code: bool = True) -> str:
        self.sample_changer.translation.on()
        return self._select_sample(sample_index, use_qr_code=use_qr_code)

    def _select_sample(self, sample_index: int, use_qr_code: bool = True) -> str:
        if use_qr_code:
            select_sample = self.sample_changer.select_sample
        else:
            select_sample = self.sample_changer.select_sample_without_qr
        return select_sample(
            sample_index, autoTuningAllowed=self.autotune_qrreader_per == "sample"
        )

    def init_workflow(self, with_autocalibration: bool = False):
        if with_autocalibration:
            basename = "streamline_with_calib"
        else:
            basename = "streamline_without_calib"
        filename = f"{basename}.json"

        dirname = self._get_workflows_dir(current_session.scan_saving.filename)
        destination = os.path.join(dirname, filename)
        if not os.path.exists(destination):
            os.makedirs(dirname, exist_ok=True)
            source = resource_filename("streamline", filename)
            shutil.copyfile(source, destination)

        self.workflow = destination
        print(f"Active data processing workflow: {destination}")

    @property
    def workflow_has_calib(self):
        return self.workflow and "with_calib" in self.workflow

    @property
    def workflow_has_flatfield(self):
        return self.workflow and "with_flat" in self.workflow

    def _set_calibration_scan(self, scan_info: ScanInfo):
        if not scan_info.filename:
            print("Cannot use as calibration because no data was collected")
            return
        info = {
            "image": self._get_image_url(scan_info),
            "gallery_directory": self._get_gallery_directory(scan_info.filename),
        }
        position = self._get_calibration_position()
        if self.calibration_scans is None:
            self.calibration_scans = dict()
        self.calibration_scans[position] = info

    def _trigger_processing(self, scan_info: ScanInfo, processed_metadata: dict):
        if not scan_info.filename:
            print("Cannot trigger workflow because no data was collected")
            return
        args, kwargs = self._job_arguments(scan_info, processed_metadata)
        submit(args=args, kwargs=kwargs, queue=self.queue)

    @contextmanager
    def run_context(self):
        self.sample_changer.translation.on()
        self.sample_changer.vibration_speed = self.vibration_speed_during_scan
        elog_print("Start streamline run")
        try:
            yield
        finally:
            self.sample_changer.vibration_speed = 0
            elog_print("End streamline run")

    def _process_sample(
        self,
        qrcode: str,
        scan_args: tuple,
        scan_kwargs: dict,
        is_calibration: bool = False,
    ):
        try:
            with self._verify_qrcode(qrcode) as qrcode:
                has_qrcode = qrcode != self._qrcode_error

                if not has_qrcode and self.skip_when_no_qr_code:
                    elog_print("SKIP SAMPLE (NO QR-CODE)")
                    return

                self._newsample(qrcode)

                self._set_scan_metadata(scan_args, scan_kwargs)
                self._set_raw_dataset_metadata(scan_args, scan_kwargs)

                scan = self.measure_sample(
                    *scan_args, has_qrcode=has_qrcode, **scan_kwargs
                )

                scan_info = self._get_scan_info(scan)
                if is_calibration:
                    self._set_calibration_scan(scan_info)

                if self.trigger_workflows:
                    processed_metadata = self._get_processed_dataset_metadata(scan_args)
                    if self.dryrun:
                        print("Dry-run: skip workflow triggering")
                    else:
                        self._trigger_processing(scan_info, processed_metadata)

                if is_calibration:
                    elog_print(
                        f"Streamline calibrant {self.calibrant}: {current_session.scan_saving.filename}"
                    )
        finally:
            setup_globals.enddataset()

    def qr_read(self) -> str:
        return self.sample_changer.qr_read(
            autoTuningAllowed=self.autotune_qrreader_per == "sample"
        )

    @property
    def _qrcode_error(self) -> str:
        return self.sample_changer.qrreader.QRCODE_NOT_READABLE

    def tune_qrreader(self, force=False) -> str:
        self.sample_changer.tune_qrreader(force=force)

    def tune_qrreader_for_baguette(self) -> None:
        for _ in self.sample_changer.iterate_samples_without_qr():
            qrcode = self.tune_qrreader()
            if qrcode != self._qrcode_error:
                break
        else:
            print("QR-reader tuning failed when loading the baguette")

    @contextmanager
    def _verify_qrcode(self, qrcode: str) -> Generator[str, None, None]:
        """Check the QR-code before (yields the new code when it changed)
        and check the QR-code after (raises and exception when it changed)"""
        if not self.verify_qrcode:
            yield qrcode
            return

        qrcode_now = self.qr_read()
        if qrcode_now != qrcode and qrcode_now != self._qrcode_error:
            print(
                f"Reading the QR-code twice gives first '{qrcode}' and then '{qrcode_now}'"
            )
            qrcode = qrcode_now
        try:
            yield qrcode
        finally:
            qrcode_now = self.qr_read()
            if qrcode_now != qrcode and qrcode_now != self._qrcode_error:
                if qrcode == self._qrcode_error:
                    msg = f"The sample name of dataset '{current_session.scan_saving.filename}' is '{qrcode_now}' (read at the end of the dataset)"
                    elog_print(msg)
                else:
                    msg = f"The sample name of dataset '{current_session.scan_saving.filename}' might be '{qrcode_now}' (read at the end of the dataset)"
                    elog_print(msg)
                    raise RuntimeError(msg)

    def _newsample(self, qrcode: str) -> None:
        setup_globals.newsample(qrcode)
        setup_globals.newdataset()

    def _set_raw_dataset_metadata(self, scan_args: tuple, scan_kwargs: dict) -> None:
        for k, v in self._get_raw_dataset_metadata(scan_args).items():
            current_session.scan_saving.dataset[k] = v

    def _set_scan_metadata(self, scan_args: tuple, scan_kwargs: dict) -> None:
        scan_info = self._get_scan_metadata()
        if scan_info:
            scan_kwargs["scan_info"] = scan_info

    def _get_scan_metadata(self) -> dict:
        return self._technique_metadata.get_scan_info()

    def _get_raw_dataset_metadata(self, scan_args: tuple) -> dict:
        metadata = self._technique_metadata.get_dataset_metadata()
        if self.energy_name:
            metadata["HTXRPD_energy"] = getattr(
                setup_globals, self.energy_name
            ).position
        if scan_args and isinstance(scan_args[0], Number):
            metadata["HTXRPD_exposureTime"] = scan_args[0]
        speed = self.vibration_speed_during_scan
        if speed is not None:
            metadata["HTXRPD_sampleVibration"] = speed
        position = self._get_calibration_position()
        if position is not None:
            metadata["HTXRPD_distance"] = position
        return metadata

    def _get_processed_dataset_metadata(self, scan_args: tuple) -> dict:
        metadata = self._technique_metadata.get_dataset_metadata()
        metadata["Sample_name"] = current_session.scan_saving.dataset["Sample_name"]
        return metadata

    def _get_calibration_position(self) -> Optional[Number]:
        if self.calibration_motor:
            return getattr(setup_globals, self.calibration_motor).position

    def _get_calibration(self) -> dict:
        calibration_scans = self.calibration_scans
        if not calibration_scans:
            return dict()
        position = self._get_calibration_position()
        if position is not None:
            positions = [p for p in calibration_scans if p is not None]
            if positions:
                idx = (numpy.abs(numpy.array(positions) - position)).argmin()
                position = positions[idx]
        return calibration_scans.get(position, dict())

    def _get_scan_info(self, scan) -> ScanInfo:
        if scan is None:
            return ScanInfo(filename="", scan_nb=0)
        if isinstance(scan, ScanInfo):
            return scan
        filename = scan.scan_info.get("filename")
        scan_nb = scan.scan_info.get("scan_nb")
        return ScanInfo(filename=filename, scan_nb=scan_nb)

    def _get_image_url(self, scan_info: ScanInfo) -> str:
        url = f"silx://{scan_info.filename}?path=/{scan_info.scan_nb}.1/measurement/{self.detector_name}"
        image_slice = self.image_slice
        if image_slice is not None:
            image_slice = str(image_slice)
            image_slice = re.sub(r"[\s\(\)]+", "", image_slice)
            url = f"{url}&slice={image_slice}"
        return url

    def _get_output_dir(self, dataset_filename: str) -> str:
        return os.path.join(
            directories.get_processed_dir(dataset_filename), "streamline"
        )

    def _get_transient_dirname(self, dataset_filename: str) -> str:
        return directories.get_nobackup_dir(dataset_filename)

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        return directories.get_workflows_dir(dataset_filename)

    def _get_output_dirname(self, dataset_filename: str) -> str:
        filename = os.path.basename(dataset_filename)
        return os.path.join(
            self._get_output_dir(dataset_filename), os.path.splitext(filename)[0]
        )

    def _get_gallery_dirname(self, dataset_filename: str) -> str:
        return os.path.join(self._get_output_dirname(dataset_filename), "gallery")

    def _get_hdf5_output_filename(self, dataset_filename: str) -> str:
        return os.path.join(
            self._get_output_dirname(dataset_filename),
            os.path.basename(dataset_filename),
        )

    def _get_ascii_output_filename(self, dataset_filename: str, unit: str) -> str:
        basename, _ = os.path.splitext(os.path.basename(dataset_filename))
        return os.path.join(
            self._get_output_dirname(dataset_filename), f"{basename}_{unit}.xye"
        )

    def _get_gallery_directory(self, dataset_filename: str) -> str:
        return self._get_gallery_dirname(dataset_filename)

    def _get_workflow_save_filename(self, dataset_filename: str) -> str:
        basename = os.path.basename(self.workflow)
        return os.path.join(
            self._get_output_dirname(dataset_filename),
            basename,
        )

    def _get_workflow_upload_parameters(
        self, dataset_filename: str, processed_metadata: dict
    ) -> Optional[dict]:
        raw = os.path.dirname(dataset_filename)
        dataset = "integrate"
        scan_saving = current_session.scan_saving
        proposal = scan_saving.proposal_name
        beamline = scan_saving.beamline
        path = self._get_output_dirname(dataset_filename)
        return {
            "beamline": beamline,
            "proposal": proposal,
            "dataset": dataset,
            "path": path,
            "raw": [raw],
            "metadata": processed_metadata,
        }

    def _job_arguments(self, scan_info: ScanInfo, processed_metadata: dict):
        """Arguments for the workflow execution"""
        self._raise_when_missing("workflow")
        if self.workflow_has_calib:
            self._raise_when_missing("calibration_scans", "calibrant")

        inputs = list()

        integrate_image_url = self._get_image_url(scan_info)

        # Configuration
        if self.integration_options:
            inputs.append(
                {
                    "task_identifier": "PyFaiConfig",
                    "name": "integration_options",
                    "value": self.integration_options.to_dict(),
                }
            )
        if self.pyfai_config:
            inputs.append(
                {
                    "task_identifier": "PyFaiConfig",
                    "name": "filename",
                    "value": self.pyfai_config,
                }
            )
        if self.calibrant:
            inputs.append(
                {
                    "task_identifier": "PyFaiConfig",
                    "name": "calibrant",
                    "value": self.calibrant,
                }
            )

        # Calibration
        if self.workflow_has_calib:
            calibration = self._get_calibration()
            if not calibration:
                raise RuntimeError("no valid calibration found")

            inputs += task_inputs(
                task_identifier="CalibrateSingle",
                inputs={
                    "image": calibration["image"],
                    "fixed": ["energy"],
                    "robust": False,
                    "ring_detector": self.calib_ring_detector_name,
                },
            )
            inputs += task_inputs(
                task_identifier="DiagnoseCalibrateSingleResults",
                inputs={
                    "image": calibration["image"],
                    "filename": os.path.join(
                        calibration["gallery_directory"], "ring_detection.png"
                    ),
                },
            )

            if calibration["image"] == integrate_image_url and self.calibrant:
                inputs += [
                    {
                        "task_identifier": "DiagnoseIntegrate1D",
                        "name": "calibrant",
                        "value": self.calibrant,
                    },
                ]

        # Integration
        inputs += task_inputs(
            task_identifier="Integrate1D",
            inputs={
                "image": integrate_image_url,
            },
        )
        inputs += task_inputs(
            task_identifier="SaveNexusPattern1D",
            inputs={
                "url": self._get_hdf5_output_filename(scan_info.filename),
                "bliss_scan_url": scan_info.url,
            },
        )

        # Different outputs depending on the unit
        detector_name = self.detector_name
        for unit in ("q", "2th"):
            inputs += task_inputs(
                task_identifier="SaveNexusPattern1D",
                label=f"save_{unit}_hdf5",
                inputs={
                    "nxprocess_name": f"{detector_name}_integrate_{unit}",
                    "nxmeasurement_name": f"{detector_name}_integrated_{unit}",
                    "metadata": {
                        f"{detector_name}_integrate_{unit}": {
                            "configuration": {"workflow": self.workflow}
                        }
                    },
                },
            )
            inputs.append(
                {
                    "task_identifier": "SaveAsciiPattern1D",
                    "label": f"save_{unit}_ascii",
                    "name": "filename",
                    "value": self._get_ascii_output_filename(scan_info.filename, unit),
                }
            )

        inputs += [
            {
                "task_identifier": "DiagnoseIntegrate1D",
                "name": "filename",
                "value": os.path.join(
                    self._get_gallery_directory(scan_info.filename),
                    "integrate.png",
                ),
            },
        ]

        # Job arguments
        args = (self.workflow,)
        convert_destination = self._get_workflow_save_filename(scan_info.filename)
        upload_parameters = self._get_workflow_upload_parameters(
            scan_info.filename, processed_metadata
        )
        if self.workflow_has_calib:
            varinfo = {
                "root_uri": self._get_transient_dirname(scan_info.filename),
                "scheme": "nexus",
            }
        else:
            varinfo = None
        kwargs = {
            "engine": None,
            "inputs": inputs,
            "varinfo": varinfo,
            "convert_destination": convert_destination,
            "upload_parameters": upload_parameters,
            "save_options": {"indent": 2},
        }
        return args, kwargs

import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ewoksjob.client import submit

from ..bliss_globals import current_session
from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessor
from ..processor import BlissScanType
from ..utils import directories

_DEFAULT_USER_PARS: Dict[str, Any] = {
    "flip_ud": False,
    "flip_lr": False,
    "wavelength": 0.1,
    "distance": 100,
    "beam": [1000, 1100],
    "polarization": 0.99,
    "kappa": 0,
    "alpha": 50,
    "theta": 0,
    "phi": 0,
    "omega": "",
    "rotation": 180,
    "dummy": -1,
    "offset": 1,
    "dry_run": False,
    "calc_mask": False,
}

_DEFAULT_SCAN_PARS: Dict[str, Any] = {
    "images": "",
    "output": "",
}


class Id15bEiger2Crysalis(
    BaseProcessor,
    parameters=[
        ParameterInfo("queue", category="workflows", deprecated_names=["worker"]),
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo(
            "lima_name",
            category="Eiger2Crysalis",
            doc="Lima name of the camera: (i.e. eiger)",
        ),
        ParameterInfo(
            "scan_parameters",
            category="Eiger2Crysalis",
            doc="Derived from scan and motors",
        ),
        ParameterInfo(
            "user_parameters", category="Eiger2Crysalis", doc="Specify explicitly"
        ),
        ParameterInfo(
            "ini_file",
            category="ExtraFiles",
            doc="CrysalisExpSettings.ini path",
        ),
        ParameterInfo(
            "par_file",
            category="ExtraFiles",
            doc=".par file path",
        ),
        ParameterInfo(
            "set_file",
            category="ExtraFiles",
            doc=".set file path",
        ),
        ParameterInfo(
            "ccd_file",
            category="ExtraFiles",
            doc=".ccd file path",
        ),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("trigger_at", "END")
        defaults.setdefault("workflow", "")
        defaults.setdefault("user_parameters", _DEFAULT_USER_PARS)
        defaults.setdefault("scan_parameters", _DEFAULT_SCAN_PARS)
        defaults.setdefault("crysalis_ini", "")

        super().__init__(config=config, defaults=defaults)

    def _info_categories(self) -> Dict[str, dict]:
        self.update_scan_parameters()
        return super()._info_categories()

    def update_scan_parameters(self, scan: Any = None) -> None:
        scan_parameters = dict()
        if scan:
            scan_parameters["images"] = self.get_lima_filenames(scan)
            scan_parameters["output"] = self.get_output_path(scan)
            scan_parameters["processed_output"] = self.get_processed_output_path(scan)
        self.scan_parameters.update(scan_parameters)
        return scan_parameters

    def get_filename(self, scan: BlissScanType) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def get_lima_name(self, scan: BlissScanType) -> List[str]:
        channels = scan.scan_info.get("channels", dict())
        if f"{self.lima_name}:image" in channels:
            return self.lima_name
        else:
            raise AssertionError(f"{self.lima_name} detector not found.")

    def get_output_path(self, scan: BlissScanType) -> str:
        scan_nb = scan.scan_info["scan_nb"]
        dataset_processed_dir = get_dataset_processed_dir(self.get_filename(scan))
        scan_processed_dir = os.path.join(dataset_processed_dir, f"scan{scan_nb:04d}")
        dataset_name = os.path.basename(dataset_processed_dir)
        output = os.path.join(
            scan_processed_dir, f"{dataset_name}_{scan_nb:04d}" + "_1_{index}.esperanto"
        )
        return output

    def get_processed_output_path(self, scan: BlissScanType) -> str:
        scan_nb = scan.scan_info["scan_nb"]
        dataset_processed_dir = get_dataset_processed_dir(self.get_filename(scan))
        scan_processed_dir = os.path.join(dataset_processed_dir, f"scan{scan_nb:04d}")
        dataset_name = os.path.basename(dataset_processed_dir)
        output = os.path.join(scan_processed_dir, f"{dataset_name}_{scan_nb:04d}")
        return output

    def workflow_destination(self, scan) -> str:
        return f"{self.get_processed_output_path(scan)}.json"

    def get_lima_filenames(self, scan: BlissScanType) -> List[str]:
        scan_number = scan.scan_number
        lima_files = [
            f"{scan.scan_saving.images_path.format(scan_number=scan_number, img_acq_device=self.lima_name)}0000.h5"
        ]
        return lima_files

    def get_omega(self, scan: BlissScanType) -> str:
        """
        Provide the omega parameter as a formatted string based on scan info.

        The scan is assumed to be centered around zero.
        """
        # Extract scan parameters.
        start = scan.scan_info["instrument"]["fscan_parameters"]["start_pos"]
        step = scan.scan_info["instrument"]["fscan_parameters"]["step_size"]

        return f"{start}+index*{step}"

    def get_scan_parameters(self, scan: BlissScanType) -> Dict[str, Any]:
        scan_parameters = dict()
        scan_parameters["omega"] = self.get_omega(scan)
        scan_parameters["exposure_time"] = scan.scan_info["instrument"][
            "fscan_parameters"
        ]["acq_time"]
        return scan_parameters

    def get_run_parameters(self, scan: BlissScanType) -> Dict[str, Any]:
        return {
            "count": scan.scan_info["npoints"],
            "omega": 0,
            "omega_start": scan.scan_info["instrument"]["fscan_parameters"][
                "start_pos"
            ],
            "omega_end": scan.scan_info["instrument"]["fscan_parameters"]["start_pos"]
            + scan.scan_info["npoints"]
            * scan.scan_info["instrument"]["fscan_parameters"]["step_size"],
            "pixel_size": 0.075,
            "omega_runs": None,
            "theta": 0,
            "kappa": 0,
            "phi": 0,
            "domega": scan.scan_info["instrument"]["fscan_parameters"]["step_size"],
            "dtheta": 0,
            "dkappa": 0,
            "dphi": 0,
            "center_x": self.user_parameters["beam"][0],
            "center_y": self.user_parameters["beam"][1],
            "alpha": 50,
            "dist": self.user_parameters["distance"],
            "l1": self.user_parameters["wavelength"],
            "l2": self.user_parameters["wavelength"],
            "l12": self.user_parameters["wavelength"],
            "b": self.user_parameters["wavelength"],
            "mono": 0.99,
            "monotype": "SYNCHROTRON",
            "chip": [1024, 1024],
            "Exposure_time": scan.scan_info["instrument"]["fscan_parameters"][
                "acq_time"
            ],
        }

    def get_icat_metadata(self, scan):
        metadata = {
            "Sample_name": scan.scan_info["dataset_metadata_snapshot"]["Sample_name"],
            "SCXRD_sample_detector_distance": self.user_parameters["distance"] * 1e-3,
            "SCXRD_beam_center_x": self.user_parameters["beam"][0],
            "SCXRD_beam_center_y": self.user_parameters["beam"][1],
            "InstrumentMonochromator_wavelength": self.user_parameters["wavelength"],
            # "SCXRD_detector_tilts" : [0,0,0],
            "SCXRD_rotation_axis": "omega",
            "SCXRD_rotation_range": scan.scan_info["npoints"]
            * scan.scan_info["instrument"]["fscan_parameters"]["step_size"],
            "SCXRD_rotation_step": scan.scan_info["instrument"]["fscan_parameters"][
                "step_size"
            ],
            "SCXRD_exposure_time": scan.scan_info["instrument"]["fscan_parameters"][
                "acq_time"
            ],
        }
        return metadata

    def get_inputs(self, scan: BlissScanType) -> List[Dict[str, Any]]:
        parameters = self.user_parameters.to_dict()
        parameters.update(self.update_scan_parameters(scan))
        parameters.update(self.get_scan_parameters(scan))
        icat_metadata = self.get_icat_metadata(scan)

        inputs = []
        for key, value in parameters.items():
            inputs.append(
                {
                    "task_identifier": "Eiger2Crysalis",
                    "name": key,
                    "value": value,
                }
            )
        inputs += [
            {
                "id": "1",
                "task_identifier": "CreateIniFiles",
                "name": "ini_file",
                "value": self.ini_file,
            },
            {
                "id": "2",
                "task_identifier": "CreateSetCcdFiles",
                "name": "ccd_set_file",
                "value": self.ccd_file,
            },
            {
                "id": "3",
                "task_identifier": "CreateSetCcdFiles",
                "name": "ccd_set_file",
                "value": self.set_file,
            },
            {
                "id": "4",
                "task_identifier": "CreateRunFiles",
                "name": "run_parameters",
                "value": self.get_run_parameters(scan),
            },
            {
                "id": "5",
                "task_identifier": "CreateParFiles",
                "name": "par_file",
                "value": self.par_file,
            },
            {
                "id": "6",
                "task_identifier": "AverageFrames",
                "name": "images",
                "value": parameters["images"],
            },
            {
                "id": "7",
                "task_identifier": "DataPortal",
                "name": "metadata",
                "value": icat_metadata,
            },
        ]
        return inputs

    def get_submit_arguments(self, scan: BlissScanType) -> Dict[str, Any]:
        return {
            "inputs": self.get_inputs(scan),
            "outputs": [{"all": "False"}],
        }

    def run_conversion(self, scan: BlissScanType) -> None:
        """Executes on given scan"""
        if "fscan" in scan.scan_info["type"] and self.get_lima_name(scan):
            kwargs = self.get_submit_arguments(scan)
            kwargs["convert_destination"] = self.workflow_destination(scan)
            submit(args=(self.workflow,), kwargs=kwargs, queue=self.queue)

    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> None:
        self.run_conversion(scan)


def get_dataset_processed_dir(
    dataset_filename: str,
) -> str:  # Temporary, waiting for !173 to be merged
    root = directories.get_processed_dir(dataset_filename)
    collection = os.path.basename(directories.get_collection_dir(dataset_filename))
    dataset = os.path.basename(directories.get_dataset_dir(dataset_filename))
    return os.path.join(root, collection, dataset)

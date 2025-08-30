import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..persistent.parameters import ParameterInfo
from ..resources import resource_filename
from ..utils.pyfai import read_config
from ..xrpd.processor import BlissScanType
from ..xrpd.processor import XrpdProcessor
from ..xrpd.processor import _get_scan_memory_url

logger = logging.getLogger(__name__)

SLURM_JOB_PARAMETERS_INTEGRATE = {
    "name": "ID13_pyFAI-integrate",
    "partition": "gpu",
    "time": "01:00:00",
    "tasks_per_node": 1,
    "cpus_per_task": 1,
    "memory_per_cpu": "50G",
    "tres_per_job": "gres/gpu:1",
    "constraints": "l40s",
}

SLURM_JOB_PARAMETERS_BACKGROUND = {
    "name": "ID13_spi-background",
    "partition": "nice",
    "time": "02:00:00",
    "tasks_per_node": 1,
    "cpus_per_task": 32,
    "memory_per_cpu": "2G",
    "tres_per_job": None,
    "constraints": None,
}

SLURM_JOB_PARAMETERS_CNMF = {
    "name": "ID13_spi-CNMF",
    "partition": "gpu",
    "time": "01:00:00",
    "tasks_per_node": 1,
    "cpus_per_task": 1,
    "memory_per_cpu": "50G",
    "tres_per_job": "gres/gpu:1",
    "constraints": "l40s",
}

QUEUE_GPU_ID13 = "lid13gpu3"
QUEUE_SLURM_ID13 = "lid13gpu3_slurm"
WORKER_MODULE = "scattering"
PRE_SCRIPT = "module load {WORKER_MODULE}; python3 -m ewoksid13.scripts.utils.slurm_python_pre_script"
PYTHON_CMD = "python3"
POST_SCRIPT = "python3 -m ewoksid13.scripts.utils.slurm_python_post_script"


class Id13XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
        ParameterInfo("workflow_juno", category="workflows"),
        ParameterInfo("current_workflow", category="workflows"),
        ParameterInfo("queue_slurm", category="workflows"),
        ParameterInfo("normalization_counter", category="Processing"),
        ParameterInfo("do_diffmap", category="Processing"),
        ParameterInfo("do_average", category="Processing"),
        ParameterInfo("do_stackedf", category="Processing"),
        ParameterInfo("average_reference", category="Processing"),
        ParameterInfo("save_external_files", category="Processing"),
        ParameterInfo("radial_limits", category="Processing"),
        ParameterInfo("directory_cif_phases", category="Processing"),
        ParameterInfo("do_background_removal", category="Processing"),
        ParameterInfo("do_cnmf", category="Processing"),
        ParameterInfo("do_phase_inference", category="Processing"),
        ParameterInfo("inference_weights_filename", category="Processing"),
        ParameterInfo("submit_to_slurm_integration", category="Slurm"),
        ParameterInfo("submit_to_slurm_neuralnetwork", category="Slurm"),
    ],
):
    DEFAULT_LIMA_URL_TEMPLATE: Optional[str] = (
        "{dirname}/scan{scan_number_as_str}/{images_prefix}{{file_index}}.h5::/entry_0000/measurement/data"
    )
    DEFAULT_WORKFLOW_JUNO: Optional[str] = resource_filename("id13", "juno.json")

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("current_workflow", "")
        defaults.setdefault("queue_slurm", QUEUE_SLURM_ID13)
        defaults.setdefault("save_scans_separately", True)
        defaults.setdefault("do_diffmap", False)
        defaults.setdefault("normalization_counter", None)
        defaults.setdefault("do_average", False)
        defaults.setdefault("do_stackedf", False)
        defaults.setdefault("average_reference", "hydrocerussite")
        defaults.setdefault("save_external_files", False)
        defaults.setdefault("workflow_juno", self.DEFAULT_WORKFLOW_JUNO)
        defaults.setdefault("do_background_removal", False)
        defaults.setdefault("radial_limits", None)
        defaults.setdefault("do_cnmf", False)
        defaults.setdefault("directory_cif_phases", None)
        defaults.setdefault("do_phase_inference", False)
        defaults.setdefault("inference_weights_filename", "")
        defaults.setdefault("submit_to_slurm_integration", False)
        defaults.setdefault("submit_to_slurm_spi", True)
        super().__init__(config=config, defaults=defaults)

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.pyfai_config

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        if self.pyfai_config:
            integration_options = read_config(filename=self.pyfai_config)
        else:
            integration_options = dict()
        if self.integration_options:
            integration_options.update(self.integration_options.to_dict())
        return integration_options

    def get_integrate_inputs(
        self, scan: BlissScanType, lima_name: str, task_identifier: str
    ) -> List[dict]:
        eval_dict = {"img_acq_device": lima_name, "scan_number": scan.scan_number}
        images_prefix = scan.scan_saving.images_prefix.format(**eval_dict)
        original_template_args = self.lima_url_template_args.to_dict()
        self.lima_url_template_args["images_prefix"] = images_prefix
        self.lima_url_template_args["scan_number_as_str"] = scan.scan_number
        try:
            return super().get_integrate_inputs(scan, lima_name, task_identifier)
        finally:
            self.lima_url_template_args = original_template_args

    def get_external_output_filename(self, scan: BlissScanType, lima_name: str):
        external_output_filename = self.external_output_filename(
            scan=scan, lima_name=lima_name
        )
        if not external_output_filename:
            scan_nb = scan.scan_info.get("scan_nb")
            master_output_filename = self.master_output_filename(scan)
            external_output_filename = master_output_filename.replace(
                ".h5", f"_{scan_nb:04d}.h5"
            )
        return external_output_filename

    def get_inputs(self, scan: BlissScanType, lima_name: str) -> List[dict]:
        """Additional inputs for the Id13 XrpdProcessor."""
        inputs = super().get_inputs(scan=scan, lima_name=lima_name)
        inputs += self.get_diff_extra_inputs(scan=scan, lima_name=lima_name)
        inputs += self.get_neuralnetwork_inputs(scan=scan, lima_name=lima_name)
        return inputs

    def get_diff_extra_inputs(
        self,
        scan: BlissScanType,
        lima_name: str,
    ) -> List[dict]:
        """Get additional inputs for the diffmap, average, and stacked EDF tasks."""
        filename = self.get_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        master_output_filename = self.master_output_filename(scan)
        external_output_filename = self.get_external_output_filename(
            scan=scan, lima_name=lima_name
        )
        external_output_filename_edf = external_output_filename.replace(".h5", ".edf")

        if self.save_external_files:
            external_output_filename = external_output_filename
        else:
            external_output_filename = master_output_filename

        params = {
            "CreateDiffMapFile": {
                "master_filename": filename,
                "scan_nb": scan_nb,
                "output_filename": master_output_filename,
                "external_output_filename": external_output_filename,
                "integration_options": self.get_integration_options(
                    lima_name=lima_name
                ),
                "lima_name": lima_name,
                "do_diffmap": self.do_diffmap,
                "scan_memory_url": _get_scan_memory_url(scan),
                "normalization_counter": self.normalization_counter,
                "processing_info": self.get_saving_info(scan),
            },
            "AverageIntegration": {
                "master_filename": filename,
                "scan_nb": scan_nb,
                "lima_name": lima_name,
                "output_filename": master_output_filename,
                "external_output_filename": external_output_filename,
                "do_average": self.do_average,
                "reference": self.average_reference,
                "scan_memory_url": _get_scan_memory_url(scan),
                "normalization_counter": self.normalization_counter,
                "processing_info": self.get_saving_info(scan),
            },
            "StackToEdf": {
                "do_stackedf": self.do_stackedf,
                "external_output_filename": external_output_filename_edf,
                "processing_info": self.get_saving_info(scan),
            },
        }

        return [
            {"name": name, "value": value, "task_identifier": task_id}
            for task_id, task_params in params.items()
            for name, value in task_params.items()
        ]

    def get_neuralnetwork_inputs(
        self, scan: BlissScanType, lima_name: str
    ) -> List[dict]:
        """Get additional inputs for the neural network (spi) tasks: background removal, constrained NMF and phase inference."""
        external_output_filename = self.get_external_output_filename(
            scan=scan, lima_name=lima_name
        )

        params = {
            "BackgroundRemoval": {
                "wavelength": self.get_wavelength(angstroms=True),
                "radial_limits": self.radial_limits,
                "force_training": False,
                "use_neuralnetwork": False,
                "do_background_removal": self.do_background_removal,
                "submit_to_slurm": self.submit_to_slurm_neuralnetwork,
                "destination_file": external_output_filename.replace(
                    ".h5", "_background.json"
                ),
                "slurm_job_parameters": SLURM_JOB_PARAMETERS_BACKGROUND,
                "worker_module": "scattering",
                "wait_to_finish": self.do_cnmf,
                "slurm_celery_queue": self.queue_slurm,
                "processing_info": self.get_saving_info(scan),
            },
            "ConstrainedNMF": {
                "wavelength": self.get_wavelength(angstroms=True),
                "references_directory": self.directory_cif_phases,
                "do_matrix_factorization": self.do_cnmf,
                "radial_limits": self.radial_limits,
                "submit_to_slurm": self.submit_to_slurm_neuralnetwork,
                "destination_file": external_output_filename.replace(
                    ".h5", "_cnmf.json"
                ),
                "slurm_job_parameters": SLURM_JOB_PARAMETERS_CNMF,
                "worker_module": "scattering",
                "wait_to_finish": False,
                "slurm_celery_queue": self.queue_slurm,
                "processing_info": self.get_saving_info(scan),
            },
            "PhaseInference": {
                "do_phase_inference": self.do_phase_inference,
                "references_directory": self.directory_cif_phases,
                "inference_weights_filename": self.inference_weights_filename,
                "processing_info": self.get_saving_info(scan),
            },
        }

        return [
            {"name": name, "value": value, "task_identifier": task_id}
            for task_id, task_params in params.items()
            for name, value in task_params.items()
        ]

    def get_wavelength(self, angstroms: bool = True) -> float:
        """Load the wavelength from the PyFai configuration file."""
        with open(self.pyfai_config) as f:
            config = json.load(f)
        if "wavelength" in config:
            return float(config["wavelength"]) * (1e10 if angstroms else 1)
        if "poni" in config:
            return float(config["poni"]["wavelength"]) * (1e10 if angstroms else 1)

    def _get_workflow(self, scan: BlissScanType) -> Optional[str]:
        """Get the workflow filename for the scan"""
        if scan.scan_info.get("save"):
            self.current_workflow = self.workflow_juno
        else:
            self.current_workflow = self.workflow_without_saving
        return self.current_workflow

    def _set_workflow(self, scan: BlissScanType, filename: str) -> None:
        """Set the workflow filename for the scan"""
        if scan.scan_info.get("save"):
            self.workflow_with_saving = filename
        else:
            self.workflow_without_saving = filename
        self.current_workflow = filename

    def get_submit_arguments(self, scan: BlissScanType, lima_name) -> dict:
        """Additional submit arguments in case of slurm queue, also switch the queue if needed."""
        submit_arguments = super().get_submit_arguments(scan, lima_name)

        if self.submit_to_slurm_integration:
            if self.queue != self.queue_slurm:
                logger.warning(
                    f"Switching queue from {self.queue} to {self.queue_slurm}"
                )
                self.queue = self.queue_slurm
            return {
                **submit_arguments,
                "slurm_arguments": {
                    "parameters": SLURM_JOB_PARAMETERS_INTEGRATE,
                    "pre_script": PRE_SCRIPT.format(WORKER_MODULE=WORKER_MODULE),
                    "python_cmd": PYTHON_CMD,
                    "post_script": POST_SCRIPT,
                },
            }
        return submit_arguments

    def get_saving_info(self, scan: BlissScanType) -> dict:
        return {
            "base_path": scan.scan_saving.base_path,
            "template": scan.scan_saving.template,
            "proposal_dirname": scan.scan_saving.proposal_dirname,
            "beamline": scan.scan_saving.beamline,
            "proposal_session_name": scan.scan_saving.proposal_session_name,
            "collection_name": scan.scan_saving.collection_name,
            "dataset_name": scan.scan_saving.dataset_name,
        }

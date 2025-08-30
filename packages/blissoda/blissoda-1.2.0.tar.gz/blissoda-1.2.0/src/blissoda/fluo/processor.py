import logging
import os
import re
import shutil
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from ewoksjob.client import get_future
from ewoksjob.client import submit

from ..bliss_globals import current_session
from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessor
from ..processor import BlissScanType
from ..resources import resource_filename
from ..utils import directories
from .parameters.fluoxas import fluoxas_workflow_inputs
from .parameters.mosaic_xrfmap import mosaic_xrfmap_workflow_inputs
from .parameters.xrfmap import xrfmap_workflow_inputs

logger = logging.getLogger(__name__)


class FluoProcessor(
    BaseProcessor,
    parameters=[
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo("queue", category="workflows"),
        ParameterInfo("xrf_names", category="data access"),
        ParameterInfo("virtual_axes", category="regrid"),
        ParameterInfo("ignore_axes", category="regrid"),
        ParameterInfo("pymca_configs", category="PyMCA"),
        ParameterInfo("energy_name", category="PyMCA"),
        ParameterInfo("quantification", category="PyMCA"),
        ParameterInfo("norm_counter_name", category="Normalization"),
        ParameterInfo("data_portal_upload", category="data portal"),
    ],
):
    """A class that holds parameters related to online workflow triggering for PyMCA."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("workflow", "")
        defaults.setdefault("xrf_names", [])
        defaults.setdefault("quantification", True)
        defaults.setdefault("virtual_axes", {})
        defaults.setdefault("ignore_axes", [])
        defaults.setdefault("data_portal_upload", False)
        defaults.setdefault("trigger_at", "END")

        super().__init__(config=config, defaults=defaults)

    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> Optional[dict]:
        metadata, _ = self._on_new_scan(scan)
        return metadata

    def _on_new_scan(self, scan: BlissScanType) -> Tuple[Optional[dict], Optional[Any]]:
        """Executed at the end of every scan"""
        future = None
        metadata = None
        if not self.scan_requires_processing(scan):
            return metadata, future

        upload_parameters = None
        if self.data_portal_upload and scan.scan_info.get("save"):
            # It is allowed to upload the same processed directory more than once.
            upload_parameters = self._get_workflow_upload_parameters(scan)

        # Submit arguments
        workflow_base, inputs = self.get_workflow_and_inputs(scan)
        workflow = self.get_workflow_dst(scan, workflow_base)
        kwargs = self.get_submit_arguments(scan, inputs)
        if scan.scan_info.get("save"):
            kwargs["convert_destination"] = directories.workflow_destination(scan)
        if upload_parameters:
            kwargs["upload_parameters"] = upload_parameters

        # Trigger workflow from the current process.
        print("Starting workflow", workflow, kwargs)
        future = submit(args=(workflow,), kwargs=kwargs, queue=self.queue)
        future = get_future(future.uuid)

        return metadata, future

    def get_submit_arguments(self, scan: BlissScanType, inputs: List[dict]) -> dict:
        return {
            "inputs": inputs,
            "outputs": [{"all": False}],
        }

    def _set_workflow(self, scan: BlissScanType, filename) -> None:
        """Set the workflow filename for the scan"""
        self.workflow = filename

    def get_filename(self, scan: BlissScanType) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def _get_axis_units_from_scan(
        self, virtual_axes: Dict[str, str], scan: BlissScanType
    ):
        units = scan.scan_info["positioners"]["positioners_units"]
        units_dict = {}
        for virtual_axis in virtual_axes:
            for motor_name in _get_motors_from_expression(virtual_axis):
                motor_unit = units[motor_name]
                if motor_unit is None:
                    logger.warning(
                        f"Unit for motor `{motor_name}` is not set in beacon!"
                    )
                else:
                    units_dict[motor_name] = motor_unit

        return units_dict

    def get_workflow_and_inputs(self, scan: BlissScanType):
        scan_info = scan.scan_info

        if scan_info.get("is_xrfmap_patch"):
            concat_filename = directories.master_output_filename(scan).replace(
                ".h5", "_concat.h5"
            )
            scan_ranges = _get_scan_ranges_from_sequence(scan)

            workflow, inputs = mosaic_xrfmap_workflow_inputs(
                filenames=[self.get_filename(scan)],
                output_root_uri=self.master_output_url(scan),
                scan_ranges=[scan_ranges],
                concat_bliss_scan_uri=f"{concat_filename}::/{scan_ranges[0]}.1",
                config_filenames=self.pymca_configs,
                detector_names=bliss_counter_to_h5_name(self.xrf_names),
                counter_name=self.norm_counter_name,
                energy_name=self.energy_name,
                quantification=self.quantification,
                virtual_axes=self.virtual_axes,
                ignore_axes=self.ignore_axes,
                axis_units=self._get_axis_units_from_scan(
                    self.virtual_axes.values(), scan
                ),
            )
        elif scan_info.get("is_fluoxas"):
            workflow, inputs = fluoxas_workflow_inputs(
                filenames=[self.get_filename(scan)],
                output_root_uri=self.master_output_url(scan),
                scan_ranges=[_get_scan_ranges_from_sequence(scan)],
                config_filenames=self.pymca_configs,
                detector_names=bliss_counter_to_h5_name(self.xrf_names),
                counter_name=self.norm_counter_name,
                energy_name=self.energy_name,
                quantification=self.quantification,
                virtual_axes=self.virtual_axes,
                ignore_axes=self.ignore_axes,
                axis_units=self._get_axis_units_from_scan(
                    self.virtual_axes.values(), scan
                ),
            )
        else:
            workflow, inputs = xrfmap_workflow_inputs(
                filename=self.get_filename(scan),
                output_root_uri=self.master_output_url(scan),
                scan_number=scan_info.get("scan_nb"),
                config_filenames=self.pymca_configs,
                detector_names=bliss_counter_to_h5_name(self.xrf_names),
                counter_name=self.norm_counter_name,
                energy_name=self.energy_name,
                quantification=self.quantification,
                virtual_axes=self.virtual_axes,
                ignore_axes=self.ignore_axes,
                axis_units=self._get_axis_units_from_scan(
                    self.virtual_axes.values(), scan
                ),
            )
        return workflow + ".ows", inputs

    def get_workflow_dst(
        self, scan: BlissScanType, workflow_base: str
    ) -> Optional[str]:
        """Get the workflow to execute for the scan and ensure it is located
        in the proposal directory for user reference and worker accessibility.
        """
        src_file = resource_filename("fluo", workflow_base)
        if src_file is None:
            return

        dataset_filename = self.get_filename(scan)
        workflow_directory = self._get_workflows_dir(dataset_filename)
        dst_file = os.path.join(workflow_directory, os.path.basename(src_file))
        if src_file != dst_file:
            self._set_workflow(scan, dst_file)

        if not os.path.exists(dst_file):
            os.makedirs(workflow_directory, exist_ok=True)
            shutil.copyfile(src_file, dst_file)

        return dst_file

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        return directories.get_workflows_dir(dataset_filename)

    def add_xrf_names(self, detector, *spectra: Sequence[int]) -> None:
        """Add an xrf detector and its spectra to the processor"""
        xrf_names = set(self.xrf_names)
        for counter in detector.counters:
            if counter.name.startswith("spectrum_det"):
                spectrum_id = int(counter.name.replace("spectrum_det", ""))
                if spectra is None or spectrum_id in spectra:
                    xrf_names.add(counter.fullname)
        self.xrf_names = sorted(xrf_names)

    def clear_xrf_names(self):
        self.xrf_names = []

    def get_xrf_names(self, scan: BlissScanType) -> List[str]:
        # If this is a sequence check the first real scan
        if scan.scan_info.get("is_scan_sequence"):
            channels = scan.streams["SUBSCANS"][0].info.get("channels", dict())
        else:
            channels = scan.scan_info.get("channels", dict())

        return sorted((xrf_name for xrf_name in self.xrf_names if xrf_name in channels))

    def scan_requires_processing(self, scan: BlissScanType) -> bool:
        scan_info = scan.scan_info
        scan_to_process = (
            scan_info.get("is_xrfmap")
            or scan_info.get("is_xrfmap_patch")
            or scan_info.get("is_fluoxas")
        )
        return (
            bool(self.get_xrf_names(scan))
            and bool(scan.scan_info.get("save"))
            and bool(scan_to_process)
        )

    def master_output_url(self, scan: BlissScanType) -> str:
        """URL which can be used to inspect the results after the processing."""
        scan_nb = scan.scan_info.get("scan_nb")
        filename = directories.master_output_filename(scan)
        return f"{filename}::/{scan_nb}.1"

    def _get_workflow_upload_parameters(self, scan: BlissScanType) -> dict:
        raw_directory = os.path.dirname(self.get_filename(scan))
        processed_directory = directories.scan_processed_directory(scan)
        scan_saving = current_session.scan_saving
        metadata = {"Sample_name": scan_saving.dataset["Sample_name"]}

        return {
            "beamline": scan_saving.beamline,
            "proposal": scan_saving.proposal_name,
            "dataset": "integrate",
            "path": processed_directory,
            "raw": [raw_directory],
            "metadata": metadata,
        }


def bliss_counter_to_h5_name(names: List[str]):
    """Mangle bliss counter to h5 dataset name"""
    h5_names = []
    for name in names:
        h5_names.append(name.replace(":", "_").replace("spectrum_det", "det"))
    return h5_names


def _get_motors_from_expression(
    expression: str,
    start_var: str = "<",
    end_var: str = ">",
) -> Tuple[str, str]:
    pattern = rf"{re.escape(start_var)}([^{re.escape(end_var)}]+){re.escape(end_var)}"
    return re.findall(pattern, expression)


def _get_scan_ranges_from_sequence(scan: BlissScanType):
    final_scan = scan.streams["SUBSCANS"][:][-1]
    return (2, final_scan.info["scan_nb"])

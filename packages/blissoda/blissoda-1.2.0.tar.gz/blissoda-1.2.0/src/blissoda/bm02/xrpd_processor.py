import logging
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from esrf_pathlib import ESRFPath
from ewoksutils.task_utils import task_inputs

from ..persistent.parameters import ParameterInfo
from ..processor import BlissScanType
from ..resources import resource_filename
from ..utils.directories import scan_processed_directory
from ..xrpd.processor import XrpdProcessor
from .utils import export_filename_prefix
from .utils import get_current_filename


class Bm02XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("config_filename", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
        ParameterInfo(
            "empty_cell_subtraction_options", category="Empty cell subtraction"
        ),
        ParameterInfo("ascii_export_enabled", category="ASCII export"),
        ParameterInfo("save_as_zip", category="ASCII export"),
        ParameterInfo("max_points", category="ASCII export"),
    ],
):

    DEFAULT_WORKFLOW: Optional[str] = resource_filename(
        "bm02", "integrate_scan_with_saving_subtract_ascii.json"
    )

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("config_filename", {"WOS": "", "D5": ""})
        defaults.setdefault(
            "integration_options",
            {
                "WOS": {
                    "method": "no_csr_cython",
                    "nbpt_rad": 4096,
                    "unit": "q_nm^-1",
                },
                "D5": {
                    "method": "no_csr_cython",
                    "nbpt_rad": 4096,
                    "unit": "q_nm^-1",
                },
            },
        )
        defaults.setdefault(
            "empty_cell_subtraction_options",
            {
                "CdTe": {
                    "enabled": False,
                    "cell_pattern_url": None,
                    "empty_cell_factor": "1",
                },
                "WOS": {
                    "enabled": False,
                    "cell_pattern_url": None,
                    "empty_cell_factor": 1,
                },
            },
        )

        defaults.setdefault("ascii_export_enabled", False)
        defaults.setdefault("save_as_zip", False)
        defaults.setdefault("max_points", 200)

        super().__init__(config=config, defaults=defaults)

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        try:
            return self.config_filename[lima_name]
        except KeyError:
            raise RuntimeError(
                f"Missing pyfai configuration file (poni or json) for '{lima_name}'"
            ) from None

    def get_integration_options(self, lima_name: str) -> dict:
        try:
            return self.integration_options.get(lima_name, {})
        except KeyError:
            raise RuntimeError(
                f"Missing pyfai integration options for '{lima_name}'"
            ) from None

    def _is_save_ascii_enabled(self, scan: BlissScanType, lima_name: str) -> bool:
        if not self.ascii_export_enabled:
            return False

        if "nbpt_azim" in self.get_integration_options(lima_name):
            logging.warning(
                f'2D integrated patterns cannot be exported to ASCII. Disabling ASCII export for scan {scan.scan_info.get("scan_nb")}'
            )
            return False

        npoints = scan.scan_info.get("npoints", float("inf"))
        if npoints >= self.max_points:
            logging.warning(
                f"""
                Disabling ASCII export for scan {scan.scan_info.get("scan_nb")}
                 since its number of points ({npoints}) exceeds the max number ({self.max_points}).
                """
            )
            return False

        return True

    def enable_ascii_export(self):
        self.ascii_export_enabled = True

    def disable_ascii_export(self):
        self.ascii_export_enabled = False

    def _get_ascii_export_inputs(
        self, scan: BlissScanType, lima_name: str
    ) -> List[dict]:
        export_folder = Path(scan_processed_directory(scan)) / "export"
        filename_prefix = export_filename_prefix(scan, lima_name)
        ascii_basename_template = filename_prefix + "_%04d.dat"

        if self.save_as_zip:
            output_filename_template = ascii_basename_template
            output_archive_filename = export_folder / f"{filename_prefix}.zip"
        else:
            output_filename_template = export_folder / ascii_basename_template
            output_archive_filename = ""

        return task_inputs(
            task_identifier="SaveNexusPatternsAsAscii",
            inputs={
                "enabled": self._is_save_ascii_enabled(scan, lima_name),
                "output_filename_template": str(output_filename_template),
                "output_archive_filename": str(output_archive_filename),
            },
        )

    def _is_cell_subtraction_enabled(self, scan: BlissScanType, lima_name: str) -> bool:
        if "nbpt_azim" in self.get_integration_options(lima_name):
            logging.warning(
                f'Cannot subtract empty cell from 2D integrated patterns. Disabling cell subtraction for scan {scan.scan_info.get("scan_nb")}'
            )
            return False

        if lima_name not in self.empty_cell_subtraction_options:
            return False

        return self.empty_cell_subtraction_options[lima_name].get("enabled", False)

    def _get_empty_cell_subtraction_inputs(
        self, scan: BlissScanType, lima_name: str
    ) -> List[dict]:
        inputs = self._get_data_access_inputs("SubtractBackgroundPattern")

        subtraction_options = self.empty_cell_subtraction_options.get(lima_name, {})

        inputs += task_inputs(
            task_identifier="SubtractBackgroundPattern",
            inputs={
                "enabled": self._is_cell_subtraction_enabled(scan, lima_name),
                "background_nxdata_url": subtraction_options.get(
                    "cell_pattern_url", None
                ),
                "background_factor": subtraction_options.get("empty_cell_factor", 1),
            },
        )
        return inputs

    def _data_to_plot_url(self, scan: BlissScanType, lima_name: str):
        if not scan.scan_info.get("save"):
            return None

        output_url = self.online_output_url(scan, lima_name)
        if self._is_cell_subtraction_enabled(scan, lima_name):
            return f"{output_url}/{lima_name}_integrate_subtracted/integrated"
        else:
            return f"{output_url}/{lima_name}_integrate/integrated"

    def set_cell_pattern_url(
        self, sample: str, dataset: str, scan_number: int, detector: str
    ) -> None:

        filename = ESRFPath(get_current_filename())
        cell_filename = filename.replace_fields(
            collection=sample, dataset=dataset
        ).processed_dataset_file

        self.empty_cell_subtraction_options[detector][
            "cell_pattern_url"
        ] = f"{cell_filename}::/{scan_number}.1/{detector}_integrate/integrated"

    def enable_empty_cell_subtraction(self, *detectors):
        for detector_obj in detectors:
            detector: str = detector_obj.name
            if detector not in self.empty_cell_subtraction_options:
                self.empty_cell_subtraction_options[detector] = {}
            self.empty_cell_subtraction_options[detector]["enabled"] = True

            if (
                self.empty_cell_subtraction_options[detector].get("cell_pattern", None)
                is None
            ):
                print(
                    f"Do not forget to set a cell_pattern_url for {detector} now that cell subtraction is enabled!"
                )

    def disable_empty_cell_subtraction(self, *detectors):
        for detector in detectors:
            if detector.name in self.empty_cell_subtraction_options:
                self.empty_cell_subtraction_options[detector.name] = {}
            self.empty_cell_subtraction_options[detector.name]["enabled"] = False

    def get_inputs(self, scan: BlissScanType, lima_name: str) -> List[dict]:
        inputs = super().get_inputs(scan, lima_name)
        inputs += self._get_ascii_export_inputs(scan, lima_name)
        inputs += self._get_empty_cell_subtraction_inputs(scan, lima_name)

        return inputs

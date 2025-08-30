"""Automatic pyfai integration for every scan with saving and plotting"""

import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ewoksutils.task_utils import task_inputs

from ..bliss_globals import setup_globals
from ..import_utils import unavailable_class
from ..persistent.parameters import ParameterInfo
from ..utils import validators
from ..xrpd.processor import XrpdProcessor

try:
    from bliss.common.axis import Axis
except ImportError as ex:
    Axis = unavailable_class(ex)


def is_motor_name(value) -> str:
    if isinstance(value, Axis):
        return str(value.name)
    return str(value)


class Id31XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config", category="PyFai", validator=validators.is_file),
        ParameterInfo("integration_options", category="PyFai"),
        ParameterInfo("flat_enabled", category="Flat-field", validator=bool),
        ParameterInfo("newflat", category="Flat-field", validator=validators.is_file),
        ParameterInfo("oldflat", category="Flat-field", validator=validators.is_file),
        ParameterInfo(
            "ascii_options",
            category="Data saving",
        ),
        ParameterInfo(
            "tomo_enabled",
            category="Data saving/Tomo",
            validator=bool,
        ),
        ParameterInfo(
            "tomo_rot_name",
            category="Data saving/Tomo",
            validator=is_motor_name,
        ),
        ParameterInfo(
            "tomo_y_name",
            category="Data saving/Tomo",
            validator=is_motor_name,
        ),
        ParameterInfo(
            "tomo_scans",
            category="Data saving/Tomo",
        ),
    ],
):

    # Override XrpdProcessor default workflows
    DEFAULT_WORKFLOW = "integrate_with_saving_with_flat.json"
    DEFAULT_WORKFLOW_NO_SAVE = "integrate_without_saving_with_flat.json"

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("queue", "online")
        defaults.setdefault(
            "integration_options",
            {
                "method": "no_csr_ocl_gpu",
                "nbpt_rad": 4096,
                "unit": "q_nm^-1",
            },
        )
        defaults.setdefault(
            "ascii_options",
            {
                "enabled": False,
                "scans": [
                    "ascan",
                    "dscan",
                    "a2scan",
                    "d2scan",
                    "loopscan",
                    "timescan",
                    "sct",
                ],
                "max_npoints": 1000,
            },
        )
        defaults.setdefault("flat_enabled", True)
        defaults.setdefault("newflat", "/data/id31/inhouse/P3/flats.mat")
        defaults.setdefault("oldflat", "/data/id31/inhouse/P3/flats_old.mat")
        defaults.setdefault("tomo_enabled", False)
        defaults.setdefault("tomo_rot_name", "srot")
        defaults.setdefault("tomo_y_name", "saby")
        defaults.setdefault("tomo_scans", ["fscan2d"])

        super().__init__(config=config, defaults=defaults)

        self.workflow_with_saving = self.DEFAULT_WORKFLOW
        self.workflow_without_saving = self.DEFAULT_WORKFLOW_NO_SAVE

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.pyfai_config

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        integration_options = self.integration_options
        if integration_options:
            return integration_options.to_dict()
        return None

    def get_inputs(self, scan, lima_name: str) -> List[dict]:
        inputs = super().get_inputs(scan, lima_name)
        inputs += task_inputs(
            task_identifier="FlatFieldFromEnergy",
            inputs={
                "newflat": self.newflat,
                "oldflat": self.oldflat,
                "energy": setup_globals.energy.position,
                "enabled": self.flat_enabled and lima_name == "p3",
            },
        )

        ascii_basename_template = self._export_filename_prefix(scan) + "_%04d.xye"
        if scan.scan_info.get("npoints", float("inf")) == 1:
            output_filename_template = os.path.join(
                self._export_folder(scan), ascii_basename_template
            )
            output_archive_filename = ""
        else:  # Store ASCII files in a zip file if there is more than one point
            output_filename_template = ascii_basename_template
            output_archive_filename = os.path.join(
                self._export_folder(scan),
                self._export_filename_prefix(scan) + ".zip",
            )
        inputs += task_inputs(
            task_identifier="SaveNexusPatternsAsAscii",
            inputs={
                "enabled": self._is_save_ascii_enabled(scan),
                "output_filename_template": output_filename_template,
                "output_archive_filename": output_archive_filename,
            },
        )

        output_tomo_filename = os.path.join(
            self._export_folder(scan),
            self._export_filename_prefix(scan) + "_tomo.h5",
        )
        scan_nb = scan.scan_info.get("scan_nb")
        inputs += task_inputs(
            task_identifier="SaveNexusPatternsAsId31TomoHdf5",
            inputs={
                "enabled": self._is_save_tomo_enabled(scan),
                "scan_entry_url": f"{self.get_filename(scan)}::/{scan_nb}.1",
                "rot_name": self.tomo_rot_name,
                "y_name": self.tomo_y_name,
                "output_filename": output_tomo_filename,
            },
        )
        return inputs

    def _is_save_tomo_enabled(self, scan) -> bool:
        """Returns whether results need to be exported as tomo for this scan"""
        if not self.tomo_enabled:
            return False

        scan_type = scan.scan_info.get("type", "")
        return scan_type in self.tomo_scans

    def _is_save_ascii_enabled(self, scan) -> bool:
        """Returns whether results need to be exported as ASCII for this scan"""
        if not self.ascii_options:
            return False

        ascii_options = self.ascii_options.to_dict()
        if not ascii_options.get("enabled", False):
            return False

        scan_type = scan.scan_info.get("type", "")
        # sct's scan_type is ct with saving enabled
        if scan_type == "ct" and scan.scan_info.get("save"):
            scan_type = "sct"

        return scan_type in ascii_options.get("scans", []) and (
            0
            < scan.scan_info.get("npoints", float("inf"))
            <= ascii_options.get("max_npoints", 0)
        )

    def _export_filename_prefix(self, scan) -> str:
        """Returns the prefix to use for exported filenames"""
        basename = os.path.basename(self.get_filename(scan))
        stem = os.path.splitext(basename)[0]
        scan_nb = scan.scan_info.get("scan_nb")
        return f"{stem}_{scan_nb:04d}"

    def _export_folder(self, scan) -> str:
        """Returns the folder where to store exported files"""
        return os.path.join(
            self.scan_processed_directory(scan),
            "export",
        )

    def get_workflow(self, scan) -> Optional[str]:
        return self._get_workflow(scan)

    def _get_default_workflow(self, scan) -> Optional[str]:
        # Make sure default workflows are never used
        return self._get_workflow(scan)

    def get_submit_arguments(self, scan, lima_name) -> dict:
        kwargs = super().get_submit_arguments(scan, lima_name)
        kwargs["outputs"] = [
            {"all": False},
            {"name": "nxdata_url", "task_identifier": "IntegrateBlissScan"},
        ]
        kwargs["load_options"] = {"root_module": "ewoksid31.workflows"}
        return kwargs

        # TODO: Redis events don't show up
        handler = {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [
                {
                    "name": "url",
                    "value": "redis://bibhelm:25001/4",
                },
                {"name": "ttl", "value": 86400},
            ],
        }
        kwargs["execinfo"] = {"handlers": [handler]}
        return kwargs

    def enabled_flatfield(self, enable: bool) -> None:
        # Kept for backward compatibility
        self.flat_enabled = enable

    def ensure_workflow_accessible(self, scan) -> None:
        pass

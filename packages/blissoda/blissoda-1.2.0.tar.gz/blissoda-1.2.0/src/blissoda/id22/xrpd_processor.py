from __future__ import annotations

import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from ..persistent.parameters import ParameterInfo
from ..persistent.parameters import autocomplete_property
from ..resources import resource_filename
from ..xrpd.processor import XrpdProcessor

MULTI_RADIAL_BINS = "multi_radial_bins"
AZIMUTHAL_RANGES = "azimuthal_ranges"

logger = logging.getLogger(__name__)


class Id22XrpdProcessor(
    XrpdProcessor,
    parameters=[
        ParameterInfo("pyfai_config", category="PyFai"),
        ParameterInfo("integration_options", category="PyFai"),
        ParameterInfo(MULTI_RADIAL_BINS, category="PyFai"),
        ParameterInfo(AZIMUTHAL_RANGES, category="PyFai"),
    ],
):
    DEFAULT_WORKFLOW = resource_filename("id22", "Sum_then_integrate_with_saving.json")
    MULTI_CONFIG_WORKFLOW = resource_filename(
        "id22", "Sum_then_multiintegrate_with_saving.json"
    )
    DEFAULT_WORKFLOW_NO_SAVE = None

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault(
            "integration_options",
            {
                "method": "no_csr_ocl_gpu",
                "nbpt_rad": 4096,
                "unit": "q_nm^-1",
            },
        )
        defaults.setdefault(MULTI_RADIAL_BINS, None)
        defaults.setdefault(AZIMUTHAL_RANGES, None)
        defaults.setdefault("trigger_at", "END")

        super().__init__(config=config, defaults=defaults)

        # Disable data from memory for now
        # The data structure is indeed different when getting it from file or from memory
        self._set_parameter("data_from_memory", False)

    def get_config_filename(self, lima_name: str) -> Optional[str]:
        return self.pyfai_config

    def get_integration_options(self, lima_name: str) -> Optional[dict]:
        integration_options = self.integration_options
        if integration_options:
            return integration_options.to_dict()
        return None

    def get_inputs(self, scan, lima_name: str) -> List[dict]:
        inputs = super().get_inputs(scan, lima_name)
        inputs += self.get_sum_inputs(scan, lima_name)
        inputs += self.get_save_ascii_inputs(scan, lima_name)
        inputs += self.get_multi_tasks_inputs(scan, lima_name)
        return inputs

    def get_sum_inputs(self, scan, lima_name: str):
        task_identifier = "SumBlissScanImages"

        filename = self.get_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")

        inputs = [
            {
                "task_identifier": task_identifier,
                "name": "filename",
                "value": filename,
            },
            {
                "task_identifier": task_identifier,
                "name": "output_filename",
                "value": self.master_output_filename(scan),
            },
            {
                "task_identifier": task_identifier,
                "name": "scan",
                "value": scan_nb,
            },
            {
                "task_identifier": task_identifier,
                "name": "detector_name",
                "value": lima_name,
            },
            {
                "task_identifier": task_identifier,
                "name": "monitor_name",
                "value": self.monitor_name,
            },
            {
                "task_identifier": task_identifier,
                "name": "flush_period",
                "value": self.flush_period,
            },
        ]
        tscan_info = scan.scan_info.get("tscan_info")
        if tscan_info:
            background_step = tscan_info.get("background_step")
            if background_step is not None:
                inputs.append(
                    {
                        "task_identifier": task_identifier,
                        "name": "background_step",
                        "value": background_step,
                    }
                )
        if self.data_from_memory:
            scan_memory_url = f"{scan.root_node.db_name}:{scan._node_name}"
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "scan_memory_url",
                    "value": scan_memory_url,
                }
            )
        inputs += self._get_data_access_inputs(task_identifier)
        return inputs

    def get_save_ascii_inputs(self, scan, lima_name):
        filename = self.get_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        root = self.scan_processed_directory(scan)
        stem = os.path.splitext(os.path.basename(filename))[0]
        basename = f"{stem}_{scan_nb}_{lima_name}_integrated.dat"
        return [
            {
                "task_identifier": "SaveAsciiPattern1D",
                "name": "filename",
                "value": os.path.join(root, basename),
            },
        ]

    def get_save_inputs(self, scan, lima_name, task_identifier):
        inputs = super().get_save_inputs(scan, lima_name, task_identifier)
        inputs += [
            {
                "task_identifier": task_identifier,
                "name": "nxprocess_name",
                "value": f"{lima_name}_integrate",
            }
        ]
        return inputs

    def get_multi_tasks_inputs(self, scan, lima_name):
        # Integration
        task_identifier = "MultiConfigIntegrate1D"
        inputs = self.get_integrate_inputs(scan, lima_name, task_identifier)
        multi_configs = self._get_multi_configs()
        if multi_configs:
            inputs.append(
                {
                    "task_identifier": task_identifier,
                    "name": "configs",
                    "value": multi_configs,
                }
            )

        # Saving
        task_identifier = "SaveNexusMultiPattern1D"
        inputs += super().get_save_inputs(scan, lima_name, task_identifier)
        inputs.append(
            {
                "task_identifier": task_identifier,
                "name": "nxprocess_name",
                "value": f"{lima_name}_multi_integrate",
            }
        )

        # ASCII Saving
        if multi_configs is not None:
            filename = self.get_filename(scan)
            scan_nb = scan.scan_info.get("scan_nb")
            root = self.scan_processed_directory(scan)
            stem = os.path.splitext(os.path.basename(filename))[0]
            filenames = []
            for config in multi_configs:
                basename = f"{stem}_{scan_nb}_{lima_name}"
                if "nbpt_rad" in config:
                    basename += f'_{config["nbpt_rad"]}rbins'
                if "azimuth_range_min" in config:
                    basename += f'_az{config["azimuth_range_min"]}-{config["azimuth_range_max"]}'
                basename += "_integrated.dat"
                filenames.append(os.path.join(root, basename))
            inputs.append(
                {
                    "task_identifier": "SaveAsciiMultiPattern1D",
                    "name": "filenames",
                    "value": filenames,
                }
            )
        return inputs

    def _get_multi_configs(self) -> Optional[List[dict]]:
        if self.multi_radial_bins and not self.azimuthal_ranges:
            return [{"nbpt_rad": npt} for npt in self.multi_radial_bins]

        if self.azimuthal_ranges and not self.multi_radial_bins:
            return [
                {"azimuth_range_min": az_min, "azimuth_range_max": az_max}
                for (az_min, az_max) in self.azimuthal_ranges
            ]

        if self.multi_radial_bins and self.azimuthal_ranges:
            configs = []
            for npt in self.multi_radial_bins:
                for az_min, az_max in self.azimuthal_ranges:
                    configs.append(
                        {
                            "nbpt_rad": npt,
                            "azimuth_range_min": az_min,
                            "azimuth_range_max": az_max,
                        }
                    )
            return configs

        return None

    @autocomplete_property
    def multi_radial_bins(self):
        return self._get_parameter(MULTI_RADIAL_BINS)

    @multi_radial_bins.setter
    def multi_radial_bins(self, bins_list: Optional[Sequence[int]]):
        if bins_list is not None and not isinstance(bins_list, Sequence):
            logging.warning(
                "multi_radial_bins must be a list of values. Ex: [100, 200, 400]"
            )
            return
        self._set_parameter(MULTI_RADIAL_BINS, bins_list)
        self._update_workflow()

    @autocomplete_property
    def azimuthal_ranges(self):
        return self._get_parameter(AZIMUTHAL_RANGES)

    @azimuthal_ranges.setter
    def azimuthal_ranges(self, ranges: Optional[Sequence[Tuple[float, float]]]):
        if ranges is not None and not isinstance(ranges, Sequence):
            logging.warning(
                "azimuthal_ranges must be a list of 2-size sequences. Ex: [(-100, 100), (45, 65), (135, 155)]"
            )
            return
        self._set_parameter(AZIMUTHAL_RANGES, ranges)
        self._update_workflow()

    def _update_workflow(self):
        if self.multi_radial_bins is None and self.azimuthal_ranges is None:
            self.workflow_with_saving = self.DEFAULT_WORKFLOW
        else:
            self.workflow_with_saving = resource_filename(
                "id22", "Sum_then_multiintegrate_with_saving.json"
            )

    def _data_to_plot_url(self, scan, lima_name):
        if not scan.scan_info.get("save"):
            return None

        output_url = self.online_output_url(scan, lima_name)
        if self.multi_radial_bins is None and self.azimuthal_ranges is None:
            return f"{output_url}/{lima_name}_integrate/integrated"
        else:
            return f"{output_url}/{lima_name}_multi_integrate_0/integrated"

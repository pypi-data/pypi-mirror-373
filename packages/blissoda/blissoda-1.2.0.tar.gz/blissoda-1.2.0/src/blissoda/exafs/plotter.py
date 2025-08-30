"""EXAFS plotting in Flint."""

import logging
import os
from collections import OrderedDict
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from ewoksjob.client import submit

from ..flint import FlintClient
from ..import_utils import unavailable_function
from ..utils.directories import get_dataset_processed_dir
from .plots import ExafsPlot
from .types import ExafsPlotWorkflowParameters
from .types import ExafsSplitWorkflowParameters
from .types import ScanInfo
from .types import SubScanInfo
from .types import XasPlotData
from .types import XasSubscanData

try:
    from bliss.common.plot import get_flint
except ImportError as ex:
    get_flint = unavailable_function(ex)


logger = logging.getLogger(__name__)


class ExafsPlotter:
    """Manage EXAFS plots in Flint based on Ewoks workflow results."""

    def __init__(self, number_of_scans: int = 0) -> None:
        self._number_of_scans = number_of_scans

        # Fixed parameters
        self._plot_id = "EXAFS"
        self._plot_names = {
            "flatten_mu": "mu",
            "chi_weighted_k": "chi",
            "ft_mag": "ft",
            "noise_savgol": "noise",
        }

        # Runtime data
        self._scan_infos: Dict[str, ScanInfo] = OrderedDict()
        self._plot: Optional[ExafsPlot] = None
        self._client = None
        self._color_index = 0

    @property
    def number_of_scans(self):
        """Maximum number of scans to be plotted"""
        return self._number_of_scans

    @number_of_scans.setter
    def number_of_scans(self, value):
        self._number_of_scans = max(value, 0)
        self.sync_plots()
        self.refresh()

    @property
    def scan_ids(self) -> List[str]:
        return list(self._scan_infos)

    def clear(self) -> None:
        """Remove all scan curves in all plots"""
        self._get_plot().clear()
        for scan_info in self._scan_infos.values():
            for subscan_info in scan_info.subscans:
                subscan_info.enabled = False

    def refresh(self) -> None:
        """Refresh all plots with the current processed data"""
        for scan_id, scan_info in self._scan_infos.items():
            for subscan_info in scan_info.subscans:
                subscan_info.updated = True
            self._update_scan_plot(scan_id)

    def create_scan_id(self, filename: str, scan_number: int) -> str:
        return f"{filename}|{scan_number}"

    def ensure_scan_infos(
        self, filename: str, scan_number: int
    ) -> Tuple[str, ScanInfo]:
        scan_id = self.create_scan_id(filename, scan_number)
        scan_info = self._scan_infos.get(scan_id)
        if scan_info:
            return scan_id, scan_info
        scan_info = ScanInfo(
            filename=filename, scan_number=scan_number, subscans=[], xas_results=[]
        )
        self._scan_infos[scan_id] = scan_info
        return scan_id, scan_info

    def _get_total_number_of_subscans(self) -> int:
        n_subscans = 0
        for scan_info in self._scan_infos.values():
            n_subscans += len(scan_info.subscans)

        return n_subscans

    def sync_plots(self):
        """Synchronize workflow results in cache with plots in Flint."""
        n_subscans = self._get_total_number_of_subscans()

        max_subscans = self.number_of_scans
        min_enabled_subscan_idx = max(n_subscans - max_subscans, 0)
        subscan_index = 0
        for scan_info in self._scan_infos.values():
            for subscan_info, xasplotdata in zip(
                scan_info.subscans, scan_info.xas_results
            ):
                enabled = subscan_index >= min_enabled_subscan_idx
                needs_refresh = subscan_info.updated or subscan_info.enabled != enabled
                if needs_refresh:
                    if enabled:
                        self._get_plot().update_scan(
                            subscan_info.legend, xasplotdata, subscan_info.color
                        )
                    else:
                        self._get_plot().remove_scan(subscan_info.legend)
                subscan_info.enabled = enabled
                subscan_info.updated = False
                subscan_index += 1

    def remove_scan(self, legend: str) -> None:
        """Disable subscan and remove from Flint."""
        removed = False
        for scan_info in self._scan_infos.values():
            for subscan_info in scan_info.subscans:
                if subscan_info.legend == legend:
                    if subscan_info.enabled:
                        subscan_info.enabled = False
                        self._get_plot().remove_scan(subscan_info.legend)
                        removed = True
                    break
        if removed:
            self.purge_scan_infos()

    def purge_scan_infos(self, keep_scan_ids: Sequence[str] = tuple()) -> None:
        """Remove cache from scans that have no enabled sub-scans or not processing results."""
        for scan_id, scan_info in list(self._scan_infos.items()):
            if scan_id in keep_scan_ids:
                continue

            # Disable all subscans when the scan has no data
            if not scan_info.xas_results:
                for subscan_info in scan_info.subscans:
                    if subscan_info.enabled:
                        subscan_info.enabled = False
                        self._get_plot().remove_scan(subscan_info.legend)

            # Delete the scan when it has no enabled subscans
            has_enabled_subscan = any(
                subscan_info.enabled for subscan_info in scan_info.subscans
            )
            if not has_enabled_subscan:
                del self._scan_infos[scan_id]

    def _update_scan_plot(self, scan_id: str) -> None:
        """Update all scan curves in all plots"""
        if self._plot_exists():
            # Update the existing plot for the requested scan
            scan_info = self._scan_infos.get(scan_id)
            if scan_info is not None:
                self.sync_results(scan_info)
                self.sync_plots()
        else:
            # Create a fresh plot with all scan curves
            for scan_info in self._scan_infos.values():
                self.sync_results(scan_info)
            self.sync_plots()

    def sync_results(self, scan_info: ScanInfo) -> None:
        """Update workflow results in cache with processing results.
        Blocks when the scan has a pending future.
        """
        if scan_info.plot_future is None:
            return

        try:
            workflow_results = scan_info.plot_future.result()
        except Exception:
            # Workflow failed
            return
        finally:
            scan_info.plot_future = None

        xas_results = [
            XasSubscanData(
                **{
                    self._plot_names[plot_name]: XasPlotData(**plot_data)
                    for plot_name, plot_data in data.items()
                }
            )
            for data in workflow_results["plot_data"]
        ]

        if not xas_results:
            # Workflow succeeded but did not return any results
            return

        for idx, xasplotdata in enumerate(
            xas_results, scan_info.min_subscan_index_to_process
        ):
            if idx < len(scan_info.xas_results):
                scan_info.xas_results[idx] = xasplotdata
                scan_info.subscans[idx].updated = True
            else:
                basename = os.path.basename(os.path.dirname(scan_info.filename))
                legend = f"{basename}: {scan_info.scan_number}.{idx + 1}"
                color = self._new_color()
                subscan_info = SubScanInfo(legend=legend, color=color, enabled=False)
                scan_info.subscans.append(subscan_info)
                scan_info.xas_results.append(xasplotdata)

    def _submit_plot_workflow(
        self,
        scan_id: str,
        parameters: ExafsPlotWorkflowParameters,
        reprocess: bool = False,
    ) -> None:
        """Submit the data processing for a scan"""
        scan_info = self._scan_infos.get(scan_id, None)
        if scan_info is None:
            return

        scan_info.reprocess_all = reprocess
        input_information = {
            "channel_url": f"{scan_info.scan_url}/measurement/{parameters.energy_name}",
            "spectra_url": f"{scan_info.scan_url}/measurement/{parameters.mu_name}",
            "energy_unit": parameters.energy_unit,
        }

        if scan_info.multi_xas_scan:
            input_information["is_concatenated"] = True
            input_information["trim_concatenated_n_points"] = parameters.trim_n_points
            input_information["skip_concatenated_n_spectra"] = (
                scan_info.min_subscan_index_to_process
            )
            input_information["concatenated_spectra_section_size"] = (
                scan_info.multi_xas_subscan_size
            )

        plot_inputs = [
            {
                "task_type": "ReadXasObject",
                "name": "input_information",
                "value": input_information,
            },
            {
                "task_type": "PlotSpectrumData",
                "name": "plot_names",
                "value": list(self._plot_names),
            },
        ]
        scan_info.plot_future = submit(
            args=(parameters.workflow,), kwargs={"inputs": plot_inputs}
        )

    def _submit_split_workflow(
        self,
        scan_id: str,
        parameters: ExafsSplitWorkflowParameters,
        reprocess: bool = False,
    ) -> None:
        """Submit the data processing for a scan"""
        scan_info = self._scan_infos.get(scan_id, None)
        if scan_info is None or not scan_info.multi_xas_scan:
            return

        out_dirname = get_dataset_processed_dir(scan_info.filename)
        h5_basename = os.path.basename(scan_info.filename)
        h5_stem, _ = os.path.splitext(h5_basename)
        out_filename = os.path.join(out_dirname, h5_basename)
        convert_destination = os.path.join(
            out_dirname, "workflows", f"{h5_stem}_scan{scan_info.scan_number:04d}.json"
        )

        if out_filename.startswith("/data/scisoft/ewoks"):
            out_filename = out_filename.replace("/data/scisoft/ewoks", "/tmp_14_days")

        split_inputs = [
            {
                "task_type": "SplitBlissScan",
                "name": "filename",
                "value": scan_info.filename,
            },
            {
                "task_type": "SplitBlissScan",
                "name": "scan_number",
                "value": scan_info.scan_number,
            },
            {
                "task_type": "SplitBlissScan",
                "name": "monotonic_channel",
                "value": parameters.monotonic_channel,
            },
            {
                "task_type": "SplitBlissScan",
                "name": "subscan_size",
                "value": scan_info.multi_xas_subscan_size,
            },
            {
                "task_type": "SplitBlissScan",
                "name": "trim_n_points",
                "value": parameters.trim_n_points,
            },
            {
                "task_type": "SplitBlissScan",
                "name": "wait_finished",
                "value": parameters.scan_complete,
            },
            {
                "task_type": "SplitBlissScan",
                "name": "out_filename",
                "value": out_filename,
            },
            {
                "task_type": "SplitBlissScan",
                "name": "counter_group",
                "value": "measurement",
            },
        ]

        scan_info.split_future = submit(
            args=(parameters.workflow,),
            kwargs={"inputs": split_inputs, "convert_destination": convert_destination},
        )

    def execute_and_plot(
        self,
        scan_id: str,
        plot_parameters: ExafsPlotWorkflowParameters,
        split_parameters: ExafsSplitWorkflowParameters,
        reprocess: bool = False,
    ) -> None:
        self._submit_plot_workflow(scan_id, plot_parameters, reprocess=reprocess)
        self._submit_split_workflow(scan_id, split_parameters, reprocess=reprocess)
        self._update_scan_plot(scan_id)

    def _get_plot(self) -> ExafsPlot:
        """Launches Flint and creates the plot when either is missing"""
        if not self._plot_exists():
            self._plot = self._get_flint().get_plot(
                ExafsPlot, unique_name=self._plot_id
            )
        return self._plot

    def _plot_exists(self) -> bool:
        if self._plot is None:
            return False
        return self._get_flint().is_plot_exists(self._plot_id)

    def _get_flint(self) -> FlintClient:
        """Get the Flint and create it when missing."""
        if not self._flint_exists():
            self._client = get_flint()
        return self._client

    def _flint_exists(self) -> bool:
        """Return True when we have an available Flint client."""
        if self._client is None:
            return False
        try:
            if self._client.is_available():
                return True
        except FileNotFoundError:
            pass
        return False

    @property
    def _n_colors(self) -> int:
        return min(len(self._COLOR_PALETTE), self.number_of_scans + 1)

    def _new_color(self) -> Tuple[int, int, int]:
        scan_color = self._COLOR_PALETTE[min(self._color_index, self._n_colors - 1)]
        self._color_index = (self._color_index + 1) % self._n_colors
        return scan_color

    _COLOR_PALETTE = [
        (87, 81, 212),
        (235, 171, 33),
        (176, 69, 0),
        (0, 197, 248),
        (207, 97, 230),
        (0, 166, 107),
        (184, 0, 87),
        (0, 138, 248),
        (0, 110, 0),
        (0, 186, 171),
        (255, 145, 133),
        (133, 133, 0),
    ]

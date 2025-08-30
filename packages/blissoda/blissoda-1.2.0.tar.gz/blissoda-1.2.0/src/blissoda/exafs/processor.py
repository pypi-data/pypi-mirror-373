"""Workflow execution and Flint EXAFS plotting during a scan"""

import logging
import os
import time
from typing import Any
from typing import Dict
from typing import Optional

from silx.io.h5py_utils import top_level_names

from ..automation import BlissAutomationObject
from ..bliss_globals import current_session
from ..bliss_globals import setup_globals
from ..exafs import scan_utils
from ..import_utils import unavailable_module
from ..persistent.parameters import ParameterInfo
from .plotter import ExafsPlotter
from .types import ExafsPlotWorkflowParameters
from .types import ExafsSplitWorkflowParameters

try:
    import gevent
except ImportError as ex:
    gevent = unavailable_module(ex)


logger = logging.getLogger(__name__)


class ExafsProcessor(
    BlissAutomationObject,
    parameters=[
        ParameterInfo("_counters"),
        ParameterInfo("_scan_type"),
        ParameterInfo("refresh_period", category="plotting"),
        ParameterInfo("max_scans", category="plotting"),
        ParameterInfo("workflow", category="workflow"),
        ParameterInfo("trim_n_points", category="Multi-XAS scans"),
        ParameterInfo("enabled", category="status"),
    ],
):
    """Run a scan, execute a workflow every x seconds during the scan
    and plot the results in Flint. A fixed number of n scans stay plotted.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("refresh_period", 2)  # seconds
        defaults.setdefault("max_scans", 3)
        defaults.setdefault("enabled", True)
        defaults.setdefault("_counters", dict())
        defaults.setdefault("trim_n_points", 0)
        defaults.setdefault("split_scans", False)

        super().__init__(config=config, defaults=defaults)

        self._plotter = ExafsPlotter(number_of_scans=self.max_scans)

    @property
    def counters(self) -> dict:
        return self._counters.get(self.scan_type, dict())

    @property
    def scan_type(self) -> Optional[str]:
        return self._scan_type

    @scan_type.setter
    def scan_type(self, value: str) -> None:
        if value not in self._counters:
            raise ValueError(f"Valid scan types are: {list(self._counters)}")
        self._scan_type = value

    @property
    def mu_name(self) -> Optional[str]:
        return self.counters.get("mu_name")

    @mu_name.setter
    def mu_name(self, value: str) -> None:
        self.counters["mu_name"] = value

    @property
    def energy_name(self) -> Optional[str]:
        return self.counters.get("energy_name")

    @energy_name.setter
    def energy_name(self, value: str) -> None:
        self.counters["energy_name"] = value

    @property
    def energy_unit(self) -> Optional[str]:
        return self.counters.get("energy_unit")

    @energy_unit.setter
    def energy_unit(self, value: str) -> None:
        self.counters["energy_unit"] = value

    @property
    def max_scans(self) -> int:
        return self._get_parameter("max_scans")

    @max_scans.setter
    def max_scans(self, value: int):
        self._set_parameter("max_scans", value)
        self._plotter.number_of_scans = value
        self._plotter.sync_plots()
        self._plotter.refresh()

    def _scan_type_from_scan(self, scan: scan_utils.ScanType) -> Optional[str]:
        raise NotImplementedError

    def _multi_xas_scan(self, scan: scan_utils.ScanType) -> bool:
        return NotImplementedError

    def _multi_xas_subscan_size(self, scan: scan_utils.ScanType) -> int:
        return NotImplementedError

    def _filename_from_scan(self, scan: scan_utils.ScanType) -> str:
        try:
            # bliss 2
            return scan.writer.get_filename()
        except AttributeError:
            pass
        try:
            # bliss 1
            return scan.writer.filename
        except AttributeError:
            pass
        # Activate filename in the Bliss session
        return setup_globals.SCAN_SAVING.filename

    def run(
        self, scan: scan_utils.ScanType, filename: Optional[str] = None, **kw
    ) -> None:
        if not self.enabled:
            scan.run()
            return

        self.scan_type = self._scan_type_from_scan(scan)

        if not self.scan_type:
            scan.run()
            return

        # Scan filename
        if filename is None:
            filename = self._filename_from_scan(scan)

        # Scan number
        if os.path.exists(filename):
            scans = top_level_names(filename, include_only=None)
            scan_number = max(int(float(s)) for s in scans) + 1
        else:
            scan_number = 1

        scan_id, scan_info = self._plotter.ensure_scan_infos(filename, scan_number)

        if self._multi_xas_scan(scan):
            scan_info.multi_xas_scan = True
            scan_info.multi_xas_subscan_size = self._multi_xas_subscan_size(scan)

        # Background process: trigger workflow and plot indefinitely
        update_loop = gevent.spawn(self._plotting_loop, scan_id)

        try:
            scan.run(**kw)
        finally:
            try:
                try:
                    # Raise error when the background process failed
                    if not update_loop:
                        update_loop.get()

                    # Kill the background process
                    update_loop.kill()

                    # Background process: trigger workflow and plot once
                    gevent.spawn(self._finish_plotting_loop, scan_id)
                finally:
                    self._plotter.purge_scan_infos(keep_scan_ids={scan_id})
            except Exception:
                logger.warning("Post-scan update failed", exc_info=True)

    def test(self, scan_number: int, auto_detect_monotonic: bool = False) -> None:
        filename = "/data/scisoft/ewoks/ch7280/id24-dcm/20250131/RAW_DATA/Ru_WVC1/Ru_WVC1_1_RT_air/Ru_WVC1_1_RT_air.h5"
        if auto_detect_monotonic:
            multi_xas_subscan_size = None
        else:
            multi_xas_subscan_size = 3001
        self.reprocess(
            filename=filename,
            scan_number=scan_number,
            multi_xas_scan=True,
            multi_xas_subscan_size=multi_xas_subscan_size,
            energy_name="energy_enc",
            energy_units="keV",
            mu_name="mu_trans",
        )

    def reprocess(
        self,
        filename: Optional[str] = None,
        scan_number: Optional[int] = None,
        multi_xas_scan: Optional[bool] = None,
        multi_xas_subscan_size: Optional[int] = None,
        energy_name: Optional[str] = None,
        energy_units: Optional[str] = None,
        mu_name: Optional[str] = None,
    ) -> None:
        """Reprocess and re-plot."""
        if scan_number:
            if not filename:
                filename = current_session.scan_saving.filename
            scan_id, scan_info = self._plotter.ensure_scan_infos(filename, scan_number)
            if multi_xas_scan is not None:
                scan_info.multi_xas_scan = multi_xas_scan
                scan_info.multi_xas_subscan_size = multi_xas_subscan_size
            self._execute_and_plot(
                scan_id,
                energy_name=energy_name,
                energy_units=energy_units,
                mu_name=mu_name,
                reprocess=True,
            )
        else:
            for scan_id in self._plotter.scan_ids:
                self._execute_and_plot(
                    scan_id,
                    energy_name=energy_name,
                    energy_units=energy_units,
                    mu_name=mu_name,
                    reprocess=True,
                )
        self._plotter.purge_scan_infos()

    def _plotting_loop(self, scan_id: str) -> None:
        t0 = time.time()
        while True:
            t1 = time.time()
            sleep_time = max(t0 + self.refresh_period - t1, 0)
            gevent.sleep(sleep_time)
            t0 = t1
            try:
                self._execute_and_plot(scan_id)
            except Exception as e:
                logger.error(f"EXAFS workflow or plot failed ({e})", exc_info=True)

    def _finish_plotting_loop(self, scan_id: str) -> None:
        gevent.sleep(1)
        self._execute_and_plot(scan_id, scan_finished=True)

    def _execute_and_plot(
        self,
        scan_id: str,
        energy_name: Optional[str] = None,
        energy_units: Optional[str] = None,
        mu_name: Optional[str] = None,
        reprocess: bool = False,
        scan_finished: bool = False,
    ) -> None:
        plot_parameters = ExafsPlotWorkflowParameters(
            workflow=self.workflow,
            energy_name=energy_name or self.energy_name,
            energy_unit=energy_units or self.energy_unit,
            mu_name=mu_name or self.mu_name,
            trim_n_points=self.trim_n_points,
        )

        split_workflow = {
            "graph": {"graph_version": "1.1", "id": "split"},
            "nodes": [
                {
                    "task_type": "class",
                    "task_identifier": "est.core.process.split.SplitBlissScan",
                }
            ],
        }
        split_parameters = ExafsSplitWorkflowParameters(
            workflow=split_workflow,
            monotonic_channel=f"measurement/{plot_parameters.energy_name}",
            scan_complete=scan_finished or reprocess,
            trim_n_points=self.trim_n_points,
        )

        self._plotter.execute_and_plot(
            scan_id,
            plot_parameters,
            split_parameters,
            reprocess=reprocess,
        )

    def remove_scan(self, legend: str) -> None:
        """Disable subscan and remove from Flint."""
        self._plotter.remove_scan(legend)

    def clear(self) -> None:
        """Remove all scan curves in all plots"""
        self._plotter.clear()

    def refresh(self) -> None:
        """Refresh all plots with the current processed data."""
        self._plotter.refresh()

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()

        categories["scan"] = {
            "scan_type": self.scan_type,
            "mu": self.mu_name,
            "energy": self.energy_name,
            "energy_unit": self.energy_unit,
        }

        categories["status"] = categories.pop("status")
        return categories

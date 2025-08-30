from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Optional

from .automation import BlissAutomationObject
from .flint.plotter import BasePlotter
from .import_utils import unavailable_type
from .persistent.parameters import ParameterInfo
from .persistent.parameters import autocomplete_property
from .utils import trigger

try:
    from bliss.scanning.scan import Scan as BlissScanType
except ImportError as ex:
    BlissScanType = unavailable_type(ex)

logger = logging.getLogger(__name__)


class BaseProcessor(
    BlissAutomationObject,
    parameters=[
        ParameterInfo("_enabled"),
        ParameterInfo("trigger_at", category="workflows"),
    ],
):
    """Enable and disable workflow triggering on new scans."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("_enabled", False)
        defaults.setdefault("trigger_at", "PREPARED")  # START, PREPARED, END

        super().__init__(config=config, defaults=defaults)

        if self._HAS_BLISS:
            if self._enabled:
                self._register_workflow_trigger()
            else:
                self._unregister_workflow_trigger()

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()
        status = categories.setdefault("status", {})
        status["Enabled"] = self._enabled
        return categories

    @autocomplete_property
    def trigger_at(self) -> Optional[str]:
        return self._get_parameter("trigger_at")

    @trigger_at.setter
    def trigger_at(self, value: str):
        self._set_parameter("trigger_at", value)
        if self._enabled:
            self.disable()
            self.enable()

    def enable(self):
        if self._enabled:
            return
        self._register_workflow_trigger()
        self._enabled = True

    def disable(self):
        if not self._enabled:
            return
        self._unregister_workflow_trigger()
        self._enabled = False

    def _register_workflow_trigger(self):
        trigger.enable_processing_trigger(
            self._processing_id(),
            self._trigger_workflow_on_new_scan,
            self.trigger_at,
        )

    def _unregister_workflow_trigger(self):
        trigger.disable_processing_trigger(
            self._processing_id(),
        )

    @classmethod
    def _processing_id(cls):
        return cls.__name__

    @abstractmethod
    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> Optional[dict]:
        pass


class BaseProcessorWithPlotting(
    BaseProcessor,
    parameters=[
        ParameterInfo("_plotting_enabled"),
        ParameterInfo("number_of_scans", category="plotting"),
    ],
):
    """Enable and disable workflow triggering and Flint plotting on new scans."""

    plotter_class = BasePlotter

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("_plotting_enabled", True)
        defaults.setdefault("number_of_scans", 4)

        super().__init__(config=config, defaults=defaults)

        if self._plotting_enabled:
            self._plotter = self.plotter_class(self.number_of_scans)
            if self._HAS_BLISS:
                self._plotter.replot()
        else:
            self._plotter = None

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()
        status = categories.setdefault("status", {})
        status["Plots in Flint"] = self._plotter is not None
        if self._plotter:
            categories["status"]["Plotting tasks"] = self._plotter.purge_tasks()
        return categories

    @property
    def plotter(self) -> Optional[plotter_class]:
        return self._plotter

    def enable_plotting(self):
        if self._plotter is not None:
            return
        self._plotter = self.plotter_class(self.number_of_scans)
        self._plotter.replot()
        self._plotting_enabled = True

    def disable_plotting(self):
        if self._plotter is None:
            return
        self.stop_plotting_tasks()
        self._plotter = None
        self._plotting_enabled = False

    def clear_plots(self) -> None:
        if self._plotter:
            return self._plotter.clear()
        else:
            print("Plotting is disabled")

    def replot(self) -> None:
        if self._plotter:
            return self._plotter.replot()
        else:
            print("Plotting is disabled")

    def purge_plotting_tasks(self) -> int:
        if self._plotter:
            return self._plotter.purge_tasks()
        else:
            print("Plotting is disabled")
            return 0

    def stop_plotting_tasks(self) -> int:
        if self._plotter:
            return self._plotter.kill_tasks()
        else:
            print("Plotting is disabled")
            return 0

    @autocomplete_property
    def number_of_scans(self) -> int:
        return self._get_parameter("number_of_scans")

    @number_of_scans.setter
    def number_of_scans(self, value: int):
        self._plotter.number_of_scans = value
        self._set_parameter("number_of_scans", self._plotter.number_of_scans)

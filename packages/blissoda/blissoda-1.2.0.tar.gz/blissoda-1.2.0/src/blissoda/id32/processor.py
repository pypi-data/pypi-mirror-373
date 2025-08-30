import json
import logging
import os
import pathlib
import time
from typing import Any
from typing import Dict
from typing import Optional

from ewoksjob.client import submit

from ..bliss_globals import current_session
from ..flint import WithFlintAccess
from ..import_utils import unavailable_function
from ..import_utils import unavailable_module
from ..persistent.parameters import ParameterInfo
from ..persistent.parameters import autocomplete_property
from ..processor import BaseProcessor
from ..processor import BlissScanType
from ..resources import resource_filename
from ..utils.directories import get_dataset_processed_dir
from .plots import SpecGenPlot

try:
    import gevent
except ImportError as ex:
    gevent = unavailable_module(ex)

try:
    from bliss.shell.getval import getval_float
except ImportError as ex:
    getval_float = unavailable_function(ex)


try:
    from bliss.shell.getval import getval_int
except ImportError as ex:
    getval_int = unavailable_function(ex)


try:
    from bliss.shell.getval import getval_yes_no
except ImportError as ex:
    getval_yes_no = unavailable_function(ex)

logger = logging.getLogger(__name__)


class Id32SpecGenProcessor(
    BaseProcessor,
    parameters=[
        ParameterInfo("parameters", category="workflows"),
        ParameterInfo("max_scans_flint", category="plotting"),
        ParameterInfo("update_period", category="workflows"),
        ParameterInfo("update_period_flint", category="plotting"),
    ],
    deprecated_class_attributes={"WORKER": "QUEUE"},
):
    QUEUE = "lid32xmcd2"
    WORKFLOW_FILENAME = "convert_image_to_spectrum.json"

    def __init__(
        self,
        detectors=[],
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault(
            "parameters",
            {
                detector: {
                    "slope": -0.0688,
                    "smile": float(0),
                    "energy calibration (meV/px)": 21.5,
                    "points per pixel": 2.7,
                    "low threshold": 0.12,
                    "high threshold": 1,
                    "mask size": 5,
                    "SPC": True,
                    "SPC grid size": 3,
                    "SPC low threshold": 0.2,
                    "SPC high threshold": 1.0,
                    "SPC single event threshold": 0.4,
                    "SPC double event threshold": 1.5,
                }
                for detector in detectors
            },
        )
        defaults.setdefault("max_scans_flint", 5)
        defaults.setdefault("update_period_flint", 1)
        defaults.setdefault("update_period", 60)

        self.detectors = detectors

        super().__init__(config=config, defaults=defaults)

        self._plotters = {
            detector: Plotter(
                max_scans=self.max_scans_flint,
                update_period=self.update_period_flint,
                detector=detector,
            )
            for detector in self.detectors
        }

    @autocomplete_property
    def max_scans_flint(self) -> Optional[int]:
        return self._get_parameter("max_scans_flint")

    @max_scans_flint.setter
    def max_scans_flint(self, value: int):
        for plotter in self._plotters:
            self._plotters[plotter].max_scans = value
            self._set_parameter("max_scans_flint", self._plotters[plotter].max_scans)

    @autocomplete_property
    def update_period_flint(self) -> Optional[float]:
        return self._get_parameter("update_period_flint")

    @update_period_flint.setter
    def update_period_flint(self, value: float):
        for plotter in self._plotters:
            self._plotters[plotter].update_period = value
            self._set_parameter(
                "update_period_flint", self._plotters[plotter].update_period
            )

    def setup(self):
        req = "  ".join(
            ["(%d) %s" % (i + 1, det) for i, det in enumerate(self.detectors)]
        )
        if not req:
            print("No detector defined")
            return

        ret = getval_int(
            "Detector?  " + req, minimum=1, maximum=len(self.detectors), default=1
        )
        det = self.detectors[ret - 1]
        for par in self.parameters[det].keys():
            old_par = self.parameters[det][par]
            if isinstance(old_par, bool):
                new_par = getval_yes_no(par, default=old_par)
            elif isinstance(old_par, int):
                new_par = getval_int(par, default=old_par)
            else:
                new_par = getval_float(par, default=old_par)
            self.parameters[det][par] = new_par

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()
        ntasks = sum([plotter.purge_tasks() for _, plotter in self._plotters.items()])
        status = categories.setdefault("status", {})
        status["Plotting tasks"] = ntasks
        return categories

    def _get_workflow(self) -> dict:
        with open(resource_filename("id32", self.WORKFLOW_FILENAME), "r") as wf:
            return json.load(wf)

    def _get_workflow_inputs(self, scan: BlissScanType, detector) -> list:
        return [
            {
                "name": "scan_number",
                "value": scan.scan_number,
            },
            {
                "name": "input_path",
                "value": scan.scan_saving.filename,
            },
            {
                "name": "output_path",
                "value": self._get_scan_processed_directory(scan),
            },
            {"name": "detector", "value": detector},
            {"name": "specgen_parameters", "value": dict(self.parameters[detector])},
            {"name": "update_period", "value": self.update_period},
            {
                "name": "scan_info",
                "value": scan.scan_info["acquisition_chain"]["timer"],
            },
        ]

    def _get_scan_filename(self, scan: BlissScanType) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def _get_scan_processed_directory(self, scan: BlissScanType) -> str:
        return get_dataset_processed_dir(self._get_scan_filename(scan))

    def _get_workflow_destination(self, scan: BlissScanType) -> str:
        """Builds the path where the workflow JSON will be saved."""
        filename = self._get_scan_filename(scan)
        scan_nb = scan.scan_info.get("scan_nb")
        root = self._get_scan_processed_directory(scan)
        stem = os.path.splitext(os.path.basename(filename))[0]
        wf_path = os.path.join(root, "workflows")
        pathlib.Path(wf_path).mkdir(parents=True, exist_ok=True)
        basename = f"{stem}_{scan_nb:04d}.json"
        return os.path.join(wf_path, basename)

    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> None:
        if not scan.scan_info["save"]:
            return

        if "timer" not in scan.scan_info["acquisition_chain"].keys():
            logger.warning(
                "Not a timescan or loopscan. Ignoring specgen workflow trigger. "
                f"Disabling {str(self.detectors)} in measurement group will speed up acquisition."
            )
            return

        for detector in self.detectors:
            if "%s:image" % detector in scan.scan_info["channels"].keys():
                workflow = self._get_workflow()
                inputs = self._get_workflow_inputs(scan, detector)
                kwargs = {"inputs": inputs, "outputs": [{"all": False}]}
                kwargs["convert_destination"] = self._get_workflow_destination(scan)

                future = submit(args=(workflow,), kwargs=kwargs, queue=self.QUEUE)

                # data = future.result()
                datasetname = "_".join(
                    [
                        scan.scan_saving.collection_name,
                        scan.scan_saving.dataset_name,
                    ]
                )

                scan_number = scan.scan_number
                output_path = self._get_scan_processed_directory(scan)
                outputfile_sum = os.path.join(
                    output_path,
                    # ~ detector,
                    f"Online_analysis_{datasetname}_{detector}.spec",
                )
                self._plotters[detector].handle_workflow_result(
                    future, outputfile_sum, scan_number
                )


class Plotter(WithFlintAccess):
    def __init__(self, max_scans: int, update_period: float, detector: str) -> None:
        super().__init__()
        self._tasks = list()
        self.max_scans = max_scans
        self.update_period = max(0.5, update_period)
        self.detector = detector

    def purge_tasks(self) -> int:
        """Remove references to tasks that have finished."""
        self._tasks = [t for t in self._tasks if t]
        return len(self._tasks)

    def kill_tasks(self) -> int:
        """Kill all tasks."""
        gevent.killall(self._tasks)
        return self.purge_tasks()

    def handle_workflow_result(self, *args, **kwargs) -> None:
        """Handle workflow results in a background task"""
        self._spawn(self._handle_workflow_result, *args, **kwargs)

    def _handle_workflow_result(self, future, outputfile_sum: str, scan_number: int):
        try:
            while not future.done():
                self._update_plot(outputfile_sum, scan_number)
                time.sleep(self.update_period)
            self._update_plot(outputfile_sum, scan_number)
        except Exception as e:
            logger.exception(e)

    def _spawn(self, *args, **kw):
        task = gevent.spawn(*args, **kw)
        self._tasks.append(task)
        self.purge_tasks()

    def _get_plot(self) -> SpecGenPlot:
        return super()._get_plot("SpecGen (%s)" % (self.detector), SpecGenPlot)

    def _update_plot(self, outputfile_sum, scan_number):
        plot = self._get_plot()
        plot.update_plot(outputfile_sum, scan_number, self.max_scans)

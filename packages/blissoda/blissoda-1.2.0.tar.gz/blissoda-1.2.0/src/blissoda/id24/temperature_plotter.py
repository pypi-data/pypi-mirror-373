import logging
import os
import shutil
from glob import glob
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

from ewoksjob.client import submit

from ..bliss_globals import current_session
from ..flint import WithFlintAccess
from ..import_utils import unavailable_module
from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessor
from ..processor import BlissScanType
from ..resources import resource_filename
from ..utils import directories
from .plots import TemperaturePlot

try:
    import gevent
except ImportError as ex:
    gevent = unavailable_module(ex)


logger = logging.getLogger(__name__)


class WorkflowType(NamedTuple):
    xas: bool
    fit: bool

    def parameter_name(self) -> str:
        name = "workflow"
        if self.fit:
            name += "_with_fit"
        if self.xas:
            name = "xas_" + name
        return name


class Id24TemperaturePlotter(
    BaseProcessor,
    parameters=[
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo("workflow_with_fit", category="workflows"),
        ParameterInfo("xas_workflow", category="workflows"),
        ParameterInfo("xas_workflow_with_fit", category="workflows"),
        ParameterInfo("energy_name", category="XAS"),
        ParameterInfo("mu_name", category="XAS"),
        ParameterInfo("extend_plotrange_left", category="plot", doc="(nm)"),
        ParameterInfo("extend_plotrange_right", category="plot", doc="(nm)"),
        ParameterInfo("two_color_difference", category="plot", doc="(nm)"),
        ParameterInfo("dpi", category="plot"),
        ParameterInfo("refit", category="fit"),
        ParameterInfo("wavelength_min", category="fit", doc="(nm)"),
        ParameterInfo("wavelength_max", category="fit", doc="(nm)"),
    ],
):
    DEFAULT_WORKFLOWS = {
        WorkflowType(xas=True, fit=True): resource_filename(
            "id24", "id24_xas_planck_fitplot.json"
        ),
        WorkflowType(xas=True, fit=False): resource_filename(
            "id24", "id24_xas_planck_plot.json"
        ),
        WorkflowType(xas=False, fit=True): resource_filename(
            "id24", "id24_planck_fitplot.json"
        ),
        WorkflowType(xas=False, fit=False): resource_filename(
            "id24", "id24_planck_plot.json"
        ),
    }

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("trigger_at", "END")

        for workflow_type, workflow_filename in self.DEFAULT_WORKFLOWS.items():
            defaults.setdefault(workflow_type.parameter_name(), workflow_filename)

        defaults.setdefault("energy_name", "energy_enc")
        defaults.setdefault("mu_name", "mu_trans")

        defaults.setdefault("extend_plotrange_left", -15)
        defaults.setdefault("extend_plotrange_right", 50)
        defaults.setdefault("two_color_difference", 42)
        defaults.setdefault("dpi", 150)

        defaults.setdefault("refit", False)
        defaults.setdefault("wavelength_min", None)
        defaults.setdefault("wavelength_max", None)

        super().__init__(config=config, defaults=defaults)

        self.plotter = Plotter()

    def _info_categories(self) -> Dict[str, dict]:
        categories = super()._info_categories()
        ntasks = self.plotter.purge_tasks()
        status = categories.setdefault("status", {})
        status["Fitting"] = self.refit
        status["Plotting tasks"] = ntasks
        return categories

    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> Optional[dict]:
        if not self._scan_requires_workflow(scan):
            return
        filename = scan.scan_info["filename"]
        scan_number = scan.scan_info["scan_nb"]
        workflow_type = self.get_workflow_type(scan)
        self._trigger_workflow(workflow_type, scan_number, filename=filename)

    def get_workflow_type(self, scan: BlissScanType) -> WorkflowType:
        return WorkflowType(xas=self._is_xas_scan(scan), fit=self.refit)

    def trigger_workflow(
        self,
        scan_number: int,
        filename: Optional[str] = None,
        xas: bool = True,
    ) -> None:
        self._trigger_workflow(
            WorkflowType(xas=xas, fit=self.refit), scan_number, filename=filename
        )

    def _trigger_workflow(
        self,
        workflow_type: WorkflowType,
        scan_number: int,
        filename: Optional[str] = None,
    ) -> None:
        if filename:
            if not os.path.isabs(filename):
                basename = os.path.basename(filename)
                raw_data = directories.get_raw_dir(current_session.scan_saving.filename)
                filenames = glob(os.path.join(raw_data, "*", "*", basename))
                if not filenames:
                    raise FileNotFoundError(filename)
                filename = filenames[0]
        else:
            filename = current_session.scan_saving.filename
        workflow = self._get_workflow(workflow_type, filename)

        future = submit(
            args=(workflow,),
            kwargs={
                "inputs": self._get_workflow_inputs(
                    workflow_type, filename, scan_number
                ),
                "outputs": [{"all": False}],
            },
        )
        self.plotter.handle_workflow_result(future)

    def _scan_requires_workflow(self, scan: BlissScanType) -> bool:
        if not self._has_temperature(scan):
            return False
        if not scan.scan_info.get("save"):
            return False
        if not scan.scan_info.get("filename"):
            return False
        if not scan.scan_info.get("scan_nb"):
            return False
        return True

    def _has_temperature(self, scan: BlissScanType) -> bool:
        channels = scan.scan_info.get("channels", dict())
        return "laser_heating_down:T_planck" in channels

    def _is_xas_scan(self, scan: BlissScanType) -> bool:
        channels = scan.scan_info.get("channels", dict())
        energy_suffix = f":{self.energy_name}"
        return any(name.endswith(energy_suffix) for name in channels)

    def _get_workflow(
        self, workflow_type: WorkflowType, filename: str
    ) -> Optional[str]:
        """Get the workflow to execute for the scan and ensure it is located
        in the proposal directory for user reference and worker accessibility.
        """
        parameter_name = workflow_type.parameter_name()
        src_file = self._get_parameter(parameter_name)
        if src_file is None:
            return
        if not os.path.isfile(src_file):
            src_file = self.DEFAULT_WORKFLOWS[workflow_type]

        workflow_directory = directories.get_workflows_dir(filename)
        dst_file = os.path.join(workflow_directory, os.path.basename(src_file))
        if src_file != dst_file:
            self._set_parameter(parameter_name, dst_file)

        if not os.path.exists(dst_file):
            os.makedirs(workflow_directory, exist_ok=True)
            shutil.copyfile(src_file, dst_file)

        return dst_file

    def _get_workflow_inputs(
        self, workflow_type: WorkflowType, filename: str, scan_number: int
    ) -> List[dict]:
        inputs = self._get_read_inputs(workflow_type, filename, scan_number)
        inputs += self._get_plot_inputs(workflow_type, filename)
        inputs += self._get_fit_inputs()
        return inputs

    def _get_read_inputs(
        self, workflow_type: WorkflowType, filename: str, scan_number: int
    ) -> List[dict]:
        if workflow_type.xas:
            task_identifier = "XasTemperatureRead"
            subscan_number = 2
        else:
            task_identifier = "ScanTemperatureRead"
            subscan_number = 1
        return [
            {
                "task_identifier": task_identifier,
                "name": "filename",
                "value": filename,
            },
            {
                "task_identifier": task_identifier,
                "name": "scan_number",
                "value": scan_number,
            },
            {
                "task_identifier": task_identifier,
                "name": "subscan_number",
                "value": subscan_number,
            },
            {
                "task_identifier": task_identifier,
                "name": "retry_timeout",
                "value": 60,
            },
            {
                "task_identifier": task_identifier,
                "name": "energy_name",
                "value": self.energy_name,
            },
            {
                "task_identifier": task_identifier,
                "name": "mu_name",
                "value": self.mu_name,
            },
        ]

    def _get_plot_inputs(
        self, workflow_type: WorkflowType, filename: str
    ) -> List[dict]:
        if workflow_type.xas:
            task_identifier = "XasTemperaturePlot"
        else:
            task_identifier = "ScanTemperaturePlot"
        output_directory = directories.get_processed_subdir(filename, "temperature")
        return [
            {
                "task_identifier": task_identifier,
                "name": "output_directory",
                "value": output_directory,
            },
            {
                "task_identifier": task_identifier,
                "name": "extend_plotrange_left",
                "value": self.extend_plotrange_left,
            },
            {
                "task_identifier": task_identifier,
                "name": "extend_plotrange_right",
                "value": self.extend_plotrange_right,
            },
            {
                "task_identifier": task_identifier,
                "name": "two_color_difference",
                "value": self.two_color_difference,
            },
            {
                "task_identifier": task_identifier,
                "name": "dpi",
                "value": self.dpi,
            },
        ]

    def _get_fit_inputs(self) -> List[dict]:
        if not self.refit:
            return []
        task_identifier = "PlanckRadianceFit"
        return [
            {
                "task_identifier": task_identifier,
                "name": "wavelength_min",
                "value": self.wavelength_min,
            },
            {
                "task_identifier": task_identifier,
                "name": "wavelength_max",
                "value": self.wavelength_max,
            },
        ]


class Plotter(WithFlintAccess):
    def __init__(self) -> None:
        super().__init__()
        self._tasks = list()

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

    def _handle_workflow_result(self, future, timeout: int = 60):
        try:
            results = future.result(timeout=timeout)
            if not results:
                return
            filenames = results["filenames"]
            directory = os.path.dirname(filenames[0])

            plot = self._get_plot()
            plot.select_directory(directory)
        except Exception as e:
            logger.exception(e)

    def _spawn(self, *args, **kw):
        task = gevent.spawn(*args, **kw)
        self._tasks.append(task)
        self.purge_tasks()

    def _get_plot(self) -> TemperaturePlot:
        return super()._get_plot("Temperature", TemperaturePlot)

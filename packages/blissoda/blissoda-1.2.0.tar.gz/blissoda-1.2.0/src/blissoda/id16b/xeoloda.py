"""User API for HDF5 conversion on the Bliss repl"""

import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ewoksjob.client import submit

from ..bliss_globals import current_session
from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessor
from ..processor import BlissScanType
from ..utils import directories


class id16bXeol(
    BaseProcessor,
    parameters=[
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo("retry_timeout", category="data access"),
        ParameterInfo("queue", category="workflows", deprecated_names=["worker"]),
        ParameterInfo("calibration_x"),
        ParameterInfo("calibration_y"),
        ParameterInfo("threshold"),
        ParameterInfo("configuration_path"),
        ParameterInfo("h5name"),
        ParameterInfo("save_path"),
        ParameterInfo("normalization_counter"),
        ParameterInfo("main_counter"),
        ParameterInfo("pixels"),
    ],
):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> None:
        if defaults is None:
            defaults = {}
        defaults.setdefault("trigger_at", "END")
        defaults.setdefault("queue", "celery")
        defaults.setdefault("calibration_x", [0, 1])
        defaults.setdefault("calibration_y", [0, 1])
        defaults.setdefault("threshold", 0)
        defaults.setdefault("pixels", None)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        workflow_path = os.path.join(
            current_dir, "..", "resources/id16b/id16b_xeol.json"
        )
        defaults.setdefault("workflow", workflow_path)
        super().__init__(config=config, defaults=defaults)

    def on_new_scan_metadata(self, scan: BlissScanType) -> None:
        if not self.scan_requires_processing(scan):
            return
        kwargs = self.get_submit_arguments(scan)
        _ = submit(args=(self.workflow,), kwargs=kwargs, queue=self.queue)

    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> None:
        self.on_new_scan_metadata(scan)

    def scan_requires_processing(self, scan: BlissScanType) -> bool:
        if self.find_in_dict(scan.scan_info, self.main_counter):
            return True
        return False

    def find_in_dict(self, current_dict, key):
        try:
            if key == current_dict["display_name"]:
                return True
        except (KeyError, AttributeError):
            for value in current_dict.values():
                if isinstance(value, dict) and self.find_in_dict(value, key):
                    return True
        return False

    def get_submit_arguments(self, scan: BlissScanType) -> dict:
        return {
            "inputs": self.get_inputs(scan),
            "outputs": [{"all": False}],
        }

    def get_filename(self, scan: BlissScanType) -> str:
        filename = scan.scan_info.get("filename")
        if filename:
            return filename
        return current_session.scan_saving.filename

    def workflow_destination(self, scan: BlissScanType) -> str:
        filename = self.get_filename(scan)
        root = directories.get_processed_dir(filename)
        basename = "xeol.h5"
        return os.path.join(root, basename)

    def get_inputs(self, scan: BlissScanType) -> List[dict]:
        # do not read data from file "self.get_filename(scan)" there are issues
        # see id16b ewoks tasks for details
        filename = self.get_filename(scan)
        scan_id = scan._scan_data.key  # self.redis_key
        if self.save_path is None:
            output_filename = self.workflow_destination(scan)
        else:
            output_filename = self.save_path
        scan_nb = scan.scan_info.get("scan_nb")
        if output_filename and filename:
            inputs = [
                {
                    "name": "save_path",
                    "value": output_filename,
                    "task_identifier": "XeolStackFit",
                },
                {
                    "name": "stack_path",
                    "value": filename,
                    "task_identifier": "ReadStack",
                },
                {
                    "name": "stack_path",
                    "value": filename,
                    "task_identifier": "SaveXeolH5",
                },
                {"name": "key", "value": scan_id, "task_identifier": "ReadStack"},
                {"name": "key", "value": scan_id, "task_identifier": "SaveXeolH5"},
                {
                    "name": "scan_number",
                    "value": scan_nb,
                    "task_identifier": "ReadStack",
                },
                {
                    "name": "scan_number",
                    "value": scan_nb,
                    "task_identifier": "SaveXeolH5",
                },
            ]
        else:
            raise Exception("could not read save path and/or read path")

        if self.configuration_path:
            inputs.append(
                {
                    "name": "config_path",
                    "value": self.configuration_path,
                    "task_identifier": "ReadCorrectConfig",
                },
            )
        else:
            raise Exception(
                "Configuration path is required. Please set it before start"
            )

        if self.calibration_x is None:
            self.calibration_x = scan.scan_info.get("instrument", dict()).get(
                "calibration"
            )
        if self.calibration_x:
            inputs.append(
                {
                    "name": "calibration_x",
                    "value": self.calibration_x,
                    "task_identifier": "ReadStack",
                },
            )
            inputs.append(
                {
                    "name": "calibration_x",
                    "value": self.calibration_x,
                    "task_identifier": "SaveXeolH5",
                },
            )

        if self.calibration_y:
            inputs.append(
                {
                    "name": "calibration_y",
                    "value": self.calibration_y,
                    "task_identifier": "ReadStack",
                },
            )

        if self.h5name:
            inputs.append(
                {
                    "name": "h5name",
                    "value": self.h5name,
                    "task_identifier": "SaveXeolH5",
                },
            )

        if self.normalization_counter:
            inputs.append(
                {
                    "name": "norm_counter",
                    "value": self.normalization_counter,
                    "task_identifier": "ReadStack",
                },
            )

        if self.threshold:
            inputs.append(
                {
                    "name": "threshold",
                    "value": self.threshold,
                    "task_identifier": "ReadStack",
                },
            )

        if self.main_counter:
            inputs.append(
                {
                    "name": "counter",
                    "value": self.main_counter,
                    "task_identifier": "ReadStack",
                },
            )

        if self.pixels:
            inputs.append(
                {
                    "name": "pixels",
                    "value": self.pixels,
                    "task_identifier": "ReadStack",
                },
            )

        return inputs

    @property
    def calibration_x(self):
        return self._get_parameter("calibration_x")

    @property
    def calibration_y(self):
        return self._get_parameter("calibration_y")

    @property
    def threshold(self):
        return self._get_parameter("threshold")

    @property
    def configuration_path(self):
        return self._get_parameter("configuration_path")

    @property
    def h5name(self):
        return self._get_parameter("h5name")

    @property
    def normalization_counter(self):
        return self._get_parameter("normalization_counter")

    @property
    def main_counter(self):
        return self._get_parameter("main_counter")

    @property
    def save_path(self):
        return self._get_parameter("save_path")

    @property
    def pixels(self):
        return self._get_parameter("pixels")

    @calibration_x.setter
    def calibration_x(self, *args):
        if len(args) == 1:
            if isinstance(args[0], list) and len(args[0]) >= 2:
                self._set_parameter("calibration_x", args[0])
            else:
                raise Exception(
                    "Wrong format for calibration. Please insert a list or a sequence longer than 2"
                )
        elif len(args) >= 2:
            self._set_parameter("calibration_x", list(args))
        else:
            raise Exception(
                "Wrong format for calibration. Please insert a list or a sequence longer than 2"
            )

    @calibration_y.setter
    def calibration_y(self, *args):
        if len(args) == 1:
            if isinstance(args[0], list) and len(args[0]) >= 2:
                self._set_parameter("calibration_y", args[0])
            else:
                raise Exception(
                    "Wrong format for calibration. Please insert a list or a sequence longer than 2"
                )
        elif len(args) >= 2:
            self._set_parameter("calibration_y", list(args))
        else:
            raise Exception(
                "Wrong format for calibration. Please insert a list or a sequence longer than 2"
            )

    @threshold.setter
    def threshold(self, lower_limit):
        if lower_limit < 0:
            raise Exception("Lower limit cannot be negative")
        else:
            self._set_parameter("threshold", lower_limit)

    @configuration_path.setter
    def configuration_path(self, path):
        if os.path.exists(path):
            self._set_parameter("configuration_path", path)
        else:
            raise Exception("This path does not exist")

    @h5name.setter
    def h5name(self, filename):
        self._set_parameter("h5name", filename)

    @normalization_counter.setter
    def normalization_counter(self, counter):
        self._set_parameter("normalization_counter", counter)

    @main_counter.setter
    def main_counter(self, counter):
        self._set_parameter("main_counter", counter)

    @save_path.setter
    def save_path(self, path):
        if os.path.isdir(path):
            self._set_parameter("save_path", path)
        else:
            raise Exception("This folder does not exist. PLease create it manually.")

    @pixels.setter
    def pixels(self, pix):
        if isinstance(pix, list) and len(pix) == 2:
            self._set_parameter("pixels", pix)
        else:
            raise Exception("Inappropriate format")

from __future__ import annotations

import json
import time
from configparser import ConfigParser
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ewoksjob.client import submit

from ..persistent.parameters import ParameterInfo
from ..persistent.parameters import _format_info_category
from ..processor import BaseProcessor
from ..processor import BlissScanType
from ..resources import resource_filename
from .flint_tomo_imshow import SingleSliceImshow
from .tomo_model import TomoProcessorModel


class TomoProcessor(
    BaseProcessor,
    parameters=[
        ParameterInfo("workflow", category="workflows"),
        ParameterInfo("queue", category="workflows"),
        ParameterInfo(
            "_bliss_hdf5_path",
            category="files",
            doc="HDF5 Dataset path (filled automatically)",
        ),
        ParameterInfo(
            "_output_path",
            category="files",
            doc="Nx output path (filled automatically)",
        ),
        ParameterInfo(
            "nabu_config_file",
            category="slice_reconstruction_parameters",
            doc="Nabu configuration file",
        ),
        ParameterInfo(
            "slice_index",
            category="slice_reconstruction_parameters",
            doc="Index of the slice that will be reconstructed online",
        ),
        ParameterInfo(
            "rotation_axis_position",
            category="slice_reconstruction_parameters",
            doc="Pixel position of the centre of rotation in the frame (or method)",
        ),
        ParameterInfo(
            "phase_retrieval_method",
            category="slice_reconstruction_parameters",
            doc="Phase retrieval method or 'None'",
        ),
        ParameterInfo(
            "delta_beta",
            category="slice_reconstruction_parameters",
            doc="For Paganin or CTF phase retrieval, default is 100",
        ),
        ParameterInfo(
            "show_last_slice",
            category="flint_display_parameters",
            doc="If True, display the last reconstructed slice in Flint",
        ),
    ],
):

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the TomoProcessor for converting BLISS HDF5 data to Nexus (NX) format.

        This processor can be integrated into a BLISS beamline configuration. Typical
        usage involves adding the following to a configuration yaml file:

        - name: tomo_blissoda
          plugin: generic
          class: TomoProcessor
          package: blissoda.tomo.tomo_processor
        """
        if defaults is None:
            defaults = {}
        defaults.setdefault("trigger_at", "END")
        defaults.setdefault("workflow", "tomo_processor.json")
        defaults.setdefault("nabu_config_file", None)
        defaults.setdefault("slice_index", "middle")
        defaults.setdefault("rotation_axis_position", "sliding-window")
        defaults.setdefault("phase_retrieval_method", "None")
        defaults.setdefault("delta_beta", "100")
        defaults.setdefault("show_last_slice", False)
        self.imshow = SingleSliceImshow(history=1)

        self._tomo_model = TomoProcessorModel(**defaults)

        super().__init__(config=config, defaults=defaults)

    def __info__(self) -> str:
        categories = self._info_categories()
        for cats in categories:
            for key in categories[cats]:
                if key in dir(self):
                    categories[cats][key] = getattr(self, key)

        # Does not display delta_beta if phase_retrieval_method is None
        parameters = categories.get("slice_reconstruction_parameters")
        if parameters is not None:
            method = parameters.get("phase_retrieval_method")
            if method == "None":
                parameters.pop("delta_beta", None)

        return "\n" + "\n\n".join(
            [
                f"{name.replace('_', ' ').title()}:\n {_format_info_category(category)}"
                for name, category in categories.items()
                if category
            ]
        )

    def load_nabu_config_file(self, nabu_file, allow_no_value=False):
        """
        Parse a configuration file and returns a dictionary.
        """
        if nabu_file and Path(nabu_file).exists():
            parser = ConfigParser(
                inline_comment_prefixes=("#",),
                allow_no_value=allow_no_value,
            )
            with open(nabu_file) as fid:
                file_content = fid.read()
            parser.read_string(file_content)
            nabu_dict = parser._sections
        else:
            nabu_dict = dict()

        # Ensure nested dictionaries exist
        nabu_dict.setdefault("dataset", {})
        nabu_dict.setdefault("reconstruction", {})
        nabu_dict.setdefault("reconstruction", {})[
            "rotation_axis_position"
        ] = self.rotation_axis_position
        nabu_dict.setdefault("phase", {})["method"] = self.phase_retrieval_method
        nabu_dict["phase"]["delta_beta"] = self.delta_beta
        nabu_dict.setdefault("output", {})

        return nabu_dict

    def _get_scan_parameters(self, scan: BlissScanType) -> Dict[str, Any]:
        scan_parameters = dict()
        for key in list(scan.scan_info.keys()):
            scan_parameters[key] = scan.scan_info[key]
        return scan_parameters

    def _get_inputs(self, scan: BlissScanType) -> List[Dict[str, Any]]:
        scan_parameters = self._get_scan_parameters(scan)
        scan_path = Path(scan_parameters["technique"]["saving"]["path"])
        self._bliss_hdf5_path = str(scan_path / f"{scan_path.name}.h5")
        self._output_path = self._bliss_hdf5_path.replace(
            "RAW_DATA", "PROCESSED_DATA"
        ).replace(".h5", ".nx")
        inputs = list()
        inputs.append(
            {
                "task_identifier": "ewokstomo.tasks.nxtomomill.H5ToNx",
                "name": "bliss_hdf5_path",
                "value": self._bliss_hdf5_path,
            }
        )
        inputs.append(
            {
                "task_identifier": "ewokstomo.tasks.nxtomomill.H5ToNx",
                "name": "nx_path",
                "value": self._output_path,
            }
        )

        inputs.append(
            {
                "task_identifier": "ewokstomo.tasks.reconstruct_slice.ReconstructSlice",
                "name": "nx_path",
                "value": self._output_path,
            }
        )
        inputs.append(
            {
                "task_identifier": "ewokstomo.tasks.reconstruct_slice.ReconstructSlice",
                "name": "config_dict",
                "value": self.load_nabu_config_file(self.nabu_config_file),
            }
        )
        inputs.append(
            {
                "task_identifier": "ewokstomo.tasks.reconstruct_slice.ReconstructSlice",
                "name": "slice_index",
                "value": self.slice_index,
            }
        )

        return inputs

    def _get_workflow(self):
        with open(resource_filename("tomo", self.workflow), "r") as wf:
            return json.load(wf)

    def _get_submit_arguments(self, scan) -> Dict[str, Any]:
        return {
            "inputs": self._get_inputs(scan),
        }

    def workflow_destination(self) -> str:
        """
        Returns the destination path for the workflow output.
        """
        return self._output_path.replace(".nx", ".json")

    def execute_workflow(self, scan: BlissScanType) -> None:
        if "tomoconfig" not in scan.scan_info.get("technique", ""):
            return
        workflow = self._get_workflow()
        kwargs = self._get_submit_arguments(scan)
        kwargs["convert_destination"] = self.workflow_destination()
        time.sleep(2)
        future = submit(args=(workflow,), kwargs=kwargs, queue=self.queue)
        if self.show_last_slice:
            self.imshow._spawn(self.imshow.handle_workflow_result, future)

    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> None:
        self.execute_workflow(scan)

    @property
    def workflow(self):
        return self._tomo_model.workflow

    @workflow.setter
    def workflow(self, value):
        self._tomo_model.workflow = value

    @property
    def queue(self):
        return self._tomo_model.queue

    @queue.setter
    def queue(self, value):
        self._tomo_model.queue = value

    @property
    def nabu_config_file(self):
        return self._tomo_model.nabu_config_file

    @nabu_config_file.setter
    def nabu_config_file(self, value):
        self._tomo_model.nabu_config_file = value

    @property
    def slice_index(self):
        return self._tomo_model.slice_index

    @slice_index.setter
    def slice_index(self, value):
        self._tomo_model.slice_index = str(value)

    @property
    def rotation_axis_position(self):
        return self._tomo_model.rotation_axis_position

    @rotation_axis_position.setter
    def rotation_axis_position(self, value):
        self._tomo_model.rotation_axis_position = value

    @property
    def phase_retrieval_method(self):
        return self._tomo_model.phase_retrieval_method

    @phase_retrieval_method.setter
    def phase_retrieval_method(self, value):
        self._tomo_model.phase_retrieval_method = value

    @property
    def delta_beta(self):
        return self._tomo_model.delta_beta

    @delta_beta.setter
    def delta_beta(self, value):
        self._tomo_model.delta_beta = value

    @property
    def show_last_slice(self):
        return self._tomo_model.show_last_slice

    @show_last_slice.setter
    def show_last_slice(self, value):
        self._tomo_model.show_last_slice = value

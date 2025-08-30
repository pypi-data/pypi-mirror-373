"""
.. code-block:: python

    DEMO_SESSION [1]: from blissoda.demo.stscan_processor import stscan_processor
    DEMO_SESSION [2]: stscan_processor
    DEMO_SESSION [3]: stscan_processor.submit_workflows()
"""

import json
import os
from contextlib import contextmanager
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ewoksjob.client import submit

from ..automation import BlissAutomationObject
from ..bliss_globals import current_session
from ..persistent.parameters import ParameterInfo
from ..utils.directories import get_processed_dir
from ..utils.directories import get_workflows_dir


class _NoRepr:
    def __repr__(self):
        return ""


_NOREPR = _NoRepr()


class StScanProcessor(
    BlissAutomationObject,
    parameters=[
        ParameterInfo("_convert_workflow"),
        ParameterInfo("_rebinsum_workflow"),
        ParameterInfo("_extract_workflow"),
        ParameterInfo("session_in_outprefix"),
    ],
):
    """Submit data processing workflows on stscan results

    StScanProcessor().submit_workflows()
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault(
            "_convert_workflow",
            "/data/id22/inhouse/ewoks/resources/workflows/convert.json",
        )
        defaults.setdefault(
            "_rebinsum_workflow",
            "/data/id22/inhouse/ewoks/resources/workflows/rebinsum.json",
        )
        defaults.setdefault(
            "_extract_workflow",
            "/data/id22/inhouse/ewoks/resources/workflows/extract.json",
        )
        defaults.setdefault("session_in_outprefix", False)

        super().__init__(config=config, defaults=defaults)

        self._context_cache = dict()

    @property
    def convert_workflow(self):
        return self._convert_workflow

    @convert_workflow.setter
    def convert_workflow(self, value):
        if os.path.exists(self._convert_workflow):
            with self._convert_context():
                self._convert_workflow = value
        else:
            self._convert_workflow = value
            with self._convert_context():
                pass

    @property
    def rebinsum_workflow(self):
        return self._rebinsum_workflow

    @rebinsum_workflow.setter
    def rebinsum_workflow(self, value):
        if os.path.exists(self._rebinsum_workflow):
            with self._rebinsum_context():
                self._rebinsum_workflow = value
        else:
            self._rebinsum_workflow = value
            with self._rebinsum_context():
                pass

    @property
    def extract_workflow(self):
        return self._extract_workflow

    @extract_workflow.setter
    def extract_workflow(self, value):
        if os.path.exists(self._extract_workflow):
            with self._extract_context():
                self._extract_workflow = value
        else:
            self._extract_workflow = value
            with self._extract_context():
                pass

    def _info_categories(self) -> Dict[str, dict]:
        with self._convert_context():
            with self._rebinsum_context():
                with self._extract_context():
                    return {
                        "workflows": self._workflows_info(),
                        "execution": self._execution_info(),
                        "convert": self._convert_info(),
                        "rebin": self._rebin_info(),
                        "sum": self._sum_info(),
                        "extract": self._extract_info(),
                    }

    def _execution_info(self) -> dict:
        info = dict()
        info["session_in_outprefix"] = self.session_in_outprefix
        return info

    def _workflows_info(self) -> dict:
        info = dict()
        info["convert"] = self.convert_workflow
        info["rebin/sum"] = self.rebinsum_workflow
        info["extract"] = self.extract_workflow
        return info

    def _convert_info(self) -> dict:
        info = dict()
        info["do_convert"] = self.do_convert
        info["Results:"] = _NOREPR
        info.update(self._outdirs_info(self.convertdirs))
        info[" include_proposal_outdir"] = self.convert_include_proposal_outdir
        return info

    def _rebin_info(self) -> dict:
        info = dict()
        info["do_rebin"] = self.do_rebin

        info["Parameters:"] = _NOREPR
        info[" range"] = self.range
        info[" delta2theta"] = self.delta2theta
        info[" startp"] = self.startp
        info[" parsfile"] = self.parsfile

        info["Results:"] = _NOREPR
        info.update(self._outdirs_info(self.rebindirs))
        info[" include_proposal_outdir"] = self.rebin_include_proposal_outdir

        return info

    def _sum_info(self) -> dict:
        info = dict()
        info["do_sum_single"] = self.do_sum_single
        info["do_sum_all"] = self.do_sum_all

        info["Parameters:"] = _NOREPR
        info[" binsize"] = self.binsize
        info[" resfile"] = self.resfile
        info[" advanced"] = self.advanced_sum_arguments

        info["Results:"] = _NOREPR
        info[" include_proposal_outdir"] = self.sum_include_proposal_outdir

        return info

    def _extract_info(self) -> dict:
        info = dict()
        info["do_extract"] = self.do_extract

        info["Parameters:"] = _NOREPR
        info[" tth_min"] = self.tth_min
        info[" tth_max"] = self.tth_max
        info[" full_tth"] = self.full_tth
        info[" startp"] = self.startp
        info[" inp_file"] = self.inp_file
        info[" inp_step"] = self.inp_step

        info["Results:"] = _NOREPR
        info[" include_proposal_outdir"] = self.extract_include_proposal_outdir

        return info

    @property
    def convertdirs(self):
        with self._convert_context() as workflow:
            return self._get_node_parameter(workflow, "convert", "outdirs")

    @convertdirs.setter
    def convertdirs(self, value):
        with self._convert_context() as workflow:
            self._set_node_parameter(workflow, "convert", "outdirs", value)

    @property
    def rebindirs(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "rebin", "outdirs")

    @rebindirs.setter
    def rebindirs(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "rebin", "outdirs", value)
            self._set_node_parameter(workflow, "convert", "outdirs", value)

    @property
    def convert_include_proposal_outdir(self):
        return True

    @property
    def rebin_include_proposal_outdir(self):
        return True

    @property
    def sum_include_proposal_outdir(self):
        return True

    @property
    def extract_include_proposal_outdir(self):
        return True

    def _outdirs_info(self, outdirs):
        if not outdirs:
            return dict()
        return {f" {k}": v for k, v in outdirs.items()}

    def submit_workflows(
        self, filename=None, outprefix=None, scannr=None, extract=False
    ):
        if scannr is None:
            entries = list()
        else:
            entries = [f"{scannr}.1", f"{scannr}.2"]
        if outprefix is None:
            if self.session_in_outprefix:
                outprefix = f"{current_session.scan_saving.proposal_name}_{current_session.scan_saving.proposal_session_name}"
            else:
                outprefix = current_session.scan_saving.proposal_name
        if filename is None:
            filename = current_session.scan_saving.filename
        if self.do_convert:
            convert_destination = self._convert_destination(
                "convert", filename, scan=scannr
            )
            self._submit_convert_workflow(
                filename, entries, outprefix, list(), convert_destination
            )
        if extract:
            convert_destination = self._convert_destination(
                "extract", filename, scan=scannr
            )
            self._submit_extract_workflow(
                filename, entries, outprefix, list(), convert_destination
            )
        elif self.do_rebin:
            for inputs, kw in self._iter_rebinsum_parameters():
                convert_destination = self._convert_destination(
                    "rebinsum", filename, scan=scannr, **kw
                )
                self._submit_rebinsum_workflow(
                    filename, entries, outprefix, inputs, convert_destination
                )

    def _iter_rebinsum_parameters(self):
        for binsize in self.binsize:
            for delta2theta in self.delta2theta:
                inputs = [
                    {"id": "rebin", "name": "delta2theta", "value": delta2theta},
                    {"id": "sum", "name": "binsize", "value": binsize},
                ]
                convert_destination = {"w": delta2theta, "b": binsize}
                yield inputs, convert_destination

    def _convert_destination(self, workflowname, filename, **kw):
        root_dir = self._get_workflows_dir(filename)
        dirname = os.path.join(root_dir, workflowname)
        basename = os.path.splitext(os.path.basename(filename))[0]
        for name, value in kw.items():
            if value is None:
                continue
            value = str(value).replace(".", "")
            basename += f"_{name}{value}"
        return os.path.join(dirname, basename + ".json")

    def _get_workflows_dir(self, dataset_filename: str) -> str:
        return get_workflows_dir(dataset_filename)

    @property
    def delta2theta(self):
        with self._rebinsum_context() as workflow:
            delta2theta_list = self._get_node_parameter(
                workflow, "rebin", "delta2theta", dest="for_bliss"
            )
            if delta2theta_list is None:
                delta2theta = self._get_node_parameter(workflow, "rebin", "delta2theta")
                if delta2theta is None:
                    delta2theta_list = list()
                else:
                    delta2theta_list = [delta2theta]
        return delta2theta_list

    @delta2theta.setter
    def delta2theta(self, value):
        try:
            delta2theta_list = list(value)
        except Exception:
            delta2theta_list = [value]
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(
                workflow, "rebin", "delta2theta", delta2theta_list[0]
            )
            self._set_node_parameter(
                workflow, "rebin", "delta2theta", delta2theta_list, dest="for_bliss"
            )

    @property
    def binsize(self):
        with self._rebinsum_context() as workflow:
            binsize_list = self._get_node_parameter(
                workflow, "sum", "binsize", dest="for_bliss"
            )
            if binsize_list is None:
                binsize = self._get_node_parameter(workflow, "sum", "binsize")
                if binsize is None:
                    binsize_list = list()
                else:
                    binsize_list = [binsize]
            return binsize_list

    @binsize.setter
    def binsize(self, value):
        try:
            binsize_list = list(value)
        except Exception:
            binsize_list = [value]
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "sum", "binsize", binsize_list[0])
            self._set_node_parameter(
                workflow, "sum", "binsize", binsize_list, dest="for_bliss"
            )

    @property
    def parsfile(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "rebin", "parsfile")

    @parsfile.setter
    def parsfile(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "rebin", "parsfile", value)

    @property
    def range(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "rebin", "range")

    @range.setter
    def range(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "rebin", "range", value)

    @property
    def startp(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "rebin", "startp")

    @startp.setter
    def startp(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "rebin", "startp", value)
        with self._extract_context() as workflow:
            self._set_node_parameter(workflow, "extract", "startp", value)

    @property
    def device(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "rebin", "device")

    @device.setter
    def device(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "rebin", "device", value)

    @property
    def resfile(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "sum", "resfile")

    @resfile.setter
    def resfile(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "sum", "resfile", value)

    @property
    def advanced_sum_arguments(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "sum", "advanced")

    @advanced_sum_arguments.setter
    def advanced_sum_arguments(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "sum", "advanced", value)

    @property
    def tth_min(self):
        with self._extract_context() as workflow:
            return self._get_node_parameter(workflow, "extract", "tth_min")

    @tth_min.setter
    def tth_min(self, value):
        with self._extract_context() as workflow:
            self._set_node_parameter(workflow, "extract", "tth_min", value)

    @property
    def tth_max(self):
        with self._extract_context() as workflow:
            return self._get_node_parameter(workflow, "extract", "tth_max")

    @tth_max.setter
    def tth_max(self, value):
        with self._extract_context() as workflow:
            self._set_node_parameter(workflow, "extract", "tth_max", value)

    @property
    def full_tth(self):
        with self._extract_context() as workflow:
            return self._get_node_parameter(workflow, "extract", "full_tth")

    @full_tth.setter
    def full_tth(self, value):
        with self._extract_context() as workflow:
            self._set_node_parameter(workflow, "extract", "full_tth", value)

    @property
    def inp_file(self):
        with self._extract_context() as workflow:
            return self._get_node_parameter(workflow, "extract", "inp_file")

    @inp_file.setter
    def inp_file(self, value):
        with self._extract_context() as workflow:
            self._set_node_parameter(workflow, "extract", "inp_file", value)

    @property
    def inp_step(self):
        with self._extract_context() as workflow:
            return self._get_node_parameter(workflow, "extract", "inp_step")

    @inp_step.setter
    def inp_step(self, value):
        with self._extract_context() as workflow:
            self._set_node_parameter(workflow, "extract", "inp_step", value)

    @property
    def do_rebin(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "rebin", "do", dest="for_bliss")

    @do_rebin.setter
    def do_rebin(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "rebin", "do", value, dest="for_bliss")

    @property
    def do_convert(self):
        return True

    @property
    def do_sum_single(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "sum", "sum_single")

    @do_sum_single.setter
    def do_sum_single(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "sum", "sum_single", value)
        if value:
            self.do_rebin = True

    @property
    def do_sum_all(self):
        with self._rebinsum_context() as workflow:
            return self._get_node_parameter(workflow, "sum", "sum_all")

    @do_sum_all.setter
    def do_sum_all(self, value):
        with self._rebinsum_context() as workflow:
            self._set_node_parameter(workflow, "sum", "sum_all", value)
        if value:
            self.do_rebin = True

    @property
    def do_extract(self):
        return "< from command stscan(..., extract=False) >"

    def _submit_convert_workflow(
        self,
        filename: str,
        entries: List[str],
        outprefix: str,
        inputs: List[dict],
        convert_destination: str,
    ):
        with self._convert_context() as workflow:
            pass
        primary_outdir = get_processed_dir(filename)
        self._add_wait_convert_inputs(inputs, filename, entries)
        self._add_convert_inputs(inputs, outprefix, primary_outdir)
        self._submit_job(workflow, inputs, convert_destination, queue="solo1")

    def _submit_rebinsum_workflow(
        self,
        filename: str,
        entries: List[str],
        outprefix: str,
        inputs: List[dict],
        convert_destination: str,
    ):
        with self._rebinsum_context() as workflow:
            pass
        primary_outdir = get_processed_dir(filename)
        self._add_wait_rebin_inputs(inputs, filename, entries)
        self._add_rebin_inputs(inputs, outprefix, primary_outdir)
        self._add_convertrebin_inputs(inputs, primary_outdir)
        self._add_sum_inputs(inputs, primary_outdir)
        self._submit_job(workflow, inputs, convert_destination, queue="solo2")

    def _submit_extract_workflow(
        self,
        filename: str,
        entries: List[str],
        outprefix: str,
        inputs: List[dict],
        convert_destination: str,
    ):
        with self._extract_context() as workflow:
            pass
        primary_outdir = get_processed_dir(filename)
        self._add_wait_extract_inputs(inputs, filename, entries)
        self._add_extract_inputs(inputs, outprefix, primary_outdir)
        self._submit_job(workflow, inputs, convert_destination, queue="solo2")

    def _submit_job(self, workflow, inputs, convert_destination, **kw):
        submit(
            args=(workflow,),
            kwargs={"inputs": inputs, "convert_destination": convert_destination},
            **kw,
        )

    def _save_default_convert_workflow(self):
        workflow = self._convert_graph()
        self._add_wait_convert_default_inputs(workflow)
        self._add_convert_default_inputs(workflow)
        self._save_workflow(self.convert_workflow, workflow)
        return workflow

    def _save_default_rebinsum_workflow(self):
        workflow = self._rebinsum_graph()
        self._add_wait_rebin_default_inputs(workflow)
        self._add_rebin_default_inputs(workflow)
        self._add_convertrebin_default_inputs(workflow)
        self._add_sum_default_inputs(workflow)
        self._save_workflow(self.rebinsum_workflow, workflow)
        return workflow

    def _save_default_extract_workflow(self):
        workflow = self._extract_graph()
        self._add_wait_extract_default_inputs(workflow)
        self._add_extract_default_inputs(workflow)
        self._save_workflow(self.extract_workflow, workflow)
        return workflow

    def _save_workflow(self, filename, workflow):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as fh:
            json.dump(workflow, fh, indent=2)

    @contextmanager
    def _convert_context(self):
        """Creates the workflow on disk when it does not exist"""
        with self._workflow_context("convert") as workflow:
            yield workflow

    @contextmanager
    def _rebinsum_context(self):
        """Creates the workflow on disk when it does not exist"""
        with self._workflow_context("rebinsum") as workflow:
            yield workflow

    @contextmanager
    def _extract_context(self):
        """Creates the workflow on disk when it does not exist"""
        with self._workflow_context("extract") as workflow:
            yield workflow

    @contextmanager
    def _workflow_context(self, workflow_id: str):
        """Re-entrant context which loads/creates the workflow upon entering
        and saves the workflow upon exiting."""
        filename = self._get_workflow_filename(workflow_id)
        workflow = self._context_cache.get(filename)
        if workflow is not None:
            yield workflow
            return
        if os.path.exists(filename):
            with open(filename, "r") as fh:
                workflow = json.load(fh)
        else:
            workflow = self._create_default_workflow(workflow_id)
        self._context_cache[filename] = workflow
        try:
            yield workflow
        finally:
            self._context_cache.pop(filename)
        filename = self._get_workflow_filename(workflow_id)
        self._save_workflow(filename, workflow)

    def _get_workflow_filename(self, workflow_id):
        if workflow_id == "convert":
            return self.convert_workflow
        elif workflow_id == "rebinsum":
            return self.rebinsum_workflow
        elif workflow_id == "extract":
            return self.extract_workflow
        assert False, f"Unkown workflow '{workflow_id}'"

    def _create_default_workflow(self, workflow_id):
        if workflow_id == "convert":
            return self._save_default_convert_workflow()
        elif workflow_id == "rebinsum":
            return self._save_default_rebinsum_workflow()
        elif workflow_id == "extract":
            return self._save_default_extract_workflow()
        assert False, f"Unkown workflow '{workflow_id}'"

    def _get_node_attrs(self, workflow, node_id):
        for node_attrs in workflow["nodes"]:
            if node_attrs["id"] == node_id:
                return node_attrs

    def _get_node_parameter(self, workflow, node_id, name, dest="default_inputs"):
        node_attrs = self._get_node_attrs(workflow, node_id)
        for argument in node_attrs.get(dest, list()):
            if argument["name"] == name:
                return argument["value"]

    def _set_node_parameter(
        self, workflow, node_id, name, value, dest="default_inputs"
    ):
        node_attrs = self._get_node_attrs(workflow, node_id)
        for argument in node_attrs.setdefault(dest, list()):
            if argument["name"] == name:
                argument["value"] = value
                return
        node_attrs[dest].append({"name": name, "value": value})

    def _convert_graph(self):
        nodes = [
            {
                "id": "wait",
                "task_type": "class",
                "task_identifier": "ewoksid22.wait.WaitScansFinished",
            },
            {
                "id": "convert",
                "task_type": "class",
                "task_identifier": "ewoksid22.convert.ID22H5ToSpec",
            },
        ]
        links = [
            {
                "source": "wait",
                "target": "convert",
                "data_mapping": [
                    {"source_output": "filename", "target_input": "filename"},
                    # {"source_output": "entries", "target_input": "entries"},
                ],
            },
        ]
        return {"graph": {"id": "convert"}, "nodes": nodes, "links": links}

    def _rebinsum_graph(self):
        nodes = [
            {
                "id": "wait",
                "task_type": "class",
                "task_identifier": "ewoksid22.wait.WaitScansFinished",
            },
            {
                "id": "rebin",
                "task_type": "class",
                "task_identifier": "ewoksid22.rebin.ID22Rebin",
            },
            {
                "id": "convert",
                "task_type": "class",
                "task_identifier": "ewoksid22.convert.ID22H5ToSpec",
            },
            {
                "id": "sum",
                "task_type": "class",
                "task_identifier": "ewoksid22.sum.ID22Sum",
            },
        ]
        links = [
            {
                "source": "wait",
                "target": "rebin",
                "data_mapping": [
                    {"source_output": "filename", "target_input": "filename"},
                    # {"source_output": "entries", "target_input": "entries"},
                ],
            },
            {
                "source": "wait",
                "target": "convert",
                "data_mapping": [
                    {"source_output": "filename", "target_input": "filename"},
                    # {"source_output": "entries", "target_input": "entries"},
                ],
            },
            {
                "source": "wait",
                "target": "sum",
                "data_mapping": [
                    {"source_output": "filename", "target_input": "raw_filename"},
                    # {"source_output": "entries", "target_input": "entries"},
                ],
            },
            {
                "source": "rebin",
                "target": "convert",
                "data_mapping": [
                    {"source_output": "outfile", "target_input": "rebin_filename"}
                ],
            },
            {
                "source": "convert",
                "target": "sum",
                "data_mapping": [
                    {"source_output": "outfile", "target_input": "filename"},
                ],
            },
        ]
        return {"graph": {"id": "rebinsum"}, "nodes": nodes, "links": links}

    def _extract_graph(self):
        nodes = [
            {
                "id": "wait",
                "task_type": "class",
                "task_identifier": "ewoksid22.wait.WaitScansFinished",
            },
            {
                "id": "extract",
                "task_type": "class",
                "task_identifier": "ewoksid22.extract.ID22TopasExtract",
            },
        ]
        links = [
            {
                "source": "wait",
                "target": "extract",
                "data_mapping": [
                    {"source_output": "filename", "target_input": "filename"},
                    {"source_output": "entries", "target_input": "entries"},
                ],
            },
        ]
        return {"graph": {"id": "extract"}, "nodes": nodes, "links": links}

    def _add_wait_convert_inputs(self, inputs: list, filename: str, entries: list):
        inputs += [
            {"id": "wait", "name": "filename", "value": filename},
            {"id": "wait", "name": "entries", "value": entries},
        ]

    def _add_wait_convert_default_inputs(self, workflow: dict):
        node_attrs = self._get_node_attrs(workflow, "wait")
        node_attrs["default_inputs"] = [
            {"name": "retry_timeout", "value": 30},
        ]

    def _add_wait_rebin_inputs(self, inputs: list, filename: str, entries: list):
        inputs += [
            {"id": "wait", "name": "filename", "value": filename},
            {"id": "wait", "name": "entries", "value": entries},
        ]

    def _add_wait_rebin_default_inputs(self, workflow: dict):
        node_attrs = self._get_node_attrs(workflow, "wait")
        node_attrs["default_inputs"] = [
            {"name": "retry_timeout", "value": 30},
        ]

    def _add_wait_extract_inputs(self, inputs: list, filename: str, entries: list):
        inputs += [
            {"id": "wait", "name": "filename", "value": filename},
            {"id": "wait", "name": "entries", "value": entries},
        ]

    def _add_wait_extract_default_inputs(self, workflow: dict):
        node_attrs = self._get_node_attrs(workflow, "wait")
        node_attrs["default_inputs"] = [
            {"name": "retry_timeout", "value": 30},
        ]

    def _add_rebin_inputs(self, inputs: list, outprefix: str, primary_outdir: str):
        if self.rebin_include_proposal_outdir:
            inputs += [
                {"id": "rebin", "name": "outprefix", "value": outprefix},
                {"id": "rebin", "name": "primary_outdir", "value": primary_outdir},
            ]

    def _add_rebin_default_inputs(self, workflow: dict):
        node_attrs = self._get_node_attrs(workflow, "rebin")
        node_attrs["for_bliss"] = [{"name": "do", "value": False}]
        node_attrs["default_inputs"] = [
            {
                "name": "parsfile",
                "value": "/data/id22/inhouse/CD_GC_PDF/advanced_50keV/patterns/for_wout/out7.pars",
            },
            {"name": "range", "value": [float("nan"), float("nan")]},
            {"name": "delta2theta", "value": 0.003},
            {"name": "startp", "value": 31},
            {"name": "device", "value": 0},
            {
                "name": "outdirs",
                "value": {
                    "primary": "opid22@diffract22new:/users/opid22/data1/",
                    # "secondary": "opid22@lid22bliss:/users/opid22/data1/",
                    "backup": "opid22@lid22bliss:/data/id22/backup/data22/",
                },
            },
            {"name": "retry_timeout", "value": 30},
        ]

    def _add_convertrebin_inputs(self, inputs: list, primary_outdir: str):
        if self.convert_include_proposal_outdir:
            inputs += [
                {"id": "convert", "name": "primary_outdir", "value": primary_outdir}
            ]

    def _add_convertrebin_default_inputs(self, workflow: dict):
        node_attrs = self._get_node_attrs(workflow, "convert")
        node_attrs["default_inputs"] = [
            {
                "name": "outdirs",
                "value": {
                    "primary": "opid22@diffract22new:/users/opid22/data1/",
                    # "secondary": "opid22@lid22bliss:/users/opid22/data1/",
                    "backup": "opid22@lid22bliss:/data/id22/backup/data22/",
                },
            },
            {"name": "retry_timeout", "value": 30},
            {"name": "ascii_extension", "value": ".adv"},
        ]

    def _add_sum_inputs(self, inputs: list, primary_outdir: str):
        if self.sum_include_proposal_outdir:
            inputs += [{"id": "sum", "name": "primary_outdir", "value": primary_outdir}]

    def _add_sum_default_inputs(self, workflow: dict):
        node_attrs = self._get_node_attrs(workflow, "sum")
        node_attrs["default_inputs"] = [
            {
                "name": "resfile",
                "value": "/data/id22/inhouse/CD_GC_PDF/advanced_50keV/patterns/for_wout/temp.res",
            },
            {"name": "binsize", "value": 0.002},
            {"name": "sum_single", "value": False},
            {"name": "sum_all", "value": False},
            {"name": "retry_timeout", "value": 30},
            {"name": "ascii_extension", "value": ".adv"},
            {"name": "advanced", "value": None},
        ]

    def _add_convert_inputs(self, inputs: list, outprefix: str, primary_outdir: str):
        if self.convert_include_proposal_outdir:
            inputs += [
                {"id": "convert", "name": "outprefix", "value": outprefix},
                {
                    "id": "convert",
                    "name": "primary_outdir",
                    "value": primary_outdir,
                },
            ]

    def _add_convert_default_inputs(self, workflow: dict):
        node_attrs = self._get_node_attrs(workflow, "convert")
        node_attrs["default_inputs"] = [
            {
                "name": "outdirs",
                "value": {
                    "primary": "opid22@diffract22new:/users/opid22/data1/",
                    # "secondary": "opid22@lid22bliss:/users/opid22/data1/",
                    "backup": "opid22@lid22bliss:/data/id22/backup/data22/",
                },
            },
            {"name": "retry_timeout", "value": 30},
        ]

    def _add_extract_inputs(self, inputs: list, outprefix: str, primary_outdir: str):
        if self.extract_include_proposal_outdir:
            inputs += [
                {"id": "extract", "name": "outprefix", "value": outprefix},
                {
                    "id": "extract",
                    "name": "primary_outdir",
                    "value": primary_outdir,
                },
            ]

    def _add_extract_default_inputs(self, workflow: dict):
        node_attrs = self._get_node_attrs(workflow, "extract")
        node_attrs["default_inputs"] = [
            {"name": "tth_min", "value": None},
            {"name": "tth_max", "value": None},
            {"name": "full_tth", "value": False},
            {"name": "inp_file", "value": "/users/opid22/out7_files/LaB6_all7_os.inp"},
            {"name": "inp_step", "value": 2},
            {"name": "startp", "value": 31},
        ]

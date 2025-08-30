from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ewoksjob.client import submit
from ewoksutils.task_utils import task_inputs

from ..import_utils import unavailable_function
from ..persistent.parameters import ParameterInfo
from ..processor import BaseProcessorWithPlotting
from ..processor import BlissScanType
from ..utils.directories import get_filename
from ..utils.directories import master_output_filename
from ..utils.directories import workflow_destination
from ..xrpd.plotter import XrpdPlotter

try:
    from id09.status import get_xray_energy
except ImportError as ex:
    get_xray_energy = unavailable_function(ex)


class TxsProcessor(
    BaseProcessorWithPlotting,
    parameters=[
        ParameterInfo("distance", category="Txs", doc="meter", validator=float),
        ParameterInfo("center", category="Txs", doc="pixel (hor, ver)"),
        ParameterInfo("binning", category="Txs", doc="(hor, ver)"),
        ParameterInfo("detector", category="Txs", validator=str),
        ParameterInfo("pixel", category="Txs", doc="meter (hor, ver)"),
        ParameterInfo("energy", category="Txs", doc="eV", validator=float),
        ParameterInfo("integrate1d_options", category="Txs"),
    ],
):
    plotter_class = XrpdPlotter

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        defaults.setdefault("distance", 1)
        defaults.setdefault("center", (960, 960))
        defaults.setdefault("binning", 2)
        defaults.setdefault("detector", "rayonix")
        defaults.setdefault("pixel", None)
        defaults.setdefault("energy", "automatic")
        defaults.setdefault("integrate1d_options", dict())

        super().__init__(config=config, defaults=defaults)

    def _trigger_workflow_on_new_scan(self, scan: BlissScanType) -> None:
        self.trigger_workflow_on_new_scan(scan)

    def trigger_workflow_on_new_scan(self, scan: BlissScanType) -> None:
        if not self.scan_requires_processing(scan):
            return None

        workflow = self.get_workflow(scan)
        kwargs = {"inputs": self.get_inputs(scan), "outputs": [{"all": False}]}
        if scan.scan_info.get("save"):
            kwargs["convert_destination"] = workflow_destination(scan)

        future = submit(args=(workflow,), kwargs=kwargs, queue="celery")

        if self._plotter:
            scan_nb = scan.scan_info.get("scan_nb")
            self._plotter.handle_workflow_result(
                future,
                self.detector,
                scan_name=f"{scan.name}: {scan_nb}.1 {scan.name}",
                output_url=(
                    # TODO: Do not hard-code the output url
                    f"{master_output_filename(scan)}::/{scan_nb}.1/integrate/integrated"
                    if scan.scan_info.get("save")
                    else None
                ),
            )

    def _get_txs_task_identifier(self, scan: BlissScanType):
        if scan.scan_info.get("save"):
            return "ewokstxs.tasks.txs.TxsTask"
        return "ewokstxs.tasks.txs.TxsTaskWithoutSaving"

    def get_workflow(self, scan: BlissScanType):
        return {
            "graph": {"id": "txs"},
            "nodes": [
                {
                    "id": "txs_task",
                    "task_type": "class",
                    "task_identifier": self._get_txs_task_identifier(scan),
                }
            ],
        }

    def scan_requires_processing(self, scan: BlissScanType) -> bool:
        return f"{self.detector}:image" in scan.scan_info.get("channels", dict())

    def get_inputs(self, scan: BlissScanType) -> List[dict]:
        if self.energy == "automatic":
            energy = get_xray_energy()
        else:
            energy = self.energy

        return task_inputs(
            task_identifier=self._get_txs_task_identifier(scan),
            inputs={
                "scan_key": scan._scan_data.key,
                "filename": get_filename(scan),
                "scan": scan.scan_info.get("scan_nb"),
                "energy": energy,
                "distance": self.distance,
                "center": self.center,
                "detector": self.detector,
                "pixel": self.pixel,
                "binning": (self.binning, self.binning),
                "output_filename": master_output_filename(scan),
                "integrate1d_options": self.integrate1d_options.to_dict(),
            },
        )

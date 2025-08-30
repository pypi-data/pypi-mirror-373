from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

import numpy


@dataclass
class XasPlotData:
    name: str
    x: numpy.ndarray
    y: numpy.ndarray
    xlabel: str
    ylabel: str
    info: Dict[str, Any]
    hlines: Sequence[float]
    vlines: Sequence[float]


@dataclass
class XasSubscanData:
    mu: Optional[XasPlotData] = None
    chi: Optional[XasPlotData] = None
    ft: Optional[XasPlotData] = None
    noise: Optional[XasPlotData] = None


@dataclass
class SubScanInfo:
    legend: str
    color: Tuple[int, int, int]
    enabled: bool = True
    updated: bool = False


@dataclass
class ScanInfo:
    filename: str
    scan_number: int
    subscans: List[SubScanInfo]
    xas_results: List[XasSubscanData]
    plot_future: Optional[Any] = None
    split_future: Optional[Any] = None
    reprocess_all: bool = False
    multi_xas_scan: bool = False
    multi_xas_subscan_size: int = 0

    @property
    def scan_url(self) -> str:
        return f"silx://{self.filename}::/{self.scan_number}.1"

    @property
    def min_subscan_index_to_process(self) -> int:
        if not self.multi_xas_scan or self.reprocess_all or not self.xas_results:
            return 0
        return len(self.xas_results) - 1

    @property
    def job_id(self) -> Optional[str]:
        if self.future is None:
            return
        return self.future.uuid


@dataclass
class ExafsPlotWorkflowParameters:
    workflow: str
    energy_name: str
    energy_unit: str
    mu_name: str
    trim_n_points: int = 0


@dataclass
class ExafsSplitWorkflowParameters:
    workflow: dict
    monotonic_channel: str
    scan_complete: bool
    trim_n_points: int = 0

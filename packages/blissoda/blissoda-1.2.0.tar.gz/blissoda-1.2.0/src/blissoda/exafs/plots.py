"""Bliss-side client for Flint EXAFS plots"""

from typing import List
from typing import Optional
from typing import Tuple

from ..flint import BasePlot
from .types import XasSubscanData


class ExafsPlot(BasePlot):
    WIDGET = "blissoda.exafs.widgets.ExafsWidget"

    def clear(self) -> None:
        self.submit("clear")

    def remove_scan(self, legend: str) -> None:
        self.submit("remove_scan", legend)

    def update_scan(
        self,
        legend: str,
        data: XasSubscanData,
        color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        self.submit("update_scan", legend, data, color=color)

    def get_scans(self) -> List[str]:
        return self.submit("get_scans")

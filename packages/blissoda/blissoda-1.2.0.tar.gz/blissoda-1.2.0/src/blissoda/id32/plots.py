"""Bliss-side for Flint ID32 plots"""

from ..flint import BasePlot


class SpecGenPlot(BasePlot):
    WIDGET = "blissoda.id32.widgets.SpecGenPlotWidget"

    def update_plot(
        self, outputfile_sum: str, scan_number: int, max_scans: int
    ) -> None:
        # print(f"{outputfile_sum=}, {scan_number=}, {max_scans=}")
        self.submit("update_plot", outputfile_sum, scan_number, max_scans)

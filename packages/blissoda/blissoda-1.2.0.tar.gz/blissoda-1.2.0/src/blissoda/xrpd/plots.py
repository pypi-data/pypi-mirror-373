"""Bliss-side for Flint XRPD plots"""

from ..flint import BasePlot


class _XrpdBasePlot(BasePlot):
    def remove_plot(self, plot_key: str) -> None:
        self.submit("remove_plot", plot_key)

    def update_plot(self, plot_key: str, hdf5_options: dict) -> None:
        self.submit("update_plot", plot_key, hdf5_options)


class XrpdCurvePlot(_XrpdBasePlot):
    WIDGET = "blissoda.xrpd.widgets.XrpdCurveWidget"


class XrpdImagePlot(_XrpdBasePlot):
    WIDGET = "blissoda.xrpd.widgets.XrpdImageWidget"


class Xrpd2dIntegrationPlot(_XrpdBasePlot):
    WIDGET = "blissoda.xrpd.widgets.Xrpd2dIntegrationWidget"

"""Bliss-side for Flint ID24 plots"""

from ..flint import BasePlot


class TemperaturePlot(BasePlot):
    WIDGET = "blissoda.id24.widgets.TemperatureWidget"

    def select_directory(self, directory: str) -> None:
        print("select_directory", directory)
        self.submit("select_directory", directory)

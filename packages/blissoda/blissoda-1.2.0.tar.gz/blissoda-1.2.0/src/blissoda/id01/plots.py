import h5py
import silx.io
from silx.gui.plot import Plot1D
from silx.io.utils import h5py_read_dataset as read_dataset

from ..flint import BasePlot
from ..flint import capture_errors


class BlissIntensityPlots(BasePlot):
    WIDGET = "blissoda.id01.plots.IntensityPlots"

    def clear_data(self):
        self.submit("clear")

    def set_data(self, output_url: str):
        self.submit("set_data", output_url)


class IntensityPlots(Plot1D):
    @capture_errors
    def set_data(self, output_url: str) -> None:
        with silx.io.open(output_url) as entry:
            process = entry["cdi_fits"]
            x0 = process["offset_fit/y"]
            parameters = process["parameters"]
            assert isinstance(parameters, h5py.Group)
            x_label: str = read_dataset(parameters["axis_name"])
            y_label: str = read_dataset(parameters["counter"])
            norm = read_dataset(parameters["norm"]) if "norm" in parameters else None

            for i, nxdata in enumerate(process["intensity_fits"].values()):
                signal = nxdata[nxdata.attrs["signal"]]
                label = signal.attrs["long_name"]
                x = nxdata[nxdata.attrs["axes"][0]]
                fit = nxdata[nxdata.attrs["auxiliary_signals"][0]]

                self.addCurve(x[()], signal[()], legend=f"{label} - {i}")
                self.addCurve(
                    x[()],
                    fit[()],
                    legend=f"fit - {label} - {i}",
                    color="r",
                    linestyle="--",
                )
                self.addCurve(
                    [x0[i], x0[i]], [signal[()].min(), signal[()].max()], legend=str(i)
                )
        self.setGraphXLabel(x_label)
        self.setGraphYLabel(y_label)
        self.setYAxisLogarithmic(norm == "log")


class BlissOffsetPlot(BasePlot):
    WIDGET = "blissoda.id01.plots.OffsetPlot"

    def clear_data(self):
        self.submit("clear")

    def set_data(self, output_url: str):
        self.submit("set_data", output_url)


class OffsetPlot(Plot1D):
    @capture_errors
    def set_data(self, output_url: str) -> None:
        with silx.io.open(output_url) as entry:
            nxdata = entry["cdi_fits/offset_fit"]
            signal = nxdata[nxdata.attrs["signal"]]
            x = nxdata[nxdata.attrs["axes"][0]]
            fit = nxdata[nxdata.attrs["auxiliary_signals"][0]]
            self.addCurve(x[()], signal[()], symbol="o", legend="original data")
            self.addCurve(x[()], fit[()], color="r", legend="fitted line")

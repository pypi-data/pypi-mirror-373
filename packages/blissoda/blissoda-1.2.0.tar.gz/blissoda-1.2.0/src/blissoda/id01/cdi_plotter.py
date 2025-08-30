from ewoksjob.client import Future

from ..flint.plotter import BasePlotter
from .plots import BlissIntensityPlots
from .plots import BlissOffsetPlot


class CdiPlotter(BasePlotter):

    def handle_workflow_result(
        self, future: Future, retry_timeout: int, retry_period: int
    ):
        self._spawn(self._handle_workflow_result, future, retry_timeout, retry_period)

    def _handle_workflow_result(
        self, future: Future, retry_timeout: int, retry_period: int
    ):
        result = future.result(timeout=retry_timeout, interval=retry_period)

        output_url = result["saved_hdf5"]

        self._get_plot("IntensityPlots", BlissIntensityPlots).set_data(output_url)
        self._get_plot("OffsetPlot", BlissOffsetPlot).set_data(output_url)

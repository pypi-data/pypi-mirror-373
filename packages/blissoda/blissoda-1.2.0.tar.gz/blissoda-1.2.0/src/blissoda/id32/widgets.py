"""Flint-side for Flint RIXS plots"""

import logging
import os

from silx.gui.plot import Plot1D
from silx.io.specfile import SpecFile

from ..flint import capture_errors

logger = logging.getLogger(__name__)


class SpecGenPlotWidget(Plot1D):

    @capture_errors
    def update_plot(
        self, outputfile_sum: str, scan_number: int, max_scans: int
    ) -> None:

        plot_x = "Pixel"
        plot_y = "SPC"

        file_exists = os.path.exists(outputfile_sum)
        logger.info(
            "Update RIXS scan %s (file=%s,file exists=%s)",
            scan_number,
            outputfile_sum,
            file_exists,
        )
        if not file_exists:
            return

        sf = SpecFile(outputfile_sum)
        keys = sf.keys()

        scan_number = int(scan_number)
        my_key = "%d" % scan_number + ".1"

        if my_key not in keys:
            logger.info("Scan %s not found in %s", my_key, outputfile_sum)
            return

        logger.info("%d", keys.index(my_key))
        x = sf[my_key].data_column_by_name(plot_x)
        y = sf[my_key].data_column_by_name(plot_y)
        title = sf.command(keys.index(my_key))
        sf.close()

        legend = str(scan_number)

        self.addCurve(x, y, legend=legend, xlabel=plot_x, ylabel=plot_y)
        self.setActiveCurve(legend)
        self.setGraphTitle(title)

        curves = self.getItems()
        del_items = curves[: max(0, len(curves) - max_scans)]
        for item in del_items:
            self.remove(item)

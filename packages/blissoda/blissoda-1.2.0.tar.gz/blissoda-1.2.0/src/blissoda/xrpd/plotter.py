from __future__ import annotations

import functools
import logging
import time
from typing import Dict
from typing import Optional
from typing import Tuple

import numpy
from silx.utils.retry import RetryTimeoutError

from ..bliss_globals import current_session
from ..flint.plotter import BasePlotter
from .data import XrpdNXDataInfo
from .data import create_plot_info
from .data import delete_old_entries
from .data import delete_plot_info
from .data import get_plots
from .data import get_plots_to_remove
from .data import get_xrpd_nxdata_info
from .models import XrpdFieldName
from .models import XrpdPlotInfo
from .plots import Xrpd2dIntegrationPlot
from .plots import XrpdCurvePlot
from .plots import XrpdImagePlot
from .utils import axis_label

logger = logging.getLogger(__name__)


def _background_task(method):
    @functools.wraps(method)
    def wrapper(*args, **kw):
        try:
            return method(*args, **kw)
        except Exception as e:
            logging.error("XRPD plotter task failed (%s)", e, exc_info=True)
            raise

    return wrapper


class XrpdPlotter(BasePlotter):
    def __init__(self, number_of_scans: int = 0) -> None:
        super().__init__(number_of_scans)
        if self._HAS_BLISS:
            nb_removed_entries = delete_old_entries(current_session)
            if nb_removed_entries:
                logging.info(f"Removed {nb_removed_entries} old entries from Redis")

    def handle_workflow_result(
        self,
        future,
        lima_name: str,
        scan_name: str,
        output_url: Optional[str] = None,
        retry_timeout: int = 60,
        retry_period: int = 1,
    ):
        """Handle workflow results in a background task"""
        if output_url:
            func = self._handle_workflow_result_from_file
        else:
            func = self._handle_workflow_result_from_memory
        self._spawn(
            func,
            future,
            scan_name,
            lima_name,
            output_url=output_url,
            retry_timeout=retry_timeout,
            retry_period=retry_period,
        )

    def replot(self, **retry_options) -> None:
        """Re-draw all plots."""
        for plot_info in get_plots():
            self._spawn(self._update_plot, plot_info, retry_options)

    def clear(self):
        """Clear all plots."""
        plot_infos = get_plots()
        for plot_info in plot_infos:
            self._remove_plot(plot_info)

    @_background_task
    def _handle_workflow_result_from_memory(
        self,
        future,
        scan_name: str,
        lima_name: str,
        retry_timeout: Optional[int] = 600,
        **retry_options,
    ) -> None:
        retry_period = retry_options.get("retry_period")
        result = future.result(timeout=retry_timeout, interval=retry_period)

        if result["radial_units"] is None:
            return

        radial_name, radial_unit = result["radial_units"].split("_")
        radial_label = axis_label(radial_name, radial_unit)

        plot_data: Dict[XrpdFieldName, numpy.ndarray] = {
            "radial": result["radial"],
            "intensity": result["intensity"],
        }

        if result.get("azimuthal") is not None:
            plot_data["azimuthal"] = result["azimuthal"]
            azim_name, azim_unit = result["azimuthal_units"].split("_")
            azim_label = axis_label(azim_name, azim_unit)
        else:
            azim_label = None

        plot_info = create_plot_info(
            scan_name,
            lima_name,
            radial_label=radial_label,
            azim_label=azim_label,
            plot_data=plot_data,
        )

        self._remove_old_plots()
        self._update_plot(plot_info, retry_options)

    @_background_task
    def _handle_workflow_result_from_file(
        self,
        future,
        scan_name: str,
        lima_name: str,
        output_url: str,
        **retry_options,
    ) -> None:
        retry_period = retry_options.get("retry_period")

        nxdata_info = self._load_nxdata_info(future, output_url, retry_period)
        if nxdata_info is None:
            return

        plot_info = create_plot_info(
            scan_name,
            lima_name,
            nxdata_info.radial_label,
            nxdata_info.azim_label,
            plot_data=nxdata_info.plot_data,
            hdf5_url=nxdata_info.intensity_url,
        )
        self._remove_old_plots()

        while not future.done():
            self._update_plot(plot_info, retry_options)
            if retry_period:
                time.sleep(retry_period)
        self._update_plot(plot_info, retry_options)

    def _load_nxdata_info(
        self,
        future,
        nxdata_url: str,
        retry_period: float,
    ) -> Optional[XrpdNXDataInfo]:
        """Try to read from nxdata_url until the future is ready"""
        while not future.done():
            try:
                return get_xrpd_nxdata_info(
                    nxdata_url,
                    # Use retry_period as a short timeout to check the future
                    retry_timeout=retry_period,
                    retry_period=retry_period,
                )
            except RetryTimeoutError:
                pass

        if future.exception():
            return None

        # Give it a last chance for 10 seconds
        try:
            return get_xrpd_nxdata_info(
                nxdata_url,
                retry_timeout=10,
                retry_period=retry_period,
            )
        except RetryTimeoutError:
            return None

    def _update_plot(self, plot_info: XrpdPlotInfo, retry_options: dict) -> None:
        for widget in self._get_plot_widgets(plot_info):
            widget.update_plot(plot_info.pk, retry_options)

    def _remove_plot(self, plot_info: XrpdPlotInfo) -> None:
        for widget in self._get_plot_widgets(plot_info):
            widget.remove_plot(plot_info.pk)
        delete_plot_info(plot_info)

    def _remove_old_plots(self):
        plot_infos = get_plots_to_remove(self._max_plots)
        for plot_info in plot_infos:
            self._remove_plot(plot_info)

    def _get_plot_widgets(
        self, plot_info: XrpdPlotInfo
    ) -> Tuple[Xrpd2dIntegrationPlot] | Tuple[XrpdCurvePlot, XrpdImagePlot]:
        if "azimuthal" in plot_info.field_names:
            twoD_plot = super()._get_plot(
                f"2D Integrated {plot_info.lima_name} (last)", Xrpd2dIntegrationPlot
            )
            return (twoD_plot,)

        image_plot = super()._get_plot(
            f"Integrated {plot_info.lima_name}", XrpdImagePlot
        )
        curve_plot = super()._get_plot("Integrated (Last)", XrpdCurvePlot)

        return (curve_plot, image_plot)

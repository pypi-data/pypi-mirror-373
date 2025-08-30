from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any
from typing import Optional
from typing import Tuple

import numpy

from ..flint import capture_errors
from ..flint.plotter import BasePlotter
from ..import_utils import unavailable_class

try:
    from flint.viewers.custom_image.client import ImageView
except ImportError as ex:
    ImageView = unavailable_class(ex)

_logger = logging.getLogger(__name__)


class SingleSliceImshow(BasePlotter):
    """
    Manage a Flint window showing the most recent reconstructed slice with enhanced controls,
    using the flint DataPlot–based ImageView.
    """

    TITLE = "Last Reconstructed Slice"

    def __init__(self, history: int = 1) -> None:
        super().__init__(max_plots=history)
        self._cache: OrderedDict[str, numpy.ndarray] = OrderedDict()

    def handle_workflow_result(self, future: Any) -> None:
        """
        Called by BasePlotter._spawn when the workflow future completes.
        Handles both success and failure with logging.
        """
        result = self._extract_result(future)
        if not result:
            return

        img = result.get("reconstructed_slice_array")
        if img is None:
            _logger.warning(
                "No 'reconstructed_slice_array' in workflow result: %r", result
            )
            return

        self.set_image(numpy.squeeze(img))

    def _extract_result(self, future: Any) -> Optional[dict]:
        """
        Safely retrieve result from a future via result() or get().
        Logs warnings or errors and returns None on failure.
        """
        try:
            res_fn = getattr(future, "result", None) or getattr(future, "get", None)
            if not callable(res_fn):
                _logger.warning("Future has no callable result()/get(): %r", future)
                return None
            result = res_fn()
            if isinstance(result, dict) or result is None:
                return result
            _logger.warning("Future result is not a dict or None: %r", result)
            return None
        except Exception as e:
            _logger.error("Workflow execution failed: %s", e, exc_info=True)
            return None

    @capture_errors
    def set_image(self, image: numpy.ndarray) -> None:
        """
        Display a new image with physical axis limits based on pixel size and image center.
        """
        widget = self._get_plot(self.TITLE, ImageView)
        self._set_title(widget)

        x_axis, y_axis = self._compute_axes(image)
        origin = (float(x_axis[0]), float(y_axis[0]))

        dx = float(x_axis[1] - x_axis[0]) if len(x_axis) > 1 else 1.0
        dy = float(y_axis[1] - y_axis[0]) if len(y_axis) > 1 else 1.0
        scale = (dx, dy)

        widget.set_data(image, origin=origin, scale=scale)
        self._apply_labels(widget)

        self._cache[self.TITLE] = image
        self.purge_tasks()
        self._purge()

    def _set_title(self, widget: ImageView) -> None:
        """
        Set the plot window title using the current data filename from scan saving.
        """
        try:
            from bliss.setup_globals import SCAN_SAVING as scan_saving

            widget.title = scan_saving.data_filename
        except Exception as e:
            _logger.warning("Failed to set widget title: %s", e)

    def _compute_axes(
        self, image: numpy.ndarray
    ) -> Tuple[numpy.ndarray, numpy.ndarray]:
        """
        Compute physical axes from sample config; fallback to pixel indices.
        Converts pixel_size (um) to axis units defined by cfg.sample_x_axis.unit and cfg.sample_y_axis.unit.
        """
        try:
            from tomo.globals import get_active_tomo_config

            cfg = get_active_tomo_config()
            pixel_size_um = cfg.detectors.active_detector.sample_pixel_size

            # Determine units for x and y axes
            unit_x = getattr(cfg.sample_x_axis, "unit", "mm")
            unit_y = getattr(cfg.sample_y_axis, "unit", "mm")
            # Conversion factors from micrometers to axis units
            conv = {"um": 1.0, "mm": 1e-3}
            if unit_x not in conv:
                _logger.warning(
                    "Unknown unit '%s' for sample_x_axis, assuming 'mm'", unit_x
                )
            if unit_y not in conv:
                _logger.warning(
                    "Unknown unit '%s' for sample_y_axis, assuming 'mm'", unit_y
                )
            # Convert pixel size to axis units
            ps_x = pixel_size_um * conv.get(unit_x, 0.001)  # Default to mm if unknown
            ps_y = pixel_size_um * conv.get(unit_y, 0.001)  # Default to mm if unknown

            rows, cols = image.shape[-2:]
            # Center positions are already in axis units
            cx = cfg.sample_x_axis.position
            cy = cfg.sample_y_axis.position

            half_w = (cols * ps_x) / 2
            half_h = (rows * ps_y) / 2

            x_axis = numpy.linspace(cx - half_w, cx + half_w, cols)
            y_axis = numpy.linspace(cy - half_h, cy + half_h, rows)
            return x_axis, y_axis
        except Exception as e:
            _logger.warning("Failed to compute physical axes: %s", e)
            rows, cols = image.shape[-2:]
            return numpy.arange(cols, dtype=float), numpy.arange(rows, dtype=float)

    def _apply_labels(self, widget: ImageView) -> None:
        try:
            from tomo.globals import get_active_tomo_config

            cfg = get_active_tomo_config()
            widget.xlabel = cfg.sample_y.name
            widget.ylabel = cfg.sample_x.name
        except Exception:
            _logger.warning("Failed to set axis labels")

    def _purge(self) -> None:
        """
        Remove oldest images beyond history.
        """
        while len(self._cache) > self._max_plots:
            self._cache.popitem(last=False)

"""Flint widgets for EXAFS plots"""

import logging
from collections import OrderedDict
from functools import wraps
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from silx.gui import qt
from silx.gui.plot import Plot1D
from silx.gui.plot.items.core import ItemChangedType

from ..import_utils import unavailable_class
from .types import XasPlotData
from .types import XasSubscanData

try:
    from pandas import DataFrame
except ImportError as ex:
    DataFrame = unavailable_class(ex)


_logger = logging.getLogger(__name__)


def capture_error(method):
    @wraps(method)
    def wrapper(self, *args, **kw):
        try:
            return method(self, *args, **kw)
        except Exception:
            _logger.critical(f"Error while executing {method}", exc_info=True)

    return wrapper


class ExafsInfoModel(qt.QAbstractTableModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=qt.Qt.DisplayRole):
        if index.isValid():
            if role == qt.Qt.DisplayRole:
                fnr = self._data.iloc[index.row(), index.column()]
                if fnr < 1 or fnr > 10000:
                    return f"{fnr:E}"
                else:
                    return f"{fnr:.02f}"
        return None

    def headerData(self, x, orientation, role):
        if orientation == qt.Qt.Horizontal and role == qt.Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == qt.Qt.Vertical and role == qt.Qt.DisplayRole:
            return self._data.index[x]
        return None


class Plot1DExafs(Plot1D):
    def __init__(self, name: str, parent=None) -> None:
        self._name = name
        self._exafsDockWidget = None
        super().__init__(parent=parent)
        self.sigItemAdded.connect(self.onNewItem)
        self.sigItemRemoved.connect(self.onItemRemoved)
        self.sigActiveCurveChanged.connect(self.onActiveItemChanged)

    @property
    def name(self) -> str:
        return self._name

    def _customControlButtonMenu(self) -> None:
        super()._customControlButtonMenu()
        controlMenu = self.controlButton.menu()
        controlMenu.addAction(self.getExafsStatsAction())

    def getExafsStatsAction(self):
        return self.getExafsStatsWidget().parent().toggleViewAction()

    def getExafsStatsWidget(self):
        if self._exafsDockWidget is None:
            self._exafsDockWidget = qt.QDockWidget(self)
            self._exafsDockWidget.setWindowTitle("EXAFS stats")
            self._exafsDockWidget.layout().setContentsMargins(0, 0, 0, 0)

            statsWidget = qt.QTableView(parent=self._exafsDockWidget)
            self._exafsDockWidget.setWidget(statsWidget)
            self._exafsDockWidget.hide()
            self._exafsDockWidget.toggleViewAction().triggered.connect(
                self._handleDockWidgetViewActionTriggered
            )
            self._exafsDockWidget.visibilityChanged.connect(
                self._handleFirstDockWidgetShow
            )

            self.updateExafsStats()
        return self._exafsDockWidget.widget()

    def updateExafsStats(self) -> None:
        if self._exafsDockWidget is None:
            return
        info = self.parent().get_info(self.name)
        if info is None:
            return
        model = ExafsInfoModel(info)
        self._exafsDockWidget.widget().setModel(model)

    def onNewItem(self, item) -> None:
        item.sigItemChanged.connect(self.syncScanChanged)
        self.updateExafsStats()

    def onItemRemoved(self, item) -> None:
        self.updateExafsStats()
        self.syncScans()

    def onActiveItemChanged(self, previous_legend, new_legend) -> None:
        self.parent()._sync_active_scan(self.name)

    def syncScans(self) -> None:
        self.parent()._sync_scans(self.name)

    def syncScanChanged(self, ctype) -> None:
        if ctype == ItemChangedType.VISIBLE:
            self.parent()._sync_scan_visiblity(self.name)

    def addScan(
        self,
        legend: str,
        plot_data: XasPlotData,
        color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        legends = self.getScans()
        if not legends:
            self.setGraphXLabel(label=plot_data.xlabel)
            self.setGraphYLabel(label=plot_data.ylabel)

        info = OrderedDict()
        info["_Index"] = legend
        if plot_data.info:
            info.update(plot_data.info)

        self.addCurve(
            plot_data.x,
            plot_data.y,
            legend=legend,
            color=color,
            linestyle="-",
            info=info,
        )

        hlines = plot_data.hlines
        if hlines:
            x = [min(plot_data.x), max(plot_data.x)]
            hcolor = color
            for i, hvalue in enumerate(hlines, 1):
                y = [hvalue, hvalue]
                hlegend = f"_{legend} (HLINE{i})"
                self.addCurve(x, y, legend=hlegend, color=hcolor, linestyle="--")

        vlines = plot_data.vlines
        if vlines:
            y = [min(plot_data.y), max(plot_data.y)]
            vcolor = "black"
            for i, value in enumerate(vlines, 1):
                x = [value, value]
                vlegend = f"_{legend} (VLINE{i})"
                self.addCurve(x, y, legend=vlegend, color=vcolor, linestyle="--")

        self.updateExafsStats()

    def removeScan(self, legend: str) -> None:
        for legend in self._get_associated_curves(legend):
            self.remove(legend=legend, kind="curve")

    def _get_associated_curves(self, legend) -> Set[str]:
        curves = set()
        for item in self.getItems():
            name = item.getName()
            if legend in name:
                curves.add(name)
        return curves

    def iterScanItems(self) -> Generator:
        for item in self.getItems():
            if item.getName().startswith("_"):
                continue
            yield item

    def getScans(self) -> List[str]:
        return sorted(item.getName() for item in self.iterScanItems())

    def getScanVisibility(self) -> Dict[str, bool]:
        return {item.getName(): item.isVisible() for item in self.iterScanItems()}

    def setScanVisibility(self, visibility: Dict[str, bool]) -> None:
        for legend, value in visibility.items():
            for legend in self._get_associated_curves(legend):
                item = self.getCurve(legend)
                if value != item.isVisible():
                    item.setVisible(value)


class ExafsWidget(qt.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.__plots = {
            "mu": Plot1DExafs("mu", parent=self),
            "chi": Plot1DExafs("chi", parent=self),
            "ft": Plot1DExafs("ft", parent=self),
            "noise": Plot1DExafs("noise", parent=self),
        }
        self._metadata = dict()

        layout = qt.QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        layout.addWidget(self.__plots["mu"], 0, 0, 1, 1)
        layout.addWidget(self.__plots["chi"], 0, 1, 1, 1)
        layout.addWidget(self.__plots["ft"], 1, 0, 1, 1)
        layout.addWidget(self.__plots["noise"], 1, 1, 1, 1)

    @capture_error
    def clear(self) -> None:
        for plot in self.__plots.values():
            plot.clear()

    @capture_error
    def update_scan(
        self,
        legend: str,
        data: XasSubscanData,
        color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        for plot_name, plot in self.__plots.items():
            plot_data = getattr(data, plot_name, None)
            if plot_data is not None:
                plot.addScan(legend, plot_data, color=color)

    @capture_error
    def remove_scan(self, legend: str) -> None:
        for plot in self.__plots.values():
            plot.removeScan(legend)

    def _sync_scans(self, ref_plot_name: str) -> None:
        ref_scans = set(self.get_scans(ref_plot_name))
        for plot_name, plot in self.__plots.items():
            scans = self.get_scans(plot_name)
            for legend in set(scans) - ref_scans:
                plot.removeScan(legend)

    def _sync_scan_visiblity(self, ref_plot_name: str) -> None:
        ref_values = self.__plots[ref_plot_name].getScanVisibility()
        for plot in self.__plots.values():
            plot.setScanVisibility(ref_values)

    def _sync_active_scan(self, ref_plot_name: str) -> None:
        activate_scan = self.__plots[ref_plot_name].getActiveCurve(just_legend=True)
        for plot in self.__plots.values():
            if plot.getActiveCurve(just_legend=True) != activate_scan:
                plot.setActiveCurve(activate_scan)

    @capture_error
    def get_scans(self, plot_name: str = "mu") -> List[str]:
        return self.__plots[plot_name].getScans()

    def get_info(self, plot_name: str) -> Optional[DataFrame]:
        all_info = list()
        for item in self.__plots[plot_name].getItems():
            info = item.getInfo()
            if info:
                all_info.append(info)
        if all_info:
            pd = DataFrame(all_info)
            pd.set_index("_Index", inplace=True, drop=True)
            return pd


if __name__ == "__main__":
    import logging

    # logging.basicConfig(level=logging.DEBUG)

    app = qt.QApplication([])
    plot = ExafsWidget()
    plot.show()
    data = {
        "mu": {
            "x": [0, 1, 2],
            "y": [0, -1, 0],
            "info": {"a": 1, "b": 2},
            "xlabel": "x",
            "ylabel": "y",
            "hlines": [1, 0.8],
            "vlines": [1],
        },
        "chi": {
            "x": [0, 1, 2],
            "y": [0, 2, 0],
            "info": {"a": 3, "b": 4},
            "xlabel": "x",
            "ylabel": "y",
        },
    }
    plot.update_scan("1.1", data)
    data = {
        "mu": {
            "x": [0, 1, 2],
            "y": [0, 1, 0],
            "info": {"a": 5, "b": 6},
            "xlabel": "x",
            "ylabel": "y",
        },
        "chi": {
            "x": [0, 1, 2],
            "y": [1, 0, 1],
            "info": {"a": 7, "b": 8},
            "xlabel": "x",
            "ylabel": "y",
        },
    }
    plot.update_scan("2.1", data)
    app.exec()

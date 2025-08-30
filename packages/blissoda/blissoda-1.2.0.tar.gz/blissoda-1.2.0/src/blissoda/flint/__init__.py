import logging
from functools import wraps
from importlib.metadata import version
from typing import Callable
from typing import Type

from packaging.version import Version

from ..bliss_globals import current_session
from ..import_utils import is_available
from ..import_utils import unavailable_class
from ..import_utils import unavailable_function

try:
    from gevent.lock import RLock
except ImportError as ex:
    RLock = unavailable_class(ex)

try:
    from bliss.common.plot import get_flint
except ImportError as ex:
    get_flint = unavailable_function(ex)

try:
    if Version(version("bliss")) >= Version("2.2"):
        from flint.client.plots import BasePlot
        from flint.client.proxy import FlintClient
    else:
        from bliss.flint.client.plots import BasePlot
        from bliss.flint.client.proxy import FlintClient
except ImportError as ex:
    FlintClient = unavailable_class(ex)
    BasePlot = unavailable_class(ex)


logger = logging.getLogger(__name__)


class WithFlintAccess:
    _HAS_BLISS = is_available(current_session)

    def __init__(self) -> None:
        self._client = None
        self.__clientlock = None
        self._plots = dict()

    @property
    def _clientlock(self) -> RLock:
        if self.__clientlock is None:
            self.__clientlock = RLock()
        return self.__clientlock

    def _get_plot(self, plot_id: str, plot_cls: Type[BasePlot]) -> BasePlot:
        """Launches Flint and creates the plot when either is missing"""
        plot = self._plots.get(plot_id)
        if plot is None:
            plot = self._flint_client.get_plot(plot_cls, unique_name=plot_id)
            self._plots["plot_id"] = plot
        return plot

    @property
    def _flint_client(self) -> FlintClient:
        """Launches Flint when missing"""
        with self._clientlock:
            try:
                if self._client.is_available():
                    return self._client
            except (FileNotFoundError, AttributeError):
                pass
            self._client = get_flint()
            self._plots = dict()
            return self._client


def capture_errors(method) -> Callable:
    @wraps(method)
    def wrapper(*args, **kw):
        try:
            return method(*args, **kw)
        except Exception as e:
            msg = f"Flint plot error: {e}"
            logger.error(msg, exc_info=True)

    return wrapper

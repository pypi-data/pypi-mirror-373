from ewoksjob.client import Future

from ..bliss_globals import current_session
from ..import_utils import unavailable_module

try:
    import gevent
except ImportError as ex:
    gevent = unavailable_module(ex)


def send_figures_to_elogbook(future: Future, retry_timeout: int, retry_period: int):
    result = future.result(timeout=retry_timeout, interval=retry_period)

    saved_figs = result.get("saved_figs", None)
    if saved_figs is None:
        return

    icat_client = current_session.scan_saving.icat_client
    for saved_fig in saved_figs:
        icat_client.send_binary_file(saved_fig)


class CdiUploader:
    def __init__(self) -> None:
        super().__init__()
        self._tasks = []

    def upload_workflow_result(
        self, future: Future, retry_timeout: int, retry_period: int
    ):
        task = gevent.spawn(
            send_figures_to_elogbook, future, retry_timeout, retry_period
        )
        self._tasks.append(task)
        self.purge_tasks()

    def purge_tasks(self) -> int:
        """Remove references to tasks that have finished."""
        self._tasks = [t for t in self._tasks if t]
        return len(self._tasks)

    def kill_tasks(self) -> int:
        """Kill all tasks."""
        gevent.killall(self._tasks)
        return self.purge_tasks()

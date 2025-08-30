import json
import logging
from importlib.metadata import version
from typing import Mapping
from typing import Optional

from packaging.version import Version

# Note: import subscriber first because it might require patching
_BLISSDATA_VERSION = Version(version("blissdata"))

# bliss 1.11 -> blissdata 0.3.x
# bliss 2.0  -> blissdata 1.0.x
# bliss 2.1  -> blissdata 1.1.x
# master     -> blissdata 2.0.x

if _BLISSDATA_VERSION >= Version("2.0.0rc1"):
    from .subscriberv2 import scan_iterator
elif _BLISSDATA_VERSION >= Version("1"):
    from .subscriberv1 import scan_iterator
else:
    from .subscriberv0 import scan_iterator

from ewoksjob.client import submit  # noqa E402

logger = logging.getLogger(__name__)


def submit_scan_workflow(workflow=None, **kwargs) -> Optional[str]:
    if not workflow:
        return
    future = submit(args=(workflow,), kwargs=kwargs)
    return future.uuid


def main(args) -> None:
    for filename, scan_nb, workflows in scan_iterator(args.session):
        for wfname, nxprocess in workflows.items():
            if not isinstance(nxprocess, Mapping):
                continue
            try:
                job_id = submit_scan_workflow(
                    **json.loads(nxprocess["configuration"]["data"])
                )
            except Exception:
                logger.exception(
                    f"Error when submitting workflow '{wfname}' for scan {scan_nb} of file '{filename}'"
                )
            else:
                if job_id is not None:
                    logger.info(
                        f"Submitted workflow '{wfname}' (JOB ID {job_id}) for scan {scan_nb} of file '{filename}'"
                    )

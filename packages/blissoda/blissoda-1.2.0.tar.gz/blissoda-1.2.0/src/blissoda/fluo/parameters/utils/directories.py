import getpass
import os
import shutil
from typing import Optional

from ....resources import resource_path
from . import defaults


def raw_directory(session: str, sample: str, dataset: str, demo: bool = False) -> str:
    path = normalize_path(
        session, "RAW_DATA", sample, f"{sample}_{dataset}", f"{sample}_{dataset}.h5"
    )
    if demo and path.startswith(defaults.REAL_DATA_ROOT):
        demo_path = path.replace(defaults.REAL_DATA_ROOT, defaults.DEMO_DATA_ROOT)
        if os.path.exists(demo_path):
            path = demo_path
    return path


def pymca_config_path(session: str, name: str, demo: bool = False) -> str:
    if os.path.isabs(name):
        return name
    path = normalize_path(session, "SCRIPTS")
    if demo and path.startswith(defaults.REAL_DATA_ROOT):
        demo_path = path.replace(defaults.REAL_DATA_ROOT, defaults.DEMO_DATA_ROOT)
        if os.path.exists(demo_path):
            path = demo_path
    return os.path.join(path, "pymca", name)


def processed_path(
    session: str,
    sample: str,
    dataset: str,
    dirname: Optional[str],
    outname: str,
    demo: bool = False,
) -> str:
    if dirname is None:
        dirname = defaults.DEFAULT_OUT_DIRNAME
    path = normalize_path(session, "PROCESSED_DATA", dirname, outname)
    return _change_demo_path(session, sample, dataset, path, demo=demo)


def accessible_workflow_path(
    session: str, sample: str, dataset: str, dirname: Optional[str], demo: bool = False
) -> str:
    if dirname is None:
        dirname = defaults.DEFAULT_OUT_DIRNAME
    path = normalize_path(session, "SCRIPTS", dirname, "workflows")
    return _change_demo_path(session, sample, dataset, path, demo=demo)


def ensure_workflow_exists(path: str) -> None:
    if os.path.exists(path):
        return
    workflow_basename = os.path.basename(path)
    with resource_path("fluo", workflow_basename) as src_path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        shutil.copyfile(src_path, path)


def _change_demo_path(
    session: str, sample: str, dataset: str, path: str, demo: bool = False
) -> str:
    raw_path = raw_directory(session, sample, dataset, demo=demo)
    if not demo or not raw_path.startswith(defaults.DEMO_DATA_ROOT):
        return path

    job_id = os.environ.get("SLURM_JOBID")
    if job_id:
        out_root = f"/tmp_14_days/{getpass.getuser()}/ewoksdemo/slurm_job_{job_id}"
    else:
        out_root = "/tmp/ewoksdemo"
    return path.replace(defaults.REAL_DATA_ROOT, out_root)


def normalize_path(path: str, *parts) -> str:
    if parts:
        path = os.path.join(path, *parts)
    path = os.path.abspath(path)
    path = path.replace("/mnt/multipath-shares", "")
    return path

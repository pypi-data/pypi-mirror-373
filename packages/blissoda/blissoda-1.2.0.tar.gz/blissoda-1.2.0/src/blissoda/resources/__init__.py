import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

if sys.version_info < (3, 9):
    import importlib_resources
else:
    import importlib.resources as importlib_resources


@contextmanager
def resource_path(*args) -> Generator[Path, None, None]:
    """The resource is specified relative to `blissoda.resources`.

    .. code-block:: python

        with resource_path("exafs", "exafs.ows") a path:
            ...
    """
    source = importlib_resources.files(__name__).joinpath(*args)
    with importlib_resources.as_file(source) as path:
        if not path.is_file():
            raise FileNotFoundError(f"Not a blissoda resource file: '{path}'")
        yield path


def resource_filename(*args) -> str:
    """The resource is specified relative to `blissoda.resources`.

    .. code-block:: python

        filename = resource_filename("exafs", "exafs.ows")
    """
    with resource_path(*args) as path:
        pass
    if not path.exists():
        # resource was extract from zip: copy for persistency
        with resource_path(*args) as path:
            path_copy = Path(tempfile.mkdtemp()) / path.name
            shutil.copyfile(str(path), str(path_copy))
            path = path_copy
    return str(path)


def copy_resource_glob(*args: str, dest_dir: Path = Path(".")) -> None:
    r"""
    Copy all resource files matching the given glob pattern to the destination directory.

    :param args: A glob pattern, e.g. ``('xrpd', '*.json')`` or ``('exafs', '*.ows')``.
    :param dest_dir: The directory where the files will be copied (default: current directory).
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    resources_root = importlib_resources.files(__name__)

    for resource in resources_root.rglob(os.path.join(*args)):
        if resource.is_file():
            with importlib_resources.as_file(resource) as src_path:
                shutil.copy(src_path, dest_dir / src_path.name)

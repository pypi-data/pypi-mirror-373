from importlib.metadata import version

from packaging.version import Version

from ...import_utils import unavailable_class

_BLISSDATA_VERSION = Version(version("blissdata"))

# bliss 1.11 -> blissdata 0.3.x
# bliss 2.0  -> blissdata 1.0.x
# bliss 2.1  -> blissdata 1.1.x
# master     -> blissdata 2.0.x

if _BLISSDATA_VERSION >= Version("1"):
    try:
        import bliss  # noqa F401
    except ImportError as ex:
        PersistentNdArray = unavailable_class(ex)
    else:
        from .ndarrayv1 import PersistentNdArray
else:
    from .ndarrayv0 import PersistentNdArray  # noqa F401

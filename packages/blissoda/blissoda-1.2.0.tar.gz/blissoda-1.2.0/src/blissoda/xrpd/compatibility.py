from importlib.metadata import version

from blissdata.beacon.data import BeaconData
from packaging.version import Version

_BLISSDATA_VERSION = Version(version("blissdata"))

# bliss 1.11 -> blissdata 0.3.x
# bliss 2.0  -> blissdata 1.0.x
# bliss 2.1  -> blissdata 1.1.x
# master     -> blissdata 2.0.x

if _BLISSDATA_VERSION >= Version("1.1"):
    from pydantic import Field  # noqa
else:
    from pydantic.v1 import Field  # noqa


def get_redis_db_url():
    if _BLISSDATA_VERSION >= Version("1.0"):
        return BeaconData().get_redis_db()

    raw_url = BeaconData().get_redis_db()
    _, url = raw_url.split(":")

    if url.endswith("sock"):
        return f"unix://{url}"
    else:
        return f"redis://{url}"

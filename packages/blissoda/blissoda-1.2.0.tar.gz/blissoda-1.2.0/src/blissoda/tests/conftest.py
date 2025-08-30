import os
from collections import namedtuple
from collections.abc import MutableMapping
from contextlib import ExitStack
from copy import deepcopy
from importlib.metadata import version
from typing import Any
from typing import Iterator
from typing import Mapping

import mock
import pytest
from packaging.version import Version

from ..persistent.parameters import WithPersistentParameters

_BLISSDATA_VERSION = Version(version("blissdata"))


def has_redis_server() -> bool:
    # TODO: instead of pytest-redis which needs a real Redis server, use fakeredis?
    with os.popen("redis-server --version") as output:
        return bool(output.read())


MockedBlissInfo = namedtuple("MockedBlissInfo", "beacon_connection")

if has_redis_server():

    @pytest.fixture(scope="session")
    def mock_bliss_session(redis_proc):
        # Ensure we do not connect to a real Beacon host
        os.environ["BEACON_HOST"] = "nonexisting:25000"

        # Skip test when Beacon dependencies are not available
        # TODO: mock to the extend we no longer need bliss as a dependency
        if _BLISSDATA_VERSION >= Version("1"):
            try:
                from bliss.redis.manager import RedisAddress
            except ImportError:
                pytest.skip("requires bliss")
        else:
            from blissdata.redis import RedisAddress

        try:
            from bliss.config.conductor.client import get_default_connection
            from bliss.config.conductor.connection import Connection
        except ImportError:
            pytest.skip("requires bliss")

        redis_url = f"{redis_proc.host}:{redis_proc.port}"

        def _get_redis_url(self):
            """Return the pytest-redis server URL"""
            return RedisAddress.factory(redis_url)

        with ExitStack() as stack:
            # The Beacon connection should connect to the pytest-redis server
            ctx = mock.patch.object(
                Connection, "get_redis_connection_address", _get_redis_url
            )
            stack.enter_context(ctx)
            ctx = mock.patch.object(
                Connection, "get_redis_data_server_connection_address", _get_redis_url
            )
            stack.enter_context(ctx)

            yield MockedBlissInfo(get_default_connection())

else:

    @pytest.fixture(scope="session")
    def mock_bliss_session():
        # redis_proc raises an exception when redis-server is not available
        pytest.skip("requires redis-server")


@pytest.fixture
def mock_bliss(mock_bliss_session):
    yield
    proxy = mock_bliss_session.beacon_connection.get_redis_proxy()
    proxy.flushall()


@pytest.fixture
def mock_persistent():
    remote_dict = MockHashObjSetting()

    def init(self, **defaults) -> None:
        self._parameters = remote_dict
        self._init_parameters(defaults)

    with mock.patch.object(WithPersistentParameters, "__init__", init):
        yield remote_dict


class MockHashObjSetting(MutableMapping):
    def __init__(self) -> None:
        self._adict = dict()
        super().__init__()

    def __repr__(self) -> str:
        return repr(self._adict)

    def get_all(self) -> dict:
        return deepcopy(self._adict)

    def __getitem__(self, key: str) -> Any:
        return self._adict[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if value is None:
            if key in self._adict:
                del self._adict[key]
        else:
            if isinstance(value, Mapping):
                value = deepcopy(value)
            self._adict[key] = value

    def __delitem__(self, key: str) -> None:
        del self._adict[key]

    def __iter__(self) -> Iterator[Any]:
        yield from self._adict

    def __len__(self) -> int:
        return len(self._adict)

import numpy
import pytest

from ..id31 import optimize_exposure
from .mock_id31 import mock_id31
from .mock_id31 import setup_globals


@pytest.fixture
def current_session_mock():
    with mock_id31():
        yield


def test_ct(current_session_mock):
    setup_globals.p3.noise = False
    setup_globals.source.rate = 1e7
    setup_globals.sample.oyield = 0.1
    expected = 1e6

    assert setup_globals.sample.rate == expected
    setup_globals.p3.ct()
    assert setup_globals.p3.proxy.last_image.max() == expected

    setup_globals.att(1)
    assert setup_globals.sample.rate <= expected
    setup_globals.p3.ct()
    fmax = int(setup_globals.sample.rate + 0.5)
    assert setup_globals.p3.proxy.last_image.max() == fmax

    setup_globals.att(0)
    assert setup_globals.sample.rate == expected
    setup_globals.p3.ct()
    assert setup_globals.p3.proxy.last_image.max() == expected

    setup_globals.source.rate = 5e7 + 25
    with pytest.raises(RuntimeError):
        setup_globals.p3.ct()

    setup_globals.att(1)
    setup_globals.p3.ct()


def test_attenuator_optimization(current_session_mock):
    setup_globals.sample.oyield = 1
    setup_globals.p3.noise = False

    lst = list()
    for default_att_position in range(32):
        sublist = list()
        lst.append(sublist)
        flux = numpy.linspace(1e4, 1e6, 10)
        for fl in flux:
            setup_globals.source.rate = fl
            setup_globals.att(0)
            assert setup_globals.p3.rate == fl
            condition = optimize_exposure.optimize_exposure_condition(
                setup_globals.p3,
                default_att_position=default_att_position,
                desired_counts=1e5,
            )
            setup_globals.ct(condition.expo_time, setup_globals.p3)
            sublist.append(setup_globals.atten.bits)

    for sublist in lst:
        assert sublist == lst[0]

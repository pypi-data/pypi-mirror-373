import numpy

from ..id06.utils import get_positions

PI = numpy.pi


def test_get_positions():
    deg_step = 1
    rad_step = numpy.deg2rad(deg_step)

    pyfai_pos = get_positions(start=0, step=1, npts=360)
    theoretical_pos = numpy.concatenate(
        (
            numpy.arange(-PI / 2 + rad_step / 2, PI + rad_step / 2, rad_step),
            numpy.arange(-PI + rad_step / 2, -PI / 2 + rad_step / 2, rad_step),
        ),
        axis=0,
    )

    assert numpy.all(pyfai_pos - theoretical_pos < 1e-13)

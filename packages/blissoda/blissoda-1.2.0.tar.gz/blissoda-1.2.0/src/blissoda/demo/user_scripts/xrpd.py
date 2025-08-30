from blissoda.bliss_globals import setup_globals
from blissoda.demo.xrpd import xrpd_processor


def xrpd_demo(expo=0.2, npoints=10):
    xrpd_processor.enable(setup_globals.difflab6)
    try:
        pct(
            expo,
            setup_globals.difflab6,
            setup_globals.diode1,
            setup_globals.diode2,
        )
        setup_globals.loopscan(
            npoints,
            expo,
            setup_globals.difflab6,
            setup_globals.diode1,
            setup_globals.diode2,
        )
        xrpd_processor.integration_options["nbpt_azim"] = 360
        pct(
            expo,
            setup_globals.difflab6,
            setup_globals.diode1,
            setup_globals.diode2,
        )
        setup_globals.loopscan(
            npoints,
            expo,
            setup_globals.difflab6,
            setup_globals.diode1,
            setup_globals.diode2,
        )
    finally:
        xrpd_processor.integration_options.pop("nbpt_azim", None)
        xrpd_processor.disable()


def xrpd_demo_get_data():
    xrpd_processor.enable(setup_globals.difflab6)
    try:
        scan = setup_globals.loopscan(
            10,
            0.2,
            setup_globals.difflab6,
            setup_globals.diode1,
            setup_globals.diode2,
        )
    finally:
        xrpd_processor.disable()
    data_keys = xrpd_processor.get_data_keys(scan, "difflab6")
    return data_keys[0], xrpd_processor.get_data(scan, data_keys[0])


def pct(*args, **kw):
    s = setup_globals.ct(*args, **kw)
    xrpd_processor.on_new_scan(s)
    return s

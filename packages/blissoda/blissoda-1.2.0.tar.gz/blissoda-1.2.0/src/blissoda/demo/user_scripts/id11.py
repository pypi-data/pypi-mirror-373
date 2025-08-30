from blissoda.bliss_globals import setup_globals
from blissoda.demo.id11 import id11_xrpd_processor


def id11_pdf_demo(expo=0.2, npoints=10):
    id11_xrpd_processor.enable(setup_globals.difflab6)
    try:
        id11_xrpd_processor.pdf_enable = True
        id11_pct(
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
        id11_xrpd_processor.disable()


def id11_pct(*args, **kw):
    s = setup_globals.ct(*args, **kw)
    return id11_xrpd_processor.on_new_scan(s)

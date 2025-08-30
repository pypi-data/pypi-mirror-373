from blissoda.bliss_globals import setup_globals
from blissoda.demo.id09 import txs_processor


def id09_txs_test(expo=0.2, npoints=10):
    try:
        txs_processor.enable()
        pct(expo)
        setup_globals.loopscan(
            npoints,
            expo,
            setup_globals.difflab6,
            setup_globals.diode1,
            setup_globals.diode2,
        )
    finally:
        txs_processor.disable()


def pct(expo):
    s = setup_globals.ct(
        expo,
        setup_globals.difflab6,
        setup_globals.diode1,
        setup_globals.diode2,
    )
    txs_processor.trigger_workflow_on_new_scan(s)
    return s

import numpy

from blissoda.bliss_globals import setup_globals
from blissoda.demo.id01 import cdi_processor
from blissoda.import_utils import unavailable_class

try:
    from bliss.scanning.scan_sequence import ScanSequence
except ImportError as ex:
    ScanSequence = unavailable_class(ex)


def scan_sequence(
    motObj0,
    motObj1,
    max_dth,
    motObj1_start=-4,
    motObj1_stop=4,
    motObj1_intervals=20,
    no_scans=5,
    exposure=0.1,
):
    # https://bliss.gitlab-pages.esrf.fr/bliss/master/scan_group.html#scan-sequences
    def runner(scan_seq):

        nb_list = []
        startpos = motObj0.position
        for ii in numpy.linspace(-max_dth, max_dth, no_scans):
            setup_globals.umv(motObj0, startpos + ii)
            print(f"[INFO] scanning in {motObj1.name}")
            scaninfo = setup_globals.ascan(
                motObj1,
                motObj1_start,
                motObj1_stop,
                motObj1_intervals,
                exposure,
                run=False,
            )
            scan_seq.add_and_run(scaninfo)
            print(
                f" blissoda.demo.. {scaninfo.scan_info['filename']} blissoda.demo.. scan_no: {scaninfo.scan_info['scan_nb']}"
            )
            nb_list.append(scaninfo.scan_info["scan_nb"])
        setup_globals.umv(motObj0, startpos)

    scan = ScanSequence(
        runner=runner,
        scan_info={
            "run_ewoks": True,
            "axis_name": motObj1.name,
            "rc_axis_name": motObj0.name,
        },
    )
    scan.run()


def id01_ewoks_test():
    try:
        cdi_processor.enable()
        scan_sequence(
            setup_globals.slit_vertical_gap,
            setup_globals.slit_vertical_offset,
            max_dth=1,
        )
    finally:
        cdi_processor.disable()

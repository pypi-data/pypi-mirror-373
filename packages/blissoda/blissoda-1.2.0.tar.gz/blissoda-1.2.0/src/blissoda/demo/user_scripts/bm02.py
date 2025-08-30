from blissoda.bliss_globals import setup_globals
from blissoda.demo.bm02 import bm02_xrpd_processor


def _scan_1d(expo=0.2, npoints=10):
    if "nbpt_azim" in bm02_xrpd_processor.integration_options["difflab6"]:
        bm02_xrpd_processor.integration_options["difflab6"].pop("nbpt_azim")
    return setup_globals.loopscan(npoints, expo, setup_globals.difflab6)


def bm02_demo_1d(expo=0.2, npoints=10, ascii=False):
    bm02_xrpd_processor.enable(setup_globals.difflab6)
    bm02_xrpd_processor.ascii_export_enabled = ascii
    try:
        _scan_1d(expo, npoints)
    finally:
        bm02_xrpd_processor.disable()


def bm02_demo_2d(expo=0.2, npoints=10, ascii=False):
    bm02_xrpd_processor.enable(setup_globals.difflab6)
    try:
        bm02_xrpd_processor.integration_options["difflab6"]["nbpt_azim"] = 100
        bm02_xrpd_processor.ascii_export_enabled = ascii
        setup_globals.loopscan(npoints, expo, setup_globals.difflab6)
    finally:
        bm02_xrpd_processor.disable()


def bm02_demo_1d_with_cell_subtraction(expo=0.2, npoints=10, ascii=False):
    bm02_xrpd_processor.enable(setup_globals.difflab6)
    bm02_xrpd_processor.ascii_export_enabled = ascii

    try:
        # Do a first scan to be subtracted
        scan = _scan_1d(expo, npoints)
        scan_metadata = scan.scan_saving

        bm02_xrpd_processor.enable_empty_cell_subtraction(setup_globals.difflab6)
        bm02_xrpd_processor.set_cell_pattern_url(
            sample=scan_metadata.sample_name,
            dataset=scan_metadata.dataset,
            scan_number=scan.scan_info["scan_nb"],
            detector="difflab6",
        )

        _scan_1d(expo, npoints)
    finally:
        bm02_xrpd_processor.disable()

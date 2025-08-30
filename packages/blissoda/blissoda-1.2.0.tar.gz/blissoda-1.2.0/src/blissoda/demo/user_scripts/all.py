from blissoda.bliss_globals import setup_globals
from blissoda.bm02.xrpd_processor import Bm02XrpdProcessor
from blissoda.bm23.exafs_processor import Bm23ExafsProcessor
from blissoda.demo.user_scripts.bm02 import bm02_demo_1d
from blissoda.demo.user_scripts.bm02 import bm02_demo_2d
from blissoda.demo.user_scripts.bm02 import bm02_xrpd_processor
from blissoda.demo.user_scripts.exafs import exafs_demo
from blissoda.demo.user_scripts.exafs import exafs_processor
from blissoda.demo.user_scripts.id11 import id11_pdf_demo  # noqa F401
from blissoda.demo.user_scripts.id11 import id11_xrpd_processor
from blissoda.demo.user_scripts.id12 import id12_converter
from blissoda.demo.user_scripts.id12 import id12_demo
from blissoda.demo.user_scripts.id14 import id14_converter
from blissoda.demo.user_scripts.id14 import id14_demo
from blissoda.demo.user_scripts.id22 import id22_stscan_demo
from blissoda.demo.user_scripts.id22 import id22_xrpd_demo
from blissoda.demo.user_scripts.id22 import id22_xrpd_processor
from blissoda.demo.user_scripts.id22 import stscan_processor
from blissoda.demo.user_scripts.id31 import id31_xrpd_processor
from blissoda.demo.user_scripts.streamline import streamline_demo
from blissoda.demo.user_scripts.streamline import streamline_scanner
from blissoda.demo.user_scripts.xrpd import xrpd_demo
from blissoda.demo.user_scripts.xrpd import xrpd_demo_get_data
from blissoda.demo.user_scripts.xrpd import xrpd_processor
from blissoda.exafs.processor import ExafsProcessor
from blissoda.id11.xrpd_processor import Id11XrpdProcessor
from blissoda.id12.converter import Id12Hdf5ToAsciiConverter
from blissoda.id14.converter import Id14Hdf5ToSpecConverter
from blissoda.id22.xrpd_processor import Id22XrpdProcessor
from blissoda.id31.streamline_scanner import Id31StreamlineScanner
from blissoda.id31.xrpd_processor import Id31XrpdProcessor
from blissoda.id32.processor import Id32SpecGenProcessor
from blissoda.streamline.scanner import StreamlineScanner
from blissoda.xrpd.processor import XrpdProcessor


def all_print():
    _print_objects(exafs_processor)
    _print_objects(xrpd_processor)
    _print_objects(id11_xrpd_processor)
    _print_objects(id22_xrpd_processor)
    _print_objects(id14_converter)
    _print_objects(id12_converter)
    _print_objects(stscan_processor)
    _print_objects(streamline_scanner)
    _print_objects(bm02_xrpd_processor)
    _print_objects(id31_xrpd_processor)

    _print_objects(XrpdProcessor())
    _print_objects(ExafsProcessor())
    _print_objects(StreamlineScanner())
    _print_objects(Bm23ExafsProcessor())
    _print_objects(Bm02XrpdProcessor())
    _print_objects(Id11XrpdProcessor())
    _print_objects(Id22XrpdProcessor())
    _print_objects(Id31XrpdProcessor())
    _print_objects(Id14Hdf5ToSpecConverter())
    _print_objects(Id12Hdf5ToAsciiConverter())

    _print_objects(Id31StreamlineScanner())

    _print_objects(Id32SpecGenProcessor())

    print()
    print("SUCCESS: all objects can be printed")


def all_demo():
    print()
    print("===================")
    setup_globals.newcollection("id22_stscan_collection")
    id22_stscan_demo()

    print()
    print("===================")
    setup_globals.newcollection("id22_xrpd_collection")
    id22_xrpd_demo()

    print()
    print("===================")
    setup_globals.newcollection("streamline_collection")
    streamline_demo()

    print()
    print("===================")
    setup_globals.newcollection("id11_collection")
    print("TODO: get license for diffpy")
    # id11_pdf_demo()

    print()
    print("===================")
    setup_globals.newcollection("xrpd_collection")
    xrpd_demo()
    xrpd_demo_get_data()

    # TODO: ewoksxrpd needs to be imported before xraylarch?
    #       Cannot load backend 'Qt5Agg' which requires the 'qt' interactive framework
    print()
    print("===================")
    setup_globals.newcollection("exafs_collection")
    exafs_demo()

    print()
    print("===================")
    setup_globals.newcollection("id14_collection")
    id14_demo()

    print()
    print("===================")
    setup_globals.newcollection("id12_collection")
    id12_demo()

    print()
    print("===================")
    setup_globals.newcollection("bm02_collection")
    bm02_demo_1d()
    bm02_demo_2d()

    print()
    print("===================")
    setup_globals.newcollection("done_collection")

    print()
    print("SUCCESS: all demos can be executed")


def _print_objects(obj):
    print()
    print("===================")
    print(obj._parameters.name)
    print(obj.__info__())

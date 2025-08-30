from blissoda.bliss_globals import setup_globals
from blissoda.demo.id14 import id14_converter


def id14_demo(expo=0.2, npoints=10):
    id14_converter.enable()
    try:
        setup_globals.loopscan(npoints, expo, setup_globals.mca1)
    finally:
        id14_converter.disable()

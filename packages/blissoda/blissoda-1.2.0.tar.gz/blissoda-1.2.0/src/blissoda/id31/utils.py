from ..bliss_globals import setup_globals


def ensure_shutter_open():
    if setup_globals.ehss.state == setup_globals.ehss.state.CLOSED:
        setup_globals.shopen()

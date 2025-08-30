"""For the BLISS demo session"""

import os

EWOKS_EVENTS_DIR = os.path.join(
    os.path.abspath(os.environ.get("DEMO_TMP_ROOT", ".")), "ewoks_events"
)

EWOKS_RESULTS_DIR = os.path.join(
    os.path.abspath(os.environ.get("DEMO_TMP_ROOT", ".")), "ewoks_results"
)

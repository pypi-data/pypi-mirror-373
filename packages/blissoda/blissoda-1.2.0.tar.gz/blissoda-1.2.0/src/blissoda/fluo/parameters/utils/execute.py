import os
import sys
import time
from datetime import timedelta
from pprint import pprint
from typing import List

try:
    from ewoks import show_graph as _show_graph
except ImportError:
    _show_graph = None

try:
    from ewoks import execute_graph as _execute_graph
except ImportError:
    _execute_graph = None

from . import defaults
from . import directories


def execute_graph(workflow: str, inputs: List[dict], convert_destination: str):
    """Used by offline processing scripts."""
    if not _execute_graph:
        raise RuntimeError("Ewoks workflows cannot be excuted in this environment.")

    directories.ensure_workflow_exists(workflow)

    if _show_graph:
        column_widths = {
            "name": None,
            "value": 80,
            "task_identifier": None,
        }
        _show_graph(
            workflow,
            inputs=inputs,
            column_widths=column_widths,
            original_source=workflow,
        )
        sys.stdout.flush()

    if defaults.DO_PROFILE:
        task_options = {
            "profile_directory": os.path.join(os.path.sep, "tmp", "ewoksprofile")
        }
    else:
        task_options = None

    start = time.time()
    try:
        print()
        result = _execute_graph(
            workflow,
            inputs=inputs,
            convert_destination=convert_destination,
            task_options=task_options,
        )
        pprint(result)
    finally:
        end = time.time()
        duration = timedelta(seconds=end - start)
        print(f"\nDuration: {duration}")
        if convert_destination:
            print(f"\nWorkflow: {convert_destination}")
        if task_options:
            print(
                f"\nProfiling results: {task_options['profile_directory']} (use 'pyprof2calltree -k -i ...' or 'snakeviz ...' to visualize the result)"
            )

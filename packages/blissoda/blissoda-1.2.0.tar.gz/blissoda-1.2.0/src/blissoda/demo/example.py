"""Send a workflow to the ewoks Celery application and recieve the
intermediate results (ewoks events) or final result (job return value)
"""

import os
import tempfile

from ewoksjob.client import submit
from ewoksjob.events.readers import instantiate_reader

from . import EWOKS_EVENTS_DIR


def example_job(redis=False):
    # Events during execution
    if redis:
        # Redis backend
        events_url = "redis://localhost:10002/5"
        handlers = [
            {
                "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
                "arguments": [{"name": "url", "value": events_url}],
            }
        ]
    else:
        # SQLite backend
        events_url = f"file://{EWOKS_EVENTS_DIR}"
        handlers = [
            {
                "class": "ewoksjob.events.handlers.Sqlite3EwoksEventHandler",
                "arguments": [{"name": "uri", "value": events_url}],
            }
        ]
    print("Ewoks events:", events_url)

    # Test workflow to execute
    workflow = {
        "graph": {"id": "mygraph"},
        "nodes": [
            {"id": "task1", "task_type": "method", "task_identifier": "numpy.add"},
            {"id": "task2", "task_type": "method", "task_identifier": "numpy.add"},
        ],
        "links": [
            {
                "source": "task1",
                "target": "task2",
                "data_mapping": [{"source_output": "return_value", "target_input": 0}],
            }
        ],
    }

    # Job arguments
    out_dir = tempfile.mkdtemp(dir=os.environ["DEMO_TMP_ROOT"], prefix="test_job_")
    print("Artifacts:", out_dir)
    varinfo = {"root_uri": out_dir, "scheme": "nexus"}
    inputs = [
        {"id": "task1", "name": 0, "value": 1},
        {"id": "task1", "name": 1, "value": 2},
        {"id": "task2", "name": 1, "value": 3},
    ]
    execinfo = {"handlers": handlers}
    args = (workflow,)
    kwargs = {
        "engine": None,
        "execinfo": execinfo,
        "inputs": inputs,
        "varinfo": varinfo,
        "outputs": [{"all": False}],
    }

    # Trigger workflow
    future = submit(args=args, kwargs=kwargs)
    job_id = future.uuid

    # events could be received in the mean time (see below)
    print(f"Wait for job {job_id} to finished ...")
    workflow_results = future.result(timeout=3, interval=0.1)
    print("Results:", workflow_results)
    assert workflow_results == {"return_value": 6}

    reader = instantiate_reader(events_url)

    # Get intermediate results from ewoks events
    results_during_execution = list(reader.get_events(job_id=job_id))
    assert len(results_during_execution) == 8  # start/stop for job, workflow and node

    try:
        # Get start event of node "task1"
        result_event = list(
            reader.get_events_with_variables(
                job_id=job_id, node_id="task1", type="start"
            )
        )
    except ImportError as e:
        print(f"Cannot read ewoks event URL's: {e}")
    else:
        assert len(result_event) == 1
        result_event = result_event[0]

        # Get access to all output variables of "task1"
        if varinfo.get("root_uri"):
            results = result_event["outputs"]
            assert results["return_value"].value == 3

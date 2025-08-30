import logging
from typing import Dict
from typing import Iterator
from typing import Tuple

from blissdata.beacon.data import BeaconData
from blissdata.redis_engine.scan import Scan
from blissdata.redis_engine.store import DataStore

logger = logging.getLogger(__name__)


def scan_iterator(session_name) -> Iterator[Tuple[str, int, Dict]]:
    logger.info(f"Started listening to Bliss session '{session_name}'")

    redis_url = BeaconData().get_redis_data_db()
    data_store = DataStore(redis_url)
    since = data_store.get_last_scan_timetag()
    while True:
        since, key = data_store.get_next_scan(since=since)
        scan = data_store.load_scan(key, scan_cls=Scan)
        if scan.session != session_name:
            continue
        if scan.info.get("is-scan-sequence") or scan.info.get("group"):
            continue
        workflows = scan.info.get("workflows")
        if not workflows:
            continue
        filename = scan.info.get("filename")
        yield filename, scan.number, workflows

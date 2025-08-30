from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional

from ..bliss_globals import current_session
from ..id31.xrpd_processor import Id31XrpdProcessor
from ..utils import directories
from ._id31_utils import ensure_difflab6_id31_flats
from .calib import DEFAULT_CALIB

_logger = logging.getLogger(__name__)


def ensure_demo_pyfai_config() -> str:
    """Create pyFAI config if not available yet and returns its filename"""
    processed_dir = directories.get_processed_dir(current_session.scan_saving.filename)
    config_path = Path(processed_dir, "config", "pyfaicalib.json")
    if not config_path.is_file():
        _logger.info(f"Create ID31 demo pyFAI config file: {str(config_path)}")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(DEFAULT_CALIB))

    return str(config_path)


class DemoId31XrpdProcessor(Id31XrpdProcessor):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        if self._HAS_BLISS:
            pyfai_config = ensure_demo_pyfai_config()
            newflat, oldflat = ensure_difflab6_id31_flats()
            defaults.setdefault("pyfai_config", pyfai_config)

        defaults.setdefault("queue", "celery")
        defaults.setdefault("lima_names", ["difflab6"])

        super().__init__(config=config, defaults=defaults)

        if self._HAS_BLISS:
            self.newflat = newflat
            self.oldflat = oldflat


id31_xrpd_processor = DemoId31XrpdProcessor()

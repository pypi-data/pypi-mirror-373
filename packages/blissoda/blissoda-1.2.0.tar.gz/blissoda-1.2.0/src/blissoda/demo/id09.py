from typing import Any
from typing import Dict
from typing import Optional

from ..id09.txs_processor import TxsProcessor


class DemoTxsProcessor(TxsProcessor):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        super().__init__(config=config, defaults=defaults)

        self.detector = "difflab6"
        self.pixel = (10e-3, 10e-3)
        self.energy = 10


txs_processor = DemoTxsProcessor()

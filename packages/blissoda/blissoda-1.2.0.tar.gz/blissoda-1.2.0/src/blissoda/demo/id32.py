from typing import Any
from typing import Dict
from typing import Optional

from ..id32.processor import Id32SpecGenProcessor


class DemoId32Processor(Id32SpecGenProcessor):
    QUEUE = None

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)
        super().__init__(detectors=("difflab6",), config=config, defaults=defaults)


id32_processor = DemoId32Processor()

import os
from typing import Any
from typing import Dict
from typing import Optional

from ..id12.converter import Id12Hdf5ToAsciiConverter
from . import EWOKS_RESULTS_DIR


class DemoId12Hdf5ToSpecConverter(Id12Hdf5ToAsciiConverter):
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ) -> None:
        defaults = self._merge_defaults(deprecated_defaults, defaults)

        root_dir = os.path.join(EWOKS_RESULTS_DIR, "id12", "inhouse")
        defaults.setdefault(
            "external_proposal_outdir", os.path.join(root_dir, "EXTERNAL")
        )
        defaults.setdefault(
            "inhouse_proposal_outdir", os.path.join(root_dir, "INHOUSE2")
        )
        defaults.setdefault("test_proposal_outdir", os.path.join(root_dir, "NOBACKUP"))

        super().__init__(config=config, defaults=defaults)

    def on_new_scan_metadata(self, scan) -> None:
        super().on_new_scan_metadata(scan)
        filename = self.output_filename(scan)
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)
        scan_basename = f"scan{scan.scan_info['scan_nb']:03d}_{basename}"
        filename = os.path.join(dirname, scan_basename)
        print("Scan data will be saved in ASCII file", filename)


id12_converter = DemoId12Hdf5ToSpecConverter()

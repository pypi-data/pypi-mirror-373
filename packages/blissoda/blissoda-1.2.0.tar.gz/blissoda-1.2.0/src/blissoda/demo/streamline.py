import os

from ..streamline.scanner import StreamlineScanner
from ._streamline_utils import DemoStreamlineScannerMixIn


class DemoStreamlineScanner(DemoStreamlineScannerMixIn, StreamlineScanner):
    def run(self, *args, **kwargs):
        if not os.path.exists(self.workflow):
            raise RuntimeError(
                "the workflow file no longer exists, execute 'init_workflow' again"
            )
        super().run(*args, **kwargs)


streamline_scanner = DemoStreamlineScanner()

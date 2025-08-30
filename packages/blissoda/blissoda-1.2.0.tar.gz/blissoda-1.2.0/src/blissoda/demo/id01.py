from ..id01.cdi_processor import CdiProcessor


class DemoCdiProcessor(CdiProcessor):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._set_parameter("counter", "beamviewer_roi1")


cdi_processor = DemoCdiProcessor()

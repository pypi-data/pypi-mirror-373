from ..flint import WithFlintAccess


class Id02Plotter(WithFlintAccess):
    def __init__(self, number_of_scans: int) -> None:
        super().__init__()
        self._number_of_scans = number_of_scans

    def replot(self):
        pass

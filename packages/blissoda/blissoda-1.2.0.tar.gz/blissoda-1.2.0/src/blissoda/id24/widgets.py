"""Flint-side for Flint ID24 plots"""

from ..flint import capture_errors
from ..gui.image_gallery import ImageGalleryViewer


class TemperatureWidget(ImageGalleryViewer):
    @capture_errors
    def select_directory(self, directory: str) -> None:
        return super().select_directory(directory)

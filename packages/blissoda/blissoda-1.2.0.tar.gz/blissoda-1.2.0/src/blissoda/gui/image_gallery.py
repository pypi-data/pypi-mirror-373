import os
from typing import Optional

from PyQt5 import Qt as qt


class ImageGalleryViewer(qt.QWidget):
    THUMBNAIL_MIN_WIDTH = 200
    THUMBNAIL_MIN_HEIGHT = 100
    THUMBNAIL_MAX_HEIGHT = 200

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._current_index: int = 0
        self._current_image: Optional[qt.QImage] = None
        self._images = []
        self._current_directory = None
        self._last_directory = None

        self._graphics_view = qt.QGraphicsView(qt.QGraphicsScene())
        self._graphics_view.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding
        )
        self._graphics_view.resizeEvent = self._resize_event_handler

        thumbnail_widget = qt.QWidget()
        self._thumbnail_layout = qt.QVBoxLayout(thumbnail_widget)
        self._thumbnail_area = qt.QScrollArea()
        self._thumbnail_area.setWidget(thumbnail_widget)
        self._thumbnail_area.setWidgetResizable(True)
        self._thumbnail_area.setVerticalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOn)
        self._thumbnail_area.setHorizontalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOff)
        self._thumbnail_area.setMinimumWidth(self.THUMBNAIL_MIN_WIDTH)

        load_images_button = qt.QPushButton("Load Images")
        load_images_button.clicked.connect(self._select_directory_interactive)
        clear_images_button = qt.QPushButton("Clear Images")
        clear_images_button.clicked.connect(self._clear_images)

        images_layout = qt.QHBoxLayout()
        splitter = qt.QSplitter(qt.Qt.Horizontal)
        splitter.addWidget(self._graphics_view)
        splitter.addWidget(self._thumbnail_area)
        images_layout.addWidget(splitter)

        button_layout = qt.QHBoxLayout()
        button_layout.addWidget(load_images_button)
        button_layout.addWidget(clear_images_button)

        layout = qt.QVBoxLayout(self)
        layout.addLayout(images_layout)
        layout.addLayout(button_layout)

        self._load_images()

    def select_directory(self, directory: str):
        self._last_directory = directory
        self._current_directory = directory
        self._load_images()

    def _select_directory_interactive(self):
        directory = qt.QFileDialog.getExistingDirectory(
            self, "Select Directory", self._last_directory
        )
        if directory:
            self.select_directory(directory)

    def _clear_images(self):
        self._current_directory = None
        self._load_images()

    def _load_images(self):
        if self._current_directory:
            images = [
                os.path.join(self._current_directory, filename)
                for filename in os.listdir(self._current_directory)
                if filename.endswith((".png", ".jpg", ".jpeg", ".gif"))
            ]
            self._images = sorted(images, key=os.path.getmtime)
        else:
            self._images = []
        self._current_image = None
        self._update_current_image()
        self._update_thumbnails()

    def _update_current_image(self):
        self._display_image(self._current_index)

    def _display_image(self, index: int):
        scene = self._graphics_view.scene()
        scene.clear()
        if not self._images:
            return
        index = min(index, len(self._images) - 1)

        if index != self._current_index or self._current_image is None:
            self._current_index = index
            self._current_image = qt.QImage(self._images[index])

        image = self._current_image.scaled(
            self._graphics_view.size(),
            qt.Qt.KeepAspectRatio,
            qt.Qt.SmoothTransformation,
        )
        pixmap = qt.QPixmap.fromImage(image)

        _ = scene.addPixmap(pixmap)

        # For testing
        # pixmap_item = scene.addPixmap(pixmap)
        # rect = pixmap_item.boundingRect()
        # pen = qt.QPen(qt.Qt.black)
        # pen.setWidth(2)
        # scene.addRect(rect, pen)

        scene = self._graphics_view.scene()
        item_bounds = scene.itemsBoundingRect()
        self._graphics_view.setSceneRect(item_bounds)
        self._graphics_view.fitInView(item_bounds, qt.Qt.KeepAspectRatio)

    def _resize_event_handler(self, event):
        self._update_current_image()
        self._update_thumbnail_icon_size()
        qt.QGraphicsView.resizeEvent(self._graphics_view, event)

    def _update_thumbnails(self):
        for i in reversed(range(self._thumbnail_layout.count())):
            widget = self._thumbnail_layout.itemAt(i).widget()
            if widget is not None:
                self._thumbnail_layout.removeWidget(widget)
                widget.deleteLater()

        thumbnail_size = self._thumbnail_size()
        for index, image_path in enumerate(self._images):
            thumbnail = qt.QPushButton()
            thumbnail.setIcon(qt.QIcon(image_path))
            thumbnail.setIconSize(thumbnail_size)
            thumbnail.clicked.connect(lambda _, idx=index: self._display_image(idx))
            self._thumbnail_layout.addWidget(thumbnail)

    def _update_thumbnail_icon_size(self):
        thumbnail_count = self._thumbnail_layout.count()
        if thumbnail_count == 0:
            return
        thumbnail_size = self._thumbnail_size()
        for i in range(thumbnail_count):
            widget = self._thumbnail_layout.itemAt(i).widget()
            widget.setIconSize(thumbnail_size)

    def _thumbnail_size(self):
        area_width = self._thumbnail_area.geometry().width()
        area_height = self._thumbnail_area.geometry().height()
        thumbnail_width = area_width
        thumbnail_count = len(self._images)
        if thumbnail_count:
            thumbnail_height = area_height // thumbnail_count
            thumbnail_height = min(thumbnail_height, self.THUMBNAIL_MAX_HEIGHT)
            thumbnail_height = max(thumbnail_height, self.THUMBNAIL_MIN_HEIGHT)
        else:
            thumbnail_height = self.THUMBNAIL_MIN_HEIGHT
        return qt.QSize(thumbnail_width, thumbnail_height)


if __name__ == "__main__":
    import sys

    app = qt.QApplication([])

    if len(sys.argv) == 2:
        directory = sys.argv[1]
    else:
        directory = None

    main_window = qt.QMainWindow()
    main_window.setWindowTitle("Image Gallery Viewer")
    main_window.setGeometry(100, 100, 800, 600)
    image_viewer = ImageGalleryViewer(parent=main_window)
    if directory:
        image_viewer.select_directory(directory)
    main_window.setCentralWidget(image_viewer)
    main_window.show()
    sys.exit(app.exec_())

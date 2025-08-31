from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtGui import QPixmap

class ImageLoader(QObject):
    """
    A worker that asynchronously downloads an image from a URL
    and emits a signal when it's ready.
    """
    finished = Signal(QPixmap)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self._on_finished)

    def load_from_url(self, url_string: str):
        """Starts downloading the image from the given URL."""
        self.manager.get(QNetworkRequest(QUrl(url_string)))

    def _on_finished(self, reply):
        """Handles the completed network request."""
        if reply.error():
            print(f"Image download error: {reply.errorString()}")
            self.finished.emit(QPixmap()) # Emit empty pixmap on error
        else:
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            self.finished.emit(pixmap)
        
        reply.deleteLater() 
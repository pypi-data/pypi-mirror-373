from .base import Trait
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QWidget
import json

class DraggableTrait(Trait):
    """
    Makes a widget draggable, initiating a drag-and-drop operation
    that carries data.
    """
    def apply(self, widget: QWidget):
        super().apply(widget)
        self.data = self.options.get("data", {})
        self._drag_start_position = None
        self._original_mousePressEvent = widget.mousePressEvent
        self._original_mouseMoveEvent = widget.mouseMoveEvent

        widget.mousePressEvent = self._mousePressEvent
        widget.mouseMoveEvent = self._mouseMoveEvent

    def _mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.pos()
        self._original_mousePressEvent(event)

    def _mouseMoveEvent(self, event):
        if self._drag_start_position is None or (event.pos() - self._drag_start_position).manhattanLength() < 10:
             if self._original_mouseMoveEvent:
                self._original_mouseMoveEvent(event)
             return

        drag = QDrag(self.widget)
        mime_data = QMimeData()
        mime_data.setText(json.dumps(self.data))
        drag.setMimeData(mime_data)

        pixmap = self.widget.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        drag.exec(Qt.DropAction.MoveAction)
        self._drag_start_position = None

    def remove(self):
        self.widget.mousePressEvent = self._original_mousePressEvent
        self.widget.mouseMoveEvent = self._original_mouseMoveEvent
        super().remove()

class DropTargetTrait(Trait):
    """
    Makes a widget a target for drag-and-drop operations.
    """
    def apply(self, widget: QWidget):
        super().apply(widget)
        self.on_drop = self.options.get("on_drop", lambda data: None)
        
        widget.setAcceptDrops(True)
        self._original_dragEnterEvent = widget.dragEnterEvent
        self._original_dropEvent = widget.dropEvent

        widget.dragEnterEvent = self._dragEnterEvent
        widget.dropEvent = self._dropEvent

    def _dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _dropEvent(self, event):
        try:
            data = json.loads(event.mimeData().text())
            self.on_drop(data)
            event.acceptProposedAction()
        except (json.JSONDecodeError, TypeError):
            event.ignore()
    
    def remove(self):
        self.widget.dragEnterEvent = self._original_dragEnterEvent
        self.widget.dropEvent = self._original_dropEvent
        super().remove() 
from .base import Trait
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QMenu

class ContextMenuTrait(Trait):
    """Adds a right-click context menu."""
    def apply(self, widget: QWidget):
        super().apply(widget)
        menu_items = self.options.get("items", {})
        if not menu_items: return

        self.menu = QMenu(widget)
        for name, handler in menu_items.items():
            if name == "---":
                self.menu.addSeparator()
            else:
                action = QAction(name, widget)
                action.triggered.connect(handler)
                self.menu.addAction(action)

        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        widget.customContextMenuRequested.connect(self._show_menu)

    def _show_menu(self, pos: QPoint):
        self.menu.exec(self.widget.mapToGlobal(pos))
    
    def remove(self):
        self.widget.customContextMenuRequested.disconnect(self._show_menu)
        super().remove() 
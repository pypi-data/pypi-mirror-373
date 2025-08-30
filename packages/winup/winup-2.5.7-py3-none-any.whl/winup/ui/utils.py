from PySide6.QtWidgets import QWidget
from winup.core.component import Component

def clear_layout(layout):
    """
    Removes all widgets from a layout, ensuring that any WinUp Components
    have their `_unmount` lifecycle hook called.
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # If the child is a Component, call its unmount handler
                if isinstance(widget, Component):
                    widget._unmount()
                widget.deleteLater()
            else:
                # If the item is a layout, clear it recursively
                sub_layout = item.layout()
                if sub_layout:
                    clear_layout(sub_layout) 
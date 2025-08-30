from .base import Trait
from PySide6.QtWidgets import QWidget

class TooltipTrait(Trait):
    """Adds a simple tooltip on hover."""
    def apply(self, widget: QWidget):
        super().apply(widget)
        text = self.options.get("text", "No tooltip text provided.")
        widget.setToolTip(text)
    
    def remove(self):
        self.widget.setToolTip("")
        super().remove() 
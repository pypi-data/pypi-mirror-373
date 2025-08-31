from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QStackedLayout, QGridLayout, QWidget
from PySide6.QtCore import Qt

class VBox(QVBoxLayout):
    """A low-level vertical layout manager."""
    def __init__(self, parent: QWidget = None, props: dict = None):
        super().__init__(parent)
        if props:
            self._apply_props(props)

    def _apply_props(self, props: dict):
        alignment = props.get("alignment")
        spacing = props.get("spacing")
        margin = props.get("margin")

        if alignment and hasattr(Qt.AlignmentFlag, alignment):
            self.setAlignment(getattr(Qt.AlignmentFlag, alignment))
        if spacing is not None:
            self.setSpacing(spacing)
        if margin is not None:
            if isinstance(margin, int):
                self.setContentsMargins(margin, margin, margin, margin)
            elif isinstance(margin, (list, tuple)) and len(margin) == 4:
                self.setContentsMargins(*margin)

class HBox(QHBoxLayout):
    """A low-level horizontal layout manager."""
    def __init__(self, parent: QWidget = None, props: dict = None):
        super().__init__(parent)
        if props:
            self._apply_props(props)

    def _apply_props(self, props: dict):
        alignment = props.get("alignment")
        spacing = props.get("spacing")
        margin = props.get("margin")

        if alignment and hasattr(Qt.AlignmentFlag, alignment):
            self.setAlignment(getattr(Qt.AlignmentFlag, alignment))
        if spacing is not None:
            self.setSpacing(spacing)
        if margin is not None:
            if isinstance(margin, int):
                self.setContentsMargins(margin, margin, margin, margin)
            elif isinstance(margin, (list, tuple)) and len(margin) == 4:
                self.setContentsMargins(*margin)

class StackBox(QStackedLayout):
    """A low-level stacked layout manager."""
    def __init__(self, parent: QWidget = None, props: dict = None):
        super().__init__(parent)
        if props:
            self._apply_props(props)

    def _apply_props(self, props: dict):
        # QStackedLayout has fewer properties to apply than box layouts
        margin = props.get("margin")
        if margin is not None:
            if isinstance(margin, int):
                self.setContentsMargins(margin, margin, margin, margin)
            elif isinstance(margin, (list, tuple)) and len(margin) == 4:
                self.setContentsMargins(*margin)

class GridBox(QGridLayout):
    """A low-level grid layout manager."""
    def __init__(self, parent: QWidget = None, props: dict = None):
        super().__init__(parent)
        if props:
            self._apply_props(props)

    def _apply_props(self, props: dict):
        spacing = props.get("spacing")
        margin = props.get("margin")
        h_spacing = props.get("horizontal-spacing")
        v_spacing = props.get("vertical-spacing")

        if spacing is not None:
            self.setHorizontalSpacing(spacing)
            self.setVerticalSpacing(spacing)
        if h_spacing is not None:
            self.setHorizontalSpacing(h_spacing)
        if v_spacing is not None:
            self.setVerticalSpacing(v_spacing)

        if margin is not None:
            if isinstance(margin, int):
                self.setContentsMargins(margin, margin, margin, margin)
            elif isinstance(margin, (list, tuple)) and len(margin) == 4:
                self.setContentsMargins(*margin)

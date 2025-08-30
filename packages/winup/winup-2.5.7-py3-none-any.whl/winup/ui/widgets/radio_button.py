from PySide6.QtWidgets import QRadioButton
from ... import style

class RadioButton(QRadioButton):
    def __init__(self, text: str = "RadioButton", props: dict = None, on_toggle: callable = None, **kwargs):
        super().__init__(text, **kwargs)
        if on_toggle:
            self.toggled.connect(on_toggle)
        if props:
            style.apply_props(self, props)

    def set_text(self, text: str):
        self.setText(text)

    def on_toggle(self, func: callable):
        """
        Sets the function to be called when the radio button is toggled.
        This replaces any previously set toggle handler.
        """
        try:
            self.toggled.disconnect()
        except RuntimeError:
            pass
        self.toggled.connect(func)
        return self

    def is_checked(self):
        return self.isChecked()

    def set_checked(self, checked: bool):
        self.setChecked(checked)
        return self 
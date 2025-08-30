from PySide6.QtWidgets import QWidget
from typing import Optional

class Trait:
    """Base class for all traits. Defines the interface."""
    def __init__(self, **kwargs):
        self.options = kwargs
        self.widget = None

    def apply(self, widget: QWidget):
        """Logic to apply the trait's behavior to a widget."""
        self.widget = widget

    def remove(self):
        """Logic to clean up and remove the trait's behavior."""
        self.widget = None

class _TraitManager:
    """Internal class to manage traits attached to widgets."""
    def __init__(self):
        self._widget_traits = {} # {widget_id: {trait_name: trait_instance}}

    def add(self, widget: QWidget, trait: 'Trait', trait_name: str):
        widget_id = id(widget)
        if widget_id not in self._widget_traits:
            self._widget_traits[widget_id] = {}
        
        if trait_name in self._widget_traits[widget_id]:
            self._widget_traits[widget_id][trait_name].remove()

        self._widget_traits[widget_id][trait_name] = trait
        trait.apply(widget)

    def get(self, widget: QWidget, trait_name: str) -> Optional['Trait']:
        return self._widget_traits.get(id(widget), {}).get(trait_name)

    def remove(self, widget: QWidget, trait_name: str):
        widget_id = id(widget)
        if widget_id in self._widget_traits and trait_name in self._widget_traits[widget_id]:
            self._widget_traits[widget_id][trait_name].remove()
            del self._widget_traits[widget_id][trait_name] 
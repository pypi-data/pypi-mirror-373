"""
The WinUp Trait System.

Traits are modular, reusable behaviors that can be dynamically attached to any
widget to give it new functionality without subclassing.
"""
from PySide6.QtWidgets import QWidget
from .base import Trait, _TraitManager
from typing import Optional

# --- Public API ---
_manager = _TraitManager()
_available_traits = {}

def register_trait(name: str, trait_class: type[Trait]):
    """Registers a new trait class for use with add_trait."""
    _available_traits[name] = trait_class

def add_trait(widget: QWidget, trait_name: str, **kwargs):
    """Adds a trait to a widget by its registered name."""
    if trait_name not in _available_traits:
        raise ValueError(f"Trait '{trait_name}' is not registered.")
    trait_instance = _available_traits[trait_name](**kwargs)
    _manager.add(widget, trait_instance, trait_name)

def remove_trait(widget: QWidget, trait_name: str):
    """Removes a trait from a widget."""
    _manager.remove(widget, trait_name)

def get_trait(widget: QWidget, trait_name: str) -> Optional[Trait]:
    """Gets a trait instance from a widget."""
    return _manager.get(widget, trait_name)

# --- Register Built-in Traits ---
from .tooltip import TooltipTrait
from .context_menu import ContextMenuTrait
from .dnd import DraggableTrait, DropTargetTrait
from .effects import HoverEffectTrait, HighlightableTrait

register_trait("tooltip", TooltipTrait)
register_trait("context_menu", ContextMenuTrait)
register_trait("draggable", DraggableTrait)
register_trait("drop_target", DropTargetTrait)
register_trait("hover_effect", HoverEffectTrait)
register_trait("highlightable", HighlightableTrait)

__all__ = ["add_trait", "remove_trait", "get_trait", "register_trait", "Trait"] 
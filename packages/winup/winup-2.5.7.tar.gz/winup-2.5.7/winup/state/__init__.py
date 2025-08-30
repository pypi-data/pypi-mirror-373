# winup/state/__init__.py
from .manager import StateManager

# Create a singleton instance to be used across the application
state = StateManager()

__all__ = ["state"] 
class EventBus:
    """A simple global event bus for decoupled communication."""
    def __init__(self):
        self._listeners = {}

    def on(self, event_name: str, callback: callable):
        """Register a listener for a specific event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, *args, **kwargs):
        """Emit an event, calling all registered listeners."""
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(*args, **kwargs)

# Singleton instance
event_bus = EventBus() 
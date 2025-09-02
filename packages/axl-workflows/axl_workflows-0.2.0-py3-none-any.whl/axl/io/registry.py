"""IO handler registry for AXL Workflows."""

from .handlers.cloudpickle import CloudpickleIOHandler
from .handlers.pickle import PickleIOHandler
from .protocol import IOHandler


class IOHandlerRegistry:
    """Registry for IO handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, type[IOHandler]] = {}

    def register(self, name: str, handler_class: type[IOHandler]) -> None:
        """Register a handler.

        Args:
            name: Handler name
            handler_class: Handler class to register
        """
        self._handlers[name] = handler_class

    def get(self, name: str) -> IOHandler:
        """Get a handler instance.

        Args:
            name: Handler name

        Returns:
            Handler instance

        Raises:
            ValueError: If handler not found
        """
        if name not in self._handlers:
            raise ValueError(f"Unknown IO handler: {name}")
        return self._handlers[name]()

    def list_handlers(self) -> list[str]:
        """List available handlers.

        Returns:
            List of handler names
        """
        return list(self._handlers.keys())

    def has_handler(self, name: str) -> bool:
        """Check if handler exists.

        Args:
            name: Handler name

        Returns:
            True if handler exists
        """
        return name in self._handlers


# Global registry instance
registry = IOHandlerRegistry()

# Register default handlers
registry.register("pickle", PickleIOHandler)
registry.register("cloudpickle", CloudpickleIOHandler)

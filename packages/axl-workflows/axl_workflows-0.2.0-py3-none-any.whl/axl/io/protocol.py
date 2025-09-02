"""IOHandler protocol for AXL Workflows."""

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IOHandler(Protocol):
    """Protocol for IO handlers that save/load Python objects."""

    def save(self, obj: Any, path: Path) -> None:
        """Save object to file path.

        Args:
            obj: Object to save
            path: File path to save to
        """
        ...

    def load(self, path: Path) -> Any:
        """Load object from file path.

        Args:
            path: File path to load from

        Returns:
            Loaded object
        """
        ...

    def dumps(self, obj: Any) -> bytes:
        """Convert object to bytes.

        Args:
            obj: Object to serialize

        Returns:
            Serialized bytes
        """
        ...

    def loads(self, data: bytes) -> Any:
        """Load object from bytes.

        Args:
            data: Serialized bytes

        Returns:
            Deserialized object
        """
        ...

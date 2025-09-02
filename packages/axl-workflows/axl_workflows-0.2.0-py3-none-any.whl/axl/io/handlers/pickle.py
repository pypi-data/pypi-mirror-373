"""Pickle-based IO handler for AXL Workflows."""

import pickle
from pathlib import Path
from typing import Any


class PickleIOHandler:
    """Pickle-based IO handler for Python objects."""

    def save(self, obj: Any, path: Path) -> None:
        """Save object to file using pickle.

        Args:
            obj: Object to save
            path: File path to save to
        """
        with open(path, "wb") as f:
            pickle.dump(obj, f)

    def load(self, path: Path) -> Any:
        """Load object from file using pickle.

        Args:
            path: File path to load from

        Returns:
            Loaded object
        """
        with open(path, "rb") as f:
            return pickle.load(f)

    def dumps(self, obj: Any) -> bytes:
        """Convert object to bytes using pickle.

        Args:
            obj: Object to serialize

        Returns:
            Serialized bytes
        """
        return pickle.dumps(obj)

    def loads(self, data: bytes) -> Any:
        """Load object from bytes using pickle.

        Args:
            data: Serialized bytes

        Returns:
            Deserialized object
        """
        return pickle.loads(data)

"""Cloudpickle-based IO handler for AXL Workflows."""

from pathlib import Path
from typing import Any

try:
    import cloudpickle  # type: ignore[import-untyped]
except ImportError:
    cloudpickle = None


class CloudpickleIOHandler:
    """Cloudpickle-based IO handler for Python objects.

    Uses cloudpickle for better serialization of complex Python objects
    including functions, classes, and lambda expressions.
    """

    def __init__(self) -> None:
        """Initialize cloudpickle handler."""
        if cloudpickle is None:
            raise ImportError(
                "cloudpickle is required for CloudpickleIOHandler. "
                "Install with: pip install cloudpickle"
            )

    def save(self, obj: Any, path: Path) -> None:
        """Save object to file using cloudpickle.

        Args:
            obj: Object to save
            path: File path to save to
        """
        with open(path, "wb") as f:
            cloudpickle.dump(obj, f)

    def load(self, path: Path) -> Any:
        """Load object from file using cloudpickle.

        Args:
            path: File path to load from

        Returns:
            Loaded object
        """
        with open(path, "rb") as f:
            return cloudpickle.load(f)

    def dumps(self, obj: Any) -> bytes:
        """Convert object to bytes using cloudpickle.

        Args:
            obj: Object to serialize

        Returns:
            Serialized bytes
        """
        return bytes(cloudpickle.dumps(obj))

    def loads(self, data: bytes) -> Any:
        """Load object from bytes using cloudpickle.

        Args:
            data: Serialized bytes

        Returns:
            Deserialized object
        """
        return cloudpickle.loads(data)

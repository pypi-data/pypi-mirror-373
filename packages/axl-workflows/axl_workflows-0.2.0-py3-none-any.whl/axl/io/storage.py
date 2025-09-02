"""Storage backends for AXL Workflows."""

from pathlib import Path
from typing import Any


class StorageBackend:
    """Base class for storage backends."""

    def save(self, data: bytes, path: str) -> None:
        """Save bytes to storage.

        Args:
            data: Bytes to save
            path: Storage path
        """
        raise NotImplementedError

    def load(self, path: str) -> bytes:
        """Load bytes from storage.

        Args:
            path: Storage path

        Returns:
            Loaded bytes
        """
        raise NotImplementedError

    def exists(self, path: str) -> bool:
        """Check if path exists in storage.

        Args:
            path: Storage path

        Returns:
            True if path exists
        """
        raise NotImplementedError


class LocalFileStorage(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self, base_path: str = "/tmp") -> None:
        """Initialize local storage.

        Args:
            base_path: Base directory for storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, path: str) -> None:
        """Save bytes to local file.

        Args:
            data: Bytes to save
            path: Relative path from base_path
        """
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(data)

    def load(self, path: str) -> bytes:
        """Load bytes from local file.

        Args:
            path: Relative path from base_path

        Returns:
            Loaded bytes
        """
        full_path = self.base_path / path

        with open(full_path, "rb") as f:
            return f.read()

    def exists(self, path: str) -> bool:
        """Check if file exists.

        Args:
            path: Relative path from base_path

        Returns:
            True if file exists
        """
        full_path = self.base_path / path
        return full_path.exists()


class InMemoryStorage(StorageBackend):
    """In-memory storage backend for testing."""

    def __init__(self) -> None:
        """Initialize in-memory storage."""
        self._storage: dict[str, bytes] = {}

    def save(self, data: bytes, path: str) -> None:
        """Save bytes to memory.

        Args:
            data: Bytes to save
            path: Storage key
        """
        self._storage[path] = data

    def load(self, path: str) -> bytes:
        """Load bytes from memory.

        Args:
            path: Storage key

        Returns:
            Loaded bytes
        """
        if path not in self._storage:
            raise FileNotFoundError(f"Path not found: {path}")
        return self._storage[path]

    def exists(self, path: str) -> bool:
        """Check if path exists in memory.

        Args:
            path: Storage key

        Returns:
            True if path exists
        """
        return path in self._storage

    def clear(self) -> None:
        """Clear all stored data."""
        self._storage.clear()


class StorageRegistry:
    """Registry for storage backends."""

    def __init__(self) -> None:
        """Initialize storage registry."""
        self._backends: dict[str, type[StorageBackend]] = {}

    def register(self, name: str, backend_class: type[StorageBackend]) -> None:
        """Register a storage backend.

        Args:
            name: Backend name
            backend_class: Backend class to register
        """
        self._backends[name] = backend_class

    def get(self, name: str, **kwargs: Any) -> StorageBackend:
        """Get a storage backend instance.

        Args:
            name: Backend name
            **kwargs: Arguments to pass to backend constructor

        Returns:
            Storage backend instance

        Raises:
            ValueError: If backend not found
        """
        if name not in self._backends:
            raise ValueError(f"Unknown storage backend: {name}")
        return self._backends[name](**kwargs)

    def list_backends(self) -> list[str]:
        """List available backends.

        Returns:
            List of backend names
        """
        return list(self._backends.keys())


# Global storage registry
storage_registry = StorageRegistry()

# Register default backends
storage_registry.register("local", LocalFileStorage)
storage_registry.register("memory", InMemoryStorage)


def create_storage_from_path(path: str) -> StorageBackend:
    """Create storage backend from path specification.

    Args:
        path: Path specification (e.g., "local:///tmp", "memory://")

    Returns:
        Storage backend instance

    Raises:
        ValueError: If path format is invalid
    """
    if "://" not in path:
        # Default to local storage
        return LocalFileStorage(path)

    scheme, rest = path.split("://", 1)

    if scheme == "local":
        return LocalFileStorage(rest)
    elif scheme == "memory":
        return InMemoryStorage()
    else:
        raise ValueError(f"Unsupported storage scheme: {scheme}")

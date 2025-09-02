"""Tests for storage backends."""

import tempfile
from pathlib import Path

import pytest

from axl.io import (
    InMemoryStorage,
    LocalFileStorage,
    StorageRegistry,
    create_storage_from_path,
    storage_registry,
)


class TestLocalFileStorage:
    """Test LocalFileStorage functionality."""

    def test_save_and_load(self) -> None:
        """Test saving and loading data to/from local files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage = LocalFileStorage(tmp_dir)
            test_data = b"test data"

            # Save data
            storage.save(test_data, "test/file.txt")

            # Load data
            loaded_data = storage.load("test/file.txt")
            assert loaded_data == test_data

    def test_exists(self) -> None:
        """Test checking if files exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage = LocalFileStorage(tmp_dir)

            # File doesn't exist initially
            assert not storage.exists("test.txt")

            # Save file
            storage.save(b"data", "test.txt")
            assert storage.exists("test.txt")

    def test_nested_directories(self) -> None:
        """Test creating nested directories automatically."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage = LocalFileStorage(tmp_dir)

            # Save to nested path
            storage.save(b"data", "nested/deep/path/file.txt")

            # Check file exists
            assert storage.exists("nested/deep/path/file.txt")

            # Load data
            data = storage.load("nested/deep/path/file.txt")
            assert data == b"data"

    def test_default_base_path(self) -> None:
        """Test default base path creation."""
        storage = LocalFileStorage()

        # Should create /tmp directory if it doesn't exist
        assert storage.base_path.exists()
        assert storage.base_path.is_dir()


class TestInMemoryStorage:
    """Test InMemoryStorage functionality."""

    def test_save_and_load(self) -> None:
        """Test saving and loading data in memory."""
        storage = InMemoryStorage()
        test_data = b"test data"

        # Save data
        storage.save(test_data, "test_key")

        # Load data
        loaded_data = storage.load("test_key")
        assert loaded_data == test_data

    def test_exists(self) -> None:
        """Test checking if keys exist."""
        storage = InMemoryStorage()

        # Key doesn't exist initially
        assert not storage.exists("test_key")

        # Save data
        storage.save(b"data", "test_key")
        assert storage.exists("test_key")

    def test_load_nonexistent_key(self) -> None:
        """Test loading nonexistent key raises error."""
        storage = InMemoryStorage()

        with pytest.raises(FileNotFoundError, match="Path not found: nonexistent"):
            storage.load("nonexistent")

    def test_clear(self) -> None:
        """Test clearing all stored data."""
        storage = InMemoryStorage()

        # Save some data
        storage.save(b"data1", "key1")
        storage.save(b"data2", "key2")

        assert storage.exists("key1")
        assert storage.exists("key2")

        # Clear all data
        storage.clear()

        assert not storage.exists("key1")
        assert not storage.exists("key2")


class TestStorageRegistry:
    """Test StorageRegistry functionality."""

    def test_register_and_get(self) -> None:
        """Test registering and retrieving backends."""
        registry = StorageRegistry()

        # Register backend
        registry.register("test", LocalFileStorage)

        # Get backend
        backend = registry.get("test", base_path="/tmp")
        assert isinstance(backend, LocalFileStorage)

    def test_get_unknown_backend(self) -> None:
        """Test getting unknown backend raises error."""
        registry = StorageRegistry()

        with pytest.raises(ValueError, match="Unknown storage backend: unknown"):
            registry.get("unknown")

    def test_list_backends(self) -> None:
        """Test listing available backends."""
        registry = StorageRegistry()

        # Initially empty
        assert registry.list_backends() == []

        # After registration
        registry.register("backend1", LocalFileStorage)
        registry.register("backend2", InMemoryStorage)

        backends = registry.list_backends()
        assert "backend1" in backends
        assert "backend2" in backends
        assert len(backends) == 2


class TestGlobalStorageRegistry:
    """Test the global storage registry instance."""

    def test_default_backends(self) -> None:
        """Test that default backends are registered."""
        assert "local" in storage_registry.list_backends()
        assert "memory" in storage_registry.list_backends()

    def test_get_local_backend(self) -> None:
        """Test getting the local backend."""
        backend = storage_registry.get("local", base_path="/tmp")
        assert isinstance(backend, LocalFileStorage)

    def test_get_memory_backend(self) -> None:
        """Test getting the memory backend."""
        backend = storage_registry.get("memory")
        assert isinstance(backend, InMemoryStorage)


class TestCreateStorageFromPath:
    """Test create_storage_from_path function."""

    def test_local_path_with_scheme(self) -> None:
        """Test creating local storage with scheme."""
        storage = create_storage_from_path("local:///tmp/test")
        assert isinstance(storage, LocalFileStorage)
        assert storage.base_path == Path("/tmp/test")

    def test_local_path_without_scheme(self) -> None:
        """Test creating local storage without scheme."""
        storage = create_storage_from_path("/tmp/test")
        assert isinstance(storage, LocalFileStorage)
        assert storage.base_path == Path("/tmp/test")

    def test_memory_path(self) -> None:
        """Test creating memory storage."""
        storage = create_storage_from_path("memory://")
        assert isinstance(storage, InMemoryStorage)

    def test_unsupported_scheme(self) -> None:
        """Test unsupported scheme raises error."""
        with pytest.raises(ValueError, match="Unsupported storage scheme: s3"):
            create_storage_from_path("s3://bucket/path")


class TestStorageIntegration:
    """Test storage integration with IO handlers."""

    def test_storage_with_pickle_handler(self) -> None:
        """Test using storage with pickle IO handler."""
        from axl.io.handlers import PickleIOHandler

        # Create storage and handler
        storage = InMemoryStorage()
        handler = PickleIOHandler()

        # Test object
        test_obj = {"key": "value", "numbers": [1, 2, 3]}

        # Save: object → pickle bytes → storage
        serialized = handler.dumps(test_obj)
        storage.save(serialized, "test_artifact.pkl")

        # Load: storage → pickle bytes → object
        loaded_bytes = storage.load("test_artifact.pkl")
        deserialized = handler.loads(loaded_bytes)

        assert deserialized == test_obj

    def test_storage_with_cloudpickle_handler(self) -> None:
        """Test using storage with cloudpickle IO handler."""
        try:
            from axl.io.handlers import CloudpickleIOHandler

            # Create storage and handler
            storage = InMemoryStorage()
            handler = CloudpickleIOHandler()

            # Test object with lambda (requires cloudpickle)
            test_obj = {"func": lambda x: x * 2, "data": [1, 2, 3]}

            # Save: object → cloudpickle bytes → storage
            serialized = handler.dumps(test_obj)
            storage.save(serialized, "test_artifact.cpkl")

            # Load: storage → cloudpickle bytes → object
            loaded_bytes = storage.load("test_artifact.cpkl")
            deserialized = handler.loads(loaded_bytes)

            # Test the loaded function
            assert deserialized["func"](5) == 10
            assert deserialized["data"] == [1, 2, 3]

        except ImportError:
            pytest.skip("cloudpickle not available")

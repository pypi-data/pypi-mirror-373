"""Tests for IO handlers."""

import tempfile
from pathlib import Path
from typing import Any

import pytest

from axl.io import IOHandler, IOHandlerRegistry, PickleIOHandler, registry


class TestPickleIOHandler:
    """Test PickleIOHandler functionality."""

    def test_save_and_load_file(self) -> None:
        """Test saving and loading objects to/from files."""
        handler = PickleIOHandler()
        test_data = {"key": "value", "numbers": [1, 2, 3]}

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            path = Path(tmp.name)

        try:
            # Save object
            handler.save(test_data, path)

            # Load object
            loaded_data = handler.load(path)

            assert loaded_data == test_data
        finally:
            path.unlink(missing_ok=True)

    def test_dumps_and_loads_bytes(self) -> None:
        """Test converting objects to/from bytes."""
        handler = PickleIOHandler()
        test_data = {"key": "value", "numbers": [1, 2, 3]}

        # Convert to bytes
        serialized = handler.dumps(test_data)
        assert isinstance(serialized, bytes)

        # Convert from bytes
        deserialized = handler.loads(serialized)
        assert deserialized == test_data

    def test_protocol_compliance(self) -> None:
        """Test that PickleIOHandler implements IOHandler protocol."""
        handler = PickleIOHandler()

        # Check that all required methods exist
        assert hasattr(handler, "save")
        assert hasattr(handler, "load")
        assert hasattr(handler, "dumps")
        assert hasattr(handler, "loads")

        # Check that it's callable as IOHandler
        assert isinstance(handler, IOHandler)

    def test_complex_objects(self) -> None:
        """Test handling complex Python objects."""
        handler = PickleIOHandler()

        # Test with various object types
        test_objects = [
            "simple string",
            42,
            [1, 2, 3],
            {"a": 1, "b": 2},
            (1, 2, 3),
            {1, 2, 3},
            None,
            True,
            False,
        ]

        for obj in test_objects:
            serialized = handler.dumps(obj)
            deserialized = handler.loads(serialized)
            assert deserialized == obj


class TestIOHandlerRegistry:
    """Test IOHandlerRegistry functionality."""

    def test_register_and_get(self) -> None:
        """Test registering and retrieving handlers."""
        registry = IOHandlerRegistry()

        # Register handler
        registry.register("test", PickleIOHandler)

        # Get handler
        handler = registry.get("test")
        assert isinstance(handler, PickleIOHandler)

    def test_get_unknown_handler(self) -> None:
        """Test getting unknown handler raises error."""
        registry = IOHandlerRegistry()

        with pytest.raises(ValueError, match="Unknown IO handler: unknown"):
            registry.get("unknown")

    def test_list_handlers(self) -> None:
        """Test listing available handlers."""
        registry = IOHandlerRegistry()

        # Initially empty
        assert registry.list_handlers() == []

        # After registration
        registry.register("handler1", PickleIOHandler)
        registry.register("handler2", PickleIOHandler)

        handlers = registry.list_handlers()
        assert "handler1" in handlers
        assert "handler2" in handlers
        assert len(handlers) == 2

    def test_has_handler(self) -> None:
        """Test checking if handler exists."""
        registry = IOHandlerRegistry()

        assert not registry.has_handler("test")

        registry.register("test", PickleIOHandler)
        assert registry.has_handler("test")


class TestGlobalRegistry:
    """Test the global registry instance."""

    def test_default_handlers(self) -> None:
        """Test that default handlers are registered."""
        assert registry.has_handler("pickle")
        assert "pickle" in registry.list_handlers()

    def test_get_pickle_handler(self) -> None:
        """Test getting the default pickle handler."""
        handler = registry.get("pickle")
        assert isinstance(handler, PickleIOHandler)

    def test_register_custom_handler(self) -> None:
        """Test registering custom handlers in global registry."""

        class CustomHandler:
            def save(self, obj: Any, path: Path) -> None:
                pass

            def load(self, path: Path) -> Any:
                pass

            def dumps(self, obj: Any) -> bytes:
                pass

            def loads(self, data: bytes) -> Any:
                pass

        registry.register("custom", CustomHandler)

        assert registry.has_handler("custom")
        handler = registry.get("custom")
        assert isinstance(handler, CustomHandler)


class TestIOHandlerProtocol:
    """Test IOHandler protocol compliance."""

    def test_protocol_definition(self) -> None:
        """Test that IOHandler protocol is properly defined."""
        # Check that protocol has required methods
        assert callable(IOHandler)  # Protocol objects are callable

        # Check method signatures (basic check)
        import inspect

        methods = inspect.getmembers(IOHandler, predicate=inspect.isfunction)
        method_names = [name for name, _ in methods]

        assert "save" in method_names
        assert "load" in method_names
        assert "dumps" in method_names
        assert "loads" in method_names

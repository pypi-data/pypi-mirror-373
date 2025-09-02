"""Tests for module imports and exports."""

import pytest

from axl import __all__


def test_all_imports():
    """Test that all exports can be imported."""
    import axl

    for name in __all__:
        if not hasattr(axl, name):
            pytest.fail(f"Could not import {name} from axl")


def test_all_defined():
    """Test that __all__ is defined."""
    assert __all__ is not None
    assert len(__all__) > 0

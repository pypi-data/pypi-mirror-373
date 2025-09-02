"""Tests for CLI parameter loading functionality."""

import tempfile
from pathlib import Path

import pytest
import typer
import yaml

from axl.cli import load_parameters


class TestParameterLoading:
    """Test parameter loading from YAML files."""

    def test_load_parameters_no_file(self):
        """Test loading parameters when no file is provided."""
        params = load_parameters(None)
        assert params == {}

    def test_load_parameters_valid_yaml(self):
        """Test loading parameters from a valid YAML file."""
        test_params = {
            "string_param": "test_value",
            "number_param": 42,
            "list_param": [1, 2, 3],
            "dict_param": {"key": "value"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_params, f)
            temp_file = f.name

        try:
            params = load_parameters(temp_file)
            assert params == test_params
        finally:
            Path(temp_file).unlink()

    def test_load_parameters_file_not_found(self):
        """Test loading parameters from a non-existent file."""
        with pytest.raises(typer.Exit):
            load_parameters("nonexistent.yaml")

    def test_load_parameters_invalid_yaml(self):
        """Test loading parameters from invalid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_file = f.name

        try:
            with pytest.raises((yaml.YAMLError, typer.Exit)):
                load_parameters(temp_file)
        finally:
            Path(temp_file).unlink()

    def test_load_parameters_not_dict(self):
        """Test loading parameters when YAML is not a dictionary."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(["list", "not", "dict"], f)
            temp_file = f.name

        try:
            with pytest.raises(typer.Exit):
                load_parameters(temp_file)
        finally:
            Path(temp_file).unlink()

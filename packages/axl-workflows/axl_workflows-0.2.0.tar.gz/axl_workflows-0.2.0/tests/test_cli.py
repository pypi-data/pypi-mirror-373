"""Tests for CLI commands."""

from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from axl.cli import app, load_workflow_class


class TestCLIValidation:
    """Test CLI validation command."""

    def setup_method(self) -> None:
        """Set up test runner."""
        self.runner = CliRunner()

    def test_validate_success(self) -> None:
        """Test successful workflow validation."""
        result = self.runner.invoke(
            app, ["validate", "examples/churn_workflow.py:ChurnTrain"]
        )

        assert result.exit_code == 0
        assert "Workflow Information" in result.stdout
        assert "churn-train" in result.stdout
        assert "✅ Workflow is valid!" in result.stdout
        assert "Steps" in result.stdout

    def test_validate_invalid_module_format(self) -> None:
        """Test validation with invalid module format."""
        result = self.runner.invoke(app, ["validate", "invalid_format"])

        assert result.exit_code == 1
        assert "Error loading workflow" in result.stdout
        assert "Module path must be in format" in result.stdout

    def test_validate_nonexistent_file(self) -> None:
        """Test validation with nonexistent file."""
        result = self.runner.invoke(app, ["validate", "nonexistent.py:MyWorkflow"])

        assert result.exit_code == 1
        assert "Error loading workflow" in result.stdout
        assert "Module file not found" in result.stdout

    def test_validate_nonexistent_class(self) -> None:
        """Test validation with nonexistent class."""
        result = self.runner.invoke(
            app, ["validate", "examples/churn_workflow.py:NonExistentClass"]
        )

        assert result.exit_code == 1
        assert "Error loading workflow" in result.stdout
        assert "not found in module" in result.stdout

    def test_validate_non_workflow_class(self) -> None:
        """Test validation with class that's not a workflow."""
        # Create a temporary file with a non-workflow class
        temp_file = Path("temp_test.py")
        try:
            temp_file.write_text(
                """
class NotAWorkflow:
    pass
"""
            )

            result = self.runner.invoke(app, ["validate", "temp_test.py:NotAWorkflow"])

            assert result.exit_code == 1
            assert "Error loading workflow" in result.stdout
            assert "not a workflow class" in result.stdout

        finally:
            temp_file.unlink(missing_ok=True)

    def test_validate_help(self) -> None:
        """Test validate command help."""
        result = self.runner.invoke(app, ["validate", "--help"])

        assert result.exit_code == 0
        assert "Validate a workflow definition" in result.stdout
        assert "Module path to workflow class" in result.stdout


class TestModuleLoading:
    """Test module loading functionality."""

    def test_load_workflow_class_success(self) -> None:
        """Test successful workflow class loading."""
        workflow_class = load_workflow_class("examples/churn_workflow.py:ChurnTrain")

        assert workflow_class.__name__ == "ChurnTrain"
        from axl.core.workflow import Workflow

        assert issubclass(workflow_class, Workflow)

    def test_load_workflow_class_invalid_format(self) -> None:
        """Test loading with invalid format."""
        with pytest.raises(typer.Exit):
            load_workflow_class("invalid_format")

    def test_load_workflow_class_nonexistent_file(self) -> None:
        """Test loading with nonexistent file."""
        with pytest.raises(typer.Exit):
            load_workflow_class("nonexistent.py:MyWorkflow")

    def test_load_workflow_class_nonexistent_class(self) -> None:
        """Test loading with nonexistent class."""
        with pytest.raises(typer.Exit):
            load_workflow_class("examples/churn_workflow.py:NonExistentClass")

    def test_load_workflow_class_non_workflow(self) -> None:
        """Test loading class that's not a workflow."""
        # Create a temporary file with a non-workflow class
        temp_file = Path("temp_test.py")
        try:
            temp_file.write_text(
                """
class NotAWorkflow:
    pass
"""
            )

            with pytest.raises(typer.Exit):
                load_workflow_class("temp_test.py:NotAWorkflow")

        finally:
            temp_file.unlink(missing_ok=True)


class TestCLICommands:
    """Test other CLI commands."""

    def setup_method(self) -> None:
        """Set up test runner."""
        self.runner = CliRunner()

    def test_version_command(self) -> None:
        """Test version command."""
        result = self.runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "AXL Workflows v" in result.stdout

    def test_compile_command_not_implemented(self) -> None:
        """Test compile command now implemented for argo target."""
        result = self.runner.invoke(
            app, ["compile", "examples/churn_workflow.py:ChurnTrain"]
        )

        assert result.exit_code == 0
        # Should print YAML and completion panel
        assert "apiVersion: argoproj.io/v1alpha1" in result.stdout
        assert "Compilation completed" in result.stdout

    def test_run_command_requires_module(self) -> None:
        """Run command requires --module for local backend."""
        result = self.runner.invoke(app, ["run", "local"])

        assert result.exit_code == 1
        assert "required for local execution" in result.stdout

    def test_render_command_not_implemented(self) -> None:
        """Test render command (not implemented yet)."""
        result = self.runner.invoke(
            app, ["render", "examples/churn_workflow.py:ChurnTrain"]
        )

        assert result.exit_code == 0
        assert "Not implemented yet" in result.stdout

    def test_cli_help(self) -> None:
        """Test main CLI help."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "AXL Workflows" in result.stdout
        assert "Commands" in result.stdout
        assert "validate" in result.stdout
        assert "compile" in result.stdout
        assert "run" in result.stdout
        assert "render" in result.stdout

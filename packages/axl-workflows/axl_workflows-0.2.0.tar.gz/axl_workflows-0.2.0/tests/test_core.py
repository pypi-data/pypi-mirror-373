"""
Tests for the core DSL components.
"""

import pytest

from axl.core import Workflow, step


class TestWorkflow:
    """Test cases for Workflow base class."""

    def test_workflow_creation(self) -> None:
        """Test that Workflow can be instantiated."""
        workflow = Workflow()
        assert workflow is not None
        assert workflow.image == "ghcr.io/axl-workflows/runner:latest"
        assert workflow.io_handler == "pickle"
        assert workflow.name == "Workflow"

    def test_workflow_graph_not_implemented(self) -> None:
        """Test that Workflow graph method raises NotImplementedError."""
        workflow = Workflow()
        with pytest.raises(NotImplementedError):
            workflow.graph()

    def test_workflow_custom_configuration(self) -> None:
        """Test that Workflow can be configured with custom values."""
        workflow = Workflow(
            image="custom-image:latest",
            io_handler="parquet",
            name="custom-name",
        )
        assert workflow.image == "custom-image:latest"
        assert workflow.io_handler == "parquet"
        assert workflow.name == "custom-name"

    def test_workflow_class_attributes(self) -> None:
        """Test that Workflow can use class attributes for configuration."""

        class TestWorkflow(Workflow):
            name = "test-workflow"
            image = "test-image:latest"
            io_handler = "numpy"

            def graph(self):
                return "test"

        workflow = TestWorkflow()
        assert workflow.name == "test-workflow"
        assert workflow.image == "test-image:latest"
        assert workflow.io_handler == "numpy"

    def test_workflow_class_attributes_with_overrides(self) -> None:
        """Test that constructor parameters override class attributes."""

        class TestWorkflow(Workflow):
            name = "test-workflow"
            image = "test-image:latest"
            io_handler = "numpy"

            def graph(self):
                return "test"

        workflow = TestWorkflow(
            name="override-name",
            image="override-image:latest",
        )
        assert workflow.name == "override-name"
        assert workflow.image == "override-image:latest"
        assert workflow.io_handler == "numpy"

    def test_workflow_validation_invalid_io_handler(self) -> None:
        """Test that Workflow validates io_handler."""
        with pytest.raises(ValueError, match="io_handler must be"):
            Workflow(io_handler="invalid")

    def test_workflow_configure_method(self) -> None:
        """Test that Workflow configure method works."""
        workflow = Workflow()
        workflow.configure(image="new-image:latest", io_handler="numpy")
        assert workflow.image == "new-image:latest"
        assert workflow.io_handler == "numpy"

    def test_workflow_configure_invalid_option(self) -> None:
        """Test that Workflow configure validates options."""
        workflow = Workflow()
        with pytest.raises(ValueError, match="Unknown configuration option"):
            workflow.configure(invalid_option="value")

    def test_workflow_get_config_methods(self) -> None:
        """Test that Workflow config getter methods work."""
        workflow = Workflow(
            io_handler="parquet",
        )

        workflow_config = workflow.get_workflow_config()
        assert workflow_config["image"] == "ghcr.io/axl-workflows/runner:latest"
        assert workflow_config["io_handler"] == "parquet"

    def test_workflow_repr(self) -> None:
        """Test that Workflow __repr__ method works."""
        workflow = Workflow()
        repr_str = repr(workflow)
        assert "Workflow(" in repr_str
        assert "name=" in repr_str
        assert "image=" in repr_str
        assert "io_handler=" in repr_str


class TestDecorators:
    """Test cases for step decorator."""

    def test_step_decorator_basic(self) -> None:
        """Test that step decorator works with basic configuration."""

        class TestWorkflow(Workflow):
            @step()
            def test_step(self):
                return "test"

            def graph(self):
                return self.test_step()

        wf = TestWorkflow()

        step_method = object.__getattribute__(wf, "test_step")
        assert hasattr(step_method, "_is_step")
        assert step_method._is_step is True
        assert step_method._step_config == {}

    def test_step_decorator_with_config(self) -> None:
        """Test that step decorator applies configuration correctly."""

        class TestWorkflow(Workflow):
            @step(io_handler="parquet", retries=3)
            def test_step(self):
                return "test"

            def graph(self):
                return self.test_step()

        wf = TestWorkflow()

        step_method = object.__getattribute__(wf, "test_step")
        assert step_method._step_config["io_handler"] == "parquet"
        assert step_method._step_config["retries"] == 3

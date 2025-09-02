"""
Workflow base class for AXL Workflows.

This module contains the core Workflow base class with configuration
and validation capabilities.
"""

from typing import Any

from ..ir import OutputRef
from ..logging import WorkflowLogger


class Workflow:
    """Base class for workflows with defaults and configuration."""

    def __init__(
        self,
        image: str | None = None,
        io_handler: str | None = None,
        name: str | None = None,
        **params: Any,
    ) -> None:
        """
        Initialize workflow with configuration and parameters.

        Args:
            image: Docker image for workflow execution (defaults to class attribute or default)
            io_handler: IO handler for step outputs (defaults to class attribute or pickle)
            name: Workflow name (defaults to class attribute or class name)
            **params: Additional parameters passed to the workflow
        """
        self.image = image or getattr(
            self, "image", "ghcr.io/axl-workflows/runner:latest"
        )
        self.io_handler = io_handler or getattr(self, "io_handler", "pickle")
        self.name = name or getattr(self, "name", self.__class__.__name__)

        self.workflow_params = params

        self.log = WorkflowLogger(str(self.name))

        self._validate_config()

    def _validate_config(self) -> None:
        """Validate workflow configuration."""
        if self.io_handler not in ["pickle", "parquet", "numpy", "torch"]:
            raise ValueError(
                f"io_handler must be one of ['pickle', 'parquet', 'numpy', 'torch'], "
                f"got {self.io_handler}"
            )

    def configure(self, **kwargs: Any) -> None:
        """
        Configure workflow settings after initialization.

        Args:
            **kwargs: Configuration options to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration option: {key}")

        self._validate_config()

    def get_workflow_config(self) -> dict[str, Any]:
        """
        Get workflow configuration for IR building.

        Returns:
            Dictionary with workflow configuration
        """
        return {
            "image": self.image,
            "io_handler": self.io_handler,
        }

    def graph(self) -> Any:
        """
        Define the workflow graph. Must be implemented by subclasses.

        Returns:
            Workflow output (typically the final step result as OutputRef)
        """
        raise NotImplementedError("graph method must be implemented")

    def __getattribute__(self, name: str) -> Any:
        """
        Intercept step method calls to return OutputRef instances.

        Step method calls always return OutputRef instances for IR building.

        Args:
            name: Method name to look up

        Returns:
            OutputRef if it's a step method, otherwise normal attribute
        """
        attr = object.__getattribute__(self, name)

        if hasattr(attr, "_is_step") and attr._is_step:
            output_ref = OutputRef(name)
            if hasattr(attr, "_step_config"):
                output_ref.metadata["step_config"] = attr._step_config
            return output_ref

        return attr

    def __repr__(self) -> str:
        """String representation of the workflow."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"image='{self.image}', "
            f"io_handler='{self.io_handler}')"
        )

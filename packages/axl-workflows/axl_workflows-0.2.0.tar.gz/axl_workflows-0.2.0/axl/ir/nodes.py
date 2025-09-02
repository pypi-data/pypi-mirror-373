"""
IR Node and Edge representations for AXL Workflows.

This module contains the IRNode and IREdge classes that represent
individual steps and their dependencies in the workflow.
"""

from typing import Any


class IRNode:
    """
    Intermediate representation of a workflow node (step).

    This class represents a single step in the workflow with its
    configuration, inputs, outputs, and metadata.
    """

    def __init__(
        self,
        name: str,
        step_config: dict[str, Any],
        inputs: list[str] | None = None,
        outputs: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize IR node.

        Args:
            name: Step name
            step_config: Step configuration (io_handler, resources, etc.)
            inputs: List of input step names
            outputs: List of output names
            metadata: Additional node metadata
        """
        self.name = name
        self.step_config = step_config
        self.inputs = inputs or []
        self.outputs = outputs or [name]  # Default output is step name
        self.metadata = metadata or {}

    def get_io_handler(self) -> str:
        """
        Get the IO handler for this step.

        Returns:
            IO handler name (defaults to workflow default)
        """
        return str(self.step_config.get("io_handler", "default"))

    def get_resources(self) -> dict[str, Any]:
        """
        Get resource requirements for this step.

        Returns:
            Resource configuration
        """
        return dict(self.step_config.get("resources", {}))

    def get_retries(self) -> int | None:
        """
        Get retry configuration for this step.

        Returns:
            Number of retries or None
        """
        retries = self.step_config.get("retries")
        return int(retries) if retries is not None else None

    def get_env(self) -> dict[str, str]:
        """
        Get environment variables for this step.

        Returns:
            Environment variables
        """
        env = self.step_config.get("env", {})
        return {str(k): str(v) for k, v in env.items()}

    def get_packages(self) -> list[str]:
        """Get per-step package requirements, if any."""
        pkgs = self.step_config.get("packages", [])
        return [str(p) for p in pkgs]

    def get_input_mode(self) -> str | dict[str, str] | None:
        """
        Get input mode configuration for this step.

        Returns:
            Input mode configuration
        """
        return self.step_config.get("input_mode")

    def __repr__(self) -> str:
        """String representation of the IR node."""
        return f"IRNode(name='{self.name}', inputs={len(self.inputs)}, outputs={len(self.outputs)})"


class IREdge:
    """
    Intermediate representation of a workflow edge (dependency).

    This class represents a dependency between two steps in the workflow,
    specifying how data flows from one step to another.
    """

    def __init__(
        self,
        source: str,
        target: str,
        source_output: str | None = None,
        target_input: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize IR edge.

        Args:
            source: Source step name
            target: Target step name
            source_output: Output name from source step
            target_input: Input name for target step
            metadata: Additional edge metadata
        """
        self.source = source
        self.target = target
        self.source_output = source_output or source
        self.target_input = target_input or source_output or source
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        """String representation of the IR edge."""
        return f"IREdge({self.source} -> {self.target})"

    def __eq__(self, other: object) -> bool:
        """Check if two edges are equal."""
        if not isinstance(other, IREdge):
            return False
        return (
            self.source == other.source
            and self.target == other.target
            and self.source_output == other.source_output
            and self.target_input == other.target_input
        )

    def __hash__(self) -> int:
        """Hash for edge comparison."""
        return hash((self.source, self.target, self.source_output, self.target_input))

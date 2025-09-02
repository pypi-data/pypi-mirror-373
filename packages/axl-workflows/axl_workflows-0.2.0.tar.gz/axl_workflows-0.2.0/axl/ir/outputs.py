"""
Output references for AXL Workflows IR.

This module contains the OutputRef class for representing step outputs
during symbolic execution and IR building.
"""

from typing import Any


class OutputRef:
    """
    Reference to a step output for IR building.

    This class represents the output of a step during symbolic execution,
    allowing the IR builder to construct the workflow DAG without
    actually executing the steps.
    """

    def __init__(self, step_name: str, inputs: list["OutputRef"] | None = None) -> None:
        """
        Initialize an output reference.

        Args:
            step_name: Name of the step that produces this output
            inputs: List of input references this step depends on
        """
        self.step_name = step_name
        self.inputs = inputs or []
        self.metadata: dict[str, Any] = {}

    def __repr__(self) -> str:
        """String representation of the output reference."""
        return f"OutputRef({self.step_name})"

    def __str__(self) -> str:
        """String representation for user display."""
        return f"<output from {self.step_name}>"

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to this output reference.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata from this output reference.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def __call__(self, *args: Any, **kwargs: Any) -> "OutputRef":
        """Create an OutputRef with inputs from arguments."""
        inputs = []

        for arg in args:
            if isinstance(arg, OutputRef):
                inputs.append(arg)
            else:
                raise ValueError(
                    f"Step arguments must be OutputRef instances, got {type(arg)}"
                )

        for arg in kwargs.values():
            if isinstance(arg, OutputRef):
                inputs.append(arg)
            else:
                raise ValueError(
                    f"Step arguments must be OutputRef instances, got {type(arg)}"
                )

        self.inputs = inputs
        return self


def validate_step_args(
    step_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> None:
    """Validate that all step arguments are OutputRef instances."""
    if not args and not kwargs:
        return

    for i, arg in enumerate(args[1:], start=1):
        if not isinstance(arg, OutputRef):
            raise ValueError(
                f"Step '{step_name}' argument {i} must be an OutputRef, got {type(arg)}"
            )

    for name, arg in kwargs.items():
        if not isinstance(arg, OutputRef):
            raise ValueError(
                f"Step '{step_name}' keyword argument '{name}' must be an OutputRef, got {type(arg)}"
            )

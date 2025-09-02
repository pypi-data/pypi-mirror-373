"""
Decorators for AXL Workflows.

This module contains the @step decorator for defining workflow steps.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, Protocol, TypedDict, cast, runtime_checkable

from ..ir import validate_step_args


class StepConfig(TypedDict, total=False):
    """Typed configuration attached to step functions at decoration time."""

    io_handler: str
    input_mode: str | dict[str, str]
    resources: dict[str, Any]
    retries: int
    env: dict[str, str]
    packages: list[str]


@runtime_checkable
class StepFunction(Protocol):
    """Protocol for functions decorated with @step."""

    _is_step: bool
    _step_config: StepConfig
    _original_func: Callable[..., Any]

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


def step(
    *,
    io_handler: str | None = None,
    input_mode: str | dict[str, str] | None = None,
    resources: dict[str, Any] | None = None,
    retries: int | None = None,
    env: dict[str, str] | None = None,
    packages: list[str] | None = None,
) -> Callable[[Callable[..., Any]], StepFunction]:
    """
    Decorator for defining workflow steps with configuration.

    Args:
        io_handler: IO handler override for this step
        input_mode: Input mode override ("object", "path", or {arg: mode})
        resources: Resource requirements (CPU, memory, etc.)
        retries: Number of retries for this step
        env: Environment variables for this step

    Returns:
        Decorated step function

    Example:
        @step(io_handler="parquet", retries=3)
        def preprocess(self, data):
            return processed_data
    """

    def decorator(func: Callable[..., Any]) -> StepFunction:
        step_cfg: StepConfig = {}
        if io_handler is not None:
            step_cfg["io_handler"] = io_handler
        if input_mode is not None:
            step_cfg["input_mode"] = input_mode
        if resources is not None:
            step_cfg["resources"] = resources
        if retries is not None:
            step_cfg["retries"] = retries
        if env is not None:
            step_cfg["env"] = env
        if packages is not None:
            step_cfg["packages"] = list(packages)

        cast(Any, func)._is_step = True
        cast(Any, func)._step_config = step_cfg

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            validate_step_args(func.__name__, args, kwargs)
            return func(*args, **kwargs)

        cast(Any, wrapper)._is_step = True
        cast(Any, wrapper)._step_config = step_cfg
        cast(Any, wrapper)._original_func = func

        return cast(StepFunction, wrapper)

    return decorator

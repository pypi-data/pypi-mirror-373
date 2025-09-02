"""
Intermediate Representation (IR) for AXL Workflows.

This module contains the backend-agnostic DAG model.
"""

from .builder import (
    build_ir,
    get_step_config,
    get_step_config_from_output_ref,
    get_workflow_info,
    validate_workflow,
)
from .nodes import IREdge, IRNode
from .outputs import OutputRef, validate_step_args
from .workflow import IRWorkflow

__all__ = [
    "IRWorkflow",
    "IRNode",
    "IREdge",
    "OutputRef",
    "validate_step_args",
    "build_ir",
    "get_workflow_info",
    "validate_workflow",
    "get_step_config",
    "get_step_config_from_output_ref",
]

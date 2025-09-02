"""
IR Builder for AXL Workflows.

This module contains the IR builder that converts workflow classes
to IR (Intermediate Representation) using graph traversal.
"""

from typing import Any

from .nodes import IREdge, IRNode
from .outputs import OutputRef
from .workflow import IRWorkflow


def build_ir(workflow_class: type) -> IRWorkflow:
    """
    Build IR from workflow class using graph traversal.

    Args:
        workflow_class: Workflow class to build IR from

    Returns:
        IRWorkflow representation

    Raises:
        ValueError: If workflow is invalid
    """
    # Create workflow instance
    wf = workflow_class()

    # Get the final output from graph()
    final_output = wf.graph()

    if not isinstance(final_output, OutputRef):
        raise ValueError(
            f"Workflow graph() must return an OutputRef, got {type(final_output).__name__}"
        )

    # Traverse the graph to build nodes and edges
    nodes: list[IRNode] = []
    edges: list[IREdge] = []
    visited: set[str] = set()

    # Iterative DFS using a stack to avoid recursion depth issues
    stack: list[OutputRef] = [final_output]
    while stack:
        ref = stack.pop()
        if ref.step_name in visited:
            continue
        visited.add(ref.step_name)

        # Get step configuration
        step_config = get_step_config_from_output_ref(ref, wf)

        # Create node
        node = IRNode(
            name=ref.step_name,
            step_config=step_config,
            inputs=[input_ref.step_name for input_ref in ref.inputs],
            outputs=[ref.step_name],
        )
        nodes.append(node)

        # Create edges from inputs and push inputs to stack
        for input_ref in ref.inputs:
            edges.append(
                IREdge(
                    source=input_ref.step_name,
                    target=ref.step_name,
                    source_output=input_ref.step_name,
                    target_input=input_ref.step_name,
                )
            )
            stack.append(input_ref)

    # Create IR workflow
    ir_workflow = IRWorkflow(
        name=wf.name,
        image=wf.image,
        io_handler=wf.io_handler,
        nodes=nodes,
        edges=edges,
        metadata={
            "workflow_module": workflow_class.__module__,
            "workflow_class": workflow_class.__name__,
        },
    )

    # Validate the IR
    ir_workflow.validate()

    return ir_workflow


def get_step_config(wf: Any, step_name: str) -> dict[str, Any]:
    """
    Get step configuration from workflow instance.

    Args:
        wf: Workflow instance
        step_name: Name of the step

    Returns:
        Step configuration dictionary
    """
    # Get the step method
    step_method = getattr(wf, step_name, None)

    if step_method is None:
        raise ValueError(f"Step '{step_name}' not found in workflow")

    # Get step configuration from decorator
    if hasattr(step_method, "_step_config"):
        config = dict(step_method._step_config.copy())
        # Override None values with workflow defaults
        if config.get("io_handler") is None:
            config["io_handler"] = wf.io_handler
        return config

    # Return default configuration
    return {
        "io_handler": wf.io_handler,
        "input_mode": None,
        "resources": {},
        "retries": None,
        "env": {},
    }


def get_step_config_from_output_ref(output_ref: OutputRef, wf: Any) -> dict[str, Any]:
    """
    Get step configuration from OutputRef metadata.

    Args:
        output_ref: OutputRef instance
        wf: Workflow instance

    Returns:
        Step configuration dictionary
    """
    # Check if step config is stored in metadata
    if "step_config" in output_ref.metadata:
        config = dict(output_ref.metadata["step_config"].copy())
        # Override None values with workflow defaults
        if config.get("io_handler") is None:
            config["io_handler"] = wf.io_handler
        return config

    # Fall back to getting from workflow
    return get_step_config(wf, output_ref.step_name)


def validate_workflow(workflow_class: type) -> None:
    """
    Validate a workflow class without building IR.

    Args:
        workflow_class: Workflow class to validate

    Raises:
        ValueError: If workflow is invalid
    """
    try:
        build_ir(workflow_class)
    except Exception as e:
        raise ValueError(f"Workflow validation failed: {e}") from e


def get_workflow_info(workflow_class: type) -> dict[str, Any]:
    """
    Get basic information about a workflow without building full IR.

    Args:
        workflow_class: Workflow class to analyze

    Returns:
        Dictionary with workflow information
    """
    wf = workflow_class()
    final_output = wf.graph()

    if not isinstance(final_output, OutputRef):
        raise ValueError(
            f"Workflow graph() must return an OutputRef, got {type(final_output).__name__}"
        )

    # Count nodes by traversing
    visited = set()

    def count_nodes(ref: OutputRef) -> None:
        if ref.step_name in visited:
            return
        visited.add(ref.step_name)
        for input_ref in ref.inputs:
            count_nodes(input_ref)

    count_nodes(final_output)

    return {
        "name": wf.name,
        "image": wf.image,
        "io_handler": wf.io_handler,
        "step_count": len(visited),
        "steps": list(visited),
        "final_step": final_output.step_name,
    }

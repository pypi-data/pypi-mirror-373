"""
Local runtime engine for AXL Workflows.

This module implements a local runtime that executes workflows
by resolving dependencies and running steps in topological order.
"""

import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from ..io import registry, storage_registry
from ..ir import IRNode, IRWorkflow


class LocalRuntime:
    """Local runtime engine for executing workflows."""

    def __init__(
        self,
        workspace_path: str | Path = "axl_workspace",
        storage_backend: str = "local",
    ) -> None:
        """
        Initialize the local runtime.

        Args:
            workspace_path: Path to workspace directory for artifacts
            storage_backend: Storage backend type ('local' or 'memory')
        """
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        # Initialize storage backend
        if storage_backend == "local":
            self.storage = storage_registry.get(
                "local", base_path=str(self.workspace_path)
            )
        elif storage_backend == "memory":
            self.storage = storage_registry.get("memory")
        else:
            raise ValueError(f"Unknown storage backend: {storage_backend}")

        # Track execution state
        self.executed_steps: set[str] = set()
        self.step_outputs: dict[str, Any] = {}

    def execute_workflow(
        self,
        ir_workflow: IRWorkflow,
        workflow_instance: Any,
        parameters: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a workflow from its IR representation.

        Args:
            ir_workflow: The IR representation of the workflow
            workflow_instance: Instance of the workflow class
            parameters: Optional parameters to pass to the workflow

        Returns:
            The output of the final step

        Raises:
            RuntimeError: If execution fails
        """
        try:
            # Log workflow start
            workflow_instance.log.info("Starting workflow execution")
            if workflow_instance.workflow_params:
                workflow_instance.log.info(
                    "Parameters", params=workflow_instance.workflow_params
                )

            # Validate the IR first
            ir_workflow.validate()

            # Resolve execution order
            execution_order = self._topological_sort(ir_workflow)
            workflow_instance.log.info(
                f"Execution order: {' -> '.join(execution_order)}"
            )

            # Track total execution time
            workflow_start_time = time.time()

            # Execute steps in order
            for step_name in execution_order:
                self._execute_step(step_name, ir_workflow, workflow_instance)

            # Find the final step (step with no dependents)
            final_step = self._find_final_step(ir_workflow)
            result = self.step_outputs.get(final_step)

            # Log workflow completion
            total_duration = time.time() - workflow_start_time
            workflow_instance.log.info(
                "Workflow completed successfully", duration=f"{total_duration:.3f}s"
            )

            return result

        except Exception as e:
            workflow_instance.log.error("Workflow execution failed", error=str(e))
            raise RuntimeError(f"Workflow execution failed: {e}") from e

    def _topological_sort(self, ir_workflow: IRWorkflow) -> list[str]:
        """
        Perform topological sort to determine execution order.

        Args:
            ir_workflow: The IR workflow

        Returns:
            List of step names in execution order

        Raises:
            ValueError: If the workflow has cycles
        """
        # Build adjacency list and in-degree count
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        all_nodes = {node.name for node in ir_workflow.nodes}

        # Initialize all nodes with in-degree 0
        for node_name in all_nodes:
            in_degree[node_name] = 0

        # Build the graph
        for edge in ir_workflow.edges:
            graph[edge.source].append(edge.target)
            in_degree[edge.target] += 1

        # Kahn's algorithm for topological sorting
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            # Reduce in-degree for all neighbors
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(result) != len(all_nodes):
            raise ValueError("Workflow contains cycles and cannot be executed")

        return result

    def _execute_step(
        self, step_name: str, ir_workflow: IRWorkflow, workflow_instance: Any
    ) -> None:
        """
        Execute a single step.

        Args:
            step_name: Name of the step to execute
            ir_workflow: The IR workflow
            workflow_instance: Instance of the workflow class
        """
        if step_name in self.executed_steps:
            return  # Already executed

        # Set step context in logger
        workflow_instance.log.set_step_context(step_name)

        # Get the step node
        node = ir_workflow.get_node(step_name)
        if node is None:
            raise ValueError(f"Step '{step_name}' not found in workflow")

        # Log step start
        dependencies = node.inputs if node.inputs else []
        workflow_instance.log.info("Step started", dependencies=dependencies)

        # Track step execution time
        step_start_time = time.time()

        # Load input artifacts
        inputs = self._load_step_inputs(node, ir_workflow, workflow_instance)

        # Get the actual step method (bypass the __getattribute__ interception)
        step_method = object.__getattribute__(workflow_instance, step_name)

        # For runtime execution, use the original function without validation
        if hasattr(step_method, "_original_func"):
            step_method = step_method._original_func

        try:
            # Execute the step
            if inputs:
                result = step_method(workflow_instance, *inputs)
            else:
                result = step_method(workflow_instance)

            # Save the output artifact
            self._save_step_output(step_name, result, node, workflow_instance)

            # Mark as executed
            self.executed_steps.add(step_name)
            self.step_outputs[step_name] = result

            # Log step completion
            step_duration = time.time() - step_start_time
            output_size = len(str(result)) if result is not None else 0
            workflow_instance.log.info(
                "Step completed",
                duration=f"{step_duration:.3f}s",
                output_size=f"{output_size} chars",
            )

        except Exception as e:
            # Log step failure
            workflow_instance.log.error("Step failed", error=str(e))
            raise RuntimeError(f"Step '{step_name}' failed: {e}") from e
        finally:
            # Clear step context
            workflow_instance.log.clear_step_context()

    def _load_step_inputs(
        self, node: IRNode, ir_workflow: IRWorkflow, workflow_instance: Any
    ) -> list[Any]:
        """
        Load input artifacts for a step.

        Args:
            node: The step node
            ir_workflow: The IR workflow
            workflow_instance: Instance of the workflow class

        Returns:
            List of loaded input objects
        """
        inputs = []

        for input_step_name in node.inputs:
            # Find the input node to get its IO handler
            input_node = ir_workflow.get_node(input_step_name)
            if input_node is None:
                raise ValueError(f"Input step '{input_step_name}' not found")

            # Get the IO handler
            handler_name = input_node.get_io_handler()
            # If no specific handler, use workflow default
            if handler_name == "default" or handler_name is None:
                handler_name = workflow_instance.io_handler
            io_handler = registry.get(handler_name)

            # Load the artifact
            artifact_path = f"{input_step_name}_output"

            if self.storage.exists(artifact_path):
                # Log artifact load
                workflow_instance.log.debug(
                    "Loading artifact", step=input_step_name, handler=handler_name
                )

                data = self.storage.load(artifact_path)
                obj = io_handler.loads(data)
                inputs.append(obj)

                # Log artifact loaded
                data_size = len(data)
                workflow_instance.log.debug(
                    "Artifact loaded",
                    step=input_step_name,
                    size=f"{data_size} bytes",
                    handler=handler_name,
                )
            else:
                raise RuntimeError(f"Artifact for step '{input_step_name}' not found")

        return inputs

    def _save_step_output(
        self, step_name: str, result: Any, node: IRNode, workflow_instance: Any
    ) -> None:
        """
        Save step output as an artifact.

        Args:
            step_name: Name of the step
            result: The step output
            node: The step node
            workflow_instance: Instance of the workflow class
        """
        # Get the IO handler
        handler_name = node.get_io_handler()
        # If no specific handler, use workflow default
        if handler_name == "default" or handler_name is None:
            handler_name = workflow_instance.io_handler
        io_handler = registry.get(handler_name)

        # Log artifact save
        workflow_instance.log.debug("Saving artifact", handler=handler_name)

        # Serialize and save
        data = io_handler.dumps(result)
        artifact_path = f"{step_name}_output"
        self.storage.save(data, artifact_path)

        # Log artifact saved
        data_size = len(data)
        workflow_instance.log.debug(
            "Artifact saved",
            path=artifact_path,
            size=f"{data_size} bytes",
            handler=handler_name,
        )

    def _find_final_step(self, ir_workflow: IRWorkflow) -> str:
        """
        Find the final step (step with no dependents).

        Args:
            ir_workflow: The IR workflow

        Returns:
            Name of the final step
        """
        # Find steps that are not dependencies of any other step
        all_steps = {node.name for node in ir_workflow.nodes}
        dependency_steps = {edge.source for edge in ir_workflow.edges}

        final_steps = all_steps - dependency_steps

        if len(final_steps) == 1:
            return list(final_steps)[0]
        elif len(final_steps) == 0:
            raise ValueError("No final step found (circular dependency)")
        else:
            # If multiple final steps, return the last one in execution order
            execution_order = self._topological_sort(ir_workflow)
            for step in reversed(execution_order):
                if step in final_steps:
                    return step

            raise ValueError("Could not determine final step")

    def cleanup(self) -> None:
        """Clean up the runtime workspace."""
        self.executed_steps.clear()
        self.step_outputs.clear()

        # For in-memory storage, clear the storage
        if hasattr(self.storage, "clear"):
            self.storage.clear()

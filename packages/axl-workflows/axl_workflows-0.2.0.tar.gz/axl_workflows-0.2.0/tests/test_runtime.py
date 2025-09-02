"""Tests for runtime engines."""

import pytest

from axl import LocalRuntime, Workflow, step
from axl.ir import build_ir


class TestLocalRuntime:
    """Test LocalRuntime execution."""

    def test_simple_workflow_execution(self) -> None:
        """Test execution of a simple workflow."""

        class SimpleWorkflow(Workflow):
            name = "test-simple"

            @step()
            def load_data(self) -> str:
                return "test_data"

            @step()
            def process_data(self, data: str) -> str:
                return f"processed_{data}"

            def graph(self):
                data = self.load_data()
                return self.process_data(data)

        # Test the execution
        runtime = LocalRuntime(storage_backend="memory")
        workflow_instance = SimpleWorkflow()
        ir_workflow = build_ir(SimpleWorkflow)

        result = runtime.execute_workflow(ir_workflow, workflow_instance)

        assert result == "processed_test_data"
        assert "load_data" in runtime.executed_steps
        assert "process_data" in runtime.executed_steps

    def test_workflow_with_no_dependencies(self) -> None:
        """Test execution of a workflow with a single step."""

        class SingleStepWorkflow(Workflow):
            name = "test-single"

            @step()
            def single_step(self) -> int:
                return 42

            def graph(self):
                return self.single_step()

        # Test the execution
        runtime = LocalRuntime(storage_backend="memory")
        workflow_instance = SingleStepWorkflow()
        ir_workflow = build_ir(SingleStepWorkflow)

        result = runtime.execute_workflow(ir_workflow, workflow_instance)

        assert result == 42
        assert "single_step" in runtime.executed_steps

    def test_complex_workflow_execution(self) -> None:
        """Test execution of a more complex workflow with multiple dependencies."""

        class ComplexWorkflow(Workflow):
            name = "test-complex"

            @step()
            def step_a(self) -> int:
                return 10

            @step()
            def step_b(self) -> int:
                return 20

            @step()
            def step_c(self, a: int, b: int) -> int:
                return a + b

            @step()
            def step_d(self, c: int) -> int:
                return c * 2

            def graph(self):
                a = self.step_a()
                b = self.step_b()
                c = self.step_c(a, b)
                return self.step_d(c)

        # Test the execution
        runtime = LocalRuntime(storage_backend="memory")
        workflow_instance = ComplexWorkflow()
        ir_workflow = build_ir(ComplexWorkflow)

        result = runtime.execute_workflow(ir_workflow, workflow_instance)

        assert result == 60  # (10 + 20) * 2
        assert len(runtime.executed_steps) == 4
        assert all(
            step in runtime.executed_steps
            for step in ["step_a", "step_b", "step_c", "step_d"]
        )

    def test_runtime_with_local_storage(self) -> None:
        """Test runtime with local file storage."""

        class TestWorkflow(Workflow):
            name = "test-local-storage"

            @step()
            def create_data(self) -> dict:
                return {"key": "value", "number": 123}

            @step()
            def process_dict(self, data: dict) -> str:
                return f"{data['key']}_{data['number']}"

            def graph(self):
                data = self.create_data()
                return self.process_dict(data)

        # Test with local storage (will create temp directory)
        runtime = LocalRuntime(workspace_path="test_workspace", storage_backend="local")
        workflow_instance = TestWorkflow()
        ir_workflow = build_ir(TestWorkflow)

        try:
            result = runtime.execute_workflow(ir_workflow, workflow_instance)
            assert result == "value_123"
        finally:
            # Cleanup
            import shutil

            shutil.rmtree("test_workspace", ignore_errors=True)

    def test_runtime_error_handling(self) -> None:
        """Test error handling in runtime execution."""

        class ErrorWorkflow(Workflow):
            name = "test-error"

            @step()
            def failing_step(self) -> str:
                raise ValueError("This step always fails")

            def graph(self):
                return self.failing_step()

        runtime = LocalRuntime(storage_backend="memory")
        workflow_instance = ErrorWorkflow()
        ir_workflow = build_ir(ErrorWorkflow)

        with pytest.raises(RuntimeError, match="Workflow execution failed"):
            runtime.execute_workflow(ir_workflow, workflow_instance)

    def test_topological_sort(self) -> None:
        """Test topological sorting of workflow steps."""

        class TopoWorkflow(Workflow):
            name = "test-topo"

            @step()
            def step_1(self) -> str:
                return "1"

            @step()
            def step_2(self, input_1: str) -> str:
                return input_1 + "2"

            @step()
            def step_3(self, input_2: str) -> str:
                return input_2 + "3"

            def graph(self):
                result_1 = self.step_1()
                result_2 = self.step_2(result_1)
                return self.step_3(result_2)

        runtime = LocalRuntime(storage_backend="memory")
        ir_workflow = build_ir(TopoWorkflow)

        # Test topological sorting
        execution_order = runtime._topological_sort(ir_workflow)

        assert execution_order == ["step_1", "step_2", "step_3"]

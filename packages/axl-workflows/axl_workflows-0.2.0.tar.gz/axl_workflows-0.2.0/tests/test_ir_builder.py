"""
Tests for IR builder functionality.
"""

import pytest

from axl.core import Workflow, step
from axl.ir import (
    IREdge,
    IRNode,
    IRWorkflow,
    build_ir,
    get_step_config,
    get_step_config_from_output_ref,
    get_workflow_info,
    validate_workflow,
)


class TestIRBuilder:
    """Test cases for IR builder functionality."""

    def test_build_ir_simple_workflow(self) -> None:
        """Test building IR from a simple workflow."""

        class SimpleWorkflow(Workflow):
            name = "test-workflow"

            @step()
            def step1(self):
                return "data"

            @step()
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        ir = build_ir(SimpleWorkflow)

        assert ir.name == "test-workflow"
        assert ir.image == "ghcr.io/axl-workflows/runner:latest"
        assert ir.io_handler == "pickle"
        assert len(ir.nodes) == 2
        assert len(ir.edges) == 1

        step1_node = ir.get_node("step1")
        step2_node = ir.get_node("step2")
        assert step1_node is not None
        assert step2_node is not None
        assert step1_node.inputs == []
        assert step2_node.inputs == ["step1"]

        edge = ir.edges[0]
        assert edge.source == "step1"
        assert edge.target == "step2"

    def test_build_ir_complex_workflow(self) -> None:
        """Test building IR from a complex workflow with multiple dependencies."""

        class ComplexWorkflow(Workflow):
            name = "complex-workflow"

            @step()
            def load_data(self):
                return "raw_data"

            @step()
            def preprocess(self, data):
                return "processed_data"

            @step()
            def train(self, data):
                return "model"

            @step()
            def evaluate(self, model, data):
                return "score"

            def graph(self):
                data = self.load_data()
                processed = self.preprocess(data)
                model = self.train(processed)
                return self.evaluate(model, processed)

        ir = build_ir(ComplexWorkflow)

        assert ir.name == "complex-workflow"
        assert len(ir.nodes) == 4
        assert len(ir.edges) == 4

        load_node = ir.get_node("load_data")
        preprocess_node = ir.get_node("preprocess")
        train_node = ir.get_node("train")
        evaluate_node = ir.get_node("evaluate")

        assert load_node.inputs == []
        assert preprocess_node.inputs == ["load_data"]
        assert train_node.inputs == ["preprocess"]
        assert evaluate_node.inputs == ["train", "preprocess"]

        edge_sources = {edge.source for edge in ir.edges}
        edge_targets = {edge.target for edge in ir.edges}
        assert edge_sources == {"load_data", "preprocess", "train"}
        assert edge_targets == {"preprocess", "train", "evaluate"}

    def test_build_ir_with_step_config(self) -> None:
        """Test building IR with step configuration."""

        class ConfigWorkflow(Workflow):
            name = "config-workflow"

            @step(io_handler="parquet", retries=3, resources={"cpu": "2"})
            def step1(self):
                return "data"

            @step(io_handler="numpy", env={"DEBUG": "true"})
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        ir = build_ir(ConfigWorkflow)

        step1_node = ir.get_node("step1")
        assert step1_node is not None
        step_config = step1_node.step_config

        assert step_config["io_handler"] == "parquet"
        assert step_config["retries"] == 3
        assert step_config["resources"] == {"cpu": "2"}

    def test_build_ir_validation(self) -> None:
        """Test that IR validation works correctly."""

        class ValidWorkflow(Workflow):
            name = "valid-workflow"

            @step()
            def step1(self):
                return "data"

            @step()
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        # Should not raise any exception
        validate_workflow(ValidWorkflow)

    def test_get_workflow_info(self) -> None:
        """Test getting workflow information."""

        class InfoWorkflow(Workflow):
            name = "info-workflow"

            @step()
            def step1(self):
                return "data"

            @step()
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        info = get_workflow_info(InfoWorkflow)

        assert info["name"] == "info-workflow"
        assert info["image"] == "ghcr.io/axl-workflows/runner:latest"
        assert info["io_handler"] == "pickle"
        assert info["step_count"] == 2
        assert "step1" in info["steps"]
        assert "step2" in info["steps"]
        assert info["final_step"] == "step2"

    def test_validate_workflow(self) -> None:
        """Test workflow validation function."""

        class ValidWorkflow(Workflow):
            name = "valid-workflow"

            @step()
            def step1(self):
                return "data"

            @step()
            def step2(self, data):
                return "result"

            def graph(self):
                return self.step2(self.step1())

        # Should not raise any exception
        validate_workflow(ValidWorkflow)

    def test_build_ir_invalid_graph_return(self) -> None:
        """Test that building IR fails with invalid graph return."""

        class InvalidWorkflow(Workflow):
            name = "invalid-workflow"

            @step()
            def step1(self):
                return "not_an_output_ref"

            def graph(self):
                return "invalid_direct_return"

        with pytest.raises(ValueError, match="must return an OutputRef"):
            build_ir(InvalidWorkflow)

    def test_build_ir_missing_step(self) -> None:
        """Test that building IR fails with missing step."""

        class MissingStepWorkflow(Workflow):
            name = "missing-step-workflow"

            @step()
            def step1(self):
                return "data"

            def graph(self):
                return self.step2(self.step1())

        with pytest.raises(AttributeError):
            build_ir(MissingStepWorkflow)

    def test_ir_workflow_validation_cycles(self) -> None:
        """Test that IR validation detects cycles."""
        ir = IRWorkflow(
            name="cyclic-workflow",
            image="test:latest",
            io_handler="pickle",
            nodes=[
                IRNode("step1", {}, inputs=["step2"]),
                IRNode("step2", {}, inputs=["step1"]),
            ],
            edges=[
                IREdge("step1", "step2"),
                IREdge("step2", "step1"),
            ],
        )

        # Should raise ValueError for cycles
        with pytest.raises(ValueError, match="contains cycles"):
            ir.validate()

    def test_ir_workflow_orphaned_nodes(self) -> None:
        """Test that IR workflow validation fails with orphaned nodes."""

        nodes = [
            IRNode("step1", {}),
            IRNode("step2", {}),
        ]
        edges = []

        ir = IRWorkflow("test", "image", "pickle", nodes, edges)

        with pytest.raises(ValueError, match="multiple nodes must have edges"):
            ir.validate()

    def test_ir_workflow_missing_dependencies(self) -> None:
        """Test that IR workflow validation fails with missing dependencies."""

        nodes = [
            IRNode("step1", {}),
            IRNode("step2", {}),
        ]
        edges = [
            IREdge("step1", "step2"),
            IREdge("step1", "missing_step"),
        ]

        ir = IRWorkflow("test", "image", "pickle", nodes, edges)

        with pytest.raises(ValueError, match="not found"):
            ir.validate()

    def test_get_step_config_missing_step(self) -> None:
        """Test get_step_config with missing step."""

        class TestWorkflow(Workflow):
            name = "test-workflow"

            @step()
            def step1(self):
                return "step1_output"

            def graph(self):
                return self.step1()

        wf = TestWorkflow()

        # Test with missing step
        with pytest.raises(
            ValueError, match="Step 'nonexistent' not found in workflow"
        ):
            get_step_config(wf, "nonexistent")

    def test_get_step_config_from_output_ref_with_metadata(self) -> None:
        """Test get_step_config_from_output_ref when metadata contains step_config."""

        class TestWorkflow(Workflow):
            name = "test-workflow"

            @step(io_handler="cloudpickle")
            def step1(self):
                return "data"

            def graph(self):
                return self.step1()

        wf = TestWorkflow()
        output_ref = wf.step1()
        output_ref.metadata["step_config"] = {"io_handler": "custom"}

        config = get_step_config_from_output_ref(output_ref, wf)
        assert config["io_handler"] == "custom"

    def test_get_step_config_from_output_ref_fallback(self) -> None:
        """Test get_step_config_from_output_ref fallback to workflow method."""

        class TestWorkflow(Workflow):
            name = "test-workflow"

            @step()
            def step1(self):
                return "data"

            def graph(self):
                return self.step1()

        wf = TestWorkflow()
        output_ref = wf.step1()

        config = get_step_config_from_output_ref(output_ref, wf)
        assert config["io_handler"] == "pickle"

    def test_validate_workflow_with_error(self) -> None:
        """Test validate_workflow when build_ir fails."""

        class TestWorkflow(Workflow):
            name = "test-workflow"

            @step()
            def step1(self):
                return "step1_output"

            def graph(self):
                return "not_an_output_ref"

        with pytest.raises(ValueError, match="Workflow validation failed"):
            validate_workflow(TestWorkflow)

    def test_get_workflow_info_with_invalid_graph_return(self) -> None:
        """Test get_workflow_info with invalid graph return type."""

        class TestWorkflow(Workflow):
            name = "test-workflow"

            @step()
            def step1(self):
                return "data"

            def graph(self):
                return "not_an_output_ref"

        with pytest.raises(ValueError, match="must return an OutputRef"):
            get_workflow_info(TestWorkflow)

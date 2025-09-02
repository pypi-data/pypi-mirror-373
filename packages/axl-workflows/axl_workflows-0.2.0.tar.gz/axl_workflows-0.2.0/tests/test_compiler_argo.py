"""
Tests for Argo compiler functionality.
"""

import json

from axl.compiler import ArgoCompiler
from axl.ir.nodes import IREdge, IRNode
from axl.ir.workflow import IRWorkflow


class TestArgoCompiler:
    """Test ArgoCompiler basic functionality."""

    def test_compiler_initialization(self):
        """Test ArgoCompiler can be initialized with IR workflow."""
        nodes = [
            IRNode("step1", {}),
            IRNode("step2", {}),
        ]
        edges = [
            IREdge("step1", "step2"),
        ]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, edges)

        compiler = ArgoCompiler(workflow)
        assert compiler.workflow == workflow
        assert compiler.templates == []
        assert compiler.tasks == []

    def test_metadata_generation(self):
        """Test workflow metadata generation."""
        nodes = [IRNode("step1", {})]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, [])
        compiler = ArgoCompiler(workflow)

        metadata = compiler._generate_metadata()
        assert metadata["name"] == "test-workflow"
        assert metadata["labels"]["axl-workflow"] == "true"
        assert metadata["labels"]["axl-version"] == "0.1.0"

    def test_template_generation(self):
        """Test basic template generation."""
        nodes = [
            IRNode("step1", {}),
            IRNode(
                "step2",
                {
                    "resources": {"cpu": "500m", "memory": "1Gi", "gpu": "1"},
                    "env": {"CUDA_VISIBLE_DEVICES": "0", "MODEL_PATH": "/models"},
                    "retries": 3,
                },
            ),
        ]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, [])
        compiler = ArgoCompiler(workflow)

        compiler._generate_templates()
        assert len(compiler.templates) == 2

        template1 = compiler.templates[0]
        assert template1["name"] == "step1"
        assert template1["container"]["image"] == "test-image"
        assert template1["container"]["command"] == ["python", "-m", "axl.runtime"]

        args1 = template1["container"]["args"]
        assert args1[0] == "--step"
        assert args1[1] == "step1"
        assert args1[2] == "--workflow-name"
        assert args1[3] == "test-workflow"
        assert args1[4] == "--io-handler"
        assert args1[5] == "pickle"

        env_vars1 = template1["container"]["env"]
        assert len(env_vars1) == 3  # AXL_WORKFLOW_NAME, AXL_STEP_NAME, AXL_IO_HANDLER
        env_names1 = [env["name"] for env in env_vars1]
        assert "AXL_WORKFLOW_NAME" in env_names1
        assert "AXL_STEP_NAME" in env_names1
        assert "AXL_IO_HANDLER" in env_names1

        resources1 = template1["container"]["resources"]
        assert resources1["requests"]["cpu"] == "100m"
        assert resources1["requests"]["memory"] == "64Mi"
        assert resources1["limits"]["cpu"] == "200m"
        assert resources1["limits"]["memory"] == "128Mi"

        template2 = compiler.templates[1]
        assert template2["name"] == "step2"

        resources2 = template2["container"]["resources"]
        assert resources2["requests"]["cpu"] == "500m"
        assert resources2["requests"]["memory"] == "1Gi"
        assert resources2["requests"]["nvidia.com/gpu"] == "1"
        assert resources2["limits"]["cpu"] == "500m"
        assert resources2["limits"]["memory"] == "1Gi"
        assert resources2["limits"]["nvidia.com/gpu"] == "1"

        env_vars2 = template2["container"]["env"]
        env_dict2 = {env["name"]: env["value"] for env in env_vars2}
        assert env_dict2["CUDA_VISIBLE_DEVICES"] == "0"
        assert env_dict2["MODEL_PATH"] == "/models"
        assert env_dict2["AXL_WORKFLOW_NAME"] == "test-workflow"
        assert env_dict2["AXL_STEP_NAME"] == "step2"

        assert "retryStrategy" in template2
        retry_strategy = template2["retryStrategy"]
        assert retry_strategy["limit"] == 3
        assert retry_strategy["retryPolicy"] == "Always"
        assert retry_strategy["backoff"]["duration"] == "10s"
        assert retry_strategy["backoff"]["factor"] == 2
        assert retry_strategy["backoff"]["maxDuration"] == "5m"

    def test_dag_generation(self):
        """Test DAG task generation."""
        nodes = [
            IRNode("step1", {}),
            IRNode("step2", {}),
            IRNode("step3", {}),
        ]
        edges = [
            IREdge("step1", "step2"),
            IREdge("step2", "step3"),
        ]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, edges)
        compiler = ArgoCompiler(workflow)

        compiler._generate_dag()
        assert len(compiler.tasks) == 3

        task1 = compiler.tasks[0]
        assert task1["name"] == "step1"
        assert task1["template"] == "step1"
        assert "dependencies" not in task1  # No dependencies

        task2 = compiler.tasks[1]
        assert task2["name"] == "step2"
        assert task2["template"] == "step2"
        assert task2["dependencies"] == ["step1"]

        task3 = compiler.tasks[2]
        assert task3["name"] == "step3"
        assert task3["template"] == "step3"
        assert task3["dependencies"] == ["step2"]

    def test_compile_basic_structure(self):
        """Test basic compilation structure."""
        nodes = [IRNode("step1", {})]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, [])
        compiler = ArgoCompiler(workflow)

        result = compiler.compile()

        assert result["apiVersion"] == "argoproj.io/v1alpha1"
        assert result["kind"] == "Workflow"
        assert "metadata" in result
        assert "spec" in result

        metadata = result["metadata"]
        assert metadata["name"] == "test-workflow"

        spec = result["spec"]
        assert "templates" in spec
        # With entrypoint + main-dag template
        assert spec["entrypoint"] == "main-dag"
        main = next(t for t in spec["templates"] if t.get("name") == "main-dag")
        assert "dag" in main and "tasks" in main["dag"]

        templates = [t for t in spec["templates"] if t.get("name") != "main-dag"]
        assert len(templates) == 1
        assert templates[0]["name"] == "step1"

        tasks = main["dag"]["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["name"] == "step1"

    def test_to_yaml_output(self):
        """Test YAML string generation."""
        nodes = [IRNode("step1", {})]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, [])
        compiler = ArgoCompiler(workflow)

        yaml_str = compiler.to_yaml()

        assert "apiVersion: argoproj.io/v1alpha1" in yaml_str
        assert "kind: Workflow" in yaml_str
        assert "name: test-workflow" in yaml_str
        assert "name: step1" in yaml_str

    def test_step_args_generation(self):
        """Test step argument generation."""
        nodes = [
            IRNode("step1", {}),
            IRNode("step2", {"retries": 2, "io_handler": "cloudpickle"}),
        ]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, [])
        compiler = ArgoCompiler(workflow)

        args1 = compiler._generate_step_args(nodes[0])
        assert args1[0] == "--step"
        assert args1[1] == "step1"
        assert args1[2] == "--workflow-name"
        assert args1[3] == "test-workflow"
        assert args1[4] == "--io-handler"
        assert args1[5] == "pickle"
        assert args1[6] == "--io-manifest"
        manifest1 = json.loads(args1[7])
        assert manifest1["step_name"] == "step1"
        assert manifest1["io_handler"] == "pickle"

        args2 = compiler._generate_step_args(nodes[1])
        assert args2[0] == "--step"
        assert args2[1] == "step2"
        assert args2[2] == "--workflow-name"
        assert args2[3] == "test-workflow"
        assert args2[4] == "--io-handler"
        assert args2[5] == "cloudpickle"
        assert args2[6] == "--retries"
        assert args2[7] == "2"
        assert args2[8] == "--io-manifest"
        manifest2 = json.loads(args2[9])
        assert manifest2["step_name"] == "step2"
        assert manifest2["io_handler"] == "cloudpickle"

    def test_io_manifest_generation(self):
        """Test IO manifest generation."""
        nodes = [
            IRNode("step1", {"io_handler": "pickle"}),
            IRNode("step2", {"io_handler": "json"}),
        ]
        edges = [IREdge("step1", "step2")]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, edges)
        compiler = ArgoCompiler(workflow)

        manifest = compiler._generate_io_manifest(nodes[1])
        manifest_dict = json.loads(manifest)

        assert manifest_dict["step_name"] == "step2"
        assert manifest_dict["io_handler"] == "json"
        assert manifest_dict["file_extension"] == ".json"
        assert len(manifest_dict["inputs"]) == 1
        assert manifest_dict["inputs"][0]["name"] == "step1"
        assert manifest_dict["inputs"][0]["source_step"] == "step1"
        assert manifest_dict["inputs"][0]["io_handler"] == "pickle"
        assert len(manifest_dict["outputs"]) == 1
        assert manifest_dict["outputs"][0]["name"] == "step2"

    def test_file_extension_mapping(self):
        """Test file extension mapping for different IO handlers."""
        nodes = [IRNode("step1", {})]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, [])
        compiler = ArgoCompiler(workflow)

        extensions = {
            "pickle": ".pkl",
            "cloudpickle": ".cpkl",
            "json": ".json",
            "yaml": ".yaml",
            "parquet": ".parquet",
            "numpy": ".npy",
            "torch": ".pt",
            "unknown": ".obj",
        }

        for io_handler, expected_ext in extensions.items():
            ext = compiler._get_file_extension(io_handler)
            assert ext == expected_ext

    def test_artifact_generation(self):
        """Test artifact input/output generation."""
        nodes = [
            IRNode("step1", {"io_handler": "pickle"}),
            IRNode("step2", {"io_handler": "json"}),
        ]
        edges = [IREdge("step1", "step2")]
        workflow = IRWorkflow("test-workflow", "test-image", "pickle", nodes, edges)
        compiler = ArgoCompiler(workflow)

        inputs = compiler._generate_artifact_inputs(nodes[1])
        assert len(inputs) == 1
        assert inputs[0]["name"] == "step1"
        assert inputs[0]["path"] == "/tmp/inputs/step1.pkl"

        outputs = compiler._generate_artifact_outputs(nodes[0])
        assert len(outputs) == 1
        assert outputs[0]["name"] == "step1"
        assert outputs[0]["path"] == "/tmp/outputs/step1.pkl"

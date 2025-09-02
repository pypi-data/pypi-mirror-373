"""
Argo Workflow compiler for AXL Workflows.

This module contains the ArgoCompiler class that converts IR workflows
to Argo Workflow YAML for execution on Kubernetes/Kubeflow.
"""

from typing import Any

from ..ir.workflow import IRWorkflow


class ArgoCompiler:
    """
    Compiler that converts IR workflows to Argo Workflow YAML.

    This compiler generates Argo Workflow YAML that is compatible with
    Kubeflow Pipelines and can be executed on Kubernetes clusters.
    """

    def __init__(self, workflow: IRWorkflow) -> None:
        """
        Initialize Argo compiler with IR workflow.

        Args:
            workflow: IR workflow to compile
        """
        self.workflow = workflow
        self.templates: list[dict[str, Any]] = []
        self.tasks: list[dict[str, Any]] = []

    def compile(self) -> dict[str, Any]:
        """
        Compile IR workflow to Argo YAML structure.

        Returns:
            Dictionary representing Argo Workflow YAML
        """
        return {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": self._generate_metadata(),
            "spec": self._generate_spec(),
        }

    def _generate_metadata(self) -> dict[str, Any]:
        """
        Generate workflow metadata.

        Returns:
            Metadata dictionary for Argo Workflow
        """
        return {
            "name": self.workflow.name,
            "labels": {
                "axl-workflow": "true",
                "axl-version": "0.1.0",
            },
        }

    def _generate_spec(self) -> dict[str, Any]:
        """
        Generate workflow spec with templates and DAG.

        Returns:
            Spec dictionary containing templates and DAG structure
        """
        self.templates = []
        self.tasks = []

        self._generate_templates()
        self._generate_dag()

        dag_template = {
            "name": "main-dag",
            "dag": {
                "tasks": self.tasks,
            },
        }

        all_templates = [dag_template] + self.templates

        return {
            "entrypoint": "main-dag",
            "serviceAccountName": "workflow-runner",
            "templates": all_templates,
        }

    def _generate_templates(self) -> None:
        """Generate Argo templates for each workflow step."""
        for node in self.workflow.nodes:
            template = self._create_template(node)
            self.templates.append(template)

    def _create_template(self, node: Any) -> dict[str, Any]:
        """
        Create Argo template for a workflow node.

        Args:
            node: IR node representing a workflow step

        Returns:
            Argo template dictionary
        """
        container: dict[str, Any] = {
            "image": self.workflow.image,
            "imagePullPolicy": "IfNotPresent",
            "workingDir": "/app",
            "command": ["python", "-m", "axl.runtime"],
            "args": self._generate_step_args(node),
            "resources": self._get_resource_spec(node),
        }

        env_vars = self._get_env_vars(node)
        wf_meta = getattr(self.workflow, "metadata", {}) or {}
        if wf_meta.get("workflow_module") or wf_meta.get("workflow_class"):
            env_vars = env_vars + [
                {"name": "PYTHONPATH", "value": "/app:/app/examples"},
            ]
        container["env"] = env_vars

        template = {
            "name": node.name.replace("_", "-"),
            "container": container,
        }

        artifact_inputs = self._generate_artifact_inputs(node)
        artifact_outputs = self._generate_artifact_outputs(node)

        if artifact_inputs:
            template["inputs"] = {"artifacts": artifact_inputs}

        if artifact_outputs:
            template["outputs"] = {"artifacts": artifact_outputs}

        retries = node.get_retries()
        if retries is not None:
            template["retryStrategy"] = {
                "limit": retries,
                "retryPolicy": "Always",
                "backoff": {
                    "duration": "10s",
                    "factor": 2,
                    "maxDuration": "5m",
                },
            }

        return template

    def _generate_step_args(self, node: Any) -> list[str]:
        """
        Generate command line arguments for step execution.

        Args:
            node: IR node to generate args for

        Returns:
            List of command line arguments
        """
        io_handler = node.get_io_handler()
        if io_handler == "default":
            io_handler = self.workflow.io_handler

        args = [
            "--step",
            node.name.replace("_", "-"),
            "--workflow-name",
            self.workflow.name,
            "--io-handler",
            io_handler,
        ]

        wf_module = (
            self.workflow.metadata.get("workflow_module")
            if hasattr(self.workflow, "metadata")
            else None
        )
        wf_class = (
            self.workflow.metadata.get("workflow_class")
            if hasattr(self.workflow, "metadata")
            else None
        )
        if wf_module and wf_class:
            args.extend(
                ["--workflow-module", str(wf_module), "--workflow-class", str(wf_class)]
            )

        retries = node.get_retries()
        if retries is not None:
            args.extend(["--retries", str(retries)])

        io_manifest = self._generate_io_manifest(node)
        args.extend(["--io-manifest", io_manifest])

        # Per-step packages (comma-separated) for runtime to install (optional)
        packages = node.get_packages()
        if packages:
            args.extend(["--packages", ",".join(packages)])

        return args

    def _get_env_vars(self, node: Any) -> list[dict[str, str]]:
        """
        Get environment variables for a node.

        Args:
            node: IR node to get env vars for

        Returns:
            List of environment variable dictionaries
        """
        env_vars = []

        io_handler = node.get_io_handler()
        if io_handler == "default":
            io_handler = self.workflow.io_handler

        env_vars.extend(
            [
                {"name": "AXL_WORKFLOW_NAME", "value": self.workflow.name},
                {"name": "AXL_STEP_NAME", "value": node.name.replace("_", "-")},
                {"name": "AXL_IO_HANDLER", "value": io_handler},
            ]
        )

        node_env = node.get_env()
        for key, value in node_env.items():
            env_vars.append({"name": key, "value": str(value)})

        return env_vars

    def _generate_io_manifest(self, node: Any) -> str:
        """
        Generate IO manifest for a node.

        Args:
            node: IR node to generate manifest for

        Returns:
            JSON string representing IO manifest
        """
        import json

        io_handler = node.get_io_handler()
        if io_handler == "default":
            io_handler = self.workflow.io_handler

        file_extension = self._get_file_extension(io_handler)

        inputs = self._generate_input_specs(node)
        outputs = self._generate_output_specs(node, file_extension)

        manifest = {
            "step_name": node.name.replace("_", "-"),
            "io_handler": io_handler,
            "file_extension": file_extension,
            "inputs": inputs,
            "outputs": outputs,
        }

        return json.dumps(manifest)

    def _get_file_extension(self, io_handler: str) -> str:
        """
        Get file extension for IO handler.

        Args:
            io_handler: IO handler name

        Returns:
            File extension (e.g., '.pkl', '.json')
        """
        extensions = {
            "pickle": ".pkl",
            "cloudpickle": ".cpkl",
            "json": ".json",
            "yaml": ".yaml",
            "parquet": ".parquet",
            "numpy": ".npy",
            "torch": ".pt",
        }
        return extensions.get(io_handler, ".obj")

    def _generate_input_specs(self, node: Any) -> list[dict[str, str]]:
        """
        Generate input specifications for a node.

        Args:
            node: IR node to generate inputs for

        Returns:
            List of input specifications
        """
        inputs = []
        dependencies = self.workflow.get_node_dependencies(node.name)

        for dep in dependencies:
            dep_io_handler = dep.get_io_handler()
            if dep_io_handler == "default":
                dep_io_handler = self.workflow.io_handler

            dep_extension = self._get_file_extension(dep_io_handler)

            inputs.append(
                {
                    "name": dep.name.replace("_", "-"),
                    "source_step": dep.name.replace("_", "-"),
                    "file_path": f"/tmp/inputs/{dep.name}{dep_extension}",
                    "io_handler": dep_io_handler,
                }
            )

        return inputs

    def _generate_output_specs(
        self, node: Any, file_extension: str
    ) -> list[dict[str, str]]:
        """
        Generate output specifications for a node.

        Args:
            node: IR node to generate outputs for
            file_extension: File extension for outputs

        Returns:
            List of output specifications
        """
        outputs = []

        for output_name in node.outputs:
            outputs.append(
                {
                    "name": output_name.replace("_", "-"),
                    "file_path": f"/tmp/outputs/{output_name}{file_extension}",
                    "io_handler": node.get_io_handler() or self.workflow.io_handler,
                }
            )

        return outputs

    def _generate_artifact_inputs(self, node: Any) -> list[dict[str, Any]]:
        """
        Generate artifact input specifications for a node.

        Args:
            node: IR node to generate inputs for

        Returns:
            List of artifact input specifications
        """
        artifacts = []
        dependencies = self.workflow.get_node_dependencies(node.name)

        for dep in dependencies:
            dep_io_handler = dep.get_io_handler()
            if dep_io_handler == "default":
                dep_io_handler = self.workflow.io_handler

            dep_extension = self._get_file_extension(dep_io_handler)

            upstream = dep.name.replace("_", "-")
            # Template inputs must only declare the artifact interface (name/path).
            # Wiring from upstream outputs is done in the DAG task arguments.
            artifacts.append(
                {
                    "name": upstream,
                    "path": f"/tmp/inputs/{dep.name}{dep_extension}",
                }
            )

        return artifacts

    def _generate_artifact_outputs(self, node: Any) -> list[dict[str, Any]]:
        """
        Generate artifact output specifications for a node.

        Args:
            node: IR node to generate outputs for

        Returns:
            List of artifact output specifications
        """
        artifacts = []

        io_handler = node.get_io_handler()
        if io_handler == "default":
            io_handler = self.workflow.io_handler

        file_extension = self._get_file_extension(io_handler)

        for output_name in node.outputs:
            artifacts.append(
                {
                    "name": output_name.replace("_", "-"),
                    "path": f"/tmp/outputs/{output_name}{file_extension}",
                }
            )

        return artifacts

    def _get_resource_spec(self, node: Any) -> dict[str, Any]:
        """
        Get resource specification for a node.

        Args:
            node: IR node to get resources for

        Returns:
            Resource specification dictionary
        """
        resources = node.get_resources()

        defaults = {
            "requests": {
                "memory": "64Mi",
                "cpu": "100m",
            },
            "limits": {
                "memory": "128Mi",
                "cpu": "200m",
            },
        }

        if resources:
            if "cpu" in resources:
                cpu_value = str(resources["cpu"])
                defaults["requests"]["cpu"] = cpu_value
                if "cpu_limit" in resources:
                    defaults["limits"]["cpu"] = str(resources["cpu_limit"])
                else:
                    defaults["limits"]["cpu"] = cpu_value

            if "memory" in resources:
                memory_value = str(resources["memory"])
                defaults["requests"]["memory"] = memory_value
                if "memory_limit" in resources:
                    defaults["limits"]["memory"] = str(resources["memory_limit"])
                else:
                    defaults["limits"]["memory"] = memory_value

            if "gpu" in resources:
                gpu_value = str(resources["gpu"])
                defaults["requests"]["nvidia.com/gpu"] = gpu_value
                defaults["limits"]["nvidia.com/gpu"] = gpu_value

            if "ephemeral-storage" in resources:
                storage_value = str(resources["ephemeral-storage"])
                defaults["requests"]["ephemeral-storage"] = storage_value
                if "ephemeral-storage-limit" in resources:
                    defaults["limits"]["ephemeral-storage"] = str(
                        resources["ephemeral-storage-limit"]
                    )
                else:
                    defaults["limits"]["ephemeral-storage"] = storage_value

        return defaults

    def _generate_dag(self) -> None:
        """Generate DAG structure from workflow edges."""
        for node in self.workflow.nodes:
            task = self._create_task(node)
            self.tasks.append(task)

    def _create_task(self, node: Any) -> dict[str, Any]:
        """
        Create DAG task for a workflow node.

        Args:
            node: IR node to create task for

        Returns:
            DAG task dictionary
        """
        dependencies = self.workflow.get_node_dependencies(node.name)
        dependency_names = [dep.name.replace("_", "-") for dep in dependencies]

        task = {
            "name": node.name.replace("_", "-"),
            "template": node.name.replace("_", "-"),
        }

        if dependency_names:
            task["dependencies"] = dependency_names

        # Map artifacts from upstream tasks into this task's inputs via arguments
        arguments_artifacts: list[dict[str, str]] = []
        dependencies = self.workflow.get_node_dependencies(node.name)
        for dep in dependencies:
            upstream = dep.name.replace("_", "-")
            # The input artifact name on the consumer template matches upstream step name (normalized)
            arguments_artifacts.append(
                {
                    "name": upstream,
                    "from": f"{{{{tasks.{upstream}.outputs.artifacts.{upstream}}}}}",
                }
            )

        if arguments_artifacts:
            task["arguments"] = {"artifacts": arguments_artifacts}

        return task

    def to_yaml(self) -> str:
        """
        Convert compiled workflow to YAML string.

        Returns:
            YAML string representation of Argo Workflow
        """
        import yaml

        workflow_dict = self.compile()
        return yaml.dump(workflow_dict, default_flow_style=False, sort_keys=False)

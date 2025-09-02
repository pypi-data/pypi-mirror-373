"""
Basic example demonstrating ArgoCompiler functionality.

This example shows how to use the ArgoCompiler to generate Argo YAML
from a simple workflow definition.
"""

from axl.compiler import ArgoCompiler
from axl.ir.nodes import IREdge, IRNode
from axl.ir.workflow import IRWorkflow


def create_simple_workflow() -> IRWorkflow:
    """Create a simple IR workflow for testing."""
    nodes = [
        IRNode("params", {}),
        IRNode("preprocess", {"resources": {"cpu": "500m", "memory": "1Gi"}}),
        IRNode("train", {"resources": {"cpu": "1000m", "memory": "2Gi"}}),
        IRNode("evaluate", {}),
    ]
    edges = [
        IREdge("params", "preprocess"),
        IREdge("preprocess", "train"),
        IREdge("train", "evaluate"),
    ]

    return IRWorkflow(
        name="simple-ml-workflow",
        image="ghcr.io/you/axl-runner:0.1.0",
        io_handler="pickle",
        nodes=nodes,
        edges=edges,
    )


def main():
    """Demonstrate ArgoCompiler functionality."""
    print("Creating simple ML workflow...")
    workflow = create_simple_workflow()

    print("Compiling to Argo YAML...")
    compiler = ArgoCompiler(workflow)

    yaml_output = compiler.to_yaml()

    print("\n" + "=" * 50)
    print("Generated Argo YAML:")
    print("=" * 50)
    print(yaml_output)

    workflow_dict = compiler.compile()
    print("\n" + "=" * 50)
    print("Workflow structure:")
    print("=" * 50)
    print(f"Workflow name: {workflow_dict['metadata']['name']}")
    print(f"Number of templates: {len(workflow_dict['spec']['templates'])}")
    print(f"Number of tasks: {len(workflow_dict['spec']['dag']['tasks'])}")

    template_names = [t["name"] for t in workflow_dict["spec"]["templates"]]
    print(f"Template names: {template_names}")

    for task in workflow_dict["spec"]["dag"]["tasks"]:
        deps = task.get("dependencies", [])
        print(f"Task '{task['name']}' depends on: {deps}")


if __name__ == "__main__":
    main()

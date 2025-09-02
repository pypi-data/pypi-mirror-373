"""
Advanced example demonstrating enhanced ArgoCompiler functionality.

This example shows advanced features like GPU resources, environment variables,
retry strategies, and sophisticated resource specifications.
"""

from axl.compiler import ArgoCompiler
from axl.ir.nodes import IREdge, IRNode
from axl.ir.workflow import IRWorkflow


def create_advanced_workflow() -> IRWorkflow:
    """Create an advanced IR workflow demonstrating enhanced features."""
    nodes = [
        IRNode("data_ingest", {}),
        IRNode(
            "feature_engineering",
            {
                "resources": {
                    "cpu": "1000m",
                    "memory": "4Gi",
                    "ephemeral-storage": "10Gi",
                },
                "env": {
                    "FEATURE_CACHE_DIR": "/tmp/features",
                    "PARALLEL_JOBS": "4",
                },
            },
        ),
        IRNode(
            "model_training",
            {
                "resources": {
                    "cpu": "2000m",
                    "memory": "8Gi",
                    "gpu": "1",
                    "ephemeral-storage": "20Gi",
                },
                "env": {
                    "CUDA_VISIBLE_DEVICES": "0",
                    "MODEL_SAVE_PATH": "/models",
                    "BATCH_SIZE": "128",
                    "LEARNING_RATE": "0.001",
                },
                "retries": 3,
                "io_handler": "cloudpickle",
            },
        ),
        IRNode(
            "model_evaluation",
            {
                "resources": {
                    "cpu": "500m",
                    "memory": "2Gi",
                },
                "env": {
                    "EVAL_METRICS": "accuracy,precision,recall,f1",
                    "THRESHOLD": "0.5",
                },
                "io_handler": "json",
            },
        ),
    ]

    edges = [
        IREdge("data_ingest", "feature_engineering"),
        IREdge("feature_engineering", "model_training"),
        IREdge("model_training", "model_evaluation"),
    ]

    return IRWorkflow(
        name="advanced-ml-pipeline",
        image="ghcr.io/you/axl-runner:0.1.0",
        io_handler="pickle",
        nodes=nodes,
        edges=edges,
    )


def main():
    """Demonstrate advanced ArgoCompiler functionality."""
    print("Creating advanced ML pipeline...")
    workflow = create_advanced_workflow()

    print("Compiling to Argo YAML...")
    compiler = ArgoCompiler(workflow)

    yaml_output = compiler.to_yaml()

    print("\n" + "=" * 60)
    print("Generated Advanced Argo YAML:")
    print("=" * 60)
    print(yaml_output)

    workflow_dict = compiler.compile()
    print("\n" + "=" * 60)
    print("Advanced Workflow Analysis:")
    print("=" * 60)
    print(f"Workflow name: {workflow_dict['metadata']['name']}")
    print(f"Number of templates: {len(workflow_dict['spec']['templates'])}")
    print(f"Number of tasks: {len(workflow_dict['spec']['dag']['tasks'])}")

    templates = workflow_dict["spec"]["templates"]
    for template in templates:
        name = template["name"]
        container = template["container"]

        print(f"\n--- Template: {name} ---")

        resources = container["resources"]
        requests = resources["requests"]
        limits = resources["limits"]

        print(
            f"  CPU: {requests.get('cpu', 'N/A')} (limit: {limits.get('cpu', 'N/A')})"
        )
        print(
            f"  Memory: {requests.get('memory', 'N/A')} (limit: {limits.get('memory', 'N/A')})"
        )

        if "nvidia.com/gpu" in requests:
            print(f"  GPU: {requests['nvidia.com/gpu']}")

        if "ephemeral-storage" in requests:
            print(f"  Storage: {requests['ephemeral-storage']}")

        env_vars = container.get("env", [])
        if env_vars:
            print(f"  Environment variables: {len(env_vars)}")
            for env in env_vars:
                if not env["name"].startswith("AXL_"):
                    print(f"    {env['name']}: {env['value']}")

        if "retryStrategy" in template:
            retry = template["retryStrategy"]
            print(f"  Retry strategy: {retry['limit']} attempts with backoff")

        args = container["args"]
        for i, arg in enumerate(args):
            if arg == "--io-handler" and i + 1 < len(args):
                print(f"  IO Handler: {args[i + 1]}")
                break

    print("\n--- Task Dependencies ---")
    tasks = workflow_dict["spec"]["dag"]["tasks"]
    for task in tasks:
        deps = task.get("dependencies", [])
        print(f"  {task['name']} depends on: {deps}")


if __name__ == "__main__":
    main()

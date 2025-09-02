"""
CLI entry point for AXL Workflows.

This module provides the command-line interface for the axl tool.
"""

import importlib
import sys
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .ir import build_ir, get_workflow_info
from .runtime import LocalRuntime

app = typer.Typer(
    name="axl",
    help="AXL Workflows - Lightweight framework for building data and ML workflows",
    add_completion=False,
)
console = Console()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=lambda v: typer.echo(f"axl {__version__}") if v else None,
        is_eager=True,
    ),
) -> None:
    """
    AXL Workflows - Write once → run anywhere (Dagster locally or Kubeflow in production).
    """
    pass


@app.command()
def version() -> None:
    """Show version information."""
    console.print(Panel(f"AXL Workflows v{__version__}", title="Version"))


def load_parameters(params_file: str | None) -> dict[str, Any]:
    """
    Load parameters from YAML file.

    Args:
        params_file: Path to YAML parameters file

    Returns:
        Dictionary of parameters

    Raises:
        typer.Exit: If file not found or invalid YAML
    """
    if not params_file:
        return {}

    try:
        params_path = Path(params_file)
        if not params_path.exists():
            raise FileNotFoundError(f"Parameters file not found: {params_path}")

        with open(params_path) as f:
            params = yaml.safe_load(f)

        if not isinstance(params, dict):
            raise ValueError("Parameters file must contain a YAML dictionary")

        console.print(
            f"[green]Loaded {len(params)} parameters from {params_file}[/green]"
        )
        return params

    except Exception as e:
        console.print(f"[red]Error loading parameters: {e}[/red]")
        raise typer.Exit(1) from None


def load_workflow_class(module_path: str) -> type:
    """
    Load workflow class from module path.

    Args:
        module_path: Module path in format 'module:Class' or 'path/to/file.py:Class'

    Returns:
        Workflow class

    Raises:
        typer.Exit: If module or class not found
    """
    try:
        if ":" not in module_path:
            raise ValueError(
                "Module path must be in format 'module:Class' or 'path/to/file.py:Class'"
            )

        module_spec, class_name = module_path.split(":", 1)

        if module_spec.endswith(".py"):
            file_path = Path(module_spec)
            if not file_path.exists():
                raise FileNotFoundError(f"Module file not found: {file_path}")

            parent_dir = file_path.parent
            sys.path.insert(0, str(parent_dir))

            module_name = file_path.stem
            module = importlib.import_module(module_name)

        else:
            module = importlib.import_module(module_spec)

        if not hasattr(module, class_name):
            raise AttributeError(
                f"Class '{class_name}' not found in module '{module_spec}'"
            )

        workflow_class = getattr(module, class_name)

        from .core.workflow import Workflow

        if not issubclass(workflow_class, Workflow):
            raise ValueError(
                f"Class '{class_name}' is not a workflow class (must inherit from Workflow)"
            )

        return workflow_class  # type: ignore[no-any-return]

    except Exception as e:
        console.print(f"[red]Error loading workflow: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def validate(
    module: str = typer.Argument(
        ...,
        help="Module path to workflow class (e.g., 'myflow:MyWorkflow')",
    ),
) -> None:
    """Validate a workflow definition."""
    try:
        console.print(f"[yellow]Validating workflow: {module}[/yellow]")

        workflow_class = load_workflow_class(module)

        info = get_workflow_info(workflow_class)

        table = Table(title="Workflow Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Name", info["name"])
        table.add_row("Image", info["image"])
        table.add_row("IO Handler", info["io_handler"])
        table.add_row("Steps", str(info["step_count"]))

        console.print(table)

        console.print("\n[yellow]Building IR and validating...[/yellow]")
        ir_workflow = build_ir(workflow_class)

        console.print("[green]✅ Workflow is valid![/green]")

        step_table = Table(title="Steps")
        step_table.add_column("Step", style="cyan")
        step_table.add_column("Inputs", style="blue")
        step_table.add_column("IO Handler", style="green")

        for node in ir_workflow.nodes:
            inputs = ", ".join(node.inputs) if node.inputs else "None"
            io_handler = node.get_io_handler() or "default"
            step_table.add_row(node.name, inputs, io_handler)

        console.print(step_table)

    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def compile(
    module: str = typer.Argument(
        ...,
        help="Module path to workflow class (e.g., 'myflow:MyWorkflow')",
    ),
    target: str = typer.Option(
        "argo",
        "--target",
        "-t",
        help="Target backend (argo, dagster)",
    ),
    out: str = typer.Option(
        None,
        "--out",
        "-o",
        help="Output file path",
    ),
) -> None:
    """Compile a workflow to target backend."""
    try:
        console.print(f"[yellow]Compiling {module} to {target} format...[/yellow]")

        if target != "argo":
            console.print("[red]Only 'argo' target is implemented for now[/red]")
            raise typer.Exit(1)

        workflow_class = load_workflow_class(module)

        ir_workflow = build_ir(workflow_class)

        from axl.compiler import ArgoCompiler

        compiler = ArgoCompiler(ir_workflow)

        if out:
            yaml_output = compiler.to_yaml()
            with open(out, "w") as f:
                f.write(yaml_output)
            console.print(f"[green]Argo YAML written to: {out}[/green]")
        else:
            yaml_output = compiler.to_yaml()
            console.print(yaml_output)

        console.print(Panel("Compilation completed", title="Compile"))

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Compilation failed: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def run(
    backend: str = typer.Argument(
        "local",
        help="Backend to run on (local, argo, dagster)",
    ),
    module: str = typer.Option(
        None,
        "--module",
        "-m",
        help="Module path to workflow class (e.g., 'examples/iris_example.py:IrisKNN')",
    ),
    storage_backend: str = typer.Option(
        "memory",
        "--storage",
        help="Storage backend for artifacts (memory|local)",
    ),
    workspace: str = typer.Option(
        "axl_workspace",
        "--workspace",
        help="Workspace directory for local storage backend",
    ),
    params: str = typer.Option(
        None,
        "--params",
        "-p",
        help="Parameters file (YAML) to pass to workflow constructor",
    ),
) -> None:
    """Run a workflow on the specified backend.

    Currently implemented: local backend using LocalRuntime.
    """
    try:
        console.print(f"[yellow]Running workflow on {backend}[/yellow]")

        if backend != "local":
            console.print("[red]Only 'local' backend is implemented for now[/red]")
            raise typer.Exit(1)

        if not module:
            console.print("[red]--module is required for local execution[/red]")
            raise typer.Exit(1)

        workflow_params = load_parameters(params)

        workflow_class = load_workflow_class(module)

        ir_workflow = build_ir(workflow_class)

        wf_instance = workflow_class(**workflow_params)

        console.print(
            f"[yellow]Executing locally (storage={storage_backend}, workspace='{workspace}')[/yellow]"
        )
        runtime = LocalRuntime(
            workspace_path=workspace, storage_backend=storage_backend
        )
        runtime.execute_workflow(ir_workflow, wf_instance)

        console.print(Panel("Local run completed", title="Run"))

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Run failed: {e}[/red]")
        raise typer.Exit(1) from None


@app.command()
def render(
    module: str = typer.Argument(
        ...,
        help="Module path to workflow class",
    ),
    out: str = typer.Option(
        None,
        "--out",
        "-o",
        help="Output file path (e.g., dag.png)",
    ),
) -> None:
    """Render a workflow DAG as an image."""
    # TODO: Implement DAG rendering
    console.print(f"[yellow]Rendering workflow: {module}[/yellow]")
    if out:
        console.print(f"[yellow]Output: {out}[/yellow]")
    console.print("[red]Not implemented yet[/red]")


if __name__ == "__main__":
    app()

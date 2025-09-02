import argparse
import importlib
import json
import sys
import time
from pathlib import Path

from axl.io.registry import registry


def load_inputs(manifest: dict) -> list:
    inputs: list = []
    for spec in manifest.get("inputs", []):
        handler_name = spec.get("io_handler")
        path = Path(spec.get("file_path"))
        handler = registry.get(handler_name)
        obj = handler.load(path)
        inputs.append(obj)
    return inputs


def save_outputs(manifest: dict, result: object) -> None:
    outputs = manifest.get("outputs", [])
    if not outputs:
        return

    # If multiple outputs and result is a tuple or list, map one-to-one
    if isinstance(result, tuple | list) and len(outputs) == len(result):
        for spec, obj in zip(outputs, result, strict=False):
            handler = registry.get(spec.get("io_handler"))
            out_path = Path(spec.get("file_path"))
            out_path.parent.mkdir(parents=True, exist_ok=True)
            handler.save(obj, out_path)
        return

    # Otherwise, save the whole result to the first output
    first = outputs[0]
    handler = registry.get(first.get("io_handler"))
    out_path = Path(first.get("file_path"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    handler.save(result, out_path)


def install_packages(packages_csv: str | None) -> None:
    if not packages_csv:
        return
    pkgs = [p.strip() for p in packages_csv.split(",") if p.strip()]
    if not pkgs:
        return
    # Prefer uv if available, else pip
    import shutil
    import subprocess

    uv = shutil.which("uv")
    if uv:
        subprocess.check_call([uv, "pip", "install", "--system", *pkgs])
    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *pkgs])


def run_step(args: argparse.Namespace) -> int:
    start_ms = int(time.time() * 1000)
    step_name_runtime = args.step
    step_name = step_name_runtime.replace("-", "_")

    manifest = json.loads(args.io_manifest)

    # Install per-step packages if provided
    install_packages(getattr(args, "packages", None))
    inputs = load_inputs(manifest)

    # Import workflow class
    module = importlib.import_module(args.workflow_module)
    wf_class = getattr(module, args.workflow_class)
    wf_instance = wf_class()

    # Get original function to avoid decorator's validation shim
    step_attr = object.__getattribute__(wf_instance, step_name)
    original = getattr(step_attr, "_original_func", None)
    if original is None:
        # Fallback: call attribute directly
        original = step_attr

    result = original(wf_instance, *inputs)
    save_outputs(manifest, result)

    duration_ms = int(time.time() * 1000) - start_ms
    print(
        json.dumps(
            {
                "workflow": args.workflow_name,
                "step": step_name_runtime,
                "status": "success",
                "duration_ms": duration_ms,
            }
        )
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="AXL Runtime Entrypoint")
    parser.add_argument("--step", required=True)
    parser.add_argument("--workflow-name", required=True)
    parser.add_argument("--io-handler", required=True)
    parser.add_argument("--io-manifest", required=True)
    parser.add_argument("--workflow-module", required=True)
    parser.add_argument("--workflow-class", required=True)
    parser.add_argument("--retries", required=False)
    parser.add_argument("--packages", required=False)

    args = parser.parse_args()
    rc = run_step(args)
    sys.exit(rc)


if __name__ == "__main__":
    main()

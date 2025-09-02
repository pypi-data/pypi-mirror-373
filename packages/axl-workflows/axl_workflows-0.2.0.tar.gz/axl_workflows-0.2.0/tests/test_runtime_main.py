import argparse
import json
from pathlib import Path

from axl.core.decorators import step
from axl.core.workflow import Workflow
from axl.io.registry import registry
from axl.runtime.__main__ import run_step


class DummyWorkflowNoInputs(Workflow):
    name = "dummy-no-inputs"

    @step()
    def do_something(self) -> int:
        return 42


class DummyWorkflowWithInput(Workflow):
    name = "dummy-with-input"

    @step()
    def process(self, value: int) -> tuple[int, int]:
        return value, value + 1


def test_run_step_no_inputs_saves_output(tmp_path: Path, capsys) -> None:
    out_file = tmp_path / "out.pkl"
    manifest = {
        "step_name": "do-something",
        "io_handler": "pickle",
        "file_extension": ".pkl",
        "inputs": [],
        "outputs": [
            {
                "name": "result",
                "file_path": str(out_file),
                "io_handler": "pickle",
            }
        ],
    }
    args = argparse.Namespace(
        step="do-something",
        workflow_name="dummy-no-inputs",
        io_handler="pickle",
        io_manifest=json.dumps(manifest),
        workflow_module="tests.test_runtime_main",
        workflow_class="DummyWorkflowNoInputs",
        retries=None,
        packages=None,
    )

    rc = run_step(args)
    assert rc == 0
    # Verify output saved
    handler = registry.get("pickle")
    assert handler.load(out_file) == 42
    # Verify structured log printed
    captured = capsys.readouterr().out
    assert '"status": "success"' in captured
    assert '"step": "do-something"' in captured


def test_run_step_with_input_tuple_outputs(tmp_path: Path) -> None:
    in_file = tmp_path / "in.pkl"
    out_a = tmp_path / "a.pkl"
    out_b = tmp_path / "b.pkl"

    handler = registry.get("pickle")
    handler.save(3, in_file)

    manifest = {
        "step_name": "process",
        "io_handler": "pickle",
        "file_extension": ".pkl",
        "inputs": [
            {
                "name": "value",
                "source_step": "upstream",
                "file_path": str(in_file),
                "io_handler": "pickle",
            }
        ],
        "outputs": [
            {
                "name": "a",
                "file_path": str(out_a),
                "io_handler": "pickle",
            },
            {
                "name": "b",
                "file_path": str(out_b),
                "io_handler": "pickle",
            },
        ],
    }

    args = argparse.Namespace(
        step="process",
        workflow_name="dummy-with-input",
        io_handler="pickle",
        io_manifest=json.dumps(manifest),
        workflow_module="tests.test_runtime_main",
        workflow_class="DummyWorkflowWithInput",
        retries=None,
        packages=None,
    )

    rc = run_step(args)
    assert rc == 0
    assert handler.load(out_a) == 3
    assert handler.load(out_b) == 4

"""
Tests for IR components.
"""

import pytest

from axl.ir import OutputRef, validate_step_args


class TestOutputRef:
    """Test cases for OutputRef class."""

    def test_output_ref_creation(self) -> None:
        """Test that OutputRef can be created."""
        ref = OutputRef("test_step")
        assert ref.step_name == "test_step"
        assert ref.inputs == []
        assert ref.metadata == {}

    def test_output_ref_with_inputs(self) -> None:
        """Test that OutputRef can be created with inputs."""
        input_ref = OutputRef("input_step")
        ref = OutputRef("test_step", inputs=[input_ref])
        assert ref.step_name == "test_step"
        assert ref.inputs == [input_ref]

    def test_output_ref_repr(self) -> None:
        """Test that OutputRef has proper string representation."""
        ref = OutputRef("test_step")
        assert repr(ref) == "OutputRef(test_step)"
        assert str(ref) == "<output from test_step>"

    def test_output_ref_metadata(self) -> None:
        """Test that OutputRef can store and retrieve metadata."""
        ref = OutputRef("test_step")
        ref.add_metadata("io_handler", "pickle")
        ref.add_metadata("resources", {"cpu": "2"})

        assert ref.get_metadata("io_handler") == "pickle"
        assert ref.get_metadata("resources") == {"cpu": "2"}
        assert ref.get_metadata("missing", "default") == "default"


class TestValidateStepArgs:
    """Test cases for validate_step_args function."""

    def test_validate_step_args_valid(self) -> None:
        """Test that validate_step_args accepts valid OutputRef arguments."""
        ref1 = OutputRef("step1")
        ref2 = OutputRef("step2")

        # Should not raise any exception
        validate_step_args("test_step", (ref1, ref2), {"kwarg": ref1})

    def test_validate_step_args_invalid_positional(self) -> None:
        """Test that validate_step_args rejects invalid positional arguments."""
        ref = OutputRef("step1")

        with pytest.raises(ValueError, match="must be an OutputRef"):
            validate_step_args("test_step", (ref, "invalid_string"), {})

    def test_validate_step_args_invalid_keyword(self) -> None:
        """Test that validate_step_args rejects invalid keyword arguments."""
        ref = OutputRef("step1")

        with pytest.raises(ValueError, match="must be an OutputRef"):
            validate_step_args("test_step", (ref,), {"invalid": 42})

    def test_validate_step_args_user_friendly_message(self) -> None:
        """Test that error messages are user-friendly."""
        with pytest.raises(ValueError, match="must be an OutputRef"):
            validate_step_args("test_step", ("self", "not_a_ref"), {})


class TestStepInterception:
    """Test cases for step method interception in Workflow."""

    def test_step_method_interception(self) -> None:
        """Test that step methods are intercepted to return OutputRef."""
        from axl.core import Workflow, step

        class TestWorkflow(Workflow):
            @step()
            def step1(self):
                return "result1"

            @step()
            def step2(self, input_ref):
                return "result2"

            def graph(self):
                return self.step2(self.step1())

        # Step methods should always return OutputRef
        wf = TestWorkflow()
        step1_ref = wf.step1()
        assert isinstance(step1_ref, OutputRef)
        assert step1_ref.step_name == "step1"

        step2_ref = wf.step2(step1_ref)
        assert isinstance(step2_ref, OutputRef)
        assert step2_ref.step_name == "step2"

    def test_non_step_method_not_intercepted(self) -> None:
        """Test that non-step methods are not intercepted."""
        from axl.core import Workflow

        class TestWorkflow(Workflow):
            def regular_method(self):
                return "regular"

            def graph(self):
                return "test"

        wf = TestWorkflow()

        # Regular methods should work normally
        result = wf.regular_method()
        assert result == "regular"

        # Non-existent methods should raise AttributeError
        with pytest.raises(AttributeError):
            wf.non_existent_method()

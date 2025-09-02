"""
Example workflow: Parameter Testing.

This demonstrates how to use parameters in workflows.
"""

from axl import Workflow, step


class ParameterTest(Workflow):
    name = "parameter-test"

    @step()
    def params(self) -> dict:
        """Define workflow parameters."""
        return {
            "input_path": "data/input.csv",
            "output_path": "data/output.csv",
            "model_type": "random_forest",
            "random_state": 42,
        }

    @step()
    def process_with_params(self, params: dict) -> str:
        """Process data using parameters."""
        input_path = params["input_path"]
        model_type = params["model_type"]
        return f"Processed {input_path} with {model_type}"

    @step()
    def save_results(self, result: str, params: dict) -> str:
        """Save results using parameters."""
        output_path = params["output_path"]
        return f"Saved {result} to {output_path}"

    def graph(self):
        """Define the workflow graph."""
        params = self.params()
        result = self.process_with_params(params)
        return self.save_results(result, params)


if __name__ == "__main__":
    workflow = ParameterTest()
    result = workflow.graph()
    print(f"Workflow result: {result}")

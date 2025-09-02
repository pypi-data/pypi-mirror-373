"""
Example workflow: Customer Churn Prediction Training.

This demonstrates the intended AXL Workflows DSL syntax with params as a step
and io_handlers for object persistence.
"""

from pydantic import BaseModel

from axl import Workflow, step


class TrainParams(BaseModel):
    seed: int = 42
    input_path: str = "data/raw.csv"


class ChurnTrain(Workflow):
    name = "churn-train"
    image = "ghcr.io/you/axl-runner:0.1.0"
    io_handler = "pickle"

    @step()
    def params(self) -> TrainParams:
        return TrainParams()

    @step()
    def preprocess(self, p: TrainParams):
        # TODO: Implement preprocessing logic
        return {"features": "preprocessed_data"}

    @step()
    def train(self, features, p: TrainParams):
        # TODO: Implement training logic
        return {"model": "trained_model"}

    @step()
    def evaluate(self, model) -> float:
        # TODO: Implement evaluation logic
        return 0.9123

    def graph(self):
        p = self.params()
        feats = self.preprocess(p)
        model = self.train(feats, p)
        return self.evaluate(model)


if __name__ == "__main__":
    print("ChurnTrain workflow defined")
    print("To compile to Argo YAML:")
    print(
        "  axl compile examples/churn_workflow.py:ChurnTrain --target argo --out churn.yaml"
    )
    print("To run locally:")
    print("  axl run local -m examples/churn_workflow.py:ChurnTrain")

"""
Example workflow: Iris Classification with KNN.

This demonstrates a simple ML workflow using scikit-learn.
"""

from typing import Any

from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from axl import Workflow, step


class IrisKNN(Workflow):
    name = "iris-knn"
    image = "axl-runner:dev3"
    io_handler = "pickle"

    @step(packages=["scikit-learn"])
    def load_data(self) -> tuple[Any, Any]:
        """Load iris dataset."""
        data = load_iris()
        return data.data, data.target

    @step(packages=["scikit-learn"])
    def split(self, data: tuple[Any, Any]) -> tuple[Any, Any, Any, Any]:
        """Split data into train/test sets."""
        X, y = data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        return X_train, X_test, y_train, y_test

    @step(packages=["scikit-learn"])
    def train(self, split: tuple[Any, Any, Any, Any]) -> tuple[Any, Any, Any]:
        """Train KNN model."""
        X_train, X_test, y_train, y_test = split
        clf = KNeighborsClassifier(n_neighbors=3)
        clf.fit(X_train, y_train)
        return clf, X_test, y_test

    @step(packages=["scikit-learn"])
    def evaluate(self, trained: tuple[Any, Any, Any]) -> float:
        """Evaluate model accuracy."""
        clf, X_test, y_test = trained
        y_pred = clf.predict(X_test)
        return float(accuracy_score(y_test, y_pred))

    def graph(self):
        """Define the workflow graph."""
        data = self.load_data()
        split_data = self.split(data)
        trained_model = self.train(split_data)
        return self.evaluate(trained_model)


if __name__ == "__main__":
    print("IrisKNN workflow defined")
    print("To compile to Argo YAML:")
    print(
        "  axl compile examples/iris_example.py:IrisKNN --target argo --out examples/compiled/iris.yaml"
    )
    print("To run locally:")
    print("  axl run local -m examples/iris_example.py:IrisKNN")

    # Also run locally to verify it works
    from axl.ir import build_ir
    from axl.runtime import LocalRuntime

    print("\n🧪 Testing local execution...")
    ir = build_ir(IrisKNN)
    result = LocalRuntime(storage_backend="memory").execute_workflow(ir, IrisKNN())
    print(f"🎯 Final accuracy: {result:.4f}")

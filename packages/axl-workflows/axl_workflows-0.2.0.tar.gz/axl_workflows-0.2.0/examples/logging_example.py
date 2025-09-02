"""
Example workflow demonstrating logging functionality.

This example shows how to use the WorkflowLogger for structured logging
in workflow steps.
"""

from axl import Workflow, step


class LoggingDemo(Workflow):
    name = "logging-demo"

    @step()
    def step_with_logging(self) -> str:
        # Log some information
        self.log.info("Starting step_with_logging")
        self.log.info("Processing data", extra={"data_size": 1000})

        # Simulate some work
        result = "processed_data"

        self.log.info("Step completed successfully", extra={"result": result})
        return result

    @step()
    def step_with_error_logging(self, data: str) -> str:
        self.log.info("Starting step_with_error_logging", extra={"input": data})

        try:
            # Simulate some work that might fail
            if data == "error":
                raise ValueError("Simulated error")

            result = f"enhanced_{data}"
            self.log.info("Step completed", extra={"result": result})
            return result

        except Exception as e:
            self.log.error("Step failed", extra={"error": str(e)})
            raise

    def graph(self):
        data = self.step_with_logging()
        return self.step_with_error_logging(data)


if __name__ == "__main__":
    # Create and run the workflow
    workflow = LoggingDemo()

    # Run the workflow
    try:
        result = workflow.graph()
        print(f"Workflow completed successfully: {result}")
    except Exception as e:
        print(f"Workflow failed: {e}")

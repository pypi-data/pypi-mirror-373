"""
Logging infrastructure for AXL Workflows.

This module provides automatic internal logging with user access via self.log
in workflow steps.
"""

from datetime import datetime
from typing import Any

from rich.console import Console

console = Console()


class WorkflowLogger:
    """Logger accessible via self.log in workflow steps."""

    def __init__(self, workflow_name: str):
        """
        Initialize workflow logger.

        Args:
            workflow_name: Name of the workflow
        """
        self.workflow_name = workflow_name
        self.step_name: str | None = None
        self.start_time: float | None = None

    def _format_log(self, level: str, message: str, **kwargs: Any) -> str:
        """
        Format log message with timestamp and context.

        Args:
            level: Log level (INFO, DEBUG, WARN, ERROR)
            message: Log message
            **kwargs: Additional context data

        Returns:
            Formatted log string
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Build context string
        context_parts = [f"workflow:{self.workflow_name}"]
        if self.step_name:
            context_parts.append(f"step:{self.step_name}")

        context = f"[{']['.join(context_parts)}]"

        # Format additional data
        data_str = ""
        if kwargs:
            data_items = [f"{k}={v}" for k, v in kwargs.items()]
            data_str = f" ({', '.join(data_items)})"

        return f"[{timestamp}] {level} {context} {message}{data_str}"

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        """
        Internal logging method.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context data
        """
        log_line = self._format_log(level, message, **kwargs)

        # Color code based on level
        if level == "ERROR":
            console.print(log_line, style="red")
        elif level == "WARN":
            console.print(log_line, style="yellow")
        elif level == "DEBUG":
            console.print(log_line, style="dim")
        else:  # INFO
            console.print(log_line, style="green")

    def info(self, message: str, **kwargs: Any) -> None:
        """
        Log info message.

        Args:
            message: Log message
            **kwargs: Additional context data
        """
        self._log("INFO", message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """
        Log debug message.

        Args:
            message: Log message
            **kwargs: Additional context data
        """
        self._log("DEBUG", message, **kwargs)

    def warn(self, message: str, **kwargs: Any) -> None:
        """
        Log warning message.

        Args:
            message: Log message
            **kwargs: Additional context data
        """
        self._log("WARN", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """
        Log error message.

        Args:
            message: Log message
            **kwargs: Additional context data
        """
        self._log("ERROR", message, **kwargs)

    def set_step_context(self, step_name: str) -> None:
        """
        Set the current step context for logging.

        Args:
            step_name: Name of the current step
        """
        self.step_name = step_name

    def clear_step_context(self) -> None:
        """Clear the current step context."""
        self.step_name = None

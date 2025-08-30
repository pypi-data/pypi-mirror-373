#!/usr/bin/env python3
"""
Context-Aware Logging System for CloudOps Runbooks

This module provides adaptive logging that detects execution context (CLI vs Jupyter)
and adjusts verbosity, formatting, and output style accordingly.

Features:
- Automatic CLI vs Jupyter environment detection
- Adaptive logging levels (technical for CLI, clean for Jupyter)
- Smart Rich console output based on context
- Performance metrics display optimization
- Context-aware error handling and stack traces

Usage:
    from runbooks.common.context_logger import ContextLogger, get_context_console

    logger = ContextLogger("finops.dashboard")
    console = get_context_console()

    logger.info("Starting analysis")  # Detailed in CLI, simple in Jupyter
    logger.technical_detail("AWS API call details")  # Only shown in CLI

Author: CloudOps Runbooks Team
Version: 0.8.0
"""

import os
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.traceback import install as install_rich_traceback

from runbooks.common.rich_utils import (
    CLOUDOPS_THEME,
    STATUS_INDICATORS,
    create_panel,
    format_cost,
    print_error,
    print_info,
    print_status,
    print_success,
    print_warning,
)
from runbooks.common.rich_utils import (
    console as rich_console,
)


class ExecutionContext(Enum):
    """Execution context types."""

    CLI = "cli"
    JUPYTER = "jupyter"
    UNKNOWN = "unknown"


@dataclass
class ContextConfig:
    """Configuration for context-aware logging."""

    context: ExecutionContext
    show_technical_details: bool
    show_performance_metrics: bool
    show_progress_bars: bool
    show_full_stack_traces: bool
    console_width: Optional[int] = None


class ContextDetector:
    """Detect execution environment context."""

    @staticmethod
    def detect_context() -> ExecutionContext:
        """
        Detect if running in CLI vs Jupyter environment.

        Returns:
            ExecutionContext: Detected execution context
        """
        # Check for IPython/Jupyter kernel
        try:
            # Check if we're in IPython/Jupyter
            from IPython import get_ipython

            ipython = get_ipython()

            if ipython is not None:
                # Check if it's a Jupyter kernel
                if hasattr(ipython, "kernel"):
                    return ExecutionContext.JUPYTER

                # Check for Jupyter-specific modules
                if "zmq" in str(type(ipython)).lower():
                    return ExecutionContext.JUPYTER

                # Check for notebook environment variables
                if any(key in os.environ for key in ["JUPYTER_SERVER_ROOT", "JPY_SESSION_NAME", "KERNEL_ID"]):
                    return ExecutionContext.JUPYTER

        except ImportError:
            # IPython not available, definitely not Jupyter
            pass

        # Check for terminal environment
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            return ExecutionContext.CLI

        # Check for common CLI indicators
        if any(arg in sys.argv for arg in ["--help", "-h", "runbooks"]):
            return ExecutionContext.CLI

        # Default fallback
        return ExecutionContext.UNKNOWN

    @staticmethod
    def get_context_config() -> ContextConfig:
        """
        Get context configuration based on detected environment.

        Returns:
            ContextConfig: Configuration optimized for detected context
        """
        context = ContextDetector.detect_context()

        if context == ExecutionContext.CLI:
            return ContextConfig(
                context=context,
                show_technical_details=True,
                show_performance_metrics=True,
                show_progress_bars=True,
                show_full_stack_traces=True,
                console_width=None,  # Auto-detect
            )
        elif context == ExecutionContext.JUPYTER:
            return ContextConfig(
                context=context,
                show_technical_details=False,
                show_performance_metrics=False,
                show_progress_bars=True,  # Still useful in notebooks
                show_full_stack_traces=False,
                console_width=100,  # Fixed width for notebook display
            )
        else:
            # Conservative defaults for unknown context
            return ContextConfig(
                context=context,
                show_technical_details=True,
                show_performance_metrics=True,
                show_progress_bars=True,
                show_full_stack_traces=True,
                console_width=None,
            )


class ContextAwareConsole:
    """Console wrapper that adapts output based on execution context."""

    def __init__(self, config: Optional[ContextConfig] = None):
        """
        Initialize context-aware console.

        Args:
            config: Optional context configuration (auto-detected if None)
        """
        self.config = config or ContextDetector.get_context_config()

        # Create console with appropriate configuration
        console_kwargs = {
            "theme": CLOUDOPS_THEME,
            "force_terminal": self.config.context == ExecutionContext.CLI,
        }

        if self.config.console_width:
            console_kwargs["width"] = self.config.console_width

        self.console = Console(**console_kwargs)

        # Install rich tracebacks if configured
        if self.config.show_full_stack_traces:
            install_rich_traceback(show_locals=True, console=self.console)

    def print(self, *args, **kwargs) -> None:
        """Print with context awareness."""
        self.console.print(*args, **kwargs)

    def log(self, *args, **kwargs) -> None:
        """Log with context awareness."""
        if self.config.show_technical_details:
            self.console.log(*args, **kwargs)

    def print_technical_detail(self, message: str, style: str = "dim") -> None:
        """Print technical detail only in appropriate contexts."""
        if self.config.show_technical_details:
            self.console.print(f"🔧 {message}", style=style)

    def print_performance_metric(self, metric_name: str, value: Union[str, float], unit: str = "") -> None:
        """Print performance metrics only in appropriate contexts."""
        if self.config.show_performance_metrics:
            if isinstance(value, float):
                formatted_value = f"{value:.2f}{unit}"
            else:
                formatted_value = f"{value}{unit}"
            self.console.print(f"⚡ {metric_name}: [highlight]{formatted_value}[/]", style="info")

    def create_progress(self, description: str = "Processing") -> Progress:
        """Create progress bar appropriate for context."""
        if self.config.show_progress_bars:
            if self.config.context == ExecutionContext.JUPYTER:
                # Simpler progress for Jupyter
                return Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(bar_width=40),
                    TaskProgressColumn(),
                    console=self.console,
                    transient=False,  # Don't hide in notebooks
                )
            else:
                # Full progress for CLI
                return Progress(
                    SpinnerColumn(spinner_name="dots", style="cyan"),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(bar_width=40, style="cyan", complete_style="green"),
                    TaskProgressColumn(),
                    TimeElapsedColumn(),
                    console=self.console,
                    transient=True,
                )
        else:
            # Minimal progress fallback
            return Progress(
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            )


class ContextLogger:
    """Context-aware logger for CloudOps operations."""

    def __init__(self, name: str, console: Optional[ContextAwareConsole] = None):
        """
        Initialize context logger.

        Args:
            name: Logger name (typically module.operation)
            console: Optional context-aware console (auto-created if None)
        """
        self.name = name
        self.console = console or ContextAwareConsole()
        self.start_time = time.time()
        self._operation_start_times: Dict[str, float] = {}

    def info(self, message: str, technical_detail: Optional[str] = None) -> None:
        """
        Log info message with optional technical detail.

        Args:
            message: Main message (always shown)
            technical_detail: Technical detail (CLI only)
        """
        # Always show main message
        print_info(message)

        # Show technical detail only in appropriate context
        if technical_detail and self.console.config.show_technical_details:
            self.console.print_technical_detail(technical_detail)

    def success(self, message: str, metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        Log success message with optional performance metrics.

        Args:
            message: Success message
            metrics: Optional performance metrics (CLI only)
        """
        print_success(message)

        if metrics and self.console.config.show_performance_metrics:
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, dict) and "value" in metric_value:
                    self.console.print_performance_metric(
                        metric_name, metric_value["value"], metric_value.get("unit", "")
                    )
                else:
                    self.console.print_performance_metric(metric_name, metric_value)

    def warning(self, message: str, technical_detail: Optional[str] = None) -> None:
        """
        Log warning message with optional technical detail.

        Args:
            message: Warning message
            technical_detail: Technical detail (CLI only)
        """
        print_warning(message)

        if technical_detail and self.console.config.show_technical_details:
            self.console.print_technical_detail(f"Details: {technical_detail}", style="yellow")

    def error(self, message: str, exception: Optional[Exception] = None, show_traceback: bool = True) -> None:
        """
        Log error message with context-appropriate error handling.

        Args:
            message: Error message
            exception: Optional exception object
            show_traceback: Whether to show full traceback
        """
        if exception:
            if self.console.config.show_full_stack_traces and show_traceback:
                # Full error details for CLI
                print_error(message, exception)
                self.console.console.print_exception(show_locals=True)
            else:
                # Simple error for Jupyter
                error_detail = f"{type(exception).__name__}: {str(exception)}"
                print_error(f"{message} - {error_detail}")
        else:
            print_error(message)

    def start_operation(self, operation: str, description: Optional[str] = None) -> None:
        """
        Start timing an operation.

        Args:
            operation: Operation name
            description: Optional description
        """
        self._operation_start_times[operation] = time.time()

        if description:
            display_msg = f"{description}"
        else:
            display_msg = f"Starting {operation}"

        if self.console.config.show_technical_details:
            self.console.print_technical_detail(f"Operation: {operation}")

        self.info(display_msg)

    def complete_operation(self, operation: str, result_summary: Optional[str] = None) -> float:
        """
        Complete timing an operation and log results.

        Args:
            operation: Operation name
            result_summary: Optional result summary

        Returns:
            Operation duration in seconds
        """
        if operation not in self._operation_start_times:
            self.warning(f"Operation '{operation}' was not started with start_operation()")
            return 0.0

        duration = time.time() - self._operation_start_times[operation]
        del self._operation_start_times[operation]

        # Build success message
        success_msg = f"Completed {operation}"
        if result_summary:
            success_msg = f"{success_msg}: {result_summary}"

        # Include metrics if configured
        metrics = None
        if self.console.config.show_performance_metrics:
            metrics = {
                "Duration": {"value": duration, "unit": "s"},
                "Total Runtime": {"value": time.time() - self.start_time, "unit": "s"},
            }

        self.success(success_msg, metrics)
        return duration

    def create_progress_context(self, description: str = "Processing"):
        """
        Create a progress context manager.

        Args:
            description: Progress description

        Returns:
            Progress context manager
        """
        return self.console.create_progress(description)


# Global instances for easy access
_global_config: Optional[ContextConfig] = None
_global_console: Optional[ContextAwareConsole] = None


def get_context_config() -> ContextConfig:
    """Get global context configuration."""
    global _global_config
    if _global_config is None:
        _global_config = ContextDetector.get_context_config()
    return _global_config


def get_context_console() -> ContextAwareConsole:
    """Get global context-aware console."""
    global _global_console
    if _global_console is None:
        _global_console = ContextAwareConsole(get_context_config())
    return _global_console


def create_context_logger(name: str) -> ContextLogger:
    """
    Create a context logger for a module.

    Args:
        name: Logger name (typically module.operation)

    Returns:
        ContextLogger instance
    """
    return ContextLogger(name, get_context_console())


# Export public API
__all__ = [
    "ExecutionContext",
    "ContextConfig",
    "ContextDetector",
    "ContextAwareConsole",
    "ContextLogger",
    "get_context_config",
    "get_context_console",
    "create_context_logger",
]

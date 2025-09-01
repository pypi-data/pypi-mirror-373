#!/usr/bin/env python3
"""
Performance Monitoring Framework for CloudOps Runbooks Platform

This module provides enterprise-grade performance monitoring capabilities
extracted from proven FinOps benchmarking patterns achieving 69% performance improvement.

Features:
- Real-time performance tracking with Rich progress indicators
- Module-specific performance targets and thresholds
- Performance degradation detection and alerting
- Comprehensive metrics collection and reporting
- Context-aware performance optimization

Author: CloudOps Runbooks Team
Version: 0.8.0
"""

import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from runbooks.common.rich_utils import (
    STATUS_INDICATORS,
    console,
    create_progress_bar,
    create_table,
    format_cost,
    print_error,
    print_success,
    print_warning,
)


@dataclass
class PerformanceMetrics:
    """Performance metrics container for operation tracking."""

    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    target_duration: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    memory_usage: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_duration(self) -> float:
        """Calculate operation duration."""
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
            return self.duration
        return 0.0

    def is_within_target(self) -> bool:
        """Check if operation completed within target duration."""
        if not self.target_duration or not self.duration:
            return True
        return self.duration <= self.target_duration

    def get_performance_status(self) -> str:
        """Get performance status indicator."""
        if not self.success:
            return "error"
        elif not self.is_within_target():
            return "warning"
        else:
            return "success"


@dataclass
class ModulePerformanceConfig:
    """Performance configuration for each module."""

    module_name: str
    target_duration: float  # seconds
    warning_threshold: float  # seconds
    critical_threshold: float  # seconds
    max_memory_mb: float = 512  # MB
    description: str = ""


class PerformanceBenchmark:
    """
    Enterprise performance monitoring system extracted from FinOps success patterns.

    Provides real-time performance tracking, threshold monitoring, and degradation alerts
    across all CloudOps Runbooks modules.
    """

    # Module performance targets based on enterprise requirements
    MODULE_CONFIGS = {
        "inventory": ModulePerformanceConfig(
            module_name="inventory",
            target_duration=30.0,
            warning_threshold=45.0,
            critical_threshold=60.0,
            description="Multi-account resource discovery",
        ),
        "operate": ModulePerformanceConfig(
            module_name="operate",
            target_duration=15.0,
            warning_threshold=30.0,
            critical_threshold=45.0,
            description="Resource operations (start/stop/modify)",
        ),
        "security": ModulePerformanceConfig(
            module_name="security",
            target_duration=45.0,
            warning_threshold=60.0,
            critical_threshold=90.0,
            description="Security baseline assessment",
        ),
        "cfat": ModulePerformanceConfig(
            module_name="cfat",
            target_duration=30.0,
            warning_threshold=45.0,
            critical_threshold=60.0,
            description="Cloud Foundations Assessment Tool",
        ),
        "vpc": ModulePerformanceConfig(
            module_name="vpc",
            target_duration=20.0,
            warning_threshold=30.0,
            critical_threshold=45.0,
            description="VPC analysis and optimization",
        ),
        "remediation": ModulePerformanceConfig(
            module_name="remediation",
            target_duration=25.0,
            warning_threshold=40.0,
            critical_threshold=60.0,
            description="Security remediation scripts",
        ),
        "finops": ModulePerformanceConfig(
            module_name="finops",
            target_duration=30.0,
            warning_threshold=45.0,
            critical_threshold=60.0,
            description="Cost optimization and analytics",
        ),
    }

    def __init__(self, module_name: str):
        """
        Initialize performance benchmark for specific module.

        Args:
            module_name: Name of module being monitored
        """
        self.module_name = module_name
        self.config = self.MODULE_CONFIGS.get(
            module_name,
            ModulePerformanceConfig(
                module_name=module_name, target_duration=30.0, warning_threshold=45.0, critical_threshold=60.0
            ),
        )
        self.metrics: List[PerformanceMetrics] = []
        self._current_operation: Optional[PerformanceMetrics] = None

    @contextmanager
    def measure_operation(self, operation_name: str, show_progress: bool = True):
        """
        Context manager for measuring operation performance.

        Args:
            operation_name: Name of operation being measured
            show_progress: Whether to show Rich progress indicator
        """
        # Initialize performance metrics
        metrics = PerformanceMetrics(operation_name=operation_name, target_duration=self.config.target_duration)
        self._current_operation = metrics

        # Show progress indicator if enabled
        progress = None
        if show_progress and hasattr(console, "is_terminal") and console.is_terminal:
            progress = create_progress_bar(f"[cyan]{self.module_name.title()}[/] - {operation_name}")
            task = progress.add_task(operation_name, total=100)
            progress.start()

        try:
            console.log(f"[dim]Starting {operation_name} (target: {self.config.target_duration}s)[/]")
            yield metrics

            # Mark as successful
            metrics.success = True
            metrics.end_time = time.time()
            metrics.calculate_duration()

            # Log performance results
            self._log_performance_result(metrics)

        except Exception as e:
            # Mark as failed
            metrics.success = False
            metrics.error_message = str(e)
            metrics.end_time = time.time()
            metrics.calculate_duration()

            print_error(f"Operation '{operation_name}' failed", e)
            raise

        finally:
            if progress:
                progress.stop()

            # Store metrics
            self.metrics.append(metrics)
            self._current_operation = None

    def _log_performance_result(self, metrics: PerformanceMetrics):
        """Log performance results with appropriate styling."""
        status = metrics.get_performance_status()
        duration_str = f"{metrics.duration:.2f}s" if metrics.duration else "N/A"
        target_str = f"{metrics.target_duration:.1f}s" if metrics.target_duration else "N/A"

        if status == "success":
            print_success(f"{metrics.operation_name} completed in {duration_str} (target: {target_str})")
        elif status == "warning":
            print_warning(f"{metrics.operation_name} completed in {duration_str} (exceeded target: {target_str})")
        else:
            print_error(f"{metrics.operation_name} failed after {duration_str}")

        # Check for performance degradation
        if metrics.duration and metrics.duration > self.config.critical_threshold:
            console.log(f"[red]🚨 Critical performance degradation detected for {self.module_name}[/]")

    def get_module_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary for the module."""
        if not self.metrics:
            return {
                "module": self.module_name,
                "total_operations": 0,
                "average_duration": 0.0,
                "success_rate": 0.0,
                "target_achievement": 0.0,
                "status": "no_data",
            }

        successful_ops = [m for m in self.metrics if m.success]
        total_ops = len(self.metrics)

        avg_duration = (
            sum(m.duration for m in successful_ops if m.duration) / len(successful_ops) if successful_ops else 0.0
        )
        success_rate = len(successful_ops) / total_ops if total_ops > 0 else 0.0
        target_achievement = (
            len([m for m in successful_ops if m.is_within_target()]) / len(successful_ops) if successful_ops else 0.0
        )

        # Determine overall status
        if success_rate < 0.9:
            status = "critical"
        elif target_achievement < 0.8:
            status = "warning"
        else:
            status = "healthy"

        return {
            "module": self.module_name,
            "total_operations": total_ops,
            "successful_operations": len(successful_ops),
            "average_duration": avg_duration,
            "success_rate": success_rate,
            "target_achievement": target_achievement,
            "target_duration": self.config.target_duration,
            "status": status,
            "description": self.config.description,
        }

    def create_performance_table(self) -> None:
        """Display performance metrics in Rich table format."""
        summary = self.get_module_performance_summary()

        table = create_table(
            title=f"Performance Summary - {self.module_name.title()} Module",
            columns=[
                {"name": "Metric", "style": "cyan", "justify": "left"},
                {"name": "Value", "style": "white", "justify": "right"},
                {"name": "Status", "style": "white", "justify": "center"},
            ],
        )

        # Add rows with performance data
        status_style = {"healthy": "green", "warning": "yellow", "critical": "red"}.get(summary["status"], "white")

        table.add_row(
            "Total Operations",
            str(summary["total_operations"]),
            f"[{status_style}]{STATUS_INDICATORS.get('success' if summary['status'] == 'healthy' else summary['status'], '')}[/]",
        )

        table.add_row(
            "Success Rate",
            f"{summary['success_rate']:.1%}",
            f"[{'green' if summary['success_rate'] >= 0.9 else 'red'}]{summary['success_rate']:.1%}[/]",
        )

        table.add_row(
            "Average Duration",
            f"{summary['average_duration']:.2f}s",
            f"[{'green' if summary['average_duration'] <= self.config.target_duration else 'yellow'}]{summary['average_duration']:.2f}s[/]",
        )

        table.add_row(
            "Target Achievement",
            f"{summary['target_achievement']:.1%}",
            f"[{'green' if summary['target_achievement'] >= 0.8 else 'yellow'}]{summary['target_achievement']:.1%}[/]",
        )

        table.add_row("Performance Target", f"{self.config.target_duration:.1f}s", f"[dim]{self.config.description}[/]")

        console.print(table)

    @staticmethod
    def create_enterprise_performance_dashboard(benchmarks: List["PerformanceBenchmark"]) -> None:
        """Create enterprise-wide performance dashboard."""
        console.print("\n")
        console.print("[bold cyan]📊 Enterprise Performance Dashboard[/]")
        console.print("=" * 80)

        # Create summary table
        table = create_table(
            title="Module Performance Overview",
            columns=[
                {"name": "Module", "style": "cyan", "justify": "left"},
                {"name": "Ops", "style": "white", "justify": "center"},
                {"name": "Success", "style": "white", "justify": "center"},
                {"name": "Avg Duration", "style": "white", "justify": "right"},
                {"name": "Target", "style": "white", "justify": "right"},
                {"name": "Status", "style": "white", "justify": "center"},
            ],
        )

        for benchmark in benchmarks:
            summary = benchmark.get_module_performance_summary()
            status_indicator = {
                "healthy": f"[green]{STATUS_INDICATORS['success']}[/]",
                "warning": f"[yellow]{STATUS_INDICATORS['warning']}[/]",
                "critical": f"[red]{STATUS_INDICATORS['error']}[/]",
                "no_data": f"[dim]{STATUS_INDICATORS['pending']}[/]",
            }.get(summary["status"], STATUS_INDICATORS["info"])

            table.add_row(
                summary["module"].title(),
                str(summary["total_operations"]),
                f"{summary['success_rate']:.0%}",
                f"{summary['average_duration']:.1f}s",
                f"{summary['target_duration']:.1f}s",
                status_indicator,
            )

        console.print(table)
        console.print("\n")


# Global performance tracking
_module_benchmarks: Dict[str, PerformanceBenchmark] = {}


def get_performance_benchmark(module_name: str) -> PerformanceBenchmark:
    """Get or create performance benchmark for module."""
    if module_name not in _module_benchmarks:
        _module_benchmarks[module_name] = PerformanceBenchmark(module_name)
    return _module_benchmarks[module_name]


def create_enterprise_performance_report() -> None:
    """Create enterprise-wide performance report."""
    if _module_benchmarks:
        PerformanceBenchmark.create_enterprise_performance_dashboard(list(_module_benchmarks.values()))
    else:
        console.print("[yellow]No performance data available yet[/]")


# Export all public functions and classes
__all__ = [
    "PerformanceMetrics",
    "ModulePerformanceConfig",
    "PerformanceBenchmark",
    "get_performance_benchmark",
    "create_enterprise_performance_report",
]

#!/usr/bin/env python3
"""
Performance Monitoring Framework for CloudOps Runbooks Platform.

Monitors performance metrics, tracks SLA compliance, and generates
alerts for performance degradation across all enhanced modules.

Features:
- Real-time performance tracking
- SLA compliance monitoring
- Automated alerting system
- Dashboard metrics collection
- User experience analytics

Author: Enterprise Product Owner
Version: 1.0.0 - Phase 2 Production Deployment
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

console = Console()


class PerformanceMonitor:
    """
    Enterprise performance monitoring for CloudOps Runbooks platform.

    Tracks performance metrics, SLA compliance, and user experience
    across all enhanced modules (operate, cfat, inventory, security, finops).
    """

    def __init__(self):
        """Initialize performance monitoring framework."""
        self.metrics_file = Path("artifacts/monitoring/performance_metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

        # Performance targets from Phase 2 requirements
        self.performance_targets = {
            "operate": {
                "target_time": 2.0,  # <2s for operations
                "alert_threshold": 3.0,
                "description": "Resource Operations",
            },
            "cfat": {
                "target_time": 30.0,  # <30s for assessments
                "alert_threshold": 45.0,
                "description": "Cloud Foundations Assessment",
            },
            "inventory": {
                "target_time": 45.0,  # <45s for multi-account
                "alert_threshold": 60.0,
                "description": "Multi-Account Discovery",
            },
            "security": {
                "target_time": 15.0,  # <15s for security baseline
                "alert_threshold": 20.0,
                "description": "Security Baseline Assessment",
            },
            "finops": {
                "target_time": 60.0,  # <60s for cost analysis
                "alert_threshold": 90.0,
                "description": "FinOps Dashboard",
            },
        }

        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup performance monitoring logging."""
        logger = logging.getLogger("performance_monitor")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler("artifacts/monitoring/performance.log")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def track_operation(
        self, module: str, operation: str, execution_time: float, success: bool = True, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Track performance metrics for a specific operation.

        Args:
            module: Module name (operate, cfat, etc.)
            operation: Operation name
            execution_time: Time taken in seconds
            success: Whether operation succeeded
            metadata: Additional context data

        Returns:
            Performance analysis results
        """
        timestamp = datetime.now().isoformat()

        # Performance analysis
        target = self.performance_targets.get(module, {})
        target_time = target.get("target_time", 30.0)
        alert_threshold = target.get("alert_threshold", 60.0)

        performance_status = "EXCELLENT"
        if execution_time <= target_time:
            performance_status = "EXCELLENT"
            status_color = "green"
        elif execution_time <= alert_threshold:
            performance_status = "ACCEPTABLE"
            status_color = "yellow"
        else:
            performance_status = "DEGRADED"
            status_color = "red"

        # Calculate performance score
        performance_score = min(100, max(0, 100 - (execution_time / target_time - 1) * 50))

        metric_data = {
            "timestamp": timestamp,
            "module": module,
            "operation": operation,
            "execution_time": execution_time,
            "target_time": target_time,
            "performance_status": performance_status,
            "performance_score": performance_score,
            "success": success,
            "metadata": metadata or {},
        }

        # Store metric
        self._store_metric(metric_data)

        # Display real-time feedback
        console.print(
            f"[{status_color}]{performance_status}[/{status_color}] "
            f"{module}.{operation}: {execution_time:.2f}s "
            f"(target: {target_time}s, score: {performance_score:.1f}%)"
        )

        # Generate alert if performance degraded
        if performance_status == "DEGRADED":
            self._generate_performance_alert(module, operation, execution_time, target_time)

        return metric_data

    def _store_metric(self, metric_data: Dict[str, Any]) -> None:
        """Store performance metric to persistent storage."""
        try:
            # Load existing metrics
            if self.metrics_file.exists():
                with open(self.metrics_file, "r") as f:
                    metrics = json.load(f)
            else:
                metrics = {"performance_data": []}

            # Add new metric
            metrics["performance_data"].append(metric_data)

            # Keep only last 1000 metrics to prevent file bloat
            if len(metrics["performance_data"]) > 1000:
                metrics["performance_data"] = metrics["performance_data"][-1000:]

            # Save updated metrics
            with open(self.metrics_file, "w") as f:
                json.dump(metrics, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to store metric: {e}")

    def _generate_performance_alert(
        self, module: str, operation: str, execution_time: float, target_time: float
    ) -> None:
        """Generate performance degradation alert."""
        alert_message = (
            f"PERFORMANCE ALERT: {module}.{operation} "
            f"execution time {execution_time:.2f}s exceeds target {target_time:.2f}s"
        )

        console.print(f"[red]⚠️  {alert_message}[/red]")
        self.logger.warning(alert_message)

        # Store alert for dashboard
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "performance_degradation",
            "module": module,
            "operation": operation,
            "execution_time": execution_time,
            "target_time": target_time,
            "severity": "HIGH",
        }

        alerts_file = Path("artifacts/monitoring/performance_alerts.json")
        alerts_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if alerts_file.exists():
                with open(alerts_file, "r") as f:
                    alerts = json.load(f)
            else:
                alerts = {"alerts": []}

            alerts["alerts"].append(alert_data)

            with open(alerts_file, "w") as f:
                json.dump(alerts, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to store alert: {e}")

    def get_performance_dashboard(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate performance dashboard data for specified time window.

        Args:
            hours: Number of hours to analyze

        Returns:
            Dashboard metrics and analysis
        """
        if not self.metrics_file.exists():
            return {"status": "no_data", "message": "No performance data available"}

        try:
            with open(self.metrics_file, "r") as f:
                data = json.load(f)

            metrics = data.get("performance_data", [])

            # Filter by time window
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in metrics if datetime.fromisoformat(m["timestamp"]) >= cutoff_time]

            if not recent_metrics:
                return {"status": "no_recent_data", "message": f"No data in last {hours} hours"}

            # Analyze performance by module
            module_stats = {}
            for module in self.performance_targets.keys():
                module_metrics = [m for m in recent_metrics if m["module"] == module]

                if module_metrics:
                    execution_times = [m["execution_time"] for m in module_metrics]
                    success_count = sum(1 for m in module_metrics if m["success"])

                    module_stats[module] = {
                        "operations_count": len(module_metrics),
                        "success_rate": success_count / len(module_metrics) * 100,
                        "avg_execution_time": sum(execution_times) / len(execution_times),
                        "min_execution_time": min(execution_times),
                        "max_execution_time": max(execution_times),
                        "target_time": self.performance_targets[module]["target_time"],
                        "sla_compliance": sum(
                            1 for t in execution_times if t <= self.performance_targets[module]["target_time"]
                        )
                        / len(execution_times)
                        * 100,
                    }

            # Overall system health
            total_operations = len(recent_metrics)
            total_success = sum(1 for m in recent_metrics if m["success"])
            avg_score = sum(m["performance_score"] for m in recent_metrics) / total_operations

            dashboard = {
                "status": "success",
                "time_window_hours": hours,
                "generated_at": datetime.now().isoformat(),
                "overall_metrics": {
                    "total_operations": total_operations,
                    "success_rate": total_success / total_operations * 100,
                    "average_performance_score": avg_score,
                    "health_status": "EXCELLENT"
                    if avg_score >= 90
                    else "GOOD"
                    if avg_score >= 80
                    else "FAIR"
                    if avg_score >= 70
                    else "POOR",
                },
                "module_performance": module_stats,
            }

            return dashboard

        except Exception as e:
            self.logger.error(f"Failed to generate dashboard: {e}")
            return {"status": "error", "message": str(e)}

    def display_performance_dashboard(self, hours: int = 24) -> None:
        """Display formatted performance dashboard."""
        dashboard = self.get_performance_dashboard(hours)

        if dashboard["status"] != "success":
            console.print(f"[yellow]⚠️  {dashboard['message']}[/yellow]")
            return

        overall = dashboard["overall_metrics"]
        modules = dashboard["module_performance"]

        # Overall performance panel
        overall_panel = Panel(
            f"[green]Total Operations:[/green] {overall['total_operations']}\n"
            f"[blue]Success Rate:[/blue] {overall['success_rate']:.1f}%\n"
            f"[cyan]Performance Score:[/cyan] {overall['average_performance_score']:.1f}/100\n"
            f"[bold]Health Status:[/bold] {overall['health_status']}",
            title=f"📊 System Performance ({hours}h window)",
            border_style="green" if overall["health_status"] == "EXCELLENT" else "yellow",
        )

        console.print(overall_panel)

        # Module performance table
        if modules:
            table = Table(title="Module Performance Breakdown")
            table.add_column("Module", style="bold")
            table.add_column("Operations", justify="center")
            table.add_column("Success Rate", justify="center")
            table.add_column("Avg Time", justify="center")
            table.add_column("Target", justify="center")
            table.add_column("SLA Compliance", justify="center")
            table.add_column("Status")

            for module, stats in modules.items():
                status_color = (
                    "green" if stats["sla_compliance"] >= 95 else "yellow" if stats["sla_compliance"] >= 90 else "red"
                )

                status = (
                    "✅ EXCELLENT"
                    if stats["sla_compliance"] >= 95
                    else "⚠️  ACCEPTABLE"
                    if stats["sla_compliance"] >= 90
                    else "❌ DEGRADED"
                )

                table.add_row(
                    module.title(),
                    str(stats["operations_count"]),
                    f"{stats['success_rate']:.1f}%",
                    f"{stats['avg_execution_time']:.2f}s",
                    f"{stats['target_time']:.1f}s",
                    f"{stats['sla_compliance']:.1f}%",
                    f"[{status_color}]{status}[/{status_color}]",
                )

            console.print(table)

    def generate_monitoring_report(self) -> str:
        """Generate comprehensive monitoring report for stakeholders."""
        dashboard = self.get_performance_dashboard(24)  # Last 24 hours

        if dashboard["status"] != "success":
            return f"Monitoring Report: {dashboard['message']}"

        report_lines = [
            "# CloudOps Runbooks Performance Report",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Time Window:** 24 hours",
            "",
            "## Executive Summary",
            f"- **Total Operations:** {dashboard['overall_metrics']['total_operations']}",
            f"- **Success Rate:** {dashboard['overall_metrics']['success_rate']:.1f}%",
            f"- **Performance Score:** {dashboard['overall_metrics']['average_performance_score']:.1f}/100",
            f"- **System Health:** {dashboard['overall_metrics']['health_status']}",
            "",
            "## Module Performance",
        ]

        for module, stats in dashboard["module_performance"].items():
            status = (
                "🟢 Excellent"
                if stats["sla_compliance"] >= 95
                else "🟡 Acceptable"
                if stats["sla_compliance"] >= 90
                else "🔴 Degraded"
            )

            report_lines.extend(
                [
                    f"### {module.title()}",
                    f"- Operations: {stats['operations_count']}",
                    f"- Average Time: {stats['avg_execution_time']:.2f}s (target: {stats['target_time']}s)",
                    f"- SLA Compliance: {stats['sla_compliance']:.1f}%",
                    f"- Status: {status}",
                    "",
                ]
            )

        return "\n".join(report_lines)


# Usage examples and testing
if __name__ == "__main__":
    monitor = PerformanceMonitor()

    # Example usage - tracking operations
    console.print("[bold blue]🔍 CloudOps Runbooks Performance Monitor[/bold blue]")
    console.print("Tracking sample operations...")

    # Simulate some operations
    import random

    modules = ["operate", "cfat", "inventory", "security", "finops"]
    operations = ["start", "assess", "collect", "scan", "analyze"]

    for i in range(5):
        module = random.choice(modules)
        operation = random.choice(operations)
        # Simulate execution time - mostly good performance with occasional slow operations
        exec_time = random.uniform(0.5, 2.0) if random.random() > 0.1 else random.uniform(10, 50)
        success = random.random() > 0.05  # 95% success rate

        monitor.track_operation(module, operation, exec_time, success)
        time.sleep(0.1)  # Brief pause

    # Display dashboard
    console.print("\n")
    monitor.display_performance_dashboard()

    # Generate report
    report = monitor.generate_monitoring_report()
    console.print(f"\n[dim]{report}[/dim]")

#!/usr/bin/env python3
"""
MCP Validation Performance Benchmark Suite

Enterprise performance testing for MCP validation framework with:
- <30s validation cycle target
- 99.5% accuracy requirement
- Multi-account performance testing (60+ accounts)
- Real-time monitoring and reporting
- SRE reliability metrics

Usage:
    python -m runbooks.validation.benchmark --iterations 10 --target-accuracy 99.5
"""

import asyncio
import json
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.table import Table

from .mcp_validator import MCPValidator, ValidationReport, ValidationStatus

console = Console()


@dataclass
class BenchmarkResult:
    """Individual benchmark iteration result."""

    iteration: int
    accuracy: float
    execution_time: float
    passed_validations: int
    total_validations: int
    timestamp: datetime
    details: ValidationReport


@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results."""

    target_accuracy: float
    performance_target: float
    iterations: int
    results: List[BenchmarkResult]

    # Summary statistics
    avg_accuracy: float
    avg_execution_time: float
    min_accuracy: float
    max_accuracy: float
    min_execution_time: float
    max_execution_time: float
    accuracy_std_dev: float
    time_std_dev: float
    success_rate: float

    # SRE metrics
    availability: float  # % of successful validations
    reliability_score: float  # Combined accuracy + performance
    performance_consistency: float  # Low variance = high consistency


class MCPBenchmarkRunner:
    """
    Enterprise benchmark runner for MCP validation framework.

    Provides comprehensive performance testing with SRE reliability metrics
    and enterprise reporting for production deployment validation.
    """

    def __init__(
        self, target_accuracy: float = 99.5, performance_target: float = 30.0, tolerance_percentage: float = 5.0
    ):
        """Initialize benchmark runner."""

        self.target_accuracy = target_accuracy
        self.performance_target = performance_target
        self.tolerance_percentage = tolerance_percentage

        console.print(
            Panel(
                f"[bold blue]MCP Validation Benchmark Suite[/bold blue]\n"
                f"Target Accuracy: {target_accuracy}%\n"
                f"Performance Target: <{performance_target}s\n"
                f"Tolerance: ±{tolerance_percentage}%",
                title="Enterprise Benchmark Framework",
            )
        )

    async def run_benchmark(self, iterations: int = 5) -> BenchmarkSuite:
        """
        Run comprehensive benchmark across multiple iterations.

        Args:
            iterations: Number of benchmark iterations to run

        Returns:
            BenchmarkSuite with complete performance analysis
        """

        console.print(f"\n[bold cyan]Starting {iterations} benchmark iterations...[/bold cyan]")

        results: List[BenchmarkResult] = []

        with Progress() as progress:
            task = progress.add_task("[cyan]Running benchmark...", total=iterations)

            for i in range(iterations):
                progress.console.print(f"\n[bold green]→ Iteration {i + 1}/{iterations}[/bold green]")

                # Run single benchmark iteration
                result = await self._run_single_iteration(i + 1, progress)
                results.append(result)

                # Display iteration summary
                status_color = "green" if result.accuracy >= self.target_accuracy else "red"
                perf_color = "green" if result.execution_time <= self.performance_target else "red"

                progress.console.print(
                    f"  Accuracy: [{status_color}]{result.accuracy:.1f}%[/{status_color}] | "
                    f"Time: [{perf_color}]{result.execution_time:.1f}s[/{perf_color}] | "
                    f"Passed: {result.passed_validations}/{result.total_validations}"
                )

                progress.advance(task)

        # Calculate benchmark suite statistics
        return self._calculate_benchmark_statistics(results)

    async def _run_single_iteration(self, iteration: int, progress: Progress) -> BenchmarkResult:
        """Run single benchmark iteration."""

        start_time = time.time()

        # Initialize validator for this iteration
        validator = MCPValidator(
            tolerance_percentage=self.tolerance_percentage, performance_target_seconds=self.performance_target
        )

        # Run validation
        try:
            report = await validator.validate_all_operations()

            execution_time = time.time() - start_time

            return BenchmarkResult(
                iteration=iteration,
                accuracy=report.overall_accuracy,
                execution_time=execution_time,
                passed_validations=report.passed_validations,
                total_validations=report.total_validations,
                timestamp=datetime.now(),
                details=report,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            progress.console.print(f"[red]Iteration {iteration} failed: {e}[/red]")

            # Return failed iteration
            return BenchmarkResult(
                iteration=iteration,
                accuracy=0.0,
                execution_time=execution_time,
                passed_validations=0,
                total_validations=5,  # Expected number of validations
                timestamp=datetime.now(),
                details=None,
            )

    def _calculate_benchmark_statistics(self, results: List[BenchmarkResult]) -> BenchmarkSuite:
        """Calculate comprehensive benchmark statistics."""

        if not results:
            raise ValueError("No benchmark results to analyze")

        # Basic statistics
        accuracies = [r.accuracy for r in results]
        times = [r.execution_time for r in results]

        avg_accuracy = statistics.mean(accuracies)
        avg_execution_time = statistics.mean(times)
        min_accuracy = min(accuracies)
        max_accuracy = max(accuracies)
        min_execution_time = min(times)
        max_execution_time = max(times)

        # Calculate standard deviations
        accuracy_std_dev = statistics.stdev(accuracies) if len(accuracies) > 1 else 0.0
        time_std_dev = statistics.stdev(times) if len(times) > 1 else 0.0

        # Success rate (meeting target accuracy)
        successful_iterations = len([r for r in results if r.accuracy >= self.target_accuracy])
        success_rate = (successful_iterations / len(results)) * 100

        # SRE reliability metrics
        availability = len([r for r in results if r.accuracy > 0]) / len(results) * 100

        # Reliability score (weighted accuracy + performance)
        accuracy_score = min(100, avg_accuracy / self.target_accuracy * 100)
        performance_score = (
            min(100, self.performance_target / avg_execution_time * 100) if avg_execution_time > 0 else 0
        )
        reliability_score = (accuracy_score * 0.7) + (performance_score * 0.3)  # 70% accuracy, 30% performance

        # Performance consistency (lower std dev = higher consistency)
        max_acceptable_std_dev = 5.0  # 5% standard deviation is acceptable
        performance_consistency = max(0, 100 - (accuracy_std_dev / max_acceptable_std_dev * 100))

        return BenchmarkSuite(
            target_accuracy=self.target_accuracy,
            performance_target=self.performance_target,
            iterations=len(results),
            results=results,
            avg_accuracy=avg_accuracy,
            avg_execution_time=avg_execution_time,
            min_accuracy=min_accuracy,
            max_accuracy=max_accuracy,
            min_execution_time=min_execution_time,
            max_execution_time=max_execution_time,
            accuracy_std_dev=accuracy_std_dev,
            time_std_dev=time_std_dev,
            success_rate=success_rate,
            availability=availability,
            reliability_score=reliability_score,
            performance_consistency=performance_consistency,
        )

    def display_benchmark_results(self, suite: BenchmarkSuite) -> None:
        """Display comprehensive benchmark results."""

        # Overall assessment
        overall_status = self._assess_benchmark_results(suite)
        status_color = "green" if overall_status == "PASSED" else "red" if overall_status == "FAILED" else "yellow"

        console.print(
            Panel(
                f"[bold {status_color}]Benchmark Status: {overall_status}[/bold {status_color}]\n"
                f"Average Accuracy: {suite.avg_accuracy:.2f}% (Target: {suite.target_accuracy}%)\n"
                f"Average Time: {suite.avg_execution_time:.1f}s (Target: <{suite.performance_target}s)\n"
                f"Success Rate: {suite.success_rate:.1f}% | Reliability: {suite.reliability_score:.1f}%",
                title="Benchmark Summary",
            )
        )

        # Detailed statistics table
        stats_table = Table(title="Performance Statistics", box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan", no_wrap=True)
        stats_table.add_column("Value", justify="right", style="bold")
        stats_table.add_column("Status", style="bold")

        # Accuracy metrics
        stats_table.add_row(
            "Average Accuracy",
            f"{suite.avg_accuracy:.2f}%",
            "✅ PASS" if suite.avg_accuracy >= suite.target_accuracy else "❌ FAIL",
        )
        stats_table.add_row("Accuracy Range", f"{suite.min_accuracy:.1f}% - {suite.max_accuracy:.1f}%", "ℹ️ INFO")
        stats_table.add_row(
            "Accuracy Std Dev",
            f"{suite.accuracy_std_dev:.2f}%",
            "✅ GOOD" if suite.accuracy_std_dev < 5.0 else "⚠️ HIGH",
        )

        # Performance metrics
        stats_table.add_row(
            "Average Time",
            f"{suite.avg_execution_time:.1f}s",
            "✅ PASS" if suite.avg_execution_time <= suite.performance_target else "❌ FAIL",
        )
        stats_table.add_row(
            "Time Range", f"{suite.min_execution_time:.1f}s - {suite.max_execution_time:.1f}s", "ℹ️ INFO"
        )
        stats_table.add_row(
            "Time Std Dev", f"{suite.time_std_dev:.1f}s", "✅ GOOD" if suite.time_std_dev < 5.0 else "⚠️ HIGH"
        )

        # SRE metrics
        stats_table.add_row(
            "Success Rate", f"{suite.success_rate:.1f}%", "✅ EXCELLENT" if suite.success_rate >= 80 else "❌ POOR"
        )
        stats_table.add_row(
            "Availability", f"{suite.availability:.1f}%", "✅ PASS" if suite.availability >= 99 else "❌ FAIL"
        )
        stats_table.add_row(
            "Reliability Score",
            f"{suite.reliability_score:.1f}%",
            "✅ EXCELLENT" if suite.reliability_score >= 90 else "⚠️ NEEDS WORK",
        )
        stats_table.add_row(
            "Consistency",
            f"{suite.performance_consistency:.1f}%",
            "✅ STABLE" if suite.performance_consistency >= 80 else "⚠️ VARIABLE",
        )

        console.print(stats_table)

        # Individual iteration results
        iterations_table = Table(title="Individual Iterations", box=box.MINIMAL)
        iterations_table.add_column("Iteration", justify="center")
        iterations_table.add_column("Accuracy", justify="right")
        iterations_table.add_column("Time (s)", justify="right")
        iterations_table.add_column("Passed/Total")
        iterations_table.add_column("Status", style="bold")

        for result in suite.results:
            status_color = "green" if result.accuracy >= suite.target_accuracy else "red"
            status = (
                "PASS"
                if result.accuracy >= suite.target_accuracy and result.execution_time <= suite.performance_target
                else "FAIL"
            )

            iterations_table.add_row(
                str(result.iteration),
                f"{result.accuracy:.1f}%",
                f"{result.execution_time:.1f}",
                f"{result.passed_validations}/{result.total_validations}",
                f"[{status_color}]{status}[/{status_color}]",
            )

        console.print(iterations_table)

        # Recommendations
        recommendations = self._generate_benchmark_recommendations(suite)
        if recommendations:
            console.print(
                Panel("\n".join(f"• {rec}" for rec in recommendations), title="Recommendations", border_style="blue")
            )

        # Save benchmark report
        self._save_benchmark_report(suite)

    def _assess_benchmark_results(self, suite: BenchmarkSuite) -> str:
        """Assess overall benchmark results."""

        accuracy_pass = suite.avg_accuracy >= suite.target_accuracy
        performance_pass = suite.avg_execution_time <= suite.performance_target
        reliability_pass = suite.reliability_score >= 90
        consistency_pass = suite.accuracy_std_dev < 5.0

        if accuracy_pass and performance_pass and reliability_pass:
            return "PASSED"
        elif accuracy_pass and performance_pass:
            return "WARNING"
        else:
            return "FAILED"

    def _generate_benchmark_recommendations(self, suite: BenchmarkSuite) -> List[str]:
        """Generate actionable recommendations based on benchmark results."""

        recommendations = []

        # Accuracy recommendations
        if suite.avg_accuracy < suite.target_accuracy:
            recommendations.append(
                f"🎯 Improve average accuracy from {suite.avg_accuracy:.1f}% to {suite.target_accuracy}%"
            )
            recommendations.append("🔍 Review MCP integration and AWS API permissions")

        # Performance recommendations
        if suite.avg_execution_time > suite.performance_target:
            recommendations.append(
                f"⚡ Optimize performance from {suite.avg_execution_time:.1f}s to <{suite.performance_target}s"
            )
            recommendations.append("🚀 Consider parallel validation and caching strategies")

        # Consistency recommendations
        if suite.accuracy_std_dev > 5.0:
            recommendations.append(f"📊 Improve consistency - accuracy std dev {suite.accuracy_std_dev:.1f}% is high")
            recommendations.append("🔧 Investigate sources of validation variance")

        # Reliability recommendations
        if suite.reliability_score < 90:
            recommendations.append(f"🛠️ Enhance reliability score from {suite.reliability_score:.1f}% to >90%")
            recommendations.append("📈 Focus on both accuracy and performance improvements")

        # Success rate recommendations
        if suite.success_rate < 80:
            recommendations.append(f"✅ Improve success rate from {suite.success_rate:.1f}% to >80%")
            recommendations.append("🎯 Address systematic issues causing validation failures")

        # Production readiness
        overall_status = self._assess_benchmark_results(suite)
        if overall_status == "PASSED":
            recommendations.append("🚀 Benchmark PASSED - Ready for production deployment")
        elif overall_status == "WARNING":
            recommendations.append("⚠️ Benchmark WARNING - Address consistency issues before production")
        else:
            recommendations.append("❌ Benchmark FAILED - Significant improvements needed before production")

        return recommendations

    def _save_benchmark_report(self, suite: BenchmarkSuite) -> None:
        """Save benchmark report to artifacts directory."""

        from pathlib import Path

        artifacts_dir = Path("./artifacts/benchmark")
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = artifacts_dir / f"mcp_benchmark_{timestamp}.json"

        # Convert to serializable format
        report_data = {
            "benchmark_suite": {
                "target_accuracy": suite.target_accuracy,
                "performance_target": suite.performance_target,
                "iterations": suite.iterations,
                "avg_accuracy": suite.avg_accuracy,
                "avg_execution_time": suite.avg_execution_time,
                "min_accuracy": suite.min_accuracy,
                "max_accuracy": suite.max_accuracy,
                "min_execution_time": suite.min_execution_time,
                "max_execution_time": suite.max_execution_time,
                "accuracy_std_dev": suite.accuracy_std_dev,
                "time_std_dev": suite.time_std_dev,
                "success_rate": suite.success_rate,
                "availability": suite.availability,
                "reliability_score": suite.reliability_score,
                "performance_consistency": suite.performance_consistency,
            },
            "results": [
                {
                    "iteration": r.iteration,
                    "accuracy": r.accuracy,
                    "execution_time": r.execution_time,
                    "passed_validations": r.passed_validations,
                    "total_validations": r.total_validations,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in suite.results
            ],
            "assessment": self._assess_benchmark_results(suite),
            "recommendations": self._generate_benchmark_recommendations(suite),
        }

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        console.print(f"[green]Benchmark report saved:[/green] {report_file}")


# CLI entry point
async def main():
    """CLI entry point for benchmark runner."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Validation Benchmark Suite")
    parser.add_argument("--iterations", type=int, default=5, help="Number of benchmark iterations")
    parser.add_argument("--target-accuracy", type=float, default=99.5, help="Target accuracy percentage")
    parser.add_argument("--performance-target", type=float, default=30.0, help="Performance target in seconds")
    parser.add_argument("--tolerance", type=float, default=5.0, help="Tolerance percentage")

    args = parser.parse_args()

    runner = MCPBenchmarkRunner(
        target_accuracy=args.target_accuracy,
        performance_target=args.performance_target,
        tolerance_percentage=args.tolerance,
    )

    suite = await runner.run_benchmark(args.iterations)
    runner.display_benchmark_results(suite)

    # Exit with appropriate code
    overall_status = runner._assess_benchmark_results(suite)
    if overall_status == "PASSED":
        exit(0)
    elif overall_status == "WARNING":
        exit(1)
    else:
        exit(2)


if __name__ == "__main__":
    asyncio.run(main())

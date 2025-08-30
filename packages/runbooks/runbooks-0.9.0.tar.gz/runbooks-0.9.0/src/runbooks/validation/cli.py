#!/usr/bin/env python3
"""
MCP Validation CLI - Enterprise Command Line Interface

Provides command-line access to MCP validation framework with enterprise features:
- Comprehensive validation across all critical operations
- Real-time progress monitoring with Rich UI
- Detailed reporting and recommendations
- Performance benchmarking with <30s target
- Multi-profile AWS integration

Usage:
    python -m runbooks.validation.cli validate-all
    python -m runbooks.validation.cli validate-costs --profile billing
    python -m runbooks.validation.cli benchmark --target-accuracy 99.5
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .mcp_validator import MCPValidator, ValidationStatus

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="MCP Validator")
def cli():
    """Enterprise MCP Validation Framework - 99.5% Accuracy Target"""
    pass


@cli.command()
@click.option("--tolerance", default=5.0, help="Tolerance percentage for variance detection")
@click.option("--performance-target", default=30.0, help="Performance target in seconds")
@click.option("--save-report", is_flag=True, help="Save detailed report to artifacts")
@click.option("--profile", help="AWS profile override")
def validate_all(tolerance: float, performance_target: float, save_report: bool, profile: Optional[str]):
    """Run comprehensive validation across all critical operations."""

    console.print(
        Panel(
            "[bold blue]Enterprise MCP Validation Framework[/bold blue]\n"
            f"Target Accuracy: 99.5% | Tolerance: ±{tolerance}% | Performance: <{performance_target}s",
            title="MCP Validator",
        )
    )

    # Initialize validator
    profiles = None
    if profile:
        profiles = {"billing": profile, "management": profile, "centralised_ops": profile, "single_aws": profile}

    validator = MCPValidator(
        profiles=profiles, tolerance_percentage=tolerance, performance_target_seconds=performance_target
    )

    # Run validation
    try:
        report = asyncio.run(validator.validate_all_operations())

        # Display results
        validator.display_validation_report(report)

        # Exit code based on results
        if report.overall_accuracy >= 99.5:
            console.print("[bold green]✅ Validation PASSED - Deploy with confidence[/bold green]")
            sys.exit(0)
        elif report.overall_accuracy >= 95.0:
            console.print("[bold yellow]⚠️ Validation WARNING - Review before deployment[/bold yellow]")
            sys.exit(1)
        else:
            console.print("[bold red]❌ Validation FAILED - Address issues before deployment[/bold red]")
            sys.exit(2)

    except Exception as e:
        console.print(f"[bold red]Error running validation: {e}[/bold red]")
        sys.exit(3)


@cli.command()
@click.option("--profile", default="ams-admin-Billing-ReadOnlyAccess-909135376185", help="AWS billing profile")
@click.option("--tolerance", default=5.0, help="Cost variance tolerance percentage")
def validate_costs(profile: str, tolerance: float):
    """Validate Cost Explorer data accuracy."""

    console.print(
        Panel(
            f"[bold cyan]Cost Explorer Validation[/bold cyan]\nProfile: {profile}\nTolerance: ±{tolerance}%",
            title="Cost Validation",
        )
    )

    validator = MCPValidator(profiles={"billing": profile}, tolerance_percentage=tolerance)

    try:
        result = asyncio.run(validator.validate_cost_explorer())

        # Display result
        status_color = "green" if result.status == ValidationStatus.PASSED else "red"

        table = Table(title="Cost Validation Result", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")

        table.add_row("Status", f"[{status_color}]{result.status.value}[/{status_color}]")
        table.add_row("Accuracy", f"{result.accuracy_percentage:.2f}%")
        table.add_row("Execution Time", f"{result.execution_time:.2f}s")
        table.add_row("Timestamp", result.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        if result.error_message:
            table.add_row("Error", f"[red]{result.error_message}[/red]")

        console.print(table)

        # Variance details
        if result.variance_details:
            console.print(
                Panel(
                    f"Runbooks Total: {result.variance_details.get('details', {}).get('runbooks_total', 'N/A')}\n"
                    f"MCP Available: {result.variance_details.get('details', {}).get('mcp_available', 'N/A')}",
                    title="Variance Analysis",
                )
            )

        sys.exit(0 if result.status == ValidationStatus.PASSED else 1)

    except Exception as e:
        console.print(f"[bold red]Error validating costs: {e}[/bold red]")
        sys.exit(3)


@cli.command()
@click.option("--profile", default="ams-admin-ReadOnlyAccess-909135376185", help="AWS management profile")
def validate_organizations(profile: str):
    """Validate Organizations API data accuracy."""

    console.print(
        Panel(f"[bold cyan]Organizations Validation[/bold cyan]\nProfile: {profile}", title="Organizations Validation")
    )

    validator = MCPValidator(profiles={"management": profile})

    try:
        result = asyncio.run(validator.validate_organizations_data())

        # Display result
        status_color = "green" if result.status == ValidationStatus.PASSED else "red"

        table = Table(title="Organizations Validation Result", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")

        table.add_row("Status", f"[{status_color}]{result.status.value}[/{status_color}]")
        table.add_row("Accuracy", f"{result.accuracy_percentage:.2f}%")
        table.add_row("Execution Time", f"{result.execution_time:.2f}s")

        if result.variance_details:
            details = result.variance_details.get("details", {})
            table.add_row("Runbooks Accounts", str(details.get("runbooks_accounts", "N/A")))
            table.add_row("MCP Accounts", str(details.get("mcp_accounts", "N/A")))

        console.print(table)

        sys.exit(0 if result.status == ValidationStatus.PASSED else 1)

    except Exception as e:
        console.print(f"[bold red]Error validating organizations: {e}[/bold red]")
        sys.exit(3)


@cli.command()
@click.option("--target-accuracy", default=99.5, help="Target accuracy percentage")
@click.option("--iterations", default=5, help="Number of benchmark iterations")
@click.option("--performance-target", default=30.0, help="Performance target in seconds")
def benchmark(target_accuracy: float, iterations: int, performance_target: float):
    """Run performance benchmark for MCP validation framework."""

    console.print(
        Panel(
            f"[bold magenta]MCP Validation Benchmark[/bold magenta]\n"
            f"Target Accuracy: {target_accuracy}%\n"
            f"Iterations: {iterations}\n"
            f"Performance Target: <{performance_target}s",
            title="Benchmark Suite",
        )
    )

    validator = MCPValidator(performance_target_seconds=performance_target)

    results = []

    try:
        for i in range(iterations):
            console.print(f"\n[bold cyan]Iteration {i + 1}/{iterations}[/bold cyan]")

            report = asyncio.run(validator.validate_all_operations())
            results.append(report)

            console.print(
                f"Accuracy: {report.overall_accuracy:.1f}% | "
                f"Time: {report.execution_time:.1f}s | "
                f"Passed: {report.passed_validations}/{report.total_validations}"
            )

        # Benchmark summary
        avg_accuracy = sum(r.overall_accuracy for r in results) / len(results)
        avg_time = sum(r.execution_time for r in results) / len(results)
        success_rate = len([r for r in results if r.overall_accuracy >= target_accuracy]) / len(results) * 100

        summary_table = Table(title="Benchmark Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="bold")

        summary_table.add_row("Average Accuracy", f"{avg_accuracy:.2f}%")
        summary_table.add_row("Average Time", f"{avg_time:.2f}s")
        summary_table.add_row("Success Rate", f"{success_rate:.1f}%")
        summary_table.add_row("Target Met", "✅ YES" if avg_accuracy >= target_accuracy else "❌ NO")
        summary_table.add_row("Performance Met", "✅ YES" if avg_time <= performance_target else "❌ NO")

        console.print(summary_table)

        # Performance analysis
        if avg_accuracy >= target_accuracy and avg_time <= performance_target:
            console.print("[bold green]🎯 Benchmark PASSED - Production ready[/bold green]")
            sys.exit(0)
        else:
            console.print("[bold red]⚠️ Benchmark FAILED - Optimization needed[/bold red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Benchmark error: {e}[/bold red]")
        sys.exit(3)


@cli.command()
@click.option(
    "--operation",
    type=click.Choice(["costs", "organizations", "ec2", "security", "vpc"]),
    help="Specific operation to validate",
)
@click.option("--profile", help="AWS profile to use")
@click.option("--tolerance", default=5.0, help="Tolerance percentage")
def validate_single(operation: str, profile: Optional[str], tolerance: float):
    """Validate a single operation."""

    console.print(
        Panel(
            f"[bold cyan]Single Operation Validation[/bold cyan]\n"
            f"Operation: {operation.title()}\n"
            f"Profile: {profile or 'default'}\n"
            f"Tolerance: ±{tolerance}%",
            title="Single Validation",
        )
    )

    validator = MCPValidator(tolerance_percentage=tolerance)

    try:
        # Map operations to methods
        operation_map = {
            "costs": validator.validate_cost_explorer,
            "organizations": validator.validate_organizations_data,
            "ec2": validator.validate_ec2_inventory,
            "security": validator.validate_security_baseline,
            "vpc": validator.validate_vpc_analysis,
        }

        if operation not in operation_map:
            console.print(f"[red]Unknown operation: {operation}[/red]")
            sys.exit(1)

        result = asyncio.run(operation_map[operation]())

        # Display result
        status_color = {
            ValidationStatus.PASSED: "green",
            ValidationStatus.WARNING: "yellow",
            ValidationStatus.FAILED: "red",
            ValidationStatus.ERROR: "red",
            ValidationStatus.TIMEOUT: "red",
        }[result.status]

        table = Table(title=f"{operation.title()} Validation Result", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")

        table.add_row("Status", f"[{status_color}]{result.status.value}[/{status_color}]")
        table.add_row("Accuracy", f"{result.accuracy_percentage:.2f}%")
        table.add_row("Execution Time", f"{result.execution_time:.2f}s")
        table.add_row("Timestamp", result.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        if result.error_message:
            table.add_row("Error", f"[red]{result.error_message}[/red]")

        console.print(table)

        sys.exit(0 if result.status == ValidationStatus.PASSED else 1)

    except Exception as e:
        console.print(f"[bold red]Error validating {operation}: {e}[/bold red]")
        sys.exit(3)


@cli.command()
def status():
    """Show MCP validation framework status."""

    table = Table(title="MCP Validation Framework Status", box=box.ROUNDED)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details")

    # Check MCP integration
    try:
        from notebooks.mcp_integration import MCPIntegrationManager

        table.add_row("MCP Integration", "[green]✅ Available[/green]", "Ready for validation")
    except ImportError:
        table.add_row("MCP Integration", "[red]❌ Unavailable[/red]", "Install MCP dependencies")

    # Check AWS profiles
    profiles = [
        "ams-admin-Billing-ReadOnlyAccess-909135376185",
        "ams-admin-ReadOnlyAccess-909135376185",
        "ams-centralised-ops-ReadOnlyAccess-335083429030",
        "ams-shared-services-non-prod-ReadOnlyAccess-499201730520",
    ]

    for profile in profiles:
        try:
            import boto3

            session = boto3.Session(profile_name=profile)
            sts = session.client("sts")
            identity = sts.get_caller_identity()
            table.add_row(f"Profile: {profile[:20]}...", "[green]✅ Valid[/green]", f"Account: {identity['Account']}")
        except Exception as e:
            table.add_row(f"Profile: {profile[:20]}...", "[red]❌ Invalid[/red]", str(e)[:50])

    # Check validation components
    components = [
        ("Cost Explorer", "runbooks.finops"),
        ("Organizations", "runbooks.inventory"),
        ("Security", "runbooks.security"),
        ("VPC Analysis", "runbooks.vpc"),
    ]

    for name, module in components:
        try:
            __import__(module)
            table.add_row(f"Component: {name}", "[green]✅ Ready[/green]", "Module loaded")
        except ImportError:
            table.add_row(f"Component: {name}", "[red]❌ Missing[/red]", "Module not available")

    console.print(table)


if __name__ == "__main__":
    cli()

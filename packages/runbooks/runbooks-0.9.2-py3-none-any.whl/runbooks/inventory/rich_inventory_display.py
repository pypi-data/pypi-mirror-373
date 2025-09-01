#!/usr/bin/env python3
"""
Rich Inventory Display - Enhanced inventory presentation with Rich library

This module provides enterprise-grade inventory display functionality using
the Rich library for beautiful, consistent CLI output that works in both
terminal and Jupyter environments.

Features:
- Rich progress bars for long-running operations
- Professional table formatting for results
- Status indicators and color coding
- Performance timing with visual feedback
- Consistent branding with CloudOps theme

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from runbooks.common.rich_utils import (
    STATUS_INDICATORS,
    console,
    create_panel,
    create_progress_bar,
    create_table,
    print_info,
    print_status,
    print_success,
)


def display_inventory_header(operation: str, profile: str, accounts: int, regions: int) -> None:
    """
    Display inventory operation header with operation context.

    Args:
        operation: Type of inventory operation (EC2, RDS, S3, etc.)
        profile: AWS profile being used
        accounts: Number of accounts to scan
        regions: Number of regions to scan
    """
    header_text = f"""
[bold cyan]🔍 AWS {operation} Inventory Discovery[/bold cyan]

[yellow]Profile:[/yellow] {profile}
[yellow]Scope:[/yellow] {accounts} accounts × {regions} regions = {accounts * regions} total operations
[yellow]Started:[/yellow] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    console.print(create_panel(header_text.strip(), title="📊 Inventory Operation", border_style="cyan"))


def create_inventory_progress(total_operations: int, operation_name: str = "Scanning Resources") -> Progress:
    """
    Create a Rich progress bar for inventory operations.

    Args:
        total_operations: Total number of operations to perform
        operation_name: Name of the operation being performed

    Returns:
        Progress instance for tracking
    """
    return Progress(
        SpinnerColumn(spinner_name="dots", style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, style="cyan", complete_style="green"),
        TaskProgressColumn(),
        TextColumn("•"),
        TextColumn("[blue]{task.completed}/{task.total} operations"),
        console=console,
        transient=False,
    )


def display_ec2_inventory_results(
    instances: List[Dict[str, Any]], accounts: int, regions: int, timing_info: Optional[Dict] = None
) -> None:
    """
    Display EC2 inventory results in a professional Rich table format.

    Args:
        instances: List of EC2 instance data
        accounts: Number of accounts scanned
        regions: Number of regions scanned
        timing_info: Optional timing information
    """
    # Summary panel first
    total_instances = len(instances)

    # Count by state
    state_counts = {}
    for instance in instances:
        state = instance.get("State", {}).get("Name", "unknown")
        state_counts[state] = state_counts.get(state, 0) + 1

    # Create status breakdown
    status_text = ""
    for state, count in sorted(state_counts.items()):
        status_indicator = {
            "running": "🟢",
            "stopped": "🔴",
            "stopping": "🟡",
            "starting": "🟡",
            "terminated": "⚫",
            "terminating": "🟡",
        }.get(state, "⚪")

        status_text += f"{status_indicator} {state.title()}: {count}\n"

    summary_content = f"""
[bold cyan]EC2 Inventory Summary[/bold cyan]

[green]Total Instances Found:[/green] {total_instances}
[green]Accounts Scanned:[/green] {accounts}
[green]Regions Scanned:[/green] {regions}

[bold yellow]Instance States:[/bold yellow]
{status_text.strip()}
"""

    console.print(create_panel(summary_content.strip(), title="📊 Discovery Results", border_style="green"))

    # Detailed results table if instances found
    if instances:
        # Group instances by account for better organization
        instances_by_account = {}
        for instance in instances:
            account_id = instance.get("AccountId", "Unknown")
            if account_id not in instances_by_account:
                instances_by_account[account_id] = []
            instances_by_account[account_id].append(instance)

        # Create detailed table
        table = create_table(
            title="🖥️ EC2 Instance Details",
            columns=[
                {"name": "Account", "style": "cyan"},
                {"name": "Region", "style": "yellow"},
                {"name": "Instance ID", "style": "magenta"},
                {"name": "Type", "style": "blue"},
                {"name": "State", "style": "green"},
                {"name": "Name", "style": "white"},
            ],
            box_style=box.ROUNDED,
        )

        # Add rows (show first 50 instances to avoid overwhelming output)
        displayed_count = 0
        for account_id in sorted(instances_by_account.keys()):
            account_instances = instances_by_account[account_id][:10]  # Max 10 per account

            for instance in account_instances:
                if displayed_count >= 50:  # Overall limit
                    break

                # Extract instance information
                instance_id = instance.get("InstanceId", "N/A")
                instance_type = instance.get("InstanceType", "N/A")
                state = instance.get("State", {}).get("Name", "unknown")
                region = instance.get("Region", "N/A")

                # Get instance name from tags
                instance_name = "N/A"
                tags = instance.get("Tags", [])
                for tag in tags:
                    if tag.get("Key") == "Name":
                        instance_name = tag.get("Value", "N/A")
                        break

                # Style state with appropriate color
                state_styled = {
                    "running": "[green]🟢 Running[/green]",
                    "stopped": "[red]🔴 Stopped[/red]",
                    "stopping": "[yellow]🟡 Stopping[/yellow]",
                    "starting": "[yellow]🟡 Starting[/yellow]",
                    "terminated": "[dim]⚫ Terminated[/dim]",
                    "terminating": "[yellow]🟡 Terminating[/yellow]",
                }.get(state, f"[white]⚪ {state.title()}[/white]")

                table.add_row(
                    account_id[:12],  # Truncate account ID
                    region,
                    instance_id,
                    instance_type,
                    state_styled,
                    instance_name[:20] if instance_name != "N/A" else "N/A",  # Truncate long names
                )

                displayed_count += 1

        console.print(table)

        # Show truncation message if needed
        if total_instances > 50:
            console.print(f"\n[dim]Showing first 50 instances. Total found: {total_instances}[/dim]")

    # Timing information
    if timing_info:
        execution_time = timing_info.get("total_time", 0)
        print_success(f"✅ Inventory scan completed in {execution_time:.2f} seconds")

    print_info("💡 Use --output json or --output csv to export complete results")


def display_generic_inventory_results(
    resource_type: str, resources: List[Dict[str, Any]], accounts: int, regions: int
) -> None:
    """
    Display generic inventory results for any resource type.

    Args:
        resource_type: Type of AWS resource (RDS, S3, Lambda, etc.)
        resources: List of resource data
        accounts: Number of accounts scanned
        regions: Number of regions scanned
    """
    total_resources = len(resources)

    # Resource type icons
    resource_icons = {
        "rds": "🗄️",
        "s3": "🪣",
        "lambda": "⚡",
        "vpc": "🌐",
        "iam": "👤",
        "cloudformation": "📚",
        "ssm": "🔑",
        "route53": "🌍",
    }

    icon = resource_icons.get(resource_type.lower(), "📦")

    summary_content = f"""
[bold cyan]{resource_type.upper()} Inventory Summary[/bold cyan]

[green]Total Resources Found:[/green] {total_resources}
[green]Accounts Scanned:[/green] {accounts}
[green]Regions Scanned:[/green] {regions}
"""

    console.print(create_panel(summary_content.strip(), title=f"{icon} Discovery Results", border_style="green"))

    if total_resources > 0:
        print_success(f"✅ Found {total_resources} {resource_type} resources across {accounts} accounts")
    else:
        print_info(f"ℹ️ No {resource_type} resources found in the specified scope")


def display_inventory_error(error_message: str, suggestions: Optional[List[str]] = None) -> None:
    """
    Display inventory operation error with helpful suggestions.

    Args:
        error_message: Error message to display
        suggestions: Optional list of suggestions for resolution
    """
    error_content = f"[bold red]❌ Inventory Operation Failed[/bold red]\n\n{error_message}"

    if suggestions:
        error_content += "\n\n[yellow]💡 Suggestions:[/yellow]\n"
        for suggestion in suggestions:
            error_content += f"  • {suggestion}\n"

    console.print(create_panel(error_content.strip(), title="🚨 Error", border_style="red", padding=1))


def display_multi_resource_summary(
    resource_counts: Dict[str, int], accounts: int, regions: int, execution_time: float
) -> None:
    """
    Display summary for multi-resource inventory operations.

    Args:
        resource_counts: Dictionary of resource type to count
        accounts: Number of accounts scanned
        regions: Number of regions scanned
        execution_time: Total execution time in seconds
    """
    # Create summary table
    table = create_table(
        title="📊 Multi-Resource Inventory Summary",
        columns=[
            {"name": "Resource Type", "style": "cyan"},
            {"name": "Count", "style": "green", "justify": "right"},
            {"name": "Status", "style": "yellow"},
        ],
    )

    total_resources = 0
    for resource_type, count in sorted(resource_counts.items()):
        status = "✅ Found" if count > 0 else "⚪ None"
        table.add_row(resource_type.title(), str(count), status)
        total_resources += count

    console.print(table)

    # Overall summary
    summary_text = f"""
[bold green]Overall Summary[/bold green]

[cyan]Total Resources:[/cyan] {total_resources}
[cyan]Accounts Scanned:[/cyan] {accounts}
[cyan]Regions Scanned:[/cyan] {regions}
[cyan]Execution Time:[/cyan] {execution_time:.2f} seconds
[cyan]Performance:[/cyan] {(accounts * regions) / execution_time:.1f} operations/second
"""

    console.print(create_panel(summary_text.strip(), title="🎯 Inventory Complete", border_style="bright_blue"))


def display_account_tree(accounts_data: Dict[str, Dict]) -> None:
    """
    Display account and resource hierarchy as a Rich tree.

    Args:
        accounts_data: Nested dictionary of account -> resource data
    """
    tree = Tree("🏢 [bold cyan]AWS Organization Structure[/bold cyan]")

    for account_id, account_data in accounts_data.items():
        account_name = account_data.get("account_name", "Unknown")
        account_branch = tree.add(f"📊 [yellow]Account: {account_id}[/yellow] ({account_name})")

        # Add regions
        regions = account_data.get("regions", {})
        for region, region_data in regions.items():
            region_branch = account_branch.add(f"🌍 [green]Region: {region}[/green]")

            # Add resource counts
            for resource_type, count in region_data.get("resource_counts", {}).items():
                if count > 0:
                    icon = {"ec2": "🖥️", "rds": "🗄️", "s3": "🪣", "lambda": "⚡"}.get(resource_type, "📦")

                    region_branch.add(f"{icon} {resource_type.upper()}: [bold]{count}[/bold] resources")

    console.print(tree)


# Export public functions
__all__ = [
    "display_inventory_header",
    "create_inventory_progress",
    "display_ec2_inventory_results",
    "display_generic_inventory_results",
    "display_inventory_error",
    "display_multi_resource_summary",
    "display_account_tree",
]

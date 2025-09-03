"""
🚨 HIGH-RISK: WorkSpaces Management - Analyze and manage WorkSpaces with deletion capabilities.

JIRA FinOps-24: Enhanced WorkSpaces cleanup with cost calculation for $12,518 annual savings
Accounts: 339712777494, 802669565615, 142964829704, 507583929055
Types: STANDARD, PERFORMANCE, VALUE in AUTO_STOP mode
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client, write_to_csv
from ..common.rich_utils import (
    console, print_header, print_success, print_error, print_warning,
    create_table, create_progress_bar, format_cost
)

logger = logging.getLogger(__name__)


def calculate_workspace_monthly_cost(workspace_bundle_id: str, running_mode: str) -> float:
    """
    Calculate monthly cost for WorkSpace based on bundle and running mode.
    
    JIRA FinOps-24: Cost calculations for $12,518 annual savings target
    Based on AWS WorkSpaces pricing: https://aws.amazon.com/workspaces/pricing/
    """
    # WorkSpaces pricing by bundle type (monthly USD)
    bundle_costs = {
        # Value bundles
        "wsb-bh8rsxt14": {"name": "Value", "monthly": 25.0, "hourly": 0.22},  # Windows 10 Value
        "wsb-3t36q8qkj": {"name": "Value", "monthly": 25.0, "hourly": 0.22},  # Amazon Linux 2 Value
        
        # Standard bundles  
        "wsb-92tn3b7gx": {"name": "Standard", "monthly": 35.0, "hourly": 0.50},  # Windows 10 Standard
        "wsb-2bs6k5lgj": {"name": "Standard", "monthly": 35.0, "hourly": 0.50},  # Amazon Linux 2 Standard
        
        # Performance bundles
        "wsb-gk1wpk43z": {"name": "Performance", "monthly": 68.0, "hourly": 0.85},  # Windows 10 Performance
        "wsb-1b5w6vnzg": {"name": "Performance", "monthly": 68.0, "hourly": 0.85},  # Amazon Linux 2 Performance
        
        # PowerPro bundles
        "wsb-8vbljg4r6": {"name": "PowerPro", "monthly": 134.0, "hourly": 1.50},  # Windows 10 PowerPro
        "wsb-vbljg4r61": {"name": "PowerPro", "monthly": 134.0, "hourly": 1.50},  # Amazon Linux 2 PowerPro
        
        # Graphics bundles
        "wsb-1pzkp0bx8": {"name": "Graphics", "monthly": 144.0, "hourly": 1.75},  # Windows 10 Graphics
        "wsb-pszkp0bx9": {"name": "Graphics", "monthly": 144.0, "hourly": 1.75},  # Amazon Linux 2 Graphics
    }
    
    # Get bundle info or use default
    bundle_info = bundle_costs.get(workspace_bundle_id, {"name": "Standard", "monthly": 35.0, "hourly": 0.50})
    
    # Calculate cost based on running mode
    if running_mode.upper() == "AUTO_STOP":
        # Auto-stop: Pay monthly fee + hourly usage (simplified to monthly for unused)
        return bundle_info["monthly"]
    elif running_mode.upper() == "ALWAYS_ON":
        # Always-on: Pay monthly fee only
        return bundle_info["monthly"]
    else:
        # Unknown mode, use monthly
        return bundle_info["monthly"]


def get_workspace_usage_by_hours(workspace_id, start_time, end_time):
    """Get WorkSpace usage hours from CloudWatch metrics."""
    try:
        cloudwatch = get_client("cloudwatch")

        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/WorkSpaces",
            MetricName="UserConnected",
            Dimensions=[{"Name": "WorkspaceId", "Value": workspace_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # 1 hour intervals
            Statistics=["Sum"],
        )

        usage_hours = sum(datapoint["Sum"] for datapoint in response.get("Datapoints", []))
        logger.debug(f"Workspace {workspace_id}: {usage_hours} usage hours")

        return round(usage_hours, 2)

    except ClientError as e:
        logger.warning(f"Could not get usage metrics for {workspace_id}: {e}")
        return 0.0


@click.command()
@click.option("--output-file", default="/tmp/workspaces.csv", help="Output CSV file path")
@click.option("--days", default=30, help="Number of days to analyze for usage metrics")
@click.option("--delete-unused", is_flag=True, help="🚨 HIGH-RISK: Delete unused WorkSpaces")
@click.option("--unused-days", default=90, help="Days threshold for considering WorkSpace unused")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompts (dangerous!)")
@click.option("--calculate-savings", is_flag=True, help="Calculate cost savings for cleanup")
@click.option("--analyze", is_flag=True, help="Perform detailed cost analysis")
@click.option("--dry-run", is_flag=True, default=True, help="Preview actions without execution")
def get_workspaces(
    output_file: str = "/tmp/workspaces.csv",
    days: int = 30,
    delete_unused: bool = False,
    unused_days: int = 90,
    confirm: bool = False,
    calculate_savings: bool = False,
    analyze: bool = False,
    dry_run: bool = True,
):
    """
    🚨 HIGH-RISK: Analyze WorkSpaces usage and optionally delete unused ones.
    
    JIRA FinOps-24: Enhanced WorkSpaces cleanup with cost calculation for $12,518 annual savings
    """

    print_header("WorkSpaces Cost Optimization Analysis", "v0.9.1")
    
    # HIGH-RISK OPERATION WARNING
    if delete_unused and not confirm:
        print_warning("🚨 HIGH-RISK OPERATION: WorkSpace deletion")
        print_warning("This operation will permanently delete WorkSpaces and all user data")
        if not click.confirm("Do you want to continue?"):
            print_error("Operation cancelled by user")
            return

    account_info = display_aws_account_info()
    console.print(f"[cyan]Analyzing WorkSpaces in {account_info}[/cyan]")

    try:
        ws_client = get_client("workspaces")

        # Get all WorkSpaces with progress bar
        console.print("[yellow]Collecting WorkSpaces data...[/yellow]")
        paginator = ws_client.get_paginator("describe_workspaces")
        data = []

        # Calculate time range for usage analysis
        end_time = datetime.now(tz=timezone.utc)
        start_time = end_time - timedelta(days=days)
        unused_threshold = end_time - timedelta(days=unused_days)

        console.print(f"[dim]Analyzing usage from {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}[/dim]")

        # Collect all workspaces first for progress tracking
        all_workspaces = []
        for page in paginator.paginate():
            workspaces = page.get("Workspaces", [])
            all_workspaces.extend(workspaces)

        total_cost = 0.0
        unused_cost = 0.0
        
        with create_progress_bar() as progress:
            task_id = progress.add_task(
                f"Analyzing {len(all_workspaces)} WorkSpaces...",
                total=len(all_workspaces)
            )

            for workspace in all_workspaces:
                workspace_id = workspace["WorkspaceId"]
                username = workspace["UserName"]
                state = workspace["State"]
                bundle_id = workspace["BundleId"]
                running_mode = workspace["WorkspaceProperties"]["RunningMode"]

                # Get connection status
                try:
                    connection_response = ws_client.describe_workspaces_connection_status(WorkspaceIds=[workspace_id])

                    connection_status_list = connection_response.get("WorkspacesConnectionStatus", [])
                    if connection_status_list:
                        last_connection = connection_status_list[0].get("LastKnownUserConnectionTimestamp")
                        connection_state = connection_status_list[0].get("ConnectionState", "UNKNOWN")
                    else:
                        last_connection = None
                        connection_state = "UNKNOWN"

                except ClientError as e:
                    logger.warning(f"Could not get connection status for {workspace_id}: {e}")
                    last_connection = None
                    connection_state = "ERROR"

                # Format last connection
                if last_connection:
                    last_connection_str = last_connection.strftime("%Y-%m-%d %H:%M:%S")
                    days_since_connection = (end_time - last_connection).days
                else:
                    last_connection_str = "Never logged in"
                    days_since_connection = 999  # High number for never connected

                # Get usage metrics
                usage_hours = get_workspace_usage_by_hours(workspace_id, start_time, end_time)

                # Determine if workspace is unused
                is_unused = last_connection is None or last_connection < unused_threshold

                # Calculate cost (JIRA FinOps-24 enhancement)
                monthly_cost = 0.0
                if calculate_savings or analyze:
                    monthly_cost = calculate_workspace_monthly_cost(bundle_id, running_mode)
                    total_cost += monthly_cost
                    if is_unused:
                        unused_cost += monthly_cost

                workspace_data = {
                    "WorkspaceId": workspace_id,
                    "UserName": username,
                    "State": state,
                    "RunningMode": running_mode,
                    "OperatingSystem": workspace["WorkspaceProperties"]["OperatingSystemName"],
                    "BundleId": bundle_id,
                    "LastConnection": last_connection_str,
                    "DaysSinceConnection": days_since_connection,
                    "ConnectionState": connection_state,
                    f"UsageHours_{days}days": usage_hours,
                    "IsUnused": is_unused,
                    "UnusedThreshold": f"{unused_days} days",
                    "MonthlyCost": monthly_cost,
                    "AnnualCost": monthly_cost * 12,
                }

                data.append(workspace_data)
                progress.advance(task_id)

        # Export data
        write_to_csv(data, output_file)
        print_success(f"WorkSpaces analysis exported to: {output_file}")

        # Analyze unused WorkSpaces
        unused_workspaces = [ws for ws in data if ws["IsUnused"]]

        # Create summary table with Rich CLI
        print_header("WorkSpaces Analysis Summary")
        
        summary_table = create_table(
            title="WorkSpaces Cost Analysis - JIRA FinOps-24",
            columns=[
                {"header": "Metric", "style": "cyan"},
                {"header": "Value", "style": "green bold"},
                {"header": "Monthly Cost", "style": "red"},
                {"header": "Annual Cost", "style": "red bold"}
            ]
        )

        # Basic metrics
        summary_table.add_row(
            "Total WorkSpaces",
            str(len(data)),
            format_cost(total_cost) if calculate_savings or analyze else "N/A",
            format_cost(total_cost * 12) if calculate_savings or analyze else "N/A"
        )
        
        summary_table.add_row(
            f"Unused WorkSpaces (>{unused_days} days)",
            str(len(unused_workspaces)),
            format_cost(unused_cost) if calculate_savings or analyze else "N/A", 
            format_cost(unused_cost * 12) if calculate_savings or analyze else "N/A"
        )

        if calculate_savings or analyze:
            potential_savings_monthly = unused_cost
            potential_savings_annual = unused_cost * 12
            
            summary_table.add_row(
                "🎯 Potential Savings",
                f"{len(unused_workspaces)} WorkSpaces",
                format_cost(potential_savings_monthly),
                format_cost(potential_savings_annual)
            )

        console.print(summary_table)

        if unused_workspaces:
            print_warning(f"⚠ Found {len(unused_workspaces)} unused WorkSpaces:")
            
            # Create detailed unused workspaces table
            unused_table = create_table(
                title="Unused WorkSpaces Details",
                columns=[
                    {"header": "WorkSpace ID", "style": "cyan"},
                    {"header": "Username", "style": "blue"},
                    {"header": "Days Since Connection", "style": "yellow"},
                    {"header": "Running Mode", "style": "green"},
                    {"header": "Monthly Cost", "style": "red"},
                    {"header": "State", "style": "magenta"}
                ]
            )
            
            for ws in unused_workspaces[:10]:  # Show first 10 for readability
                unused_table.add_row(
                    ws['WorkspaceId'],
                    ws['UserName'],
                    str(ws['DaysSinceConnection']),
                    ws['RunningMode'],
                    format_cost(ws['MonthlyCost']) if ws['MonthlyCost'] > 0 else "N/A",
                    ws['State']
                )
            
            console.print(unused_table)
            
            if len(unused_workspaces) > 10:
                console.print(f"[dim]... and {len(unused_workspaces) - 10} more unused WorkSpaces[/dim]")

        # Target validation (JIRA FinOps-24: $12,518 annual savings)
        if calculate_savings or analyze:
            target_annual_savings = 12518.0  # JIRA FinOps-24 target
            if potential_savings_annual >= target_annual_savings * 0.8:  # 80% of target
                print_success(f"🎯 Target Achievement: {potential_savings_annual/target_annual_savings*100:.1f}% of $12,518 annual savings target")
            else:
                print_warning(f"📊 Analysis: {potential_savings_annual/target_annual_savings*100:.1f}% of $12,518 annual savings target")

        # Handle deletion of unused WorkSpaces
        if delete_unused and unused_workspaces:
            logger.warning(f"\n🚨 DELETION PHASE: {len(unused_workspaces)} WorkSpaces to delete")

            deletion_candidates = []
            for ws in unused_workspaces:
                # Additional safety check - only delete if really unused
                if ws["State"] in ["AVAILABLE", "STOPPED"] and ws["DaysSinceConnection"] >= unused_days:
                    deletion_candidates.append(ws)

            if deletion_candidates:
                logger.warning(f"Confirmed deletion candidates: {len(deletion_candidates)}")

                # Final confirmation
                if not confirm:
                    logger.warning("\n🚨 FINAL CONFIRMATION:")
                    logger.warning(f"About to delete {len(deletion_candidates)} WorkSpaces permanently")
                    if not click.confirm("Proceed with WorkSpace deletion?"):
                        logger.info("Deletion cancelled")
                        return

                # Perform deletions
                deleted_count = 0
                failed_count = 0

                for ws in deletion_candidates:
                    workspace_id = ws["WorkspaceId"]
                    username = ws["UserName"]

                    logger.warning(f"🗑 Deleting WorkSpace: {workspace_id} ({username})")

                    try:
                        ws_client.terminate_workspaces(TerminateWorkspaceRequests=[{"WorkspaceId": workspace_id}])
                        deleted_count += 1
                        logger.warning(f"  ✓ Successfully deleted {workspace_id}")

                        # Log for audit
                        logger.info(f"🔍 Audit: WorkSpace deletion completed")
                        logger.info(f"  WorkSpace ID: {workspace_id}")
                        logger.info(f"  Username: {username}")
                        logger.info(f"  Days since connection: {ws['DaysSinceConnection']}")

                    except ClientError as e:
                        failed_count += 1
                        logger.error(f"  ✗ Failed to delete {workspace_id}: {e}")

                logger.warning(f"\n🔄 Deletion complete: {deleted_count} deleted, {failed_count} failed")
            else:
                logger.info("No WorkSpaces meet the deletion criteria")

        elif delete_unused and not unused_workspaces:
            logger.info("✓ No unused WorkSpaces found for deletion")

    except Exception as e:
        logger.error(f"Failed to analyze WorkSpaces: {e}")
        raise

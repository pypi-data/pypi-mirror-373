"""
🚨 HIGH-RISK: WorkSpaces Management - Analyze and manage WorkSpaces with deletion capabilities.
"""

import logging
from datetime import datetime, timedelta, timezone

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client, write_to_csv

logger = logging.getLogger(__name__)


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
def get_workspaces(
    output_file: str = "/tmp/workspaces.csv",
    days: int = 30,
    delete_unused: bool = False,
    unused_days: int = 90,
    confirm: bool = False,
):
    """🚨 HIGH-RISK: Analyze WorkSpaces usage and optionally delete unused ones."""

    # HIGH-RISK OPERATION WARNING
    if delete_unused and not confirm:
        logger.warning("🚨 HIGH-RISK OPERATION: WorkSpace deletion")
        logger.warning("This operation will permanently delete WorkSpaces and all user data")
        if not click.confirm("Do you want to continue?"):
            logger.info("Operation cancelled by user")
            return

    logger.info(f"Analyzing WorkSpaces in {display_aws_account_info()}")

    try:
        ws_client = get_client("workspaces")

        # Get all WorkSpaces
        logger.info("Collecting WorkSpaces data...")
        paginator = ws_client.get_paginator("describe_workspaces")
        data = []

        # Calculate time range for usage analysis
        end_time = datetime.now(tz=timezone.utc)
        start_time = end_time - timedelta(days=days)
        unused_threshold = end_time - timedelta(days=unused_days)

        logger.info(f"Analyzing usage from {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")

        total_workspaces = 0
        for page in paginator.paginate():
            workspaces = page.get("Workspaces", [])
            total_workspaces += len(workspaces)

            for workspace in workspaces:
                workspace_id = workspace["WorkspaceId"]
                username = workspace["UserName"]
                state = workspace["State"]

                logger.info(f"Analyzing WorkSpace: {workspace_id} ({username})")

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

                workspace_data = {
                    "WorkspaceId": workspace_id,
                    "UserName": username,
                    "State": state,
                    "RunningMode": workspace["WorkspaceProperties"]["RunningMode"],
                    "OperatingSystem": workspace["WorkspaceProperties"]["OperatingSystemName"],
                    "BundleId": workspace["BundleId"],
                    "LastConnection": last_connection_str,
                    "DaysSinceConnection": days_since_connection,
                    "ConnectionState": connection_state,
                    f"UsageHours_{days}days": usage_hours,
                    "IsUnused": is_unused,
                    "UnusedThreshold": f"{unused_days} days",
                }

                data.append(workspace_data)

                # Log status
                if is_unused:
                    logger.warning(f"  ⚠ UNUSED: Last connection {days_since_connection} days ago")
                else:
                    logger.info(f"  ✓ Active: {usage_hours}h usage in {days} days")

        # Export data
        write_to_csv(data, output_file)
        logger.info(f"WorkSpaces analysis exported to: {output_file}")

        # Analyze unused WorkSpaces
        unused_workspaces = [ws for ws in data if ws["IsUnused"]]

        logger.info("\n=== ANALYSIS SUMMARY ===")
        logger.info(f"Total WorkSpaces: {len(data)}")
        logger.info(f"Unused WorkSpaces (>{unused_days} days): {len(unused_workspaces)}")

        if unused_workspaces:
            logger.warning(f"⚠ Found {len(unused_workspaces)} unused WorkSpaces:")
            for ws in unused_workspaces:
                logger.warning(
                    f"  - {ws['WorkspaceId']} ({ws['UserName']}) - {ws['DaysSinceConnection']} days since connection"
                )

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

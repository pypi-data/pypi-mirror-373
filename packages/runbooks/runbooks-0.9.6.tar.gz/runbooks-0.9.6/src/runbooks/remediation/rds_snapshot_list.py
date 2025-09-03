"""
RDS Snapshot Lifecycle Analysis - Storage cost optimization and lifecycle management.

Business Case: Enhanced snapshot analysis with cost calculation for $5K-24K annual savings
Target Accounts: 91893567291, 142964829704, 363435891329, 507583929055
Focus: 89 manual snapshots causing storage costs and operational clutter
Strategic Value: Operational cleanup and cost reduction through automated lifecycle management
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


def calculate_snapshot_age(create_time):
    """Calculate snapshot age in days."""
    if isinstance(create_time, str):
        create_time = datetime.fromisoformat(create_time.replace("Z", "+00:00"))

    now = datetime.now(tz=timezone.utc)
    age = (now - create_time).days
    return age


def estimate_snapshot_cost(allocated_storage, storage_type="gp2", days_old=1):
    """
    Estimate monthly snapshot storage cost with enhanced accuracy.
    
    JIRA FinOps-23: Enhanced cost estimation for $5K-24K annual savings target
    Based on AWS RDS snapshot pricing: https://aws.amazon.com/rds/pricing/
    """
    # RDS Snapshot storage cost per GB per month (USD)
    # Note: RDS snapshots are charged at $0.095/GB-month for all regions (simplified)
    snapshot_cost_per_gb_month = 0.095
    
    # Calculate base monthly cost
    monthly_cost = allocated_storage * snapshot_cost_per_gb_month

    # Pro-rate for actual age if less than a month
    if days_old < 30:
        return round((monthly_cost / 30) * days_old, 2)
    else:
        return round(monthly_cost, 2)


def calculate_manual_snapshot_savings(snapshots_data: List[Dict]) -> Dict[str, float]:
    """
    Calculate potential savings from manual snapshot cleanup.
    
    JIRA FinOps-23: Focuses on 89 manual snapshots for cost optimization
    """
    manual_snapshots = [s for s in snapshots_data if s.get("SnapshotType", "").lower() == "manual"]
    
    # Calculate costs by age groups
    old_manual_snapshots = [s for s in manual_snapshots if s.get("AgeDays", 0) >= 90]  # 3+ months old
    very_old_manual_snapshots = [s for s in manual_snapshots if s.get("AgeDays", 0) >= 180]  # 6+ months old
    
    total_manual_cost = sum(s.get("EstimatedMonthlyCost", 0) for s in manual_snapshots)
    old_manual_cost = sum(s.get("EstimatedMonthlyCost", 0) for s in old_manual_snapshots)
    very_old_manual_cost = sum(s.get("EstimatedMonthlyCost", 0) for s in very_old_manual_snapshots)
    
    return {
        "total_manual_snapshots": len(manual_snapshots),
        "total_manual_monthly_cost": total_manual_cost,
        "total_manual_annual_cost": total_manual_cost * 12,
        
        "old_manual_snapshots": len(old_manual_snapshots),  # 90+ days
        "old_manual_monthly_savings": old_manual_cost,
        "old_manual_annual_savings": old_manual_cost * 12,
        
        "very_old_manual_snapshots": len(very_old_manual_snapshots),  # 180+ days
        "very_old_manual_monthly_savings": very_old_manual_cost,
        "very_old_manual_annual_savings": very_old_manual_cost * 12,
    }


@click.command()
@click.option("--output-file", default="/tmp/rds_snapshots.csv", help="Output CSV file path")
@click.option("--old-days", default=30, help="Days threshold for considering snapshots old")
@click.option("--include-cost", is_flag=True, help="Include estimated cost analysis")
@click.option("--snapshot-type", help="Filter by snapshot type (automated, manual)")
@click.option("--manual-only", is_flag=True, help="Focus on manual snapshots only (JIRA FinOps-23)")
@click.option("--older-than", default=90, help="Focus on snapshots older than X days")
@click.option("--calculate-savings", is_flag=True, help="Calculate detailed cost savings analysis")
@click.option("--analyze", is_flag=True, help="Perform comprehensive cost analysis")
def get_rds_snapshot_details(output_file, old_days, include_cost, snapshot_type, manual_only, older_than, calculate_savings, analyze):
    """
    Analyze RDS snapshots for lifecycle management and cost optimization.
    
    JIRA FinOps-23: Enhanced RDS snapshots analysis for $5K-24K annual savings
    Focus on 89 manual snapshots causing storage costs and operational clutter
    """
    print_header("RDS Snapshot Cost Optimization Analysis", "v0.9.1")
    
    account_info = display_aws_account_info()
    console.print(f"[cyan]Analyzing RDS snapshots in {account_info}[/cyan]")

    try:
        rds = get_client("rds")

        # Get all snapshots
        console.print("[yellow]Collecting RDS snapshot data...[/yellow]")
        response = rds.describe_db_snapshots()
        snapshots = response.get("DBSnapshots", [])

        if not snapshots:
            print_warning("No RDS snapshots found")
            return

        console.print(f"[green]Found {len(snapshots)} RDS snapshots to analyze[/green]")

        # Apply filters
        if manual_only:
            original_count = len(snapshots)
            snapshots = [s for s in snapshots if s.get("SnapshotType", "").lower() == "manual"]
            console.print(f"[dim]JIRA FinOps-23 Filter: {len(snapshots)} manual snapshots (from {original_count} total)[/dim]")
            
        if snapshot_type:
            original_count = len(snapshots)
            snapshots = [s for s in snapshots if s.get("SnapshotType", "").lower() == snapshot_type.lower()]
            console.print(f"[dim]Filtered to {len(snapshots)} snapshots of type '{snapshot_type}'[/dim]")
            
        if older_than > 0:
            now = datetime.now(tz=timezone.utc)
            threshold_date = now - timedelta(days=older_than)
            original_count = len(snapshots)
            snapshots = [s for s in snapshots if s.get("SnapshotCreateTime") and s["SnapshotCreateTime"] < threshold_date]
            console.print(f"[dim]Age filter: {len(snapshots)} snapshots older than {older_than} days (from {original_count})[/dim]")

        data = []
        old_snapshots = []
        manual_snapshots = []
        automated_snapshots = []
        total_storage = 0
        total_estimated_cost = 0

        with create_progress_bar() as progress:
            task_id = progress.add_task(
                f"Analyzing {len(snapshots)} snapshots...",
                total=len(snapshots)
            )
            
            for i, snapshot in enumerate(snapshots, 1):
                snapshot_id = snapshot["DBSnapshotIdentifier"]

                create_time = snapshot.get("SnapshotCreateTime")
                age_days = calculate_snapshot_age(create_time) if create_time else 0
                allocated_storage = snapshot.get("AllocatedStorage", 0)
                storage_type = snapshot.get("StorageType", "gp2")
                snap_type = snapshot.get("SnapshotType", "unknown")

                snapshot_data = {
                    "DBSnapshotIdentifier": snapshot_id,
                    "DBInstanceIdentifier": snapshot.get("DBInstanceIdentifier", "Unknown"),
                    "SnapshotCreateTime": create_time.strftime("%Y-%m-%d %H:%M:%S") if create_time else "Unknown",
                    "AgeDays": age_days,
                    "SnapshotType": snap_type,
                    "Status": snapshot.get("Status", "Unknown"),
                    "Engine": snapshot.get("Engine", "Unknown"),
                    "EngineVersion": snapshot.get("EngineVersion", "Unknown"),
                    "StorageType": storage_type,
                    "AllocatedStorage": allocated_storage,
                    "Encrypted": snapshot.get("Encrypted", False),
                    "AvailabilityZone": snapshot.get("AvailabilityZone", "Unknown"),
                }

                # Enhanced cost analysis (JIRA FinOps-23)
                estimated_cost = 0.0
                if include_cost or calculate_savings or analyze:
                    if allocated_storage > 0:
                        estimated_cost = estimate_snapshot_cost(allocated_storage, storage_type, age_days)
                        total_estimated_cost += estimated_cost
                
                snapshot_data["EstimatedMonthlyCost"] = estimated_cost
                snapshot_data["EstimatedAnnualCost"] = estimated_cost * 12

                # Categorization for analysis
                if age_days >= old_days:
                    old_snapshots.append(snapshot_id)
                    snapshot_data["IsOld"] = True
                else:
                    snapshot_data["IsOld"] = False

                if snap_type.lower() == "manual":
                    manual_snapshots.append(snapshot_id)
                elif snap_type.lower() == "automated":
                    automated_snapshots.append(snapshot_id)

                total_storage += allocated_storage

                # Enhanced cleanup recommendations (JIRA FinOps-23)
                recommendations = []
                if age_days >= older_than and snap_type.lower() == "manual":
                    recommendations.append(f"HIGH PRIORITY: Manual snapshot >{older_than} days old")
                elif age_days >= old_days and snap_type.lower() == "manual":
                    recommendations.append(f"Consider deletion (>{old_days} days old)")
                if snap_type.lower() == "automated" and age_days > 35:  # AWS default retention
                    recommendations.append("Check retention policy")
                if not snapshot.get("Encrypted", False):
                    recommendations.append("Not encrypted")

                snapshot_data["Recommendations"] = "; ".join(recommendations) if recommendations else "None"
                data.append(snapshot_data)
                progress.advance(task_id)

        # Export results
        write_to_csv(data, output_file)
        print_success(f"RDS snapshot analysis exported to: {output_file}")

        # Enhanced cost analysis for JIRA FinOps-23
        if calculate_savings or analyze:
            savings_analysis = calculate_manual_snapshot_savings(data)
        
        # Create comprehensive summary table with Rich CLI
        print_header("RDS Snapshot Analysis Summary")
        
        summary_table = create_table(
            title="RDS Snapshot Cost Analysis - JIRA FinOps-23",
            columns=[
                {"header": "Metric", "style": "cyan"},
                {"header": "Count", "style": "green bold"},
                {"header": "Storage (GB)", "style": "yellow"},
                {"header": "Monthly Cost", "style": "red"},
                {"header": "Annual Cost", "style": "red bold"}
            ]
        )

        # Basic metrics
        summary_table.add_row(
            "Total Snapshots",
            str(len(data)),
            str(total_storage),
            format_cost(total_estimated_cost) if (include_cost or calculate_savings or analyze) else "N/A",
            format_cost(total_estimated_cost * 12) if (include_cost or calculate_savings or analyze) else "N/A"
        )
        
        summary_table.add_row(
            "Manual Snapshots",
            str(len(manual_snapshots)),
            str(sum(s["AllocatedStorage"] for s in data if s["SnapshotType"].lower() == "manual")),
            format_cost(savings_analysis["total_manual_monthly_cost"]) if (calculate_savings or analyze) else "N/A",
            format_cost(savings_analysis["total_manual_annual_cost"]) if (calculate_savings or analyze) else "N/A"
        )
        
        summary_table.add_row(
            "Automated Snapshots", 
            str(len(automated_snapshots)),
            str(sum(s["AllocatedStorage"] for s in data if s["SnapshotType"].lower() == "automated")),
            "Retention Policy",
            "Retention Policy"
        )
        
        summary_table.add_row(
            f"Old Snapshots (>{old_days} days)",
            str(len(old_snapshots)),
            str(sum(s["AllocatedStorage"] for s in data if s["IsOld"])),
            "Mixed Types",
            "Mixed Types"
        )

        # JIRA FinOps-23 specific analysis
        if calculate_savings or analyze:
            summary_table.add_row(
                f"🎯 Manual >{older_than}d (Cleanup Target)",
                str(savings_analysis["old_manual_snapshots"]),
                str(sum(s["AllocatedStorage"] for s in data if s["AgeDays"] >= older_than and s["SnapshotType"].lower() == "manual")),
                format_cost(savings_analysis["old_manual_monthly_savings"]),
                format_cost(savings_analysis["old_manual_annual_savings"])
            )

        console.print(summary_table)

        # Cleanup recommendations with Rich CLI
        cleanup_candidates = [s for s in data if s["IsOld"] and s["SnapshotType"].lower() == "manual"]
        high_priority_candidates = [s for s in data if s["AgeDays"] >= older_than and s["SnapshotType"].lower() == "manual"]
        
        if high_priority_candidates:
            print_warning(f"🎯 JIRA FinOps-23: {len(high_priority_candidates)} high-priority manual snapshots (>{older_than} days):")
            
            # Create detailed cleanup candidates table
            cleanup_table = create_table(
                title=f"High-Priority Manual Snapshots (>{older_than} days old)",
                columns=[
                    {"header": "Snapshot ID", "style": "cyan"},
                    {"header": "DB Instance", "style": "blue"},
                    {"header": "Age (Days)", "style": "yellow"},
                    {"header": "Size (GB)", "style": "green"},
                    {"header": "Monthly Cost", "style": "red"},
                    {"header": "Engine", "style": "magenta"}
                ]
            )
            
            for snap in high_priority_candidates[:15]:  # Show first 15 for readability
                cleanup_table.add_row(
                    snap['DBSnapshotIdentifier'],
                    snap['DBInstanceIdentifier'],
                    str(snap['AgeDays']),
                    str(snap['AllocatedStorage']),
                    format_cost(snap['EstimatedMonthlyCost']) if snap['EstimatedMonthlyCost'] > 0 else "N/A",
                    snap['Engine']
                )
            
            console.print(cleanup_table)
            
            if len(high_priority_candidates) > 15:
                console.print(f"[dim]... and {len(high_priority_candidates) - 15} more high-priority snapshots[/dim]")
                
        elif cleanup_candidates:
            print_warning(f"⚠ {len(cleanup_candidates)} old manual snapshots for review (>{old_days} days)")
        else:
            print_success("✓ No old manual snapshots found")

        # Target validation (JIRA FinOps-23: $5K-24K annual savings)
        if calculate_savings or analyze:
            target_min_annual = 5000.0
            target_max_annual = 24000.0
            actual_savings = savings_analysis["old_manual_annual_savings"]
            
            if actual_savings >= target_min_annual:
                if actual_savings <= target_max_annual:
                    print_success(f"🎯 Target Achievement: ${actual_savings:,.0f} within JIRA FinOps-23 range (${target_min_annual:,.0f}-${target_max_annual:,.0f})")
                else:
                    print_success(f"🎯 Target Exceeded: ${actual_savings:,.0f} exceeds JIRA FinOps-23 maximum target (${target_max_annual:,.0f})")
            else:
                percentage = (actual_savings / target_min_annual) * 100
                print_warning(f"📊 Analysis: ${actual_savings:,.0f} is {percentage:.1f}% of JIRA FinOps-23 minimum target (${target_min_annual:,.0f})")

        # Encryption status
        encrypted_count = sum(1 for s in data if s["Encrypted"])
        unencrypted_count = len(data) - encrypted_count
        logger.info(f"Encrypted snapshots: {encrypted_count}")
        if unencrypted_count > 0:
            logger.warning(f"⚠ Unencrypted snapshots: {unencrypted_count}")

        # Engine distribution
        engines = {}
        for snapshot in data:
            engine = snapshot["Engine"]
            engines[engine] = engines.get(engine, 0) + 1

        logger.info("Engine distribution:")
        for engine, count in sorted(engines.items()):
            logger.info(f"  {engine}: {count} snapshots")

    except Exception as e:
        logger.error(f"Failed to analyze RDS snapshots: {e}")
        raise

"""
RDS Snapshot Analysis - Analyze RDS snapshots for lifecycle management and cost optimization.
"""

import logging
from datetime import datetime, timedelta, timezone

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client, write_to_csv

logger = logging.getLogger(__name__)


def calculate_snapshot_age(create_time):
    """Calculate snapshot age in days."""
    if isinstance(create_time, str):
        create_time = datetime.fromisoformat(create_time.replace("Z", "+00:00"))

    now = datetime.now(tz=timezone.utc)
    age = (now - create_time).days
    return age


def estimate_snapshot_cost(allocated_storage, storage_type="gp2", days_old=1):
    """Estimate monthly snapshot storage cost (simplified)."""
    # Simplified cost estimation per GB per month
    cost_per_gb_month = {
        "gp2": 0.095,  # General Purpose SSD
        "gp3": 0.08,  # General Purpose SSD (gp3)
        "io1": 0.125,  # Provisioned IOPS SSD
        "io2": 0.125,  # Provisioned IOPS SSD
        "standard": 0.05,  # Magnetic
    }

    rate = cost_per_gb_month.get(storage_type.lower(), 0.095)  # Default to gp2
    monthly_cost = allocated_storage * rate

    # Pro-rate for actual age if less than a month
    if days_old < 30:
        return round((monthly_cost / 30) * days_old, 2)
    else:
        return round(monthly_cost, 2)


@click.command()
@click.option("--output-file", default="/tmp/rds_snapshots.csv", help="Output CSV file path")
@click.option("--old-days", default=30, help="Days threshold for considering snapshots old")
@click.option("--include-cost", is_flag=True, help="Include estimated cost analysis")
@click.option("--snapshot-type", help="Filter by snapshot type (automated, manual)")
def get_rds_snapshot_details(output_file, old_days, include_cost, snapshot_type):
    """Analyze RDS snapshots for lifecycle management and cost optimization."""
    logger.info(f"Analyzing RDS snapshots in {display_aws_account_info()}")

    try:
        rds = get_client("rds")

        # Get all snapshots
        logger.info("Collecting RDS snapshot data...")
        response = rds.describe_db_snapshots()
        snapshots = response.get("DBSnapshots", [])

        if not snapshots:
            logger.info("No RDS snapshots found")
            return

        logger.info(f"Found {len(snapshots)} RDS snapshots to analyze")

        # Filter by snapshot type if specified
        if snapshot_type:
            original_count = len(snapshots)
            snapshots = [s for s in snapshots if s.get("SnapshotType", "").lower() == snapshot_type.lower()]
            logger.info(f"Filtered to {len(snapshots)} snapshots of type '{snapshot_type}'")

        data = []
        old_snapshots = []
        manual_snapshots = []
        automated_snapshots = []
        total_storage = 0
        total_estimated_cost = 0

        for i, snapshot in enumerate(snapshots, 1):
            snapshot_id = snapshot["DBSnapshotIdentifier"]
            logger.info(f"Analyzing snapshot {i}/{len(snapshots)}: {snapshot_id}")

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

            # Cost analysis
            if include_cost and allocated_storage > 0:
                estimated_cost = estimate_snapshot_cost(allocated_storage, storage_type, age_days)
                snapshot_data["EstimatedMonthlyCost"] = estimated_cost
                total_estimated_cost += estimated_cost
            else:
                snapshot_data["EstimatedMonthlyCost"] = 0

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

            # Cleanup recommendations
            recommendations = []
            if age_days >= old_days and snap_type.lower() == "manual":
                recommendations.append(f"Consider deletion (>{old_days} days old)")
            if snap_type.lower() == "automated" and age_days > 35:  # AWS default retention
                recommendations.append("Check retention policy")
            if not snapshot.get("Encrypted", False):
                recommendations.append("Not encrypted")

            snapshot_data["Recommendations"] = "; ".join(recommendations) if recommendations else "None"

            data.append(snapshot_data)

            # Log summary for this snapshot
            status = "OLD" if age_days >= old_days else "RECENT"
            logger.info(f"  → {snap_type}, {age_days}d old, {allocated_storage}GB, {status}")

        # Export results
        write_to_csv(data, output_file)
        logger.info(f"RDS snapshot analysis exported to: {output_file}")

        # Summary report
        logger.info("\n=== ANALYSIS SUMMARY ===")
        logger.info(f"Total snapshots: {len(snapshots)}")
        logger.info(f"Manual snapshots: {len(manual_snapshots)}")
        logger.info(f"Automated snapshots: {len(automated_snapshots)}")
        logger.info(f"Old snapshots (>{old_days} days): {len(old_snapshots)}")
        logger.info(f"Total storage: {total_storage} GB")

        if include_cost:
            logger.info(f"Estimated total monthly cost: ${total_estimated_cost:.2f}")

        # Cleanup recommendations
        cleanup_candidates = [s for s in data if s["IsOld"] and s["SnapshotType"].lower() == "manual"]
        if cleanup_candidates:
            logger.warning(f"⚠ {len(cleanup_candidates)} old manual snapshots for review:")
            for snap in cleanup_candidates:
                logger.warning(
                    f"  - {snap['DBSnapshotIdentifier']}: {snap['AgeDays']} days old, {snap['AllocatedStorage']}GB"
                )
        else:
            logger.info("✓ No old manual snapshots found")

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

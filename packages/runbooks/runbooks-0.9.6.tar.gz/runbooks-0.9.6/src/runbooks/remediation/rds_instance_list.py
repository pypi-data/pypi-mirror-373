"""
RDS Instance Cost Analysis - Analyze RDS instances for cost optimization opportunities.
"""

import logging
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client, write_to_csv

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def get_rds_reserved_instances():
    """Get RDS reserved instances with caching for performance."""
    try:
        rds_client = get_client("rds")
        response = rds_client.describe_reserved_db_instances()
        logger.debug(f"Found {len(response.get('ReservedDBInstances', []))} reserved instances")
        return response
    except ClientError as e:
        logger.warning(f"Could not get reserved instances: {e}")
        return {"ReservedDBInstances": []}


def get_cloudwatch_metrics(cloudwatch, instance_id, metric_name, days=7):
    """Get CloudWatch metrics for RDS instance."""
    try:
        end_time = datetime.now(tz=timezone.utc)
        start_time = end_time - timedelta(days=days)

        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/RDS",
            MetricName=metric_name,
            Dimensions=[{"Name": "DBInstanceIdentifier", "Value": instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # Daily average
            Statistics=["Average", "Maximum"],
        )

        datapoints = response.get("Datapoints", [])
        if datapoints:
            avg_value = sum(dp["Average"] for dp in datapoints) / len(datapoints)
            max_value = max(dp["Maximum"] for dp in datapoints)
            return round(avg_value, 2), round(max_value, 2)
        else:
            logger.debug(f"No metrics data for {instance_id} - {metric_name}")
            return 0, 0

    except ClientError as e:
        logger.warning(f"Could not get {metric_name} metrics for {instance_id}: {e}")
        return 0, 0


@click.command()
@click.option("--output-file", default="/tmp/rds_cost_optimization.csv", help="Output CSV file path")
@click.option("--days", default=7, help="Number of days for CloudWatch metrics analysis")
@click.option("--include-storage", is_flag=True, help="Include detailed storage analysis")
def get_rds_list(output_file, days, include_storage):
    """Analyze RDS instances for cost optimization and performance insights."""
    logger.info(f"Analyzing RDS instances in {display_aws_account_info()}")

    try:
        rds = get_client("rds")
        cloudwatch = get_client("cloudwatch")

        # Get RDS instances
        logger.info("Collecting RDS instance data...")
        response = rds.describe_db_instances()
        instances = response.get("DBInstances", [])

        if not instances:
            logger.info("No RDS instances found")
            return

        logger.info(f"Found {len(instances)} RDS instances to analyze")

        # Get reserved instances for cost analysis
        reserved_instances = get_rds_reserved_instances()
        reserved_classes = {
            ri["DBInstanceClass"]
            for ri in reserved_instances.get("ReservedDBInstances", [])
            if ri.get("State") == "active"
        }

        data = []
        optimization_candidates = []

        for i, instance in enumerate(instances, 1):
            instance_id = instance["DBInstanceIdentifier"]
            instance_class = instance["DBInstanceClass"]

            logger.info(f"Analyzing instance {i}/{len(instances)}: {instance_id}")

            # Basic instance information
            instance_data = {
                "InstanceIdentifier": instance_id,
                "Engine": instance.get("Engine", "Unknown"),
                "EngineVersion": instance.get("EngineVersion", "Unknown"),
                "InstanceClass": instance_class,
                "StorageType": instance.get("StorageType", "Unknown"),
                "AllocatedStorage": instance.get("AllocatedStorage", 0),
                "MultiAZ": instance.get("MultiAZ", False),
                "DBInstanceStatus": instance.get("DBInstanceStatus", "Unknown"),
                "AvailabilityZone": instance.get("AvailabilityZone", "Unknown"),
            }

            # Determine purchase type
            purchase_type = "Reserved" if instance_class in reserved_classes else "On-Demand"
            instance_data["PurchaseType"] = purchase_type

            # Get CloudWatch metrics
            logger.debug(f"  Getting CloudWatch metrics for {instance_id}...")

            # CPU Utilization
            cpu_avg, cpu_max = get_cloudwatch_metrics(cloudwatch, instance_id, "CPUUtilization", days)
            instance_data[f"CPUUtilization_Avg_{days}d"] = cpu_avg
            instance_data[f"CPUUtilization_Max_{days}d"] = cpu_max

            # Memory metrics (FreeableMemory)
            mem_avg, mem_max = get_cloudwatch_metrics(cloudwatch, instance_id, "FreeableMemory", days)
            # Convert bytes to GB
            mem_avg_gb = round(mem_avg / (1024**3), 2) if mem_avg > 0 else 0
            mem_max_gb = round(mem_max / (1024**3), 2) if mem_max > 0 else 0
            instance_data[f"FreeMemory_Avg_GB_{days}d"] = mem_avg_gb
            instance_data[f"FreeMemory_Max_GB_{days}d"] = mem_max_gb

            # Storage analysis if requested
            if include_storage:
                try:
                    storage_response = rds.describe_db_instances(DBInstanceIdentifier=instance_id)
                    db_instance = storage_response["DBInstances"][0]
                    instance_data["StorageEncrypted"] = db_instance.get("StorageEncrypted", False)
                    instance_data["Iops"] = db_instance.get("Iops", "Standard")
                except ClientError as e:
                    logger.debug(f"Could not get storage details for {instance_id}: {e}")

            # Cost optimization analysis
            optimization_notes = []

            # Low CPU utilization suggests downsizing
            if cpu_avg < 20:
                optimization_notes.append(f"Low CPU utilization ({cpu_avg}%)")
                optimization_candidates.append(instance_id)

            # High memory availability suggests downsizing
            if mem_avg_gb > 2:  # More than 2GB free on average
                optimization_notes.append(f"High free memory ({mem_avg_gb}GB avg)")

            # Reserved instance recommendation
            if purchase_type == "On-Demand" and cpu_avg > 10:  # Active instance
                optimization_notes.append("Consider Reserved Instance")

            instance_data["OptimizationNotes"] = "; ".join(optimization_notes) if optimization_notes else "None"
            instance_data["OptimizationCandidate"] = instance_id in optimization_candidates

            data.append(instance_data)

            # Log summary for this instance
            logger.info(f"  → {instance_class}, CPU: {cpu_avg}%, Free Mem: {mem_avg_gb}GB, {purchase_type}")

        # Export results
        write_to_csv(data, output_file)
        logger.info(f"RDS analysis exported to: {output_file}")

        # Summary report
        logger.info("\n=== ANALYSIS SUMMARY ===")
        logger.info(f"Total RDS instances: {len(instances)}")
        logger.info(f"Reserved instances: {sum(1 for d in data if d['PurchaseType'] == 'Reserved')}")
        logger.info(f"On-Demand instances: {sum(1 for d in data if d['PurchaseType'] == 'On-Demand')}")
        logger.info(f"Optimization candidates: {len(optimization_candidates)}")

        if optimization_candidates:
            logger.warning(f"⚠ Instances with low utilization ({days}d avg):")
            for instance_id in optimization_candidates:
                instance_info = next(d for d in data if d["InstanceIdentifier"] == instance_id)
                cpu_avg = instance_info[f"CPUUtilization_Avg_{days}d"]
                logger.warning(f"  - {instance_id}: {cpu_avg}% CPU")
        else:
            logger.info("✓ No obvious optimization candidates found")

        # Engine distribution
        engines = {}
        for instance in data:
            engine = instance["Engine"]
            engines[engine] = engines.get(engine, 0) + 1

        logger.info("Engine distribution:")
        for engine, count in sorted(engines.items()):
            logger.info(f"  {engine}: {count} instances")

    except Exception as e:
        logger.error(f"Failed to analyze RDS instances: {e}")
        raise

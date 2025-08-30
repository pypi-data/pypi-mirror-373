"""
DynamoDB Cost Optimization - Analyze and optimize table settings for cost savings.
"""

import logging
from datetime import datetime, timedelta
from functools import lru_cache

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client, list_tables, write_to_csv

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def get_table_details(table_name):
    """Get DynamoDB table details with error handling."""
    try:
        dynamodb = get_client("dynamodb")
        return dynamodb.describe_table(TableName=table_name)["Table"]
    except ClientError as e:
        logger.error(f"Failed to get table details for {table_name}: {e}")
        raise


def update_table_billing_mode(table_name, billing_mode):
    """Update DynamoDB table billing mode."""
    try:
        dynamodb = get_client("dynamodb")
        dynamodb.update_table(TableName=table_name, BillingMode=billing_mode)
        logger.info(f"Updated {table_name} to {billing_mode} billing mode")
    except ClientError as e:
        logger.error(f"Failed to update {table_name} billing mode: {e}")
        raise


@lru_cache(maxsize=32)
def analyze_table(table_name):
    """Analyze table usage patterns and suggest cost optimizations."""
    try:
        table_details = get_table_details(table_name)

        # Get basic table info
        billing_mode_summary = table_details.get("BillingModeSummary", {})
        billing_mode = billing_mode_summary.get("BillingMode", "PROVISIONED")
        table_size_bytes = table_details.get("TableSizeBytes", 0)
        table_item_count = table_details.get("ItemCount", 0)

        # Get CloudWatch metrics for last 7 days
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)

        try:
            cloudwatch = get_client("cloudwatch")
            metrics = cloudwatch.get_metric_statistics(
                Namespace="AWS/DynamoDB",
                MetricName="ConsumedReadCapacityUnits",
                Dimensions=[{"Name": "TableName", "Value": table_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # Daily resolution
                Statistics=["Average"],
            )

            # Calculate average RCU usage
            datapoints = metrics.get("Datapoints", [])
            average_rcu = sum(dp["Average"] for dp in datapoints) / len(datapoints) if datapoints else 0

        except ClientError as e:
            logger.warning(f"Could not get CloudWatch metrics for {table_name}: {e}")
            average_rcu = 0

        # Get provisioned capacity if applicable
        provisioned_rcu = None
        if billing_mode == "PROVISIONED" and "ProvisionedThroughput" in table_details:
            provisioned_rcu = table_details["ProvisionedThroughput"].get("ReadCapacityUnits", 0)

        # Build analysis result
        analysis = {
            "Table": table_name,
            "Billing Mode": billing_mode,
            "Table Size": f"{table_size_bytes / (1024**3):.2f} GB" if table_size_bytes else "0 GB",
            "Item Count": table_item_count,
            "Average RCU": round(average_rcu, 2),
            "Provisioned RCU": provisioned_rcu,
            "Recommendations": [],
        }

        # Generate recommendations
        if billing_mode == "PROVISIONED" and provisioned_rcu and average_rcu < 0.9 * provisioned_rcu:
            analysis["Recommendations"].append("Consider lowering provisioned RCU to match actual usage")

        if average_rcu > 1000:
            analysis["Recommendations"].append("Consider enabling DynamoDB Accelerator (DAX) for high read workloads")

        # Storage optimization for large, infrequently accessed tables
        if table_size_bytes > 10 * (1024**3) and table_item_count > 0 and average_rcu / table_item_count < 0.1:
            table_class = table_details.get("TableClassSummary", {}).get("TableClass", "STANDARD")
            if table_class != "STANDARD_INFREQUENT_ACCESS":
                analysis["Recommendations"].append("Consider STANDARD_INFREQUENT_ACCESS for storage cost savings")

        return analysis

    except Exception as e:
        logger.error(f"Failed to analyze table {table_name}: {e}")
        return {
            "Table": table_name,
            "Error": str(e),
            "Recommendations": ["Unable to analyze - check table permissions"],
        }


@click.command()
@click.option("--apply", "-a", is_flag=True, help="Apply suggested optimizations")
@click.option("--output", "-o", default="/tmp/dynamodb_analysis.csv", help="Output CSV file path")
def dynamodb_analyze(apply=False, output="/tmp/dynamodb_analysis.csv"):
    """Analyze DynamoDB tables and suggest cost optimizations."""
    logger.info(f"Analyzing DynamoDB tables in {display_aws_account_info()}")

    try:
        table_names = list_tables()
        if not table_names:
            logger.info("No DynamoDB tables found")
            return

        logger.info(f"Found {len(table_names)} tables to analyze")

        # Analyze each table
        results = []
        for table_name in table_names:
            logger.info(f"Analyzing table: {table_name}")
            result = analyze_table(table_name)
            results.append(result)

            # Log recommendations
            if result.get("Recommendations"):
                for rec in result["Recommendations"]:
                    logger.info(f"  Recommendation: {rec}")
            else:
                logger.info("  No optimization recommendations")

        # Save results to CSV
        write_to_csv(results, output)
        logger.info(f"Analysis results saved to: {output}")

        # Apply optimizations if requested
        if apply:
            logger.info("Apply functionality not yet implemented")
            # TODO: Implement safe optimization application

    except Exception as e:
        logger.error(f"Failed to analyze DynamoDB tables: {e}")
        raise

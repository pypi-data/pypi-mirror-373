"""
DynamoDB Server-Side Encryption - Enable encryption at rest for all tables.
"""

import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client, list_tables

logger = logging.getLogger(__name__)


def get_table_sse_status(table_name):
    """Check if DynamoDB table has server-side encryption enabled."""
    try:
        dynamodb = get_client("dynamodb")
        response = dynamodb.describe_table(TableName=table_name)
        sse_description = response["Table"].get("SSEDescription")

        if sse_description and sse_description.get("Status") == "ENABLED":
            logger.debug(f"Table '{table_name}' has SSE enabled")
            return sse_description
        else:
            logger.debug(f"Table '{table_name}' does not have SSE enabled")
            return None

    except ClientError as e:
        logger.error(f"Failed to get SSE status for table '{table_name}': {e}")
        return None


def enable_table_sse(table_name):
    """Enable server-side encryption for DynamoDB table using AWS managed key."""
    kms_key_id = "alias/aws/dynamodb"  # Use AWS managed key for DynamoDB

    try:
        dynamodb = get_client("dynamodb")
        dynamodb.update_table(
            TableName=table_name,
            SSESpecification={
                "Enabled": True,
                "SSEType": "KMS",
                "KMSMasterKeyId": kms_key_id,
            },
        )
        logger.info(f"Enabled SSE for table '{table_name}' with AWS managed key")
        return True

    except ClientError as e:
        logger.error(f"Failed to enable SSE for table '{table_name}': {e}")
        return False


@click.command()
@click.option("--dry-run", is_flag=True, default=True, help="Preview mode - show actions without making changes")
def dynamodb_server_side_encryption(dry_run=True):
    """Check and enable server-side encryption for all DynamoDB tables."""
    logger.info(f"Checking DynamoDB encryption in {display_aws_account_info()}")

    try:
        table_names = list_tables()
        if not table_names:
            logger.info("No DynamoDB tables found")
            return

        logger.info(f"Found {len(table_names)} tables to check")

        # Track results
        tables_with_sse = []
        tables_without_sse = []
        tables_updated = []

        # Check each table
        for table_name in table_names:
            logger.info(f"Checking table: {table_name}")
            sse_status = get_table_sse_status(table_name)

            if sse_status:
                tables_with_sse.append(table_name)
                logger.info(f"  ✓ SSE already enabled")
            else:
                tables_without_sse.append(table_name)
                logger.info(f"  ✗ SSE not enabled")

                # Enable SSE if not in dry-run mode
                if not dry_run:
                    logger.info(f"  → Enabling SSE for table '{table_name}'...")
                    if enable_table_sse(table_name):
                        tables_updated.append(table_name)
                        logger.info(f"  ✓ Successfully enabled SSE")
                    else:
                        logger.error(f"  ✗ Failed to enable SSE")

        # Summary
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Tables with SSE: {len(tables_with_sse)}")
        logger.info(f"Tables without SSE: {len(tables_without_sse)}")

        if dry_run and tables_without_sse:
            logger.info(f"To enable SSE on {len(tables_without_sse)} tables, run with --no-dry-run")
        elif not dry_run:
            logger.info(f"Successfully enabled SSE on {len(tables_updated)} tables")

    except Exception as e:
        logger.error(f"Failed to process DynamoDB encryption: {e}")
        raise

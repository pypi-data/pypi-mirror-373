"""
Enterprise-Grade DynamoDB Operations Module.

Comprehensive DynamoDB resource management with Lambda support, environment configuration,
and full compatibility with original AWS Cloud Foundations scripts.

Migrated and enhanced from:
- aws/dynamodb_operations.py (with Lambda handlers, environment variables, and batch operations)

Author: CloudOps DevOps Engineer
Date: 2025-01-21
Version: 2.0.0 - Enterprise Enhancement
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from loguru import logger
from rich.console import Console

from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus

# Initialize Rich console for enhanced CLI output
console = Console()


class DynamoDBOperations(BaseOperation):
    """
    Enterprise-grade DynamoDB resource operations and lifecycle management.

    Handles all DynamoDB-related operational tasks including table management,
    data operations, backup/restore operations, and batch processing.
    Supports environment variable configuration and AWS Lambda execution.
    """

    service_name = "dynamodb"
    supported_operations = {
        "create_table",
        "delete_table",
        "put_item",
        "delete_item",
        "update_item",
        "batch_write_item",
        "create_backup",
        "restore_table",
        "update_table_throughput",
        "enable_point_in_time_recovery",
    }
    requires_confirmation = True

    def __init__(
        self,
        profile: Optional[str] = None,
        region: Optional[str] = None,
        dry_run: bool = False,
        table_name: Optional[str] = None,
    ):
        """
        Initialize DynamoDB operations with enhanced configuration support.

        Args:
            profile: AWS profile name (can be overridden by AWS_PROFILE env var)
            region: AWS region (can be overridden by AWS_REGION env var)
            dry_run: Dry run mode (can be overridden by DRY_RUN env var)
            table_name: Default table name (can be overridden by TABLE_NAME env var)
        """
        # Environment variable support for Lambda/Container deployment
        self.profile = profile or os.getenv("AWS_PROFILE")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.dry_run = dry_run or os.getenv("DRY_RUN", "false").lower() == "true"

        # DynamoDB-specific environment variables from original file
        self.default_table_name = table_name or os.getenv("TABLE_NAME", "employees")
        self.max_batch_items = int(os.getenv("MAX_BATCH_ITEMS", "100"))

        super().__init__(self.profile, self.region, self.dry_run)

        # Initialize DynamoDB resource (from original file approach)
        self.dynamodb_resource = None
        self.default_table = None

    def get_dynamodb_resource(self) -> Any:
        """Get DynamoDB resource with caching."""
        if not self.dynamodb_resource:
            self.dynamodb_resource = boto3.resource("dynamodb", region_name=self.region)
        return self.dynamodb_resource

    def get_table(self, table_name: Optional[str] = None) -> Any:
        """
        Get DynamoDB table resource.

        Based on original aws/dynamodb_operations.py table initialization.

        Args:
            table_name: Table name (uses default if not provided)

        Returns:
            DynamoDB table resource
        """
        table_name = table_name or self.default_table_name
        dynamodb = self.get_dynamodb_resource()
        return dynamodb.Table(table_name)

    def execute_operation(self, context: OperationContext, operation_type: str, **kwargs) -> List[OperationResult]:
        """
        Execute DynamoDB operation.

        Args:
            context: Operation context
            operation_type: Type of operation to execute
            **kwargs: Operation-specific arguments

        Returns:
            List of operation results
        """
        self.validate_context(context)

        if operation_type == "create_table":
            return self.create_table(context, **kwargs)
        elif operation_type == "delete_table":
            return self.delete_table(context, kwargs.get("table_name"))
        elif operation_type == "put_item":
            return self.put_item(context, **kwargs)
        elif operation_type == "delete_item":
            return self.delete_item(context, **kwargs)
        elif operation_type == "update_item":
            return self.update_item(context, **kwargs)
        elif operation_type == "batch_write_item":
            return self.batch_write_item(context, **kwargs)
        elif operation_type == "create_backup":
            return self.create_backup(context, **kwargs)
        elif operation_type == "restore_table":
            return self.restore_table(context, **kwargs)
        elif operation_type == "update_table_throughput":
            return self.update_table_throughput(context, **kwargs)
        elif operation_type == "enable_point_in_time_recovery":
            return self.enable_point_in_time_recovery(context, kwargs.get("table_name"))
        else:
            raise ValueError(f"Unsupported operation: {operation_type}")

    def create_table(
        self,
        context: OperationContext,
        table_name: str,
        key_schema: List[Dict[str, str]],
        attribute_definitions: List[Dict[str, str]],
        billing_mode: str = "PAY_PER_REQUEST",
        provisioned_throughput: Optional[Dict[str, int]] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> List[OperationResult]:
        """
        Create DynamoDB table.

        Args:
            context: Operation context
            table_name: Name of table to create
            key_schema: Primary key schema definition
            attribute_definitions: Attribute definitions
            billing_mode: PAY_PER_REQUEST or PROVISIONED
            provisioned_throughput: Read/write capacity units (if PROVISIONED)
            tags: Table tags

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        result = self.create_operation_result(context, "create_table", "dynamodb:table", table_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create DynamoDB table {table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            create_params = {
                "TableName": table_name,
                "KeySchema": key_schema,
                "AttributeDefinitions": attribute_definitions,
                "BillingMode": billing_mode,
            }

            if billing_mode == "PROVISIONED" and provisioned_throughput:
                create_params["ProvisionedThroughput"] = provisioned_throughput

            if tags:
                create_params["Tags"] = tags

            response = self.execute_aws_call(dynamodb_client, "create_table", **create_params)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully created DynamoDB table {table_name}")

        except ClientError as e:
            error_msg = f"Failed to create DynamoDB table {table_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_table(self, context: OperationContext, table_name: str) -> List[OperationResult]:
        """
        Delete DynamoDB table.

        Args:
            context: Operation context
            table_name: Name of table to delete

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        result = self.create_operation_result(context, "delete_table", "dynamodb:table", table_name)

        try:
            if not self.confirm_operation(context, table_name, "delete table"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete DynamoDB table {table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(dynamodb_client, "delete_table", TableName=table_name)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted DynamoDB table {table_name}")

        except ClientError as e:
            error_msg = f"Failed to delete DynamoDB table {table_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def put_item(
        self,
        context: OperationContext,
        table_name: str,
        item: Dict[str, Any],
        condition_expression: Optional[str] = None,
    ) -> List[OperationResult]:
        """
        Put item into DynamoDB table.

        Args:
            context: Operation context
            table_name: Target table name
            item: Item data to insert
            condition_expression: Optional condition for put operation

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        # Generate item identifier for tracking
        item_id = str(item.get("id", item.get("pk", "unknown")))

        result = self.create_operation_result(context, "put_item", "dynamodb:item", f"{table_name}#{item_id}")

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would put item in table {table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                put_params = {"TableName": table_name, "Item": item}

                if condition_expression:
                    put_params["ConditionExpression"] = condition_expression

                response = self.execute_aws_call(dynamodb_client, "put_item", **put_params)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully put item in table {table_name}")

        except ClientError as e:
            error_msg = f"Failed to put item in table {table_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_item(
        self,
        context: OperationContext,
        table_name: str,
        key: Dict[str, Any],
        condition_expression: Optional[str] = None,
    ) -> List[OperationResult]:
        """
        Delete item from DynamoDB table.

        Args:
            context: Operation context
            table_name: Source table name
            key: Primary key of item to delete
            condition_expression: Optional condition for delete operation

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        # Generate item identifier for tracking
        key_str = str(key.get("id", key.get("pk", "unknown")))

        result = self.create_operation_result(context, "delete_item", "dynamodb:item", f"{table_name}#{key_str}")

        try:
            if not self.confirm_operation(context, f"{table_name}#{key_str}", "delete item"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete item from table {table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                delete_params = {"TableName": table_name, "Key": key}

                if condition_expression:
                    delete_params["ConditionExpression"] = condition_expression

                response = self.execute_aws_call(dynamodb_client, "delete_item", **delete_params)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted item from table {table_name}")

        except ClientError as e:
            error_msg = f"Failed to delete item from table {table_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def update_item(
        self,
        context: OperationContext,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_attribute_values: Optional[Dict[str, Any]] = None,
        expression_attribute_names: Optional[Dict[str, str]] = None,
        condition_expression: Optional[str] = None,
    ) -> List[OperationResult]:
        """
        Update item in DynamoDB table.

        Args:
            context: Operation context
            table_name: Target table name
            key: Primary key of item to update
            update_expression: Update expression
            expression_attribute_values: Attribute values for expression
            expression_attribute_names: Attribute names for expression
            condition_expression: Optional condition for update operation

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        # Generate item identifier for tracking
        key_str = str(key.get("id", key.get("pk", "unknown")))

        result = self.create_operation_result(context, "update_item", "dynamodb:item", f"{table_name}#{key_str}")

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would update item in table {table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                update_params = {"TableName": table_name, "Key": key, "UpdateExpression": update_expression}

                if expression_attribute_values:
                    update_params["ExpressionAttributeValues"] = expression_attribute_values
                if expression_attribute_names:
                    update_params["ExpressionAttributeNames"] = expression_attribute_names
                if condition_expression:
                    update_params["ConditionExpression"] = condition_expression

                response = self.execute_aws_call(dynamodb_client, "update_item", **update_params)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully updated item in table {table_name}")

        except ClientError as e:
            error_msg = f"Failed to update item in table {table_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def batch_write_item(
        self, context: OperationContext, request_items: Dict[str, List[Dict[str, Any]]]
    ) -> List[OperationResult]:
        """
        Batch write items to DynamoDB tables.

        Args:
            context: Operation context
            request_items: Batch write request items by table name

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        result = self.create_operation_result(context, "batch_write_item", "dynamodb:batch", "batch_operation")

        try:
            if context.dry_run:
                item_count = sum(len(items) for items in request_items.values())
                logger.info(f"[DRY-RUN] Would batch write {item_count} items")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(dynamodb_client, "batch_write_item", RequestItems=request_items)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)

                processed_count = sum(len(items) for items in request_items.values())
                unprocessed_count = len(response.get("UnprocessedItems", {}))
                logger.info(
                    f"Successfully processed {processed_count - unprocessed_count} items, {unprocessed_count} unprocessed"
                )

        except ClientError as e:
            error_msg = f"Failed to batch write items: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def create_backup(
        self, context: OperationContext, table_name: str, backup_name: Optional[str] = None
    ) -> List[OperationResult]:
        """
        Create backup of DynamoDB table.

        Args:
            context: Operation context
            table_name: Table to backup
            backup_name: Name for backup (defaults to table_name_timestamp)

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        if not backup_name:
            backup_name = f"{table_name}_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        result = self.create_operation_result(context, "create_backup", "dynamodb:backup", backup_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create backup {backup_name} for table {table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(
                    dynamodb_client, "create_backup", TableName=table_name, BackupName=backup_name
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully created backup {backup_name} for table {table_name}")

        except ClientError as e:
            error_msg = f"Failed to create backup for table {table_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def restore_table(
        self,
        context: OperationContext,
        source_table_arn: str,
        target_table_name: str,
        restore_date_time: Optional[datetime] = None,
        billing_mode_override: Optional[str] = None,
    ) -> List[OperationResult]:
        """
        Restore DynamoDB table from backup or point-in-time.

        Args:
            context: Operation context
            source_table_arn: ARN of source table or backup
            target_table_name: Name for restored table
            restore_date_time: Point-in-time to restore to
            billing_mode_override: Override billing mode for restored table

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        result = self.create_operation_result(context, "restore_table", "dynamodb:table", target_table_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would restore table {target_table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                restore_params = {"TargetTableName": target_table_name, "SourceTableArn": source_table_arn}

                if restore_date_time:
                    restore_params["RestoreDateTime"] = restore_date_time
                if billing_mode_override:
                    restore_params["BillingModeOverride"] = billing_mode_override

                response = self.execute_aws_call(dynamodb_client, "restore_table_from_backup", **restore_params)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully initiated restore of table {target_table_name}")

        except ClientError as e:
            error_msg = f"Failed to restore table {target_table_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def update_table_throughput(
        self, context: OperationContext, table_name: str, provisioned_throughput: Dict[str, int]
    ) -> List[OperationResult]:
        """
        Update DynamoDB table throughput settings.

        Args:
            context: Operation context
            table_name: Table to update
            provisioned_throughput: New read/write capacity units

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        result = self.create_operation_result(context, "update_table_throughput", "dynamodb:table", table_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would update throughput for table {table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(
                    dynamodb_client, "update_table", TableName=table_name, ProvisionedThroughput=provisioned_throughput
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully updated throughput for table {table_name}")

        except ClientError as e:
            error_msg = f"Failed to update throughput for table {table_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def enable_point_in_time_recovery(self, context: OperationContext, table_name: str) -> List[OperationResult]:
        """
        Enable point-in-time recovery for DynamoDB table.

        Args:
            context: Operation context
            table_name: Table to enable PITR for

        Returns:
            List of operation results
        """
        dynamodb_client = self.get_client("dynamodb", context.region)

        result = self.create_operation_result(context, "enable_point_in_time_recovery", "dynamodb:table", table_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would enable PITR for table {table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(
                    dynamodb_client,
                    "update_continuous_backups",
                    TableName=table_name,
                    PointInTimeRecoverySpecification={"PointInTimeRecoveryEnabled": True},
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully enabled PITR for table {table_name}")

        except ClientError as e:
            error_msg = f"Failed to enable PITR for table {table_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def batch_write_items_enhanced(
        self, context: OperationContext, table_name: Optional[str] = None, batch_size: Optional[int] = None
    ) -> List[OperationResult]:
        """
        Batch write multiple items efficiently using resource-based approach.

        Enhanced from original aws/dynamodb_operations.py batch_write_items functionality.

        Args:
            context: Operation context
            table_name: Target table name (uses default if not provided)
            batch_size: Number of items to write (uses MAX_BATCH_ITEMS env var if not provided)

        Returns:
            List of operation results
        """
        # Environment variable support from original file
        table_name = table_name or self.default_table_name
        batch_size = batch_size or self.max_batch_items

        # Use resource-based approach from original file
        table = self.get_table(table_name)

        result = self.create_operation_result(
            context, "batch_write_items", "dynamodb:table", f"{table_name}#{batch_size}items"
        )

        try:
            logger.info(f"🚀 Starting batch write with {batch_size} items...")

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would batch write {batch_size} items to table {table_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            # Use batch_writer from original file
            with table.batch_writer() as batch:
                for i in range(batch_size):
                    batch.put_item(
                        Item={
                            "emp_id": str(i),
                            "name": f"Name-{i}",
                            "salary": 50000 + i * 100,  # Incremental salary from original
                        }
                    )

            result.response_data = {"items_written": batch_size, "table": table_name}
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"✅ Batch write completed successfully with {batch_size} items.")

        except ClientError as e:
            error_msg = f"❌ AWS Client Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except BotoCoreError as e:
            error_msg = f"❌ BotoCore Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except Exception as e:
            error_msg = f"❌ Unexpected Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]


# ==============================
# AWS LAMBDA HANDLERS
# ==============================


def lambda_handler_dynamodb_operations(event, context):
    """
    AWS Lambda handler for DynamoDB operations.

    Based on original aws/dynamodb_operations.py Lambda handler with enhanced action routing.

    Args:
        event (dict): AWS Lambda event with action details
        context: AWS Lambda context object
    """
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate.base import OperationContext

        action = event.get("action")
        emp_id = event.get("emp_id")
        name = event.get("name")
        salary = event.get("salary", 0)
        batch_size = int(event.get("batch_size", os.getenv("MAX_BATCH_ITEMS", "100")))
        table_name = event.get("table_name", os.getenv("TABLE_NAME", "employees"))
        region = event.get("region", os.getenv("AWS_REGION", "us-east-1"))

        dynamodb_ops = DynamoDBOperations(table_name=table_name)
        account = AWSAccount(account_id="current", account_name="lambda-execution")
        operation_context = OperationContext(
            account=account, region=region, operation_type=action, resource_types=["dynamodb:table"], dry_run=False
        )

        if action == "put":
            results = dynamodb_ops.put_item(
                operation_context, table_name=table_name, emp_id=emp_id, name=name, salary=salary
            )
            return {"statusCode": 200, "body": f"Item {emp_id} inserted."}

        elif action == "delete":
            results = dynamodb_ops.delete_item(operation_context, table_name=table_name, key={"emp_id": emp_id})
            if results and results[0].success:
                item = results[0].response_data
                return {"statusCode": 200, "body": f"Item {item} deleted."}
            else:
                return {"statusCode": 500, "body": "Failed to delete item"}

        elif action == "batch_write":
            results = dynamodb_ops.batch_write_items_enhanced(
                operation_context, table_name=table_name, batch_size=batch_size
            )
            return {"statusCode": 200, "body": "Batch write completed."}

        else:
            raise ValueError("Invalid action. Use 'put', 'delete', or 'batch_write'.")

    except Exception as e:
        logger.error(f"❌ Lambda Error: {e}")
        return {"statusCode": 500, "body": str(e)}


# ==============================
# SCRIPT ENTRY POINT (CLI Support)
# ==============================


def main():
    """
    Main entry point for standalone execution (CLI or Docker).

    Provides compatibility with original AWS script execution patterns.
    """
    import sys

    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python dynamodb_operations.py <operation> [args...][/yellow]")
        console.print("[blue]Operations: put, delete, batch-write, create-table, backup-table[/blue]")
        sys.exit(1)

    operation = sys.argv[1]

    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate.base import OperationContext

        dynamodb_ops = DynamoDBOperations()
        account = AWSAccount(account_id="current", account_name="cli-execution")
        operation_context = OperationContext(
            account=account,
            region=os.getenv("AWS_REGION", "us-east-1"),
            operation_type=operation.replace("-", "_"),
            resource_types=["dynamodb"],
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
        )

        if operation == "put":
            # Example: put item with environment variables or defaults
            results = dynamodb_ops.put_item(operation_context, emp_id="2", name="John Doe", salary=75000)

        elif operation == "delete":
            # Example: delete item
            results = dynamodb_ops.delete_item(operation_context, key={"emp_id": "2"})

        elif operation == "batch-write":
            # Example: batch write items
            batch_size = int(os.getenv("MAX_BATCH_ITEMS", "100"))
            results = dynamodb_ops.batch_write_items_enhanced(operation_context, batch_size=batch_size)

        elif operation == "create-table":
            # Example: create table
            table_name = os.getenv("TABLE_NAME", "employees")
            key_schema = [{"AttributeName": "emp_id", "KeyType": "HASH"}]
            attribute_definitions = [{"AttributeName": "emp_id", "AttributeType": "S"}]
            results = dynamodb_ops.create_table(operation_context, table_name, key_schema, attribute_definitions)

        elif operation == "backup-table":
            # Example: backup table
            table_name = os.getenv("TABLE_NAME", "employees")
            results = dynamodb_ops.create_backup(operation_context, table_name)

        else:
            raise ValueError(f"Unknown operation: {operation}")

        # Print results with Rich formatting
        for result in results:
            if result.success:
                console.print(f"[green]✅ {result.operation_type} completed successfully[/green]")
                if result.response_data:
                    console.print(f"[blue]   Data: {json.dumps(result.response_data, default=str, indent=2)}[/blue]")
            else:
                console.print(f"[red]❌ {result.operation_type} failed: {result.error_message}[/red]")

    except Exception as e:
        logger.error(f"Error during operation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

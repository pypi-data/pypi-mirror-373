"""
CloudWatch Operations Module.

Provides comprehensive CloudWatch resource management capabilities including
log group management, retention policies, and monitoring configuration.

Migrated and enhanced from:
- inventory/update_cloudwatch_logs_retention_policy.py
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus


class CloudWatchOperations(BaseOperation):
    """
    CloudWatch resource operations and lifecycle management.

    Handles all CloudWatch-related operational tasks including log group management,
    retention policy updates, and monitoring configuration.
    """

    service_name = "cloudwatch"
    supported_operations = {
        "create_log_group",
        "delete_log_group",
        "update_log_retention_policy",
        "create_metric_alarm",
        "delete_metric_alarm",
        "put_metric_data",
        "create_dashboard",
        "delete_dashboard",
        "tag_log_group",
        "untag_log_group",
    }
    requires_confirmation = True

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None, dry_run: bool = False):
        """Initialize CloudWatch operations."""
        super().__init__(profile, region, dry_run)

    def execute_operation(self, context: OperationContext, operation_type: str, **kwargs) -> List[OperationResult]:
        """
        Execute CloudWatch operation.

        Args:
            context: Operation context
            operation_type: Type of operation to execute
            **kwargs: Operation-specific arguments

        Returns:
            List of operation results
        """
        self.validate_context(context)

        if operation_type == "create_log_group":
            return self.create_log_group(context, **kwargs)
        elif operation_type == "delete_log_group":
            return self.delete_log_group(context, kwargs.get("log_group_name"))
        elif operation_type == "update_log_retention_policy":
            return self.update_log_retention_policy(context, **kwargs)
        elif operation_type == "create_metric_alarm":
            return self.create_metric_alarm(context, **kwargs)
        elif operation_type == "delete_metric_alarm":
            return self.delete_metric_alarm(context, kwargs.get("alarm_name"))
        elif operation_type == "put_metric_data":
            return self.put_metric_data(context, **kwargs)
        elif operation_type == "create_dashboard":
            return self.create_dashboard(context, **kwargs)
        elif operation_type == "delete_dashboard":
            return self.delete_dashboard(context, kwargs.get("dashboard_name"))
        elif operation_type == "tag_log_group":
            return self.tag_log_group(context, **kwargs)
        elif operation_type == "untag_log_group":
            return self.untag_log_group(context, **kwargs)
        else:
            raise ValueError(f"Unsupported operation: {operation_type}")

    def create_log_group(
        self,
        context: OperationContext,
        log_group_name: str,
        kms_key_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        retention_in_days: Optional[int] = None,
    ) -> List[OperationResult]:
        """
        Create CloudWatch log group.

        Args:
            context: Operation context
            log_group_name: Name of log group to create
            kms_key_id: KMS key ID for encryption
            tags: Log group tags
            retention_in_days: Log retention period in days

        Returns:
            List of operation results
        """
        logs_client = self.get_client("logs", context.region)

        result = self.create_operation_result(context, "create_log_group", "logs:log_group", log_group_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create log group {log_group_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            create_params = {"logGroupName": log_group_name}

            if kms_key_id:
                create_params["kmsKeyId"] = kms_key_id
            if tags:
                create_params["tags"] = tags

            response = self.execute_aws_call(logs_client, "create_log_group", **create_params)

            # Set retention policy if specified
            if retention_in_days:
                self.execute_aws_call(
                    logs_client, "put_retention_policy", logGroupName=log_group_name, retentionInDays=retention_in_days
                )
                logger.info(f"Set retention policy to {retention_in_days} days for {log_group_name}")

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully created log group {log_group_name}")

        except ClientError as e:
            error_msg = f"Failed to create log group {log_group_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_log_group(self, context: OperationContext, log_group_name: str) -> List[OperationResult]:
        """
        Delete CloudWatch log group.

        Args:
            context: Operation context
            log_group_name: Name of log group to delete

        Returns:
            List of operation results
        """
        logs_client = self.get_client("logs", context.region)

        result = self.create_operation_result(context, "delete_log_group", "logs:log_group", log_group_name)

        try:
            if not self.confirm_operation(context, log_group_name, "delete log group"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete log group {log_group_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(logs_client, "delete_log_group", logGroupName=log_group_name)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted log group {log_group_name}")

        except ClientError as e:
            error_msg = f"Failed to delete log group {log_group_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def update_log_retention_policy(
        self,
        context: OperationContext,
        log_group_name: Optional[str] = None,
        retention_in_days: int = 30,
        update_all_log_groups: bool = False,
    ) -> List[OperationResult]:
        """
        Update CloudWatch log retention policy.

        Migrated from inventory/update_cloudwatch_logs_retention_policy.py

        Args:
            context: Operation context
            log_group_name: Specific log group name (if None, updates all)
            retention_in_days: Retention period in days
            update_all_log_groups: Whether to update all log groups

        Returns:
            List of operation results
        """
        logs_client = self.get_client("logs", context.region)
        results = []

        try:
            if log_group_name:
                # Update specific log group
                log_groups = [log_group_name]
            elif update_all_log_groups:
                # Get all log groups
                paginator = logs_client.get_paginator("describe_log_groups")
                log_groups = []

                for page in paginator.paginate():
                    for log_group in page["logGroups"]:
                        log_groups.append(log_group["logGroupName"])
            else:
                raise ValueError("Either log_group_name must be specified or update_all_log_groups must be True")

            for lg_name in log_groups:
                result = self.create_operation_result(context, "update_log_retention_policy", "logs:log_group", lg_name)

                try:
                    if context.dry_run:
                        logger.info(f"[DRY-RUN] Would set retention to {retention_in_days} days for {lg_name}")
                        result.mark_completed(OperationStatus.DRY_RUN)
                    else:
                        response = self.execute_aws_call(
                            logs_client, "put_retention_policy", logGroupName=lg_name, retentionInDays=retention_in_days
                        )

                        result.response_data = response
                        result.mark_completed(OperationStatus.SUCCESS)
                        logger.info(f"Successfully updated retention policy for {lg_name}")

                except ClientError as e:
                    error_msg = f"Failed to update retention policy for {lg_name}: {e}"
                    logger.error(error_msg)
                    result.mark_completed(OperationStatus.FAILED, error_msg)

                results.append(result)

        except Exception as e:
            error_msg = f"Failed to update log retention policies: {e}"
            logger.error(error_msg)
            result = self.create_operation_result(
                context, "update_log_retention_policy", "logs:operation", "batch_update"
            )
            result.mark_completed(OperationStatus.FAILED, error_msg)
            results.append(result)

        return results

    def create_metric_alarm(
        self,
        context: OperationContext,
        alarm_name: str,
        comparison_operator: str,
        evaluation_periods: int,
        metric_name: str,
        namespace: str,
        period: int,
        statistic: str,
        threshold: float,
        actions_enabled: bool = True,
        alarm_actions: Optional[List[str]] = None,
        alarm_description: Optional[str] = None,
        dimensions: Optional[List[Dict[str, str]]] = None,
        insufficient_data_actions: Optional[List[str]] = None,
        ok_actions: Optional[List[str]] = None,
        tags: Optional[List[Dict[str, str]]] = None,
        unit: Optional[str] = None,
    ) -> List[OperationResult]:
        """
        Create CloudWatch metric alarm.

        Args:
            context: Operation context
            alarm_name: Name of alarm to create
            comparison_operator: Comparison operator
            evaluation_periods: Number of evaluation periods
            metric_name: Metric name
            namespace: Metric namespace
            period: Period in seconds
            statistic: Statistic type
            threshold: Alarm threshold
            actions_enabled: Whether actions are enabled
            alarm_actions: Alarm actions
            alarm_description: Alarm description
            dimensions: Metric dimensions
            insufficient_data_actions: Insufficient data actions
            ok_actions: OK actions
            tags: Alarm tags
            unit: Metric unit

        Returns:
            List of operation results
        """
        cloudwatch_client = self.get_client("cloudwatch", context.region)

        result = self.create_operation_result(context, "create_metric_alarm", "cloudwatch:alarm", alarm_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create CloudWatch alarm {alarm_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            alarm_params = {
                "AlarmName": alarm_name,
                "ComparisonOperator": comparison_operator,
                "EvaluationPeriods": evaluation_periods,
                "MetricName": metric_name,
                "Namespace": namespace,
                "Period": period,
                "Statistic": statistic,
                "Threshold": threshold,
                "ActionsEnabled": actions_enabled,
            }

            if alarm_actions:
                alarm_params["AlarmActions"] = alarm_actions
            if alarm_description:
                alarm_params["AlarmDescription"] = alarm_description
            if dimensions:
                alarm_params["Dimensions"] = dimensions
            if insufficient_data_actions:
                alarm_params["InsufficientDataActions"] = insufficient_data_actions
            if ok_actions:
                alarm_params["OKActions"] = ok_actions
            if tags:
                alarm_params["Tags"] = tags
            if unit:
                alarm_params["Unit"] = unit

            response = self.execute_aws_call(cloudwatch_client, "put_metric_alarm", **alarm_params)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully created CloudWatch alarm {alarm_name}")

        except ClientError as e:
            error_msg = f"Failed to create CloudWatch alarm {alarm_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_metric_alarm(self, context: OperationContext, alarm_name: str) -> List[OperationResult]:
        """
        Delete CloudWatch metric alarm.

        Args:
            context: Operation context
            alarm_name: Name of alarm to delete

        Returns:
            List of operation results
        """
        cloudwatch_client = self.get_client("cloudwatch", context.region)

        result = self.create_operation_result(context, "delete_metric_alarm", "cloudwatch:alarm", alarm_name)

        try:
            if not self.confirm_operation(context, alarm_name, "delete CloudWatch alarm"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete CloudWatch alarm {alarm_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(cloudwatch_client, "delete_alarms", AlarmNames=[alarm_name])

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted CloudWatch alarm {alarm_name}")

        except ClientError as e:
            error_msg = f"Failed to delete CloudWatch alarm {alarm_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def put_metric_data(
        self, context: OperationContext, namespace: str, metric_data: List[Dict[str, Any]]
    ) -> List[OperationResult]:
        """
        Put custom metric data to CloudWatch.

        Args:
            context: Operation context
            namespace: Metric namespace
            metric_data: List of metric data points

        Returns:
            List of operation results
        """
        cloudwatch_client = self.get_client("cloudwatch", context.region)

        result = self.create_operation_result(context, "put_metric_data", "cloudwatch:metric", namespace)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would put {len(metric_data)} metric data points to {namespace}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(
                    cloudwatch_client, "put_metric_data", Namespace=namespace, MetricData=metric_data
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully put {len(metric_data)} metric data points to {namespace}")

        except ClientError as e:
            error_msg = f"Failed to put metric data to {namespace}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def tag_log_group(
        self, context: OperationContext, log_group_name: str, tags: Dict[str, str]
    ) -> List[OperationResult]:
        """
        Add tags to CloudWatch log group.

        Args:
            context: Operation context
            log_group_name: Name of log group to tag
            tags: Tags to add

        Returns:
            List of operation results
        """
        logs_client = self.get_client("logs", context.region)

        result = self.create_operation_result(context, "tag_log_group", "logs:log_group", log_group_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would add {len(tags)} tags to log group {log_group_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(logs_client, "tag_log_group", logGroupName=log_group_name, tags=tags)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully added {len(tags)} tags to log group {log_group_name}")

        except ClientError as e:
            error_msg = f"Failed to tag log group {log_group_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def untag_log_group(
        self, context: OperationContext, log_group_name: str, tag_keys: List[str]
    ) -> List[OperationResult]:
        """
        Remove tags from CloudWatch log group.

        Args:
            context: Operation context
            log_group_name: Name of log group to untag
            tag_keys: Tag keys to remove

        Returns:
            List of operation results
        """
        logs_client = self.get_client("logs", context.region)

        result = self.create_operation_result(context, "untag_log_group", "logs:log_group", log_group_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would remove {len(tag_keys)} tags from log group {log_group_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(
                    logs_client, "untag_log_group", logGroupName=log_group_name, tags=tag_keys
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully removed {len(tag_keys)} tags from log group {log_group_name}")

        except ClientError as e:
            error_msg = f"Failed to untag log group {log_group_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

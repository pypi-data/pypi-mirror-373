"""
CloudFormation Operations Module.

Provides comprehensive CloudFormation resource management capabilities including
stack operations, StackSet management, and infrastructure automation.

Migrated and enhanced from:
- inventory/cfn_move_stack_instances.py
- inventory/update_cfn_stacksets.py
- inventory/lockdown_cfn_stackset_role.py
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus


class CloudFormationOperations(BaseOperation):
    """
    CloudFormation resource operations and lifecycle management.

    Handles all CloudFormation-related operational tasks including stack management,
    StackSet operations, and infrastructure automation workflows.
    """

    service_name = "cloudformation"
    supported_operations = {
        "create_stack",
        "update_stack",
        "delete_stack",
        "create_stack_set",
        "update_stack_set",
        "delete_stack_set",
        "create_stack_instances",
        "update_stack_instances",
        "delete_stack_instances",
        "move_stack_instances",
        "lockdown_stackset_role",
        "enable_drift_detection",
        "detect_stack_drift",
        "cancel_update_stack",
    }
    requires_confirmation = True

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None, dry_run: bool = False):
        """Initialize CloudFormation operations."""
        super().__init__(profile, region, dry_run)

    def execute_operation(self, context: OperationContext, operation_type: str, **kwargs) -> List[OperationResult]:
        """
        Execute CloudFormation operation.

        Args:
            context: Operation context
            operation_type: Type of operation to execute
            **kwargs: Operation-specific arguments

        Returns:
            List of operation results
        """
        self.validate_context(context)

        if operation_type == "create_stack":
            return self.create_stack(context, **kwargs)
        elif operation_type == "update_stack":
            return self.update_stack(context, **kwargs)
        elif operation_type == "delete_stack":
            return self.delete_stack(context, kwargs.get("stack_name"))
        elif operation_type == "create_stack_set":
            return self.create_stack_set(context, **kwargs)
        elif operation_type == "update_stack_set":
            return self.update_stack_set(context, **kwargs)
        elif operation_type == "delete_stack_set":
            return self.delete_stack_set(context, kwargs.get("stack_set_name"))
        elif operation_type == "create_stack_instances":
            return self.create_stack_instances(context, **kwargs)
        elif operation_type == "update_stack_instances":
            return self.update_stack_instances(context, **kwargs)
        elif operation_type == "delete_stack_instances":
            return self.delete_stack_instances(context, **kwargs)
        elif operation_type == "move_stack_instances":
            return self.move_stack_instances(context, **kwargs)
        elif operation_type == "lockdown_stackset_role":
            return self.lockdown_stackset_role(context, **kwargs)
        elif operation_type == "enable_drift_detection":
            return self.enable_drift_detection(context, kwargs.get("stack_name"))
        elif operation_type == "detect_stack_drift":
            return self.detect_stack_drift(context, kwargs.get("stack_name"))
        elif operation_type == "cancel_update_stack":
            return self.cancel_update_stack(context, kwargs.get("stack_name"))
        else:
            raise ValueError(f"Unsupported operation: {operation_type}")

    def create_stack(
        self,
        context: OperationContext,
        stack_name: str,
        template_body: Optional[str] = None,
        template_url: Optional[str] = None,
        parameters: Optional[List[Dict[str, str]]] = None,
        capabilities: Optional[List[str]] = None,
        tags: Optional[List[Dict[str, str]]] = None,
        role_arn: Optional[str] = None,
        enable_termination_protection: bool = False,
    ) -> List[OperationResult]:
        """
        Create CloudFormation stack.

        Args:
            context: Operation context
            stack_name: Name of stack to create
            template_body: Template body as string
            template_url: Template URL
            parameters: Stack parameters
            capabilities: Required capabilities
            tags: Stack tags
            role_arn: Service role ARN
            enable_termination_protection: Enable termination protection

        Returns:
            List of operation results
        """
        cfn_client = self.get_client("cloudformation", context.region)

        result = self.create_operation_result(context, "create_stack", "cloudformation:stack", stack_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create CloudFormation stack {stack_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            create_params = {
                "StackName": stack_name,
                "EnableTerminationProtection": enable_termination_protection,
            }

            if template_body:
                create_params["TemplateBody"] = template_body
            elif template_url:
                create_params["TemplateURL"] = template_url
            else:
                raise ValueError("Either template_body or template_url must be provided")

            if parameters:
                create_params["Parameters"] = parameters
            if capabilities:
                create_params["Capabilities"] = capabilities
            if tags:
                create_params["Tags"] = tags
            if role_arn:
                create_params["RoleARN"] = role_arn

            response = self.execute_aws_call(cfn_client, "create_stack", **create_params)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully created CloudFormation stack {stack_name}")

        except ClientError as e:
            error_msg = f"Failed to create CloudFormation stack {stack_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_stack(
        self, context: OperationContext, stack_name: str, role_arn: Optional[str] = None
    ) -> List[OperationResult]:
        """
        Delete CloudFormation stack.

        Args:
            context: Operation context
            stack_name: Name of stack to delete
            role_arn: Service role ARN

        Returns:
            List of operation results
        """
        cfn_client = self.get_client("cloudformation", context.region)

        result = self.create_operation_result(context, "delete_stack", "cloudformation:stack", stack_name)

        try:
            if not self.confirm_operation(context, stack_name, "delete CloudFormation stack"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete CloudFormation stack {stack_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                delete_params = {"StackName": stack_name}
                if role_arn:
                    delete_params["RoleARN"] = role_arn

                response = self.execute_aws_call(cfn_client, "delete_stack", **delete_params)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully initiated deletion of CloudFormation stack {stack_name}")

        except ClientError as e:
            error_msg = f"Failed to delete CloudFormation stack {stack_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def move_stack_instances(
        self,
        context: OperationContext,
        source_stack_set_name: str,
        target_stack_set_name: str,
        account_ids: List[str],
        regions: List[str],
        operation_preferences: Optional[Dict[str, Any]] = None,
    ) -> List[OperationResult]:
        """
        Move stack instances between StackSets.

        Migrated from inventory/cfn_move_stack_instances.py

        Args:
            context: Operation context
            source_stack_set_name: Source StackSet name
            target_stack_set_name: Target StackSet name
            account_ids: Account IDs to move
            regions: Regions to move
            operation_preferences: Operation preferences

        Returns:
            List of operation results
        """
        cfn_client = self.get_client("cloudformation", context.region)

        result = self.create_operation_result(
            context,
            "move_stack_instances",
            "cloudformation:stackset",
            f"{source_stack_set_name} -> {target_stack_set_name}",
        )

        try:
            if not self.confirm_operation(context, f"{len(account_ids)} instances", "move StackSet instances"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(
                    f"[DRY-RUN] Would move {len(account_ids)} instances from {source_stack_set_name} to {target_stack_set_name}"
                )
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            # Step 1: Delete instances from source StackSet
            delete_params = {"StackSetName": source_stack_set_name, "Accounts": account_ids, "Regions": regions}

            if operation_preferences:
                delete_params["OperationPreferences"] = operation_preferences

            delete_response = self.execute_aws_call(cfn_client, "delete_stack_instances", **delete_params)

            delete_operation_id = delete_response["OperationId"]
            logger.info(f"Initiated deletion from source StackSet: {delete_operation_id}")

            # Wait for deletion to complete (simplified - in production, implement proper polling)
            # For now, we'll return the operation ID for monitoring

            # Step 2: Create instances in target StackSet
            create_params = {"StackSetName": target_stack_set_name, "Accounts": account_ids, "Regions": regions}

            if operation_preferences:
                create_params["OperationPreferences"] = operation_preferences

            create_response = self.execute_aws_call(cfn_client, "create_stack_instances", **create_params)

            create_operation_id = create_response["OperationId"]
            logger.info(f"Initiated creation in target StackSet: {create_operation_id}")

            result.response_data = {
                "delete_operation_id": delete_operation_id,
                "create_operation_id": create_operation_id,
                "moved_accounts": account_ids,
                "moved_regions": regions,
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully initiated move of {len(account_ids)} instances")

        except ClientError as e:
            error_msg = f"Failed to move stack instances: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def lockdown_stackset_role(
        self,
        context: OperationContext,
        target_role_name: str = "AWSCloudFormationStackSetExecutionRole",
        management_account_id: Optional[str] = None,
        lock_policy: bool = True,
    ) -> List[OperationResult]:
        """
        Lockdown CloudFormation StackSet execution role.

        Migrated from inventory/lockdown_cfn_stackset_role.py

        Args:
            context: Operation context
            target_role_name: Role name to lockdown
            management_account_id: Management account ID to restrict access to
            lock_policy: Whether to apply restrictive policy

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam", context.region)

        result = self.create_operation_result(context, "lockdown_stackset_role", "iam:role", target_role_name)

        try:
            if not self.confirm_operation(context, target_role_name, "lockdown StackSet role"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would lockdown StackSet role {target_role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            # Get current role
            role_response = self.execute_aws_call(iam_client, "get_role", RoleName=target_role_name)

            current_trust_policy = role_response["Role"]["AssumeRolePolicyDocument"]

            if lock_policy and management_account_id:
                # Create restrictive trust policy
                locked_trust_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": f"arn:aws:iam::{management_account_id}:root"},
                            "Action": "sts:AssumeRole",
                            "Condition": {"StringEquals": {"aws:PrincipalServiceName": "cloudformation.amazonaws.com"}},
                        }
                    ],
                }

                # Update trust policy
                response = self.execute_aws_call(
                    iam_client,
                    "update_assume_role_policy",
                    RoleName=target_role_name,
                    PolicyDocument=json.dumps(locked_trust_policy),
                )

                result.response_data = {
                    "role_name": target_role_name,
                    "previous_policy": current_trust_policy,
                    "new_policy": locked_trust_policy,
                    "management_account_id": management_account_id,
                }
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully locked down StackSet role {target_role_name}")
            else:
                result.response_data = {
                    "role_name": target_role_name,
                    "current_policy": current_trust_policy,
                    "action": "Policy retrieved but not modified",
                }
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Retrieved current policy for role {target_role_name}")

        except ClientError as e:
            error_msg = f"Failed to lockdown StackSet role {target_role_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def create_stack_set(
        self,
        context: OperationContext,
        stack_set_name: str,
        template_body: Optional[str] = None,
        template_url: Optional[str] = None,
        parameters: Optional[List[Dict[str, str]]] = None,
        capabilities: Optional[List[str]] = None,
        tags: Optional[List[Dict[str, str]]] = None,
        administration_role_arn: Optional[str] = None,
        execution_role_name: Optional[str] = None,
        permission_model: str = "SERVICE_MANAGED",
    ) -> List[OperationResult]:
        """
        Create CloudFormation StackSet.

        Args:
            context: Operation context
            stack_set_name: Name of StackSet to create
            template_body: Template body as string
            template_url: Template URL
            parameters: StackSet parameters
            capabilities: Required capabilities
            tags: StackSet tags
            administration_role_arn: Administration role ARN
            execution_role_name: Execution role name
            permission_model: Permission model (SERVICE_MANAGED or SELF_MANAGED)

        Returns:
            List of operation results
        """
        cfn_client = self.get_client("cloudformation", context.region)

        result = self.create_operation_result(context, "create_stack_set", "cloudformation:stackset", stack_set_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create CloudFormation StackSet {stack_set_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            create_params = {
                "StackSetName": stack_set_name,
                "PermissionModel": permission_model,
            }

            if template_body:
                create_params["TemplateBody"] = template_body
            elif template_url:
                create_params["TemplateURL"] = template_url
            else:
                raise ValueError("Either template_body or template_url must be provided")

            if parameters:
                create_params["Parameters"] = parameters
            if capabilities:
                create_params["Capabilities"] = capabilities
            if tags:
                create_params["Tags"] = tags
            if administration_role_arn:
                create_params["AdministrationRoleARN"] = administration_role_arn
            if execution_role_name:
                create_params["ExecutionRoleName"] = execution_role_name

            response = self.execute_aws_call(cfn_client, "create_stack_set", **create_params)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully created CloudFormation StackSet {stack_set_name}")

        except ClientError as e:
            error_msg = f"Failed to create CloudFormation StackSet {stack_set_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_stack_set(self, context: OperationContext, stack_set_name: str) -> List[OperationResult]:
        """
        Delete CloudFormation StackSet.

        Args:
            context: Operation context
            stack_set_name: Name of StackSet to delete

        Returns:
            List of operation results
        """
        cfn_client = self.get_client("cloudformation", context.region)

        result = self.create_operation_result(context, "delete_stack_set", "cloudformation:stackset", stack_set_name)

        try:
            if not self.confirm_operation(context, stack_set_name, "delete CloudFormation StackSet"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete CloudFormation StackSet {stack_set_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(cfn_client, "delete_stack_set", StackSetName=stack_set_name)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted CloudFormation StackSet {stack_set_name}")

        except ClientError as e:
            error_msg = f"Failed to delete CloudFormation StackSet {stack_set_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def create_stack_instances(
        self,
        context: OperationContext,
        stack_set_name: str,
        account_ids: List[str],
        regions: List[str],
        parameter_overrides: Optional[List[Dict[str, str]]] = None,
        operation_preferences: Optional[Dict[str, Any]] = None,
    ) -> List[OperationResult]:
        """
        Create CloudFormation StackSet instances.

        Args:
            context: Operation context
            stack_set_name: StackSet name
            account_ids: Target account IDs
            regions: Target regions
            parameter_overrides: Parameter overrides
            operation_preferences: Operation preferences

        Returns:
            List of operation results
        """
        cfn_client = self.get_client("cloudformation", context.region)

        result = self.create_operation_result(
            context, "create_stack_instances", "cloudformation:stackset", stack_set_name
        )

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create {len(account_ids)} stack instances in StackSet {stack_set_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            create_params = {"StackSetName": stack_set_name, "Accounts": account_ids, "Regions": regions}

            if parameter_overrides:
                create_params["ParameterOverrides"] = parameter_overrides
            if operation_preferences:
                create_params["OperationPreferences"] = operation_preferences

            response = self.execute_aws_call(cfn_client, "create_stack_instances", **create_params)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully initiated creation of {len(account_ids)} stack instances")

        except ClientError as e:
            error_msg = f"Failed to create stack instances: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_stack_instances(
        self,
        context: OperationContext,
        stack_set_name: str,
        account_ids: List[str],
        regions: List[str],
        retain_stacks: bool = False,
        operation_preferences: Optional[Dict[str, Any]] = None,
    ) -> List[OperationResult]:
        """
        Delete CloudFormation StackSet instances.

        Args:
            context: Operation context
            stack_set_name: StackSet name
            account_ids: Target account IDs
            regions: Target regions
            retain_stacks: Whether to retain stacks
            operation_preferences: Operation preferences

        Returns:
            List of operation results
        """
        cfn_client = self.get_client("cloudformation", context.region)

        result = self.create_operation_result(
            context, "delete_stack_instances", "cloudformation:stackset", stack_set_name
        )

        try:
            if not self.confirm_operation(context, f"{len(account_ids)} instances", "delete StackSet instances"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete {len(account_ids)} stack instances from StackSet {stack_set_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            delete_params = {
                "StackSetName": stack_set_name,
                "Accounts": account_ids,
                "Regions": regions,
                "RetainStacks": retain_stacks,
            }

            if operation_preferences:
                delete_params["OperationPreferences"] = operation_preferences

            response = self.execute_aws_call(cfn_client, "delete_stack_instances", **delete_params)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully initiated deletion of {len(account_ids)} stack instances")

        except ClientError as e:
            error_msg = f"Failed to delete stack instances: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

"""
IAM Operations Module.

Provides comprehensive IAM resource management capabilities including role management,
policy operations, cross-account access management, and access key lifecycle operations.

Migrated and enhanced from:
- inventory/update_iam_roles_cross_accounts.py
- unSkript AWS_Access_Key_Rotation.ipynb (access key rotation workflow)
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass

import boto3
import dateutil.tz
from botocore.exceptions import ClientError
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus

console = Console()


class IAMOperations(BaseOperation):
    """
    IAM resource operations and lifecycle management.

    Handles all IAM-related operational tasks including role management,
    policy operations, and cross-account access configuration.
    """

    service_name = "iam"
    supported_operations = {
        "create_role",
        "update_role",
        "delete_role",
        "create_policy",
        "update_policy",
        "delete_policy",
        "attach_role_policy",
        "detach_role_policy",
        "update_assume_role_policy",
        "update_roles_cross_accounts",
        "create_service_linked_role",
        "tag_role",
        "untag_role",
        "list_expiring_access_keys",
        "create_access_key",
        "update_access_key_status",
        "delete_access_key",
        "rotate_access_keys",
    }
    requires_confirmation = True

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None, dry_run: bool = False):
        """Initialize IAM operations."""
        super().__init__(profile, region, dry_run)

    def execute_operation(self, context: OperationContext, operation_type: str, **kwargs) -> List[OperationResult]:
        """
        Execute IAM operation.

        Args:
            context: Operation context
            operation_type: Type of operation to execute
            **kwargs: Operation-specific arguments

        Returns:
            List of operation results
        """
        self.validate_context(context)

        if operation_type == "create_role":
            return self.create_role(context, **kwargs)
        elif operation_type == "update_role":
            return self.update_role(context, **kwargs)
        elif operation_type == "delete_role":
            return self.delete_role(context, kwargs.get("role_name"))
        elif operation_type == "create_policy":
            return self.create_policy(context, **kwargs)
        elif operation_type == "update_policy":
            return self.update_policy(context, **kwargs)
        elif operation_type == "delete_policy":
            return self.delete_policy(context, kwargs.get("policy_arn"))
        elif operation_type == "attach_role_policy":
            return self.attach_role_policy(context, **kwargs)
        elif operation_type == "detach_role_policy":
            return self.detach_role_policy(context, **kwargs)
        elif operation_type == "update_assume_role_policy":
            return self.update_assume_role_policy(context, **kwargs)
        elif operation_type == "update_roles_cross_accounts":
            return self.update_roles_cross_accounts(context, **kwargs)
        elif operation_type == "create_service_linked_role":
            return self.create_service_linked_role(context, **kwargs)
        elif operation_type == "tag_role":
            return self.tag_role(context, **kwargs)
        elif operation_type == "untag_role":
            return self.untag_role(context, **kwargs)
        elif operation_type == "list_expiring_access_keys":
            return self.list_expiring_access_keys(context, **kwargs)
        elif operation_type == "create_access_key":
            return self.create_access_key(context, **kwargs)
        elif operation_type == "update_access_key_status":
            return self.update_access_key_status(context, **kwargs)
        elif operation_type == "delete_access_key":
            return self.delete_access_key(context, **kwargs)
        elif operation_type == "rotate_access_keys":
            return self.rotate_access_keys(context, **kwargs)
        else:
            raise ValueError(f"Unsupported operation: {operation_type}")

    def create_role(
        self,
        context: OperationContext,
        role_name: str,
        assume_role_policy_document: str,
        path: str = "/",
        description: Optional[str] = None,
        max_session_duration: int = 3600,
        permissions_boundary: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> List[OperationResult]:
        """
        Create IAM role.

        Args:
            context: Operation context
            role_name: Name of role to create
            assume_role_policy_document: Trust policy document
            path: Role path
            description: Role description
            max_session_duration: Maximum session duration
            permissions_boundary: Permissions boundary ARN
            tags: Role tags

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")

        result = self.create_operation_result(context, "create_role", "iam:role", role_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create IAM role {role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            create_params = {
                "RoleName": role_name,
                "AssumeRolePolicyDocument": assume_role_policy_document,
                "Path": path,
                "MaxSessionDuration": max_session_duration,
            }

            if description:
                create_params["Description"] = description
            if permissions_boundary:
                create_params["PermissionsBoundary"] = permissions_boundary
            if tags:
                create_params["Tags"] = tags

            response = self.execute_aws_call(iam_client, "create_role", **create_params)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully created IAM role {role_name}")

        except ClientError as e:
            error_msg = f"Failed to create IAM role {role_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_role(self, context: OperationContext, role_name: str) -> List[OperationResult]:
        """
        Delete IAM role.

        Args:
            context: Operation context
            role_name: Name of role to delete

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")

        result = self.create_operation_result(context, "delete_role", "iam:role", role_name)

        try:
            if not self.confirm_operation(context, role_name, "delete IAM role"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete IAM role {role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                # First detach all policies
                attached_policies = self.execute_aws_call(iam_client, "list_attached_role_policies", RoleName=role_name)

                for policy in attached_policies.get("AttachedPolicies", []):
                    self.execute_aws_call(
                        iam_client, "detach_role_policy", RoleName=role_name, PolicyArn=policy["PolicyArn"]
                    )

                # Delete inline policies
                inline_policies = self.execute_aws_call(iam_client, "list_role_policies", RoleName=role_name)

                for policy_name in inline_policies.get("PolicyNames", []):
                    self.execute_aws_call(iam_client, "delete_role_policy", RoleName=role_name, PolicyName=policy_name)

                # Finally delete the role
                response = self.execute_aws_call(iam_client, "delete_role", RoleName=role_name)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted IAM role {role_name}")

        except ClientError as e:
            error_msg = f"Failed to delete IAM role {role_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def update_assume_role_policy(
        self, context: OperationContext, role_name: str, policy_document: str
    ) -> List[OperationResult]:
        """
        Update IAM role trust policy.

        Args:
            context: Operation context
            role_name: Name of role to update
            policy_document: New trust policy document

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")

        result = self.create_operation_result(context, "update_assume_role_policy", "iam:role", role_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would update trust policy for IAM role {role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(
                    iam_client, "update_assume_role_policy", RoleName=role_name, PolicyDocument=policy_document
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully updated trust policy for IAM role {role_name}")

        except ClientError as e:
            error_msg = f"Failed to update trust policy for IAM role {role_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def update_roles_cross_accounts(
        self,
        context: OperationContext,
        role_name: str,
        trusted_account_ids: List[str],
        external_id: Optional[str] = None,
        require_mfa: bool = False,
        session_duration: int = 3600,
    ) -> List[OperationResult]:
        """
        Update IAM roles for cross-account access.

        Migrated from inventory/update_iam_roles_cross_accounts.py

        Args:
            context: Operation context
            role_name: Name of role to update
            trusted_account_ids: List of trusted account IDs
            external_id: External ID for additional security
            require_mfa: Whether to require MFA
            session_duration: Session duration in seconds

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")

        result = self.create_operation_result(context, "update_roles_cross_accounts", "iam:role", role_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would update cross-account access for role {role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            # Build trust policy for cross-account access
            trust_policy = {"Version": "2012-10-17", "Statement": []}

            for account_id in trusted_account_ids:
                statement = {
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{account_id}:root"},
                    "Action": "sts:AssumeRole",
                }

                # Add conditions if specified
                conditions = {}

                if external_id:
                    conditions["StringEquals"] = {"sts:ExternalId": external_id}

                if require_mfa:
                    conditions["Bool"] = {"aws:MultiFactorAuthPresent": "true"}

                if session_duration != 3600:
                    conditions["NumericLessThan"] = {"aws:TokenIssueTime": str(session_duration)}

                if conditions:
                    statement["Condition"] = conditions

                trust_policy["Statement"].append(statement)

            # Update the role's trust policy
            response = self.execute_aws_call(
                iam_client, "update_assume_role_policy", RoleName=role_name, PolicyDocument=json.dumps(trust_policy)
            )

            # Update max session duration if different from default
            if session_duration != 3600:
                self.execute_aws_call(
                    iam_client, "update_role", RoleName=role_name, MaxSessionDuration=session_duration
                )

            result.response_data = {
                "role_name": role_name,
                "trusted_accounts": trusted_account_ids,
                "external_id": external_id,
                "require_mfa": require_mfa,
                "session_duration": session_duration,
                "trust_policy": trust_policy,
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully updated cross-account access for role {role_name}")

        except ClientError as e:
            error_msg = f"Failed to update cross-account access for role {role_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def update_role(
        self, 
        context: OperationContext, 
        role_name: str,
        description: Optional[str] = None,
        max_session_duration: Optional[int] = None,
        permissions_boundary: Optional[str] = None
    ) -> List[OperationResult]:
        """
        Update IAM role properties.
        
        Args:
            context: Operation context
            role_name: Name of role to update
            description: New description
            max_session_duration: New max session duration
            permissions_boundary: New permissions boundary ARN
            
        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")
        
        result = self.create_operation_result(context, "update_role", "iam:role", role_name)
        
        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would update IAM role {role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]
                
            update_params = {"RoleName": role_name}
            
            if description is not None:
                update_params["Description"] = description
            if max_session_duration is not None:
                update_params["MaxSessionDuration"] = max_session_duration
                
            response = self.execute_aws_call(iam_client, "update_role", **update_params)
            
            # Handle permissions boundary separately if provided
            if permissions_boundary is not None:
                if permissions_boundary == "":
                    # Remove permissions boundary
                    self.execute_aws_call(iam_client, "delete_role_permissions_boundary", RoleName=role_name)
                else:
                    # Set permissions boundary
                    self.execute_aws_call(iam_client, "put_role_permissions_boundary", 
                                        RoleName=role_name, PermissionsBoundary=permissions_boundary)
            
            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully updated IAM role {role_name}")
            
        except ClientError as e:
            error_msg = f"Failed to update IAM role {role_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
            
        return [result]

    def update_policy(
        self,
        context: OperationContext,
        policy_arn: str,
        policy_document: str,
        set_as_default: bool = True
    ) -> List[OperationResult]:
        """
        Update IAM policy by creating a new version.
        
        Args:
            context: Operation context
            policy_arn: ARN of policy to update
            policy_document: New policy document JSON
            set_as_default: Whether to set new version as default
            
        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")
        
        result = self.create_operation_result(context, "update_policy", "iam:policy", policy_arn)
        
        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would update IAM policy {policy_arn}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]
                
            response = self.execute_aws_call(
                iam_client,
                "create_policy_version",
                PolicyArn=policy_arn,
                PolicyDocument=policy_document,
                SetAsDefault=set_as_default
            )
            
            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully updated IAM policy {policy_arn}")
            
        except ClientError as e:
            error_msg = f"Failed to update IAM policy {policy_arn}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
            
        return [result]

    def create_service_linked_role(
        self,
        context: OperationContext,
        aws_service_name: str,
        description: Optional[str] = None,
        custom_suffix: Optional[str] = None
    ) -> List[OperationResult]:
        """
        Create service-linked role for AWS service.
        
        Args:
            context: Operation context
            aws_service_name: AWS service name (e.g., 'elasticloadbalancing.amazonaws.com')
            description: Custom description
            custom_suffix: Custom suffix for role name
            
        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")
        
        result = self.create_operation_result(context, "create_service_linked_role", "iam:service-linked-role", aws_service_name)
        
        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create service-linked role for {aws_service_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]
                
            create_params = {"AWSServiceName": aws_service_name}
            
            if description:
                create_params["Description"] = description
            if custom_suffix:
                create_params["CustomSuffix"] = custom_suffix
                
            response = self.execute_aws_call(iam_client, "create_service_linked_role", **create_params)
            
            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully created service-linked role for {aws_service_name}")
            
        except ClientError as e:
            error_msg = f"Failed to create service-linked role for {aws_service_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
            
        return [result]

    def untag_role(self, context: OperationContext, role_name: str, tag_keys: List[str]) -> List[OperationResult]:
        """
        Remove tags from IAM role.
        
        Args:
            context: Operation context
            role_name: Name of role to untag
            tag_keys: List of tag keys to remove
            
        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")
        
        result = self.create_operation_result(context, "untag_role", "iam:role", role_name)
        
        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would remove {len(tag_keys)} tags from role {role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(iam_client, "untag_role", RoleName=role_name, TagKeys=tag_keys)
                
                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully removed {len(tag_keys)} tags from role {role_name}")
                
        except ClientError as e:
            error_msg = f"Failed to untag role {role_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
            
        return [result]

    def attach_role_policy(self, context: OperationContext, role_name: str, policy_arn: str) -> List[OperationResult]:
        """
        Attach policy to IAM role.

        Args:
            context: Operation context
            role_name: Name of role
            policy_arn: Policy ARN to attach

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")

        result = self.create_operation_result(context, "attach_role_policy", "iam:role", f"{role_name}:{policy_arn}")

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would attach policy {policy_arn} to role {role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(
                    iam_client, "attach_role_policy", RoleName=role_name, PolicyArn=policy_arn
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully attached policy {policy_arn} to role {role_name}")

        except ClientError as e:
            error_msg = f"Failed to attach policy to role: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def detach_role_policy(self, context: OperationContext, role_name: str, policy_arn: str) -> List[OperationResult]:
        """
        Detach policy from IAM role.

        Args:
            context: Operation context
            role_name: Name of role
            policy_arn: Policy ARN to detach

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")

        result = self.create_operation_result(context, "detach_role_policy", "iam:role", f"{role_name}:{policy_arn}")

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would detach policy {policy_arn} from role {role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(
                    iam_client, "detach_role_policy", RoleName=role_name, PolicyArn=policy_arn
                )

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully detached policy {policy_arn} from role {role_name}")

        except ClientError as e:
            error_msg = f"Failed to detach policy from role: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def create_policy(
        self,
        context: OperationContext,
        policy_name: str,
        policy_document: str,
        path: str = "/",
        description: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None,
    ) -> List[OperationResult]:
        """
        Create IAM policy.

        Args:
            context: Operation context
            policy_name: Name of policy to create
            policy_document: Policy document JSON
            path: Policy path
            description: Policy description
            tags: Policy tags

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")

        result = self.create_operation_result(context, "create_policy", "iam:policy", policy_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would create IAM policy {policy_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            create_params = {
                "PolicyName": policy_name,
                "PolicyDocument": policy_document,
                "Path": path,
            }

            if description:
                create_params["Description"] = description
            if tags:
                create_params["Tags"] = tags

            response = self.execute_aws_call(iam_client, "create_policy", **create_params)

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully created IAM policy {policy_name}")

        except ClientError as e:
            error_msg = f"Failed to create IAM policy {policy_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def delete_policy(self, context: OperationContext, policy_arn: str) -> List[OperationResult]:
        """
        Delete IAM policy.

        Args:
            context: Operation context
            policy_arn: ARN of policy to delete

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")

        result = self.create_operation_result(context, "delete_policy", "iam:policy", policy_arn)

        try:
            if not self.confirm_operation(context, policy_arn, "delete IAM policy"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would delete IAM policy {policy_arn}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                # Detach policy from all entities first
                entities = self.execute_aws_call(iam_client, "list_entities_for_policy", PolicyArn=policy_arn)

                # Detach from roles
                for role in entities.get("PolicyRoles", []):
                    self.execute_aws_call(
                        iam_client, "detach_role_policy", RoleName=role["RoleName"], PolicyArn=policy_arn
                    )

                # Detach from users
                for user in entities.get("PolicyUsers", []):
                    self.execute_aws_call(
                        iam_client, "detach_user_policy", UserName=user["UserName"], PolicyArn=policy_arn
                    )

                # Detach from groups
                for group in entities.get("PolicyGroups", []):
                    self.execute_aws_call(
                        iam_client, "detach_group_policy", GroupName=group["GroupName"], PolicyArn=policy_arn
                    )

                # Delete all non-default versions
                versions = self.execute_aws_call(iam_client, "list_policy_versions", PolicyArn=policy_arn)

                for version in versions.get("Versions", []):
                    if not version["IsDefaultVersion"]:
                        self.execute_aws_call(
                            iam_client, "delete_policy_version", PolicyArn=policy_arn, VersionId=version["VersionId"]
                        )

                # Finally delete the policy
                response = self.execute_aws_call(iam_client, "delete_policy", PolicyArn=policy_arn)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted IAM policy {policy_arn}")

        except ClientError as e:
            error_msg = f"Failed to delete IAM policy {policy_arn}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def tag_role(self, context: OperationContext, role_name: str, tags: List[Dict[str, str]]) -> List[OperationResult]:
        """
        Add tags to IAM role.

        Args:
            context: Operation context
            role_name: Name of role to tag
            tags: Tags to add

        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")

        result = self.create_operation_result(context, "tag_role", "iam:role", role_name)

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would add {len(tags)} tags to role {role_name}")
                result.mark_completed(OperationStatus.DRY_RUN)
            else:
                response = self.execute_aws_call(iam_client, "tag_role", RoleName=role_name, Tags=tags)

                result.response_data = response
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully added {len(tags)} tags to role {role_name}")

        except ClientError as e:
            error_msg = f"Failed to tag role {role_name}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    # =======================================
    # Access Key Management Operations
    # Migrated from unSkript AWS_Access_Key_Rotation.ipynb
    # =======================================

    @dataclass
    class ExpiringAccessKey:
        """Data class for expiring access key information."""
        username: str
        access_key_id: str
        create_date: datetime
        days_old: int

    def list_expiring_access_keys(
        self, context: OperationContext, threshold_days: int = 90
    ) -> List[OperationResult]:
        """
        List all IAM access keys that are expiring within threshold days.
        
        Migrated from unSkript aws_list_expiring_access_keys function.
        
        Args:
            context: Operation context
            threshold_days: Threshold number of days to check for expiry
            
        Returns:
            List of operation results with expiring access keys
        """
        iam_client = self.get_client("iam")
        
        result = self.create_operation_result(
            context, "list_expiring_access_keys", "iam:access-keys", f"threshold-{threshold_days}-days"
        )
        
        try:
            console.print(f"[blue]Checking for access keys older than {threshold_days} days...[/blue]")
            
            expiring_keys = []
            
            # Get all IAM users
            paginator = iam_client.get_paginator('list_users')
            
            for page in paginator.paginate():
                for user in page['Users']:
                    username = user['UserName']
                    
                    try:
                        # List access keys for each user
                        response = self.execute_aws_call(iam_client, "list_access_keys", UserName=username)
                        
                        for key_metadata in response.get("AccessKeyMetadata", []):
                            create_date = key_metadata["CreateDate"]
                            right_now = datetime.now(dateutil.tz.tzlocal())
                            
                            # Calculate age in days
                            age_diff = right_now - create_date
                            days_old = age_diff.days
                            
                            if days_old > threshold_days:
                                expiring_key = self.ExpiringAccessKey(
                                    username=username,
                                    access_key_id=key_metadata["AccessKeyId"],
                                    create_date=create_date,
                                    days_old=days_old
                                )
                                expiring_keys.append(expiring_key)
                                
                    except ClientError as e:
                        if e.response['Error']['Code'] != 'NoSuchEntity':
                            logger.warning(f"Failed to list access keys for user {username}: {e}")
                            
            # Display results with Rich table
            if expiring_keys:
                table = Table(title=f"Access Keys Expiring (>{threshold_days} days old)")
                table.add_column("Username", style="cyan")
                table.add_column("Access Key ID", style="yellow")
                table.add_column("Created Date", style="magenta")
                table.add_column("Days Old", style="red")
                
                for key in expiring_keys:
                    table.add_row(
                        key.username,
                        key.access_key_id,
                        key.create_date.strftime("%Y-%m-%d %H:%M:%S"),
                        str(key.days_old)
                    )
                    
                console.print(table)
                console.print(f"[red]Found {len(expiring_keys)} expiring access keys[/red]")
            else:
                console.print(Panel("[green]✅ No expiring access keys found[/green]", title="Success"))
                
            result.response_data = {
                "expiring_keys": [
                    {
                        "username": key.username,
                        "access_key_id": key.access_key_id,
                        "create_date": key.create_date.isoformat(),
                        "days_old": key.days_old
                    }
                    for key in expiring_keys
                ],
                "count": len(expiring_keys),
                "threshold_days": threshold_days
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Found {len(expiring_keys)} expiring access keys")
            
        except Exception as e:
            error_msg = f"Failed to list expiring access keys: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
            
        return [result]

    def create_access_key(self, context: OperationContext, username: str) -> List[OperationResult]:
        """
        Create new access key for specified IAM user.
        
        Migrated from unSkript aws_create_access_key function.
        
        Args:
            context: Operation context
            username: IAM username to create access key for
            
        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")
        
        result = self.create_operation_result(context, "create_access_key", "iam:access-key", username)
        
        try:
            if context.dry_run:
                console.print(f"[yellow][DRY-RUN] Would create new access key for user {username}[/yellow]")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]
                
            # Safety confirmation for access key creation
            if not self.confirm_operation(context, username, "create new access key for user"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]
                
            response = self.execute_aws_call(iam_client, "create_access_key", UserName=username)
            
            # Extract access key information
            access_key = response.get("AccessKey", {})
            
            # Display new access key information (with security warning)
            console.print(Panel(
                f"[green]✅ New access key created for user: {username}[/green]\n"
                f"[yellow]⚠️  IMPORTANT: Save these credentials securely![/yellow]\n"
                f"Access Key ID: [cyan]{access_key.get('AccessKeyId')}[/cyan]\n"
                f"Secret Access Key: [red]{'*' * 20}[/red] (Check logs for full key)",
                title="Access Key Created"
            ))
            
            result.response_data = {
                "username": username,
                "access_key_id": access_key.get("AccessKeyId"),
                "status": access_key.get("Status"),
                "create_date": access_key.get("CreateDate").isoformat() if access_key.get("CreateDate") else None,
                # Note: Secret key not stored in result for security
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully created access key for user {username}")
            
        except ClientError as e:
            error_msg = f"Failed to create access key for user {username}: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            
        return [result]

    def update_access_key_status(
        self, context: OperationContext, username: str, access_key_id: str, status: str
    ) -> List[OperationResult]:
        """
        Update access key status (Active/Inactive).
        
        Migrated from unSkript aws_update_access_key function.
        
        Args:
            context: Operation context
            username: IAM username
            access_key_id: Access key ID to update
            status: New status ('Active' or 'Inactive')
            
        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")
        
        result = self.create_operation_result(
            context, "update_access_key_status", "iam:access-key", f"{username}:{access_key_id}"
        )
        
        try:
            if status not in ['Active', 'Inactive']:
                raise ValueError(f"Invalid status '{status}'. Must be 'Active' or 'Inactive'")
                
            if context.dry_run:
                console.print(f"[yellow][DRY-RUN] Would update access key {access_key_id} status to {status}[/yellow]")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]
                
            # Safety confirmation for status changes
            if not self.confirm_operation(context, access_key_id, f"update access key status to {status}"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]
                
            response = self.execute_aws_call(
                iam_client, 
                "update_access_key", 
                UserName=username,
                AccessKeyId=access_key_id,
                Status=status
            )
            
            status_color = "green" if status == "Active" else "yellow"
            console.print(f"[{status_color}]✅ Access key {access_key_id} status updated to {status}[/{status_color}]")
            
            result.response_data = {
                "username": username,
                "access_key_id": access_key_id,
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully updated access key {access_key_id} status to {status}")
            
        except ClientError as e:
            error_msg = f"Failed to update access key status: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            
        return [result]

    def delete_access_key(self, context: OperationContext, username: str, access_key_id: str) -> List[OperationResult]:
        """
        Delete access key for specified user.
        
        Migrated from unSkript aws_delete_access_key function.
        
        Args:
            context: Operation context
            username: IAM username
            access_key_id: Access key ID to delete
            
        Returns:
            List of operation results
        """
        iam_client = self.get_client("iam")
        
        result = self.create_operation_result(
            context, "delete_access_key", "iam:access-key", f"{username}:{access_key_id}"
        )
        
        try:
            if context.dry_run:
                console.print(f"[yellow][DRY-RUN] Would delete access key {access_key_id} for user {username}[/yellow]")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]
                
            # Strong confirmation required for deletion
            console.print(f"[red]⚠️  WARNING: This will permanently delete access key {access_key_id}[/red]")
            if not self.confirm_operation(context, access_key_id, f"PERMANENTLY DELETE access key"):
                result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                return [result]
                
            response = self.execute_aws_call(
                iam_client,
                "delete_access_key",
                UserName=username,
                AccessKeyId=access_key_id
            )
            
            console.print(f"[green]✅ Access key {access_key_id} successfully deleted[/green]")
            
            result.response_data = {
                "username": username,
                "access_key_id": access_key_id,
                "deleted_at": datetime.now().isoformat()
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully deleted access key {access_key_id} for user {username}")
            
        except ClientError as e:
            error_msg = f"Failed to delete access key: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            
        return [result]

    def rotate_access_keys(
        self, context: OperationContext, threshold_days: int = 90, auto_rotate: bool = False
    ) -> List[OperationResult]:
        """
        Complete access key rotation workflow combining all steps.
        
        This orchestrates the full unSkript notebook workflow:
        1. List expiring access keys
        2. Create new access keys  
        3. Deactivate old access keys
        4. Delete old access keys (optional)
        
        Args:
            context: Operation context
            threshold_days: Age threshold for rotation
            auto_rotate: If True, automatically rotates without confirmation per key
            
        Returns:
            List of operation results
        """
        results = []
        
        # Step 1: Find expiring access keys
        console.print(Panel("[blue]Step 1: Finding expiring access keys...[/blue]", title="Access Key Rotation"))
        expiring_result = self.list_expiring_access_keys(context, threshold_days=threshold_days)
        results.extend(expiring_result)
        
        if not expiring_result or expiring_result[0].status == OperationStatus.FAILED:
            return results
            
        expiring_keys_data = expiring_result[0].response_data.get("expiring_keys", [])
        
        if not expiring_keys_data:
            console.print(Panel("[green]✅ No access keys need rotation[/green]", title="Complete"))
            return results
            
        console.print(f"[yellow]Found {len(expiring_keys_data)} keys to rotate[/yellow]")
        
        if not auto_rotate:
            if not self.confirm_operation(context, f"{len(expiring_keys_data)} access keys", "rotate"):
                cancelled_result = self.create_operation_result(
                    context, "rotate_access_keys", "iam:access-keys", "rotation-workflow"
                )
                cancelled_result.mark_completed(OperationStatus.CANCELLED, "Rotation cancelled by user")
                results.append(cancelled_result)
                return results
        
        # Steps 2-4: Rotate each expiring key
        for key_data in expiring_keys_data:
            username = key_data["username"]
            old_access_key_id = key_data["access_key_id"]
            
            console.print(f"[cyan]Rotating access key for user: {username}[/cyan]")
            
            # Step 2: Create new access key
            console.print(f"[blue]  → Creating new access key...[/blue]")
            create_result = self.create_access_key(context, username=username)
            results.extend(create_result)
            
            if create_result[0].status == OperationStatus.SUCCESS:
                # Step 3: Deactivate old access key
                console.print(f"[yellow]  → Deactivating old access key...[/yellow]")
                deactivate_result = self.update_access_key_status(
                    context, username=username, access_key_id=old_access_key_id, status="Inactive"
                )
                results.extend(deactivate_result)
                
                if deactivate_result[0].status == OperationStatus.SUCCESS:
                    # Step 4: Option to delete old key (with confirmation)
                    console.print(f"[red]  → Old key deactivated. Delete permanently?[/red]")
                    if auto_rotate or self.confirm_operation(
                        context, old_access_key_id, "delete old access key"
                    ):
                        delete_result = self.delete_access_key(
                            context, username=username, access_key_id=old_access_key_id
                        )
                        results.extend(delete_result)
                    else:
                        console.print(f"[yellow]  → Old key kept inactive for manual cleanup[/yellow]")
                        
        console.print(Panel("[green]✅ Access key rotation workflow complete[/green]", title="Complete"))
        return results

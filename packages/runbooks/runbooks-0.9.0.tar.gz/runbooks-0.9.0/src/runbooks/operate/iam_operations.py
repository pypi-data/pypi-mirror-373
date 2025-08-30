"""
IAM Operations Module.

Provides comprehensive IAM resource management capabilities including role management,
policy operations, and cross-account access management.

Migrated and enhanced from:
- inventory/update_iam_roles_cross_accounts.py
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus


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

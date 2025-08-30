"""
Enterprise Remediation Base Classes - Production-Ready Security & Compliance Automation

This module provides the foundational architecture for AWS security and compliance
remediation operations, designed to integrate seamlessly with assessment findings
from security and CFAT modules.

## Design Principles

**Safety First**: All operations include dry-run, backup, and rollback capabilities
**Enterprise Ready**: Multi-account, multi-region support with SSO integration
**Audit Compliant**: Complete operation tracking and compliance mapping
**Assessment Integration**: Direct integration with security/CFAT findings

## Architecture

The remediation framework follows proven enterprise patterns from the operate module:

- **BaseRemediation**: Abstract base class for all remediation operations
- **RemediationContext**: Execution context with assessment findings integration
- **RemediationResult**: Structured outcomes with compliance mapping
- **RemediationStatus**: Operation states and progress tracking

## Example Usage

```python
from runbooks.remediation import S3SecurityRemediation
from runbooks.security import SecurityBaselineTester

# 1. Run security assessment
security_findings = SecurityBaselineTester().run_assessment()

# 2. Create remediation context from findings
context = RemediationContext.from_security_findings(security_findings)

# 3. Execute remediation with safety checks
s3_remediation = S3SecurityRemediation()
results = s3_remediation.enforce_ssl(context, bucket_name="critical-data")

# 4. Verify remediation success
verification_results = security_findings.verify_remediation(results)
```

## Multi-Account Integration

All remediation operations support enterprise multi-account patterns:

```python
# Multi-account remediation execution
accounts = ["123456789012", "987654321098", "456789012345"]
results = s3_remediation.enforce_ssl_bulk(context, accounts=accounts)
```

## Compliance Mapping

Each remediation operation includes compliance framework mapping:

- **CIS AWS Foundations Benchmark**: Direct control mapping
- **NIST Cybersecurity Framework**: Category and function alignment
- **AWS Well-Architected Framework**: Pillar and principle mapping
- **CheckPoint CloudGuard/Dome9**: Rule-by-rule remediation mapping

Version: 0.7.8 - Enterprise Production Ready
Compatibility: AWS SDK v3, Python 3.8+, Multi-deployment ready
"""

import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

import boto3
import click
from botocore.exceptions import BotoCoreError, ClientError
from loguru import logger
from pydantic import BaseModel, Field

from runbooks.inventory.models.account import AWSAccount


class RemediationStatus(Enum):
    """
    Enumerated remediation operation states.

    Provides consistent status tracking across all remediation operations
    with clear semantic meaning for enterprise reporting and monitoring.
    """

    PENDING = "pending"  # Remediation planned but not started
    IN_PROGRESS = "in_progress"  # Remediation currently executing
    SUCCESS = "success"  # Remediation completed successfully
    FAILED = "failed"  # Remediation failed with errors
    DRY_RUN = "dry_run"  # Dry-run mode (no actual changes)
    CANCELLED = "cancelled"  # User cancelled operation
    ROLLED_BACK = "rolled_back"  # Operation rolled back
    REQUIRES_MANUAL = "requires_manual"  # Manual intervention required
    SKIPPED = "skipped"  # Operation skipped (already compliant)


class ComplianceMapping(BaseModel):
    """
    Compliance framework mapping for remediation operations.

    Maps each remediation to relevant compliance frameworks and controls,
    enabling automated compliance reporting and audit trail generation.
    """

    cis_controls: List[str] = Field(default_factory=list, description="CIS AWS Foundations controls")
    nist_categories: List[str] = Field(default_factory=list, description="NIST Cybersecurity Framework categories")
    well_architected_pillars: List[str] = Field(default_factory=list, description="AWS Well-Architected pillars")
    dome9_rules: List[str] = Field(default_factory=list, description="CheckPoint CloudGuard/Dome9 rules")
    aws_config_rules: List[str] = Field(default_factory=list, description="AWS Config compliance rules")
    severity: str = Field(default="medium", description="Risk severity level")


class RemediationContext(BaseModel):
    """
    Comprehensive execution context for remediation operations.

    Provides all necessary context for safe, auditable remediation execution
    including account information, safety settings, and assessment integration.

    Attributes:
        account: AWS account information
        region: Target AWS region
        operation_type: Type of remediation operation
        resource_types: AWS resource types affected
        dry_run: Safety flag for testing operations
        force: Override confirmation prompts (for automation)
        backup_enabled: Enable automatic backup creation
        compliance_mapping: Compliance framework mapping
        assessment_findings: Related assessment findings
        rollback_plan: Automatic rollback configuration
        change_ticket: Change management integration
    """

    account: AWSAccount
    region: str = Field(default="us-east-1", description="AWS region")
    operation_type: str = Field(description="Remediation operation type")
    resource_types: List[str] = Field(default_factory=list, description="AWS resource types")

    # Safety and control flags
    dry_run: bool = Field(default=True, description="Enable dry-run mode")
    force: bool = Field(default=False, description="Skip confirmation prompts")
    backup_enabled: bool = Field(default=True, description="Enable automatic backups")

    # Compliance and audit
    compliance_mapping: ComplianceMapping = Field(default_factory=ComplianceMapping)
    assessment_findings: Dict[str, Any] = Field(default_factory=dict, description="Related assessment findings")

    # Enterprise features
    rollback_plan: Dict[str, Any] = Field(default_factory=dict, description="Rollback configuration")
    change_ticket: Optional[str] = Field(default=None, description="Change management ticket")
    notification_targets: List[str] = Field(default_factory=list, description="SNS notification targets")

    @classmethod
    def from_security_findings(cls, findings: Dict[str, Any], **kwargs) -> "RemediationContext":
        """
        Create remediation context from security assessment findings.

        Args:
            findings: Security assessment findings from security module
            **kwargs: Additional context parameters

        Returns:
            RemediationContext with populated assessment data

        Example:
            ```python
            security_findings = SecurityBaselineTester().run_assessment()
            context = RemediationContext.from_security_findings(security_findings)
            ```
        """
        # Extract account information from findings
        account_id = findings.get("account_id", "unknown")
        account_name = findings.get("account_name", "unknown")
        account = AWSAccount(account_id=account_id, account_name=account_name)

        # Map findings to compliance frameworks
        compliance_mapping = ComplianceMapping()
        if "cis_controls" in findings:
            compliance_mapping.cis_controls = findings["cis_controls"]
        if "severity" in findings:
            compliance_mapping.severity = findings["severity"]

        return cls(
            account=account,
            operation_type="security_remediation",
            assessment_findings=findings,
            compliance_mapping=compliance_mapping,
            **kwargs,
        )

    @classmethod
    def from_cfat_findings(cls, findings: Dict[str, Any], **kwargs) -> "RemediationContext":
        """
        Create remediation context from CFAT assessment findings.

        Args:
            findings: CFAT assessment findings from cfat module
            **kwargs: Additional context parameters

        Returns:
            RemediationContext with populated assessment data
        """
        account_id = findings.get("account_id", "unknown")
        account_name = findings.get("account_name", "unknown")
        account = AWSAccount(account_id=account_id, account_name=account_name)

        # Map CFAT findings to Well-Architected pillars
        compliance_mapping = ComplianceMapping()
        if "well_architected_pillars" in findings:
            compliance_mapping.well_architected_pillars = findings["well_architected_pillars"]

        return cls(
            account=account,
            operation_type="cfat_remediation",
            assessment_findings=findings,
            compliance_mapping=compliance_mapping,
            **kwargs,
        )


class RemediationResult(BaseModel):
    """
    Structured result from remediation operations.

    Provides comprehensive outcome tracking with compliance mapping,
    backup information, and rollback capabilities for enterprise audit trails.

    Attributes:
        operation_id: Unique operation identifier
        context: Original operation context
        status: Current operation status
        start_time: Operation start timestamp
        end_time: Operation completion timestamp
        affected_resources: List of resources modified
        backup_locations: Backup storage locations
        rollback_instructions: Manual rollback procedures
        compliance_evidence: Compliance verification data
        error_message: Error details if operation failed
        response_data: Raw AWS API response data
    """

    operation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique operation ID")
    context: RemediationContext
    status: RemediationStatus = Field(default=RemediationStatus.PENDING)

    # Timing information
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(default=None)
    duration_seconds: Optional[float] = Field(default=None)

    # Resource tracking
    affected_resources: List[str] = Field(default_factory=list, description="Resources modified")
    backup_locations: Dict[str, str] = Field(default_factory=dict, description="Backup storage locations")

    # Enterprise features
    rollback_instructions: List[str] = Field(default_factory=list, description="Rollback procedures")
    compliance_evidence: Dict[str, Any] = Field(default_factory=dict, description="Compliance verification")

    # Operation outcomes
    error_message: Optional[str] = Field(default=None)
    response_data: Dict[str, Any] = Field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if remediation was successful."""
        return self.status == RemediationStatus.SUCCESS

    @property
    def failed(self) -> bool:
        """Check if remediation failed."""
        return self.status == RemediationStatus.FAILED

    def mark_completed(self, status: RemediationStatus, error_message: str = None) -> None:
        """
        Mark remediation as completed with final status.

        Args:
            status: Final operation status
            error_message: Error details if operation failed
        """
        self.status = status
        self.end_time = datetime.utcnow()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()

        if error_message:
            self.error_message = error_message

        logger.info(f"Remediation {self.operation_id} completed with status: {status.value}")

    def create_rollback_plan(self, instructions: List[str]) -> None:
        """
        Create rollback plan with manual instructions.

        Args:
            instructions: Step-by-step rollback procedures
        """
        self.rollback_instructions = instructions
        logger.info(f"Rollback plan created for operation {self.operation_id}")

    def add_compliance_evidence(self, framework: str, evidence: Dict[str, Any]) -> None:
        """
        Add compliance verification evidence.

        Args:
            framework: Compliance framework name (CIS, NIST, etc.)
            evidence: Verification evidence data
        """
        self.compliance_evidence[framework] = evidence
        logger.debug(f"Compliance evidence added for {framework}")


class BaseRemediation(ABC):
    """
    Abstract base class for all AWS remediation operations.

    Provides consistent enterprise patterns for safety, auditing, and compliance
    across all remediation implementations. Follows the proven architecture
    from the operate module with enhanced safety and compliance features.

    Key Features:
    - Automatic backup creation before changes
    - Comprehensive dry-run capabilities
    - Multi-account and multi-region support
    - Compliance framework mapping
    - Integration with assessment findings
    - Rollback and recovery procedures

    Example Implementation:
    ```python
    class S3SecurityRemediation(BaseRemediation):
        supported_operations = ["enforce_ssl", "block_public_access", "enable_encryption"]

        def enforce_ssl(self, context: RemediationContext, bucket_name: str) -> List[RemediationResult]:
            result = self.create_remediation_result(context, "enforce_ssl", "s3:bucket", bucket_name)

            try:
                # Create backup if enabled
                if context.backup_enabled:
                    self.create_backup(context, bucket_name)

                # Execute remediation
                if not context.dry_run:
                    self.apply_ssl_policy(bucket_name)

                result.mark_completed(RemediationStatus.SUCCESS)

            except Exception as e:
                result.mark_completed(RemediationStatus.FAILED, str(e))

            return [result]
    ```
    """

    supported_operations: List[str] = []

    def __init__(self, profile: str = None, region: str = None, **kwargs):
        """
        Initialize remediation base with AWS configuration.

        Args:
            profile: AWS profile name (uses environment if not specified)
            region: AWS region (uses environment if not specified)
            **kwargs: Additional configuration parameters
        """
        self.profile = profile or os.getenv("AWS_PROFILE", "default")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")

        # Enterprise configuration
        self.backup_enabled = kwargs.get("backup_enabled", True)
        self.notification_enabled = kwargs.get("notification_enabled", False)
        self.sns_topic_arn = kwargs.get("sns_topic_arn", os.getenv("REMEDIATION_SNS_TOPIC_ARN"))

        # Initialize AWS clients lazily
        self._session = None
        self._clients = {}

        logger.info(f"Initialized remediation base for profile: {self.profile}, region: {self.region}")

    @property
    def session(self) -> boto3.Session:
        """Get or create AWS session with profile configuration."""
        if self._session is None:
            try:
                self._session = boto3.Session(profile_name=self.profile, region_name=self.region)
            except Exception as e:
                logger.warning(f"Failed to create session with profile {self.profile}: {e}")
                self._session = boto3.Session(region_name=self.region)
        return self._session

    def get_client(self, service_name: str, region: str = None) -> Any:
        """
        Get or create AWS service client with caching.

        Args:
            service_name: AWS service name (e.g., 's3', 'ec2', 'iam')
            region: Override region for client

        Returns:
            Configured AWS service client
        """
        region = region or self.region
        client_key = f"{service_name}_{region}"

        if client_key not in self._clients:
            try:
                self._clients[client_key] = self.session.client(service_name, region_name=region)
                logger.debug(f"Created AWS client for {service_name} in {region}")
            except Exception as e:
                logger.error(f"Failed to create {service_name} client: {e}")
                raise

        return self._clients[client_key]

    def create_remediation_result(
        self, context: RemediationContext, operation_type: str, resource_type: str, resource_id: str
    ) -> RemediationResult:
        """
        Create standardized remediation result object.

        Args:
            context: Remediation execution context
            operation_type: Type of remediation operation
            resource_type: AWS resource type (e.g., 's3:bucket', 'ec2:instance')
            resource_id: Unique resource identifier

        Returns:
            Initialized RemediationResult object
        """
        # Update context with operation details
        context.operation_type = operation_type
        if resource_type not in context.resource_types:
            context.resource_types.append(resource_type)

        result = RemediationResult(context=context, affected_resources=[f"{resource_type}:{resource_id}"])

        logger.info(f"Created remediation result {result.operation_id} for {resource_type}:{resource_id}")
        return result

    def execute_aws_call(self, client: Any, method_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute AWS API call with enterprise error handling.

        Args:
            client: AWS service client
            method_name: API method name
            **kwargs: Method parameters

        Returns:
            AWS API response data

        Raises:
            ClientError: AWS service errors
            BotoCoreError: Boto3 core errors
        """
        try:
            method = getattr(client, method_name)
            response = method(**kwargs)
            logger.debug(f"AWS API call successful: {method_name}")
            return response

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))
            logger.error(f"AWS ClientError in {method_name}: {error_code} - {error_message}")
            raise

        except BotoCoreError as e:
            logger.error(f"AWS BotoCoreError in {method_name}: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error in {method_name}: {e}")
            raise

    def create_backup(self, context: RemediationContext, resource_id: str, backup_type: str = "configuration") -> str:
        """
        Create backup of resource configuration before remediation.

        Args:
            context: Remediation execution context
            resource_id: Resource identifier
            backup_type: Type of backup (configuration, snapshot, etc.)

        Returns:
            Backup location or identifier
        """
        if not context.backup_enabled:
            logger.info("Backup disabled, skipping backup creation")
            return ""

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_key = f"remediation_backup_{resource_id}_{timestamp}"

        try:
            # Implementation depends on resource type
            backup_location = self._create_resource_backup(resource_id, backup_key, backup_type)
            logger.info(f"Backup created for {resource_id} at {backup_location}")
            return backup_location

        except Exception as e:
            logger.error(f"Failed to create backup for {resource_id}: {e}")
            raise

    @abstractmethod
    def _create_resource_backup(self, resource_id: str, backup_key: str, backup_type: str) -> str:
        """
        Implementation-specific backup creation.

        Must be implemented by each remediation class to handle
        resource-specific backup procedures.
        """
        pass

    def confirm_operation(self, context: RemediationContext, resource_id: str, operation_type: str) -> bool:
        """
        Confirm destructive operations with user interaction.

        Args:
            context: Remediation execution context
            resource_id: Resource identifier
            operation_type: Operation description

        Returns:
            True if operation confirmed, False otherwise
        """
        if context.force:
            logger.info(f"Force mode enabled, skipping confirmation for {operation_type}")
            return True

        if context.dry_run:
            logger.info(f"Dry-run mode, confirmation not required for {operation_type}")
            return True

        try:
            confirmation = click.confirm(
                f"⚠️  DESTRUCTIVE OPERATION: {operation_type} on {resource_id}. Continue?", default=False
            )
            if confirmation:
                logger.info(f"User confirmed {operation_type} on {resource_id}")
            else:
                logger.info(f"User cancelled {operation_type} on {resource_id}")
            return confirmation

        except Exception as e:
            logger.error(f"Confirmation prompt failed: {e}")
            return False

    def send_notification(self, context: RemediationContext, result: RemediationResult) -> None:
        """
        Send operation notification via SNS.

        Args:
            context: Remediation execution context
            result: Remediation operation result
        """
        if not self.notification_enabled or not self.sns_topic_arn:
            return

        try:
            sns_client = self.get_client("sns")

            message = {
                "operation_id": result.operation_id,
                "operation_type": context.operation_type,
                "status": result.status.value,
                "account": context.account.account_id,
                "region": context.region,
                "affected_resources": result.affected_resources,
                "duration_seconds": result.duration_seconds,
            }

            subject = f"Remediation {result.status.value}: {context.operation_type}"

            self.execute_aws_call(
                sns_client,
                "publish",
                TopicArn=self.sns_topic_arn,
                Message=json.dumps(message, default=str),
                Subject=subject,
            )

            logger.info(f"Notification sent for operation {result.operation_id}")

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    @abstractmethod
    def execute_remediation(self, context: RemediationContext, **kwargs) -> List[RemediationResult]:
        """
        Execute specific remediation operation.

        Must be implemented by each remediation class to provide
        the actual remediation logic for their service area.

        Args:
            context: Remediation execution context
            **kwargs: Operation-specific parameters

        Returns:
            List of remediation results
        """
        pass

    def bulk_execute(self, contexts: List[RemediationContext], **kwargs) -> List[RemediationResult]:
        """
        Execute remediation across multiple accounts/resources.

        Args:
            contexts: List of remediation contexts
            **kwargs: Operation-specific parameters

        Returns:
            Consolidated list of remediation results
        """
        all_results = []

        for context in contexts:
            try:
                results = self.execute_remediation(context, **kwargs)
                all_results.extend(results)

                # Send notifications for each result
                for result in results:
                    self.send_notification(context, result)

            except Exception as e:
                logger.error(f"Bulk execution failed for context {context.account.account_id}: {e}")
                # Create failure result
                error_result = self.create_remediation_result(
                    context, "bulk_execution", "account", context.account.account_id
                )
                error_result.mark_completed(RemediationStatus.FAILED, str(e))
                all_results.append(error_result)

        logger.info(f"Bulk execution completed: {len(all_results)} total results")
        return all_results

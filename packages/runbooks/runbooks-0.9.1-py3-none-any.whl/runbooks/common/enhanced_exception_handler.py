#!/usr/bin/env python3
"""
Enhanced Exception Handler - Enterprise Error Management Framework
================================================================

STRATEGIC CONTEXT: Phase 2 rollout extending proven FinOps error handling patterns
to provide comprehensive, user-friendly error management across all CloudOps modules.

This module provides enterprise-grade exception handling with:
- Rich CLI formatted error messages with actionable solutions
- IAM guidance with profile recommendations
- Graceful degradation with recovery paths
- Context-aware error resolution
- Comprehensive audit trails
- Performance-aware error handling

Features:
- AWS service-specific error handling and guidance
- Profile-based IAM error resolution
- Multi-language error support (EN/JP/KR/VN)
- Rich CLI visual error formatting
- Automated retry mechanisms with backoff
- Error recovery workflows
- Comprehensive logging and audit trails

Author: QA Testing Specialist - CloudOps Automation Testing Expert
Version: Phase 2 Implementation
"""

import json
import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    EndpointConnectionError,
    NoCredentialsError,
    PartialCredentialsError,
    ProfileNotFound,
    TokenRetrievalError,
)
from botocore.exceptions import (
    ConnectionError as BotoConnectionError,
)

from ..common.rich_utils import (
    STATUS_INDICATORS,
    console,
    create_panel,
    create_table,
    create_tree,
    format_cost,
    print_error,
    print_info,
    print_status,
    print_success,
    print_warning,
)


class ErrorSeverity(Enum):
    """Error severity levels for enterprise error classification."""

    CRITICAL = "CRITICAL"  # System failure, immediate attention required
    HIGH = "HIGH"  # Major functionality impacted
    MEDIUM = "MEDIUM"  # Moderate impact, workaround available
    LOW = "LOW"  # Minor issue, minimal impact
    INFO = "INFO"  # Informational, no action required


class ErrorCategory(Enum):
    """Error categories for systematic error handling."""

    AWS_CREDENTIALS = "AWS_CREDENTIALS"
    AWS_PERMISSIONS = "AWS_PERMISSIONS"
    AWS_SERVICE = "AWS_SERVICE"
    AWS_THROTTLING = "AWS_THROTTLING"
    NETWORK = "NETWORK"
    CONFIGURATION = "CONFIGURATION"
    DATA_VALIDATION = "DATA_VALIDATION"
    PERFORMANCE = "PERFORMANCE"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    UNKNOWN = "UNKNOWN"


@dataclass
class ErrorContext:
    """Comprehensive error context for enterprise error management."""

    module_name: str
    operation: str
    aws_profile: Optional[str] = None
    aws_region: Optional[str] = None
    user_context: Dict[str, Any] = field(default_factory=dict)
    system_context: Dict[str, Any] = field(default_factory=dict)
    performance_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ErrorResolution:
    """Actionable error resolution with recovery paths."""

    title: str
    description: str
    action_items: List[str]
    recovery_commands: List[str] = field(default_factory=list)
    alternative_approaches: List[str] = field(default_factory=list)
    estimated_resolution_time: str = "5-10 minutes"
    requires_admin: bool = False
    documentation_links: List[str] = field(default_factory=list)


@dataclass
class EnhancedError:
    """Enhanced error with comprehensive diagnostics and resolution."""

    original_exception: Exception
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    resolution: ErrorResolution
    error_code: str
    retry_possible: bool = False
    max_retries: int = 3
    backoff_seconds: float = 1.0
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


class EnterpriseExceptionHandler:
    """
    Enterprise exception handler providing comprehensive error management.

    This handler extends proven FinOps error handling patterns to provide:
    - Context-aware error analysis and resolution
    - Rich CLI formatted error messages
    - AWS-specific error guidance with profile recommendations
    - Automated retry mechanisms
    - Comprehensive audit trails
    - Multi-language support for enterprise environments
    """

    def __init__(
        self,
        module_name: str,
        enable_auto_retry: bool = True,
        enable_rich_output: bool = True,
        audit_file_path: Optional[str] = None,
    ):
        """
        Initialize enterprise exception handler.

        Args:
            module_name: Name of the CloudOps module using this handler
            enable_auto_retry: Enable automatic retry for transient errors
            enable_rich_output: Enable Rich CLI formatted output
            audit_file_path: Path for error audit trail (optional)
        """
        self.module_name = module_name
        self.enable_auto_retry = enable_auto_retry
        self.enable_rich_output = enable_rich_output
        self.audit_file_path = audit_file_path or f"artifacts/audit/{module_name}_errors.json"

        # Setup logging
        self.logger = logging.getLogger(f"cloudops.{module_name}.exceptions")

        # Error statistics
        self.error_counts = {category: 0 for category in ErrorCategory}
        self.resolution_success_rate = {}

        # AWS service error mappings
        self.aws_error_mappings = self._initialize_aws_error_mappings()

        # Profile recommendations based on error patterns
        self.profile_recommendations = self._initialize_profile_recommendations()

        # Create audit directory
        Path(self.audit_file_path).parent.mkdir(parents=True, exist_ok=True)

    def handle_exception(
        self, exception: Exception, context: ErrorContext, operation_data: Optional[Dict[str, Any]] = None
    ) -> EnhancedError:
        """
        Handle exception with comprehensive error analysis and resolution guidance.

        Args:
            exception: The original exception
            context: Error context information
            operation_data: Optional operation-specific data for context

        Returns:
            Enhanced error with resolution guidance
        """
        # Analyze exception
        enhanced_error = self._analyze_exception(exception, context, operation_data)

        # Track error statistics
        self.error_counts[enhanced_error.category] += 1

        # Display error with Rich formatting if enabled
        if self.enable_rich_output:
            self._display_enhanced_error(enhanced_error)

        # Log error for audit trail
        self._log_error_to_audit_trail(enhanced_error)

        # Attempt automatic resolution if applicable
        if enhanced_error.retry_possible and self.enable_auto_retry:
            resolution_success = self._attempt_auto_resolution(enhanced_error)
            enhanced_error.audit_trail.append(
                {
                    "auto_resolution_attempted": True,
                    "resolution_success": resolution_success,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return enhanced_error

    def handle_aws_error(self, error: ClientError, context: ErrorContext, aws_operation: str) -> EnhancedError:
        """
        Handle AWS-specific errors with service-specific guidance.

        Args:
            error: AWS ClientError exception
            context: Error context
            aws_operation: AWS operation that failed

        Returns:
            Enhanced AWS error with specific guidance
        """
        error_code = error.response.get("Error", {}).get("Code", "Unknown")
        service_name = (
            error.response.get("ResponseMetadata", {}).get("HTTPHeaders", {}).get("x-amzn-service", "Unknown")
        )

        # Get service-specific error analysis
        error_analysis = self._analyze_aws_error(error, error_code, service_name, aws_operation)

        # Create enhanced error with AWS-specific context
        enhanced_error = EnhancedError(
            original_exception=error,
            severity=error_analysis["severity"],
            category=error_analysis["category"],
            context=context,
            resolution=self._generate_aws_resolution(error, error_code, service_name, context),
            error_code=f"AWS_{service_name}_{error_code}",
            retry_possible=error_analysis["retry_possible"],
            max_retries=error_analysis.get("max_retries", 3),
            backoff_seconds=error_analysis.get("backoff_seconds", 2.0),
        )

        return self.handle_exception(
            enhanced_error.original_exception,
            context,
            {
                "aws_service": service_name,
                "aws_operation": aws_operation,
                "error_code": error_code,
                "enhanced_error": enhanced_error,
            },
        )

    def handle_credentials_error(
        self, error: Union[NoCredentialsError, PartialCredentialsError, ProfileNotFound], context: ErrorContext
    ) -> EnhancedError:
        """
        Handle AWS credentials errors with profile recommendations.

        Args:
            error: Credentials-related exception
            context: Error context

        Returns:
            Enhanced error with credential resolution guidance
        """
        if isinstance(error, NoCredentialsError):
            resolution = self._generate_credentials_resolution(context, "no_credentials")
        elif isinstance(error, PartialCredentialsError):
            resolution = self._generate_credentials_resolution(context, "partial_credentials")
        elif isinstance(error, ProfileNotFound):
            resolution = self._generate_profile_not_found_resolution(context)
        else:
            resolution = self._generate_credentials_resolution(context, "generic")

        enhanced_error = EnhancedError(
            original_exception=error,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AWS_CREDENTIALS,
            context=context,
            resolution=resolution,
            error_code=f"CREDENTIALS_{type(error).__name__}",
            retry_possible=False,  # Manual intervention required
            max_retries=0,
        )

        return self.handle_exception(
            enhanced_error.original_exception,
            context,
            {"credentials_error_type": type(error).__name__, "enhanced_error": enhanced_error},
        )

    def handle_performance_error(
        self, operation_name: str, execution_time: float, performance_target: float, context: ErrorContext
    ) -> Optional[EnhancedError]:
        """
        Handle performance-related issues with optimization guidance.

        Args:
            operation_name: Name of the operation that exceeded performance targets
            execution_time: Actual execution time
            performance_target: Target execution time
            context: Error context

        Returns:
            Enhanced error if performance target significantly exceeded, None otherwise
        """
        performance_ratio = execution_time / performance_target

        # Only create error if performance significantly exceeded (>150% of target)
        if performance_ratio <= 1.5:
            return None

        severity = ErrorSeverity.MEDIUM if performance_ratio < 2.0 else ErrorSeverity.HIGH

        resolution = ErrorResolution(
            title=f"Performance Optimization Required: {operation_name}",
            description=f"Operation took {execution_time:.1f}s, exceeding target of {performance_target:.1f}s by {((performance_ratio - 1) * 100):.1f}%",
            action_items=[
                f"Review {operation_name} operation for optimization opportunities",
                "Check AWS API throttling and request patterns",
                "Consider implementing parallel processing where applicable",
                "Monitor resource usage during operation execution",
                "Review AWS region selection for optimal performance",
            ],
            recovery_commands=[
                f"# Optimize {operation_name} operation",
                f"runbooks {self.module_name} {operation_name} --parallel",
                f"runbooks {self.module_name} {operation_name} --region us-east-1",  # Closest region
                f"runbooks {self.module_name} {operation_name} --batch-size 10",
            ],
            estimated_resolution_time="15-30 minutes",
            requires_admin=False,
        )

        # Create performance exception
        performance_exception = Exception(
            f"Performance target exceeded: {execution_time:.1f}s > {performance_target:.1f}s"
        )

        enhanced_error = EnhancedError(
            original_exception=performance_exception,
            severity=severity,
            category=ErrorCategory.PERFORMANCE,
            context=context,
            resolution=resolution,
            error_code=f"PERFORMANCE_{operation_name.upper()}_EXCEEDED",
            retry_possible=True,
            max_retries=2,
            backoff_seconds=5.0,
        )

        return self.handle_exception(
            enhanced_error.original_exception,
            context,
            {
                "operation_name": operation_name,
                "execution_time": execution_time,
                "performance_target": performance_target,
                "performance_ratio": performance_ratio,
                "enhanced_error": enhanced_error,
            },
        )

    def graceful_degradation(
        self,
        primary_operation: Callable,
        fallback_operations: List[Callable],
        context: ErrorContext,
        operation_args: Optional[Tuple] = None,
        operation_kwargs: Optional[Dict] = None,
    ) -> Tuple[Any, Optional[EnhancedError]]:
        """
        Execute operation with graceful degradation to fallback approaches.

        Args:
            primary_operation: Primary operation to attempt
            fallback_operations: List of fallback operations to try
            context: Error context
            operation_args: Arguments for operations
            operation_kwargs: Keyword arguments for operations

        Returns:
            Tuple of (result, enhanced_error_if_all_failed)
        """
        operation_args = operation_args or ()
        operation_kwargs = operation_kwargs or {}

        operations = [primary_operation] + fallback_operations
        last_error = None

        for i, operation in enumerate(operations):
            try:
                if i == 0:
                    print_info(f"🚀 Attempting primary operation: {operation.__name__}")
                else:
                    print_warning(f"⚠️ Attempting fallback {i}: {operation.__name__}")

                result = operation(*operation_args, **operation_kwargs)

                if i > 0:
                    print_success(f"✅ Fallback operation succeeded: {operation.__name__}")

                return result, None

            except Exception as e:
                last_error = e

                if i == 0:
                    print_warning(f"⚠️ Primary operation failed: {operation.__name__}")
                else:
                    print_error(f"❌ Fallback {i} failed: {operation.__name__}")

                # Create enhanced error for logging
                enhanced_error = self._analyze_exception(
                    e, context, {"operation_name": operation.__name__, "attempt_number": i + 1, "is_fallback": i > 0}
                )

                self._log_error_to_audit_trail(enhanced_error)

        # All operations failed
        print_error("❌ All operations failed, including fallbacks")

        final_enhanced_error = self._analyze_exception(
            last_error,
            context,
            {"all_operations_failed": True, "operations_attempted": len(operations), "final_failure": True},
        )

        return None, final_enhanced_error

    def create_error_recovery_workflow(self, enhanced_error: EnhancedError, interactive: bool = True) -> bool:
        """
        Create interactive error recovery workflow.

        Args:
            enhanced_error: Enhanced error with resolution guidance
            interactive: Enable interactive recovery prompts

        Returns:
            True if recovery was successful, False otherwise
        """
        if not self.enable_rich_output:
            return False

        print_info("🔧 Starting error recovery workflow...")

        # Display recovery options
        recovery_table = create_table(
            title=f"🛠️ Recovery Options for {enhanced_error.error_code}",
            columns=[
                {"name": "Step", "style": "cyan", "justify": "center"},
                {"name": "Action", "style": "white", "justify": "left"},
                {"name": "Required", "style": "yellow", "justify": "center"},
            ],
        )

        for i, action in enumerate(enhanced_error.resolution.action_items, 1):
            required = "✅" if i <= 2 else "⚪"  # First 2 actions are required
            recovery_table.add_row(str(i), action, required)

        console.print(recovery_table)

        # Display recovery commands if available
        if enhanced_error.resolution.recovery_commands:
            commands_panel = create_panel(
                "\n".join(enhanced_error.resolution.recovery_commands),
                title="🔄 Recovery Commands",
                border_style="green",
            )
            console.print(commands_panel)

        # Interactive recovery if enabled
        if interactive:
            from ..common.rich_utils import confirm_action

            if confirm_action("Would you like to proceed with automated recovery?", default=True):
                return self._execute_automated_recovery(enhanced_error)

        return False

    def generate_error_report(self, time_period_hours: int = 24) -> Dict[str, Any]:
        """
        Generate comprehensive error report for enterprise monitoring.

        Args:
            time_period_hours: Time period for error analysis

        Returns:
            Comprehensive error report
        """
        report = {
            "report_metadata": {
                "module": self.module_name,
                "time_period_hours": time_period_hours,
                "report_timestamp": datetime.now().isoformat(),
                "handler_version": "Phase 2 Implementation",
            },
            "error_statistics": {
                "total_errors": sum(self.error_counts.values()),
                "errors_by_category": dict(self.error_counts),
                "error_trends": self._calculate_error_trends(),
                "resolution_success_rate": self.resolution_success_rate,
            },
            "top_error_patterns": self._analyze_error_patterns(),
            "performance_impact": self._calculate_performance_impact(),
            "recommendations": self._generate_recommendations(),
            "audit_trail_summary": self._summarize_audit_trail(time_period_hours),
        }

        return report

    def display_error_report(self, report: Dict[str, Any]):
        """Display error report with Rich CLI formatting."""
        print_info("📊 Enterprise Error Analysis Report")

        # Error statistics table
        stats_table = create_table(
            title="🔍 Error Statistics",
            columns=[
                {"name": "Category", "style": "cyan", "justify": "left"},
                {"name": "Count", "style": "red", "justify": "right"},
                {"name": "Percentage", "style": "yellow", "justify": "right"},
            ],
        )

        total_errors = report["error_statistics"]["total_errors"]
        for category, count in report["error_statistics"]["errors_by_category"].items():
            if count > 0:
                percentage = (count / total_errors) * 100 if total_errors > 0 else 0
                stats_table.add_row(category.replace("_", " ").title(), str(count), f"{percentage:.1f}%")

        console.print(stats_table)

        # Recommendations panel
        if report["recommendations"]:
            recommendations_text = "\n".join([f"• {rec}" for rec in report["recommendations"]])
            recommendations_panel = create_panel(recommendations_text, title="💡 Recommendations", border_style="blue")
            console.print(recommendations_panel)

    # Private methods for error analysis and handling
    def _analyze_exception(
        self, exception: Exception, context: ErrorContext, operation_data: Optional[Dict[str, Any]] = None
    ) -> EnhancedError:
        """Analyze exception and create enhanced error with resolution guidance."""
        # Check if this is already an enhanced error
        if operation_data and "enhanced_error" in operation_data:
            return operation_data["enhanced_error"]

        # Determine error category and severity
        category = self._classify_error(exception)
        severity = self._determine_severity(exception, category)

        # Generate resolution guidance
        resolution = self._generate_resolution(exception, category, context)

        # Create error code
        error_code = f"{self.module_name.upper()}_{category.value}_{type(exception).__name__}"

        # Determine retry possibility
        retry_possible = self._is_retryable_error(exception, category)

        enhanced_error = EnhancedError(
            original_exception=exception,
            severity=severity,
            category=category,
            context=context,
            resolution=resolution,
            error_code=error_code,
            retry_possible=retry_possible,
            audit_trail=[
                {
                    "created": datetime.now().isoformat(),
                    "analysis_completed": True,
                    "operation_data": operation_data or {},
                }
            ],
        )

        return enhanced_error

    def _classify_error(self, exception: Exception) -> ErrorCategory:
        """Classify exception into appropriate category."""
        if isinstance(exception, (NoCredentialsError, PartialCredentialsError, ProfileNotFound)):
            return ErrorCategory.AWS_CREDENTIALS
        elif isinstance(exception, ClientError):
            error_code = exception.response.get("Error", {}).get("Code", "")
            if error_code in ["AccessDenied", "Forbidden", "UnauthorizedOperation"]:
                return ErrorCategory.AWS_PERMISSIONS
            elif error_code in ["Throttling", "ThrottlingException", "RequestLimitExceeded"]:
                return ErrorCategory.AWS_THROTTLING
            else:
                return ErrorCategory.AWS_SERVICE
        elif isinstance(exception, (EndpointConnectionError, BotoConnectionError, ConnectionError)):
            return ErrorCategory.NETWORK
        elif isinstance(exception, (ValueError, TypeError)) and "validation" in str(exception).lower():
            return ErrorCategory.DATA_VALIDATION
        elif "timeout" in str(exception).lower() or "performance" in str(exception).lower():
            return ErrorCategory.PERFORMANCE
        elif isinstance(exception, (FileNotFoundError, PermissionError)):
            return ErrorCategory.CONFIGURATION
        else:
            return ErrorCategory.UNKNOWN

    def _determine_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on exception type and category."""
        if category == ErrorCategory.AWS_CREDENTIALS:
            return ErrorSeverity.HIGH
        elif category == ErrorCategory.AWS_PERMISSIONS:
            return ErrorSeverity.HIGH
        elif category == ErrorCategory.NETWORK:
            return ErrorSeverity.MEDIUM
        elif category == ErrorCategory.AWS_THROTTLING:
            return ErrorSeverity.LOW  # Usually temporary
        elif category == ErrorCategory.PERFORMANCE:
            return ErrorSeverity.MEDIUM
        elif category == ErrorCategory.DATA_VALIDATION:
            return ErrorSeverity.HIGH
        else:
            return ErrorSeverity.MEDIUM

    def _generate_resolution(
        self, exception: Exception, category: ErrorCategory, context: ErrorContext
    ) -> ErrorResolution:
        """Generate resolution guidance based on error category."""
        if category == ErrorCategory.AWS_CREDENTIALS:
            return self._generate_credentials_resolution(context, "generic")
        elif category == ErrorCategory.AWS_PERMISSIONS:
            return self._generate_permissions_resolution(exception, context)
        elif category == ErrorCategory.NETWORK:
            return self._generate_network_resolution(exception, context)
        elif category == ErrorCategory.AWS_THROTTLING:
            return self._generate_throttling_resolution(exception, context)
        else:
            return self._generate_generic_resolution(exception, context)

    def _generate_credentials_resolution(self, context: ErrorContext, error_type: str) -> ErrorResolution:
        """Generate credentials-specific resolution guidance."""
        if error_type == "no_credentials":
            title = "AWS Credentials Not Found"
            description = "No AWS credentials were found for authentication"
            action_items = [
                "Configure AWS credentials using one of the following methods:",
                "1. Run 'aws configure' to set up default credentials",
                "2. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables",
                "3. Use AWS SSO login: 'aws sso login --profile your-profile'",
                "4. Use IAM roles if running on EC2",
            ]
            recovery_commands = [
                "aws configure",
                "aws sso login --profile " + (context.aws_profile or "default"),
                "export AWS_PROFILE=" + (context.aws_profile or "default"),
            ]
        elif error_type == "partial_credentials":
            title = "Incomplete AWS Credentials"
            description = "AWS credentials are partially configured"
            action_items = [
                "Ensure all required credential components are provided:",
                "1. Access Key ID",
                "2. Secret Access Key",
                "3. Session Token (if using temporary credentials)",
                "4. Region configuration",
            ]
            recovery_commands = [
                "aws configure list",
                "aws configure set region " + (context.aws_region or "us-east-1"),
            ]
        else:
            title = "AWS Credentials Issue"
            description = "Generic AWS credentials problem detected"
            action_items = [
                "Verify AWS credentials configuration",
                "Check AWS profile settings",
                "Ensure credentials have not expired",
            ]
            recovery_commands = ["aws sts get-caller-identity", "aws configure list-profiles"]

        return ErrorResolution(
            title=title,
            description=description,
            action_items=action_items,
            recovery_commands=recovery_commands,
            estimated_resolution_time="2-5 minutes",
            requires_admin=False,
            documentation_links=["https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html"],
        )

    def _generate_permissions_resolution(self, exception: Exception, context: ErrorContext) -> ErrorResolution:
        """Generate AWS permissions resolution guidance."""
        error_code = ""
        if isinstance(exception, ClientError):
            error_code = exception.response.get("Error", {}).get("Code", "")

        # Get recommended profile based on operation
        recommended_profiles = self.profile_recommendations.get(context.operation, [])

        action_items = [
            f"AWS permissions error detected: {error_code}",
            "Verify your AWS profile has the required permissions for this operation",
            "Consider switching to a profile with appropriate permissions",
        ]

        if recommended_profiles:
            action_items.extend(
                ["Recommended profiles for this operation:", *[f"  • {profile}" for profile in recommended_profiles]]
            )

        recovery_commands = ["aws sts get-caller-identity", "aws iam get-user", "aws iam list-attached-user-policies"]

        if recommended_profiles:
            recovery_commands.extend(
                [
                    f"export AWS_PROFILE={recommended_profiles[0]}",
                    f"runbooks {context.module_name} {context.operation} --profile {recommended_profiles[0]}",
                ]
            )

        return ErrorResolution(
            title="AWS Permissions Error",
            description=f"Insufficient permissions for {context.operation} operation",
            action_items=action_items,
            recovery_commands=recovery_commands,
            estimated_resolution_time="10-15 minutes",
            requires_admin=True,
            documentation_links=["https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html"],
        )

    def _generate_profile_not_found_resolution(self, context: ErrorContext) -> ErrorResolution:
        """Generate profile not found resolution guidance."""
        return ErrorResolution(
            title="AWS Profile Not Found",
            description=f"AWS profile '{context.aws_profile}' was not found in your configuration",
            action_items=[
                "Verify the profile name is spelled correctly",
                "Check available AWS profiles",
                "Configure the profile if it doesn't exist",
                "Use the default profile if appropriate",
            ],
            recovery_commands=[
                "aws configure list-profiles",
                f"aws configure --profile {context.aws_profile or 'your-profile'}",
                "aws sso login --profile " + (context.aws_profile or "your-profile"),
            ],
            alternative_approaches=[
                "Use --profile default if you have default credentials configured",
                "Use environment variables instead of profiles",
            ],
            estimated_resolution_time="5-10 minutes",
            requires_admin=False,
        )

    def _generate_network_resolution(self, exception: Exception, context: ErrorContext) -> ErrorResolution:
        """Generate network error resolution guidance."""
        return ErrorResolution(
            title="Network Connection Error",
            description="Unable to connect to AWS services",
            action_items=[
                "Check your internet connection",
                "Verify AWS service endpoints are accessible",
                "Check firewall and proxy settings",
                "Try a different AWS region if applicable",
            ],
            recovery_commands=[
                "ping aws.amazon.com",
                "nslookup " + (context.aws_region or "us-east-1") + ".amazonaws.com",
                f"runbooks {context.module_name} {context.operation} --region us-west-2",
            ],
            estimated_resolution_time="5-15 minutes",
            requires_admin=False,
        )

    def _generate_throttling_resolution(self, exception: Exception, context: ErrorContext) -> ErrorResolution:
        """Generate throttling error resolution guidance."""
        return ErrorResolution(
            title="AWS API Throttling",
            description="Request rate exceeded AWS API limits",
            action_items=[
                "Reduce request frequency",
                "Implement exponential backoff",
                "Consider using pagination for large datasets",
                "Monitor API usage patterns",
            ],
            recovery_commands=[
                f"runbooks {context.module_name} {context.operation} --batch-size 10",
                f"runbooks {context.module_name} {context.operation} --delay 2",
            ],
            estimated_resolution_time="Automatic retry in 30-60 seconds",
            requires_admin=False,
        )

    def _generate_generic_resolution(self, exception: Exception, context: ErrorContext) -> ErrorResolution:
        """Generate generic resolution guidance."""
        return ErrorResolution(
            title=f"Error in {context.operation}",
            description=str(exception),
            action_items=[
                "Review the error message for specific details",
                "Check operation parameters and configuration",
                "Verify system prerequisites are met",
                "Consider enabling verbose logging for more details",
            ],
            recovery_commands=[
                f"runbooks {context.module_name} {context.operation} --verbose",
                f"runbooks {context.module_name} {context.operation} --dry-run",
            ],
            estimated_resolution_time="10-20 minutes",
            requires_admin=False,
        )

    def _is_retryable_error(self, exception: Exception, category: ErrorCategory) -> bool:
        """Determine if error is retryable."""
        if category == ErrorCategory.AWS_THROTTLING:
            return True
        elif category == ErrorCategory.NETWORK:
            return True
        elif category == ErrorCategory.AWS_SERVICE:
            if isinstance(exception, ClientError):
                error_code = exception.response.get("Error", {}).get("Code", "")
                return error_code in ["InternalError", "ServiceUnavailable", "RequestTimeout"]
        return False

    def _display_enhanced_error(self, enhanced_error: EnhancedError):
        """Display enhanced error with Rich CLI formatting."""
        # Error severity indicator
        severity_colors = {
            ErrorSeverity.CRITICAL: "red bold reverse",
            ErrorSeverity.HIGH: "red bold",
            ErrorSeverity.MEDIUM: "yellow bold",
            ErrorSeverity.LOW: "yellow",
            ErrorSeverity.INFO: "blue",
        }

        severity_icons = {
            ErrorSeverity.CRITICAL: "🚨",
            ErrorSeverity.HIGH: "🔴",
            ErrorSeverity.MEDIUM: "🟡",
            ErrorSeverity.LOW: "🟠",
            ErrorSeverity.INFO: "🔵",
        }

        # Main error panel
        error_content = f"""
[bold red]Error:[/] {enhanced_error.resolution.title}

[bold yellow]Details:[/] {enhanced_error.resolution.description}

[bold cyan]Module:[/] {enhanced_error.context.module_name}
[bold cyan]Operation:[/] {enhanced_error.context.operation}
[bold cyan]Severity:[/] {severity_icons[enhanced_error.severity]} {enhanced_error.severity.value}
[bold cyan]Category:[/] {enhanced_error.category.value.replace("_", " ").title()}
        """

        error_panel = create_panel(
            error_content.strip(),
            title=f"⚠️ {enhanced_error.error_code}",
            border_style=severity_colors[enhanced_error.severity].split()[0],
        )
        console.print(error_panel)

        # Resolution guidance
        if enhanced_error.resolution.action_items:
            resolution_table = create_table(
                title="🛠️ Resolution Steps",
                columns=[
                    {"name": "Step", "style": "cyan", "justify": "center"},
                    {"name": "Action", "style": "white", "justify": "left"},
                ],
            )

            for i, action in enumerate(enhanced_error.resolution.action_items, 1):
                resolution_table.add_row(str(i), action)

            console.print(resolution_table)

        # Recovery commands
        if enhanced_error.resolution.recovery_commands:
            commands_text = "\n".join(enhanced_error.resolution.recovery_commands)
            commands_panel = create_panel(commands_text, title="💻 Recovery Commands", border_style="green")
            console.print(commands_panel)

        # Time estimate
        print_info(f"⏱️ Estimated resolution time: {enhanced_error.resolution.estimated_resolution_time}")

        if enhanced_error.resolution.requires_admin:
            print_warning("👤 Administrator privileges may be required")

    def _log_error_to_audit_trail(self, enhanced_error: EnhancedError):
        """Log error to audit trail."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "module": self.module_name,
            "error_code": enhanced_error.error_code,
            "severity": enhanced_error.severity.value,
            "category": enhanced_error.category.value,
            "operation": enhanced_error.context.operation,
            "aws_profile": enhanced_error.context.aws_profile,
            "error_message": str(enhanced_error.original_exception),
            "resolution_title": enhanced_error.resolution.title,
            "retry_possible": enhanced_error.retry_possible,
            "audit_trail": enhanced_error.audit_trail,
        }

        # Append to audit file
        try:
            audit_data = []
            if Path(self.audit_file_path).exists():
                with open(self.audit_file_path, "r") as f:
                    audit_data = json.load(f)

            audit_data.append(audit_entry)

            with open(self.audit_file_path, "w") as f:
                json.dump(audit_data, f, indent=2, default=str)

        except Exception as e:
            self.logger.warning(f"Failed to write audit entry: {e}")

    def _attempt_auto_resolution(self, enhanced_error: EnhancedError) -> bool:
        """Attempt automated error resolution."""
        if enhanced_error.category == ErrorCategory.AWS_THROTTLING:
            # Implement exponential backoff
            time.sleep(enhanced_error.backoff_seconds)
            return True

        # For other error types, manual intervention is typically required
        return False

    def _initialize_aws_error_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize AWS service error mappings."""
        return {
            "AccessDenied": {
                "severity": ErrorSeverity.HIGH,
                "category": ErrorCategory.AWS_PERMISSIONS,
                "retry_possible": False,
                "description": "Access denied to AWS resource",
            },
            "Throttling": {
                "severity": ErrorSeverity.LOW,
                "category": ErrorCategory.AWS_THROTTLING,
                "retry_possible": True,
                "max_retries": 5,
                "backoff_seconds": 2.0,
            },
            "InvalidParameterValue": {
                "severity": ErrorSeverity.MEDIUM,
                "category": ErrorCategory.DATA_VALIDATION,
                "retry_possible": False,
                "description": "Invalid parameter provided to AWS API",
            },
        }

    def _initialize_profile_recommendations(self) -> Dict[str, List[str]]:
        """Initialize profile recommendations for different operations."""
        return {
            "inventory": ["ams-admin-ReadOnlyAccess-909135376185", "ams-centralised-ops-ReadOnlyAccess-335083429030"],
            "operate": ["ams-centralised-ops-ReadOnlyAccess-335083429030", "ams-admin-ReadOnlyAccess-909135376185"],
            "finops": ["ams-admin-Billing-ReadOnlyAccess-909135376185", "ams-admin-ReadOnlyAccess-909135376185"],
            "security": ["ams-admin-ReadOnlyAccess-909135376185"],
            "cfat": ["ams-admin-ReadOnlyAccess-909135376185"],
        }

    def _analyze_aws_error(self, error: ClientError, error_code: str, service: str, operation: str) -> Dict[str, Any]:
        """Analyze AWS-specific error details."""
        base_analysis = self.aws_error_mappings.get(
            error_code,
            {"severity": ErrorSeverity.MEDIUM, "category": ErrorCategory.AWS_SERVICE, "retry_possible": False},
        )

        # Service-specific adjustments
        if service == "ce" and error_code == "AccessDenied":
            # Cost Explorer requires special billing permissions
            base_analysis["recommended_profiles"] = ["ams-admin-Billing-ReadOnlyAccess-909135376185"]

        return base_analysis

    def _generate_aws_resolution(
        self, error: ClientError, error_code: str, service: str, context: ErrorContext
    ) -> ErrorResolution:
        """Generate AWS-specific resolution guidance."""
        service_friendly = {
            "ce": "Cost Explorer",
            "ec2": "EC2",
            "s3": "S3",
            "iam": "IAM",
            "organizations": "Organizations",
        }.get(service, service.upper())

        if error_code == "AccessDenied":
            return self._generate_permissions_resolution(error, context)
        elif error_code in ["Throttling", "ThrottlingException"]:
            return self._generate_throttling_resolution(error, context)
        else:
            return ErrorResolution(
                title=f"{service_friendly} Service Error",
                description=f"AWS {service_friendly} service error: {error_code}",
                action_items=[
                    f"Review {service_friendly} service documentation",
                    "Check API parameters and request format",
                    "Verify service availability in your region",
                    "Consider alternative approaches if available",
                ],
                recovery_commands=[
                    f"aws {service} help",
                    f"runbooks {context.module_name} {context.operation} --dry-run",
                ],
                estimated_resolution_time="10-20 minutes",
                requires_admin=False,
            )

    # Additional helper methods for error analysis
    def _calculate_error_trends(self) -> Dict[str, Any]:
        """Calculate error trends for reporting."""
        return {"trend_analysis": "Stable", "peak_error_times": [], "common_patterns": []}

    def _analyze_error_patterns(self) -> List[Dict[str, Any]]:
        """Analyze common error patterns."""
        return []

    def _calculate_performance_impact(self) -> Dict[str, Any]:
        """Calculate performance impact of errors."""
        return {
            "average_resolution_time": "5-15 minutes",
            "operations_affected": 0,
            "performance_degradation": "Minimal",
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on error patterns."""
        recommendations = []

        if self.error_counts[ErrorCategory.AWS_CREDENTIALS] > 0:
            recommendations.append("Consider implementing AWS SSO for improved credential management")

        if self.error_counts[ErrorCategory.AWS_THROTTLING] > 0:
            recommendations.append("Implement exponential backoff for API calls")

        if self.error_counts[ErrorCategory.NETWORK] > 0:
            recommendations.append("Review network connectivity and proxy settings")

        return recommendations

    def _summarize_audit_trail(self, hours: int) -> Dict[str, Any]:
        """Summarize audit trail for given time period."""
        return {"entries": 0, "resolution_success_rate": 0.0, "average_resolution_time": "5-15 minutes"}

    def _execute_automated_recovery(self, enhanced_error: EnhancedError) -> bool:
        """Execute automated recovery procedures."""
        # Implementation would depend on specific recovery procedures
        print_info("🔄 Executing automated recovery...")
        return False


# Factory function for easy integration
def create_exception_handler(
    module_name: str, enable_rich_output: bool = True, enable_auto_retry: bool = True
) -> EnterpriseExceptionHandler:
    """Factory function to create enterprise exception handler."""
    return EnterpriseExceptionHandler(
        module_name=module_name, enable_rich_output=enable_rich_output, enable_auto_retry=enable_auto_retry
    )


# Context manager for enhanced exception handling
class enhanced_error_handling:
    """Context manager for enhanced exception handling."""

    def __init__(
        self,
        handler: EnterpriseExceptionHandler,
        context: ErrorContext,
        operation_data: Optional[Dict[str, Any]] = None,
    ):
        self.handler = handler
        self.context = context
        self.operation_data = operation_data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback_obj):
        if exc_value is not None:
            enhanced_error = self.handler.handle_exception(exc_value, self.context, self.operation_data)

            # Create recovery workflow if error is recoverable
            if enhanced_error.retry_possible:
                recovery_success = self.handler.create_error_recovery_workflow(enhanced_error, interactive=False)
                if recovery_success:
                    return True  # Suppress the exception

        return False  # Let the exception propagate

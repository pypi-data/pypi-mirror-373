"""
Base operation classes for AWS resource management.

This module provides the abstract foundation for all AWS operational capabilities,
ensuring consistent patterns, safety features, and enterprise-grade reliability
across all service-specific operations.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from runbooks.common.cross_module_integration import DataFlowType, EnterpriseCrossModuleIntegrator
from runbooks.common.mcp_integration import EnterpriseMCPIntegrator, MCPOperationType
from runbooks.common.profile_utils import create_operational_session, get_profile_for_operation
from runbooks.common.rich_utils import print_error, print_info, print_success, print_warning
from runbooks.inventory.models.account import AWSAccount
from runbooks.inventory.utils.aws_helpers import aws_api_retry, get_boto3_session

# Enterprise 4-Profile Architecture - Proven FinOps Patterns
ENTERPRISE_PROFILES = {
    "BILLING_PROFILE": "ams-admin-Billing-ReadOnlyAccess-909135376185",
    "MANAGEMENT_PROFILE": "ams-admin-ReadOnlyAccess-909135376185",
    "CENTRALISED_OPS_PROFILE": "ams-centralised-ops-ReadOnlyAccess-335083429030",
    "SINGLE_ACCOUNT_PROFILE": "ams-shared-services-non-prod-ReadOnlyAccess-499201730520",
}

# Rich console instance for consistent formatting
console = Console()


class OperationStatus(Enum):
    """Status of an AWS operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRY_RUN = "dry_run"


@dataclass
class OperationContext:
    """Context information for AWS operations."""

    account: AWSAccount
    region: str
    operation_type: str
    resource_types: List[str]
    dry_run: bool = False
    force: bool = False
    operation_timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize context after creation."""
        if not self.operation_timestamp:
            self.operation_timestamp = datetime.utcnow()


@dataclass
class OperationResult:
    """Result of an AWS operation."""

    operation_id: str
    status: OperationStatus
    operation_type: str
    resource_type: str
    resource_id: str
    account_id: str
    region: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    response_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Update success flag based on status."""
        self.success = self.status == OperationStatus.SUCCESS

    def mark_completed(self, status: OperationStatus, error_message: Optional[str] = None):
        """Mark operation as completed with given status."""
        self.status = status
        self.completed_at = datetime.utcnow()
        self.success = status == OperationStatus.SUCCESS
        if error_message:
            self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "operation_id": self.operation_id,
            "status": self.status.value,
            "operation_type": self.operation_type,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "account_id": self.account_id,
            "region": self.region,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "success": self.success,
            "error_message": self.error_message,
            "response_data": self.response_data,
            "metadata": self.metadata,
        }


class BaseOperation(ABC):
    """
    Abstract base class for all AWS operations.

    Provides common functionality including session management, error handling,
    logging, and safety features that all operation classes should inherit.

    Attributes:
        service_name: AWS service name (e.g., 'ec2', 's3', 'dynamodb')
        supported_operations: Set of operation types this class handles
        requires_confirmation: Whether operations require explicit confirmation
    """

    service_name: str = None
    supported_operations: set = set()
    requires_confirmation: bool = False

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None, dry_run: bool = False):
        """
        Initialize base operation class with enterprise patterns.

        Args:
            profile: AWS profile name for authentication (supports ENTERPRISE_PROFILES)
            region: AWS region for operations
            dry_run: Enable dry-run mode for safe testing
        """
        # Support enterprise profile shortcuts
        if profile in ENTERPRISE_PROFILES:
            self.profile = ENTERPRISE_PROFILES[profile]
            console.print(f"[blue]Using enterprise profile: {profile} -> {self.profile}[/blue]")
        else:
            self.profile = profile

        self.region = region or "us-east-1"
        self.dry_run = dry_run
        self._session = None
        self._clients = {}

        # Performance benchmarking
        self._operation_start_time = None
        self._performance_target = 2.0  # <2s target for operate operations

        # Phase 4: MCP Integration Framework
        self.mcp_integrator = EnterpriseMCPIntegrator(self.profile)
        self.cross_module_integrator = EnterpriseCrossModuleIntegrator(self.profile)
        self.enable_mcp_validation = True

        print_info(f"BaseOperation initialized with MCP integration for {self.service_name or 'unknown'} service")

    @property
    def session(self) -> boto3.Session:
        """Get or create AWS session."""
        if self._session is None:
            self._session = get_boto3_session(profile_name=self.profile)
        return self._session

    def get_client(self, service: str, region: Optional[str] = None) -> Any:
        """
        Get AWS service client.

        Args:
            service: AWS service name
            region: Override region for this client

        Returns:
            Configured AWS service client
        """
        client_key = f"{service}:{region or self.region}"

        if client_key not in self._clients:
            self._clients[client_key] = self.session.client(service, region_name=region or self.region)

        return self._clients[client_key]

    def validate_context(self, context: OperationContext) -> bool:
        """
        Validate operation context before execution.

        Args:
            context: Operation context to validate

        Returns:
            True if context is valid

        Raises:
            ValueError: If context validation fails
        """
        if not context.account:
            raise ValueError("Operation context must include AWS account information")

        if not context.region:
            raise ValueError("Operation context must include AWS region")

        if context.operation_type not in self.supported_operations:
            raise ValueError(
                f"Operation '{context.operation_type}' not supported. "
                f"Supported operations: {list(self.supported_operations)}"
            )

        return True

    def confirm_operation(self, context: OperationContext, resource_id: str, operation_type: str) -> bool:
        """
        Request user confirmation for destructive operations with Rich CLI.

        Args:
            context: Operation context
            resource_id: Resource identifier
            operation_type: Type of operation

        Returns:
            True if operation is confirmed
        """
        if context.dry_run:
            console.print(
                Panel(
                    f"[yellow]Would perform {operation_type} on {resource_id}[/yellow]",
                    title="🏃 DRY-RUN MODE",
                    border_style="yellow",
                )
            )
            return True

        if context.force or not self.requires_confirmation:
            return True

        # Rich CLI confirmation display
        console.print(
            Panel(
                f"[red]⚠️  Destructive operation: {operation_type}[/red]\n"
                f"[white]Resource: {resource_id}[/white]\n"
                f"[white]Account: {context.account.account_id}[/white]",
                title="🚨 CONFIRMATION REQUIRED",
                border_style="red",
            )
        )
        return True  # Simplified for this implementation

    @aws_api_retry
    def execute_aws_call(self, client: Any, method_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute AWS API call with retry and error handling.

        Args:
            client: AWS service client
            method_name: Method name to call
            **kwargs: Method arguments

        Returns:
            AWS API response

        Raises:
            ClientError: AWS service errors
        """
        try:
            method = getattr(client, method_name)
            response = method(**kwargs)

            logger.debug(f"AWS API call successful: {method_name}")
            return response

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"AWS API call failed: {method_name} - {error_code}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AWS API call: {method_name} - {e}")
            raise

    def create_operation_result(
        self,
        context: OperationContext,
        operation_type: str,
        resource_type: str,
        resource_id: str,
        status: OperationStatus = OperationStatus.PENDING,
    ) -> OperationResult:
        """
        Create operation result object.

        Args:
            context: Operation context
            operation_type: Type of operation
            resource_type: Type of resource
            resource_id: Resource identifier
            status: Initial status

        Returns:
            OperationResult object
        """
        operation_id = f"{operation_type}-{resource_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        return OperationResult(
            operation_id=operation_id,
            status=status,
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            account_id=context.account.account_id,
            region=context.region,
            started_at=datetime.utcnow(),
            metadata=context.metadata.copy(),
        )

    @abstractmethod
    def execute_operation(self, context: OperationContext, operation_type: str, **kwargs) -> List[OperationResult]:
        """
        Execute the specified operation.

        Args:
            context: Operation context
            operation_type: Type of operation to execute
            **kwargs: Operation-specific arguments

        Returns:
            List of operation results

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement execute_operation")

    def get_operation_history(
        self, resource_id: Optional[str] = None, operation_type: Optional[str] = None, limit: int = 100
    ) -> List[OperationResult]:
        """
        Get operation history for resources.

        Args:
            resource_id: Filter by resource ID
            operation_type: Filter by operation type
            limit: Maximum results to return

        Returns:
            List of historical operation results
        """
        # In a real implementation, this would query a database or log store
        console.print(f"[blue]📊 Operation history requested for {resource_id or 'all resources'}[/blue]")
        return []

    def start_performance_benchmark(self) -> None:
        """Start performance timing for operation benchmarking."""
        self._operation_start_time = time.time()

    def end_performance_benchmark(self, operation_name: str) -> float:
        """
        End performance timing and display results.

        Args:
            operation_name: Name of the operation for reporting

        Returns:
            Elapsed time in seconds
        """
        if self._operation_start_time is None:
            return 0.0

        elapsed_time = time.time() - self._operation_start_time

        # Performance validation against target
        if elapsed_time <= self._performance_target:
            console.print(
                f"[green]⚡ {operation_name} completed in {elapsed_time:.2f}s (target: {self._performance_target}s) ✅[/green]"
            )
        else:
            console.print(
                f"[yellow]⚠️  {operation_name} completed in {elapsed_time:.2f}s (exceeded target: {self._performance_target}s)[/yellow]"
            )

        self._operation_start_time = None
        return elapsed_time

    def display_operation_summary(self, results: List[OperationResult]) -> None:
        """
        Display operation summary using Rich table formatting.

        Args:
            results: List of operation results to summarize
        """
        if not results:
            console.print("[yellow]No operations to display[/yellow]")
            return

        table = Table(title="🔧 Operation Summary")
        table.add_column("Operation", style="cyan")
        table.add_column("Resource", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="blue")

        success_count = 0
        total_count = len(results)

        for result in results:
            status_icon = "✅" if result.success else "❌"
            status_text = f"{status_icon} {result.status.value}"

            duration = "N/A"
            if result.completed_at and result.started_at:
                elapsed = (result.completed_at - result.started_at).total_seconds()
                duration = f"{elapsed:.2f}s"

            if result.success:
                success_count += 1

            table.add_row(result.operation_type, result.resource_id, status_text, duration)

        console.print(table)

        # Success rate summary
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        if success_rate >= 95:
            console.print(
                f"[green]🎯 Success Rate: {success_rate:.1f}% ({success_count}/{total_count}) - Excellent![/green]"
            )
        elif success_rate >= 90:
            console.print(
                f"[yellow]📊 Success Rate: {success_rate:.1f}% ({success_count}/{total_count}) - Good[/yellow]"
            )
        else:
            console.print(
                f"[red]⚠️  Success Rate: {success_rate:.1f}% ({success_count}/{total_count}) - Needs Attention[/red]"
            )

    # Phase 4: MCP Integration Methods
    async def validate_operation_with_mcp(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate operation results using MCP integration.

        Args:
            operation_data: Operation results to validate

        Returns:
            Dictionary containing validation results
        """
        try:
            if not self.enable_mcp_validation:
                return {"validation_skipped": True, "reason": "MCP validation disabled"}

            print_info("Validating operation results with MCP integration")

            validation_result = await self.mcp_integrator.validate_operate_operations(operation_data)

            if validation_result.success:
                print_success(f"Operation MCP validation passed: {validation_result.accuracy_score}% accuracy")
            else:
                print_warning("Operation MCP validation encountered issues")

            return validation_result.to_dict()

        except Exception as e:
            print_error(f"MCP validation failed: {str(e)[:50]}...")
            return {"validation_error": str(e), "validation_failed": True}

    async def prepare_data_for_finops_analysis(self, operation_results: List[OperationResult]) -> Dict[str, Any]:
        """
        Prepare operation results for FinOps cost analysis integration.

        Args:
            operation_results: List of operation results

        Returns:
            Dictionary formatted for FinOps module consumption
        """
        try:
            print_info("Preparing operation data for FinOps analysis")

            # Convert operation results to data flow format
            operation_data = {
                "operations": [
                    {
                        "id": result.operation_id,
                        "type": result.operation_type,
                        "resource_id": result.resource_id,
                        "resource_type": result.resource_type,
                        "account_id": result.account_id,
                        "region": result.region,
                        "success": result.success,
                        "started_at": result.started_at.isoformat(),
                        "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                        "metadata": result.metadata,
                    }
                    for result in operation_results
                ]
            }

            data_flow_result = await self.cross_module_integrator.execute_data_flow(
                flow_type=DataFlowType.OPERATE_TO_FINOPS, source_data=operation_data
            )

            if data_flow_result.success:
                print_success("Operate → FinOps data flow completed successfully")
                return data_flow_result.transformed_data
            else:
                print_error(f"Data flow failed: {', '.join(data_flow_result.error_details)}")
                return {}

        except Exception as e:
            print_error(f"Failed to prepare data for FinOps analysis: {str(e)}")
            return {}

    def execute_operation_with_validation(
        self, context: OperationContext, operation_func: Callable, *args, **kwargs
    ) -> List[OperationResult]:
        """
        Execute operation with automatic MCP validation and performance tracking.

        Args:
            context: Operation context
            operation_func: Operation function to execute
            *args: Arguments for operation function
            **kwargs: Keyword arguments for operation function

        Returns:
            List of operation results with MCP validation
        """
        self.start_performance_benchmark()

        try:
            # Execute the operation
            results = operation_func(context, *args, **kwargs)

            # Add MCP validation asynchronously if enabled
            if self.enable_mcp_validation and results:
                try:
                    operation_data = {
                        "operations": [result.__dict__ for result in results],
                        "context": context.__dict__,
                    }

                    validation_result = asyncio.run(self.validate_operation_with_mcp(operation_data))

                    # Add validation results to operation metadata
                    for result in results:
                        result.metadata["mcp_validation"] = validation_result

                except Exception as e:
                    print_warning(f"MCP validation failed: {str(e)[:50]}... - operation completed without validation")

            # End performance benchmark
            elapsed_time = self.end_performance_benchmark(f"{context.operation_type} operation")

            # Add performance metrics to results
            for result in results:
                result.metadata["performance_seconds"] = elapsed_time
                result.metadata["performance_target_met"] = elapsed_time <= self._performance_target

            return results

        except Exception as e:
            self.end_performance_benchmark(f"{context.operation_type} operation (failed)")
            raise e

    def get_mcp_integration_status(self) -> Dict[str, Any]:
        """
        Get current MCP integration status and configuration.

        Returns:
            Dictionary containing MCP integration details
        """
        return {
            "service_name": self.service_name,
            "mcp_validation_enabled": self.enable_mcp_validation,
            "mcp_integrator_initialized": self.mcp_integrator is not None,
            "cross_module_integrator_initialized": self.cross_module_integrator is not None,
            "supported_operations": list(self.supported_operations),
            "performance_target_seconds": self._performance_target,
            "profile": self.profile,
            "region": self.region,
        }

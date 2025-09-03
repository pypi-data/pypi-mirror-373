"""
Base CloudOps Class with Enterprise Patterns

Provides common functionality for all CloudOps automation classes including:
- Rich CLI integration with enterprise UX standards
- Performance monitoring and benchmarking
- AWS profile management with multi-account support
- Error handling and logging
- Business metrics collection

Strategic Alignment:
- Integrates with existing runbooks architecture
- Follows Rich CLI standards from rich_utils.py
- Supports multi-profile enterprise configurations
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from dataclasses import dataclass
from datetime import datetime

from runbooks.common.rich_utils import (
    console, print_header, print_success, print_error, print_warning, print_info,
    create_table, create_progress_bar, format_cost, create_panel, STATUS_INDICATORS
)
from .models import (
    BusinessScenario, ExecutionMode, RiskLevel, 
    ProfileConfiguration, CloudOpsExecutionResult, BusinessMetrics, ResourceImpact
)

@dataclass
class PerformanceBenchmark:
    """Performance benchmarking for enterprise operations."""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """Calculate operation duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

class CloudOpsBase:
    """
    Base class for all CloudOps automation scenarios.
    
    Provides enterprise-grade functionality including:
    - Rich CLI integration with consistent UX
    - Performance monitoring and benchmarking
    - Multi-account AWS profile management
    - Error handling with business-focused messaging
    - Audit trail and logging
    """
    
    def __init__(
        self, 
        profile: str = "default", 
        dry_run: bool = True,
        execution_mode: ExecutionMode = ExecutionMode.DRY_RUN
    ):
        """
        Initialize CloudOps base class.
        
        Args:
            profile: AWS profile name for operations
            dry_run: Enable dry-run mode (safe analysis only)
            execution_mode: Execution mode (dry_run/execute/validate_only)
        """
        self.profile = profile
        self.dry_run = dry_run
        self.execution_mode = execution_mode
        
        # Performance monitoring
        self.benchmarks: List[PerformanceBenchmark] = []
        self.session_start_time = time.time()
        
        # AWS session management
        self.session: Optional[boto3.Session] = None
        self.available_regions: List[str] = []
        
        # Business metrics collection
        self.resources_analyzed = 0
        self.resources_impacted: List[ResourceImpact] = []
        
        # Initialize AWS session
        self._initialize_aws_session()
        
    def _initialize_aws_session(self) -> None:
        """Initialize AWS session with profile validation."""
        try:
            self.session = boto3.Session(profile_name=self.profile)
            
            # Validate session by getting caller identity
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            
            self.account_id = identity.get('Account', 'unknown')
            self.user_arn = identity.get('Arn', 'unknown')
            
            print_success(f"AWS session initialized for profile: {self.profile}")
            print_info(f"Account ID: {self.account_id}")
            
        except ProfileNotFound:
            error_msg = f"AWS profile '{self.profile}' not found in local configuration"
            print_error(error_msg)
            raise ValueError(error_msg)
            
        except NoCredentialsError:
            error_msg = f"No valid credentials found for profile '{self.profile}'"
            print_error(error_msg)
            raise ValueError(error_msg)
            
        except ClientError as e:
            error_msg = f"AWS authentication failed for profile '{self.profile}': {str(e)}"
            print_error(error_msg)
            raise ValueError(error_msg)
    
    def _get_available_regions(self, service_name: str = 'ec2') -> List[str]:
        """Get available AWS regions for a service."""
        if not self.available_regions:
            try:
                client = self.session.client(service_name, region_name='us-east-1')
                response = client.describe_regions()
                self.available_regions = [region['RegionName'] for region in response['Regions']]
            except Exception as e:
                print_warning(f"Could not fetch available regions: {str(e)}")
                # Fallback to common regions
                self.available_regions = [
                    'us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'
                ]
        return self.available_regions
    
    def start_benchmark(self, operation_name: str) -> PerformanceBenchmark:
        """Start performance benchmarking for an operation."""
        benchmark = PerformanceBenchmark(
            operation_name=operation_name,
            start_time=time.time()
        )
        self.benchmarks.append(benchmark)
        return benchmark
    
    def complete_benchmark(
        self, 
        benchmark: PerformanceBenchmark, 
        success: bool = True, 
        error_message: Optional[str] = None
    ) -> None:
        """Complete performance benchmarking."""
        benchmark.end_time = time.time()
        benchmark.success = success
        benchmark.error_message = error_message
        
        duration = benchmark.duration
        
        # Rich CLI performance feedback
        if success:
            if duration < 30:  # < 30s target for single account
                print_success(f"✅ {benchmark.operation_name} completed ({duration:.1f}s)")
            elif duration < 120:  # < 120s target for multi-account
                print_warning(f"⚠️  {benchmark.operation_name} completed ({duration:.1f}s) - approaching time limit")
            else:
                print_error(f"⏰ {benchmark.operation_name} completed ({duration:.1f}s) - exceeds performance target")
        else:
            print_error(f"❌ {benchmark.operation_name} failed ({duration:.1f}s): {error_message}")
    
    async def execute_with_monitoring(
        self, 
        operation_name: str, 
        operation_func,
        *args, 
        **kwargs
    ) -> Any:
        """
        Execute an operation with comprehensive monitoring.
        
        Args:
            operation_name: Human-readable operation name
            operation_func: Async function to execute
            *args, **kwargs: Arguments to pass to operation_func
            
        Returns:
            Result of operation_func execution
        """
        benchmark = self.start_benchmark(operation_name)
        
        try:
            with console.status(f"[cyan]Executing {operation_name}..."):
                if asyncio.iscoroutinefunction(operation_func):
                    result = await operation_func(*args, **kwargs)
                else:
                    result = operation_func(*args, **kwargs)
                
                self.complete_benchmark(benchmark, success=True)
                return result
                
        except Exception as e:
            error_message = str(e)
            self.complete_benchmark(benchmark, success=False, error_message=error_message)
            
            # Rich CLI error display
            print_error(f"Operation failed: {operation_name}")
            print_error(f"Error details: {error_message}")
            
            raise
    
    def create_resource_impact(
        self,
        resource_type: str,
        resource_id: str,
        region: str,
        estimated_cost: Optional[float] = None,
        projected_savings: Optional[float] = None,
        risk_level: RiskLevel = RiskLevel.LOW,
        modification_required: bool = False,
        **kwargs
    ) -> ResourceImpact:
        """
        Create a standardized ResourceImpact object.
        
        Args:
            resource_type: AWS resource type (e.g., 'nat-gateway', 'ec2-instance')
            resource_id: Unique resource identifier
            region: AWS region
            estimated_cost: Current monthly cost estimate
            projected_savings: Projected monthly savings
            risk_level: Risk level for modification
            modification_required: Whether resource needs modification
            **kwargs: Additional ResourceImpact fields
            
        Returns:
            ResourceImpact object with standardized business metrics
        """
        impact = ResourceImpact(
            resource_type=resource_type,
            resource_id=resource_id,
            region=region,
            account_id=self.account_id,
            estimated_monthly_cost=estimated_cost,
            projected_savings=projected_savings,
            risk_level=risk_level,
            modification_required=modification_required,
            **kwargs
        )
        
        self.resources_impacted.append(impact)
        self.resources_analyzed += 1
        
        return impact
    
    def display_execution_summary(self, result: CloudOpsExecutionResult) -> None:
        """
        Display Rich CLI execution summary for business stakeholders.
        
        Args:
            result: CloudOpsExecutionResult with business metrics
        """
        # Executive Summary Panel
        summary_content = (
            f"📊 Resources Analyzed: {result.resources_analyzed:,}\n"
            f"🎯 Resources Impacted: {len(result.resources_impacted):,}\n"
            f"💰 Monthly Savings: {format_cost(result.business_metrics.total_monthly_savings)}\n"
            f"⏱️  Execution Time: {result.execution_time:.1f}s\n"
            f"🛡️  Risk Level: {result.business_metrics.overall_risk_level.value.title()}"
        )
        
        if result.business_metrics.roi_percentage:
            summary_content += f"\n📈 ROI: {result.business_metrics.roi_percentage:.1f}%"
        
        summary_panel = create_panel(
            summary_content,
            title="Executive Business Impact Summary",
            border_style="green" if result.success else "red"
        )
        console.print(summary_panel)
        
        # Performance Benchmarks Table
        if self.benchmarks:
            perf_table = create_table(
                title="Performance Benchmarks",
                columns=[
                    {"name": "Operation", "style": "cyan"},
                    {"name": "Duration", "style": "yellow"},
                    {"name": "Status", "style": "green"}
                ]
            )
            
            for benchmark in self.benchmarks:
                status_icon = "✅" if benchmark.success else "❌"
                duration_str = f"{benchmark.duration:.1f}s"
                
                # Color code performance
                if benchmark.duration < 30:
                    duration_style = "green"
                elif benchmark.duration < 120:
                    duration_style = "yellow"
                else:
                    duration_style = "red"
                
                perf_table.add_row(
                    benchmark.operation_name,
                    f"[{duration_style}]{duration_str}[/{duration_style}]",
                    status_icon
                )
            
            console.print(perf_table)
        
        # Recommendations Display
        if result.recommendations:
            recommendations_text = "\n".join([f"• {rec}" for rec in result.recommendations])
            rec_panel = create_panel(
                recommendations_text,
                title="Strategic Recommendations",
                border_style="blue"
            )
            console.print(rec_panel)
    
    def create_business_metrics(
        self,
        total_savings: float = 0.0,
        implementation_cost: Optional[float] = None,
        overall_risk: RiskLevel = RiskLevel.LOW
    ) -> BusinessMetrics:
        """
        Create standardized business metrics for executive reporting.
        
        Args:
            total_savings: Total projected monthly savings
            implementation_cost: One-time implementation cost
            overall_risk: Overall risk level for the operation
            
        Returns:
            BusinessMetrics object with calculated ROI and business impact
        """
        # Calculate ROI if implementation cost is provided
        roi_percentage = None
        payback_period = None
        
        if implementation_cost and implementation_cost > 0 and total_savings > 0:
            annual_savings = total_savings * 12
            roi_percentage = (annual_savings / implementation_cost - 1) * 100
            payback_period = int(implementation_cost / total_savings)
        
        return BusinessMetrics(
            total_monthly_savings=total_savings,
            implementation_cost=implementation_cost,
            roi_percentage=roi_percentage,
            payback_period_months=payback_period,
            overall_risk_level=overall_risk,
            operational_efficiency_gain=80.0 if total_savings > 1000 else 50.0,  # Estimate based on savings
            manual_effort_reduction=90.0,  # High automation benefit
            business_continuity_impact="minimal"
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary for audit trail."""
        total_duration = time.time() - self.session_start_time
        successful_ops = sum(1 for b in self.benchmarks if b.success)
        failed_ops = len(self.benchmarks) - successful_ops
        
        return {
            "profile_used": self.profile,
            "account_id": getattr(self, 'account_id', 'unknown'),
            "execution_mode": self.execution_mode.value,
            "total_session_duration": total_duration,
            "resources_analyzed": self.resources_analyzed,
            "resources_impacted": len(self.resources_impacted),
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "performance_benchmarks": [
                {
                    "operation": b.operation_name,
                    "duration": b.duration,
                    "success": b.success,
                    "error": b.error_message
                }
                for b in self.benchmarks
            ]
        }
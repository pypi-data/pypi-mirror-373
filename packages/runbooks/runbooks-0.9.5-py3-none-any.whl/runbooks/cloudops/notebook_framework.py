#!/usr/bin/env python3
"""
CloudOps Notebook Framework - Enterprise Consolidation Infrastructure

Provides reusable components for consolidating 64 individual notebooks into 
12-15 production scenarios with enterprise-grade functionality.

Strategic Alignment:
- Follows Rich CLI standards from rich_utils.py  
- Handles authentication failures gracefully (no hardcoding/assumptions)
- Dual-purpose interface: executive summary + technical details
- Type-safe validation with Pydantic v2

Key Features:
- Authentication flow management with comprehensive error handling
- Executive and technical reporting modes  
- Multi-scenario consolidation support
- MCP integration readiness
- Performance monitoring and benchmarking
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import boto3
import pandas as pd
from botocore.exceptions import (
    ClientError, NoCredentialsError, ProfileNotFound, 
    TokenRetrievalError, UnauthorizedSSOTokenError
)
from pydantic import BaseModel, Field, ValidationError

from runbooks.common.rich_utils import (
    console, print_header, print_success, print_error, print_warning, print_info,
    create_table, create_progress_bar, format_cost, create_panel, STATUS_INDICATORS,
    print_json, create_columns, confirm_action
)
from runbooks.common.profile_utils import (
    get_profile_for_operation, create_cost_session, create_management_session,
    create_operational_session
)
from .models import (
    BusinessScenario, ExecutionMode, RiskLevel, ProfileConfiguration,
    CloudOpsExecutionResult, BusinessMetrics, ResourceImpact, CostOptimizationResult
)
from .base import CloudOpsBase, PerformanceBenchmark


class NotebookMode(str, Enum):
    """Execution modes for notebook interface."""
    EXECUTIVE = "executive"  # Executive summary for business stakeholders
    TECHNICAL = "technical"  # Technical details for engineering teams  
    COMPREHENSIVE = "comprehensive"  # Both executive and technical views


class AuthenticationStatus(str, Enum):
    """AWS authentication status tracking."""
    SUCCESS = "success"
    EXPIRED_TOKEN = "expired_token"
    INVALID_PROFILE = "invalid_profile"
    NO_CREDENTIALS = "no_credentials"
    PERMISSION_DENIED = "permission_denied"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class AuthenticationResult:
    """Results of AWS authentication validation."""
    status: AuthenticationStatus
    profile_name: str
    account_id: Optional[str] = None
    error_message: Optional[str] = None
    remediation_steps: List[str] = None
    
    def __post_init__(self):
        if self.remediation_steps is None:
            self.remediation_steps = []


class ScenarioMetadata(BaseModel):
    """Metadata for consolidated notebook scenarios."""
    scenario_id: str = Field(description="Unique scenario identifier")
    scenario_name: str = Field(description="Human-readable scenario name")
    scenario_type: BusinessScenario = Field(description="Business scenario category")
    consolidated_notebooks: List[str] = Field(description="List of individual notebooks consolidated")
    
    # Executive Information
    business_objective: str = Field(description="High-level business objective")
    expected_outcomes: List[str] = Field(description="Expected business outcomes")
    stakeholders: List[str] = Field(description="Key stakeholders", default=[])
    
    # Technical Information  
    aws_services: List[str] = Field(description="AWS services utilized")
    estimated_execution_time: int = Field(description="Estimated execution time in minutes")
    prerequisites: List[str] = Field(description="Technical prerequisites", default=[])


class NotebookFramework(CloudOpsBase):
    """
    Enterprise notebook framework for consolidated CloudOps scenarios.
    
    Provides comprehensive infrastructure for transforming individual notebooks
    into enterprise-grade consolidated scenarios with dual executive/technical interfaces.
    """
    
    def __init__(
        self, 
        profile: str = "default",
        mode: NotebookMode = NotebookMode.COMPREHENSIVE,
        dry_run: bool = True,
        validate_auth: bool = True
    ):
        """
        Initialize notebook framework.
        
        Args:
            profile: AWS profile for authentication
            mode: Notebook execution mode (executive/technical/comprehensive)
            dry_run: Enable dry-run mode for safe analysis
            validate_auth: Validate authentication before proceeding
        """
        self.mode = mode
        self.validate_auth = validate_auth
        self.auth_status: Optional[AuthenticationResult] = None
        
        # Initialize base class (handles AWS session setup)
        # Note: This may raise exceptions for authentication issues
        try:
            super().__init__(profile=profile, dry_run=dry_run)
            if self.validate_auth:
                self.auth_status = self._validate_authentication()
        except Exception as e:
            # Handle authentication failures gracefully
            self.auth_status = AuthenticationResult(
                status=AuthenticationStatus.UNKNOWN_ERROR,
                profile_name=profile,
                error_message=str(e),
                remediation_steps=self._get_generic_remediation_steps()
            )
            self.session = None  # Ensure session is None on failure
    
    def _validate_authentication(self) -> AuthenticationResult:
        """
        Comprehensive AWS authentication validation with detailed error handling.
        
        Returns:
            AuthenticationResult with status and remediation guidance
        """
        try:
            if not self.session:
                return AuthenticationResult(
                    status=AuthenticationStatus.NO_CREDENTIALS,
                    profile_name=self.profile,
                    error_message="No AWS session available",
                    remediation_steps=self._get_generic_remediation_steps()
                )
            
            # Test authentication by calling STS
            sts_client = self.session.client('sts')
            identity = sts_client.get_caller_identity()
            
            account_id = identity.get('Account')
            user_arn = identity.get('Arn')
            
            print_success(f"Authentication successful for profile: {self.profile}")
            print_info(f"Account: {account_id}, Identity: {user_arn}")
            
            return AuthenticationResult(
                status=AuthenticationStatus.SUCCESS,
                profile_name=self.profile,
                account_id=account_id
            )
            
        except UnauthorizedSSOTokenError:
            return AuthenticationResult(
                status=AuthenticationStatus.EXPIRED_TOKEN,
                profile_name=self.profile,
                error_message="AWS SSO token has expired",
                remediation_steps=[
                    "Run: aws sso login",
                    "Ensure your AWS SSO session is active",
                    f"Verify profile '{self.profile}' is configured for SSO"
                ]
            )
            
        except TokenRetrievalError as e:
            return AuthenticationResult(
                status=AuthenticationStatus.EXPIRED_TOKEN,
                profile_name=self.profile,
                error_message=f"Token retrieval failed: {str(e)}",
                remediation_steps=[
                    "Run: aws sso login",
                    "Check your internet connection",
                    "Verify AWS SSO configuration"
                ]
            )
            
        except ProfileNotFound:
            return AuthenticationResult(
                status=AuthenticationStatus.INVALID_PROFILE,
                profile_name=self.profile,
                error_message=f"AWS profile '{self.profile}' not found",
                remediation_steps=[
                    f"Check if profile '{self.profile}' exists in ~/.aws/config",
                    "Run: aws configure list-profiles",
                    "Configure the profile using: aws configure sso"
                ]
            )
            
        except NoCredentialsError:
            return AuthenticationResult(
                status=AuthenticationStatus.NO_CREDENTIALS,
                profile_name=self.profile,
                error_message="No valid AWS credentials found",
                remediation_steps=[
                    "Configure AWS credentials using: aws configure",
                    "Or set up SSO using: aws configure sso",
                    "Verify AWS credentials are properly configured"
                ]
            )
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code in ['AccessDenied', 'UnauthorizedOperation']:
                return AuthenticationResult(
                    status=AuthenticationStatus.PERMISSION_DENIED,
                    profile_name=self.profile,
                    error_message=f"Permission denied: {str(e)}",
                    remediation_steps=[
                        "Verify your AWS profile has sufficient permissions",
                        "Contact your AWS administrator for access",
                        "Check IAM policies attached to your role/user"
                    ]
                )
            else:
                return AuthenticationResult(
                    status=AuthenticationStatus.UNKNOWN_ERROR,
                    profile_name=self.profile,
                    error_message=f"AWS API error: {str(e)}",
                    remediation_steps=self._get_generic_remediation_steps()
                )
                
        except Exception as e:
            return AuthenticationResult(
                status=AuthenticationStatus.UNKNOWN_ERROR,
                profile_name=self.profile,
                error_message=f"Unexpected error: {str(e)}",
                remediation_steps=self._get_generic_remediation_steps()
            )
    
    def _get_generic_remediation_steps(self) -> List[str]:
        """Get generic remediation steps for authentication issues."""
        return [
            "Check AWS profile configuration: aws configure list-profiles",
            "Verify credentials: aws sts get-caller-identity",
            "For SSO profiles, login again: aws sso login", 
            "Contact your AWS administrator if issues persist"
        ]
    
    def display_authentication_status(self) -> None:
        """Display authentication status with Rich CLI formatting."""
        if not self.auth_status:
            print_warning("Authentication status not available")
            return
        
        status_colors = {
            AuthenticationStatus.SUCCESS: "green",
            AuthenticationStatus.EXPIRED_TOKEN: "yellow",
            AuthenticationStatus.INVALID_PROFILE: "red",
            AuthenticationStatus.NO_CREDENTIALS: "red", 
            AuthenticationStatus.PERMISSION_DENIED: "red",
            AuthenticationStatus.UNKNOWN_ERROR: "red"
        }
        
        status_icons = {
            AuthenticationStatus.SUCCESS: "✅",
            AuthenticationStatus.EXPIRED_TOKEN: "⚠️",
            AuthenticationStatus.INVALID_PROFILE: "❌",
            AuthenticationStatus.NO_CREDENTIALS: "❌",
            AuthenticationStatus.PERMISSION_DENIED: "🔒",
            AuthenticationStatus.UNKNOWN_ERROR: "❓"
        }
        
        status_color = status_colors.get(self.auth_status.status, "white")
        status_icon = status_icons.get(self.auth_status.status, "?")
        
        # Authentication Status Panel
        status_content = (
            f"Profile: {self.auth_status.profile_name}\n"
            f"Status: {status_icon} {self.auth_status.status.value.replace('_', ' ').title()}"
        )
        
        if self.auth_status.account_id:
            status_content += f"\nAccount ID: {self.auth_status.account_id}"
            
        if self.auth_status.error_message:
            status_content += f"\nError: {self.auth_status.error_message}"
        
        auth_panel = create_panel(
            status_content,
            title="AWS Authentication Status",
            border_style=status_color
        )
        console.print(auth_panel)
        
        # Remediation Steps (if authentication failed)
        if (self.auth_status.status != AuthenticationStatus.SUCCESS and 
            self.auth_status.remediation_steps):
            
            remediation_text = "\n".join([f"• {step}" for step in self.auth_status.remediation_steps])
            remediation_panel = create_panel(
                remediation_text,
                title="Remediation Steps",
                border_style="blue"
            )
            console.print(remediation_panel)
    
    def is_authenticated(self) -> bool:
        """Check if AWS authentication is successful."""
        return (self.auth_status and 
                self.auth_status.status == AuthenticationStatus.SUCCESS and
                self.session is not None)
    
    def create_scenario_header(
        self, 
        metadata: ScenarioMetadata,
        show_consolidated_info: bool = True
    ) -> None:
        """
        Create rich scenario header for consolidated notebooks.
        
        Args:
            metadata: Scenario metadata with business and technical information
            show_consolidated_info: Show information about consolidated notebooks
        """
        # Main scenario header
        print_header(f"CloudOps Scenario: {metadata.scenario_name}", "v0.9.1")
        
        # Executive Summary (always shown)
        if self.mode in [NotebookMode.EXECUTIVE, NotebookMode.COMPREHENSIVE]:
            exec_content = (
                f"🎯 Business Objective: {metadata.business_objective}\n"
                f"📊 Scenario Type: {metadata.scenario_type.value.replace('_', ' ').title()}\n"
                f"⏱️  Estimated Time: {metadata.estimated_execution_time} minutes\n"
                f"🛡️  Execution Mode: {'🔍 Analysis Only' if self.dry_run else '⚡ Live Execution'}"
            )
            
            if metadata.expected_outcomes:
                exec_content += f"\n\n📈 Expected Outcomes:\n"
                exec_content += "\n".join([f"• {outcome}" for outcome in metadata.expected_outcomes])
            
            exec_panel = create_panel(
                exec_content,
                title="Executive Summary",
                border_style="cyan"
            )
            console.print(exec_panel)
        
        # Technical Details (technical/comprehensive modes)
        if self.mode in [NotebookMode.TECHNICAL, NotebookMode.COMPREHENSIVE]:
            tech_content = (
                f"🔧 AWS Services: {', '.join(metadata.aws_services)}\n"
                f"📝 Scenario ID: {metadata.scenario_id}"
            )
            
            if metadata.prerequisites:
                tech_content += f"\n\n✅ Prerequisites:\n"
                tech_content += "\n".join([f"• {prereq}" for prereq in metadata.prerequisites])
            
            if show_consolidated_info and metadata.consolidated_notebooks:
                tech_content += f"\n\n📚 Consolidated Notebooks ({len(metadata.consolidated_notebooks)}):\n"
                tech_content += "\n".join([f"• {nb}" for nb in metadata.consolidated_notebooks])
            
            tech_panel = create_panel(
                tech_content,
                title="Technical Information",
                border_style="blue"
            )
            console.print(tech_panel)
    
    def create_results_summary(
        self, 
        result: CloudOpsExecutionResult,
        show_detailed_metrics: bool = None
    ) -> None:
        """
        Create comprehensive results summary with mode-appropriate detail level.
        
        Args:
            result: CloudOps execution result
            show_detailed_metrics: Override detail level (None = use mode default)
        """
        if show_detailed_metrics is None:
            show_detailed_metrics = self.mode in [NotebookMode.TECHNICAL, NotebookMode.COMPREHENSIVE]
        
        # Executive Summary (always shown)
        exec_summary = (
            f"📊 Scenario: {result.scenario_name}\n"
            f"✅ Success: {'Yes' if result.success else 'No'}\n"
            f"🔍 Resources Analyzed: {result.resources_analyzed:,}\n"
            f"🎯 Resources Impacted: {len(result.resources_impacted):,}\n"
            f"💰 Monthly Savings: {format_cost(result.business_metrics.total_monthly_savings)}\n"
            f"⏱️  Execution Time: {result.execution_time:.1f}s"
        )
        
        if result.business_metrics.roi_percentage:
            exec_summary += f"\n📈 ROI: {result.business_metrics.roi_percentage:.1f}%"
        
        if not result.success and result.error_message:
            exec_summary += f"\n❌ Error: {result.error_message}"
        
        exec_panel = create_panel(
            exec_summary,
            title="Execution Results Summary", 
            border_style="green" if result.success else "red"
        )
        console.print(exec_panel)
        
        # Detailed Metrics (technical/comprehensive modes)
        if show_detailed_metrics and result.business_metrics:
            metrics_table = create_table(
                title="Business Impact Metrics",
                columns=[
                    {"name": "Metric", "style": "cyan"},
                    {"name": "Value", "style": "green"},
                    {"name": "Impact", "style": "yellow"}
                ]
            )
            
            # Financial Metrics
            metrics_table.add_row(
                "Monthly Savings",
                f"${result.business_metrics.total_monthly_savings:,.2f}",
                "Cost Reduction"
            )
            
            if result.business_metrics.roi_percentage:
                metrics_table.add_row(
                    "ROI Percentage", 
                    f"{result.business_metrics.roi_percentage:.1f}%",
                    "Investment Return"
                )
            
            if result.business_metrics.payback_period_months:
                metrics_table.add_row(
                    "Payback Period",
                    f"{result.business_metrics.payback_period_months} months",
                    "Investment Recovery"
                )
            
            # Operational Metrics
            if result.business_metrics.operational_efficiency_gain:
                metrics_table.add_row(
                    "Efficiency Gain",
                    f"{result.business_metrics.operational_efficiency_gain:.1f}%",
                    "Operational Improvement"
                )
            
            metrics_table.add_row(
                "Risk Level",
                result.business_metrics.overall_risk_level.value.title(),
                "Risk Assessment"
            )
            
            console.print(metrics_table)
        
        # Recommendations (always shown if present)
        if result.recommendations:
            rec_text = "\n".join([f"• {rec}" for rec in result.recommendations])
            rec_panel = create_panel(
                rec_text,
                title="Strategic Recommendations",
                border_style="blue"
            )
            console.print(rec_panel)
    
    async def execute_with_auth_handling(
        self,
        operation_name: str,
        operation_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation with comprehensive authentication error handling.
        
        Args:
            operation_name: Human-readable operation name
            operation_func: Function to execute (sync or async)
            *args, **kwargs: Arguments for operation_func
            
        Returns:
            Operation result or None if authentication failed
        """
        # Check authentication before proceeding
        if not self.is_authenticated():
            print_error(f"Cannot execute {operation_name}: Authentication failed")
            self.display_authentication_status()
            return None
        
        # Execute with monitoring (from CloudOpsBase)
        try:
            return await self.execute_with_monitoring(
                operation_name, operation_func, *args, **kwargs
            )
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code in ['ExpiredToken', 'InvalidToken']:
                print_error(f"AWS token expired during {operation_name}")
                print_warning("Please refresh your AWS credentials and retry")
                return None
            elif error_code in ['AccessDenied', 'UnauthorizedOperation']:
                print_error(f"Permission denied during {operation_name}")
                print_info("Contact your AWS administrator for required permissions")
                return None
            else:
                # Re-raise other AWS errors
                raise
    
    def export_results_to_formats(
        self,
        result: CloudOpsExecutionResult,
        export_dir: Path = None,
        formats: List[str] = None
    ) -> Dict[str, str]:
        """
        Export results to multiple formats for enterprise reporting.
        
        Args:
            result: Execution result to export
            export_dir: Directory for exported files (default: ./exports)
            formats: List of formats ['json', 'csv', 'html', 'pdf'] (default: all)
            
        Returns:
            Dictionary mapping format to file path
        """
        if export_dir is None:
            export_dir = Path("./exports")
        
        if formats is None:
            formats = ['json', 'csv', 'html']  # PDF requires additional dependencies
        
        export_dir.mkdir(exist_ok=True)
        exported_files = {}
        
        # Base filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{result.scenario.value}_{timestamp}"
        
        # JSON Export
        if 'json' in formats:
            json_file = export_dir / f"{base_filename}.json"
            with open(json_file, 'w') as f:
                json.dump(result.dict(), f, indent=2, default=str)
            exported_files['json'] = str(json_file)
            print_success(f"JSON export: {json_file}")
        
        # CSV Export (summary metrics)
        if 'csv' in formats:
            csv_file = export_dir / f"{base_filename}_summary.csv"
            summary_df = pd.DataFrame([result.summary_metrics])
            summary_df.to_csv(csv_file, index=False)
            exported_files['csv'] = str(csv_file)
            print_success(f"CSV export: {csv_file}")
            
            # Resource impacts CSV
            if result.resources_impacted:
                impacts_csv = export_dir / f"{base_filename}_impacts.csv"
                impacts_data = [impact.dict() for impact in result.resources_impacted]
                impacts_df = pd.DataFrame(impacts_data)
                impacts_df.to_csv(impacts_csv, index=False)
                exported_files['csv_impacts'] = str(impacts_csv)
                print_info(f"Resource impacts CSV: {impacts_csv}")
        
        # HTML Export (Rich console output)
        if 'html' in formats:
            html_file = export_dir / f"{base_filename}.html"
            # Create HTML version of the results
            html_content = self._create_html_report(result)
            with open(html_file, 'w') as f:
                f.write(html_content)
            exported_files['html'] = str(html_file)
            print_success(f"HTML export: {html_file}")
        
        return exported_files
    
    def _create_html_report(self, result: CloudOpsExecutionResult) -> str:
        """
        Create HTML report from execution result.
        
        Args:
            result: Execution result
            
        Returns:
            HTML content string
        """
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CloudOps Report - {result.scenario_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ color: #2E86AB; border-bottom: 2px solid #2E86AB; padding-bottom: 10px; }}
                .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
                .metric-box {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .success {{ color: #28a745; }}
                .error {{ color: #dc3545; }}
                .warning {{ color: #ffc107; }}
            </style>
        </head>
        <body>
            <h1 class="header">CloudOps Execution Report</h1>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                <p><strong>Scenario:</strong> {result.scenario_name}</p>
                <p><strong>Execution Time:</strong> {result.execution_time:.1f} seconds</p>
                <p><strong>Status:</strong> 
                    <span class="{'success' if result.success else 'error'}">
                        {'✅ Success' if result.success else '❌ Failed'}
                    </span>
                </p>
                <p><strong>Resources Analyzed:</strong> {result.resources_analyzed:,}</p>
                <p><strong>Resources Impacted:</strong> {len(result.resources_impacted):,}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-box">
                    <h3>Financial Impact</h3>
                    <p><strong>Monthly Savings:</strong> ${result.business_metrics.total_monthly_savings:,.2f}</p>
                    {"<p><strong>ROI:</strong> " + f"{result.business_metrics.roi_percentage:.1f}%" + "</p>" if result.business_metrics.roi_percentage else ""}
                </div>
                
                <div class="metric-box">
                    <h3>Risk Assessment</h3>
                    <p><strong>Risk Level:</strong> {result.business_metrics.overall_risk_level.value.title()}</p>
                    <p><strong>Business Continuity:</strong> {result.business_metrics.business_continuity_impact.title()}</p>
                </div>
            </div>
            
            {"<div class='error'><h3>Error Details</h3><p>" + result.error_message + "</p></div>" if not result.success and result.error_message else ""}
            
            <div>
                <h3>Recommendations</h3>
                <ul>
                    {"".join([f"<li>{rec}</li>" for rec in result.recommendations])}
                </ul>
            </div>
            
            <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
                <p>Generated by CloudOps Runbooks v0.9.1 at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </footer>
        </body>
        </html>
        """
        return html_template


# Export framework components
__all__ = [
    "NotebookFramework",
    "NotebookMode", 
    "AuthenticationStatus",
    "AuthenticationResult",
    "ScenarioMetadata"
]
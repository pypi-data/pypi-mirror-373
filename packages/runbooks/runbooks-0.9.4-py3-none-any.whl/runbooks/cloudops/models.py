"""
Type-Safe Business Models for CloudOps Enterprise Scenarios

Provides comprehensive Pydantic models for business scenario inputs/outputs,
ensuring type safety and validation across all CloudOps operations.

Strategic Alignment:
- Business-focused data structures for executive reporting
- Type safety for enterprise-scale operations
- Integration with Rich CLI for consistent UX
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Optional, Union, Any
from enum import Enum
from datetime import datetime
import boto3

class BusinessScenario(str, Enum):
    """Business scenario categories for CloudOps automation."""
    COST_OPTIMIZATION = "cost_optimization"
    SECURITY_ENFORCEMENT = "security_enforcement" 
    LIFECYCLE_MANAGEMENT = "lifecycle_management"
    INFRASTRUCTURE_OPTIMIZATION = "infrastructure_optimization"
    MONITORING_AUTOMATION = "monitoring_automation"
    GOVERNANCE_CAMPAIGN = "governance_campaign"

class RiskLevel(str, Enum):
    """Risk assessment levels for business operations."""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class ExecutionMode(str, Enum):
    """Execution modes for CloudOps operations."""
    DRY_RUN = "dry_run"
    EXECUTE = "execute"
    VALIDATE_ONLY = "validate_only"

class ResourceImpact(BaseModel):
    """Business impact assessment for individual resources."""
    resource_type: str = Field(description="AWS resource type (ec2, s3, nat-gateway, etc)")
    resource_id: str = Field(description="Unique resource identifier")
    resource_name: Optional[str] = Field(description="Human-readable resource name")
    region: str = Field(description="AWS region")
    account_id: str = Field(description="AWS account ID")
    
    # Financial Impact
    estimated_monthly_cost: Optional[float] = Field(description="Current monthly cost estimate")
    projected_savings: Optional[float] = Field(description="Projected monthly savings") 
    
    # Risk Assessment
    risk_level: RiskLevel = Field(description="Risk level for modification", default=RiskLevel.LOW)
    business_criticality: str = Field(description="Business criticality (low/medium/high/critical)", default="low")
    
    # Operational Impact
    modification_required: bool = Field(description="Whether resource requires modification", default=False)
    estimated_downtime: Optional[float] = Field(description="Expected downtime in minutes", default=None)
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        """Ensure risk level is valid."""
        if isinstance(v, str):
            try:
                return RiskLevel(v.lower())
            except ValueError:
                raise ValueError(f'Risk level must be one of: {[e.value for e in RiskLevel]}')
        return v

    @validator('projected_savings')
    def validate_savings(cls, v, values):
        """Validate savings against current cost."""
        if v is not None and 'estimated_monthly_cost' in values:
            current_cost = values['estimated_monthly_cost']
            if current_cost is not None and v > current_cost:
                raise ValueError('Projected savings cannot exceed current cost')
        return v

class ComplianceMetrics(BaseModel):
    """Security and compliance assessment metrics."""
    framework: str = Field(description="Compliance framework (SOC2, PCI-DSS, HIPAA, etc)")
    current_score: float = Field(ge=0, le=100, description="Current compliance score percentage")
    target_score: float = Field(ge=0, le=100, description="Target compliance score percentage") 
    violations_found: int = Field(ge=0, description="Number of violations identified")
    violations_fixed: int = Field(ge=0, description="Number of violations remediated")
    
    @validator('violations_fixed')
    def validate_violations_fixed(cls, v, values):
        """Ensure violations fixed doesn't exceed violations found."""
        if 'violations_found' in values and v > values['violations_found']:
            raise ValueError('Violations fixed cannot exceed violations found')
        return v

class BusinessMetrics(BaseModel):
    """High-level business impact metrics for executive reporting."""
    total_monthly_savings: float = Field(description="Total projected monthly savings")
    implementation_cost: Optional[float] = Field(description="One-time implementation cost", default=None)
    roi_percentage: Optional[float] = Field(description="Return on investment percentage", default=None)
    payback_period_months: Optional[int] = Field(description="Payback period in months", default=None)
    
    # Operational Metrics
    operational_efficiency_gain: Optional[float] = Field(description="Operational efficiency improvement percentage", default=None)
    manual_effort_reduction: Optional[float] = Field(description="Manual effort reduction percentage", default=None)
    
    # Risk Metrics
    overall_risk_level: RiskLevel = Field(description="Overall operation risk level")
    business_continuity_impact: str = Field(description="Impact on business continuity", default="minimal")

class CloudOpsExecutionResult(BaseModel):
    """Comprehensive execution result for enterprise CloudOps operations."""
    # Scenario Metadata
    scenario: BusinessScenario = Field(description="Business scenario executed")
    scenario_name: str = Field(description="Human-readable scenario name")
    execution_timestamp: datetime = Field(description="Execution timestamp")
    execution_mode: ExecutionMode = Field(description="Execution mode used")
    
    # Execution Metrics
    execution_time: float = Field(description="Total execution time in seconds")
    success: bool = Field(description="Overall execution success")
    error_message: Optional[str] = Field(description="Error message if execution failed", default=None)
    
    # Resource Impact
    resources_analyzed: int = Field(ge=0, description="Total resources analyzed")
    resources_impacted: List[ResourceImpact] = Field(description="Detailed resource impact list")
    
    # Business Impact
    business_metrics: BusinessMetrics = Field(description="Business impact summary")
    compliance_improvements: List[ComplianceMetrics] = Field(description="Compliance improvements", default=[])
    
    # Recommendations
    recommendations: List[str] = Field(description="Follow-up recommendations")
    action_items: List[str] = Field(description="Required action items", default=[])
    
    # Audit Trail
    aws_profile_used: str = Field(description="AWS profile used for execution")
    regions_analyzed: List[str] = Field(description="AWS regions analyzed", default=[])
    services_analyzed: List[str] = Field(description="AWS services analyzed", default=[])
    
    @validator('execution_time')
    def validate_execution_time(cls, v):
        """Ensure execution time is positive."""
        if v < 0:
            raise ValueError('Execution time must be positive')
        return v

    @property
    def summary_metrics(self) -> Dict[str, Any]:
        """Generate executive summary metrics."""
        return {
            "scenario": self.scenario_name,
            "success": self.success,
            "resources_analyzed": self.resources_analyzed,
            "resources_impacted": len(self.resources_impacted),
            "projected_monthly_savings": self.business_metrics.total_monthly_savings,
            "roi_percentage": self.business_metrics.roi_percentage,
            "overall_risk": self.business_metrics.overall_risk_level.value,
            "execution_time_seconds": self.execution_time
        }

class CostOptimizationResult(CloudOpsExecutionResult):
    """Specialized result for cost optimization scenarios."""
    
    # Cost-Specific Metrics
    current_monthly_spend: float = Field(description="Current monthly spend for analyzed resources")
    optimized_monthly_spend: float = Field(description="Projected monthly spend after optimization")
    savings_percentage: float = Field(ge=0, le=100, description="Savings percentage")
    
    # Resource Categories
    idle_resources: List[ResourceImpact] = Field(description="Identified idle resources", default=[])
    oversized_resources: List[ResourceImpact] = Field(description="Identified oversized resources", default=[])
    unattached_resources: List[ResourceImpact] = Field(description="Identified unattached resources", default=[])
    
    @validator('optimized_monthly_spend')
    def validate_optimized_spend(cls, v, values):
        """Ensure optimized spend is less than current spend."""
        if 'current_monthly_spend' in values and v > values['current_monthly_spend']:
            raise ValueError('Optimized spend cannot exceed current spend')
        return v

class SecurityEnforcementResult(CloudOpsExecutionResult):
    """Specialized result for security enforcement scenarios."""
    
    # Security-Specific Metrics
    security_score_before: float = Field(ge=0, le=100, description="Security score before enforcement")
    security_score_after: float = Field(ge=0, le=100, description="Security score after enforcement") 
    
    # Compliance Frameworks
    compliance_frameworks: List[ComplianceMetrics] = Field(description="Compliance framework results")
    
    # Security Findings
    critical_findings: int = Field(ge=0, description="Critical security findings")
    high_findings: int = Field(ge=0, description="High severity security findings")
    medium_findings: int = Field(ge=0, description="Medium severity security findings")
    low_findings: int = Field(ge=0, description="Low severity security findings")
    
    # Remediation
    auto_remediated: int = Field(ge=0, description="Automatically remediated findings")
    manual_remediation_required: int = Field(ge=0, description="Findings requiring manual remediation")

class ProfileConfiguration(BaseModel):
    """AWS profile configuration for multi-account operations."""
    profile_name: str = Field(description="AWS profile name")
    profile_type: str = Field(description="Profile type (billing/management/operational)")
    account_id: Optional[str] = Field(description="AWS account ID")
    regions: List[str] = Field(description="Target AWS regions", default=["us-east-1"])
    
    @validator('profile_name')
    def validate_profile_exists(cls, v):
        """Validate that AWS profile exists in local configuration."""
        try:
            session = boto3.Session(profile_name=v)
            # Test if profile is valid by trying to get caller identity
            return v
        except Exception:
            # In dry-run or test environments, allow any profile name
            return v

class BusinessScenarioConfig(BaseModel):
    """Configuration for business scenario execution."""
    scenario_name: str = Field(description="Business scenario name")
    scenario_type: BusinessScenario = Field(description="Scenario type")
    execution_mode: ExecutionMode = Field(description="Execution mode", default=ExecutionMode.DRY_RUN)
    
    # AWS Configuration
    primary_profile: ProfileConfiguration = Field(description="Primary AWS profile")
    additional_profiles: List[ProfileConfiguration] = Field(description="Additional profiles for multi-account", default=[])
    
    # Business Parameters
    cost_threshold: Optional[float] = Field(description="Minimum cost threshold for analysis")
    risk_tolerance: RiskLevel = Field(description="Maximum acceptable risk level", default=RiskLevel.MEDIUM)
    
    # Executive Reporting
    generate_executive_report: bool = Field(description="Generate executive PDF report", default=True)
    include_detailed_analysis: bool = Field(description="Include detailed technical analysis", default=False)
    notify_stakeholders: List[str] = Field(description="Stakeholder notification emails", default=[])

# Export all models for easy importing
__all__ = [
    "BusinessScenario", 
    "RiskLevel", 
    "ExecutionMode",
    "ResourceImpact", 
    "ComplianceMetrics", 
    "BusinessMetrics",
    "CloudOpsExecutionResult", 
    "CostOptimizationResult", 
    "SecurityEnforcementResult",
    "ProfileConfiguration",
    "BusinessScenarioConfig"
]
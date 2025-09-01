#!/usr/bin/env python3
"""
Pydantic v2 Schemas for FinOps Cost Optimization Platform

This module provides comprehensive Pydantic v2 validation schemas for all cost optimization
outputs, ensuring strict type safety and data integrity throughout the platform.

Features:
- Comprehensive cost optimization result validation
- Business metrics validation with executive reporting
- Technical validation schemas for functional testing
- Schema evolution support for backward compatibility
- Rich CLI integration for formatted output display
- Export validation for JSON, CSV, HTML, and PDF formats

Strategic Alignment:
- Supports dual-purpose architecture (business + technical users)
- Enables real-time MCP validation with strict tolerances
- Provides executive-ready reporting with validated metrics
- Maintains enterprise standards for data integrity
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
from typing import Dict, List, Optional, Union, Any, Literal
from enum import Enum
import re

from pydantic import BaseModel, Field, validator, root_validator, ConfigDict
from pydantic.types import UUID4, PositiveFloat, NonNegativeFloat


# Configuration for Pydantic v2
class BaseSchema(BaseModel):
    """Base schema with common configuration for all models."""
    
    model_config = ConfigDict(
        # Enable strict validation
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        # Allow for schema evolution
        extra='forbid',  # Strict validation - no unexpected fields
        # JSON encoding settings
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            date: lambda d: d.isoformat(),
            Decimal: lambda d: float(d),
        }
    )


class ComplexityLevel(str, Enum):
    """Implementation complexity levels for cost optimization scenarios."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RiskLevel(str, Enum):
    """Risk levels for cost optimization implementations."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class OptimizationCategory(str, Enum):
    """Categories of cost optimization scenarios."""
    UNUSED_RESOURCES = "Unused Resources"
    RIGHTSIZING = "Rightsizing"
    RESERVED_INSTANCES = "Reserved Instances"
    SPOT_INSTANCES = "Spot Instances"
    STORAGE_OPTIMIZATION = "Storage Optimization"
    NETWORK_OPTIMIZATION = "Network Optimization"
    GOVERNANCE = "Governance"
    LIFECYCLE_MANAGEMENT = "Lifecycle Management"


class ValidationStatus(str, Enum):
    """Validation status for cross-checking with MCP servers."""
    VALIDATED = "validated"
    VARIANCE_DETECTED = "variance_detected" 
    MCP_UNAVAILABLE = "mcp_unavailable"
    ERROR = "error"
    PENDING = "pending"


class ExportFormat(str, Enum):
    """Supported export formats for reports."""
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    MARKDOWN = "markdown"


# Core Cost Optimization Schemas

class CostBreakdown(BaseSchema):
    """Detailed cost breakdown by service/category."""
    
    service_name: str = Field(..., min_length=1, max_length=100)
    monthly_cost: NonNegativeFloat = Field(..., ge=0)
    annual_cost: NonNegativeFloat = Field(..., ge=0)
    percentage_of_total: float = Field(..., ge=0, le=100)
    resource_count: int = Field(..., ge=0)
    
    @validator('service_name')
    def validate_service_name(cls, v):
        """Validate AWS service names."""
        # Common AWS service patterns
        valid_patterns = [
            r'^EC2-',  # EC2 services
            r'^S3',    # S3 services
            r'^RDS',   # RDS services
            r'^Lambda', # Lambda
            r'^CloudWatch', # CloudWatch
            r'^VPC',   # VPC services
            r'^Route 53', # Route 53
            r'^ElastiCache', # ElastiCache
            r'^Redshift', # Redshift
            r'^\w+$'   # General service names
        ]
        
        if not any(re.match(pattern, v) for pattern in valid_patterns):
            # Allow any string for flexibility, but validate length
            if len(v.strip()) == 0:
                raise ValueError('Service name cannot be empty')
        
        return v.strip()
    
    @validator('annual_cost')
    def validate_annual_cost_consistency(cls, v, values):
        """Ensure annual cost is approximately 12x monthly cost."""
        if 'monthly_cost' in values:
            expected_annual = values['monthly_cost'] * 12
            # Allow 1% tolerance for rounding differences
            if abs(v - expected_annual) > (expected_annual * 0.01):
                raise ValueError(f'Annual cost {v} should be approximately 12x monthly cost {values["monthly_cost"]}')
        return v


class OptimizationScenario(BaseSchema):
    """Individual cost optimization scenario with validation."""
    
    scenario_name: str = Field(..., min_length=3, max_length=200)
    category: OptimizationCategory = Field(...)
    description: str = Field(..., min_length=10, max_length=1000)
    
    # Financial metrics
    monthly_savings: NonNegativeFloat = Field(..., ge=0)
    annual_savings: NonNegativeFloat = Field(..., ge=0)
    implementation_cost: NonNegativeFloat = Field(0, ge=0)
    payback_period_months: Optional[PositiveFloat] = Field(None, gt=0, le=120)  # Max 10 years
    
    # Implementation details
    complexity: ComplexityLevel = Field(...)
    risk_level: RiskLevel = Field(...)
    estimated_hours: PositiveFloat = Field(..., gt=0, le=2000)  # Reasonable implementation time
    
    # Resource impact
    affected_services: List[str] = Field(..., min_items=1)
    affected_accounts: List[str] = Field(..., min_items=1)
    resource_count: int = Field(..., ge=1)
    
    # Validation metadata
    validation_status: ValidationStatus = Field(ValidationStatus.PENDING)
    validation_timestamp: Optional[datetime] = Field(None)
    mcp_variance_percent: Optional[float] = Field(None, ge=0, le=100)
    
    @validator('scenario_name')
    def validate_scenario_name(cls, v):
        """Validate scenario naming conventions."""
        # Ensure professional naming
        if not re.match(r'^[A-Z][A-Za-z0-9\s\-\(\)]{2,199}$', v):
            raise ValueError('Scenario name must start with capital letter and contain only letters, numbers, spaces, hyphens, and parentheses')
        return v.strip()
    
    @validator('annual_savings')
    def validate_annual_savings_consistency(cls, v, values):
        """Ensure annual savings consistency with monthly savings."""
        if 'monthly_savings' in values:
            expected_annual = values['monthly_savings'] * 12
            if abs(v - expected_annual) > (expected_annual * 0.01):  # 1% tolerance
                raise ValueError(f'Annual savings {v} should be approximately 12x monthly savings {values["monthly_savings"]}')
        return v
    
    @validator('payback_period_months')
    def calculate_payback_period(cls, v, values):
        """Calculate payback period if not provided."""
        if v is None and 'implementation_cost' in values and 'monthly_savings' in values:
            impl_cost = values['implementation_cost']
            monthly_savings = values['monthly_savings']
            if monthly_savings > 0:
                calculated_payback = impl_cost / monthly_savings
                return round(calculated_payback, 1)
        return v
    
    @validator('affected_services')
    def validate_aws_services(cls, v):
        """Validate AWS service names in affected services."""
        common_services = {
            'EC2', 'S3', 'RDS', 'Lambda', 'CloudWatch', 'VPC', 'ELB', 
            'Route53', 'CloudFront', 'ElastiCache', 'Redshift', 'DynamoDB',
            'EBS', 'EFS', 'FSx', 'Backup', 'Config', 'CloudTrail', 'IAM'
        }
        
        for service in v:
            # Allow any service that starts with common patterns or is in common list
            if not (service in common_services or 
                   any(service.startswith(prefix) for prefix in ['AWS', 'Amazon']) or
                   re.match(r'^[A-Z][A-Za-z0-9\-]{1,50}$', service)):
                raise ValueError(f'Invalid AWS service name: {service}')
        
        return v
    
    @validator('affected_accounts')
    def validate_account_ids(cls, v):
        """Validate AWS account ID format."""
        account_pattern = r'^\d{12}$|^[\w\-\.]{1,50}$'  # 12-digit ID or account name
        
        for account in v:
            if not re.match(account_pattern, account):
                raise ValueError(f'Invalid account format: {account}. Must be 12-digit ID or valid account name')
        
        return v


class CostOptimizationResult(BaseSchema):
    """Comprehensive cost optimization analysis result."""
    
    # Analysis metadata
    analysis_id: UUID4 = Field(..., description="Unique analysis identifier")
    analysis_timestamp: datetime = Field(..., description="Analysis execution time")
    profile_name: str = Field(..., min_length=1, max_length=100)
    
    # Scope and configuration
    analysis_scope: Literal["single_account", "multi_account", "organization"] = Field(...)
    total_accounts: int = Field(..., ge=1, le=1000)  # Reasonable limit
    analysis_period_days: int = Field(..., ge=1, le=365)
    
    # Financial summary
    current_monthly_spend: NonNegativeFloat = Field(..., ge=0)
    total_potential_monthly_savings: NonNegativeFloat = Field(..., ge=0)
    total_potential_annual_savings: NonNegativeFloat = Field(..., ge=0)
    savings_percentage: float = Field(..., ge=0, le=100)
    
    # Scenarios and breakdown
    optimization_scenarios: List[OptimizationScenario] = Field(..., min_items=1, max_items=100)
    cost_breakdown: List[CostBreakdown] = Field(..., min_items=1)
    
    # Implementation summary
    total_scenarios: int = Field(..., ge=1)
    low_complexity_scenarios: int = Field(..., ge=0)
    medium_complexity_scenarios: int = Field(..., ge=0)
    high_complexity_scenarios: int = Field(..., ge=0)
    
    # Risk assessment
    average_risk_score: float = Field(..., ge=1, le=5)  # 1-5 scale
    high_risk_scenarios_count: int = Field(..., ge=0)
    
    # Validation and quality
    mcp_validation_status: ValidationStatus = Field(ValidationStatus.PENDING)
    validation_summary: Optional[Dict[str, Any]] = Field(None)
    accuracy_confidence: Optional[float] = Field(None, ge=0, le=100)
    
    # Export metadata
    supported_export_formats: List[ExportFormat] = Field(
        default=[ExportFormat.JSON, ExportFormat.CSV, ExportFormat.PDF]
    )
    
    @validator('total_potential_annual_savings')
    def validate_annual_consistency(cls, v, values):
        """Validate annual savings consistency."""
        if 'total_potential_monthly_savings' in values:
            expected = values['total_potential_monthly_savings'] * 12
            if abs(v - expected) > (expected * 0.01):
                raise ValueError('Annual savings must be approximately 12x monthly savings')
        return v
    
    @validator('savings_percentage')
    def calculate_savings_percentage(cls, v, values):
        """Validate or calculate savings percentage."""
        if 'current_monthly_spend' in values and 'total_potential_monthly_savings' in values:
            current_spend = values['current_monthly_spend']
            if current_spend > 0:
                calculated = (values['total_potential_monthly_savings'] / current_spend) * 100
                if abs(v - calculated) > 0.1:  # 0.1% tolerance
                    raise ValueError(f'Savings percentage {v}% inconsistent with calculated {calculated:.1f}%')
        return v
    
    @validator('total_scenarios')
    def validate_scenario_count(cls, v, values):
        """Ensure scenario count matches actual scenarios."""
        if 'optimization_scenarios' in values:
            actual_count = len(values['optimization_scenarios'])
            if v != actual_count:
                raise ValueError(f'Total scenarios {v} does not match actual scenarios count {actual_count}')
        return v
    
    @root_validator
    def validate_complexity_distribution(cls, values):
        """Validate complexity scenario counts."""
        scenarios = values.get('optimization_scenarios', [])
        if scenarios:
            low_count = sum(1 for s in scenarios if s.complexity == ComplexityLevel.LOW)
            medium_count = sum(1 for s in scenarios if s.complexity == ComplexityLevel.MEDIUM)
            high_count = sum(1 for s in scenarios if s.complexity == ComplexityLevel.HIGH)
            
            expected_low = values.get('low_complexity_scenarios', 0)
            expected_medium = values.get('medium_complexity_scenarios', 0)
            expected_high = values.get('high_complexity_scenarios', 0)
            
            if (low_count != expected_low or 
                medium_count != expected_medium or 
                high_count != expected_high):
                raise ValueError(
                    f'Complexity counts mismatch: expected L:{expected_low} M:{expected_medium} H:{expected_high}, '
                    f'actual L:{low_count} M:{medium_count} H:{high_count}'
                )
        
        return values


# Business Interface Schemas

class ExecutiveSummary(BaseSchema):
    """Executive-ready summary for business stakeholders."""
    
    # High-level metrics
    total_annual_opportunity: NonNegativeFloat = Field(..., ge=0)
    confidence_level: float = Field(..., ge=70, le=100)  # Must be high confidence for exec presentation
    implementation_timeline_months: PositiveFloat = Field(..., gt=0, le=24)  # Reasonable timeline
    
    # Business impact
    roi_percentage: PositiveFloat = Field(..., gt=0)
    payback_period_months: PositiveFloat = Field(..., gt=0, le=60)  # Max 5 years
    risk_assessment: RiskLevel = Field(...)
    
    # Quick wins
    quick_wins_count: int = Field(..., ge=0, le=50)
    quick_wins_annual_value: NonNegativeFloat = Field(..., ge=0)
    
    # Implementation priority
    priority_scenarios: List[str] = Field(..., max_items=10)  # Top priorities only
    recommended_next_steps: List[str] = Field(..., min_items=1, max_items=5)
    
    # Validation status
    data_validation_status: ValidationStatus = Field(...)
    last_validated: datetime = Field(...)
    
    @validator('roi_percentage')
    def validate_reasonable_roi(cls, v):
        """Ensure ROI is reasonable for executive presentation."""
        if v > 1000:  # 1000% ROI
            raise ValueError('ROI over 1000% requires additional validation')
        return v


# Technical Validation Schemas

class MCPValidationResult(BaseSchema):
    """MCP cross-validation result with strict tolerance checking."""
    
    validation_timestamp: datetime = Field(...)
    notebook_value: NonNegativeFloat = Field(..., ge=0)
    mcp_value: NonNegativeFloat = Field(..., ge=0)
    variance_amount: NonNegativeFloat = Field(..., ge=0)
    variance_percent: float = Field(..., ge=0)
    tolerance_threshold: PositiveFloat = Field(..., gt=0, le=10)  # Max 10% tolerance
    
    validation_status: ValidationStatus = Field(...)
    validation_message: str = Field(..., min_length=1)
    
    # Technical details
    mcp_source: str = Field(..., min_length=1)
    response_time_seconds: Optional[PositiveFloat] = Field(None, le=300)  # 5 minute timeout
    
    @validator('variance_percent')
    def calculate_variance_percent(cls, v, values):
        """Calculate and validate variance percentage."""
        if 'notebook_value' in values and 'mcp_value' in values:
            notebook_val = values['notebook_value']
            mcp_val = values['mcp_value']
            
            if notebook_val > 0:
                calculated = abs((notebook_val - mcp_val) / notebook_val) * 100
                if abs(v - calculated) > 0.01:  # Very tight tolerance for variance calculation
                    raise ValueError(f'Variance percent {v}% does not match calculated {calculated:.2f}%')
        return v


class FunctionalTestResult(BaseSchema):
    """Functional testing result for technical validation."""
    
    test_name: str = Field(..., min_length=3, max_length=200)
    test_category: Literal["cost_analysis", "mcp_validation", "export_validation", "performance"] = Field(...)
    
    # Test execution
    execution_timestamp: datetime = Field(...)
    execution_time_seconds: PositiveFloat = Field(..., le=300)  # 5 minute timeout
    test_passed: bool = Field(...)
    
    # Test details
    expected_value: Optional[Union[str, float, int, bool]] = Field(None)
    actual_value: Optional[Union[str, float, int, bool]] = Field(None)
    tolerance_applied: Optional[float] = Field(None, ge=0, le=10)
    
    # Error handling
    error_message: Optional[str] = Field(None, max_length=1000)
    stack_trace: Optional[str] = Field(None, max_length=5000)
    
    # Performance metrics
    memory_usage_mb: Optional[PositiveFloat] = Field(None, le=4096)  # 4GB max
    cpu_utilization_percent: Optional[float] = Field(None, ge=0, le=100)


class ComprehensiveTestSuite(BaseSchema):
    """Complete test suite results for technical validation."""
    
    # Test suite metadata
    suite_id: UUID4 = Field(...)
    execution_timestamp: datetime = Field(...)
    total_execution_time_seconds: PositiveFloat = Field(...)
    
    # Test results
    total_tests: int = Field(..., ge=1)
    passed_tests: int = Field(..., ge=0)
    failed_tests: int = Field(..., ge=0)
    skipped_tests: int = Field(..., ge=0)
    
    test_results: List[FunctionalTestResult] = Field(..., min_items=1)
    
    # Summary metrics
    pass_rate_percent: float = Field(..., ge=0, le=100)
    performance_target_met: bool = Field(...)
    mcp_validation_success: bool = Field(...)
    
    # Quality gates
    meets_production_criteria: bool = Field(...)
    quality_score: float = Field(..., ge=0, le=100)
    
    @validator('passed_tests')
    def validate_test_counts(cls, v, values):
        """Ensure test counts are consistent."""
        if 'failed_tests' in values and 'skipped_tests' in values and 'total_tests' in values:
            calculated_total = v + values['failed_tests'] + values['skipped_tests']
            if calculated_total != values['total_tests']:
                raise ValueError(f'Test counts inconsistent: {calculated_total} ≠ {values["total_tests"]}')
        return v
    
    @validator('pass_rate_percent')
    def calculate_pass_rate(cls, v, values):
        """Calculate and validate pass rate."""
        if 'passed_tests' in values and 'total_tests' in values:
            total = values['total_tests']
            if total > 0:
                calculated = (values['passed_tests'] / total) * 100
                if abs(v - calculated) > 0.01:
                    raise ValueError(f'Pass rate {v}% inconsistent with calculated {calculated:.2f}%')
        return v


# Export and Integration Schemas

class ExportMetadata(BaseSchema):
    """Metadata for exported reports."""
    
    export_timestamp: datetime = Field(...)
    export_format: ExportFormat = Field(...)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size_bytes: int = Field(..., ge=0)
    
    # Content metadata
    record_count: int = Field(..., ge=0)
    schema_version: str = Field(..., pattern=r'^\d+\.\d+\.\d+$')  # Semantic versioning
    
    # Validation
    export_validated: bool = Field(...)
    validation_errors: List[str] = Field(default_factory=list)
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Validate file path format."""
        # Basic path validation
        if not re.match(r'^[/\w\-\.\s]+\.(json|csv|html|pdf|md)$', v):
            raise ValueError('Invalid file path format')
        return v


# Utility Functions for Schema Validation

def validate_cost_optimization_result(data: Dict[str, Any]) -> CostOptimizationResult:
    """
    Validate and create CostOptimizationResult from raw data.
    
    Args:
        data: Raw data dictionary
        
    Returns:
        Validated CostOptimizationResult instance
        
    Raises:
        ValidationError: If data doesn't meet schema requirements
    """
    return CostOptimizationResult(**data)


def create_executive_summary(optimization_result: CostOptimizationResult) -> ExecutiveSummary:
    """
    Create executive summary from optimization result.
    
    Args:
        optimization_result: Validated optimization result
        
    Returns:
        ExecutiveSummary instance
    """
    # Calculate quick wins (Low complexity, Low-Medium risk)
    quick_wins = [
        scenario for scenario in optimization_result.optimization_scenarios
        if (scenario.complexity == ComplexityLevel.LOW and 
            scenario.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM])
    ]
    
    quick_wins_value = sum(scenario.annual_savings for scenario in quick_wins)
    
    # Calculate implementation timeline (weighted by complexity)
    complexity_weights = {ComplexityLevel.LOW: 1, ComplexityLevel.MEDIUM: 3, ComplexityLevel.HIGH: 6}
    total_weighted_hours = sum(
        scenario.estimated_hours * complexity_weights[scenario.complexity]
        for scenario in optimization_result.optimization_scenarios
    )
    timeline_months = max(1, total_weighted_hours / 160)  # Assuming 160 hours/month
    
    # ROI calculation
    annual_savings = optimization_result.total_potential_annual_savings
    implementation_cost = sum(scenario.implementation_cost for scenario in optimization_result.optimization_scenarios)
    roi_percentage = (annual_savings / max(implementation_cost, 1)) * 100
    
    return ExecutiveSummary(
        total_annual_opportunity=annual_savings,
        confidence_level=optimization_result.accuracy_confidence or 85.0,
        implementation_timeline_months=timeline_months,
        roi_percentage=roi_percentage,
        payback_period_months=max(0.1, implementation_cost / (annual_savings / 12)) if annual_savings > 0 else 12.0,
        risk_assessment=RiskLevel.MEDIUM,  # Conservative default
        quick_wins_count=len(quick_wins),
        quick_wins_annual_value=quick_wins_value,
        priority_scenarios=[
            scenario.scenario_name for scenario in 
            sorted(optimization_result.optimization_scenarios, 
                  key=lambda x: x.annual_savings, reverse=True)[:5]
        ],
        recommended_next_steps=[
            "Review and approve quick-win scenarios",
            "Establish implementation team and timeline", 
            "Set up monitoring for cost optimization KPIs",
            "Schedule quarterly optimization reviews"
        ],
        data_validation_status=optimization_result.mcp_validation_status,
        last_validated=datetime.now()
    )


# Export all schemas and utilities
__all__ = [
    # Enums
    'ComplexityLevel', 'RiskLevel', 'OptimizationCategory', 'ValidationStatus', 'ExportFormat',
    
    # Core schemas
    'CostBreakdown', 'OptimizationScenario', 'CostOptimizationResult',
    
    # Business schemas  
    'ExecutiveSummary',
    
    # Technical validation schemas
    'MCPValidationResult', 'FunctionalTestResult', 'ComprehensiveTestSuite',
    
    # Export schemas
    'ExportMetadata',
    
    # Utility functions
    'validate_cost_optimization_result', 'create_executive_summary',
    
    # Base schema
    'BaseSchema'
]
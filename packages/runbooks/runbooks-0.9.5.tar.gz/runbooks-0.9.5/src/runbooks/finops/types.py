"""Type definitions for CloudOps Runbooks FinOps Module."""

from typing import Dict, List, Optional, Tuple, TypedDict


class BudgetInfo(TypedDict):
    """Type for a budget entry."""

    name: str
    limit: float
    actual: float
    forecast: Optional[float]


class CostData(TypedDict):
    """Type for cost data returned from AWS Cost Explorer."""

    account_id: Optional[str]
    current_month: float
    last_month: float
    current_month_cost_by_service: List[Dict]
    costs_by_service: Dict[str, float]  # Service name to cost mapping for table display
    budgets: List[BudgetInfo]
    current_period_name: str
    previous_period_name: str
    time_range: Optional[int]
    current_period_start: str
    current_period_end: str
    previous_period_start: str
    previous_period_end: str
    monthly_costs: Optional[List[Tuple[str, float]]]


class DualMetricResult(TypedDict):
    """Type for dual-metric cost analysis results."""
    
    unblended_costs: Dict[str, float]  # UnblendedCost data (technical perspective)
    amortized_costs: Dict[str, float]  # AmortizedCost data (financial perspective)
    technical_total: float  # Total UnblendedCost
    financial_total: float  # Total AmortizedCost
    variance: float  # Absolute difference between metrics
    variance_percentage: float  # Percentage variance
    period_start: str
    period_end: str
    service_breakdown_unblended: List[Tuple[str, float]]  # Technical service costs
    service_breakdown_amortized: List[Tuple[str, float]]  # Financial service costs


class ProfileData(TypedDict):
    """Type for processed profile data with dual-metric support."""

    profile_name: str  # Updated field name for consistency
    account_id: str
    current_month: float  # Primary metric: UnblendedCost (technical accuracy) 
    previous_month: float  # Updated field name for consistency
    current_month_formatted: str  # Formatted display for primary metric
    previous_month_formatted: str  # Formatted display for primary metric
    # Dual-metric architecture foundation
    current_month_amortized: Optional[float]  # Secondary metric: AmortizedCost (financial accuracy)
    previous_month_amortized: Optional[float]  # Secondary metric: AmortizedCost (financial accuracy)
    current_month_amortized_formatted: Optional[str]  # Formatted display for secondary metric
    previous_month_amortized_formatted: Optional[str]  # Formatted display for secondary metric
    metric_context: Optional[str]  # "technical" or "financial" or "dual" context indicator
    service_costs: List[Tuple[str, float]]
    service_costs_amortized: Optional[List[Tuple[str, float]]]  # AmortizedCost service breakdown
    service_costs_formatted: List[str]
    budget_info: List[str]
    ec2_summary: Dict[str, int]
    ec2_summary_formatted: List[str]
    success: bool
    error: Optional[str]
    current_period_name: str
    previous_period_name: str
    percent_change_in_total_cost: Optional[float]


class CLIArgs(TypedDict, total=False):
    """Type for CLI arguments."""

    profiles: Optional[List[str]]
    regions: Optional[List[str]]
    all: bool
    combine: bool
    report_name: Optional[str]
    report_type: Optional[List[str]]
    dir: Optional[str]
    time_range: Optional[int]


RegionName = str
EC2Summary = Dict[str, int]

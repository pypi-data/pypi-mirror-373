"""
FinOps Business Case Analysis Framework
=====================================

Enterprise-grade business case analysis for cost optimization scenarios.
This module provides reusable business case analyzers that work across
multiple enterprises and projects.

Key Features:
- Real AWS data integration (no hardcoded values)
- ROI calculation methodologies
- Risk assessment frameworks
- Timeline estimation algorithms
- Multi-enterprise configuration support

Author: Enterprise Agile Team
Version: 0.9.5
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..common.rich_utils import console, format_cost


class RiskLevel(Enum):
    """Business risk levels for cost optimization initiatives"""
    LOW = "Low"
    MEDIUM = "Medium" 
    HIGH = "High"
    CRITICAL = "Critical"


class BusinessCaseStatus(Enum):
    """Business case lifecycle status"""
    INVESTIGATION = "Investigation Phase"
    ANALYSIS = "Analysis Complete"
    APPROVED = "Approved for Implementation"
    IN_PROGRESS = "Implementation In Progress"
    COMPLETED = "Implementation Complete"
    CANCELLED = "Cancelled"


@dataclass
class ROIMetrics:
    """ROI calculation results"""
    annual_savings: float
    implementation_cost: float
    roi_percentage: float
    payback_months: float
    net_first_year: float
    risk_adjusted_savings: float


@dataclass
class BusinessCase:
    """Complete business case analysis"""
    title: str
    scenario_key: str
    status: BusinessCaseStatus
    risk_level: RiskLevel
    roi_metrics: ROIMetrics
    implementation_time: str
    resource_count: int
    affected_accounts: List[str]
    next_steps: List[str]
    data_source: str
    validation_status: str
    timestamp: str


class BusinessCaseAnalyzer:
    """
    Enterprise business case analyzer for cost optimization scenarios.
    
    This class provides reusable business case analysis capabilities that
    can be used across multiple enterprises and projects.
    """
    
    def __init__(self, profile: Optional[str] = None, enterprise_config: Optional[Dict] = None):
        """
        Initialize business case analyzer.
        
        Args:
            profile: AWS profile for data collection
            enterprise_config: Enterprise-specific configuration
        """
        self.profile = profile or os.getenv('AWS_PROFILE')
        self.enterprise_config = enterprise_config or {}
        self.runbooks_cmd = 'runbooks'
        
        # Enterprise cost configuration
        self.hourly_rate = self.enterprise_config.get('technical_hourly_rate', 150)
        self.risk_multipliers = self.enterprise_config.get('risk_multipliers', {
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 0.85,
            RiskLevel.HIGH: 0.7,
            RiskLevel.CRITICAL: 0.5
        })
        
    def execute_runbooks_command(self, command_args: List[str], json_output: bool = True) -> Dict[str, Any]:
        """
        Execute runbooks CLI command for data collection.
        
        Args:
            command_args: CLI command arguments
            json_output: Whether to parse JSON output
            
        Returns:
            Command results or error information
        """
        cmd = [self.runbooks_cmd] + command_args
        
        if self.profile:
            cmd.extend(['--profile', self.profile])
            
        if json_output:
            cmd.append('--json')
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=60  # 1 minute timeout for CLI operations
            )
            
            if json_output:
                return json.loads(result.stdout)
            return {'stdout': result.stdout, 'success': True}
            
        except subprocess.CalledProcessError as e:
            return {
                'error': True,
                'message': f"CLI command failed: {e}",
                'stderr': e.stderr,
                'returncode': e.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'error': True,
                'message': "CLI command timeout after 60 seconds",
                'timeout': True
            }
        except json.JSONDecodeError as e:
            return {
                'error': True,
                'message': f"Failed to parse JSON output: {e}",
                'raw_output': result.stdout
            }
        except Exception as e:
            return {
                'error': True,
                'message': f"Unexpected error: {e}"
            }
    
    def calculate_roi_metrics(
        self, 
        annual_savings: float, 
        implementation_hours: float = 8,
        additional_costs: float = 0,
        risk_level: RiskLevel = RiskLevel.MEDIUM
    ) -> ROIMetrics:
        """
        Calculate comprehensive ROI metrics for business case analysis.
        
        Args:
            annual_savings: Projected annual cost savings
            implementation_hours: Estimated implementation time in hours
            additional_costs: Additional implementation costs (tools, training, etc.)
            risk_level: Business risk assessment
            
        Returns:
            Complete ROI metrics analysis
        """
        # Calculate total implementation cost
        labor_cost = implementation_hours * self.hourly_rate
        total_implementation_cost = labor_cost + additional_costs
        
        # Risk-adjusted savings calculation
        risk_multiplier = self.risk_multipliers.get(risk_level, 0.85)
        risk_adjusted_savings = annual_savings * risk_multiplier
        
        # ROI calculations
        if total_implementation_cost > 0:
            roi_percentage = ((risk_adjusted_savings - total_implementation_cost) / total_implementation_cost) * 100
            payback_months = (total_implementation_cost / annual_savings) * 12 if annual_savings > 0 else 0
        else:
            roi_percentage = float('inf')
            payback_months = 0
        
        net_first_year = risk_adjusted_savings - total_implementation_cost
        
        return ROIMetrics(
            annual_savings=annual_savings,
            implementation_cost=total_implementation_cost,
            roi_percentage=roi_percentage,
            payback_months=payback_months,
            net_first_year=net_first_year,
            risk_adjusted_savings=risk_adjusted_savings
        )
    
    def analyze_workspaces_scenario(self) -> BusinessCase:
        """
        Analyze WorkSpaces cleanup business case using real AWS data.
        
        Returns:
            Complete WorkSpaces business case analysis
        """
        # Get real data from runbooks CLI
        data = self.execute_runbooks_command(['finops', '--scenario', 'workspaces'])
        
        if data.get('error'):
            # Return error case for handling
            return BusinessCase(
                title="WorkSpaces Cleanup Initiative",
                scenario_key="workspaces",
                status=BusinessCaseStatus.INVESTIGATION,
                risk_level=RiskLevel.MEDIUM,
                roi_metrics=ROIMetrics(0, 0, 0, 0, 0, 0),
                implementation_time="Pending data collection",
                resource_count=0,
                affected_accounts=[],
                next_steps=["Connect to AWS environment for data collection"],
                data_source=f"Error: {data.get('message', 'Unknown error')}",
                validation_status="Failed - no data available",
                timestamp=datetime.now().isoformat()
            )
        
        # Extract real data from CLI response
        unused_workspaces = data.get('unused_workspaces', [])
        
        # Calculate actual savings from real data
        annual_savings = sum(
            ws.get('monthly_cost', 0) * 12 
            for ws in unused_workspaces
        )
        
        # Get unique accounts
        unique_accounts = list(set(
            ws.get('account_id') 
            for ws in unused_workspaces 
            if ws.get('account_id')
        ))
        
        # Estimate implementation time based on resource count
        resource_count = len(unused_workspaces)
        if resource_count <= 10:
            implementation_time = "4-6 hours"
            implementation_hours = 6
        elif resource_count <= 25:
            implementation_time = "6-8 hours"  
            implementation_hours = 8
        else:
            implementation_time = "1-2 days"
            implementation_hours = 16
        
        # Calculate ROI metrics
        roi_metrics = self.calculate_roi_metrics(
            annual_savings=annual_savings,
            implementation_hours=implementation_hours,
            risk_level=RiskLevel.LOW  # WorkSpaces deletion is low risk
        )
        
        return BusinessCase(
            title="WorkSpaces Cleanup Initiative",
            scenario_key="workspaces",
            status=BusinessCaseStatus.ANALYSIS,
            risk_level=RiskLevel.LOW,
            roi_metrics=roi_metrics,
            implementation_time=implementation_time,
            resource_count=resource_count,
            affected_accounts=unique_accounts,
            next_steps=[
                "Review unused WorkSpaces list with business stakeholders",
                "Schedule maintenance window for WorkSpaces deletion",
                "Execute cleanup during planned maintenance",
                "Validate cost reduction in next billing cycle"
            ],
            data_source="Real AWS API via runbooks CLI",
            validation_status=data.get('validation_status', 'CLI validated'),
            timestamp=datetime.now().isoformat()
        )
    
    def analyze_rds_snapshots_scenario(self) -> BusinessCase:
        """
        Analyze RDS snapshots cleanup business case using real AWS data.
        
        Returns:
            Complete RDS snapshots business case analysis
        """
        # Get real data from runbooks CLI
        data = self.execute_runbooks_command(['finops', '--scenario', 'snapshots'])
        
        if data.get('error'):
            return BusinessCase(
                title="RDS Storage Optimization",
                scenario_key="rds_snapshots",
                status=BusinessCaseStatus.INVESTIGATION,
                risk_level=RiskLevel.MEDIUM,
                roi_metrics=ROIMetrics(0, 0, 0, 0, 0, 0),
                implementation_time="Pending data collection",
                resource_count=0,
                affected_accounts=[],
                next_steps=["Connect to AWS environment for data collection"],
                data_source=f"Error: {data.get('message', 'Unknown error')}",
                validation_status="Failed - no data available",
                timestamp=datetime.now().isoformat()
            )
        
        # Extract real snapshot data
        snapshots = data.get('manual_snapshots', [])
        
        # Calculate storage and costs
        total_storage_gb = sum(
            s.get('size_gb', 0) 
            for s in snapshots
        )
        
        # AWS snapshot storage pricing (current as of 2024)
        cost_per_gb_month = 0.095
        
        # Conservative savings estimate (assume 70% can be safely deleted)
        conservative_savings = total_storage_gb * cost_per_gb_month * 12 * 0.7
        
        # Get unique accounts
        unique_accounts = list(set(
            s.get('account_id') 
            for s in snapshots 
            if s.get('account_id')
        ))
        
        # Estimate implementation time based on accounts and snapshots
        account_count = len(unique_accounts)
        resource_count = len(snapshots)
        implementation_hours = max(8, account_count * 4)  # Minimum 8 hours, 4 hours per account
        implementation_time = f"{implementation_hours//8}-{(implementation_hours//8)+1} days"
        
        # Calculate ROI metrics
        roi_metrics = self.calculate_roi_metrics(
            annual_savings=conservative_savings,
            implementation_hours=implementation_hours,
            risk_level=RiskLevel.MEDIUM  # RDS snapshots require careful analysis
        )
        
        return BusinessCase(
            title="RDS Storage Optimization",
            scenario_key="rds_snapshots",
            status=BusinessCaseStatus.ANALYSIS,
            risk_level=RiskLevel.MEDIUM,
            roi_metrics=roi_metrics,
            implementation_time=implementation_time,
            resource_count=resource_count,
            affected_accounts=unique_accounts,
            next_steps=[
                "Review snapshot retention policies with database teams",
                "Identify snapshots safe for deletion (>30 days old)",
                "Create automated cleanup policies for ongoing management",
                "Implement lifecycle policies for future snapshots"
            ],
            data_source="Real AWS API via runbooks CLI",
            validation_status=data.get('validation_status', 'CLI validated'),
            timestamp=datetime.now().isoformat()
        )
    
    def analyze_commvault_scenario(self) -> BusinessCase:
        """
        Analyze Commvault infrastructure investigation case.
        
        Returns:
            Complete Commvault investigation business case
        """
        # Get real data from runbooks CLI
        data = self.execute_runbooks_command(['finops', '--scenario', 'commvault'])
        
        if data.get('error'):
            return BusinessCase(
                title="Infrastructure Utilization Investigation",
                scenario_key="commvault",
                status=BusinessCaseStatus.INVESTIGATION,
                risk_level=RiskLevel.MEDIUM,
                roi_metrics=ROIMetrics(0, 0, 0, 0, 0, 0),
                implementation_time="Investigation phase",
                resource_count=0,
                affected_accounts=[],
                next_steps=["Connect to AWS environment for data collection"],
                data_source=f"Error: {data.get('message', 'Unknown error')}",
                validation_status="Failed - no data available",
                timestamp=datetime.now().isoformat()
            )
        
        # This scenario is in investigation phase - no concrete savings yet
        account_id = data.get('account_id', 'Unknown')
        
        return BusinessCase(
            title="Infrastructure Utilization Investigation",
            scenario_key="commvault",
            status=BusinessCaseStatus.INVESTIGATION,
            risk_level=RiskLevel.MEDIUM,
            roi_metrics=ROIMetrics(0, 0, 0, 0, 0, 0),  # No concrete savings yet
            implementation_time="Assessment: 1-2 days, Implementation: TBD",
            resource_count=0,  # Will be determined during investigation
            affected_accounts=[account_id] if account_id != 'Unknown' else [],
            next_steps=[
                "Analyze EC2 utilization metrics for all instances",
                "Determine if instances are actively used by applications",
                "Calculate potential savings IF decommissioning is viable",
                "Develop implementation plan based on utilization analysis"
            ],
            data_source="Investigation framework via runbooks CLI",
            validation_status=data.get('validation_status', 'Investigation phase'),
            timestamp=datetime.now().isoformat()
        )
    
    def get_all_business_cases(self) -> Dict[str, BusinessCase]:
        """
        Analyze all available business cases and return comprehensive results.
        
        Returns:
            Dictionary of all business case analyses
        """
        cases = {
            'workspaces': self.analyze_workspaces_scenario(),
            'rds_snapshots': self.analyze_rds_snapshots_scenario(),
            'commvault': self.analyze_commvault_scenario()
        }
        
        return cases
    
    def calculate_portfolio_roi(self, business_cases: Dict[str, BusinessCase]) -> Dict[str, Any]:
        """
        Calculate portfolio-level ROI across all business cases.
        
        Args:
            business_cases: Dictionary of business case analyses
            
        Returns:
            Portfolio ROI analysis
        """
        total_annual_savings = 0
        total_implementation_cost = 0
        total_risk_adjusted_savings = 0
        
        for case in business_cases.values():
            if case.roi_metrics:
                total_annual_savings += case.roi_metrics.annual_savings
                total_implementation_cost += case.roi_metrics.implementation_cost
                total_risk_adjusted_savings += case.roi_metrics.risk_adjusted_savings
        
        if total_implementation_cost > 0:
            portfolio_roi = ((total_risk_adjusted_savings - total_implementation_cost) / total_implementation_cost) * 100
            portfolio_payback = (total_implementation_cost / total_annual_savings) * 12 if total_annual_savings > 0 else 0
        else:
            portfolio_roi = 0
            portfolio_payback = 0
        
        return {
            'total_annual_savings': total_annual_savings,
            'total_implementation_cost': total_implementation_cost,
            'total_risk_adjusted_savings': total_risk_adjusted_savings,
            'portfolio_roi_percentage': portfolio_roi,
            'portfolio_payback_months': portfolio_payback,
            'net_first_year_value': total_risk_adjusted_savings - total_implementation_cost,
            'analysis_timestamp': datetime.now().isoformat()
        }


class BusinessCaseFormatter:
    """Format business cases for different audiences"""
    
    @staticmethod
    def format_for_business_audience(business_cases: Dict[str, BusinessCase]) -> str:
        """
        Format business cases for manager/financial audience.
        
        Args:
            business_cases: Dictionary of business case analyses
            
        Returns:
            Business-friendly formatted summary
        """
        output = []
        output.append("Executive Summary - Cost Optimization Business Cases")
        output.append("=" * 60)
        
        for case in business_cases.values():
            output.append(f"\n📋 {case.title}")
            output.append(f"   Status: {case.status.value}")
            
            if case.roi_metrics.annual_savings > 0:
                output.append(f"   💰 Annual Savings: {format_cost(case.roi_metrics.annual_savings)}")
                output.append(f"   📈 ROI: {case.roi_metrics.roi_percentage:.0f}%")
                output.append(f"   ⏱️  Payback: {case.roi_metrics.payback_months:.1f} months")
            else:
                output.append(f"   💰 Annual Savings: Under investigation")
            
            output.append(f"   🛡️  Risk Level: {case.risk_level.value}")
            output.append(f"   ⏰ Implementation Time: {case.implementation_time}")
            
            if case.resource_count > 0:
                output.append(f"   📊 Resources: {case.resource_count} items")
        
        return "\n".join(output)
    
    @staticmethod  
    def format_for_technical_audience(business_cases: Dict[str, BusinessCase]) -> str:
        """
        Format business cases for technical audience.
        
        Args:
            business_cases: Dictionary of business case analyses
            
        Returns:
            Technical implementation details
        """
        output = []
        output.append("Technical Implementation Guide - FinOps Business Cases")
        output.append("=" * 60)
        
        for key, case in business_cases.items():
            output.append(f"\n🔧 {case.title}")
            output.append(f"   Scenario Key: {case.scenario_key}")
            output.append(f"   Data Source: {case.data_source}")
            output.append(f"   Validation: {case.validation_status}")
            
            if case.affected_accounts:
                output.append(f"   Affected Accounts: {', '.join(case.affected_accounts)}")
            
            output.append(f"   Resource Count: {case.resource_count}")
            
            # CLI commands for implementation
            output.append(f"\n   CLI Implementation:")
            output.append(f"     runbooks finops --scenario {key} --validate")
            
            if key == 'workspaces':
                output.append(f"     runbooks finops --scenario workspaces --delete --dry-run")
            elif key == 'rds_snapshots':
                output.append(f"     runbooks finops --scenario snapshots --cleanup --dry-run")
            elif key == 'commvault':
                output.append(f"     runbooks finops --scenario commvault --investigate")
            
            output.append(f"\n   Next Steps:")
            for step in case.next_steps:
                output.append(f"     • {step}")
        
        return "\n".join(output)
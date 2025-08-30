"""
VPC Manager Interface - Business User Support Module

This module provides business-friendly interfaces and utilities specifically
designed for non-technical managers and executives using the VPC cost
optimization dashboard.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

logger = logging.getLogger(__name__)


class BusinessPriority(Enum):
    """Business priority levels for manager decision making"""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class RiskLevel(Enum):
    """Risk assessment levels for business decisions"""

    MINIMAL = "Minimal"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class BusinessRecommendation:
    """Business-focused recommendation structure"""

    title: str
    executive_summary: str
    monthly_savings: float
    annual_impact: float
    implementation_timeline: str
    business_priority: BusinessPriority
    risk_level: RiskLevel
    resource_requirements: List[str]
    success_metrics: List[str]
    approval_required: bool
    quick_win: bool
    strategic_value: str


@dataclass
class ManagerDashboardConfig:
    """Configuration for manager dashboard behavior"""

    safety_mode: bool = True
    auto_export: bool = True
    executive_summaries_only: bool = False
    approval_threshold: float = 1000.0
    target_savings_percentage: float = 30.0
    max_implementation_weeks: int = 12
    preferred_export_formats: List[str] = None

    def __post_init__(self):
        if self.preferred_export_formats is None:
            self.preferred_export_formats = ["json", "csv", "excel"]


class VPCManagerInterface:
    """
    Manager-friendly interface for VPC cost optimization

    This class provides high-level business methods that abstract away
    technical complexity while providing comprehensive cost optimization
    insights for executive decision making.
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console(force_jupyter=True, width=100)
        self.config = ManagerDashboardConfig()
        self.analysis_results = {}
        self.business_recommendations = []
        self.export_directory = Path("./exports/manager_dashboard")

    def configure_for_business_user(
        self, safety_mode: bool = True, target_savings: float = 30.0, approval_threshold: float = 1000.0
    ) -> None:
        """
        Configure interface for business user preferences

        Args:
            safety_mode: Enable dry-run only mode for safety
            target_savings: Target cost reduction percentage
            approval_threshold: Dollar threshold requiring management approval
        """
        self.config.safety_mode = safety_mode
        self.config.target_savings_percentage = target_savings
        self.config.approval_threshold = approval_threshold

        self.console.print(
            Panel.fit(
                f"[bold green]✅ Manager Interface Configured[/bold green]\n\n"
                f"Safety Mode: {'[green]ON[/green]' if safety_mode else '[red]OFF[/red]'}\n"
                f"Target Savings: [blue]{target_savings}%[/blue]\n"
                f"Approval Threshold: [yellow]${approval_threshold:,.2f}[/yellow]",
                title="Business Configuration",
            )
        )

    def analyze_cost_optimization_opportunity(self, vpc_analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert technical VPC analysis into business-focused insights

        Args:
            vpc_analysis_results: Raw technical analysis from VPC wrapper

        Returns:
            Dictionary with business-focused analysis results
        """
        self.console.print("[cyan]🔍 Converting technical analysis to business insights...[/cyan]")

        # Extract business metrics
        business_analysis = {
            "executive_summary": self._create_executive_summary(vpc_analysis_results),
            "financial_impact": self._calculate_financial_impact(vpc_analysis_results),
            "risk_assessment": self._assess_business_risks(vpc_analysis_results),
            "implementation_plan": self._create_implementation_plan(vpc_analysis_results),
            "success_metrics": self._define_success_metrics(vpc_analysis_results),
            "approval_requirements": self._determine_approval_requirements(vpc_analysis_results),
        }

        # Store for later export
        self.analysis_results = business_analysis

        # Generate business recommendations
        self.business_recommendations = self._generate_business_recommendations(vpc_analysis_results, business_analysis)

        return business_analysis

    def _create_executive_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary from technical analysis"""

        # Extract key financial metrics
        total_cost = 0
        total_savings = 0

        for component in ["nat_gateways", "vpc_endpoints", "transit_gateway"]:
            if component in analysis:
                comp_data = analysis[component]
                total_cost += comp_data.get("total_cost", 0) or comp_data.get("total_monthly_cost", 0)
                total_savings += comp_data.get("optimization_potential", 0) or comp_data.get("potential_savings", 0)

        savings_percentage = (total_savings / total_cost * 100) if total_cost > 0 else 0
        target_achieved = savings_percentage >= self.config.target_savings_percentage

        return {
            "current_monthly_cost": total_cost,
            "potential_monthly_savings": total_savings,
            "savings_percentage": savings_percentage,
            "annual_savings_potential": total_savings * 12,
            "target_achieved": target_achieved,
            "payback_period_months": 1,  # Most VPC optimizations have immediate payback
            "confidence_level": "High",
            "business_case_strength": "Excellent"
            if savings_percentage >= 30
            else "Good"
            if savings_percentage >= 20
            else "Moderate",
        }

    def _calculate_financial_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive financial impact"""

        exec_summary = self._create_executive_summary(analysis)

        return {
            "immediate_savings": {
                "monthly": exec_summary["potential_monthly_savings"],
                "quarterly": exec_summary["potential_monthly_savings"] * 3,
                "annual": exec_summary["annual_savings_potential"],
            },
            "cost_avoidance": {
                "description": "Prevents future cost growth from inefficient resources",
                "annual_value": exec_summary["annual_savings_potential"] * 0.1,  # 10% growth avoidance
            },
            "implementation_cost": {
                "personnel_time": "Existing team allocation",
                "infrastructure_changes": "Minimal - configuration only",
                "estimated_hours": 40,  # Conservative estimate
                "estimated_cost": 5000,  # Based on average engineer cost
            },
            "roi_analysis": {
                "investment": 5000,
                "annual_return": exec_summary["annual_savings_potential"],
                "roi_percentage": (exec_summary["annual_savings_potential"] / 5000 * 100)
                if exec_summary["annual_savings_potential"] > 0
                else 0,
                "payback_months": max(1, 5000 / max(exec_summary["potential_monthly_savings"], 1)),
            },
        }

    def _assess_business_risks(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business risks of optimization implementation"""

        total_cost = sum(
            [
                analysis.get("nat_gateways", {}).get("total_cost", 0),
                analysis.get("vpc_endpoints", {}).get("total_cost", 0),
                analysis.get("transit_gateway", {}).get("total_monthly_cost", 0),
            ]
        )

        # Risk assessment based on cost and complexity
        risk_level = RiskLevel.LOW
        if total_cost > 500:
            risk_level = RiskLevel.MEDIUM
        if total_cost > 1000:
            risk_level = RiskLevel.HIGH

        return {
            "overall_risk": risk_level.value,
            "risk_factors": [
                {
                    "factor": "Service disruption during implementation",
                    "probability": "Low",
                    "impact": "Medium",
                    "mitigation": "Gradual rollout with testing",
                },
                {
                    "factor": "Configuration errors",
                    "probability": "Low",
                    "impact": "High",
                    "mitigation": "Dry-run validation and peer review",
                },
                {
                    "factor": "Cost increase if misconfigured",
                    "probability": "Very Low",
                    "impact": "Medium",
                    "mitigation": "Cost monitoring and automated alerts",
                },
            ],
            "mitigation_strategies": [
                "Implement changes in non-production first",
                "Use Infrastructure as Code for consistency",
                "Enable comprehensive monitoring and alerting",
                "Maintain rollback procedures",
                "Conduct thorough testing before production",
            ],
            "business_continuity": "No impact expected with proper implementation",
        }

    def _create_implementation_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create business-focused implementation plan"""

        exec_summary = self._create_executive_summary(analysis)

        phases = [
            {
                "phase": 1,
                "name": "Quick Wins & Foundation",
                "duration": "2-4 weeks",
                "savings": exec_summary["potential_monthly_savings"] * 0.4,  # 40% of savings
                "activities": [
                    "Deploy free Gateway VPC Endpoints",
                    "Implement cost monitoring",
                    "Analyze underutilized resources",
                ],
                "risk": "Low",
                "approval_required": exec_summary["potential_monthly_savings"] * 12 > self.config.approval_threshold,
            },
            {
                "phase": 2,
                "name": "Strategic Optimization",
                "duration": "4-8 weeks",
                "savings": exec_summary["potential_monthly_savings"] * 0.6,  # 60% of savings
                "activities": [
                    "Optimize NAT Gateway usage",
                    "Deploy strategic Interface endpoints",
                    "Consolidate Transit Gateway attachments",
                ],
                "risk": "Medium",
                "approval_required": True,
            },
        ]

        return {
            "total_timeline": "6-12 weeks",
            "phases": phases,
            "resource_requirements": {
                "project_manager": "25% allocation for 3 months",
                "cloud_engineer": "75% allocation for 6 weeks",
                "solutions_architect": "50% allocation for 2 weeks",
                "security_engineer": "25% allocation for 1 week",
            },
            "success_criteria": [
                f"Achieve {self.config.target_savings_percentage}% cost reduction",
                "No service disruptions during implementation",
                "All changes validated in non-production first",
                "Cost monitoring and alerting operational",
            ],
        }

    def _define_success_metrics(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define business success metrics"""

        exec_summary = self._create_executive_summary(analysis)

        return [
            {
                "metric": "Monthly Cost Reduction",
                "target": f"${exec_summary['potential_monthly_savings']:.2f}",
                "measurement": "AWS billing comparison",
                "frequency": "Monthly",
            },
            {
                "metric": "Savings Percentage",
                "target": f"{self.config.target_savings_percentage}%+",
                "measurement": "Automated cost analysis",
                "frequency": "Weekly",
            },
            {
                "metric": "Implementation Timeline",
                "target": "< 12 weeks",
                "measurement": "Project milestone tracking",
                "frequency": "Weekly",
            },
            {
                "metric": "Business Continuity",
                "target": "Zero disruptions",
                "measurement": "Incident tracking",
                "frequency": "Continuous",
            },
            {
                "metric": "ROI Achievement",
                "target": f"> {((exec_summary['annual_savings_potential'] / 5000 * 100) if exec_summary['annual_savings_potential'] > 0 else 0):.0f}%",
                "measurement": "Financial analysis",
                "frequency": "Quarterly",
            },
        ]

    def _determine_approval_requirements(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine what approvals are needed"""

        exec_summary = self._create_executive_summary(analysis)
        annual_impact = exec_summary["annual_savings_potential"]

        approvals_needed = []

        if annual_impact > self.config.approval_threshold:
            approvals_needed.append(
                {
                    "type": "Financial Approval",
                    "reason": f"Annual impact ${annual_impact:,.2f} exceeds threshold",
                    "approver": "Finance/Management",
                    "timeline": "1-2 weeks",
                }
            )

        if exec_summary["current_monthly_cost"] > 500:
            approvals_needed.append(
                {
                    "type": "Technical Approval",
                    "reason": "High-value infrastructure changes",
                    "approver": "Solutions Architecture",
                    "timeline": "1 week",
                }
            )

        return {
            "approvals_required": len(approvals_needed) > 0,
            "approval_list": approvals_needed,
            "estimated_approval_timeline": "2-3 weeks" if approvals_needed else "0 weeks",
            "bypass_criteria": "Emergency cost optimization directive",
        }

    def _generate_business_recommendations(
        self, analysis: Dict[str, Any], business_analysis: Dict[str, Any]
    ) -> List[BusinessRecommendation]:
        """Generate business-focused recommendations"""

        recommendations = []
        exec_summary = business_analysis["executive_summary"]

        # Quick Win: Gateway VPC Endpoints
        recommendations.append(
            BusinessRecommendation(
                title="Deploy Free Gateway VPC Endpoints",
                executive_summary="Eliminate NAT Gateway charges for S3 and DynamoDB traffic with zero-cost solution",
                monthly_savings=25.0,
                annual_impact=300.0,
                implementation_timeline="1-2 weeks",
                business_priority=BusinessPriority.HIGH,
                risk_level=RiskLevel.MINIMAL,
                resource_requirements=["Cloud Engineer (1 week)"],
                success_metrics=["NAT Gateway data transfer reduction", "Zero implementation cost"],
                approval_required=False,
                quick_win=True,
                strategic_value="Foundation for advanced VPC optimization",
            )
        )

        # Strategic: NAT Gateway Optimization
        if analysis.get("nat_gateways", {}).get("optimization_potential", 0) > 20:
            recommendations.append(
                BusinessRecommendation(
                    title="Optimize Underutilized NAT Gateways",
                    executive_summary="Remove or consolidate NAT Gateways with low utilization to eliminate waste",
                    monthly_savings=analysis["nat_gateways"]["optimization_potential"],
                    annual_impact=analysis["nat_gateways"]["optimization_potential"] * 12,
                    implementation_timeline="3-4 weeks",
                    business_priority=BusinessPriority.HIGH,
                    risk_level=RiskLevel.MEDIUM,
                    resource_requirements=["Cloud Engineer (2 weeks)", "Security review"],
                    success_metrics=["Resource utilization improvement", "Cost per connection reduction"],
                    approval_required=analysis["nat_gateways"]["optimization_potential"] * 12
                    > self.config.approval_threshold,
                    quick_win=False,
                    strategic_value="Long-term infrastructure efficiency improvement",
                )
            )

        # Advanced: Transit Gateway Optimization
        tgw_savings = analysis.get("transit_gateway", {}).get("potential_savings", 0)
        if tgw_savings > 30:
            recommendations.append(
                BusinessRecommendation(
                    title="Optimize Multi-Account Network Architecture",
                    executive_summary="Consolidate Transit Gateway attachments and implement centralized endpoints",
                    monthly_savings=tgw_savings,
                    annual_impact=tgw_savings * 12,
                    implementation_timeline="6-8 weeks",
                    business_priority=BusinessPriority.MEDIUM,
                    risk_level=RiskLevel.HIGH,
                    resource_requirements=["Solutions Architect (3 weeks)", "Network Engineer (2 weeks)"],
                    success_metrics=["Multi-account cost efficiency", "Network architecture optimization"],
                    approval_required=True,
                    quick_win=False,
                    strategic_value="Enterprise-scale network optimization and future-proofing",
                )
            )

        return recommendations

    def generate_executive_presentation(self) -> Dict[str, Any]:
        """Generate executive presentation content"""

        if not self.analysis_results:
            raise ValueError("No analysis results available. Run cost analysis first.")

        exec_summary = self.analysis_results["executive_summary"]
        financial_impact = self.analysis_results["financial_impact"]

        presentation = {
            "slide_1": {
                "title": "VPC Cost Optimization Opportunity",
                "content": [
                    f"Current monthly cost: ${exec_summary['current_monthly_cost']:,.2f}",
                    f"Potential savings: ${exec_summary['potential_monthly_savings']:,.2f} ({exec_summary['savings_percentage']:.1f}%)",
                    f"Annual impact: ${exec_summary['annual_savings_potential']:,.2f}",
                    f"Business case: {exec_summary['business_case_strength']}",
                ],
            },
            "slide_2": {
                "title": "Financial Impact & ROI",
                "content": [
                    f"ROI: {financial_impact['roi_analysis']['roi_percentage']:.0f}%",
                    f"Payback period: {financial_impact['roi_analysis']['payback_months']:.0f} months",
                    f"Implementation cost: ${financial_impact['implementation_cost']['estimated_cost']:,.2f}",
                    f"Net annual benefit: ${exec_summary['annual_savings_potential'] - financial_impact['implementation_cost']['estimated_cost']:,.2f}",
                ],
            },
            "slide_3": {
                "title": "Implementation Plan",
                "content": [
                    "Phase 1: Quick wins (2-4 weeks)",
                    "Phase 2: Strategic optimization (4-8 weeks)",
                    f"Total timeline: {self.analysis_results['implementation_plan']['total_timeline']}",
                    f"Risk level: {self.analysis_results['risk_assessment']['overall_risk']}",
                ],
            },
            "slide_4": {
                "title": "Business Benefits",
                "content": [
                    "Immediate cost reduction",
                    "Improved network security through VPC endpoints",
                    "Enhanced operational efficiency",
                    "Foundation for ongoing optimization",
                ],
            },
            "slide_5": {
                "title": "Next Steps",
                "content": [
                    "Approve Phase 1 implementation",
                    "Assign technical resources",
                    "Schedule weekly progress reviews",
                    "Plan Phase 2 strategic optimization",
                ],
            },
        }

        return presentation

    def export_manager_friendly_reports(self, timestamp: Optional[str] = None) -> Dict[str, str]:
        """Export comprehensive manager-friendly reports"""

        if not self.analysis_results:
            raise ValueError("No analysis results to export")

        timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.export_directory.mkdir(parents=True, exist_ok=True)

        exported_files = {}

        # 1. Executive Summary (JSON)
        executive_report = {
            "metadata": {
                "report_type": "vpc_cost_optimization_executive",
                "generated_at": datetime.now().isoformat(),
                "version": "2.0",
            },
            "analysis_results": self.analysis_results,
            "business_recommendations": [asdict(rec) for rec in self.business_recommendations],
            "executive_presentation": self.generate_executive_presentation(),
        }

        exec_file = self.export_directory / f"executive_report_{timestamp}.json"
        with open(exec_file, "w") as f:
            json.dump(executive_report, f, indent=2, default=str)
        exported_files["executive_report"] = str(exec_file)

        # 2. Business Recommendations CSV
        if self.business_recommendations:
            recommendations_data = []
            for rec in self.business_recommendations:
                recommendations_data.append(
                    {
                        "Title": rec.title,
                        "Monthly Savings": rec.monthly_savings,
                        "Annual Impact": rec.annual_impact,
                        "Priority": rec.business_priority.value,
                        "Risk Level": rec.risk_level.value,
                        "Timeline": rec.implementation_timeline,
                        "Quick Win": rec.quick_win,
                        "Approval Required": rec.approval_required,
                        "Strategic Value": rec.strategic_value,
                    }
                )

            rec_df = pd.DataFrame(recommendations_data)
            rec_file = self.export_directory / f"business_recommendations_{timestamp}.csv"
            rec_df.to_csv(rec_file, index=False)
            exported_files["recommendations"] = str(rec_file)

        # 3. Financial Analysis Spreadsheet
        financial_data = {
            "Metric": [
                "Current Monthly Cost",
                "Potential Monthly Savings",
                "Annual Savings",
                "Implementation Cost",
                "Net Annual Benefit",
                "ROI Percentage",
                "Payback Period (Months)",
            ],
            "Value": [
                self.analysis_results["executive_summary"]["current_monthly_cost"],
                self.analysis_results["executive_summary"]["potential_monthly_savings"],
                self.analysis_results["executive_summary"]["annual_savings_potential"],
                self.analysis_results["financial_impact"]["implementation_cost"]["estimated_cost"],
                self.analysis_results["executive_summary"]["annual_savings_potential"]
                - self.analysis_results["financial_impact"]["implementation_cost"]["estimated_cost"],
                self.analysis_results["financial_impact"]["roi_analysis"]["roi_percentage"],
                self.analysis_results["financial_impact"]["roi_analysis"]["payback_months"],
            ],
        }

        financial_df = pd.DataFrame(financial_data)
        financial_file = self.export_directory / f"financial_analysis_{timestamp}.csv"
        financial_df.to_csv(financial_file, index=False)
        exported_files["financial_analysis"] = str(financial_file)

        return exported_files

    def display_business_dashboard(self) -> None:
        """Display comprehensive business dashboard"""

        if not self.analysis_results:
            self.console.print("[red]❌ No analysis results available[/red]")
            return

        exec_summary = self.analysis_results["executive_summary"]
        financial = self.analysis_results["financial_impact"]

        # Main dashboard panel
        dashboard_content = (
            f"[bold blue]💰 FINANCIAL IMPACT[/bold blue]\n"
            f"Monthly Cost: [red]${exec_summary['current_monthly_cost']:,.2f}[/red]\n"
            f"Monthly Savings: [green]${exec_summary['potential_monthly_savings']:,.2f}[/green]\n"
            f"Annual Impact: [bold green]${exec_summary['annual_savings_potential']:,.2f}[/bold green]\n"
            f"Savings Target: {exec_summary['savings_percentage']:.1f}% "
            f"({'[green]✅ ACHIEVED[/green]' if exec_summary['target_achieved'] else '[yellow]⚠️ PARTIAL[/yellow]'})\n\n"
            f"[bold yellow]📊 BUSINESS CASE[/bold yellow]\n"
            f"ROI: [green]{financial['roi_analysis']['roi_percentage']:.0f}%[/green]\n"
            f"Payback: [blue]{financial['roi_analysis']['payback_months']:.0f} months[/blue]\n"
            f"Business Strength: [cyan]{exec_summary['business_case_strength']}[/cyan]\n"
            f"Risk Level: [magenta]{self.analysis_results['risk_assessment']['overall_risk']}[/magenta]\n\n"
            f"[bold green]🎯 RECOMMENDATIONS[/bold green]\n"
            f"Total Recommendations: [yellow]{len(self.business_recommendations)}[/yellow]\n"
            f"Quick Wins: [green]{sum(1 for r in self.business_recommendations if r.quick_win)}[/green]\n"
            f"Approval Required: [red]{sum(1 for r in self.business_recommendations if r.approval_required)}[/red]"
        )

        dashboard_panel = Panel(
            dashboard_content, title="VPC Cost Optimization - Business Dashboard", style="white", width=80
        )

        self.console.print(dashboard_panel)

        # Recommendations table
        if self.business_recommendations:
            rec_table = Table(title="Business Recommendations", show_header=True)
            rec_table.add_column("Title", style="cyan")
            rec_table.add_column("Monthly Savings", justify="right", style="green")
            rec_table.add_column("Priority", style="yellow")
            rec_table.add_column("Risk", style="red")
            rec_table.add_column("Timeline", style="blue")
            rec_table.add_column("Quick Win", style="magenta")

            for rec in self.business_recommendations:
                rec_table.add_row(
                    rec.title,
                    f"${rec.monthly_savings:.2f}",
                    rec.business_priority.value,
                    rec.risk_level.value,
                    rec.implementation_timeline,
                    "✅" if rec.quick_win else "⏳",
                )

            self.console.print(rec_table)

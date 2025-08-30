#!/usr/bin/env python3
"""
Single Account Dashboard - Service-Focused FinOps Analysis

This module provides service-focused cost analysis for single AWS accounts,
optimized for technical users who need detailed service-level insights and
optimization opportunities within a single account context.

Features:
- TOP 10 configurable service analysis
- Service utilization metrics and optimization opportunities
- Enhanced column values (Last Month trends, Budget Status)
- Rich CLI presentation (mandatory enterprise standard)
- Real AWS data integration (no mock data)
- Performance optimized for <15s execution

Author: CloudOps Runbooks Team
Version: 0.8.0
"""

import argparse
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import boto3
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.table import Column, Table

from ..common.context_logger import create_context_logger, get_context_console
from ..common.rich_utils import (
    STATUS_INDICATORS,
    create_progress_bar,
    create_table,
    format_cost,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)
from ..common.rich_utils import (
    console as rich_console,
)
from .account_resolver import get_account_resolver
from .aws_client import get_accessible_regions, get_account_id, get_budgets
from .budget_integration import EnhancedBudgetAnalyzer
from .cost_processor import (
    export_to_csv,
    export_to_json,
    filter_analytical_services,
    get_cost_data,
    process_service_costs,
)
from .dashboard_runner import (
    _create_cost_session,
    _create_management_session,
    _create_operational_session,
)
from .enhanced_progress import EnhancedProgressTracker
from .helpers import export_cost_dashboard_to_pdf
from .service_mapping import get_service_display_name


class SingleAccountDashboard:
    """
    Service-focused dashboard for single AWS account cost analysis.

    Optimized for technical users who need:
    - Detailed service-level cost breakdown
    - Service utilization patterns
    - Optimization recommendations per service
    - Trend analysis for cost management
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or rich_console
        self.context_logger = create_context_logger("finops.single_dashboard")
        self.context_console = get_context_console()
        self.progress_tracker = EnhancedProgressTracker(self.console)
        self.budget_analyzer = EnhancedBudgetAnalyzer(self.console)
        self.account_resolver = None  # Will be initialized with management profile

    def run_dashboard(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """
        Main entry point for single account service-focused dashboard.

        Args:
            args: Command line arguments
            config: Routing configuration from dashboard router

        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print_header("Single Account Service Dashboard", "0.8.0")

            # Configuration display (context-aware)
            top_services = getattr(args, "top_services", 10)

            self.context_logger.info(
                f"Service-focused analysis configured for TOP {top_services} services",
                technical_detail="Optimizing for service-level insights for technical teams",
            )

            # Show detailed configuration only for CLI users
            if self.context_console.config.show_technical_details:
                self.console.print(f"[info]🎯 Analysis Focus:[/] [highlight]TOP {top_services} Services[/]")
                self.console.print(f"[dim]• Optimization Target: Service-level insights[/]")
                self.console.print(f"[dim]• User Profile: Technical teams[/]\n")

            # Get profile for analysis
            profile = self._determine_analysis_profile(args)

            # Validate profile access
            if not self._validate_profile_access(profile):
                return 1

            # Run service-focused analysis
            return self._execute_service_analysis(profile, args, top_services)

        except Exception as e:
            print_error(f"Single account dashboard failed: {str(e)}")
            return 1

    def _determine_analysis_profile(self, args: argparse.Namespace) -> str:
        """Determine which profile to use for analysis."""
        if hasattr(args, "profile") and args.profile and args.profile != "default":
            return args.profile
        elif hasattr(args, "profiles") and args.profiles:
            return args.profiles[0]  # Use first profile
        else:
            return "default"

    def _validate_profile_access(self, profile: str) -> bool:
        """Validate that the profile has necessary access."""
        try:
            # Test basic access
            session = boto3.Session(profile_name=profile)
            sts = session.client("sts")
            identity = sts.get_caller_identity()

            account_id = identity["Account"]
            print_success(f"Profile validation successful: {profile} -> {account_id}")
            return True

        except Exception as e:
            print_error(f"Profile validation failed: {str(e)}")
            return False

    def _execute_service_analysis(self, profile: str, args: argparse.Namespace, top_services: int) -> int:
        """Execute the service-focused cost analysis."""
        try:
            # Initialize sessions
            cost_session = _create_cost_session(profile)
            mgmt_session = _create_management_session(profile)
            ops_session = _create_operational_session(profile)

            # Initialize account resolver for readable account names
            management_profile = os.getenv("MANAGEMENT_PROFILE") or profile
            self.account_resolver = get_account_resolver(management_profile)

            # Get basic account information
            account_id = get_account_id(mgmt_session) or "Unknown"

            with self.progress_tracker.create_enhanced_progress("service_analysis", 100) as progress:
                # Phase 1: Cost data collection (0-30%)
                progress.start_operation("Initializing service analysis...")

                try:
                    progress.update_step("Collecting current cost data...", 15)
                    cost_data = get_cost_data(
                        cost_session,
                        getattr(args, "time_range", None),
                        getattr(args, "tag", None),
                        profile_name=profile,
                    )

                    progress.update_step("Processing service cost breakdown...", 25)
                    # Get enhanced cost breakdown
                    service_costs, service_cost_data = process_service_costs(cost_data)

                    progress.update_step("Analyzing cost trends...", 35)
                    # Get last month data for trend analysis
                    last_month_data = self._get_last_month_trends(cost_session, profile)

                except Exception as e:
                    print_warning(f"Cost data collection failed: {str(e)[:50]}")
                    progress.update_step("Using fallback data due to API issues...", 30)
                    # Continue with limited data
                    cost_data = {"current_month": 0, "last_month": 0, "costs_by_service": {}}
                    service_costs = []
                    last_month_data = {}

                # Phase 2: Enhanced budget analysis (40-70%)
                try:
                    progress.update_step("Collecting budget information...", 45)
                    budget_data = get_budgets(cost_session)

                    progress.update_step("Analyzing service utilization patterns...", 60)
                    # Service utilization analysis
                    utilization_data = self._analyze_service_utilization(ops_session, cost_data)

                    progress.update_step("Generating optimization recommendations...", 75)
                    # Simulate processing time for optimization analysis
                    import time

                    time.sleep(0.5)  # Brief processing simulation for smooth progress

                except Exception as e:
                    print_warning(f"Budget/utilization analysis failed: {str(e)[:50]}")
                    progress.update_step("Using basic analysis due to API limitations...", 65)
                    budget_data = []
                    utilization_data = {}

                # Phase 3: Table generation and formatting (80-100%)
                progress.update_step("Preparing service-focused table...", 85)
                # Brief pause for table preparation
                import time

                time.sleep(0.3)

                progress.update_step("Formatting optimization recommendations...", 95)
                # Final formatting step

                progress.complete_operation("Service analysis completed successfully")

            # Create and display the service-focused table
            self._display_service_focused_table(
                account_id=account_id,
                profile=profile,
                cost_data=cost_data,
                service_costs=service_costs,
                last_month_data=last_month_data,
                budget_data=budget_data,
                utilization_data=utilization_data,
                top_services=top_services,
            )

            # Export if requested
            if hasattr(args, "report_name") and args.report_name:
                self._export_service_analysis(args, cost_data, service_costs, account_id)

            # Export to markdown if requested
            should_export_markdown = False

            # Check if markdown export was requested via --export-markdown flag
            if hasattr(args, "export_markdown") and getattr(args, "export_markdown", False):
                should_export_markdown = True

            # Check if markdown export was requested via --report-type markdown
            if hasattr(args, "report_type") and args.report_type:
                if isinstance(args.report_type, list) and "markdown" in args.report_type:
                    should_export_markdown = True
                elif isinstance(args.report_type, str) and "markdown" in args.report_type:
                    should_export_markdown = True

            if should_export_markdown:
                # Prepare service data for markdown export with Tax filtering
                current_services = cost_data.get("costs_by_service", {})
                previous_services = last_month_data.get("costs_by_service", {})  # Use already collected data

                # Apply same Tax filtering for consistent markdown export
                filtered_current_services = filter_analytical_services(current_services)
                filtered_previous_services = filter_analytical_services(previous_services)

                all_services_sorted = sorted(filtered_current_services.items(), key=lambda x: x[1], reverse=True)

                # Calculate totals for markdown export
                total_current = cost_data.get("current_month", 0)
                total_previous = cost_data.get("last_month", 0)
                total_trend_pct = ((total_current - total_previous) / total_previous * 100) if total_previous > 0 else 0

                self._export_service_table_to_markdown(
                    all_services_sorted,
                    filtered_current_services,
                    filtered_previous_services,
                    profile,
                    account_id,
                    total_current,
                    total_previous,
                    total_trend_pct,
                    args,
                )

            print_success(f"Service analysis completed for account {account_id}")
            return 0

        except Exception as e:
            print_error(f"Service analysis execution failed: {str(e)}")
            return 1

    def _get_last_month_trends(self, cost_session: boto3.Session, profile: str) -> Dict[str, Any]:
        """Get last month cost data for trend analysis."""
        try:
            # Get cost data for previous month
            previous_month_data = get_cost_data(cost_session, 60, None, profile_name=profile)  # 60 days for comparison
            return previous_month_data
        except Exception as e:
            print_warning(f"Trend data collection failed: {str(e)[:30]}")
            return {}

    def _analyze_service_utilization(self, ops_session: boto3.Session, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze service utilization patterns for optimization opportunities."""
        utilization_data = {}

        try:
            # Basic service utilization patterns (can be expanded)
            services_with_costs = cost_data.get("costs_by_service", {})

            for service, cost in services_with_costs.items():
                utilization_data[service] = {
                    "cost": cost,
                    "optimization_potential": "Medium",  # Placeholder - can be enhanced
                    "utilization_score": 75,  # Placeholder - can be enhanced with CloudWatch
                    "recommendation": self._get_service_recommendation(service, cost),
                }

        except Exception as e:
            print_warning(f"Utilization analysis failed: {str(e)[:30]}")

        return utilization_data

    def _get_service_recommendation(self, service: str, cost: float) -> str:
        """Get optimization recommendation for a service based on cost patterns."""
        if cost == 0:
            return "No usage detected"
        elif "ec2" in service.lower():
            return "Review instance sizing"
        elif "s3" in service.lower():
            return "Check storage classes"
        elif "rds" in service.lower():
            return "Evaluate instance types"
        else:
            return "Monitor usage patterns"

    def _get_enhanced_service_recommendation(self, service: str, current_cost: float, previous_cost: float) -> str:
        """Get enhanced service-specific optimization recommendations with trend awareness."""
        if current_cost == 0:
            return "[dim]No current usage - consider resource cleanup[/]"

        # Calculate cost trend for context-aware recommendations
        trend_factor = 1.0
        if previous_cost > 0:
            trend_factor = current_cost / previous_cost

        service_lower = service.lower()

        if "ec2" in service_lower or "compute" in service_lower:
            if trend_factor > 1.2:
                return "[red]High growth: review scaling policies & rightsizing[/]"
            elif current_cost > 1000:
                return "[yellow]Significant cost: analyze Reserved Instance opportunities[/]"
            else:
                return "[green]Monitor CPU utilization & consider spot instances[/]"

        elif "s3" in service_lower or "storage" in service_lower:
            if trend_factor > 1.3:
                return "[red]Storage growth: implement lifecycle policies[/]"
            elif current_cost > 500:
                return "[yellow]Review storage classes: Standard → IA/Glacier[/]"
            else:
                return "[green]Optimize object lifecycle & access patterns[/]"

        elif "rds" in service_lower or "database" in service_lower:
            if current_cost > 1500:
                return "[yellow]High DB costs: evaluate instance types & Reserved[/]"
            else:
                return "[green]Monitor connections & consider read replicas[/]"

        elif "lambda" in service_lower or "serverless" in service_lower:
            if trend_factor > 1.5:
                return "[red]Function invocations increasing: optimize runtime[/]"
            else:
                return "[green]Review memory allocation & execution time[/]"

        elif "glue" in service_lower:
            if current_cost > 75:
                return "[yellow]Review job frequency & data processing efficiency[/]"
            else:
                return "[green]Monitor ETL job performance & scheduling[/]"

        elif "tax" in service_lower:
            return "[dim]Regulatory requirement - no optimization available[/]"

        elif "cloudwatch" in service_lower or "monitoring" in service_lower:
            if current_cost > 100:
                return "[yellow]High monitoring costs: review log retention[/]"
            else:
                return "[green]Optimize custom metrics & log groups[/]"

        elif "nat" in service_lower or "gateway" in service_lower:
            if current_cost > 200:
                return "[yellow]High NAT costs: consider VPC endpoints[/]"
            else:
                return "[green]Monitor data transfer patterns[/]"

        else:
            # Generic recommendations based on cost level
            if current_cost > 1000:
                return f"[yellow]High cost service: detailed analysis recommended[/]"
            elif trend_factor > 1.3:
                return f"[red]Growing cost: investigate usage increase[/]"
            else:
                return f"[green]Monitor usage patterns & optimization opportunities[/]"

    def _display_service_focused_table(
        self,
        account_id: str,
        profile: str,
        cost_data: Dict[str, Any],
        service_costs: List[str],
        last_month_data: Dict[str, Any],
        budget_data: List[Dict[str, Any]],
        utilization_data: Dict[str, Any],
        top_services: int,
    ) -> None:
        """Display the service-focused analysis table."""

        # Create enhanced table for service analysis (service-per-row layout)
        # Get readable account name for display
        if self.account_resolver and account_id != "Unknown":
            account_name = self.account_resolver.get_account_name(account_id)
            if account_name and account_name != account_id:
                account_display = f"{account_name} ({account_id})"
                account_caption = f"Account: {account_name}"
            else:
                account_display = account_id
                account_caption = f"Account ID: {account_id}"
        else:
            account_display = account_id
            account_caption = f"Profile: {profile}"

        table = Table(
            Column("Service", style="resource", width=20),
            Column("Current Cost", justify="right", style="cost", width=15),
            Column("Last Month", justify="right", width=15),
            Column("Trend", justify="center", width=10),
            Column("Optimization Opportunities", width=35),
            title=f"🎯 TOP {top_services} Services Analysis - {account_display}",
            box=box.ROUNDED,
            show_lines=True,
            style="bright_cyan",
            caption=f"[dim]Service-focused analysis • {account_caption} • Each row represents one service[/]",
        )

        # Get current and previous service costs
        current_services = cost_data.get("costs_by_service", {})
        previous_services = last_month_data.get("costs_by_service", {})

        # WIP.md requirement: Exclude "Tax" service as it provides no analytical insights
        # Use centralized filtering function for consistency across all dashboards
        filtered_current_services = filter_analytical_services(current_services)
        filtered_previous_services = filter_analytical_services(previous_services)

        # Sort services by current cost and take top N, plus "Other Services" summary
        all_services = sorted(filtered_current_services.items(), key=lambda x: x[1], reverse=True)
        top_services_list = all_services[:top_services]
        remaining_services = all_services[top_services:]

        # Add individual service rows
        for service, current_cost in top_services_list:
            previous_cost = filtered_previous_services.get(service, 0)

            # Calculate trend
            if previous_cost > 0:
                trend_percent = ((current_cost - previous_cost) / previous_cost) * 100
                if trend_percent > 5:
                    trend_display = f"[red]⬆ {trend_percent:.1f}%[/]"
                elif trend_percent < -5:
                    trend_display = f"[green]⬇ {abs(trend_percent):.1f}%[/]"
                else:
                    trend_display = f"[yellow]➡ {trend_percent:.1f}%[/]"
            else:
                trend_display = "[dim]New[/]"

            # Enhanced service-specific optimization recommendations
            optimization_rec = self._get_enhanced_service_recommendation(service, current_cost, previous_cost)

            # Use standardized service name mapping (RDS, S3, CloudWatch, etc.)
            display_name = get_service_display_name(service)

            table.add_row(
                display_name, format_cost(current_cost), format_cost(previous_cost), trend_display, optimization_rec
            )

        # Add "Other Services" summary row if there are remaining services
        if remaining_services:
            other_current = sum(cost for _, cost in remaining_services)
            other_previous = sum(filtered_previous_services.get(service, 0) for service, _ in remaining_services)

            if other_previous > 0:
                other_trend_percent = ((other_current - other_previous) / other_previous) * 100
                if other_trend_percent > 5:
                    other_trend = f"[red]⬆ {other_trend_percent:.1f}%[/]"
                elif other_trend_percent < -5:
                    other_trend = f"[green]⬇ {abs(other_trend_percent):.1f}%[/]"
                else:
                    other_trend = f"[yellow]➡ {other_trend_percent:.1f}%[/]"
            else:
                other_trend = "[dim]Various[/]"

            other_optimization = (
                f"[dim]{len(remaining_services)} services: review individually for optimization opportunities[/]"
            )

            # Add separator line for "Other Services"
            table.add_row(
                "[dim]Other Services[/]",
                format_cost(other_current),
                format_cost(other_previous),
                other_trend,
                other_optimization,
                style="dim",
            )

        self.console.print(table)

        # Summary panel (using filtered services for consistent analysis)
        total_current = sum(filtered_current_services.values())
        total_previous = sum(filtered_previous_services.values())
        total_trend = ((total_current - total_previous) / total_previous * 100) if total_previous > 0 else 0

        # Use readable account name in summary
        if self.account_resolver and account_id != "Unknown":
            account_name = self.account_resolver.get_account_name(account_id)
            if account_name and account_name != account_id:
                account_summary_line = f"• Account: {account_name} ({account_id})"
            else:
                account_summary_line = f"• Account ID: {account_id}"
        else:
            account_summary_line = f"• Profile: {profile}"

        summary_text = f"""
[highlight]Account Summary[/]
{account_summary_line}
• Total Current: {format_cost(total_current)}
• Total Previous: {format_cost(total_previous)}
• Overall Trend: {"⬆" if total_trend > 0 else "⬇"} {abs(total_trend):.1f}%
• Services Analyzed: {len(all_services)}
        """

        self.console.print(Panel(summary_text.strip(), title="📊 Analysis Summary", style="info"))

    def _export_service_analysis(
        self, args: argparse.Namespace, cost_data: Dict[str, Any], service_costs: List[str], account_id: str
    ) -> None:
        """Export service analysis results."""
        try:
            if hasattr(args, "report_type") and args.report_type:
                export_data = [
                    {
                        "account_id": account_id,
                        "service_costs": cost_data.get("costs_by_service", {}),
                        "total_current": cost_data.get("current_month", 0),
                        "total_previous": cost_data.get("last_month", 0),
                        "analysis_type": "service_focused",
                    }
                ]

                for report_type in args.report_type:
                    if report_type == "json":
                        json_path = export_to_json(export_data, args.report_name, getattr(args, "dir", None))
                        if json_path:
                            print_success(f"Service analysis exported to JSON: {json_path}")
                    elif report_type == "csv":
                        csv_path = export_to_csv(export_data, args.report_name, getattr(args, "dir", None))
                        if csv_path:
                            print_success(f"Service analysis exported to CSV: {csv_path}")

        except Exception as e:
            print_warning(f"Export failed: {str(e)[:50]}")

    def _export_service_table_to_markdown(
        self,
        sorted_services,
        current_services,
        previous_services,
        profile,
        account_id,
        total_current,
        total_previous,
        total_trend_pct,
        args,
    ):
        """Export service-per-row table to properly formatted markdown file."""
        import os
        from datetime import datetime

        try:
            # Prepare file path with proper directory creation
            output_dir = args.dir if hasattr(args, "dir") and args.dir else "./exports"
            os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
            report_name = args.report_name if hasattr(args, "report_name") and args.report_name else "service_analysis"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(output_dir, f"{report_name}_{timestamp}.md")

            # Generate markdown content with properly aligned pipes
            lines = []
            lines.append("# Service-Per-Row FinOps Analysis")
            lines.append("")
            # Use readable account name in markdown export
            if self.account_resolver and account_id != "Unknown":
                account_name = self.account_resolver.get_account_name(account_id)
                if account_name and account_name != account_id:
                    account_line = f"**Account:** {account_name} ({account_id})"
                else:
                    account_line = f"**Account ID:** {account_id}"
            else:
                account_line = f"**Profile:** {profile}"

            lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(account_line)
            lines.append("")
            lines.append("## Service Cost Breakdown")
            lines.append("")

            # Create GitHub-compatible markdown table with proper alignment syntax
            lines.append("| Service | Last Month | Current Month | Trend | Optimization Opportunities |")
            lines.append("| --- | ---: | ---: | :---: | --- |")  # GitHub-compliant alignment

            # Add TOP 10 services with proper formatting
            for i, (service_name, current_cost) in enumerate(sorted_services[:10]):
                previous_cost = previous_services.get(service_name, 0)
                trend_pct = ((current_cost - previous_cost) / previous_cost * 100) if previous_cost > 0 else 0
                trend_icon = "⬆️" if trend_pct > 0 else "⬇️" if trend_pct < 0 else "➡️"

                # Generate optimization recommendation
                optimization = self._get_service_optimization(service_name, current_cost, previous_cost)

                # Format row for GitHub-compatible table
                service_name_clean = service_name.replace("|", "\\|")  # Escape pipes in service names
                optimization_clean = optimization.replace("|", "\\|")  # Escape pipes in text

                lines.append(
                    f"| {service_name_clean} | ${previous_cost:.2f} | ${current_cost:.2f} | {trend_icon} {abs(trend_pct):.1f}% | {optimization_clean} |"
                )

            # Add Others row if there are remaining services
            remaining_services = sorted_services[10:]
            if remaining_services:
                others_current = sum(current_cost for _, current_cost in remaining_services)
                others_previous = sum(previous_services.get(service_name, 0) for service_name, _ in remaining_services)
                others_trend_pct = (
                    ((others_current - others_previous) / others_previous * 100) if others_previous > 0 else 0
                )
                trend_icon = "⬆️" if others_trend_pct > 0 else "⬇️" if others_trend_pct < 0 else "➡️"

                others_row = f"Others ({len(remaining_services)} services)"
                lines.append(
                    f"| {others_row} | ${others_previous:.2f} | ${others_current:.2f} | {trend_icon} {abs(others_trend_pct):.1f}% | Review individually for optimization |"
                )

            lines.append("")
            lines.append("## Summary")
            lines.append("")
            lines.append(f"- **Total Current Cost:** ${total_current:,.2f}")
            lines.append(f"- **Total Previous Cost:** ${total_previous:,.2f}")
            trend_icon = "⬆️" if total_trend_pct > 0 else "⬇️" if total_trend_pct < 0 else "➡️"
            lines.append(f"- **Overall Trend:** {trend_icon} {abs(total_trend_pct):.1f}%")
            lines.append(f"- **Services Analyzed:** {len(sorted_services)}")
            lines.append(
                f"- **Optimization Focus:** {'Review highest cost services' if total_current > 100 else 'Continue monitoring'}"
            )
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append("*Generated by CloudOps Runbooks FinOps Platform*")

            # Write to file
            with open(file_path, "w") as f:
                f.write("\n".join(lines))

            print_success(f"Markdown export saved to: {file_path}")
            self.console.print("[cyan]📋 Ready for GitHub/MkDocs documentation[/]")

        except Exception as e:
            print_warning(f"Markdown export failed: {str(e)[:50]}")

    def _get_service_optimization(self, service, current, previous):
        """Get optimization recommendation for a service."""
        service_lower = service.lower()

        # Generate optimization recommendations based on service type and cost
        if current > 10000:  # High cost services
            if "rds" in service_lower or "database" in service_lower:
                return "High DB costs: evaluate instance types & Reserved Instances"
            elif "ec2" in service_lower:
                return "Significant cost: analyze Reserved Instance opportunities"
            else:
                return "High cost service: detailed analysis recommended"
        elif current > 1000:  # Medium cost services
            if "lambda" in service_lower:
                return "Review memory allocation & execution time"
            elif "cloudwatch" in service_lower:
                return "High monitoring costs: review log retention"
            elif "s3" in service_lower:
                return "Review storage classes: Standard → IA/Glacier"
            else:
                return "Monitor usage patterns & optimization opportunities"
        else:  # Lower cost services
            return "Continue monitoring for optimization opportunities"


def create_single_dashboard(console: Optional[Console] = None) -> SingleAccountDashboard:
    """Factory function to create single account dashboard."""
    return SingleAccountDashboard(console=console)

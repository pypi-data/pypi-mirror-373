"""
Rich Formatters - Beautiful console output formatting for VPC operations

This module provides consistent, beautiful formatting using the Rich library
for both CLI and Jupyter notebook environments.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


def display_cost_table(console: Console, data: Dict[str, Any], title: str = "Cost Analysis"):
    """
    Display cost data in a beautiful table format

    Args:
        console: Rich console instance
        data: Cost data to display
        title: Table title
    """
    table = Table(title=title, show_header=True, header_style="bold magenta", box=box.ROUNDED)

    # Determine columns based on data
    if "nat_gateways" in data:
        table.add_column("Resource", style="cyan")
        table.add_column("ID", style="yellow")
        table.add_column("State", style="green")
        table.add_column("Monthly Cost", justify="right", style="red")
        table.add_column("Optimization", style="magenta")

        for ng in data["nat_gateways"]:
            table.add_row(
                "NAT Gateway",
                ng["id"][-12:],  # Show last 12 chars
                ng.get("state", "active"),
                f"${ng.get('monthly_cost', 0):.2f}",
                ng.get("optimization", {}).get("recommendation", "Optimized"),
            )

    elif "vpc_endpoints" in data:
        table.add_column("Endpoint ID", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Service", style="green")
        table.add_column("Monthly Cost", justify="right", style="red")

        for endpoint in data["vpc_endpoints"]:
            service = endpoint["service"].split(".")[-1] if "." in endpoint["service"] else endpoint["service"]
            table.add_row(endpoint["id"][-12:], endpoint["type"], service, f"${endpoint.get('monthly_cost', 0):.2f}")

    else:
        # Generic cost table
        table.add_column("Item", style="cyan")
        table.add_column("Value", justify="right", style="yellow")

        for key, value in data.items():
            if isinstance(value, (int, float)):
                if "cost" in key.lower():
                    table.add_row(key.replace("_", " ").title(), f"${value:.2f}")
                else:
                    table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)


def display_heatmap(console: Console, heat_maps: Dict[str, Any]):
    """
    Display heat map data with visual representation

    Args:
        console: Rich console instance
        heat_maps: Heat map data to display
    """
    # Display single account heat map
    if "single_account_heat_map" in heat_maps:
        single = heat_maps["single_account_heat_map"]

        # Create a visual heat map using colored blocks
        console.print(
            Panel.fit(
                f"[bold cyan]Single Account Heat Map[/bold cyan]\n"
                f"Account: {single.get('account_id', 'N/A')}\n"
                f"Total Monthly Cost: [bold red]${single.get('total_monthly_cost', 0):.2f}[/bold red]",
                title="🔥 Cost Heat Map",
                border_style="blue",
            )
        )

        # Display regional distribution
        if "cost_distribution" in single:
            regional_table = Table(title="Regional Cost Distribution", box=box.SIMPLE)
            regional_table.add_column("Region", style="cyan")
            regional_table.add_column("Cost", justify="right", style="yellow")
            regional_table.add_column("Heat Level", style="red")

            regional_totals = single["cost_distribution"].get("regional_totals", [])
            regions = single.get("regions", [])

            for idx, (region, cost) in enumerate(zip(regions, regional_totals)):
                heat_level = _get_heat_level(cost)
                regional_table.add_row(region, f"${cost:.2f}", heat_level)

            console.print(regional_table)

    # Display multi-account aggregation
    if "multi_account_aggregated" in heat_maps:
        multi = heat_maps["multi_account_aggregated"]

        console.print(
            Panel.fit(
                f"[bold cyan]Multi-Account Heat Map[/bold cyan]\n"
                f"Total Accounts: {multi.get('total_accounts', 0)}\n"
                f"Total Monthly Cost: [bold red]${multi.get('total_monthly_cost', 0):.2f}[/bold red]\n"
                f"Average per Account: [bold yellow]${multi.get('average_account_cost', 0):.2f}[/bold yellow]",
                title="🔥 Aggregated Heat Map",
                border_style="blue",
            )
        )

        # Display hotspots
        if "cost_hotspots" in multi and multi["cost_hotspots"]:
            hotspot_table = Table(title="Cost Hotspots", box=box.SIMPLE)
            hotspot_table.add_column("Region", style="cyan")
            hotspot_table.add_column("Service", style="yellow")
            hotspot_table.add_column("Cost", justify="right", style="red")
            hotspot_table.add_column("Severity", style="magenta")

            for hotspot in multi["cost_hotspots"][:10]:  # Top 10
                hotspot_table.add_row(
                    hotspot["region"], hotspot["service"], f"${hotspot['monthly_cost']:.2f}", hotspot["severity"]
                )

            console.print(hotspot_table)

    # Display time series trends
    if "time_series_heat_maps" in heat_maps:
        time_series = heat_maps["time_series_heat_maps"]
        if "trend_analysis" in time_series:
            trend = time_series["trend_analysis"]
            console.print(
                Panel(
                    f"Growth Rate: [bold yellow]{trend.get('growth_rate', 0)}%[/bold yellow]\n"
                    f"Patterns: {trend.get('seasonal_patterns', 'None')}\n"
                    f"Opportunities: {trend.get('optimization_opportunities', 'None')}",
                    title="📈 Trend Analysis",
                    border_style="green",
                )
            )


def display_optimization_recommendations(console: Console, recommendations: Dict[str, Any]):
    """
    Display optimization recommendations with visual impact

    Args:
        console: Rich console instance
        recommendations: Optimization recommendations data
    """
    # Display summary panel
    current = recommendations.get("current_monthly_cost", 0)
    projected = recommendations.get("projected_monthly_cost", 0)
    savings = recommendations.get("potential_savings", 0)
    target = recommendations.get("target_reduction", 0)

    summary_text = f"""
[bold cyan]Cost Optimization Summary[/bold cyan]

Current Monthly Cost: [bold red]${current:.2f}[/bold red]
Potential Savings: [bold green]${savings:.2f}[/bold green]
Projected Cost: [bold yellow]${projected:.2f}[/bold yellow]
Target Reduction: [bold magenta]{target}%[/bold magenta]

Savings Percentage: [bold green]{(savings / current * 100 if current > 0 else 0):.1f}%[/bold green]
Annual Savings: [bold green]${savings * 12:.2f}[/bold green]
    """

    console.print(Panel(summary_text.strip(), title="💰 Optimization Summary", border_style="green"))

    # Display recommendations table
    if "recommendations" in recommendations and recommendations["recommendations"]:
        rec_table = Table(title="Optimization Recommendations", show_header=True, box=box.ROUNDED)
        rec_table.add_column("Priority", style="cyan")
        rec_table.add_column("Resource", style="yellow")
        rec_table.add_column("Action", style="green")
        rec_table.add_column("Savings", justify="right", style="red")
        rec_table.add_column("Risk", style="magenta")
        rec_table.add_column("Effort", style="blue")

        for idx, rec in enumerate(recommendations["recommendations"][:10], 1):
            rec_table.add_row(
                str(idx),
                rec.get("resource_id", "N/A")[-12:],
                rec.get("action", "N/A"),
                f"${rec.get('potential_savings', 0):.2f}",
                rec.get("risk_level", "medium"),
                rec.get("implementation_effort", "medium"),
            )

        console.print(rec_table)

    # Display implementation plan
    if "implementation_plan" in recommendations and recommendations["implementation_plan"]:
        plan_tree = Tree("📋 Implementation Plan")

        current_phase = None
        phase_branch = None

        for item in recommendations["implementation_plan"][:15]:  # First 15 items
            phase = item.get("phase", 1)

            if phase != current_phase:
                phase_branch = plan_tree.add(f"[bold cyan]Phase {phase}[/bold cyan]")
                current_phase = phase

            if phase_branch:
                phase_branch.add(
                    f"{item.get('action', 'N/A')} - "
                    f"[green]${item.get('savings', 0):.2f}[/green] - "
                    f"[yellow]{item.get('risk', 'medium')} risk[/yellow]"
                )

        console.print(plan_tree)


def display_progress(console: Console, title: str, total: int, current: int):
    """
    Display a progress bar for long-running operations

    Args:
        console: Rich console instance
        title: Progress bar title
        total: Total items
        current: Current item count
    """
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task(title, total=total)
        progress.update(task, advance=current)


def display_multi_account_progress(console: Console, accounts: List[str]) -> Progress:
    """
    Create multi-task progress bar for concurrent account analysis

    Args:
        console: Rich console instance
        accounts: List of AWS account IDs

    Returns:
        Progress instance with tasks for each account
    """
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("[blue]{task.completed}/{task.total} accounts"),
        console=console,
    )

    # Add tasks for different analysis phases
    progress.add_task("🔍 Discovery", total=len(accounts))
    progress.add_task("💰 Cost Analysis", total=len(accounts))
    progress.add_task("🔥 Heat Maps", total=len(accounts))

    return progress


def display_transit_gateway_architecture(console: Console, tgw_data: Dict[str, Any]):
    """
    Display Transit Gateway architecture as Rich Tree for Issue #97

    Args:
        console: Rich console instance
        tgw_data: Transit Gateway architecture data
    """
    tgw_tree = Tree("🌐 [bold cyan]AWS Transit Gateway Architecture[/bold cyan]")

    # Central Egress VPC
    central_vpc_id = tgw_data.get("central_vpc_id", "vpc-central")
    central_vpc = tgw_tree.add(f"🏢 [yellow]Central Egress VPC[/yellow] ({central_vpc_id})")

    # Add Transit Gateway details
    tgw_id = tgw_data.get("transit_gateway_id", "tgw-central")
    tgw_branch = central_vpc.add(f"🔗 [magenta]Transit Gateway[/magenta] ({tgw_id})")

    # Organizational Units
    for ou in tgw_data.get("organizational_units", []):
        ou_branch = tgw_tree.add(f"🏗️ [green]OU: {ou.get('name', 'Unknown')}[/green]")

        # Accounts within OU
        for account in ou.get("accounts", []):
            account_id = account.get("id", "unknown")
            account_branch = ou_branch.add(f"📊 [cyan]Account: {account_id}[/cyan]")

            # VPCs in account
            for vpc in account.get("vpcs", []):
                vpc_id = vpc.get("id", "vpc-unknown")
                monthly_cost = vpc.get("monthly_cost", 0)
                vpc_branch = account_branch.add(f"🌐 VPC: {vpc_id} - [red]${monthly_cost:.2f}[/red]/month")

                # VPC Endpoints
                for endpoint in vpc.get("endpoints", []):
                    endpoint_service = endpoint.get("service", "Unknown")
                    endpoint_type = endpoint.get("type", "Interface")
                    vpc_branch.add(f"🔗 {endpoint_service} - [yellow]{endpoint_type}[/yellow]")

                # NAT Gateways
                for nat in vpc.get("nat_gateways", []):
                    nat_id = nat.get("id", "nat-unknown")
                    nat_cost = nat.get("monthly_cost", 0)
                    vpc_branch.add(f"🚪 NAT Gateway: {nat_id} - [red]${nat_cost:.2f}[/red]/month")

    console.print(tgw_tree)


def display_error(console: Console, error_message: str, suggestion: Optional[str] = None):
    """
    Display an error message with optional suggestion

    Args:
        console: Rich console instance
        error_message: Error message to display
        suggestion: Optional suggestion for resolution
    """
    error_panel = f"[bold red]❌ Error[/bold red]\n\n{error_message}"

    if suggestion:
        error_panel += f"\n\n[yellow]💡 Suggestion:[/yellow] {suggestion}"

    console.print(Panel(error_panel, border_style="red", box=box.DOUBLE))


def display_success(console: Console, message: str, details: Optional[Dict] = None):
    """
    Display a success message with optional details

    Args:
        console: Rich console instance
        message: Success message
        details: Optional details dictionary
    """
    success_text = f"[bold green]✅ Success[/bold green]\n\n{message}"

    if details:
        success_text += "\n\n[cyan]Details:[/cyan]\n"
        for key, value in details.items():
            success_text += f"  • {key}: {value}\n"

    console.print(Panel(success_text, border_style="green"))


def format_currency(value: float) -> str:
    """Format a value as currency"""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format a value as percentage"""
    return f"{value:.1f}%"


def display_optimized_cost_table(console: Console, data: Dict[str, Any], sort_by: str = "monthly_cost"):
    """
    Display cost table with advanced optimization features

    Args:
        console: Rich console instance
        data: Cost data with optimization recommendations
        sort_by: Column to sort by (monthly_cost, potential_savings, risk_level)
    """
    table = Table(
        title="💰 [bold cyan]Cost Optimization Analysis[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
    )

    # Enhanced columns with sorting indicators
    table.add_column("Resource", style="cyan")
    table.add_column("ID", style="yellow")
    table.add_column("Monthly Cost ⬇️", justify="right", style="red")
    table.add_column("Potential Savings", justify="right", style="green")
    table.add_column("Optimization Priority", style="magenta")
    table.add_column("Risk Level", style="blue")

    # Sort data by specified column
    if "nat_gateways" in data:
        sorted_items = sorted(data["nat_gateways"], key=lambda x: x.get(sort_by, 0), reverse=True)

        for ng in sorted_items:
            # Color-coded priority indicators
            priority = _get_optimization_priority(ng)
            risk_indicator = _get_risk_indicator(ng.get("optimization", {}).get("risk_level", "medium"))

            table.add_row(
                "NAT Gateway",
                ng["id"][-12:],
                f"${ng.get('monthly_cost', 0):.2f}",
                f"${ng.get('optimization', {}).get('potential_savings', 0):.2f}",
                priority,
                risk_indicator,
            )

    elif "vpc_endpoints" in data:
        sorted_items = sorted(data["vpc_endpoints"], key=lambda x: x.get(sort_by, 0), reverse=True)

        for endpoint in sorted_items:
            priority = _get_optimization_priority(endpoint)
            risk_indicator = _get_risk_indicator(endpoint.get("optimization", {}).get("risk_level", "low"))

            # Shorten service name for display
            service = (
                endpoint["service"].split(".")[-1]
                if "." in endpoint.get("service", "")
                else endpoint.get("service", "Unknown")
            )

            table.add_row(
                f"VPC Endpoint ({endpoint.get('type', 'Interface')})",
                endpoint["id"][-12:],
                f"${endpoint.get('monthly_cost', 0):.2f}",
                f"${endpoint.get('optimization', {}).get('potential_savings', 0):.2f}",
                priority,
                risk_indicator,
            )

    console.print(table)


def _get_optimization_priority(resource: Dict) -> str:
    """Get color-coded optimization priority"""
    savings = resource.get("optimization", {}).get("potential_savings", 0)
    if savings > 40:
        return "[bold red]🔥 CRITICAL[/bold red]"
    elif savings > 20:
        return "[red]⚠️ HIGH[/red]"
    elif savings > 10:
        return "[yellow]📈 MEDIUM[/yellow]"
    else:
        return "[green]✅ LOW[/green]"


def _get_risk_indicator(risk_level: str) -> str:
    """Get color-coded risk indicator"""
    risk_colors = {
        "high": "[bold red]🔴 HIGH[/bold red]",
        "medium": "[yellow]🟡 MEDIUM[/yellow]",
        "low": "[green]🟢 LOW[/green]",
    }
    return risk_colors.get(risk_level.lower(), "[yellow]🟡 MEDIUM[/yellow]")


def _get_heat_level(cost: float) -> str:
    """
    Get heat level indicator based on cost

    Args:
        cost: Cost value

    Returns:
        Heat level string with color
    """
    if cost > 500:
        return "[bold red]🔥🔥🔥 CRITICAL[/bold red]"
    elif cost > 100:
        return "[red]🔥🔥 HIGH[/red]"
    elif cost > 50:
        return "[yellow]🔥 MEDIUM[/yellow]"
    elif cost > 10:
        return "[green]• LOW[/green]"
    else:
        return "[dim]○ MINIMAL[/dim]"


def create_summary_layout(data: Dict[str, Any]) -> Layout:
    """
    Create a summary layout for comprehensive display

    Args:
        data: Summary data to display

    Returns:
        Rich Layout object
    """
    layout = Layout()

    # Create main sections
    layout.split_column(Layout(name="header", size=3), Layout(name="body"), Layout(name="footer", size=3))

    # Header
    layout["header"].update(Panel("[bold cyan]VPC Networking Cost Analysis[/bold cyan]", style="blue"))

    # Body split into columns
    layout["body"].split_row(Layout(name="costs"), Layout(name="recommendations"))

    # Footer
    layout["footer"].update(Panel(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim"))

    return layout


def display_transit_gateway_analysis(results: Dict[str, Any], console: Console) -> None:
    """
    Display comprehensive Transit Gateway analysis results with Rich formatting.

    Enhanced for Issue #97: Strategic executive reporting with $325+/month savings focus
    and business impact visualization for 60-account enterprise environment.
    """

    # Executive header with business impact
    console.print("\n🎯 Enterprise Transit Gateway Strategic Analysis", style="bold bright_blue")
    console.print("Issue #97: Multi-Account Cost Optimization Campaign", style="dim italic")
    console.print("=" * 85, style="dim")

    # Executive Business Impact Panel (TOP PRIORITY)
    cost_analysis = results.get("cost_analysis", {})
    business_impact = cost_analysis.get("business_impact", {})

    if business_impact:
        executive_panel = Panel(
            f"💰 Monthly Savings: [bold green]${business_impact.get('monthly_savings', 0):.0f}[/bold green]\n"
            f"📊 Annual Impact: [bold cyan]${business_impact.get('annual_savings', 0):,.0f}[/bold cyan]\n"
            f"🎯 Target Achievement: [bold yellow]{business_impact.get('target_achievement', 'N/A')}[/bold yellow]\n"
            f"⭐ ROI Grade: [bold magenta]{business_impact.get('roi_grade', 'UNKNOWN')}[/bold magenta]\n"
            f"📋 {business_impact.get('executive_summary', 'Analysis pending')}",
            title="🎯 Executive Business Impact",
            border_style="green" if business_impact.get("roi_grade") == "EXCEEDS TARGET" else "yellow",
        )
        console.print(executive_panel)

    # Enhanced summary metrics table with optimization focus
    summary_table = Table(title="📊 Strategic Analysis Dashboard", show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", style="cyan", no_wrap=True)
    summary_table.add_column("Current State", style="green")
    summary_table.add_column("Optimization Target", style="yellow")
    summary_table.add_column("Business Value", style="bold green")

    tgw_count = len(results.get("transit_gateways", []))
    attachment_count = len(results.get("attachments", []))
    route_table_count = len(results.get("route_tables", []))

    total_cost = cost_analysis.get("total_monthly_cost", 0)
    savings_potential = cost_analysis.get("savings_potential", 0)

    summary_table.add_row("Transit Gateways", str(tgw_count), "Optimized topology", f"Architecture review")
    summary_table.add_row(
        "Attachments", str(attachment_count), f"{attachment_count * 0.85:.0f} (15% reduction)", "Remove underutilized"
    )
    summary_table.add_row(
        "Route Tables",
        str(route_table_count),
        f"{route_table_count * 0.75:.0f} (25% consolidation)",
        "Streamlined routing",
    )
    summary_table.add_row(
        "Monthly Cost",
        f"${total_cost:.2f}",
        f"${total_cost - savings_potential:.2f}",
        f"-${savings_potential:.0f}/month",
    )
    summary_table.add_row(
        "Annual Savings", "Current baseline", f"${savings_potential * 12:,.0f}/year", "Target: $325+/month"
    )

    console.print(summary_table)

    # Transit Gateway details
    if results.get("transit_gateways"):
        tgw_table = Table(title="🌉 Transit Gateway Details", show_header=True, header_style="bold blue")
        tgw_table.add_column("ID", style="cyan")
        tgw_table.add_column("State", style="green")
        tgw_table.add_column("Owner", style="yellow")
        tgw_table.add_column("ASN", style="magenta")
        tgw_table.add_column("Description", style="white")

        for tgw in results["transit_gateways"]:
            tgw_table.add_row(
                tgw.get("TransitGatewayId", "")[:20],
                tgw.get("State", ""),
                tgw.get("OwnerId", "")[:12],
                str(tgw.get("AmazonSideAsn", "")),
                tgw.get("Description", "No description")[:30],
            )

        console.print(tgw_table)

    # Central Egress VPC information
    if results.get("central_egress_vpc"):
        egress_vpc = results["central_egress_vpc"]
        egress_panel = Panel(
            f"[bold green]VPC ID:[/bold green] {egress_vpc.get('VpcId', 'N/A')}\n"
            f"[bold green]Name:[/bold green] {egress_vpc.get('VpcName', 'N/A')}\n"
            f"[bold green]CIDR:[/bold green] {egress_vpc.get('CidrBlock', 'N/A')}\n"
            f"[bold green]Transit Gateway:[/bold green] {egress_vpc.get('TransitGatewayId', 'N/A')}",
            title="🏗️ Central Egress VPC",
            border_style="green",
        )
        console.print(egress_panel)

    # Cost breakdown
    cost_analysis = results.get("cost_analysis", {})
    if cost_analysis.get("cost_breakdown"):
        cost_table = Table(title="💰 Cost Breakdown", show_header=True, header_style="bold green")
        cost_table.add_column("Component", style="cyan")
        cost_table.add_column("Monthly Cost", style="green", justify="right")
        cost_table.add_column("Percentage", style="yellow", justify="right")

        total_cost = cost_analysis.get("total_monthly_cost", 0)
        for component in cost_analysis["cost_breakdown"]:
            cost = component.get("monthly_cost", 0)
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            cost_table.add_row(component.get("component", ""), f"${cost:.2f}", f"{percentage:.1f}%")

        console.print(cost_table)

    # Optimization recommendations
    recommendations = results.get("optimization_recommendations", [])
    if recommendations:
        rec_table = Table(title="🎯 Optimization Recommendations", show_header=True, header_style="bold yellow")
        rec_table.add_column("Priority", style="red")
        rec_table.add_column("Title", style="cyan")
        rec_table.add_column("Monthly Savings", style="green", justify="right")
        rec_table.add_column("Effort", style="yellow")
        rec_table.add_column("Description", style="white")

        for rec in recommendations[:5]:  # Top 5 recommendations
            rec_table.add_row(
                rec.get("priority", ""),
                rec.get("title", ""),
                f"${rec.get('monthly_savings', 0):.2f}",
                rec.get("effort", ""),
                rec.get("description", "")[:50] + "..."
                if len(rec.get("description", "")) > 50
                else rec.get("description", ""),
            )

        console.print(rec_table)

    # Architecture gaps and drift detection
    gaps = results.get("architecture_gaps", [])
    if gaps:
        gap_table = Table(title="⚠️ Architecture Gaps & Drift Detection", show_header=True, header_style="bold red")
        gap_table.add_column("Category", style="cyan")
        gap_table.add_column("Severity", style="red")
        gap_table.add_column("Description", style="white")
        gap_table.add_column("Details", style="yellow")

        for gap in gaps:
            severity_style = {
                "Info": "blue",
                "Warning": "yellow",
                "Medium": "orange",
                "High": "red",
                "Critical": "bright_red",
            }.get(gap.get("severity", ""), "white")

            gap_table.add_row(
                gap.get("category", ""),
                f"[{severity_style}]{gap.get('severity', '')}[/{severity_style}]",
                gap.get("description", ""),
                gap.get("details", "")[:60],
            )

        console.print(gap_table)

    # Footer with next steps
    next_steps = Panel(
        "[bold cyan]Next Steps:[/bold cyan]\n"
        "1. Review optimization recommendations by priority\n"
        "2. Address architecture gaps and drift detection issues\n"
        "3. Implement centralized VPC endpoint sharing\n"
        "4. Monitor cost savings and performance impact\n"
        "5. Schedule regular analysis runs for continuous optimization",
        title="🚀 Recommended Actions",
        border_style="bright_blue",
    )
    console.print(next_steps)

    # Analysis timestamp
    console.print(f"\n[dim]Analysis completed: {results.get('analysis_timestamp', 'N/A')}[/dim]")

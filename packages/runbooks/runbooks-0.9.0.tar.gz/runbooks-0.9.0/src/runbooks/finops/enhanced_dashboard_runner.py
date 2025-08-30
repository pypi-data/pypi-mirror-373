#!/usr/bin/env python3
"""
Enhanced FinOps Dashboard Runner

This module provides enterprise-grade FinOps dashboard capabilities including:
- Multi-profile AWS cost analysis with Rich console formatting
- Advanced audit reporting with PDF/CSV/JSON export
- Resource utilization tracking and optimization recommendations
- Budget monitoring and alerting integration
- Trend analysis and forecasting capabilities
"""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import boto3
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, track
from rich.status import Status
from rich.table import Column, Table
from rich.tree import Tree

from ..common.rich_utils import get_console

# FinOpsConfig dependency removed - using simple dict configuration instead

console = Console()


class EnhancedFinOpsDashboard:
    """Enhanced FinOps Dashboard with production-tested capabilities from runbooks finops"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.console = Console()
        self.rich_console = self.console  # Use the console instance directly

        # Export directory setup
        self.export_dir = Path("artifacts/finops-exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def get_aws_profiles(self) -> List[str]:
        """Get available AWS profiles from AWS CLI configuration"""
        try:
            import configparser
            import os

            aws_config_path = os.path.expanduser("~/.aws/config")
            aws_credentials_path = os.path.expanduser("~/.aws/credentials")

            profiles = set()

            # Parse AWS config file
            if os.path.exists(aws_config_path):
                config = configparser.ConfigParser()
                config.read(aws_config_path)
                for section in config.sections():
                    if section.startswith("profile "):
                        profiles.add(section.replace("profile ", ""))
                    elif section == "default":
                        profiles.add("default")

            # Parse AWS credentials file
            if os.path.exists(aws_credentials_path):
                credentials = configparser.ConfigParser()
                credentials.read(aws_credentials_path)
                profiles.update(credentials.sections())

            return sorted(list(profiles))

        except Exception as e:
            console.print(f"⚠️  Error reading AWS profiles: {e}", style="yellow")
            return []

    def get_account_info(self, profile: str) -> Dict[str, Any]:
        """Get AWS account information for a profile"""
        try:
            session = boto3.Session(profile_name=profile)
            sts = session.client("sts")

            identity = sts.get_caller_identity()

            return {
                "account_id": identity["Account"],
                "user_arn": identity["Arn"],
                "user_id": identity["UserId"],
                "profile": profile,
                "status": "active",
            }

        except Exception as e:
            return {"account_id": "N/A", "profile": profile, "status": "error", "error": str(e)}

    def get_resource_audit_data(self, profile: str, regions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get comprehensive resource audit data for a profile

        Enhanced with additional resource types and cost impact analysis
        """
        audit_data = {
            "profile": profile,
            "account_info": self.get_account_info(profile),
            "untagged_resources": 0,
            "stopped_instances": 0,
            "unused_volumes": 0,
            "unused_eips": 0,
            "budget_alerts": 0,
            "cost_optimization_opportunities": [],
            "regional_breakdown": {},
            "total_potential_savings": 0.0,
        }

        if audit_data["account_info"]["status"] == "error":
            return audit_data

        try:
            session = boto3.Session(profile_name=profile)

            # Default to common regions if none specified
            if not regions:
                regions = ["us-east-1", "us-west-2", "eu-west-1"]

            for region in regions:
                region_data = self._audit_region_resources(session, region)
                audit_data["regional_breakdown"][region] = region_data

                # Aggregate data
                audit_data["untagged_resources"] += region_data["untagged_resources"]
                audit_data["stopped_instances"] += region_data["stopped_instances"]
                audit_data["unused_volumes"] += region_data["unused_volumes"]
                audit_data["unused_eips"] += region_data["unused_eips"]
                audit_data["total_potential_savings"] += region_data["potential_savings"]
                audit_data["cost_optimization_opportunities"].extend(region_data["optimization_opportunities"])

            # Get budget information
            audit_data["budget_alerts"] = self._get_budget_alerts(session)

        except Exception as e:
            console.print(f"⚠️  Error auditing resources for {profile}: {e}", style="yellow")

        return audit_data

    def _audit_region_resources(self, session: boto3.Session, region: str) -> Dict[str, Any]:
        """Audit resources in a specific region"""
        region_data = {
            "region": region,
            "untagged_resources": 0,
            "stopped_instances": 0,
            "unused_volumes": 0,
            "unused_eips": 0,
            "potential_savings": 0.0,
            "optimization_opportunities": [],
        }

        try:
            ec2 = session.client("ec2", region_name=region)

            # Get stopped EC2 instances
            instances_response = ec2.describe_instances(
                Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
            )

            stopped_instances = []
            for reservation in instances_response["Reservations"]:
                for instance in reservation["Instances"]:
                    stopped_instances.append(
                        {
                            "instance_id": instance["InstanceId"],
                            "instance_type": instance["InstanceType"],
                            "launch_time": instance.get("LaunchTime"),
                            "tags": instance.get("Tags", []),
                        }
                    )

            region_data["stopped_instances"] = len(stopped_instances)

            # Calculate potential savings from stopped instances (rough estimate)
            # Assume average $50/month per stopped instance in savings opportunity
            region_data["potential_savings"] += len(stopped_instances) * 50.0

            if stopped_instances:
                region_data["optimization_opportunities"].append(
                    {
                        "type": "stopped_instances",
                        "count": len(stopped_instances),
                        "description": f"{len(stopped_instances)} stopped EC2 instances - consider termination",
                        "potential_savings": len(stopped_instances) * 50.0,
                        "priority": "high",
                    }
                )

            # Get unused EBS volumes
            volumes_response = ec2.describe_volumes(Filters=[{"Name": "status", "Values": ["available"]}])

            unused_volumes = volumes_response["Volumes"]
            region_data["unused_volumes"] = len(unused_volumes)

            # Note: EBS cost calculation requires real AWS Cost Explorer pricing data
            # Hardcoded pricing estimates removed per compliance requirements
            volume_savings = 0  # Cannot calculate without real AWS pricing API
            region_data["potential_savings"] += volume_savings

            if unused_volumes:
                region_data["optimization_opportunities"].append(
                    {
                        "type": "unused_volumes",
                        "count": len(unused_volumes),
                        "description": f"{len(unused_volumes)} unused EBS volumes",
                        "potential_savings": volume_savings,
                        "priority": "medium",
                    }
                )

            # Get unused Elastic IPs
            eips_response = ec2.describe_addresses()
            unused_eips = [eip for eip in eips_response["Addresses"] if "InstanceId" not in eip]
            region_data["unused_eips"] = len(unused_eips)

            # Unused EIP cost: $3.65/month each
            eip_savings = len(unused_eips) * 3.65
            region_data["potential_savings"] += eip_savings

            if unused_eips:
                region_data["optimization_opportunities"].append(
                    {
                        "type": "unused_eips",
                        "count": len(unused_eips),
                        "description": f"{len(unused_eips)} unused Elastic IPs",
                        "potential_savings": eip_savings,
                        "priority": "high",
                    }
                )

            # Count untagged resources (simplified check)
            untagged_count = 0
            for instance in stopped_instances:
                if not instance["tags"]:
                    untagged_count += 1
            for volume in unused_volumes:
                if not volume.get("Tags"):
                    untagged_count += 1

            region_data["untagged_resources"] = untagged_count

        except Exception as e:
            console.print(f"⚠️  Error auditing {region}: {e}", style="yellow")

        return region_data

    def _get_budget_alerts(self, session: boto3.Session) -> int:
        """Get budget alert count"""
        try:
            budgets = session.client("budgets")

            # Get account ID for budgets API
            sts = session.client("sts")
            account_id = sts.get_caller_identity()["Account"]

            response = budgets.describe_budgets(AccountId=account_id)
            return len(response.get("Budgets", []))

        except Exception:
            return 0  # Budgets API might not be accessible

    def generate_audit_report(
        self, profiles: Optional[List[str]] = None, regions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive audit report for specified profiles"""

        if not profiles:
            profiles = self.get_aws_profiles()
            if not profiles:
                console.print("❌ No AWS profiles found", style="red")
                return {}

        audit_results = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "profiles_analyzed": len(profiles),
                "regions_analyzed": len(regions) if regions else 3,
                "report_type": "comprehensive_audit",
            },
            "profile_data": {},
            "summary": {
                "total_untagged_resources": 0,
                "total_stopped_instances": 0,
                "total_unused_volumes": 0,
                "total_unused_eips": 0,
                "total_budget_alerts": 0,
                "total_potential_savings": 0.0,
                "optimization_opportunities": [],
            },
        }

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            for profile in profiles:
                task = progress.add_task(f"Auditing profile {profile}...", total=None)

                profile_data = self.get_resource_audit_data(profile, regions)
                audit_results["profile_data"][profile] = profile_data

                # Aggregate summary data
                summary = audit_results["summary"]
                summary["total_untagged_resources"] += profile_data["untagged_resources"]
                summary["total_stopped_instances"] += profile_data["stopped_instances"]
                summary["total_unused_volumes"] += profile_data["unused_volumes"]
                summary["total_unused_eips"] += profile_data["unused_eips"]
                summary["total_budget_alerts"] += profile_data["budget_alerts"]
                summary["total_potential_savings"] += profile_data["total_potential_savings"]
                summary["optimization_opportunities"].extend(profile_data["cost_optimization_opportunities"])

                progress.remove_task(task)

        return audit_results

    def display_audit_report(self, audit_results: Dict[str, Any]):
        """Display audit report with enhanced Rich formatting"""

        summary = audit_results["summary"]
        profile_data = audit_results["profile_data"]

        # Report header
        header_panel = Panel.fit(
            f"[bold bright_cyan]🏢 AWS FinOps Comprehensive Audit Report[/bold bright_cyan]\n\n"
            f"📊 Profiles Analyzed: [yellow]{len(profile_data)}[/yellow]\n"
            f"🕒 Generated: [green]{audit_results['report_metadata']['generated_at'][:19]}[/green]\n"
            f"💰 Total Savings Potential: [bold green]${summary['total_potential_savings']:.2f}/month[/bold green]",
            title="Audit Report",
            style="bright_cyan",
        )
        console.print(header_panel)

        # Summary table
        summary_table = Table(title="📈 Executive Summary", box=box.ASCII_DOUBLE_HEAD, style="bright_cyan")
        summary_table.add_column("Metric", style="cyan", width=25)
        summary_table.add_column("Count", style="yellow", width=10)
        summary_table.add_column("Impact", style="green", width=20)

        summary_table.add_row("Untagged Resources", str(summary["total_untagged_resources"]), "Compliance Risk")
        summary_table.add_row(
            "Stopped Instances",
            str(summary["total_stopped_instances"]),
            f"${summary['total_stopped_instances'] * 50:.0f}/month potential",
        )
        summary_table.add_row("Unused Volumes", str(summary["total_unused_volumes"]), "Storage waste")
        summary_table.add_row(
            "Unused EIPs", str(summary["total_unused_eips"]), f"${summary['total_unused_eips'] * 3.65:.0f}/month waste"
        )
        summary_table.add_row("Budget Alerts", str(summary["total_budget_alerts"]), "Monitoring coverage")

        console.print(summary_table)

        # Profile-specific table
        profile_table = Table(
            title="👥 Profile-Specific Analysis", show_lines=True, box=box.ASCII_DOUBLE_HEAD, style="bright_cyan"
        )

        profile_table.add_column("Profile", justify="center", width=20)
        profile_table.add_column("Account ID", justify="center", width=15)
        profile_table.add_column("Untagged", width=10)
        profile_table.add_column("Stopped EC2", width=12)
        profile_table.add_column("Unused Vol", width=12)
        profile_table.add_column("Unused EIP", width=12)
        profile_table.add_column("Savings", width=12)

        for profile, data in profile_data.items():
            account_info = data["account_info"]
            profile_table.add_row(
                profile,
                account_info["account_id"] if account_info["status"] == "active" else "ERROR",
                str(data["untagged_resources"]),
                str(data["stopped_instances"]),
                str(data["unused_volumes"]),
                str(data["unused_eips"]),
                f"${data['total_potential_savings']:.0f}",
            )

        console.print(profile_table)

        # Top optimization opportunities
        if summary["optimization_opportunities"]:
            console.print("\n[bold blue]🎯 Top Optimization Opportunities[/bold blue]")

            # Sort by potential savings
            sorted_opportunities = sorted(
                summary["optimization_opportunities"], key=lambda x: x.get("potential_savings", 0), reverse=True
            )

            for i, opp in enumerate(sorted_opportunities[:10], 1):  # Top 10
                priority_color = {"high": "red", "medium": "yellow", "low": "green"}
                color = priority_color.get(opp.get("priority", "low"), "white")

                console.print(
                    f"{i:2d}. [bold {color}]{opp['description']}[/bold {color}] "
                    f"([green]${opp.get('potential_savings', 0):.0f}/month[/green])"
                )

    def export_audit_report(
        self, audit_results: Dict[str, Any], formats: List[str] = ["json", "csv"]
    ) -> Dict[str, str]:
        """Export audit report in multiple formats"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_files = {}

        # JSON export
        if "json" in formats:
            json_file = self.export_dir / f"finops_audit_report_{timestamp}.json"
            with open(json_file, "w") as f:
                json.dump(audit_results, f, indent=2, default=str)
            export_files["json"] = str(json_file)

        # CSV export
        if "csv" in formats:
            csv_file = self.export_dir / f"finops_audit_summary_{timestamp}.csv"
            with open(csv_file, "w", newline="") as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(
                    [
                        "Profile",
                        "Account_ID",
                        "Untagged_Resources",
                        "Stopped_Instances",
                        "Unused_Volumes",
                        "Unused_EIPs",
                        "Budget_Alerts",
                        "Potential_Savings_Monthly",
                    ]
                )

                # Data rows
                for profile, data in audit_results["profile_data"].items():
                    writer.writerow(
                        [
                            profile,
                            data["account_info"]["account_id"],
                            data["untagged_resources"],
                            data["stopped_instances"],
                            data["unused_volumes"],
                            data["unused_eips"],
                            data["budget_alerts"],
                            f"${data['total_potential_savings']:.2f}",
                        ]
                    )

            export_files["csv"] = str(csv_file)

        return export_files

    def run_comprehensive_audit(
        self,
        profiles: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        export_formats: List[str] = ["json", "csv"],
        display_report: bool = True,
    ) -> Dict[str, Any]:
        """Run comprehensive FinOps audit with reporting and export"""

        console.print("[bold bright_cyan]🚀 Starting Enhanced FinOps Audit...[/bold bright_cyan]")

        # Generate audit data
        audit_results = self.generate_audit_report(profiles, regions)

        if not audit_results:
            console.print("❌ No audit data generated", style="red")
            return {}

        # Display report
        if display_report:
            self.display_audit_report(audit_results)

        # Export results
        if export_formats:
            console.print(f"\n📄 Exporting report in formats: {', '.join(export_formats)}")
            export_files = self.export_audit_report(audit_results, export_formats)

            console.print("✅ Export completed:")
            for format_type, file_path in export_files.items():
                console.print(f"   📁 {format_type.upper()}: {file_path}")

        # Summary of potential savings
        total_savings = audit_results["summary"]["total_potential_savings"]
        if total_savings > 0:
            annual_savings = total_savings * 12
            console.print(f"\n💰 [bold green]Total Optimization Potential:[/bold green]")
            console.print(f"   Monthly: [yellow]${total_savings:.2f}[/yellow]")
            console.print(f"   Annual:  [green]${annual_savings:.2f}[/green]")

        return audit_results


# CLI integration functions
def enhanced_audit_cli(
    profiles: Optional[str] = None,
    regions: Optional[str] = None,
    export_formats: str = "json,csv",
    output_dir: Optional[str] = None,
) -> None:
    """CLI command for enhanced FinOps audit"""

    profile_list = profiles.split(",") if profiles else None
    region_list = regions.split(",") if regions else None
    format_list = export_formats.split(",") if export_formats else ["json"]

    dashboard = EnhancedFinOpsDashboard()

    if output_dir:
        dashboard.export_dir = Path(output_dir)
        dashboard.export_dir.mkdir(parents=True, exist_ok=True)

    audit_results = dashboard.run_comprehensive_audit(
        profiles=profile_list, regions=region_list, export_formats=format_list, display_report=True
    )

    return audit_results

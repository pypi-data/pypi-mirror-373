"""
EC2 Utilization Analysis - Investigate EC2 utilization patterns for cost optimization.

Business Case: Enhanced EC2 investigation framework for backup infrastructure analysis
Target Account: 637423383469 (Backup infrastructure account)
Challenge: Determine if EC2 instances are actively used for backups or idle
Strategic Value: Infrastructure right-sizing and cost optimization through utilization analysis
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client, write_to_csv
from ..common.rich_utils import (
    console, print_header, print_success, print_error, print_warning,
    create_table, create_progress_bar, format_cost
)

logger = logging.getLogger(__name__)


def calculate_ec2_cost_impact(instances_data: List[Dict]) -> Dict[str, float]:
    """
    Calculate potential cost impact for EC2 instances.
    
    JIRA FinOps-25: Focuses on Commvault backup account utilization analysis
    """
    total_instances = len(instances_data)
    running_instances = [i for i in instances_data if i.get("State", {}).get("Name") == "running"]
    idle_instances = [i for i in instances_data if i.get("CpuUtilization", 0) < 5.0]  # <5% CPU
    
    # Rough cost estimation (simplified for investigation phase)
    estimated_monthly_cost = 0.0
    for instance in running_instances:
        instance_type = instance.get("InstanceType", "t3.micro")
        # Simplified cost mapping (USD/month for common instance types)
        cost_map = {
            "t3.micro": 8.47,
            "t3.small": 16.94,
            "t3.medium": 33.87,
            "m5.large": 70.08,
            "m5.xlarge": 140.16,
            "c5.large": 62.98,
            "c5.xlarge": 125.95,
        }
        estimated_monthly_cost += cost_map.get(instance_type, 50.0)  # Default $50/month
    
    return {
        "total_instances": total_instances,
        "running_instances": len(running_instances),
        "idle_instances": len(idle_instances),
        "estimated_monthly_cost": estimated_monthly_cost,
        "estimated_annual_cost": estimated_monthly_cost * 12,
        "potential_savings_if_idle": estimated_monthly_cost * 12 * 0.7,  # 70% of cost if truly idle
    }


@click.command()
@click.option("--output-file", default="/tmp/commvault_ec2_investigation.csv", help="Output CSV file path")
@click.option("--account", default="637423383469", help="Commvault backup account ID (JIRA FinOps-25)")
@click.option("--investigate-utilization", is_flag=True, help="Investigate EC2 utilization patterns")
@click.option("--days", default=7, help="Number of days to analyze for utilization metrics")
@click.option("--dry-run", is_flag=True, default=True, help="Preview analysis without execution")
def investigate_commvault_ec2(output_file, account, investigate_utilization, days, dry_run):
    """
    FinOps-25: Commvault EC2 investigation for cost optimization.
    
    Account: 637423383469 (Commvault backup account)
    Challenge: Determine if EC2 instances are actively used for backups or idle
    """
    print_header("JIRA FinOps-25: Commvault EC2 Investigation", "v0.9.1")
    
    account_info = display_aws_account_info()
    console.print(f"[cyan]Account: {account} - Investigating EC2 usage patterns[/cyan]")

    try:
        ec2_client = get_client("ec2")
        cloudwatch_client = get_client("cloudwatch")

        # Get all EC2 instances
        console.print("[yellow]Collecting EC2 instance data...[/yellow]")
        response = ec2_client.describe_instances()
        
        instances_data = []
        all_instances = []
        
        # Flatten instance data
        for reservation in response.get("Reservations", []):
            all_instances.extend(reservation.get("Instances", []))

        if not all_instances:
            print_warning("No EC2 instances found in this account")
            return

        console.print(f"[green]Found {len(all_instances)} EC2 instances to investigate[/green]")

        # Calculate time range for analysis
        end_time = datetime.now(tz=timezone.utc)
        start_time = end_time - timedelta(days=days)

        with create_progress_bar() as progress:
            task_id = progress.add_task(
                f"Investigating {len(all_instances)} EC2 instances...",
                total=len(all_instances)
            )

            for instance in all_instances:
                instance_id = instance["InstanceId"]
                instance_type = instance.get("InstanceType", "unknown")
                state = instance.get("State", {}).get("Name", "unknown")
                launch_time = instance.get("LaunchTime")
                
                # Get CPU utilization metrics
                cpu_utilization = 0.0
                if investigate_utilization and state == "running":
                    try:
                        cpu_response = cloudwatch_client.get_metric_statistics(
                            Namespace="AWS/EC2",
                            MetricName="CPUUtilization",
                            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=3600,  # 1 hour intervals
                            Statistics=["Average"],
                        )
                        
                        if cpu_response.get("Datapoints"):
                            cpu_utilization = sum(
                                dp["Average"] for dp in cpu_response["Datapoints"]
                            ) / len(cpu_response["Datapoints"])
                            
                    except ClientError as e:
                        logger.warning(f"Could not get CPU metrics for {instance_id}: {e}")

                # Get tags for context
                tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                
                instance_data = {
                    "InstanceId": instance_id,
                    "InstanceType": instance_type,
                    "State": state,
                    "LaunchTime": launch_time.strftime("%Y-%m-%d %H:%M:%S") if launch_time else "Unknown",
                    "CpuUtilization": round(cpu_utilization, 2),
                    "Name": tags.get("Name", "Unknown"),
                    "Environment": tags.get("Environment", tags.get("Env", "Unknown")),
                    "Purpose": tags.get("Purpose", tags.get("Application", "Unknown")),
                    "IsLowUtilization": cpu_utilization < 5.0 if investigate_utilization else False,
                }
                
                instances_data.append(instance_data)
                progress.advance(task_id)

        # Export results
        write_to_csv(instances_data, output_file)
        print_success(f"Commvault EC2 investigation exported to: {output_file}")

        # Calculate cost impact analysis
        cost_analysis = calculate_ec2_cost_impact(instances_data)
        
        # Create summary table
        print_header("Commvault EC2 Investigation Summary")
        
        summary_table = create_table(
            title="EC2 Cost Impact Analysis - JIRA FinOps-25",
            columns=[
                {"header": "Metric", "style": "cyan"},
                {"header": "Count", "style": "green bold"},
                {"header": "Monthly Cost", "style": "red"},
                {"header": "Annual Cost", "style": "red bold"}
            ]
        )

        summary_table.add_row(
            "Total EC2 Instances",
            str(cost_analysis["total_instances"]),
            "Mixed Types",
            "Mixed Types"
        )
        
        summary_table.add_row(
            "Running Instances",
            str(cost_analysis["running_instances"]),
            format_cost(cost_analysis["estimated_monthly_cost"]),
            format_cost(cost_analysis["estimated_annual_cost"])
        )
        
        if investigate_utilization:
            summary_table.add_row(
                "Low Utilization (<5% CPU)",
                str(cost_analysis["idle_instances"]),
                "Investigation Required",
                "Investigation Required"
            )
            
            summary_table.add_row(
                "🎯 Potential Savings (if idle)",
                f"{cost_analysis['idle_instances']} instances",
                format_cost(cost_analysis["potential_savings_if_idle"] / 12),
                format_cost(cost_analysis["potential_savings_if_idle"])
            )

        console.print(summary_table)

        # Investigation recommendations
        if investigate_utilization:
            low_util_instances = [i for i in instances_data if i["IsLowUtilization"]]
            
            if low_util_instances:
                print_warning(f"🔍 Found {len(low_util_instances)} instances with low utilization:")
                
                # Create detailed investigation table
                investigation_table = create_table(
                    title="Low Utilization Instances (Investigation Required)",
                    columns=[
                        {"header": "Instance ID", "style": "cyan"},
                        {"header": "Type", "style": "blue"},
                        {"header": "CPU %", "style": "yellow"},
                        {"header": "Name", "style": "green"},
                        {"header": "Purpose", "style": "magenta"},
                        {"header": "State", "style": "red"}
                    ]
                )
                
                for instance in low_util_instances[:10]:  # Show first 10
                    investigation_table.add_row(
                        instance['InstanceId'],
                        instance['InstanceType'],
                        f"{instance['CpuUtilization']:.1f}%",
                        instance['Name'],
                        instance['Purpose'],
                        instance['State']
                    )
                
                console.print(investigation_table)
                
                if len(low_util_instances) > 10:
                    console.print(f"[dim]... and {len(low_util_instances) - 10} more instances requiring investigation[/dim]")
                    
                # Manual verification checklist
                print_header("Manual Verification Checklist")
                console.print("[yellow]For each low-utilization instance, verify:[/yellow]")
                console.print("[dim]1. Is this instance actively used for Commvault backup operations?[/dim]")
                console.print("[dim]2. Are there scheduled backup jobs running on this instance?[/dim]") 
                console.print("[dim]3. Can this instance be right-sized or terminated safely?[/dim]")
                console.print("[dim]4. Are there any dependencies or integrations that require this instance?[/dim]")
                
            else:
                print_success("✓ No low-utilization instances detected")

        # JIRA FinOps-25 completion status
        console.print(f"\n[cyan]📋 JIRA FinOps-25 Status: Investigation framework complete[/cyan]")
        console.print(f"[dim]Next steps: Manual review of findings and cost impact validation[/dim]")

    except Exception as e:
        logger.error(f"Failed to investigate Commvault EC2: {e}")
        raise
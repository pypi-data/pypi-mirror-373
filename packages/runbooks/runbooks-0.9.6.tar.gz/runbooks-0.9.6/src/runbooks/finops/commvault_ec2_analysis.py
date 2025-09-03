"""
FinOps-25: Commvault EC2 Investigation Framework

Strategic Achievement: Investigation methodology established for infrastructure optimization
Account Focus: 637423383469 (Commvault backups account)
Objective: Analyze EC2 instances for backup utilization and cost optimization potential

This module provides comprehensive EC2 utilization analysis specifically for Commvault
backup infrastructure to determine if instances are actively performing backups.

Strategic Alignment:
- "Do one thing and do it well": Focus on Commvault-specific EC2 analysis
- "Move Fast, But Not So Fast We Crash": Careful analysis before decommissioning
- Enterprise FAANG SDLC: Evidence-based investigation with audit trails
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import boto3
import click
from botocore.exceptions import ClientError

from ..common.rich_utils import (
    console, print_header, print_success, print_error, print_warning, print_info,
    create_table, create_progress_bar, format_cost, create_panel
)

logger = logging.getLogger(__name__)


class CommvaultEC2Analysis:
    """
    FinOps-25: Commvault EC2 Investigation Framework
    
    Provides systematic analysis of EC2 instances in Commvault backup account
    to determine utilization patterns and optimization opportunities.
    """
    
    def __init__(self, profile_name: Optional[str] = None, account_id: str = "637423383469"):
        """Initialize Commvault EC2 analysis."""
        self.profile_name = profile_name
        self.account_id = account_id
        self.session = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
    
    def analyze_commvault_instances(self, region: str = "us-east-1") -> Dict:
        """
        Analyze EC2 instances in Commvault account for utilization patterns.
        
        Args:
            region: AWS region to analyze (default: us-east-1)
            
        Returns:
            Dict containing analysis results with cost implications
        """
        print_header("FinOps-25: Commvault EC2 Investigation", f"Account: {self.account_id}")
        
        try:
            ec2_client = self.session.client('ec2', region_name=region)
            cloudwatch_client = self.session.client('cloudwatch', region_name=region)
            
            # Get all EC2 instances
            response = ec2_client.describe_instances()
            instances = []
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    if instance['State']['Name'] != 'terminated':
                        instances.append(instance)
            
            if not instances:
                print_warning(f"No active instances found in account {self.account_id}")
                return {"instances": [], "total_cost": 0, "optimization_potential": 0}
            
            print_info(f"Found {len(instances)} active instances for analysis")
            
            # Analyze each instance
            analysis_results = []
            total_monthly_cost = 0
            
            with create_progress_bar() as progress:
                task = progress.add_task("Analyzing instances...", total=len(instances))
                
                for instance in instances:
                    instance_analysis = self._analyze_single_instance(
                        instance, cloudwatch_client, region
                    )
                    analysis_results.append(instance_analysis)
                    total_monthly_cost += instance_analysis['estimated_monthly_cost']
                    progress.advance(task)
            
            # Generate summary
            optimization_potential = self._calculate_optimization_potential(analysis_results)
            
            # Display results
            self._display_analysis_results(analysis_results, total_monthly_cost, optimization_potential)
            
            return {
                "instances": analysis_results,
                "total_monthly_cost": total_monthly_cost,
                "optimization_potential": optimization_potential,
                "account_id": self.account_id,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except ClientError as e:
            print_error(f"AWS API Error: {e}")
            raise
        except Exception as e:
            print_error(f"Analysis Error: {e}")
            raise
    
    def _analyze_single_instance(self, instance: Dict, cloudwatch_client, region: str) -> Dict:
        """Analyze a single EC2 instance for utilization patterns."""
        instance_id = instance['InstanceId']
        instance_type = instance['InstanceType']
        
        # Get CloudWatch metrics for last 30 days
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=30)
        
        try:
            # CPU Utilization
            cpu_response = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour intervals
                Statistics=['Average']
            )
            
            # Network metrics for backup activity indication
            network_in_response = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkIn',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
            network_out_response = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkOut',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
        except ClientError as e:
            logger.warning(f"CloudWatch metrics unavailable for {instance_id}: {e}")
            cpu_response = {'Datapoints': []}
            network_in_response = {'Datapoints': []}
            network_out_response = {'Datapoints': []}
        
        # Calculate averages
        avg_cpu = 0
        if cpu_response['Datapoints']:
            avg_cpu = sum(dp['Average'] for dp in cpu_response['Datapoints']) / len(cpu_response['Datapoints'])
        
        total_network_in = sum(dp['Sum'] for dp in network_in_response['Datapoints']) if network_in_response['Datapoints'] else 0
        total_network_out = sum(dp['Sum'] for dp in network_out_response['Datapoints']) if network_out_response['Datapoints'] else 0
        
        # Estimate monthly cost (simplified pricing model)
        estimated_monthly_cost = self._estimate_instance_cost(instance_type)
        
        # Get instance tags
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        
        # Backup activity assessment
        backup_activity_score = self._assess_backup_activity(
            avg_cpu, total_network_in, total_network_out, tags
        )
        
        return {
            "instance_id": instance_id,
            "instance_type": instance_type,
            "state": instance['State']['Name'],
            "launch_time": instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else '',
            "avg_cpu_utilization": round(avg_cpu, 2),
            "network_in_bytes": int(total_network_in),
            "network_out_bytes": int(total_network_out),
            "estimated_monthly_cost": estimated_monthly_cost,
            "tags": tags,
            "backup_activity_score": backup_activity_score,
            "recommendation": self._generate_recommendation(backup_activity_score, avg_cpu)
        }
    
    def _estimate_instance_cost(self, instance_type: str) -> float:
        """Estimate monthly cost for EC2 instance type."""
        # Simplified pricing model - actual costs may vary
        instance_pricing = {
            't2.micro': 8.76,
            't2.small': 17.52,
            't2.medium': 35.04,
            't2.large': 70.08,
            't3.micro': 7.59,
            't3.small': 15.18,
            't3.medium': 30.37,
            't3.large': 60.74,
            'm5.large': 70.08,
            'm5.xlarge': 140.16,
            'm5.2xlarge': 280.32,
            'c5.large': 62.93,
            'c5.xlarge': 125.87,
            'r5.large': 91.98,
            'r5.xlarge': 183.96
        }
        
        return instance_pricing.get(instance_type, 100.0)  # Default estimate
    
    def _assess_backup_activity(self, cpu: float, network_in: int, network_out: int, tags: Dict) -> str:
        """Assess likelihood of backup activity based on metrics and tags."""
        score_factors = []
        
        # CPU utilization assessment
        if cpu > 20:
            score_factors.append("High CPU usage suggests active processes")
        elif cpu < 5:
            score_factors.append("Low CPU usage may indicate idle instance")
        
        # Network activity assessment
        total_network = network_in + network_out
        if total_network > 10 * 1024**3:  # 10 GB
            score_factors.append("High network activity suggests data transfer")
        elif total_network < 1 * 1024**3:  # 1 GB
            score_factors.append("Low network activity may indicate minimal backup activity")
        
        # Tag analysis for Commvault indicators
        commvault_indicators = ['commvault', 'backup', 'cv', 'media', 'agent']
        for indicator in commvault_indicators:
            for tag_value in tags.values():
                if indicator.lower() in str(tag_value).lower():
                    score_factors.append(f"Tag indicates Commvault purpose: {tag_value}")
                    break
        
        if len(score_factors) >= 2:
            return "LIKELY_ACTIVE"
        elif len(score_factors) == 1:
            return "UNCERTAIN"
        else:
            return "LIKELY_IDLE"
    
    def _generate_recommendation(self, activity_score: str, cpu: float) -> str:
        """Generate optimization recommendation based on analysis."""
        if activity_score == "LIKELY_IDLE" and cpu < 5:
            return "CANDIDATE_FOR_DECOMMISSION"
        elif activity_score == "UNCERTAIN":
            return "REQUIRES_DEEPER_INVESTIGATION" 
        elif activity_score == "LIKELY_ACTIVE":
            return "RETAIN_MONITOR_USAGE"
        else:
            return "MANUAL_REVIEW_REQUIRED"
    
    def _calculate_optimization_potential(self, instances: List[Dict]) -> Dict:
        """Calculate potential cost savings from optimization."""
        decommission_candidates = [
            i for i in instances 
            if i['recommendation'] == 'CANDIDATE_FOR_DECOMMISSION'
        ]
        
        investigation_required = [
            i for i in instances
            if i['recommendation'] == 'REQUIRES_DEEPER_INVESTIGATION'
        ]
        
        potential_monthly_savings = sum(i['estimated_monthly_cost'] for i in decommission_candidates)
        potential_annual_savings = potential_monthly_savings * 12
        
        return {
            "decommission_candidates": len(decommission_candidates),
            "investigation_required": len(investigation_required),
            "potential_monthly_savings": potential_monthly_savings,
            "potential_annual_savings": potential_annual_savings,
            "confidence_level": "HIGH" if len(decommission_candidates) > 0 else "MEDIUM"
        }
    
    def _display_analysis_results(self, instances: List[Dict], total_cost: float, optimization: Dict):
        """Display comprehensive analysis results."""
        # Summary table
        summary_table = create_table(
            title="FinOps-25: Commvault EC2 Analysis Summary",
            caption=f"Account: {self.account_id} | Analysis Date: {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        summary_table.add_column("Metric", style="cyan", width=25)
        summary_table.add_column("Value", style="green", justify="right", width=20)
        summary_table.add_column("Impact", style="yellow", width=30)
        
        summary_table.add_row(
            "Total Instances", 
            str(len(instances)),
            "Infrastructure scope"
        )
        summary_table.add_row(
            "Monthly Cost",
            format_cost(total_cost, period="monthly"),
            "Current infrastructure cost"
        )
        summary_table.add_row(
            "Decommission Candidates",
            str(optimization['decommission_candidates']),
            "Immediate optimization opportunities"
        )
        summary_table.add_row(
            "Investigation Required", 
            str(optimization['investigation_required']),
            "Further analysis needed"
        )
        summary_table.add_row(
            "Potential Annual Savings",
            format_cost(optimization['potential_annual_savings'], period="annual"),
            f"Confidence: {optimization['confidence_level']}"
        )
        
        console.print(summary_table)
        
        # Detailed instance analysis
        if instances:
            detail_table = create_table(
                title="Detailed Instance Analysis",
                caption="CPU and network utilization patterns with recommendations"
            )
            
            detail_table.add_column("Instance ID", style="cyan", width=18)
            detail_table.add_column("Type", style="blue", width=12)
            detail_table.add_column("Avg CPU %", style="yellow", justify="right", width=10)
            detail_table.add_column("Network (GB)", style="magenta", justify="right", width=12)
            detail_table.add_column("Monthly Cost", style="green", justify="right", width=12)
            detail_table.add_column("Recommendation", style="red", width=20)
            
            for instance in instances:
                network_gb = (instance['network_in_bytes'] + instance['network_out_bytes']) / (1024**3)
                
                recommendation_style = {
                    'CANDIDATE_FOR_DECOMMISSION': '[red]DECOMMISSION[/red]',
                    'REQUIRES_DEEPER_INVESTIGATION': '[yellow]INVESTIGATE[/yellow]', 
                    'RETAIN_MONITOR_USAGE': '[green]RETAIN[/green]',
                    'MANUAL_REVIEW_REQUIRED': '[blue]MANUAL REVIEW[/blue]'
                }.get(instance['recommendation'], instance['recommendation'])
                
                detail_table.add_row(
                    instance['instance_id'],
                    instance['instance_type'],
                    f"{instance['avg_cpu_utilization']:.1f}%",
                    f"{network_gb:.1f}",
                    format_cost(instance['estimated_monthly_cost'], period="monthly"),
                    recommendation_style
                )
            
            console.print(detail_table)
        
        # Business impact panel
        if optimization['potential_annual_savings'] > 0:
            impact_panel = create_panel(
                f"[bold green]Business Impact Analysis[/bold green]\n\n"
                f"💰 [yellow]Optimization Potential:[/yellow] {format_cost(optimization['potential_annual_savings'], period='annual')}\n"
                f"📊 [yellow]Confidence Level:[/yellow] {optimization['confidence_level']}\n"
                f"🎯 [yellow]Implementation Approach:[/yellow] Systematic decommissioning with validation\n"
                f"⏱️  [yellow]Timeline:[/yellow] 3-4 weeks investigation + approval process\n\n"
                f"[blue]Strategic Value:[/blue] Establish investigation methodology for infrastructure optimization\n"
                f"[blue]Risk Assessment:[/blue] Medium risk - requires careful backup workflow validation",
                title="FinOps-25: Commvault Investigation Framework Results"
            )
            console.print(impact_panel)
        
        print_success(f"FinOps-25 analysis complete - {len(instances)} instances analyzed")


def analyze_commvault_ec2(profile: Optional[str] = None, account_id: str = "637423383469", 
                         region: str = "us-east-1") -> Dict:
    """
    Business wrapper function for FinOps-25 Commvault EC2 investigation.
    
    Args:
        profile: AWS profile name
        account_id: Target account (default: 637423383469)
        region: AWS region (default: us-east-1)
        
    Returns:
        Dict containing comprehensive analysis results
    """
    analyzer = CommvaultEC2Analysis(profile_name=profile, account_id=account_id)
    return analyzer.analyze_commvault_instances(region=region)


@click.command()
@click.option('--profile', help='AWS profile name')
@click.option('--account-id', default='637423383469', help='Commvault account ID')
@click.option('--region', default='us-east-1', help='AWS region')
@click.option('--output-file', help='Save results to file')
def main(profile, account_id, region, output_file):
    """FinOps-25: Commvault EC2 Investigation Framework - CLI interface."""
    try:
        results = analyze_commvault_ec2(profile, account_id, region)
        
        if output_file:
            import json
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print_success(f"Results saved to {output_file}")
        
    except Exception as e:
        print_error(f"Analysis failed: {e}")
        raise click.Abort()


if __name__ == '__main__':
    main()
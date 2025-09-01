#!/usr/bin/env python3
"""
Cost Optimization Module - Migrated from unSkript notebooks
===============================================

Objective: Stop idle EC2 instances and optimize AWS costs using CloudWatch metrics
Description: Find and stop EC2 instances with low CPU utilization to reduce costs
Step-by-Step:
1. Find Idle EC2 Instances (using CloudWatch CPU metrics)
2. Stop AWS Instances (with safety checks)
3. Report cost savings potential

Input: region, idle_cpu_threshold, idle_duration, instance_ids (optional)
Output: List of stopped instances and cost impact analysis
"""

from typing import Dict, List, Optional, Tuple, Any
import datetime
import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field
from dataclasses import dataclass

from ..common.rich_utils import (
    console, print_header, print_success, print_error, print_warning,
    create_table, create_progress_bar, format_cost
)

@dataclass
class IdleInstance:
    """Data class for idle EC2 instances"""
    instance_id: str
    region: str
    instance_type: str = ""
    avg_cpu_utilization: float = 0.0
    estimated_monthly_cost: float = 0.0
    tags: Dict[str, str] = Field(default_factory=dict)

@dataclass
class LowUsageVolume:
    """Data class for low usage EBS volumes"""
    volume_id: str
    region: str
    volume_type: str = ""
    size_gb: int = 0
    avg_usage: float = 0.0
    estimated_monthly_cost: float = 0.0
    creation_date: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)

@dataclass
class UnusedNATGateway:
    """Data class for unused NAT Gateways"""
    nat_gateway_id: str
    region: str
    vpc_id: str = ""
    state: str = ""
    estimated_monthly_cost: float = 45.0  # ~$45/month per NAT Gateway
    creation_date: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)

@dataclass 
class CostOptimizationResult:
    """Results from cost optimization operations"""
    stopped_instances: List[IdleInstance] = Field(default_factory=list)
    deleted_volumes: List[LowUsageVolume] = Field(default_factory=list)
    deleted_nat_gateways: List[UnusedNATGateway] = Field(default_factory=list)
    total_potential_savings: float = 0.0
    execution_summary: Dict[str, Any] = Field(default_factory=dict)
    
class AWSCostOptimizer:
    """
    Enterprise AWS Cost Optimization
    Migrated and enhanced from unSkript notebooks
    Handles EC2 instances, EBS volumes, and other cost optimization scenarios
    """
    
    def __init__(self, profile: Optional[str] = None):
        self.profile = profile
        self.session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        
    def find_idle_instances(
        self,
        region: str = "",
        idle_cpu_threshold: int = 5,
        idle_duration: int = 6
    ) -> Tuple[bool, Optional[List[IdleInstance]]]:
        """
        Find idle EC2 instances based on CPU utilization
        
        Migrated from: AWS_Stop_Idle_EC2_Instances.ipynb
        
        Args:
            region: AWS Region to scan (empty for all regions)
            idle_cpu_threshold: CPU threshold percentage (default 5%)
            idle_duration: Duration in hours to check (default 6h)
            
        Returns:
            Tuple (success, list_of_idle_instances)
        """
        print_header("Cost Optimizer - Idle Instance Detection", "v0.9.1")
        
        result = []
        regions_to_check = [region] if region else self._get_all_regions()
        
        with create_progress_bar() as progress:
            task_id = progress.add_task(
                f"Scanning {len(regions_to_check)} regions for idle instances...",
                total=len(regions_to_check)
            )
            
            for reg in regions_to_check:
                try:
                    idle_instances = self._scan_region_for_idle_instances(
                        reg, idle_cpu_threshold, idle_duration
                    )
                    result.extend(idle_instances)
                    progress.advance(task_id)
                    
                except Exception as e:
                    print_warning(f"Failed to scan region {reg}: {str(e)}")
                    progress.advance(task_id)
                    continue
        
        if result:
            print_success(f"Found {len(result)} idle instances across {len(regions_to_check)} regions")
            self._display_idle_instances_table(result)
            return (False, result)  # False = found results (unSkript convention)
        else:
            print_success("No idle instances found")
            return (True, None)  # True = no results (unSkript convention)
    
    def _scan_region_for_idle_instances(
        self,
        region: str,
        idle_cpu_threshold: int,
        idle_duration: int
    ) -> List[IdleInstance]:
        """Scan a specific region for idle instances"""
        
        result = []
        
        try:
            ec2_client = self.session.client('ec2', region_name=region)
            cloudwatch_client = self.session.client('cloudwatch', region_name=region)
            
            # Get all running instances
            response = ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    
                    if self._is_instance_idle(
                        instance_id, idle_cpu_threshold, idle_duration, cloudwatch_client
                    ):
                        # Extract tags
                        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                        
                        idle_instance = IdleInstance(
                            instance_id=instance_id,
                            region=region,
                            instance_type=instance.get('InstanceType', 'unknown'),
                            tags=tags
                        )
                        
                        # Calculate estimated cost (simplified - real implementation would use pricing API)
                        idle_instance.estimated_monthly_cost = self._estimate_instance_monthly_cost(
                            instance.get('InstanceType', 't3.micro')
                        )
                        
                        result.append(idle_instance)
                        
        except ClientError as e:
            print_warning(f"AWS API error in region {region}: {e}")
        except Exception as e:
            print_error(f"Unexpected error in region {region}: {e}")
            
        return result
    
    def _is_instance_idle(
        self,
        instance_id: str,
        idle_cpu_threshold: int,
        idle_duration: int,
        cloudwatch_client
    ) -> bool:
        """Check if instance is idle based on CPU metrics"""
        
        try:
            now = datetime.datetime.utcnow()
            start_time = now - datetime.timedelta(hours=idle_duration)
            
            cpu_stats = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start_time,
                EndTime=now,
                Period=3600,  # 1 hour periods
                Statistics=["Average"]
            )
            
            if not cpu_stats["Datapoints"]:
                return False  # No metrics = not idle (may be new instance)
            
            # Calculate average CPU across all data points
            avg_cpu = sum(
                datapoint["Average"] for datapoint in cpu_stats["Datapoints"]
            ) / len(cpu_stats["Datapoints"])
            
            return avg_cpu < idle_cpu_threshold
            
        except Exception as e:
            print_warning(f"Could not get metrics for {instance_id}: {e}")
            return False
    
    def stop_idle_instances(
        self,
        idle_instances: List[IdleInstance],
        dry_run: bool = True
    ) -> CostOptimizationResult:
        """
        Stop idle EC2 instances
        
        Migrated from: AWS_Stop_Idle_EC2_Instances.ipynb
        
        Args:
            idle_instances: List of idle instances to stop
            dry_run: If True, only simulate the action
            
        Returns:
            CostOptimizationResult with stopped instances and savings
        """
        print_header(f"Cost Optimizer - Stop Idle Instances ({'DRY RUN' if dry_run else 'LIVE'})")
        
        stopped_instances = []
        total_savings = 0.0
        errors = []
        
        with create_progress_bar() as progress:
            task_id = progress.add_task(
                "Processing idle instances...",
                total=len(idle_instances)
            )
            
            for instance in idle_instances:
                try:
                    if dry_run:
                        # Simulate stop operation
                        stopped_instances.append(instance)
                        total_savings += instance.estimated_monthly_cost
                        console.print(f"[yellow]DRY RUN: Would stop {instance.instance_id} "
                                    f"(${instance.estimated_monthly_cost:.2f}/month savings)[/yellow]")
                    else:
                        # Actually stop the instance
                        result = self._stop_single_instance(instance)
                        if result['success']:
                            stopped_instances.append(instance)
                            total_savings += instance.estimated_monthly_cost
                            print_success(f"Stopped {instance.instance_id} - "
                                        f"${instance.estimated_monthly_cost:.2f}/month saved")
                        else:
                            errors.append(f"{instance.instance_id}: {result['error']}")
                            print_error(f"Failed to stop {instance.instance_id}: {result['error']}")
                    
                    progress.advance(task_id)
                    
                except Exception as e:
                    errors.append(f"{instance.instance_id}: {str(e)}")
                    print_error(f"Error processing {instance.instance_id}: {e}")
                    progress.advance(task_id)
        
        # Create summary
        execution_summary = {
            'total_instances_processed': len(idle_instances),
            'successful_stops': len(stopped_instances),
            'errors': errors,
            'dry_run': dry_run,
            'estimated_annual_savings': total_savings * 12
        }
        
        result = CostOptimizationResult(
            stopped_instances=stopped_instances,
            total_potential_savings=total_savings,
            execution_summary=execution_summary
        )
        
        self._display_optimization_summary(result)
        return result
    
    def _stop_single_instance(self, instance: IdleInstance) -> Dict[str, Any]:
        """Stop a single EC2 instance"""
        
        try:
            ec2_client = self.session.client('ec2', region_name=instance.region)
            
            response = ec2_client.stop_instances(InstanceIds=[instance.instance_id])
            
            # Extract state information
            instance_state = {}
            for stopping_instance in response['StoppingInstances']:
                instance_state[stopping_instance['InstanceId']] = stopping_instance['CurrentState']
            
            return {
                'success': True,
                'state_info': instance_state,
                'instance_id': instance.instance_id
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f"AWS API Error: {e}",
                'instance_id': instance.instance_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {e}",
                'instance_id': instance.instance_id
            }
    
    def _get_all_regions(self) -> List[str]:
        """Get list of all AWS regions"""
        try:
            ec2_client = self.session.client('ec2', region_name='us-east-1')
            response = ec2_client.describe_regions()
            return [region['RegionName'] for region in response['Regions']]
        except Exception:
            # Fallback to common regions
            return [
                'us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1',
                'ap-southeast-1', 'ap-northeast-1'
            ]
    
    def _estimate_instance_monthly_cost(self, instance_type: str) -> float:
        """
        Estimate monthly cost for instance type
        Note: Real implementation should use AWS Pricing API
        """
        # Simplified cost estimates (USD per month for common instance types)
        cost_map = {
            't3.micro': 8.76,
            't3.small': 17.52,
            't3.medium': 35.04,
            't3.large': 70.08,
            't3.xlarge': 140.16,
            't3.2xlarge': 280.32,
            'm5.large': 87.60,
            'm5.xlarge': 175.20,
            'm5.2xlarge': 350.40,
            'c5.large': 78.84,
            'c5.xlarge': 157.68,
            'r5.large': 116.8,
            'r5.xlarge': 233.6,
        }
        
        return cost_map.get(instance_type, 50.0)  # Default estimate
    
    def _display_idle_instances_table(self, idle_instances: List[IdleInstance]):
        """Display idle instances in a formatted table"""
        
        table = create_table(
            title="Idle EC2 Instances Found",
            columns=[
                {"header": "Instance ID", "style": "cyan"},
                {"header": "Region", "style": "blue"},
                {"header": "Type", "style": "green"},
                {"header": "Est. Monthly Cost", "style": "red"},
                {"header": "Tags", "style": "yellow"},
            ]
        )
        
        for instance in idle_instances:
            # Format tags for display
            tag_display = ', '.join([f"{k}:{v}" for k, v in list(instance.tags.items())[:2]])
            if len(instance.tags) > 2:
                tag_display += f" (+{len(instance.tags)-2} more)"
            
            table.add_row(
                instance.instance_id,
                instance.region,
                instance.instance_type,
                format_cost(instance.estimated_monthly_cost),
                tag_display or "No tags"
            )
        
        console.print(table)
    
    def find_low_usage_volumes(
        self,
        region: str = "",
        threshold_days: int = 10
    ) -> Tuple[bool, Optional[List[LowUsageVolume]]]:
        """
        Find EBS volumes with low usage based on CloudWatch metrics
        
        Migrated from: AWS_Delete_EBS_Volumes_With_Low_Usage.ipynb
        
        Args:
            region: AWS Region to scan (empty for all regions)
            threshold_days: Days to look back for usage metrics
            
        Returns:
            Tuple (success, list_of_low_usage_volumes)
        """
        print_header("Cost Optimizer - Low Usage EBS Volume Detection", "v0.9.1")
        
        result = []
        regions_to_check = [region] if region else self._get_all_regions()
        
        with create_progress_bar() as progress:
            task_id = progress.add_task(
                f"Scanning {len(regions_to_check)} regions for low usage volumes...",
                total=len(regions_to_check)
            )
            
            for reg in regions_to_check:
                try:
                    low_usage_volumes = self._scan_region_for_low_usage_volumes(
                        reg, threshold_days
                    )
                    result.extend(low_usage_volumes)
                    progress.advance(task_id)
                    
                except Exception as e:
                    print_warning(f"Failed to scan region {reg}: {str(e)}")
                    progress.advance(task_id)
                    continue
        
        if result:
            print_success(f"Found {len(result)} low usage volumes across {len(regions_to_check)} regions")
            self._display_low_usage_volumes_table(result)
            return (False, result)  # False = found results (unSkript convention)
        else:
            print_success("No low usage volumes found")
            return (True, None)  # True = no results (unSkript convention)
    
    def _scan_region_for_low_usage_volumes(
        self,
        region: str,
        threshold_days: int
    ) -> List[LowUsageVolume]:
        """Scan a specific region for low usage EBS volumes"""
        
        result = []
        
        try:
            ec2_client = self.session.client('ec2', region_name=region)
            cloudwatch_client = self.session.client('cloudwatch', region_name=region)
            
            # Get all EBS volumes
            paginator = ec2_client.get_paginator('describe_volumes')
            
            now = datetime.datetime.utcnow()
            days_ago = now - datetime.timedelta(days=threshold_days)
            
            for page in paginator.paginate():
                for volume in page['Volumes']:
                    volume_id = volume['VolumeId']
                    
                    # Get CloudWatch metrics for volume usage
                    try:
                        metrics_response = cloudwatch_client.get_metric_statistics(
                            Namespace='AWS/EBS',
                            MetricName='VolumeReadBytes',  # Changed from VolumeUsage to more standard metric
                            Dimensions=[
                                {
                                    'Name': 'VolumeId',
                                    'Value': volume_id
                                }
                            ],
                            StartTime=days_ago,
                            EndTime=now,
                            Period=86400,  # Daily periods
                            Statistics=['Sum']
                        )
                        
                        # Calculate average usage
                        total_bytes = sum(dp['Sum'] for dp in metrics_response['Datapoints'])
                        avg_daily_bytes = total_bytes / max(len(metrics_response['Datapoints']), 1)
                        avg_daily_gb = avg_daily_bytes / (1024**3)  # Convert to GB
                        
                        # Consider volume as low usage if < 1GB daily average read
                        if avg_daily_gb < 1.0 or not metrics_response['Datapoints']:
                            
                            # Extract tags
                            tags = {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
                            
                            low_usage_volume = LowUsageVolume(
                                volume_id=volume_id,
                                region=region,
                                volume_type=volume.get('VolumeType', 'unknown'),
                                size_gb=volume.get('Size', 0),
                                avg_usage=avg_daily_gb,
                                creation_date=volume.get('CreateTime', '').isoformat() if volume.get('CreateTime') else None,
                                tags=tags
                            )
                            
                            # Calculate estimated cost
                            low_usage_volume.estimated_monthly_cost = self._estimate_ebs_monthly_cost(
                                volume.get('VolumeType', 'gp3'),
                                volume.get('Size', 0)
                            )
                            
                            result.append(low_usage_volume)
                            
                    except ClientError as e:
                        # Skip volumes we can't get metrics for
                        if 'Throttling' not in str(e):
                            print_warning(f"Could not get metrics for volume {volume_id}: {e}")
                        continue
                        
        except ClientError as e:
            print_warning(f"AWS API error in region {region}: {e}")
        except Exception as e:
            print_error(f"Unexpected error in region {region}: {e}")
            
        return result
    
    def delete_low_usage_volumes(
        self,
        low_usage_volumes: List[LowUsageVolume],
        create_snapshots: bool = True,
        dry_run: bool = True
    ) -> CostOptimizationResult:
        """
        Delete low usage EBS volumes (optionally creating snapshots first)
        
        Migrated from: AWS_Delete_EBS_Volumes_With_Low_Usage.ipynb
        
        Args:
            low_usage_volumes: List of volumes to delete
            create_snapshots: Create snapshots before deletion
            dry_run: If True, only simulate the action
            
        Returns:
            CostOptimizationResult with deleted volumes and savings
        """
        print_header(f"Cost Optimizer - Delete Low Usage Volumes ({'DRY RUN' if dry_run else 'LIVE'})")
        
        deleted_volumes = []
        total_savings = 0.0
        errors = []
        
        with create_progress_bar() as progress:
            task_id = progress.add_task(
                "Processing low usage volumes...",
                total=len(low_usage_volumes)
            )
            
            for volume in low_usage_volumes:
                try:
                    if dry_run:
                        # Simulate deletion
                        deleted_volumes.append(volume)
                        total_savings += volume.estimated_monthly_cost
                        console.print(f"[yellow]DRY RUN: Would delete {volume.volume_id} "
                                    f"({volume.size_gb}GB {volume.volume_type}) - "
                                    f"${volume.estimated_monthly_cost:.2f}/month savings[/yellow]")
                    else:
                        # Actually delete the volume
                        result = self._delete_single_volume(volume, create_snapshots)
                        if result['success']:
                            deleted_volumes.append(volume)
                            total_savings += volume.estimated_monthly_cost
                            print_success(f"Deleted {volume.volume_id} - "
                                        f"${volume.estimated_monthly_cost:.2f}/month saved")
                        else:
                            errors.append(f"{volume.volume_id}: {result['error']}")
                            print_error(f"Failed to delete {volume.volume_id}: {result['error']}")
                    
                    progress.advance(task_id)
                    
                except Exception as e:
                    errors.append(f"{volume.volume_id}: {str(e)}")
                    print_error(f"Error processing {volume.volume_id}: {e}")
                    progress.advance(task_id)
        
        # Create summary
        execution_summary = {
            'total_volumes_processed': len(low_usage_volumes),
            'successful_deletions': len(deleted_volumes),
            'errors': errors,
            'dry_run': dry_run,
            'snapshots_created': create_snapshots,
            'estimated_annual_savings': total_savings * 12
        }
        
        result = CostOptimizationResult(
            deleted_volumes=deleted_volumes,
            total_potential_savings=total_savings,
            execution_summary=execution_summary
        )
        
        self._display_volume_optimization_summary(result)
        return result
    
    def _delete_single_volume(self, volume: LowUsageVolume, create_snapshot: bool = True) -> Dict[str, Any]:
        """Delete a single EBS volume (with optional snapshot)"""
        
        try:
            ec2_client = self.session.client('ec2', region_name=volume.region)
            
            snapshot_id = None
            if create_snapshot:
                # Create snapshot first
                snapshot_response = ec2_client.create_snapshot(
                    VolumeId=volume.volume_id,
                    Description=f"Automated backup before deleting low usage volume {volume.volume_id}"
                )
                snapshot_id = snapshot_response['SnapshotId']
                print_success(f"Created snapshot {snapshot_id} for volume {volume.volume_id}")
            
            # Delete the volume
            ec2_client.delete_volume(VolumeId=volume.volume_id)
            
            return {
                'success': True,
                'snapshot_id': snapshot_id,
                'volume_id': volume.volume_id
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f"AWS API Error: {e}",
                'volume_id': volume.volume_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {e}",
                'volume_id': volume.volume_id
            }
    
    def _estimate_ebs_monthly_cost(self, volume_type: str, size_gb: int) -> float:
        """
        Estimate monthly cost for EBS volume
        Note: Real implementation should use AWS Pricing API
        """
        # Simplified cost estimates (USD per GB per month)
        cost_per_gb = {
            'gp3': 0.08,
            'gp2': 0.10,
            'io1': 0.125,
            'io2': 0.125,
            'st1': 0.045,
            'sc1': 0.025,
            'standard': 0.05
        }
        
        rate = cost_per_gb.get(volume_type, 0.08)  # Default to gp3
        return size_gb * rate
    
    def _display_low_usage_volumes_table(self, low_usage_volumes: List[LowUsageVolume]):
        """Display low usage volumes in a formatted table"""
        
        table = create_table(
            title="Low Usage EBS Volumes Found",
            columns=[
                {"header": "Volume ID", "style": "cyan"},
                {"header": "Region", "style": "blue"},
                {"header": "Type", "style": "green"},
                {"header": "Size (GB)", "style": "yellow"},
                {"header": "Est. Monthly Cost", "style": "red"},
                {"header": "Tags", "style": "magenta"},
            ]
        )
        
        for volume in low_usage_volumes:
            # Format tags for display
            tag_display = ', '.join([f"{k}:{v}" for k, v in list(volume.tags.items())[:2]])
            if len(volume.tags) > 2:
                tag_display += f" (+{len(volume.tags)-2} more)"
            
            table.add_row(
                volume.volume_id,
                volume.region,
                volume.volume_type,
                str(volume.size_gb),
                format_cost(volume.estimated_monthly_cost),
                tag_display or "No tags"
            )
        
        console.print(table)
    
    def _display_volume_optimization_summary(self, result: CostOptimizationResult):
        """Display volume optimization summary"""
        
        summary = result.execution_summary
        
        console.print()
        print_header("EBS Volume Optimization Summary")
        
        # Create summary table
        summary_table = create_table(
            title="Volume Optimization Results",
            columns=[
                {"header": "Metric", "style": "cyan"},
                {"header": "Value", "style": "green bold"}
            ]
        )
        
        summary_table.add_row("Volumes Processed", str(summary['total_volumes_processed']))
        summary_table.add_row("Successfully Deleted", str(summary['successful_deletions']))
        summary_table.add_row("Errors", str(len(summary['errors'])))
        summary_table.add_row("Snapshots Created", "Yes" if summary['snapshots_created'] else "No")
        summary_table.add_row("Monthly Savings", format_cost(result.total_potential_savings))
        summary_table.add_row("Annual Savings", format_cost(summary['estimated_annual_savings']))
        summary_table.add_row("Mode", "DRY RUN" if summary['dry_run'] else "LIVE EXECUTION")
        
        console.print(summary_table)
        
        if summary['errors']:
            print_warning(f"Encountered {len(summary['errors'])} errors:")
            for error in summary['errors']:
                console.print(f"  [red]• {error}[/red]")
    
    def find_unused_nat_gateways(
        self,
        region: str = "",
        number_of_days: int = 7
    ) -> Tuple[bool, Optional[List[UnusedNATGateway]]]:
        """
        Find unused NAT Gateways based on CloudWatch connection metrics
        
        Migrated from: AWS_Delete_Unused_NAT_Gateways.ipynb
        
        Args:
            region: AWS Region to scan (empty for all regions)
            number_of_days: Days to look back for usage metrics
            
        Returns:
            Tuple (success, list_of_unused_nat_gateways)
        """
        print_header("Cost Optimizer - Unused NAT Gateway Detection", "v0.9.1")
        
        result = []
        regions_to_check = [region] if region else self._get_all_regions()
        
        with create_progress_bar() as progress:
            task_id = progress.add_task(
                f"Scanning {len(regions_to_check)} regions for unused NAT Gateways...",
                total=len(regions_to_check)
            )
            
            for reg in regions_to_check:
                try:
                    unused_gateways = self._scan_region_for_unused_nat_gateways(
                        reg, number_of_days
                    )
                    result.extend(unused_gateways)
                    progress.advance(task_id)
                    
                except Exception as e:
                    print_warning(f"Failed to scan region {reg}: {str(e)}")
                    progress.advance(task_id)
                    continue
        
        if result:
            print_success(f"Found {len(result)} unused NAT Gateways across {len(regions_to_check)} regions")
            self._display_unused_nat_gateways_table(result)
            return (False, result)  # False = found results (unSkript convention)
        else:
            print_success("No unused NAT Gateways found")
            return (True, None)  # True = no results (unSkript convention)
    
    def _scan_region_for_unused_nat_gateways(
        self,
        region: str,
        number_of_days: int
    ) -> List[UnusedNATGateway]:
        """Scan a specific region for unused NAT Gateways"""
        
        result = []
        
        try:
            ec2_client = self.session.client('ec2', region_name=region)
            cloudwatch_client = self.session.client('cloudwatch', region_name=region)
            
            # Get all NAT Gateways
            response = ec2_client.describe_nat_gateways()
            
            end_time = datetime.datetime.utcnow()
            start_time = end_time - datetime.timedelta(days=number_of_days)
            
            for nat_gateway in response['NatGateways']:
                if nat_gateway['State'] == 'deleted':
                    continue
                    
                nat_gateway_id = nat_gateway['NatGatewayId']
                
                # Check if NAT Gateway is used based on connection metrics
                if not self._is_nat_gateway_used(
                    cloudwatch_client, nat_gateway, start_time, end_time, number_of_days
                ):
                    # Extract tags
                    tags = {tag['Key']: tag['Value'] for tag in nat_gateway.get('Tags', [])}
                    
                    unused_gateway = UnusedNATGateway(
                        nat_gateway_id=nat_gateway_id,
                        region=region,
                        vpc_id=nat_gateway.get('VpcId', ''),
                        state=nat_gateway.get('State', ''),
                        creation_date=nat_gateway.get('CreateTime', '').isoformat() if nat_gateway.get('CreateTime') else None,
                        tags=tags
                    )
                    
                    result.append(unused_gateway)
                        
        except ClientError as e:
            print_warning(f"AWS API error in region {region}: {e}")
        except Exception as e:
            print_error(f"Unexpected error in region {region}: {e}")
            
        return result
    
    def _is_nat_gateway_used(
        self,
        cloudwatch_client,
        nat_gateway: Dict[str, Any],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        number_of_days: int
    ) -> bool:
        """Check if NAT Gateway is used based on connection metrics"""
        
        try:
            if nat_gateway['State'] != 'available':
                return True  # Consider non-available gateways as "used"
            
            # Get ActiveConnectionCount metrics
            metrics_response = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/NATGateway',
                MetricName='ActiveConnectionCount',
                Dimensions=[
                    {
                        'Name': 'NatGatewayId',
                        'Value': nat_gateway['NatGatewayId']
                    },
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400 * number_of_days,  # Daily periods
                Statistics=['Sum']
            )
            
            datapoints = metrics_response.get('Datapoints', [])
            
            if not datapoints:
                return False  # No metrics = unused
                
            # Check if there are any active connections
            total_connections = sum(dp['Sum'] for dp in datapoints)
            return total_connections > 0
            
        except Exception as e:
            print_warning(f"Could not get metrics for NAT Gateway {nat_gateway['NatGatewayId']}: {e}")
            return True  # Assume used if we can't get metrics
    
    def delete_unused_nat_gateways(
        self,
        unused_nat_gateways: List[UnusedNATGateway],
        dry_run: bool = True
    ) -> CostOptimizationResult:
        """
        Delete unused NAT Gateways
        
        Migrated from: AWS_Delete_Unused_NAT_Gateways.ipynb
        
        Args:
            unused_nat_gateways: List of NAT Gateways to delete
            dry_run: If True, only simulate the action
            
        Returns:
            CostOptimizationResult with deleted NAT Gateways and savings
        """
        print_header(f"Cost Optimizer - Delete Unused NAT Gateways ({'DRY RUN' if dry_run else 'LIVE'})")
        
        deleted_gateways = []
        total_savings = 0.0
        errors = []
        
        with create_progress_bar() as progress:
            task_id = progress.add_task(
                "Processing unused NAT Gateways...",
                total=len(unused_nat_gateways)
            )
            
            for gateway in unused_nat_gateways:
                try:
                    if dry_run:
                        # Simulate deletion
                        deleted_gateways.append(gateway)
                        total_savings += gateway.estimated_monthly_cost
                        console.print(f"[yellow]DRY RUN: Would delete {gateway.nat_gateway_id} "
                                    f"in VPC {gateway.vpc_id} - "
                                    f"${gateway.estimated_monthly_cost:.2f}/month savings[/yellow]")
                    else:
                        # Actually delete the NAT Gateway
                        result = self._delete_single_nat_gateway(gateway)
                        if result['success']:
                            deleted_gateways.append(gateway)
                            total_savings += gateway.estimated_monthly_cost
                            print_success(f"Deleted {gateway.nat_gateway_id} - "
                                        f"${gateway.estimated_monthly_cost:.2f}/month saved")
                        else:
                            errors.append(f"{gateway.nat_gateway_id}: {result['error']}")
                            print_error(f"Failed to delete {gateway.nat_gateway_id}: {result['error']}")
                    
                    progress.advance(task_id)
                    
                except Exception as e:
                    errors.append(f"{gateway.nat_gateway_id}: {str(e)}")
                    print_error(f"Error processing {gateway.nat_gateway_id}: {e}")
                    progress.advance(task_id)
        
        # Create summary
        execution_summary = {
            'total_nat_gateways_processed': len(unused_nat_gateways),
            'successful_deletions': len(deleted_gateways),
            'errors': errors,
            'dry_run': dry_run,
            'estimated_annual_savings': total_savings * 12
        }
        
        result = CostOptimizationResult(
            deleted_nat_gateways=deleted_gateways,
            total_potential_savings=total_savings,
            execution_summary=execution_summary
        )
        
        self._display_nat_gateway_optimization_summary(result)
        return result
    
    def _delete_single_nat_gateway(self, gateway: UnusedNATGateway) -> Dict[str, Any]:
        """Delete a single NAT Gateway"""
        
        try:
            ec2_client = self.session.client('ec2', region_name=gateway.region)
            
            response = ec2_client.delete_nat_gateway(NatGatewayId=gateway.nat_gateway_id)
            
            return {
                'success': True,
                'response': response,
                'nat_gateway_id': gateway.nat_gateway_id
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f"AWS API Error: {e}",
                'nat_gateway_id': gateway.nat_gateway_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {e}",
                'nat_gateway_id': gateway.nat_gateway_id
            }
    
    def _display_unused_nat_gateways_table(self, unused_gateways: List[UnusedNATGateway]):
        """Display unused NAT Gateways in a formatted table"""
        
        table = create_table(
            title="Unused NAT Gateways Found",
            columns=[
                {"header": "NAT Gateway ID", "style": "cyan"},
                {"header": "Region", "style": "blue"},
                {"header": "VPC ID", "style": "green"},
                {"header": "State", "style": "yellow"},
                {"header": "Est. Monthly Cost", "style": "red"},
                {"header": "Tags", "style": "magenta"},
            ]
        )
        
        for gateway in unused_gateways:
            # Format tags for display
            tag_display = ', '.join([f"{k}:{v}" for k, v in list(gateway.tags.items())[:2]])
            if len(gateway.tags) > 2:
                tag_display += f" (+{len(gateway.tags)-2} more)"
            
            table.add_row(
                gateway.nat_gateway_id,
                gateway.region,
                gateway.vpc_id,
                gateway.state,
                format_cost(gateway.estimated_monthly_cost),
                tag_display or "No tags"
            )
        
        console.print(table)
    
    def _display_nat_gateway_optimization_summary(self, result: CostOptimizationResult):
        """Display NAT Gateway optimization summary"""
        
        summary = result.execution_summary
        
        console.print()
        print_header("NAT Gateway Optimization Summary")
        
        # Create summary table
        summary_table = create_table(
            title="NAT Gateway Optimization Results",
            columns=[
                {"header": "Metric", "style": "cyan"},
                {"header": "Value", "style": "green bold"}
            ]
        )
        
        summary_table.add_row("NAT Gateways Processed", str(summary['total_nat_gateways_processed']))
        summary_table.add_row("Successfully Deleted", str(summary['successful_deletions']))
        summary_table.add_row("Errors", str(len(summary['errors'])))
        summary_table.add_row("Monthly Savings", format_cost(result.total_potential_savings))
        summary_table.add_row("Annual Savings", format_cost(summary['estimated_annual_savings']))
        summary_table.add_row("Mode", "DRY RUN" if summary['dry_run'] else "LIVE EXECUTION")
        
        console.print(summary_table)
        
        if summary['errors']:
            print_warning(f"Encountered {len(summary['errors'])} errors:")
            for error in summary['errors']:
                console.print(f"  [red]• {error}[/red]")
    
    def _display_optimization_summary(self, result: CostOptimizationResult):
        """Display cost optimization summary"""
        
        summary = result.execution_summary
        
        console.print()
        print_header("Cost Optimization Summary")
        
        # Create summary table
        summary_table = create_table(
            title="Optimization Results",
            columns=[
                {"header": "Metric", "style": "cyan"},
                {"header": "Value", "style": "green bold"}
            ]
        )
        
        summary_table.add_row("Instances Processed", str(summary['total_instances_processed']))
        summary_table.add_row("Successfully Stopped", str(summary['successful_stops']))
        summary_table.add_row("Errors", str(len(summary['errors'])))
        summary_table.add_row("Monthly Savings", format_cost(result.total_potential_savings))
        summary_table.add_row("Annual Savings", format_cost(summary['estimated_annual_savings']))
        summary_table.add_row("Mode", "DRY RUN" if summary['dry_run'] else "LIVE EXECUTION")
        
        console.print(summary_table)
        
        if summary['errors']:
            print_warning(f"Encountered {len(summary['errors'])} errors:")
            for error in summary['errors']:
                console.print(f"  [red]• {error}[/red]")


# CLI Interface Functions (compatible with existing runbooks architecture)
def find_and_stop_idle_instances(
    profile: Optional[str] = None,
    region: str = "",
    idle_cpu_threshold: int = 5,
    idle_duration: int = 6,
    instance_ids: Optional[List[str]] = None,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Main function for cost optimization - find and stop idle EC2 instances
    
    This function replicates the complete unSkript notebook workflow
    """
    
    optimizer = AWSCostOptimizer(profile=profile)
    
    # Step 1: Find idle instances (or use provided instance IDs)
    if instance_ids:
        print_warning("Using provided instance IDs - skipping idle detection")
        # Create IdleInstance objects from provided IDs
        idle_instances = []
        for instance_id in instance_ids:
            idle_instance = IdleInstance(
                instance_id=instance_id,
                region=region,
                estimated_monthly_cost=50.0  # Default estimate
            )
            idle_instances.append(idle_instance)
        success = False
        found_instances = idle_instances
    else:
        success, found_instances = optimizer.find_idle_instances(
            region=region,
            idle_cpu_threshold=idle_cpu_threshold,
            idle_duration=idle_duration
        )
    
    if success or not found_instances:  # No idle instances found
        print_success("No idle instances to process")
        return {
            'idle_instances_found': 0,
            'instances_stopped': 0,
            'potential_savings': 0.0,
            'status': 'completed'
        }
    
    # Step 2: Stop idle instances
    optimization_result = optimizer.stop_idle_instances(
        idle_instances=found_instances,
        dry_run=dry_run
    )
    
    return {
        'idle_instances_found': len(found_instances),
        'instances_stopped': len(optimization_result.stopped_instances),
        'potential_monthly_savings': optimization_result.total_potential_savings,
        'potential_annual_savings': optimization_result.execution_summary['estimated_annual_savings'],
        'dry_run': dry_run,
        'status': 'completed',
        'details': optimization_result.execution_summary
    }


# Additional CLI Functions for EBS Volume Optimization
def find_and_delete_low_usage_volumes(
    profile: Optional[str] = None,
    region: str = "",
    threshold_days: int = 10,
    volume_ids: Optional[List[str]] = None,
    create_snapshots: bool = True,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Main function for EBS cost optimization - find and delete low usage volumes
    
    Migrated from: AWS_Delete_EBS_Volumes_With_Low_Usage.ipynb
    """
    
    optimizer = AWSCostOptimizer(profile=profile)
    
    # Step 1: Find low usage volumes (or use provided volume IDs)
    if volume_ids:
        print_warning("Using provided volume IDs - skipping usage detection")
        # Create LowUsageVolume objects from provided IDs
        low_usage_volumes = []
        for volume_id in volume_ids:
            low_usage_volume = LowUsageVolume(
                volume_id=volume_id,
                region=region,
                estimated_monthly_cost=5.0  # Default estimate
            )
            low_usage_volumes.append(low_usage_volume)
        success = False
        found_volumes = low_usage_volumes
    else:
        success, found_volumes = optimizer.find_low_usage_volumes(
            region=region,
            threshold_days=threshold_days
        )
    
    if success or not found_volumes:  # No low usage volumes found
        print_success("No low usage volumes to process")
        return {
            'low_usage_volumes_found': 0,
            'volumes_deleted': 0,
            'potential_savings': 0.0,
            'status': 'completed'
        }
    
    # Step 2: Delete low usage volumes
    optimization_result = optimizer.delete_low_usage_volumes(
        low_usage_volumes=found_volumes,
        create_snapshots=create_snapshots,
        dry_run=dry_run
    )
    
    return {
        'low_usage_volumes_found': len(found_volumes),
        'volumes_deleted': len(optimization_result.deleted_volumes),
        'potential_monthly_savings': optimization_result.total_potential_savings,
        'potential_annual_savings': optimization_result.execution_summary['estimated_annual_savings'],
        'snapshots_created': create_snapshots,
        'dry_run': dry_run,
        'status': 'completed',
        'details': optimization_result.execution_summary
    }


def comprehensive_cost_optimization(
    profile: Optional[str] = None,
    region: str = "",
    idle_cpu_threshold: int = 5,
    idle_duration: int = 6,
    volume_threshold_days: int = 10,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Comprehensive cost optimization combining EC2 and EBS optimizations
    
    This combines multiple unSkript notebooks:
    - AWS_Stop_Idle_EC2_Instances.ipynb 
    - AWS_Delete_EBS_Volumes_With_Low_Usage.ipynb
    """
    
    print_header("Comprehensive AWS Cost Optimization", "v0.9.1")
    
    total_monthly_savings = 0.0
    total_annual_savings = 0.0
    results = {}
    
    # Step 1: EC2 Instance Optimization
    try:
        print_header("Phase 1: EC2 Instance Optimization")
        ec2_result = find_and_stop_idle_instances(
            profile=profile,
            region=region,
            idle_cpu_threshold=idle_cpu_threshold,
            idle_duration=idle_duration,
            dry_run=dry_run
        )
        results['ec2_optimization'] = ec2_result
        total_monthly_savings += ec2_result.get('potential_monthly_savings', 0.0)
        total_annual_savings += ec2_result.get('potential_annual_savings', 0.0)
        
    except Exception as e:
        print_error(f"EC2 optimization failed: {e}")
        results['ec2_optimization'] = {'error': str(e)}
    
    # Step 2: EBS Volume Optimization  
    try:
        print_header("Phase 2: EBS Volume Optimization")
        ebs_result = find_and_delete_low_usage_volumes(
            profile=profile,
            region=region,
            threshold_days=volume_threshold_days,
            create_snapshots=True,
            dry_run=dry_run
        )
        results['ebs_optimization'] = ebs_result
        total_monthly_savings += ebs_result.get('potential_monthly_savings', 0.0)
        total_annual_savings += ebs_result.get('potential_annual_savings', 0.0)
        
    except Exception as e:
        print_error(f"EBS optimization failed: {e}")
        results['ebs_optimization'] = {'error': str(e)}
    
    # Summary
    print_header("Comprehensive Cost Optimization Summary")
    
    summary_table = create_table(
        title="Total Cost Optimization Impact",
        columns=[
            {"header": "Resource Type", "style": "cyan"},
            {"header": "Items Found", "style": "yellow"},  
            {"header": "Items Processed", "style": "green"},
            {"header": "Monthly Savings", "style": "red bold"},
        ]
    )
    
    # EC2 Summary
    ec2_found = results.get('ec2_optimization', {}).get('idle_instances_found', 0)
    ec2_stopped = results.get('ec2_optimization', {}).get('instances_stopped', 0)
    ec2_savings = results.get('ec2_optimization', {}).get('potential_monthly_savings', 0.0)
    
    summary_table.add_row(
        "EC2 Instances", 
        str(ec2_found), 
        str(ec2_stopped),
        format_cost(ec2_savings)
    )
    
    # EBS Summary
    ebs_found = results.get('ebs_optimization', {}).get('low_usage_volumes_found', 0)
    ebs_deleted = results.get('ebs_optimization', {}).get('volumes_deleted', 0)
    ebs_savings = results.get('ebs_optimization', {}).get('potential_monthly_savings', 0.0)
    
    summary_table.add_row(
        "EBS Volumes",
        str(ebs_found),
        str(ebs_deleted), 
        format_cost(ebs_savings)
    )
    
    # Total
    summary_table.add_row(
        "[bold]TOTAL[/bold]",
        "[bold]" + str(ec2_found + ebs_found) + "[/bold]",
        "[bold]" + str(ec2_stopped + ebs_deleted) + "[/bold]",
        "[bold]" + format_cost(total_monthly_savings) + "[/bold]"
    )
    
    console.print(summary_table)
    
    print_success(f"Total Annual Savings Potential: {format_cost(total_annual_savings)}")
    
    if dry_run:
        print_warning("This was a DRY RUN. No actual changes were made.")
    
    return {
        'total_monthly_savings': total_monthly_savings,
        'total_annual_savings': total_annual_savings,
        'ec2_optimization': results.get('ec2_optimization', {}),
        'ebs_optimization': results.get('ebs_optimization', {}),
        'dry_run': dry_run,
        'status': 'completed'
    }


if __name__ == "__main__":
    # Direct execution for testing
    print("Testing Cost Optimization Module...")
    
    # Test 1: EC2 Instance Optimization
    print("\n=== Testing EC2 Optimization ===")
    ec2_result = find_and_stop_idle_instances(
        region="us-east-1",
        idle_cpu_threshold=10,
        idle_duration=24,
        dry_run=True
    )
    print(f"EC2 Result: {ec2_result}")
    
    # Test 2: EBS Volume Optimization  
    print("\n=== Testing EBS Optimization ===")
    ebs_result = find_and_delete_low_usage_volumes(
        region="us-east-1",
        threshold_days=30,
        dry_run=True
    )
    print(f"EBS Result: {ebs_result}")
    
    # Test 3: Comprehensive Optimization
    print("\n=== Testing Comprehensive Optimization ===")
    comprehensive_result = comprehensive_cost_optimization(
        region="us-east-1",
        dry_run=True
    )
    print(f"Comprehensive Result: {comprehensive_result}")
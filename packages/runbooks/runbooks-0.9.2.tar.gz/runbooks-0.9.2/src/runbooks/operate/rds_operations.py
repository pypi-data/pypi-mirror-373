"""
AWS RDS Operations for cost optimization and security compliance.

This module provides comprehensive RDS database management capabilities including
cost optimization through underutilized instance cleanup, security compliance
through access control automation, and reserved instance management.

Extracted from unSkript notebooks and enhanced with enterprise patterns.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table

from runbooks.common.aws_helpers import get_paginated_results
from runbooks.common.profile_utils import get_profile_for_operation
from runbooks.common.rich_utils import (
    console,
    create_table,
    format_cost,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)
from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus


class RDSOperations(BaseOperation):
    """AWS RDS operations for cost optimization and security compliance."""
    
    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None, dry_run: bool = True):
        """Initialize RDS operations."""
        super().__init__(profile=profile, region=region, dry_run=dry_run)
        self.service = 'rds'
        self.supported_operations = {
            'find_low_cpu_instances',
            'delete_instance_safely', 
            'get_publicly_accessible_instances',
            'secure_public_instances',
            'analyze_reserved_instance_opportunities',
            'get_instance_metrics',
            'list_instances',
            'get_instance_details'
        }

    def find_low_cpu_instances(
        self, 
        context: OperationContext, 
        utilization_threshold: float = 10.0,
        duration_minutes: int = 60
    ) -> List[OperationResult]:
        """
        Find RDS instances with low CPU utilization.
        
        Extracted from: AWS_Delete_RDS_Instances_with_Low_CPU_Utilization.ipynb
        
        Args:
            context: Operation context
            utilization_threshold: CPU threshold percentage (default 10%)
            duration_minutes: Duration to analyze metrics (default 60 minutes)
            
        Returns:
            List of operation results with low CPU instances
        """
        print_header("RDS Low CPU Analysis", "Cost Optimization")
        
        results = []
        regions_to_check = [context.region] if context.region else self._get_all_regions()
        
        for region in track(regions_to_check, description="Analyzing regions..."):
            try:
                # Get RDS client for region
                session = self._get_aws_session(context.profile)
                rds_client = session.client('rds', region_name=region)
                cloudwatch_client = session.client('cloudwatch', region_name=region)
                
                # Get all RDS instances in region
                instances = get_paginated_results(
                    rds_client, 
                    'describe_db_instances',
                    'DBInstances'
                )
                
                region_low_cpu_instances = []
                
                for db in instances:
                    try:
                        db_identifier = db['DBInstanceIdentifier']
                        
                        # Get CPU metrics from CloudWatch
                        end_time = datetime.utcnow()
                        start_time = end_time - timedelta(minutes=duration_minutes)
                        
                        response = cloudwatch_client.get_metric_data(
                            MetricDataQueries=[
                                {
                                    'Id': 'cpu',
                                    'MetricStat': {
                                        'Metric': {
                                            'Namespace': 'AWS/RDS',
                                            'MetricName': 'CPUUtilization',
                                            'Dimensions': [
                                                {
                                                    'Name': 'DBInstanceIdentifier',
                                                    'Value': db_identifier
                                                }
                                            ]
                                        },
                                        'Period': 3600,  # 1 hour periods
                                        'Stat': 'Average'
                                    },
                                    'ReturnData': True
                                }
                            ],
                            StartTime=start_time,
                            EndTime=end_time
                        )
                        
                        # Process CPU utilization data
                        if (response['MetricDataResults'] and 
                            response['MetricDataResults'][0]['Values']):
                            
                            cpu_values = response['MetricDataResults'][0]['Values']
                            avg_cpu = sum(cpu_values) / len(cpu_values)
                            
                            if avg_cpu < utilization_threshold:
                                instance_info = {
                                    'region': region,
                                    'instance_id': db_identifier,
                                    'instance_class': db.get('DBInstanceClass'),
                                    'engine': db.get('Engine'),
                                    'avg_cpu_utilization': round(avg_cpu, 2),
                                    'status': db.get('DBInstanceStatus'),
                                    'creation_time': db.get('InstanceCreateTime')
                                }
                                region_low_cpu_instances.append(instance_info)
                                
                    except ClientError as e:
                        print_warning(f"Could not get metrics for {db_identifier}: {e}")
                        continue
                        
                if region_low_cpu_instances:
                    results.append(OperationResult(
                        status=OperationStatus.SUCCESS,
                        data=region_low_cpu_instances,
                        metadata={
                            'region': region,
                            'threshold': utilization_threshold,
                            'duration_minutes': duration_minutes,
                            'instances_found': len(region_low_cpu_instances)
                        }
                    ))
                    
                    print_info(f"Found {len(region_low_cpu_instances)} low CPU instances in {region}")
                    
            except ClientError as e:
                print_error(f"Error analyzing region {region}: {e}")
                results.append(OperationResult(
                    status=OperationStatus.FAILED,
                    error=str(e),
                    metadata={'region': region}
                ))
                
        if results:
            total_instances = sum(
                len(r.data) for r in results 
                if r.status == OperationStatus.SUCCESS and r.data
            )
            print_success(f"Analysis complete. Found {total_instances} instances below {utilization_threshold}% CPU")
        else:
            print_info("No instances found below threshold")
            
        return results

    def get_publicly_accessible_instances(self, context: OperationContext) -> List[OperationResult]:
        """
        Get all publicly accessible RDS instances.
        
        Extracted from: AWS_Secure_Publicly_Accessible_RDS_Instances.ipynb
        
        Args:
            context: Operation context
            
        Returns:
            List of operation results with publicly accessible instances
        """
        print_header("RDS Public Access Analysis", "Security Compliance")
        
        results = []
        regions_to_check = [context.region] if context.region else self._get_all_regions()
        
        for region in track(regions_to_check, description="Scanning regions..."):
            try:
                session = self._get_aws_session(context.profile)
                rds_client = session.client('rds', region_name=region)
                
                # Get all RDS instances
                instances = get_paginated_results(
                    rds_client,
                    'describe_db_instances', 
                    'DBInstances'
                )
                
                public_instances = []
                
                for db in instances:
                    if db.get('PubliclyAccessible', False):
                        instance_info = {
                            'region': region,
                            'instance_id': db['DBInstanceIdentifier'],
                            'instance_class': db.get('DBInstanceClass'),
                            'engine': db.get('Engine'),
                            'status': db.get('DBInstanceStatus'),
                            'endpoint': db.get('Endpoint', {}).get('Address'),
                            'port': db.get('Endpoint', {}).get('Port'),
                            'vpc_id': db.get('DBSubnetGroup', {}).get('VpcId') if db.get('DBSubnetGroup') else None
                        }
                        public_instances.append(instance_info)
                        
                if public_instances:
                    results.append(OperationResult(
                        status=OperationStatus.SUCCESS,
                        data=public_instances,
                        metadata={
                            'region': region,
                            'public_instances_found': len(public_instances)
                        }
                    ))
                    print_warning(f"Found {len(public_instances)} publicly accessible instances in {region}")
                    
            except ClientError as e:
                print_error(f"Error scanning region {region}: {e}")
                results.append(OperationResult(
                    status=OperationStatus.FAILED,
                    error=str(e),
                    metadata={'region': region}
                ))
                
        total_public = sum(
            len(r.data) for r in results 
            if r.status == OperationStatus.SUCCESS and r.data
        )
        
        if total_public > 0:
            print_warning(f"Security Alert: {total_public} publicly accessible RDS instances found")
        else:
            print_success("No publicly accessible RDS instances found")
            
        return results

    def secure_public_instances(
        self, 
        context: OperationContext, 
        instance_identifiers: List[str]
    ) -> List[OperationResult]:
        """
        Make RDS instances not publicly accessible.
        
        Extracted from: AWS_Secure_Publicly_Accessible_RDS_Instances.ipynb
        
        Args:
            context: Operation context
            instance_identifiers: List of instance identifiers to secure
            
        Returns:
            List of operation results
        """
        print_header("RDS Security Remediation", "Making Instances Private")
        
        if self.dry_run:
            print_info("DRY RUN: Would secure the following instances:")
            for instance_id in instance_identifiers:
                print_info(f"  - {instance_id} (would set PubliclyAccessible=False)")
            return [OperationResult(
                status=OperationStatus.SUCCESS,
                data={'dry_run': True, 'instances': instance_identifiers},
                metadata={'operation': 'secure_instances_dry_run'}
            )]
        
        results = []
        
        for instance_identifier in track(instance_identifiers, description="Securing instances..."):
            try:
                # Determine region for instance (simplified - assumes current region)
                session = self._get_aws_session(context.profile)
                rds_client = session.client('rds', region_name=context.region)
                
                # Modify instance to make it not publicly accessible
                response = rds_client.modify_db_instance(
                    DBInstanceIdentifier=instance_identifier,
                    PubliclyAccessible=False
                )
                
                results.append(OperationResult(
                    status=OperationStatus.SUCCESS,
                    data={'instance_id': instance_identifier, 'response': response},
                    metadata={'operation': 'modify_public_access'}
                ))
                
                print_success(f"Initiated security modification for {instance_identifier}")
                
            except ClientError as e:
                print_error(f"Failed to secure instance {instance_identifier}: {e}")
                results.append(OperationResult(
                    status=OperationStatus.FAILED,
                    error=str(e),
                    metadata={'instance_id': instance_identifier}
                ))
                
        return results

    def analyze_reserved_instance_opportunities(
        self, 
        context: OperationContext,
        threshold_days: int = 30
    ) -> List[OperationResult]:
        """
        Find long-running instances without reserved instances.
        
        Extracted from: AWS_Purchase_Reserved_Instances_For_Long_Running_RDS_Instances.ipynb
        
        Args:
            context: Operation context
            threshold_days: Minimum days running to consider for RI (default 30)
            
        Returns:
            List of operation results with RI opportunities
        """
        print_header("RDS Reserved Instance Analysis", "Cost Optimization")
        
        results = []
        regions_to_check = [context.region] if context.region else self._get_all_regions()
        
        for region in track(regions_to_check, description="Analyzing RI opportunities..."):
            try:
                session = self._get_aws_session(context.profile)
                rds_client = session.client('rds', region_name=region)
                
                # Get reserved instances per region
                reserved_response = rds_client.describe_reserved_db_instances()
                reserved_by_class = {}
                
                for reserved in reserved_response.get('ReservedDBInstances', []):
                    instance_class = reserved['DBInstanceClass']
                    reserved_by_class[instance_class] = reserved_by_class.get(instance_class, 0) + reserved.get('DBInstanceCount', 1)
                
                # Get running instances
                instances = get_paginated_results(
                    rds_client,
                    'describe_db_instances',
                    'DBInstances'
                )
                
                ri_opportunities = []
                
                for db in instances:
                    if db.get('DBInstanceStatus') == 'available':
                        # Check if instance has been running long enough
                        create_time = db.get('InstanceCreateTime')
                        if create_time:
                            uptime = datetime.now(timezone.utc) - create_time
                            if uptime > timedelta(days=threshold_days):
                                
                                instance_class = db.get('DBInstanceClass')
                                reserved_count = reserved_by_class.get(instance_class, 0)
                                
                                # Count running instances of this class
                                running_count = sum(
                                    1 for inst in instances 
                                    if (inst.get('DBInstanceClass') == instance_class and 
                                        inst.get('DBInstanceStatus') == 'available')
                                )
                                
                                if running_count > reserved_count:
                                    ri_opportunity = {
                                        'region': region,
                                        'instance_id': db['DBInstanceIdentifier'],
                                        'instance_class': instance_class,
                                        'engine': db.get('Engine'),
                                        'running_days': uptime.days,
                                        'reserved_count': reserved_count,
                                        'running_count': running_count,
                                        'ri_gap': running_count - reserved_count
                                    }
                                    ri_opportunities.append(ri_opportunity)
                                    
                if ri_opportunities:
                    results.append(OperationResult(
                        status=OperationStatus.SUCCESS,
                        data=ri_opportunities,
                        metadata={
                            'region': region,
                            'threshold_days': threshold_days,
                            'opportunities_found': len(ri_opportunities)
                        }
                    ))
                    
                    print_info(f"Found {len(ri_opportunities)} RI opportunities in {region}")
                    
            except ClientError as e:
                print_error(f"Error analyzing RI opportunities in {region}: {e}")
                results.append(OperationResult(
                    status=OperationStatus.FAILED,
                    error=str(e),
                    metadata={'region': region}
                ))
                
        return results

    def delete_instance_safely(
        self, 
        context: OperationContext,
        instance_identifier: str,
        skip_final_snapshot: bool = False
    ) -> OperationResult:
        """
        Safely delete an RDS instance with proper safeguards.
        
        Extracted from: AWS_Delete_RDS_Instances_with_Low_CPU_Utilization.ipynb
        
        Args:
            context: Operation context
            instance_identifier: RDS instance identifier
            skip_final_snapshot: Whether to skip final snapshot (default False)
            
        Returns:
            Operation result
        """
        print_header(f"RDS Instance Deletion", f"Instance: {instance_identifier}")
        
        if self.dry_run:
            print_warning(f"DRY RUN: Would delete RDS instance {instance_identifier}")
            return OperationResult(
                status=OperationStatus.SUCCESS,
                data={'dry_run': True, 'instance_id': instance_identifier},
                metadata={'operation': 'delete_instance_dry_run'}
            )
        
        # Safety confirmation for destructive operation
        print_warning(f"DESTRUCTIVE OPERATION: Preparing to delete RDS instance {instance_identifier}")
        
        try:
            session = self._get_aws_session(context.profile)
            rds_client = session.client('rds', region_name=context.region)
            
            delete_params = {
                'DBInstanceIdentifier': instance_identifier,
                'SkipFinalSnapshot': skip_final_snapshot
            }
            
            if not skip_final_snapshot:
                # Create snapshot with timestamp
                timestamp = datetime.utcnow().strftime('%Y-%m-%d-%H-%M')
                delete_params['FinalDBSnapshotIdentifier'] = f"{instance_identifier}-final-{timestamp}"
                print_info(f"Creating final snapshot: {delete_params['FinalDBSnapshotIdentifier']}")
            
            response = rds_client.delete_db_instance(**delete_params)
            
            print_success(f"RDS instance {instance_identifier} deletion initiated")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                data={'instance_id': instance_identifier, 'response': response},
                metadata={'operation': 'delete_instance', 'final_snapshot': not skip_final_snapshot}
            )
            
        except ClientError as e:
            print_error(f"Failed to delete instance {instance_identifier}: {e}")
            return OperationResult(
                status=OperationStatus.FAILED,
                error=str(e),
                metadata={'instance_id': instance_identifier}
            )

    def execute_operation(self, operation: str, context: OperationContext, **kwargs) -> List[OperationResult]:
        """Execute the specified RDS operation."""
        if operation not in self.supported_operations:
            raise ValueError(f"Unsupported operation: {operation}")
            
        operation_method = getattr(self, operation)
        return operation_method(context, **kwargs)

    def _get_all_regions(self) -> List[str]:
        """Get all available AWS regions for RDS."""
        try:
            session = boto3.Session()
            return session.get_available_regions('rds')
        except Exception:
            # Fallback to common regions if API call fails
            return [
                'us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1',
                'us-west-1', 'eu-central-1', 'ap-southeast-2'
            ]

    def _get_aws_session(self, profile: Optional[str] = None) -> boto3.Session:
        """Get AWS session with proper profile handling."""
        if profile:
            return boto3.Session(profile_name=profile)
        return boto3.Session()
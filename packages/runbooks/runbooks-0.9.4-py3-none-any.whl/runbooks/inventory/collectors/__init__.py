"""
AWS resource collectors organized by service category.

This module provides specialized collectors for different AWS service categories,
each implementing a common interface for resource discovery and inventory.

Categories:
    - aws_compute: EC2, Lambda, ECS, Batch, Fargate
    - aws_storage: S3, EBS, EFS, FSx
    - aws_database: RDS, DynamoDB, ElastiCache, Redshift
    - aws_network: VPC, ELB, CloudFront, Route53, API Gateway
    - aws_security: IAM, GuardDuty, Config, Security Hub, WAF
    - aws_management: CloudFormation, Organizations, Control Tower, SSM
"""

from runbooks.inventory.collectors.aws_compute import ComputeResourceCollector
from runbooks.inventory.collectors.aws_management import ManagementResourceCollector, OrganizationsManager
from runbooks.inventory.collectors.aws_networking import SubnetCollector, VPCCollector
from runbooks.inventory.collectors.base import BaseResourceCollector

__all__ = [
    "BaseResourceCollector",
    "ComputeResourceCollector",
    "VPCCollector",
    "SubnetCollector",
    "ManagementResourceCollector",
    "OrganizationsManager",
]

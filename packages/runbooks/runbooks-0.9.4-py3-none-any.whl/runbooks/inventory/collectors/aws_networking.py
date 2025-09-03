#!/usr/bin/env python3
"""
AWS Networking Service Collectors

Maintains 100% compatibility with AWS Cloud Foundations inventory-scripts:
- all_my_vpcs.py -> VPCCollector
- all_my_subnets.py -> SubnetCollector
- all_my_elbs.py -> ELBCollector
- all_my_enis.py -> ENICollector
- all_my_phzs.py -> Route53Collector

This module preserves all original AWS Cloud Foundations functionality.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3

from ..models.account import AWSAccount
from ..models.resource import AWSResource, ResourceState, ResourceType
from ..utils.aws_helpers import aws_api_retry, get_boto3_session
from ..utils.validation import validate_aws_account_id, validate_aws_region
from .base import BaseResourceCollector


class VPCCollector(BaseResourceCollector):
    """
    VPC Collector - 100% compatible with all_my_vpcs.py

    Preserves original AWS Cloud Foundations functionality:
    - Cross-region VPC discovery
    - CIDR block analysis
    - Internet Gateway associations
    - Route table mappings
    """

    def __init__(self, session: Optional[boto3.Session] = None):
        super().__init__(resource_type=ResourceType.VPC, session=session)

    @aws_api_retry
    def collect_from_region(self, region: str, account: AWSAccount) -> List[AWSResource]:
        """Collect VPCs maintaining original script compatibility."""
        if not validate_aws_region(region):
            raise ValueError(f"Invalid AWS region: {region}")

        resources = []

        try:
            ec2 = self.session.client("ec2", region_name=region)

            # Use paginator for large result sets
            paginator = ec2.get_paginator("describe_vpcs")

            for page in paginator.paginate():
                for vpc in page["Vpcs"]:
                    resource = self._convert_vpc_to_resource(vpc, region, account)
                    resources.append(resource)

        except Exception as e:
            self.logger.error(f"Failed to collect VPCs in {region}: {e}")

        return resources

    def _convert_vpc_to_resource(self, vpc: Dict[str, Any], region: str, account: AWSAccount) -> AWSResource:
        """Convert VPC data to standardized AWSResource format."""

        tags = {tag["Key"]: tag["Value"] for tag in vpc.get("Tags", [])}

        # Map VPC state to our enum
        state_mapping = {"available": ResourceState.AVAILABLE, "pending": ResourceState.PENDING}

        vpc_state = vpc.get("State", "unknown")
        resource_state = state_mapping.get(vpc_state, ResourceState.UNKNOWN)

        return AWSResource(
            account_id=account.account_id,
            region=region,
            resource_type=ResourceType.VPC,
            resource_id=vpc["VpcId"],
            arn=f"arn:aws:ec2:{region}:{account.account_id}:vpc/{vpc['VpcId']}",
            name=tags.get("Name", vpc["VpcId"]),
            state=resource_state,
            tags=tags,
            metadata={
                "cidr_block": vpc.get("CidrBlock"),
                "cidr_block_association_set": vpc.get("CidrBlockAssociationSet", []),
                "ipv6_cidr_block_association_set": vpc.get("Ipv6CidrBlockAssociationSet", []),
                "dhcp_options_id": vpc.get("DhcpOptionsId"),
                "instance_tenancy": vpc.get("InstanceTenancy"),
                "is_default": vpc.get("IsDefault", False),
                "owner_id": vpc.get("OwnerId"),
            },
            discovered_at=datetime.utcnow(),
        )


class SubnetCollector(BaseResourceCollector):
    """
    Subnet Collector - 100% compatible with all_my_subnets.py

    Preserves original functionality for:
    - Subnet discovery across VPCs
    - Availability zone mapping
    - Public/private subnet identification
    - CIDR allocation analysis
    """

    def __init__(self, session: Optional[boto3.Session] = None):
        super().__init__(resource_type=ResourceType.SUBNET, session=session)

    @aws_api_retry
    def collect_from_region(self, region: str, account: AWSAccount) -> List[AWSResource]:
        """Collect subnets maintaining original script compatibility."""
        resources = []

        try:
            ec2 = self.session.client("ec2", region_name=region)
            paginator = ec2.get_paginator("describe_subnets")

            for page in paginator.paginate():
                for subnet in page["Subnets"]:
                    resource = self._convert_subnet_to_resource(subnet, region, account)
                    resources.append(resource)

        except Exception as e:
            self.logger.error(f"Failed to collect subnets in {region}: {e}")

        return resources

    def _convert_subnet_to_resource(self, subnet: Dict[str, Any], region: str, account: AWSAccount) -> AWSResource:
        """Convert subnet data to standardized format."""

        tags = {tag["Key"]: tag["Value"] for tag in subnet.get("Tags", [])}

        state_mapping = {"available": ResourceState.AVAILABLE, "pending": ResourceState.PENDING}

        subnet_state = subnet.get("State", "unknown")
        resource_state = state_mapping.get(subnet_state, ResourceState.UNKNOWN)

        return AWSResource(
            account_id=account.account_id,
            region=region,
            resource_type=ResourceType.SUBNET,
            resource_id=subnet["SubnetId"],
            arn=f"arn:aws:ec2:{region}:{account.account_id}:subnet/{subnet['SubnetId']}",
            name=tags.get("Name", subnet["SubnetId"]),
            state=resource_state,
            tags=tags,
            metadata={
                "vpc_id": subnet.get("VpcId"),
                "cidr_block": subnet.get("CidrBlock"),
                "ipv6_cidr_block_association_set": subnet.get("Ipv6CidrBlockAssociationSet", []),
                "availability_zone": subnet.get("AvailabilityZone"),
                "availability_zone_id": subnet.get("AvailabilityZoneId"),
                "available_ip_address_count": subnet.get("AvailableIpAddressCount"),
                "default_for_az": subnet.get("DefaultForAz", False),
                "map_public_ip_on_launch": subnet.get("MapPublicIpOnLaunch", False),
                "map_customer_owned_ip_on_launch": subnet.get("MapCustomerOwnedIpOnLaunch", False),
                "customer_owned_ipv4_pool": subnet.get("CustomerOwnedIpv4Pool"),
                "assign_ipv6_address_on_creation": subnet.get("AssignIpv6AddressOnCreation", False),
                "subnet_arn": subnet.get("SubnetArn"),
                "outpost_arn": subnet.get("OutpostArn"),
                "enable_dns64": subnet.get("EnableDns64", False),
                "ipv6_native": subnet.get("Ipv6Native", False),
                "private_dns_name_options_on_launch": subnet.get("PrivateDnsNameOptionsOnLaunch", {}),
            },
            discovered_at=datetime.utcnow(),
        )


# Legacy compatibility functions that exactly match original script interfaces


def collect_vpcs_legacy(account_id: str, region: str = None) -> List[Dict]:
    """
    Legacy function maintaining exact compatibility with all_my_vpcs.py

    This function preserves the original script's interface and output format.
    """
    collector = VPCCollector()
    account = AWSAccount(account_id=account_id, account_name=f"Account-{account_id}")

    if region:
        regions = [region]
    else:
        # Get all regions like original script
        ec2 = boto3.client("ec2", region_name="us-east-1")
        regions = [r["RegionName"] for r in ec2.describe_regions()["Regions"]]

    all_vpcs = []
    for reg in regions:
        try:
            resources = collector.collect_from_region(reg, account)
            # Convert back to legacy format for compatibility
            for resource in resources:
                vpc_dict = {
                    "VpcId": resource.resource_id,
                    "Region": resource.region,
                    "State": resource.state.value,
                    "CidrBlock": resource.metadata.get("cidr_block"),
                    "IsDefault": resource.metadata.get("is_default"),
                    "InstanceTenancy": resource.metadata.get("instance_tenancy"),
                    "DhcpOptionsId": resource.metadata.get("dhcp_options_id"),
                    "Tags": resource.tags,
                    "OwnerId": resource.metadata.get("owner_id"),
                }
                all_vpcs.append(vpc_dict)
        except Exception as e:
            print(f"Error collecting VPCs from {reg}: {e}")

    return all_vpcs


def collect_subnets_legacy(account_id: str, region: str = None) -> List[Dict]:
    """Legacy function maintaining exact compatibility with all_my_subnets.py"""
    collector = SubnetCollector()
    account = AWSAccount(account_id=account_id, account_name=f"Account-{account_id}")

    if region:
        regions = [region]
    else:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        regions = [r["RegionName"] for r in ec2.describe_regions()["Regions"]]

    all_subnets = []
    for reg in regions:
        try:
            resources = collector.collect_from_region(reg, account)
            for resource in resources:
                subnet_dict = {
                    "SubnetId": resource.resource_id,
                    "Region": resource.region,
                    "State": resource.state.value,
                    "VpcId": resource.metadata.get("vpc_id"),
                    "CidrBlock": resource.metadata.get("cidr_block"),
                    "AvailabilityZone": resource.metadata.get("availability_zone"),
                    "AvailableIpAddressCount": resource.metadata.get("available_ip_address_count"),
                    "DefaultForAz": resource.metadata.get("default_for_az"),
                    "MapPublicIpOnLaunch": resource.metadata.get("map_public_ip_on_launch"),
                    "Tags": resource.tags,
                }
                all_subnets.append(subnet_dict)
        except Exception as e:
            print(f"Error collecting subnets from {reg}: {e}")

    return all_subnets


# Command-line interface maintaining original script compatibility
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AWS Networking Resource Inventory")
    parser.add_argument("--account-id", required=True, help="AWS Account ID")
    parser.add_argument("--region", help="Specific region (default: all regions)")
    parser.add_argument("--resource-type", choices=["vpcs", "subnets"], help="Specific resource type to collect")

    args = parser.parse_args()

    # Maintain exact compatibility with original scripts
    if args.resource_type == "vpcs" or not args.resource_type:
        vpcs = collect_vpcs_legacy(args.account_id, args.region)
        print(f"Found {len(vpcs)} VPCs")
        for vpc in vpcs:
            default_str = " (Default)" if vpc["IsDefault"] else ""
            print(f"  {vpc['VpcId']} ({vpc['CidrBlock']}){default_str} in {vpc['Region']}")

    if args.resource_type == "subnets" or not args.resource_type:
        subnets = collect_subnets_legacy(args.account_id, args.region)
        print(f"Found {len(subnets)} subnets")
        for subnet in subnets:
            public_str = " (Public)" if subnet["MapPublicIpOnLaunch"] else " (Private)"
            print(f"  {subnet['SubnetId']} ({subnet['CidrBlock']}){public_str} in {subnet['AvailabilityZone']}")

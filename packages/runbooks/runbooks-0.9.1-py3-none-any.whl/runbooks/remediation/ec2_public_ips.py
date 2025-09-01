"""
EC2 Public IP Analysis - Identify instances with public IP addresses.
"""

import logging
from typing import Any, Dict, List

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client

logger = logging.getLogger(__name__)


def is_vpc_public(vpc_id: str) -> bool:
    """Check if VPC has internet connectivity (IGW or NAT gateway)."""
    try:
        ec2 = get_client("ec2")

        # Check for internet gateway attached to VPC
        igw_response = ec2.describe_internet_gateways(Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}])
        has_igw = len(igw_response.get("InternetGateways", [])) > 0

        # Check for NAT gateways in VPC
        nat_response = ec2.describe_nat_gateways(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
        has_nat = any(gw.get("State") == "available" for gw in nat_response.get("NatGateways", []))

        return has_igw or has_nat

    except ClientError as e:
        logger.error(f"Failed to check VPC connectivity for {vpc_id}: {e}")
        return False


def get_instance_public_ips(instance: Dict[str, Any]) -> List[str]:
    """Get all public IP addresses and DNS names for an EC2 instance."""
    public_ips = set()

    # Instance-level public IP and DNS
    if instance.get("PublicIpAddress"):
        public_ips.add(instance["PublicIpAddress"])
    if instance.get("PublicDnsName") and instance["PublicDnsName"]:
        public_ips.add(instance["PublicDnsName"])

    # Network interface public IPs and DNS
    for interface in instance.get("NetworkInterfaces", []):
        association = interface.get("Association", {})
        if association.get("PublicIp"):
            public_ips.add(association["PublicIp"])
        if association.get("PublicDnsName") and association["PublicDnsName"]:
            public_ips.add(association["PublicDnsName"])

    return list(public_ips)


@click.command()
@click.option("--instance-id", multiple=True, help="Specific instance IDs to check (checks all if not provided)")
@click.option("--show-private", is_flag=True, help="Also show instances without public IPs")
def get_public_ips(instance_id: tuple, show_private: bool):
    """Analyze EC2 instances for public IP addresses and VPC connectivity."""
    logger.info(f"Analyzing EC2 public IPs in {display_aws_account_info()}")

    try:
        ec2 = get_client("ec2")

        # Build query filters
        if instance_id:
            logger.info(f"Checking specific instances: {list(instance_id)}")
            response = ec2.describe_instances(Filters=[{"Name": "instance-id", "Values": list(instance_id)}])
        else:
            logger.info("Checking all EC2 instances")
            response = ec2.describe_instances()

        # Track results
        instances_with_public_ips = []
        instances_without_public_ips = []
        total_instances = 0

        # Process all instances
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                total_instances += 1
                instance_id = instance["InstanceId"]
                instance_state = instance.get("State", {}).get("Name", "unknown")
                vpc_id = instance.get("VpcId", "unknown")

                # Get public IPs for this instance
                public_ips = get_instance_public_ips(instance)
                vpc_is_public = is_vpc_public(vpc_id)

                instance_info = {
                    "instance_id": instance_id,
                    "state": instance_state,
                    "vpc_id": vpc_id,
                    "public_ips": public_ips,
                    "vpc_has_internet": vpc_is_public,
                }

                if public_ips:
                    instances_with_public_ips.append(instance_info)
                    logger.info(f"Instance {instance_id} ({instance_state})")
                    logger.info(f"  Public IPs: {', '.join(public_ips)}")
                    logger.info(f"  VPC {vpc_id} has internet: {vpc_is_public}")
                else:
                    instances_without_public_ips.append(instance_info)
                    if show_private:
                        logger.info(f"Instance {instance_id} ({instance_state})")
                        logger.info(f"  No public IPs")
                        logger.info(f"  VPC {vpc_id} has internet: {vpc_is_public}")

        # Summary
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Total instances: {total_instances}")
        logger.info(f"Instances with public IPs: {len(instances_with_public_ips)}")
        logger.info(f"Instances without public IPs: {len(instances_without_public_ips)}")

        if instances_with_public_ips:
            logger.warning(f"⚠ {len(instances_with_public_ips)} instances have public IP addresses")
            logger.info("Review these instances for security implications")

        if not show_private and instances_without_public_ips:
            logger.info(f"Use --show-private to see {len(instances_without_public_ips)} instances without public IPs")

    except ClientError as e:
        logger.error(f"Failed to describe EC2 instances: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    get_public_ips()

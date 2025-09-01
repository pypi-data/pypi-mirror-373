"""
EC2 Subnet Security - Disable automatic public IP assignment for enhanced security.
"""

import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client

logger = logging.getLogger(__name__)


@click.command()
@click.option("--dry-run", is_flag=True, default=True, help="Preview mode - show actions without making changes")
def disable_auto_public_ips(dry_run: bool = True):
    """Disable automatic public IP assignment on VPC subnets."""
    logger.info(f"Checking subnet auto-assign public IP in {display_aws_account_info()}")

    try:
        ec2 = get_client("ec2")

        # Find subnets with auto-assign public IP enabled
        response = ec2.describe_subnets(Filters=[{"Name": "mapPublicIpOnLaunch", "Values": ["true"]}])

        subnets_with_auto_ip = response.get("Subnets", [])

        if not subnets_with_auto_ip:
            logger.info("✓ No subnets found with automatic public IP assignment enabled")
            return

        logger.info(f"Found {len(subnets_with_auto_ip)} subnets with auto-assign public IP enabled")

        # Track results
        subnets_modified = []

        # Process each subnet
        for subnet in subnets_with_auto_ip:
            subnet_id = subnet["SubnetId"]
            vpc_id = subnet.get("VpcId", "Unknown")
            az = subnet.get("AvailabilityZone", "Unknown")

            logger.info(f"Subnet: {subnet_id} (VPC: {vpc_id}, AZ: {az})")
            logger.info(f"  ✗ Auto-assign public IP is enabled")

            # Disable auto-assign if not in dry-run mode
            if not dry_run:
                try:
                    logger.info(f"  → Disabling auto-assign public IP...")
                    ec2.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={"Value": False})
                    subnets_modified.append(subnet_id)
                    logger.info(f"  ✓ Successfully disabled auto-assign public IP")

                except ClientError as e:
                    logger.error(f"  ✗ Failed to modify subnet {subnet_id}: {e}")

        # Summary
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Subnets with auto-assign public IP: {len(subnets_with_auto_ip)}")

        if dry_run and subnets_with_auto_ip:
            logger.info(f"To disable auto-assign on {len(subnets_with_auto_ip)} subnets, run with --no-dry-run")
        elif not dry_run:
            logger.info(f"Successfully modified {len(subnets_modified)} subnets")

    except ClientError as e:
        logger.error(f"Failed to process subnet auto-assign settings: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

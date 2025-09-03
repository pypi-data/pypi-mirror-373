"""
EC2 Security Group Cleanup - Identify and remove unused security groups safely.
"""

import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client

logger = logging.getLogger(__name__)


@click.command()
@click.option("--dry-run", is_flag=True, default=True, help="Preview mode - show actions without making changes")
@click.option("--include-elb", is_flag=True, help="Also check ELB/ALB/NLB usage (comprehensive scan)")
@click.option("--include-eni", is_flag=True, help="Also check network interface usage")
def find_unused_security_groups(dry_run, include_elb, include_eni):
    """Find and remove unused security groups with comprehensive usage checks."""
    logger.info(f"Finding unused security groups in {display_aws_account_info()}")

    try:
        ec2 = get_client("ec2")

        # Collect all security groups
        logger.info("🔍 Scanning all security groups...")
        response = ec2.describe_security_groups()
        all_security_groups = {}
        default_security_groups = set()

        for sg in response["SecurityGroups"]:
            sg_id = sg["GroupId"]
            sg_name = sg.get("GroupName", "")
            all_security_groups[sg_id] = {
                "name": sg_name,
                "description": sg.get("Description", ""),
                "vpc_id": sg.get("VpcId", ""),
            }

            # Track default security groups (cannot be deleted)
            if sg_name == "default":
                default_security_groups.add(sg_id)

        logger.info(f"Found {len(all_security_groups)} security groups")

        # Find security groups in use
        used_security_groups = set()

        # Check EC2 instances
        logger.info("📋 Checking EC2 instance usage...")
        instances_response = ec2.describe_instances()
        instance_count = 0

        for reservation in instances_response["Reservations"]:
            for instance in reservation["Instances"]:
                instance_count += 1
                for sg in instance.get("SecurityGroups", []):
                    used_security_groups.add(sg["GroupId"])

        logger.info(f"Checked {instance_count} EC2 instances")

        # Check Load Balancers if requested
        if include_elb:
            logger.info("🔍 Checking Load Balancer usage...")
            try:
                # Check Classic Load Balancers
                elb = get_client("elb")
                elb_response = elb.describe_load_balancers()
                for lb in elb_response.get("LoadBalancerDescriptions", []):
                    for sg_id in lb.get("SecurityGroups", []):
                        used_security_groups.add(sg_id)

                # Check Application/Network Load Balancers
                elbv2 = get_client("elbv2")
                elbv2_response = elbv2.describe_load_balancers()
                for lb in elbv2_response.get("LoadBalancers", []):
                    for sg_id in lb.get("SecurityGroups", []):
                        used_security_groups.add(sg_id)

                logger.info("✓ Load balancer usage checked")

            except ClientError as e:
                logger.warning(f"Could not check load balancers: {e}")

        # Check Network Interfaces if requested
        if include_eni:
            logger.info("🔍 Checking network interface usage...")
            try:
                eni_response = ec2.describe_network_interfaces()
                for eni in eni_response.get("NetworkInterfaces", []):
                    for group in eni.get("Groups", []):
                        used_security_groups.add(group["GroupId"])

                logger.info("✓ Network interface usage checked")

            except ClientError as e:
                logger.warning(f"Could not check network interfaces: {e}")

        # Check for security group references (ingress/egress rules)
        logger.info("🔍 Checking security group rule references...")
        referenced_security_groups = set()

        for sg_id, sg_info in all_security_groups.items():
            try:
                sg_details = ec2.describe_security_groups(GroupIds=[sg_id])["SecurityGroups"][0]

                # Check ingress rules for SG references
                for rule in sg_details.get("IpPermissions", []):
                    for sg_ref in rule.get("UserIdGroupPairs", []):
                        referenced_security_groups.add(sg_ref["GroupId"])

                # Check egress rules for SG references
                for rule in sg_details.get("IpPermissionsEgress", []):
                    for sg_ref in rule.get("UserIdGroupPairs", []):
                        referenced_security_groups.add(sg_ref["GroupId"])

            except ClientError as e:
                logger.debug(f"Could not check rules for {sg_id}: {e}")

        # Combine all usage types
        all_used_groups = used_security_groups | referenced_security_groups | default_security_groups

        # Find unused security groups
        unused_security_groups = set(all_security_groups.keys()) - all_used_groups

        logger.info("\n=== ANALYSIS RESULTS ===")
        logger.info(f"Total security groups: {len(all_security_groups)}")
        logger.info(f"Used by resources: {len(used_security_groups)}")
        logger.info(f"Referenced in rules: {len(referenced_security_groups)}")
        logger.info(f"Default groups (protected): {len(default_security_groups)}")
        logger.info(f"Unused security groups: {len(unused_security_groups)}")

        if not unused_security_groups:
            logger.info("✅ No unused security groups found")
            return

        logger.warning(f"⚠ Found {len(unused_security_groups)} unused security groups")

        # Show unused security groups details
        logger.info("\n📋 Unused Security Groups:")
        deletion_candidates = []

        for sg_id in unused_security_groups:
            sg_info = all_security_groups[sg_id]
            logger.info(f"  {sg_id}: {sg_info['name']}")
            logger.info(f"    Description: {sg_info['description']}")
            logger.info(f"    VPC: {sg_info['vpc_id']}")

            # Skip default security groups
            if sg_info["name"] == "default":
                logger.info(f"    Status: Protected (default security group)")
            else:
                deletion_candidates.append(sg_id)
                logger.info(f"    Status: Can be deleted")

        logger.info(f"\n📊 Summary: {len(deletion_candidates)} security groups can be safely deleted")

        # Delete unused security groups
        if deletion_candidates:
            if dry_run:
                logger.info("DRY-RUN: Would delete the following security groups:")
                for sg_id in deletion_candidates:
                    sg_info = all_security_groups[sg_id]
                    logger.info(f"  - {sg_id} ({sg_info['name']})")
                logger.info("To perform actual deletion, run with --no-dry-run")
            else:
                logger.info("🗑 Deleting unused security groups...")
                deleted_count = 0
                failed_count = 0

                for sg_id in deletion_candidates:
                    sg_info = all_security_groups[sg_id]
                    logger.info(f"  → Deleting {sg_id} ({sg_info['name']})...")

                    try:
                        ec2.delete_security_group(GroupId=sg_id)
                        deleted_count += 1
                        logger.info(f"  ✓ Successfully deleted {sg_id}")

                    except ClientError as e:
                        error_code = e.response.get("Error", {}).get("Code", "Unknown")
                        if error_code == "DependencyViolation":
                            logger.warning(f"  ⚠ Cannot delete {sg_id}: has dependencies")
                        elif error_code == "InvalidGroup.InUse":
                            logger.warning(f"  ⚠ Cannot delete {sg_id}: currently in use")
                        else:
                            logger.error(f"  ✗ Failed to delete {sg_id}: {e}")
                        failed_count += 1

                logger.info(f"\n✅ Deletion complete: {deleted_count} deleted, {failed_count} failed")

    except ClientError as e:
        logger.error(f"Failed to scan security groups: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    find_unused_security_groups()

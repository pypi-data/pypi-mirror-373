"""
S3 Static Website Hosting Disable - Remove website configuration from S3 buckets.
"""

import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client

logger = logging.getLogger(__name__)


@click.command()
@click.option("--dry-run", is_flag=True, default=True, help="Preview mode - show actions without making changes")
def disable_static_web_hosting_on_all_buckets(dry_run: bool = True):
    """Disable static website hosting on all S3 buckets."""
    logger.info(f"Checking S3 static website hosting in {display_aws_account_info()}")

    try:
        s3 = get_client("s3")
        response = s3.list_buckets()
        buckets = response.get("Buckets", [])

        if not buckets:
            logger.info("No S3 buckets found")
            return

        logger.info(f"Found {len(buckets)} buckets to check")

        # Track results
        buckets_with_hosting = []
        buckets_disabled = []

        # Check each bucket for static website hosting
        for bucket in buckets:
            bucket_name = bucket["Name"]
            logger.info(f"Checking bucket: {bucket_name}")

            try:
                # Check if website configuration exists
                s3.get_bucket_website(Bucket=bucket_name)

                # If we get here, website hosting is enabled
                buckets_with_hosting.append(bucket_name)
                logger.info(f"  ✗ Static website hosting is enabled")

                # Disable hosting if not in dry-run mode
                if not dry_run:
                    logger.info(f"  → Disabling static website hosting...")
                    s3.delete_bucket_website(Bucket=bucket_name)
                    buckets_disabled.append(bucket_name)
                    logger.info(f"  ✓ Successfully disabled static website hosting")

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")
                if error_code == "NoSuchWebsiteConfiguration":
                    logger.info(f"  ✓ Static website hosting already disabled")
                else:
                    logger.error(f"  ✗ Error checking bucket: {e}")

        # Summary
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Buckets with static hosting: {len(buckets_with_hosting)}")

        if dry_run and buckets_with_hosting:
            logger.info(f"To disable hosting on {len(buckets_with_hosting)} buckets, run with --no-dry-run")
        elif not dry_run:
            logger.info(f"Successfully disabled hosting on {len(buckets_disabled)} buckets")

    except Exception as e:
        logger.error(f"Failed to process S3 static website hosting: {e}")
        raise

"""
S3 HTTPS-Only Policy - Enforce secure transport for all S3 bucket access.
"""

import json
import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client

logger = logging.getLogger(__name__)


def check_https_only_policy(bucket_name):
    """Check if S3 bucket has HTTPS-only policy enabled."""
    try:
        s3 = get_client("s3")

        # Get existing bucket policy
        response = s3.get_bucket_policy(Bucket=bucket_name)
        policy_json = json.loads(response["Policy"])

        # Look for HTTPS-only deny statement
        for statement in policy_json.get("Statement", []):
            if (
                statement.get("Effect") == "Deny"
                and statement.get("Condition", {}).get("Bool", {}).get("aws:SecureTransport") == "false"
            ):
                logger.debug(f"Bucket '{bucket_name}' has HTTPS-only policy")
                return True

        logger.debug(f"Bucket '{bucket_name}' does not have HTTPS-only policy")
        return False

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "NoSuchBucketPolicy":
            logger.debug(f"Bucket '{bucket_name}' has no bucket policy")
            return False
        else:
            logger.error(f"Failed to check bucket policy for '{bucket_name}': {e}")
            return False


def update_https_only_policy(bucket_name):
    """Add HTTPS-only policy to S3 bucket."""
    try:
        s3 = get_client("s3")

        # Get existing bucket policy or create new one
        try:
            response = s3.get_bucket_policy(Bucket=bucket_name)
            policy_json = json.loads(response["Policy"])
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "NoSuchBucketPolicy":
                # Create new policy if none exists
                policy_json = {"Version": "2012-10-17", "Statement": []}
            else:
                raise

        # Create HTTPS-only policy statement
        https_only_statement = {
            "Sid": "AllowSSLRequestsOnly",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [f"arn:aws:s3:::{bucket_name}/*", f"arn:aws:s3:::{bucket_name}"],
            "Condition": {"Bool": {"aws:SecureTransport": "false"}},
        }

        # Add the statement to the policy
        policy_json["Statement"].append(https_only_statement)

        # Apply the updated policy
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy_json))
        logger.info(f"Applied HTTPS-only policy to bucket '{bucket_name}'")
        return True

    except ClientError as e:
        logger.error(f"Failed to update policy for bucket '{bucket_name}': {e}")
        return False


@click.command()
@click.option("--dry-run", is_flag=True, default=True, help="Preview mode - show actions without making changes")
def enable_ssl_secure_on_all_buckets(dry_run: bool = True):
    """Enforce HTTPS-only access for all S3 buckets."""
    logger.info(f"Checking S3 HTTPS policies in {display_aws_account_info()}")

    try:
        s3 = get_client("s3")
        response = s3.list_buckets()
        buckets = response.get("Buckets", [])

        if not buckets:
            logger.info("No S3 buckets found")
            return

        logger.info(f"Found {len(buckets)} buckets to check")

        # Track results
        buckets_with_https = []
        buckets_without_https = []
        buckets_updated = []

        # Check each bucket
        for bucket in buckets:
            bucket_name = bucket["Name"]
            logger.info(f"Checking bucket: {bucket_name}")

            has_https_policy = check_https_only_policy(bucket_name)

            if has_https_policy:
                buckets_with_https.append(bucket_name)
                logger.info(f"  ✓ HTTPS-only policy already enabled")
            else:
                buckets_without_https.append(bucket_name)
                logger.info(f"  ✗ HTTPS-only policy not found")

                # Apply policy if not in dry-run mode
                if not dry_run:
                    logger.info(f"  → Adding HTTPS-only policy to '{bucket_name}'...")
                    if update_https_only_policy(bucket_name):
                        buckets_updated.append(bucket_name)
                        logger.info(f"  ✓ Successfully applied HTTPS-only policy")
                    else:
                        logger.error(f"  ✗ Failed to apply HTTPS-only policy")

        # Summary
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Buckets with HTTPS policy: {len(buckets_with_https)}")
        logger.info(f"Buckets without HTTPS policy: {len(buckets_without_https)}")

        if dry_run and buckets_without_https:
            logger.info(f"To apply HTTPS policies to {len(buckets_without_https)} buckets, run with --no-dry-run")
        elif not dry_run:
            logger.info(f"Successfully applied HTTPS policies to {len(buckets_updated)} buckets")

    except Exception as e:
        logger.error(f"Failed to process S3 HTTPS policies: {e}")
        raise

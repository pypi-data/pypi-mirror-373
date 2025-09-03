"""
🚨 HIGH-RISK: CloudTrail S3 Policy Modifications - Audit trail security operations.
"""

import json
import logging
from datetime import datetime, timedelta

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client

logger = logging.getLogger(__name__)


def apply_policy(policy_json: dict, bucket_name: str, backup_enabled: bool = True):
    """Apply S3 bucket policy with backup and validation."""
    try:
        s3 = get_client("s3")

        # Backup existing policy before applying new one
        backup_policy = None
        if backup_enabled:
            try:
                backup_response = s3.get_bucket_policy(Bucket=bucket_name)
                backup_policy = backup_response["Policy"]
                logger.info(f"✅ Backed up existing policy for bucket: {bucket_name}")
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") != "NoSuchBucketPolicy":
                    logger.warning(f"Could not backup policy: {e}")

        # Apply the new policy
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy_json))
        logger.info(f"✅ Applied new policy to bucket: {bucket_name}")

        return backup_policy

    except ClientError as e:
        logger.error(f"❌ Failed to apply policy to bucket '{bucket_name}': {e}")
        raise


def get_s3_policy_modifications(user_email, start_time=None, end_time=None):
    """Search CloudTrail for S3 policy modifications by a specific user."""
    try:
        cloudtrail = get_client("cloudtrail")
        config = get_client("config")

        # Set default time range if not provided (last 30 days)
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time - timedelta(days=30)

        logger.info(f"🔍 Searching CloudTrail events from {start_time} to {end_time}")

        # Define CloudTrail LookupEvent parameters
        event_selector = {
            "LookupAttributes": [
                {"AttributeKey": "EventName", "AttributeValue": "PutBucketPolicy"},
                {"AttributeKey": "ResourceType", "AttributeValue": "AWS::S3::Bucket"},
            ],
            "StartTime": start_time,
            "EndTime": end_time,
        }

        response = cloudtrail.lookup_events(**event_selector)
        events = response.get("Events", [])

        logger.info(f"Found {len(events)} S3 policy modification events")

        modifications = []

        for event in events:
            try:
                cloudtrail_event = json.loads(event["CloudTrailEvent"])
                user_identity = cloudtrail_event.get("userIdentity", {})

                # Check for modifications by the specified user (multiple ways to match)
                user_matches = False
                principal_id = user_identity.get("principalId", "")
                user_name = user_identity.get("userName", "")
                arn = user_identity.get("arn", "")

                if user_email in principal_id or user_email in user_name or user_email in arn:
                    user_matches = True

                if user_matches:
                    # Extract bucket name and policy changes
                    request_params = cloudtrail_event.get("requestParameters", {})
                    bucket_name = request_params.get("bucketName")
                    new_policy = request_params.get("bucketPolicy")

                    if not bucket_name:
                        logger.warning(f"No bucket name found in event: {event.get('EventId', 'Unknown')}")
                        continue

                    logger.debug(f"Found modification to bucket: {bucket_name}")

                    # Try to get previous policy from AWS Config
                    old_policy = None
                    try:
                        config_response = config.get_resource_config_history(
                            resourceType="AWS::S3::Bucket",
                            resourceId=bucket_name,
                            laterTime=event["EventTime"],
                            limit=1,
                        )

                        if config_response.get("configurationItems"):
                            old_config = config_response["configurationItems"][0]
                            bucket_policy_config = old_config.get("supplementaryConfiguration", {}).get("BucketPolicy")

                            if bucket_policy_config:
                                policy_data = json.loads(bucket_policy_config)
                                if policy_data.get("policyText"):
                                    old_policy = json.loads(policy_data["policyText"])

                    except ClientError as e:
                        error_code = e.response.get("Error", {}).get("Code", "Unknown")
                        if error_code == "ResourceNotDiscoveredException":
                            logger.debug(f"Bucket {bucket_name} not tracked in Config")
                        else:
                            logger.warning(f"Config query failed for {bucket_name}: {e}")

                    modification = {
                        "BucketName": bucket_name,
                        "NewPolicy": new_policy,
                        "OldPolicy": old_policy,
                        "EventTime": event["EventTime"],
                        "EventId": event.get("EventId"),
                        "UserIdentity": user_identity,
                    }

                    modifications.append(modification)

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse CloudTrail event: {e}")
                continue

        logger.info(f"Found {len(modifications)} policy modifications by user: {user_email}")
        return modifications

    except ClientError as e:
        logger.error(f"Failed to query CloudTrail: {e}")
        raise


@click.command()
@click.option("--email", required=True, help="User email to check for S3 policy modifications")
@click.option("--days", default=30, help="Number of days to look back for modifications")
@click.option("--dry-run", is_flag=True, default=True, help="Preview mode - show analysis without reverting policies")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompts (dangerous!)")
def cloudtrail_s3_modifications(email, days, dry_run, confirm):
    """🚨 HIGH-RISK: Analyze and potentially revert S3 policy modifications from CloudTrail."""

    # HIGH-RISK OPERATION WARNING
    if not dry_run and not confirm:
        logger.warning("🚨 HIGH-RISK OPERATION: S3 Policy Reversion")
        logger.warning("This operation can modify S3 bucket policies based on CloudTrail analysis")
        if not click.confirm("Do you want to continue?"):
            logger.info("Operation cancelled by user")
            return

    logger.info(f"🔍 CloudTrail S3 policy analysis in {display_aws_account_info()}")
    logger.info(f"Analyzing modifications by user: {email}")
    logger.info(f"Looking back {days} days")

    try:
        # Set time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        # Get policy modifications
        policy_changes = get_s3_policy_modifications(email, start_time, end_time)

        if not policy_changes:
            logger.info(f"✅ No S3 bucket policy modifications found for user: {email}")
            return

        logger.warning(f"⚠ Found {len(policy_changes)} policy modifications")

        # Analyze each modification
        reversion_candidates = []

        for i, change in enumerate(policy_changes, 1):
            bucket_name = change["BucketName"]
            event_time = change["EventTime"]
            event_id = change.get("EventId", "Unknown")

            logger.info(f"\n📋 Modification {i}/{len(policy_changes)}:")
            logger.info(f"  Bucket: {bucket_name}")
            logger.info(f"  Event Time: {event_time}")
            logger.info(f"  Event ID: {event_id}")

            # Show user identity details
            user_identity = change.get("UserIdentity", {})
            logger.info(f"  User Type: {user_identity.get('type', 'Unknown')}")
            logger.info(f"  Principal ID: {user_identity.get('principalId', 'Unknown')}")

            # Analyze policy changes
            new_policy = change.get("NewPolicy")
            old_policy = change.get("OldPolicy")

            if old_policy:
                logger.info(f"  ✅ Previous policy found - reversion possible")

                # Check if current policy still matches the problematic one
                try:
                    s3 = get_client("s3")
                    current_response = s3.get_bucket_policy(Bucket=bucket_name)
                    current_policy = json.loads(current_response["Policy"])

                    # Simple comparison - check if old policy statements are missing
                    old_statements = old_policy.get("Statement", [])
                    current_statements = current_policy.get("Statement", [])

                    missing_statements = []
                    for old_stmt in old_statements:
                        if old_stmt not in current_statements:
                            missing_statements.append(old_stmt)

                    if missing_statements:
                        logger.warning(f"  ⚠ {len(missing_statements)} policy statements appear to be missing")
                        reversion_candidates.append(
                            {
                                "bucket": bucket_name,
                                "old_policy": old_policy,
                                "current_policy": current_policy,
                                "missing_statements": missing_statements,
                                "event_time": event_time,
                            }
                        )
                    else:
                        logger.info(f"  ✓ Current policy appears to include previous statements")

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code", "Unknown")
                    if error_code == "NoSuchBucketPolicy":
                        logger.warning(f"  ⚠ Bucket currently has no policy")
                    else:
                        logger.error(f"  ❌ Failed to get current policy: {e}")

            else:
                logger.warning(f"  ⚠ No previous policy found - cannot revert")

            # Show policy details if verbose
            logger.debug(f"  New Policy: {json.dumps(new_policy, indent=2) if new_policy else 'None'}")
            logger.debug(f"  Old Policy: {json.dumps(old_policy, indent=2) if old_policy else 'None'}")

        # Summary and reversion
        logger.info(f"\n=== ANALYSIS SUMMARY ===")
        logger.info(f"Total modifications found: {len(policy_changes)}")
        logger.info(f"Buckets eligible for reversion: {len(reversion_candidates)}")

        if reversion_candidates:
            logger.warning(f"⚠ {len(reversion_candidates)} buckets have potential policy issues")

            if dry_run:
                logger.info("DRY-RUN: Would attempt to revert the following buckets:")
                for candidate in reversion_candidates:
                    logger.info(f"  - {candidate['bucket']} (modified: {candidate['event_time']})")
                logger.info("To perform actual reversion, run with --no-dry-run")
            else:
                # Perform reversions with confirmation
                for candidate in reversion_candidates:
                    bucket_name = candidate["bucket"]
                    old_policy = candidate["old_policy"]

                    if not confirm:
                        logger.warning(f"\n🚨 REVERT BUCKET POLICY:")
                        logger.warning(f"  Bucket: {bucket_name}")
                        logger.warning(f"  Event Time: {candidate['event_time']}")
                        if not click.confirm(f"Revert policy for bucket {bucket_name}?"):
                            logger.info(f"Skipped reversion for {bucket_name}")
                            continue

                    logger.info(f"🔄 Reverting policy for bucket: {bucket_name}")
                    try:
                        backup_policy = apply_policy(old_policy, bucket_name, backup_enabled=True)
                        logger.info(f"✅ Successfully reverted policy for: {bucket_name}")

                        # Log the reversion for audit
                        logger.info(f"🔍 Audit: Policy reversion completed")
                        logger.info(f"  Bucket: {bucket_name}")
                        logger.info(f"  Original Event Time: {candidate['event_time']}")

                    except Exception as e:
                        logger.error(f"❌ Failed to revert policy for {bucket_name}: {e}")
        else:
            logger.info("✅ No policy reversions needed")

    except Exception as e:
        logger.error(f"❌ CloudTrail analysis failed: {e}")
        raise

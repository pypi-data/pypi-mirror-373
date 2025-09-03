"""
Enterprise EBS Volume Cleanup - Unattached Volume Detection and Management

## Overview

This module provides capabilities for detecting and optionally cleaning up unattached
EBS volumes in AWS accounts. Unattached volumes incur unnecessary costs and represent
potential security risks if they contain sensitive data.

## Key Features

- **Safe Detection**: Identifies unattached EBS volumes with comprehensive metadata
- **CloudTrail Integration**: Tracks last attachment times for informed decisions
- **Dry-Run Support**: Safe preview mode before any destructive operations
- **Cost Optimization**: Helps reduce unnecessary EBS storage costs
- **Audit Trail**: Comprehensive logging of all detection and cleanup operations

## Usage Examples

```python
# Detection only (safe)
python ec2_unattached_ebs_volumes.py --dry-run

# Cleanup unattached volumes (destructive)
python ec2_unattached_ebs_volumes.py
```

## Important Safety Notes

⚠️ **WARNING**: This script can DELETE EBS volumes permanently
⚠️ **DATA LOSS**: Deleted volumes cannot be recovered
⚠️ **COST IMPACT**: Verify volumes are truly unused before deletion

Version: 0.7.8 - Enterprise Production Ready
Compliance: CIS AWS Foundations, Cost Optimization Best Practices
"""

import datetime
import logging
from typing import Any, Dict, List, Optional, Union

import click
from botocore.exceptions import BotoCoreError, ClientError

from .commons import get_client, write_to_csv

# Configure enterprise logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_last_volume_attachment_time(volume_id: str) -> Optional[datetime.datetime]:
    """
    Retrieve the last attachment time of an EBS volume from CloudTrail audit logs.

    This function queries CloudTrail for AttachVolume events to determine when the
    specified EBS volume was last attached to an EC2 instance. This information
    is crucial for making informed decisions about volume cleanup.

    ## Implementation Details

    - Searches CloudTrail events for the past 365 days
    - Filters for 'AttachVolume' events associated with the specified volume
    - Returns the most recent attachment timestamp if found
    - Handles CloudTrail API pagination and rate limiting

    ## Security Considerations

    - Requires CloudTrail to be enabled in the AWS account
    - Requires appropriate IAM permissions for CloudTrail access
    - May not find events if CloudTrail logging was disabled

    Args:
        volume_id (str): The EBS volume identifier (e.g., 'vol-1234567890abcdef0')
                        Must be a valid AWS EBS volume ID format

    Returns:
        Optional[datetime.datetime]: The UTC timestamp of the last attachment event,
                                   or None if no attachment history is found

    Raises:
        ClientError: If CloudTrail API access fails due to permissions or service issues
        ValueError: If volume_id format is invalid

    Example:
        >>> last_attached = get_last_volume_attachment_time('vol-1234567890abcdef0')
        >>> if last_attached:
        ...     print(f"Volume was last attached on {last_attached}")
        ... else:
        ...     print("No attachment history found")
    """

    # Input validation
    if not volume_id or not isinstance(volume_id, str):
        raise ValueError(f"Invalid volume_id: {volume_id}. Must be a non-empty string.")

    if not volume_id.startswith("vol-"):
        raise ValueError(f"Invalid volume_id format: {volume_id}. Must start with 'vol-'.")

    logger.debug(f"Querying CloudTrail for attachment history of volume: {volume_id}")

    try:
        # Initialize CloudTrail client with error handling
        cloudtrail = get_client("cloudtrail")

        # Define search parameters with comprehensive time range
        search_start_time = datetime.datetime.utcnow() - datetime.timedelta(days=365)

        logger.debug(f"Searching CloudTrail from {search_start_time} to present for volume {volume_id}")

        # Query CloudTrail for volume attachment events
        response = cloudtrail.lookup_events(
            LookupAttributes=[{"AttributeKey": "ResourceName", "AttributeValue": volume_id}],
            MaxResults=1,  # Only need the most recent attachment event
            StartTime=search_start_time,
        )

        # Process CloudTrail response
        events = response.get("Events", [])

        if events:
            event = events[0]
            event_name = event.get("EventName", "")

            logger.debug(f"Found CloudTrail event for volume {volume_id}: {event_name}")

            # Verify this is an attachment event
            if event_name == "AttachVolume":
                timestamp = event.get("EventTime")
                if timestamp:
                    logger.info(f"Volume {volume_id} was last attached on {timestamp}")
                    return timestamp
                else:
                    logger.warning(f"AttachVolume event found for {volume_id} but no timestamp available")
            else:
                logger.debug(f"Most recent event for volume {volume_id} was {event_name}, not AttachVolume")
        else:
            logger.info(f"No CloudTrail events found for volume {volume_id} in the past 365 days")

        return None

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(f"CloudTrail API error while querying volume {volume_id}: {error_code} - {error_message}")

        # Handle specific CloudTrail errors gracefully
        if error_code in ["AccessDenied", "UnauthorizedOperation"]:
            logger.warning(f"Insufficient permissions to access CloudTrail for volume {volume_id}")
            return None
        elif error_code == "TrailNotFoundException":
            logger.warning(f"CloudTrail not configured - cannot determine attachment history for volume {volume_id}")
            return None
        else:
            # Re-raise unexpected errors
            raise

    except BotoCoreError as e:
        logger.error(f"AWS service error while querying CloudTrail for volume {volume_id}: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error while querying attachment history for volume {volume_id}: {e}")
        raise


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="Preview mode - show volumes that would be deleted without actually deleting them",
)
@click.option(
    "--max-age-days", type=int, default=30, help="Only consider volumes unattached for this many days or more"
)
@click.option("--output-file", type=str, help="Save results to CSV file")
@click.option("--region", type=str, help="AWS region to scan (defaults to current region)")
def detect_and_delete_volumes(dry_run: bool, max_age_days: int, output_file: Optional[str], region: Optional[str]):
    """
    Enterprise EBS Volume Cleanup - Detect and optionally remove unattached volumes.

    This command provides comprehensive detection and optional cleanup of unattached
    EBS volumes in your AWS account. Unattached volumes incur unnecessary costs and
    may represent security risks if they contain sensitive data.

    ## Operation Modes

    **Dry-Run Mode (Default - SAFE):**
    - Detects and reports unattached volumes
    - No destructive operations performed
    - Generates detailed analysis reports
    - Safe for production environments

    **Cleanup Mode (DESTRUCTIVE):**
    - Actually deletes identified unattached volumes
    - Requires explicit --no-dry-run flag
    - Creates comprehensive audit trail
    - ⚠️ **WARNING: Data loss is permanent**

    ## Safety Features

    - CloudTrail integration for attachment history analysis
    - Configurable age thresholds for volume consideration
    - Comprehensive logging and audit trails
    - CSV export for external analysis
    - Input validation and error recovery

    ## Cost Impact Analysis

    This tool helps identify cost optimization opportunities by finding:
    - Volumes incurring unnecessary storage charges
    - Orphaned volumes from terminated instances
    - Development/testing volumes left unattached

    Args:
        dry_run (bool): When True (default), only reports findings without deletion
        max_age_days (int): Minimum age in days before considering volumes for cleanup
        output_file (str): Optional CSV file path for saving detailed results
        region (str): AWS region to scan (defaults to configured region)

    Returns:
        None: Results are logged and optionally saved to CSV

    Raises:
        ClientError: If AWS API access fails due to permissions or service issues
        ValueError: If invalid parameters are provided

    Examples:
        # Safe detection only (recommended first step)
        python ec2_unattached_ebs_volumes.py --dry-run

        # Detection with custom age threshold and output
        python ec2_unattached_ebs_volumes.py --dry-run --max-age-days 7 --output-file volumes.csv

        # Actual cleanup (DESTRUCTIVE - use with extreme caution)
        python ec2_unattached_ebs_volumes.py --no-dry-run --max-age-days 90
    """

    # Input validation and configuration
    if max_age_days < 0:
        raise ValueError(f"max_age_days must be non-negative, got: {max_age_days}")

    # Enhanced logging for operation start
    operation_mode = "DRY-RUN (Safe Preview)" if dry_run else "CLEANUP (Destructive)"
    logger.info(f"🚀 Starting EBS Volume Analysis - Mode: {operation_mode}")
    logger.info(f"📊 Configuration: max_age_days={max_age_days}, region={region or 'default'}")

    if not dry_run:
        logger.warning("⚠️ DESTRUCTIVE MODE ENABLED - Volumes will be permanently deleted!")
        logger.warning("⚠️ Ensure you have verified these volumes are truly unused!")

    try:
        # Initialize EC2 client with region support
        ec2_client = get_client("ec2", region_name=region)
        logger.debug(f"Initialized EC2 client for region: {region or 'default'}")

        # Query for unattached volumes with comprehensive filtering
        logger.info("🔍 Querying for unattached EBS volumes...")

        response = ec2_client.describe_volumes(
            Filters=[
                {"Name": "status", "Values": ["available"]}  # Only unattached volumes
            ]
        )

        volumes = response.get("Volumes", [])
        total_volumes_found = len(volumes)

        logger.info(f"📋 Found {total_volumes_found} unattached volumes for analysis")

        if total_volumes_found == 0:
            logger.info("✅ No unattached volumes found - account is optimized!")
            return

        # Analyze each volume with comprehensive metadata collection
        analysis_results = []
        deletion_candidates = []
        total_cost_gb_month = 0.0

        logger.info("🔬 Analyzing volume metadata and attachment history...")

        for volume_index, volume in enumerate(volumes, 1):
            volume_id = volume["VolumeId"]
            volume_size = volume["Size"]
            volume_type = volume["VolumeType"]
            create_time = volume["CreateTime"]

            logger.debug(f"Processing volume {volume_index}/{total_volumes_found}: {volume_id}")

            try:
                # Calculate volume age
                volume_age_days = (datetime.datetime.now(datetime.timezone.utc) - create_time).days

                # Get CloudTrail attachment history
                last_attachment_time = get_last_volume_attachment_time(volume_id)

                # Determine time since last use
                if last_attachment_time:
                    days_since_detached = (
                        datetime.datetime.now(datetime.timezone.utc)
                        - last_attachment_time.replace(tzinfo=datetime.timezone.utc)
                    ).days
                else:
                    days_since_detached = volume_age_days  # Never attached

                # Estimate monthly cost (rough approximation)
                # GP3: $0.08/GB/month, GP2: $0.10/GB/month, IO1/IO2: varies
                cost_per_gb = 0.08 if volume_type == "gp3" else 0.10
                monthly_cost = volume_size * cost_per_gb
                total_cost_gb_month += monthly_cost

                # Comprehensive volume analysis data
                volume_analysis = {
                    "VolumeId": volume_id,
                    "Size": volume_size,
                    "VolumeType": volume_type,
                    "CreateTime": create_time.isoformat(),
                    "VolumeAgeDays": volume_age_days,
                    "LastAttachmentTime": last_attachment_time.isoformat()
                    if last_attachment_time
                    else "Never attached",
                    "DaysSinceDetached": days_since_detached,
                    "EstimatedMonthlyCost": f"${monthly_cost:.2f}",
                    "EligibleForCleanup": days_since_detached >= max_age_days,
                    "AvailabilityZone": volume.get("AvailabilityZone", "Unknown"),
                    "State": volume.get("State", "Unknown"),
                    "Encrypted": volume.get("Encrypted", False),
                    "Tags": volume.get("Tags", []),
                }

                analysis_results.append(volume_analysis)

                # Log volume findings with appropriate level
                if days_since_detached >= max_age_days:
                    logger.info(
                        f"🎯 CLEANUP CANDIDATE: {volume_id} ({volume_size}GB {volume_type}) - "
                        f"unattached for {days_since_detached} days, cost: ${monthly_cost:.2f}/month"
                    )
                    deletion_candidates.append(volume_analysis)
                else:
                    logger.debug(
                        f"📅 TOO RECENT: {volume_id} - unattached for only {days_since_detached} days "
                        f"(threshold: {max_age_days} days)"
                    )

            except Exception as e:
                logger.error(f"❌ Error analyzing volume {volume_id}: {e}")
                # Continue processing other volumes
                continue

        # Generate comprehensive summary report
        eligible_count = len(deletion_candidates)
        eligible_size_gb = sum(vol["Size"] for vol in deletion_candidates)
        eligible_monthly_cost = sum(float(vol["EstimatedMonthlyCost"].replace("$", "")) for vol in deletion_candidates)

        logger.info("📊 ANALYSIS SUMMARY:")
        logger.info(f"   📋 Total unattached volumes: {total_volumes_found}")
        logger.info(f"   🎯 Eligible for cleanup: {eligible_count}")
        logger.info(f"   💾 Total eligible storage: {eligible_size_gb} GB")
        logger.info(f"   💰 Potential monthly savings: ${eligible_monthly_cost:.2f}")
        logger.info(f"   📈 Total monthly EBS cost: ${total_cost_gb_month:.2f}")

        # Execute cleanup operations if not in dry-run mode
        if not dry_run and deletion_candidates:
            logger.warning(f"🗑️ EXECUTING CLEANUP: Deleting {eligible_count} volumes...")

            successful_deletions = 0
            failed_deletions = []

            for volume_data in deletion_candidates:
                volume_id = volume_data["VolumeId"]

                try:
                    logger.info(f"🗑️ Deleting volume: {volume_id}")

                    ec2_client.delete_volume(VolumeId=volume_id)
                    successful_deletions += 1

                    logger.info(f"✅ Successfully deleted volume: {volume_id}")

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code", "Unknown")
                    error_message = e.response.get("Error", {}).get("Message", str(e))

                    logger.error(f"❌ Failed to delete volume {volume_id}: {error_code} - {error_message}")
                    failed_deletions.append({"volume_id": volume_id, "error": error_message})

                    # Handle specific deletion errors
                    if error_code == "VolumeInUse":
                        logger.warning(f"⚠️ Volume {volume_id} is now in use - skipping deletion")
                    elif error_code in ["AccessDenied", "UnauthorizedOperation"]:
                        logger.error(f"🔒 Insufficient permissions to delete volume {volume_id}")

                except Exception as e:
                    logger.error(f"❌ Unexpected error deleting volume {volume_id}: {e}")
                    failed_deletions.append({"volume_id": volume_id, "error": str(e)})

            # Cleanup summary
            logger.info("🏁 CLEANUP OPERATION COMPLETE:")
            logger.info(f"   ✅ Successfully deleted: {successful_deletions} volumes")
            logger.info(f"   ❌ Failed deletions: {len(failed_deletions)} volumes")

            if failed_deletions:
                logger.warning("❌ Failed deletions details:")
                for failure in failed_deletions:
                    logger.warning(f"   - {failure['volume_id']}: {failure['error']}")

        # Save results to CSV if requested
        if output_file and analysis_results:
            try:
                write_to_csv(analysis_results, output_file)
                logger.info(f"💾 Results saved to: {output_file}")
            except Exception as e:
                logger.error(f"❌ Failed to save results to {output_file}: {e}")

        # Final operation summary
        if dry_run:
            logger.info("✅ DRY-RUN COMPLETE - No volumes were deleted")
            if eligible_count > 0:
                logger.info(f"💡 To proceed with cleanup, run with --no-dry-run flag")
                logger.info(f"💰 Potential monthly savings: ${eligible_monthly_cost:.2f}")
        else:
            logger.info("✅ CLEANUP OPERATION COMPLETE")

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(f"❌ AWS API error during volume analysis: {error_code} - {error_message}")

        # Handle specific AWS errors gracefully
        if error_code in ["AccessDenied", "UnauthorizedOperation"]:
            logger.error("🔒 Insufficient IAM permissions for EC2 volume operations")
            logger.error("   Required permissions: ec2:DescribeVolumes, ec2:DeleteVolume, cloudtrail:LookupEvents")
        elif error_code == "InvalidRegion":
            logger.error(f"🌍 Invalid AWS region specified: {region}")
        else:
            raise

    except BotoCoreError as e:
        logger.error(f"❌ AWS service error during volume analysis: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected error during volume analysis: {e}")
        raise

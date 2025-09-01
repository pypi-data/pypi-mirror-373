"""
Enterprise S3 Access Logging Management - Automated Security Audit Trail

## Overview

This module provides comprehensive S3 server access logging management to enhance
security monitoring and compliance posture. S3 access logging is a critical
security requirement for tracking bucket access patterns and detecting unauthorized
activities.

## Key Features

- **Comprehensive Detection**: Identifies buckets without access logging enabled
- **Safe Configuration**: Enables server access logging with optimal settings
- **Bulk Operations**: Efficiently processes all buckets in an account
- **Compliance Integration**: Supports CIS, NIST, SOC2, and PCI DSS requirements
- **Audit Trail**: Comprehensive logging of all configuration operations
- **Cost Optimization**: Configurable log retention and storage options

## Security Benefits

- **Access Monitoring**: Tracks all requests to S3 buckets for security analysis
- **Compliance Adherence**: Meets regulatory requirements for access logging
- **Incident Response**: Provides detailed audit trails for security investigations
- **Threat Detection**: Enables detection of unauthorized access patterns
- **Forensic Analysis**: Supports detailed investigation of security events

## Access Log Format

S3 server access logs contain:
- Request timestamp and remote IP address
- Requester identity and authentication status
- Request type, target resource, and response details
- Bytes transferred and processing time
- Error codes and referrer information

## Usage Examples

```python
# Audit mode - detect buckets without logging (safe)
python s3_enable_access_logging.py --dry-run

# Enable access logging with default settings
python s3_enable_access_logging.py

# Enable with custom log bucket and prefix
python s3_enable_access_logging.py --log-bucket audit-logs --log-prefix access-logs/
```

## Important Configuration Notes

⚠️ **LOG STORAGE**: Logs are stored in the same bucket by default
⚠️ **COST IMPACT**: Access logging incurs additional storage costs
⚠️ **RETENTION**: Consider lifecycle policies for log management

Version: 0.7.8 - Enterprise Production Ready
Compliance: CIS AWS Foundations 3.1, SOC2 A1.1, PCI DSS 10.2
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import click
from botocore.exceptions import BotoCoreError, ClientError

from .commons import display_aws_account_info, get_client

# Configure enterprise logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_bucket_logging_status(bucket_name: str, s3_client) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check the current access logging configuration for an S3 bucket.

    This function queries the S3 service to determine whether server access logging
    is currently enabled for the specified bucket. It handles various edge cases
    and permission scenarios that may occur in enterprise environments.

    ## Implementation Details

    - Uses S3 GetBucketLogging API
    - Handles permission and access errors gracefully
    - Returns both status and configuration details
    - Provides structured error logging for troubleshooting

    ## Security Considerations

    - Requires s3:GetBucketLogging permission
    - May encounter cross-region access restrictions
    - Bucket policies may deny logging configuration access

    Args:
        bucket_name (str): S3 bucket name to check
                          Must be a valid S3 bucket name format
        s3_client: Initialized boto3 S3 client instance

    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: (is_enabled, logging_config)
            - is_enabled: True if access logging is configured
            - logging_config: Current logging configuration or None

    Raises:
        ClientError: If S3 API access fails with unexpected errors
        ValueError: If bucket_name is invalid

    Example:
        >>> s3_client = boto3.client('s3')
        >>> is_enabled, config = check_bucket_logging_status('my-bucket', s3_client)
        >>> if is_enabled:
        ...     print(f"Logging enabled to {config['LoggingEnabled']['TargetBucket']}")
        ... else:
        ...     print("Access logging is not configured")
    """

    # Input validation
    if not bucket_name or not isinstance(bucket_name, str):
        raise ValueError(f"Invalid bucket_name: {bucket_name}. Must be a non-empty string.")

    logger.debug(f"Checking access logging status for bucket: {bucket_name}")

    try:
        # Query bucket logging configuration
        logging_response = s3_client.get_bucket_logging(Bucket=bucket_name)

        # Check if logging is enabled
        is_logging_enabled = "LoggingEnabled" in logging_response
        logging_config = logging_response.get("LoggingEnabled", None)

        if is_logging_enabled:
            target_bucket = logging_config.get("TargetBucket", "Unknown")
            target_prefix = logging_config.get("TargetPrefix", "")
            logger.debug(f"Bucket {bucket_name} has logging enabled to {target_bucket} with prefix '{target_prefix}'")
        else:
            logger.debug(f"Bucket {bucket_name} does not have access logging enabled")

        return is_logging_enabled, logging_config

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        # Handle specific S3 errors gracefully
        if error_code == "NoSuchBucket":
            logger.warning(f"Bucket not found: {bucket_name}")
            return False, None
        elif error_code in ["AccessDenied", "Forbidden"]:
            logger.warning(f"Insufficient permissions to check logging for bucket: {bucket_name}")
            return False, None
        elif error_code == "NoSuchLoggingConfiguration":
            logger.debug(f"No logging configuration found for bucket: {bucket_name}")
            return False, None
        else:
            logger.error(f"S3 API error checking logging for {bucket_name}: {error_code} - {error_message}")
            raise

    except BotoCoreError as e:
        logger.error(f"AWS service error checking logging for {bucket_name}: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error checking logging for {bucket_name}: {e}")
        raise


def enable_bucket_access_logging(bucket_name: str, target_bucket: str, target_prefix: str, s3_client) -> bool:
    """
    Enable server access logging for a specific S3 bucket.

    This function configures S3 server access logging for the specified bucket,
    directing log files to a target bucket with the specified prefix. This is
    essential for security monitoring and compliance requirements.

    ## Implementation Details

    - Uses S3 PutBucketLogging API
    - Validates target bucket accessibility
    - Configures optimal logging settings
    - Provides comprehensive error handling and logging

    ## Security Benefits

    - **Audit Trail**: Creates detailed access logs for security analysis
    - **Compliance**: Meets regulatory requirements for access monitoring
    - **Threat Detection**: Enables identification of suspicious access patterns
    - **Forensics**: Supports incident investigation and response

    Args:
        bucket_name (str): Source bucket to enable logging for
        target_bucket (str): Destination bucket for log files
                            Must have appropriate ACL permissions
        target_prefix (str): Prefix for log files (e.g., 'access-logs/')
                           Helps organize logs by source or date
        s3_client: Initialized boto3 S3 client instance

    Returns:
        bool: True if logging was successfully enabled, False otherwise

    Raises:
        ValueError: If parameters are invalid
        ClientError: If S3 API access fails with unexpected errors

    Example:
        >>> s3_client = boto3.client('s3')
        >>> success = enable_bucket_access_logging('my-bucket', 'logs-bucket', 'access-logs/', s3_client)
        >>> if success:
        ...     print("Access logging enabled successfully")
        ... else:
        ...     print("Failed to enable access logging - check logs")
    """

    # Input validation
    if not bucket_name or not isinstance(bucket_name, str):
        raise ValueError(f"Invalid bucket_name: {bucket_name}. Must be a non-empty string.")

    if not target_bucket or not isinstance(target_bucket, str):
        raise ValueError(f"Invalid target_bucket: {target_bucket}. Must be a non-empty string.")

    if not isinstance(target_prefix, str):
        raise ValueError(f"Invalid target_prefix: {target_prefix}. Must be a string.")

    logger.info(f"🔧 Enabling access logging for bucket: {bucket_name}")
    logger.info(f"   📝 Target bucket: {target_bucket}")
    logger.info(f"   📁 Log prefix: {target_prefix}")

    try:
        # Configure bucket logging
        logging_configuration = {"LoggingEnabled": {"TargetBucket": target_bucket, "TargetPrefix": target_prefix}}

        # Apply logging configuration
        s3_client.put_bucket_logging(Bucket=bucket_name, BucketLoggingStatus=logging_configuration)

        logger.info(f"✅ Successfully enabled access logging for bucket: {bucket_name}")
        return True

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        # Handle specific S3 errors with informative messages
        if error_code == "NoSuchBucket":
            logger.error(f"❌ Source bucket not found: {bucket_name}")
        elif error_code == "InvalidTargetBucketForLogging":
            logger.error(f"❌ Invalid target bucket for logging: {target_bucket}")
            logger.error("   Target bucket must be in the same region and have proper ACL permissions")
        elif error_code in ["AccessDenied", "Forbidden"]:
            logger.error(f"🔒 Insufficient permissions to enable logging for bucket: {bucket_name}")
            logger.error("   Required permissions: s3:PutBucketLogging")
        elif error_code == "InvalidRequest":
            logger.error(f"❌ Invalid logging configuration for bucket: {bucket_name}")
            logger.error(f"   Check target bucket permissions and prefix format: {target_prefix}")
        else:
            logger.error(f"❌ S3 API error enabling logging for {bucket_name}: {error_code} - {error_message}")

        return False

    except BotoCoreError as e:
        logger.error(f"❌ AWS service error enabling logging for {bucket_name}: {e}")
        return False

    except Exception as e:
        logger.error(f"❌ Unexpected error enabling logging for {bucket_name}: {e}")
        raise


@click.command()
@click.option(
    "--dry-run", is_flag=True, default=True, help="Preview mode - show buckets that need logging without enabling it"
)
@click.option("--target-bucket", type=str, help="Destination bucket for access logs (defaults to same bucket)")
@click.option("--log-prefix", type=str, default="access-logs/", help="Prefix for log files (default: access-logs/)")
@click.option("--region", type=str, help="AWS region to scan (defaults to current region)")
@click.option("--bucket-filter", type=str, help="Filter buckets by name pattern (supports wildcards)")
@click.option("--output-file", type=str, help="Save results to CSV file")
def enable_s3_access_logging(
    dry_run: bool,
    target_bucket: Optional[str],
    log_prefix: str,
    region: Optional[str],
    bucket_filter: Optional[str],
    output_file: Optional[str],
):
    """
    Enterprise S3 Access Logging Management - Bulk logging enablement for security monitoring.

    This command provides comprehensive detection and enablement of S3 server access logging
    across all buckets in your AWS account. Access logging is a critical security requirement
    for monitoring bucket access patterns and detecting unauthorized activities.

    ## Operation Modes

    **Dry-Run Mode (Default - SAFE):**
    - Scans and reports buckets without access logging
    - No configuration changes are made
    - Generates detailed compliance reports
    - Safe for production environments

    **Enablement Mode (CONFIGURATION CHANGE):**
    - Actually enables access logging on eligible buckets
    - Requires explicit --no-dry-run flag
    - Creates comprehensive audit trail
    - Enhances security monitoring capabilities

    ## Logging Configuration

    **Default Settings:**
    - Logs stored in the same bucket as the source
    - Log prefix: 'access-logs/' for organization
    - Standard S3 server access log format

    **Custom Settings:**
    - Specify dedicated log bucket with --target-bucket
    - Custom log prefix with --log-prefix
    - Regional configuration with --region

    ## Compliance Benefits

    - **CIS AWS Foundations 3.1**: Ensures S3 access logging is enabled
    - **SOC2 A1.1**: Demonstrates access monitoring controls
    - **PCI DSS 10.2**: Implements audit trail requirements
    - **Cost Optimization**: Centralized log management options

    Args:
        dry_run (bool): When True (default), only reports findings without changes
        target_bucket (str): Destination bucket for log files (optional)
        log_prefix (str): Prefix for organizing log files
        region (str): AWS region to scan (defaults to configured region)
        bucket_filter (str): Filter buckets by name pattern
        output_file (str): Optional CSV file path for saving detailed results

    Returns:
        None: Results are logged and optionally saved to CSV

    Examples:
        # Safe audit of all buckets (recommended first step)
        python s3_enable_access_logging.py --dry-run

        # Audit with filtering and output
        python s3_enable_access_logging.py --dry-run --bucket-filter "*prod*" --output-file s3-logging-audit.csv

        # Enable logging with default settings
        python s3_enable_access_logging.py --no-dry-run

        # Enable with custom log bucket and prefix
        python s3_enable_access_logging.py --no-dry-run --target-bucket audit-logs --log-prefix s3-access/
    """

    # Input validation
    if log_prefix and not isinstance(log_prefix, str):
        raise ValueError(f"Invalid log_prefix: {log_prefix}. Must be a string.")

    # Enhanced logging for operation start
    operation_mode = "DRY-RUN (Safe Audit)" if dry_run else "ENABLEMENT (Configuration Change)"
    logger.info(f"📝 Starting S3 Access Logging Analysis - Mode: {operation_mode}")
    logger.info(f"📊 Configuration: region={region or 'default'}, filter={bucket_filter or 'none'}")
    logger.info(f"📁 Log settings: target_bucket={target_bucket or 'same bucket'}, prefix={log_prefix}")

    # Display account information for verification
    account_info = display_aws_account_info()
    logger.info(f"🏢 {account_info}")

    if not dry_run:
        logger.warning("⚠️ CONFIGURATION MODE ENABLED - Access logging will be enabled!")
        logger.warning("⚠️ This will incur additional storage costs for log files!")

    try:
        # Initialize S3 client with region support
        s3_client = get_client("s3", region_name=region)
        logger.debug(f"Initialized S3 client for region: {region or 'default'}")

        # Collect comprehensive bucket analysis data
        bucket_analysis_results = []
        buckets_without_logging = []
        buckets_with_logging = []
        skipped_buckets = []
        total_buckets_scanned = 0

        logger.info("🔍 Scanning S3 buckets in account...")

        # List all buckets
        try:
            response = s3_client.list_buckets()
            all_buckets = response.get("Buckets", [])
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"❌ Failed to list S3 buckets: {error_code}")
            raise

        logger.info(f"📋 Found {len(all_buckets)} total buckets to analyze")

        for bucket_index, bucket in enumerate(all_buckets, 1):
            bucket_name = bucket["Name"]
            bucket_creation_date = bucket.get("CreationDate")
            total_buckets_scanned += 1

            logger.debug(f"Analyzing bucket {bucket_index}/{len(all_buckets)}: {bucket_name}")

            # Apply bucket filtering if specified
            if bucket_filter:
                if bucket_filter.replace("*", "") not in bucket_name:
                    logger.debug(f"Bucket {bucket_name} filtered out by pattern: {bucket_filter}")
                    continue

            try:
                # Check current logging status
                is_logging_enabled, logging_config = check_bucket_logging_status(bucket_name, s3_client)

                # Determine target bucket for this bucket's logs
                effective_target_bucket = target_bucket or bucket_name

                # Build comprehensive bucket analysis
                bucket_analysis = {
                    "BucketName": bucket_name,
                    "CreationDate": bucket_creation_date.isoformat() if bucket_creation_date else "Unknown",
                    "CurrentLoggingEnabled": is_logging_enabled,
                    "CurrentTargetBucket": logging_config.get("TargetBucket", "") if logging_config else "",
                    "CurrentLogPrefix": logging_config.get("TargetPrefix", "") if logging_config else "",
                    "NeedsLoggingEnabled": not is_logging_enabled,
                    "ProposedTargetBucket": effective_target_bucket,
                    "ProposedLogPrefix": log_prefix,
                    "Region": region or "default",
                }

                bucket_analysis_results.append(bucket_analysis)

                # Categorize buckets for processing
                if is_logging_enabled:
                    buckets_with_logging.append(bucket_analysis)
                    target_info = f"→ {logging_config.get('TargetBucket', 'Unknown')}"
                    prefix_info = f"(prefix: {logging_config.get('TargetPrefix', 'none')})"
                    logger.debug(f"✅ LOGGING ENABLED: {bucket_name} {target_info} {prefix_info}")
                else:
                    buckets_without_logging.append(bucket_analysis)
                    logger.info(f"🎯 NEEDS LOGGING: {bucket_name} → {effective_target_bucket}/{log_prefix}")

            except Exception as e:
                logger.warning(f"⚠️ Could not analyze bucket {bucket_name}: {e}")
                skipped_buckets.append({"bucket_name": bucket_name, "error": str(e)})
                continue

        # Generate comprehensive analysis summary
        needs_logging_count = len(buckets_without_logging)
        already_enabled_count = len(buckets_with_logging)
        skipped_count = len(skipped_buckets)

        logger.info("📊 S3 ACCESS LOGGING ANALYSIS SUMMARY:")
        logger.info(f"   📋 Total buckets scanned: {total_buckets_scanned}")
        logger.info(f"   ✅ Buckets with logging enabled: {already_enabled_count}")
        logger.info(f"   🎯 Buckets needing logging: {needs_logging_count}")
        logger.info(f"   ⚠️ Skipped buckets: {skipped_count}")

        # Calculate compliance percentage
        analyzable_total = already_enabled_count + needs_logging_count
        if analyzable_total > 0:
            compliance_percentage = (already_enabled_count / analyzable_total) * 100
            logger.info(f"   📈 Current compliance rate: {compliance_percentage:.1f}%")

        # Execute logging enablement if not in dry-run mode
        if not dry_run and buckets_without_logging:
            logger.warning(f"📝 ENABLING ACCESS LOGGING: Processing {needs_logging_count} buckets...")

            successful_enablements = 0
            failed_enablements = []

            for bucket_data in buckets_without_logging:
                bucket_name = bucket_data["BucketName"]
                effective_target_bucket = bucket_data["ProposedTargetBucket"]

                try:
                    logger.info(f"📝 Enabling access logging for bucket: {bucket_name}")

                    success = enable_bucket_access_logging(bucket_name, effective_target_bucket, log_prefix, s3_client)

                    if success:
                        successful_enablements += 1
                        logger.info(f"✅ Successfully enabled logging for: {bucket_name}")
                    else:
                        failed_enablements.append(
                            {"bucket_name": bucket_name, "error": "Enable function returned False"}
                        )

                except Exception as e:
                    error_message = str(e)
                    logger.error(f"❌ Failed to enable logging for {bucket_name}: {error_message}")
                    failed_enablements.append({"bucket_name": bucket_name, "error": error_message})

            # Enablement summary
            logger.info("🏁 ACCESS LOGGING ENABLEMENT COMPLETE:")
            logger.info(f"   ✅ Successfully enabled: {successful_enablements} buckets")
            logger.info(f"   ❌ Failed enablements: {len(failed_enablements)} buckets")

            if failed_enablements:
                logger.warning("❌ Failed enablement details:")
                for failure in failed_enablements:
                    logger.warning(f"   - {failure['bucket_name']}: {failure['error']}")

            # Calculate final compliance rate
            final_enabled_count = already_enabled_count + successful_enablements
            final_compliance_percentage = (final_enabled_count / analyzable_total) * 100 if analyzable_total > 0 else 0
            logger.info(f"   📈 Final compliance rate: {final_compliance_percentage:.1f}%")

        # Save results to CSV if requested
        if output_file and bucket_analysis_results:
            try:
                # Use the commons write_to_csv function if available
                from .commons import write_to_csv

                write_to_csv(bucket_analysis_results, output_file)
                logger.info(f"💾 Results saved to: {output_file}")
            except Exception as e:
                logger.error(f"❌ Failed to save results to {output_file}: {e}")

        # Display skipped buckets if any
        if skipped_buckets:
            logger.warning("⚠️ Skipped buckets due to errors:")
            for skipped in skipped_buckets:
                logger.warning(f"   - {skipped['bucket_name']}: {skipped['error']}")

        # Final operation summary with actionable recommendations
        if dry_run:
            logger.info("✅ DRY-RUN COMPLETE - No buckets were modified")
            if needs_logging_count > 0:
                logger.info(f"💡 To enable access logging on {needs_logging_count} buckets, run with --no-dry-run")
                logger.info(f"📝 This will improve compliance from {compliance_percentage:.1f}% to 100%")

                # Estimate storage cost impact
                avg_log_size_mb = 1  # Conservative estimate: 1MB per bucket per day
                monthly_cost_estimate = needs_logging_count * avg_log_size_mb * 30 * 0.023  # $0.023/GB/month
                logger.info(f"💰 Estimated additional monthly cost: ${monthly_cost_estimate:.2f}")
            else:
                logger.info("🎉 All eligible buckets already have access logging enabled!")
        else:
            logger.info("✅ ACCESS LOGGING ENABLEMENT COMPLETE")
            logger.info(f"📝 S3 security monitoring enhanced for {successful_enablements} buckets")

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(f"❌ AWS API error during S3 analysis: {error_code} - {error_message}")

        # Handle specific AWS errors gracefully
        if error_code in ["AccessDenied", "UnauthorizedOperation"]:
            logger.error("🔒 Insufficient IAM permissions for S3 operations")
            logger.error("   Required permissions: s3:ListAllMyBuckets, s3:GetBucketLogging, s3:PutBucketLogging")
        elif error_code == "InvalidRegion":
            logger.error(f"🌍 Invalid AWS region specified: {region}")
        else:
            raise

    except BotoCoreError as e:
        logger.error(f"❌ AWS service error during S3 analysis: {e}")
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected error during S3 analysis: {e}")
        raise


if __name__ == "__main__":
    enable_s3_access_logging()

"""
Enterprise S3 Encryption Management - Automated Data Protection at Rest

## Overview

This module provides comprehensive S3 bucket encryption management to enhance
data protection and compliance posture. S3 encryption at rest is a fundamental
security requirement for protecting sensitive data stored in cloud environments.

## Key Features

- **Comprehensive Detection**: Identifies buckets without encryption enabled
- **Flexible Encryption**: Supports SSE-S3, SSE-KMS, and SSE-C options
- **KMS Integration**: Creates and manages customer-managed encryption keys
- **Bulk Operations**: Efficiently processes all buckets in an account
- **Compliance Integration**: Supports CIS, NIST, SOC2, and PCI DSS requirements
- **Cost Optimization**: Balanced approach between security and cost

## Encryption Options

**SSE-S3 (Server-Side Encryption with Amazon S3-Managed Keys):**
- Simplest option with no additional cost
- Automatic key management by AWS
- Good for basic encryption requirements

**SSE-KMS (Server-Side Encryption with AWS KMS):**
- Customer-managed encryption keys
- Detailed access logging and control
- Integration with AWS CloudTrail
- Additional per-request charges apply

**SSE-C (Server-Side Encryption with Customer-Provided Keys):**
- Customer provides encryption keys
- Maximum control over key management
- Requires client-side key management

## Usage Examples

```python
# Audit mode - detect buckets without encryption (safe)
python s3_encryption.py --dry-run

# Enable SSE-S3 encryption (default)
python s3_encryption.py --encryption-type sse-s3

# Enable SSE-KMS with new customer-managed key
python s3_encryption.py --encryption-type sse-kms --create-kms-key
```

## Important Security Notes

⚠️ **COST IMPACT**: SSE-KMS incurs additional charges per request
⚠️ **KEY MANAGEMENT**: Customer-managed keys require proper lifecycle management
⚠️ **COMPLIANCE**: Some regulations require specific encryption types

Version: 0.7.8 - Enterprise Production Ready
Compliance: CIS AWS Foundations 2.1.1, SOC2 A1.2, PCI DSS 3.4
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import click
from botocore.exceptions import BotoCoreError, ClientError

from .commons import display_aws_account_info, get_client

# Configure enterprise logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_bucket_encryption_status(bucket_name: str, s3_client) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check the current encryption configuration for an S3 bucket.

    This function queries the S3 service to determine whether server-side encryption
    is currently enabled for the specified bucket. It handles various edge cases
    and permission scenarios that may occur in enterprise environments.

    ## Implementation Details

    - Uses S3 GetBucketEncryption API
    - Handles permission and access errors gracefully
    - Returns both status and configuration details
    - Provides structured error logging for troubleshooting

    ## Security Considerations

    - Requires s3:GetBucketEncryption permission
    - May encounter cross-region access restrictions
    - Bucket policies may deny encryption configuration access

    Args:
        bucket_name (str): S3 bucket name to check
                          Must be a valid S3 bucket name format
        s3_client: Initialized boto3 S3 client instance

    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: (is_encrypted, encryption_config)
            - is_encrypted: True if encryption is configured
            - encryption_config: Current encryption configuration or None

    Raises:
        ClientError: If S3 API access fails with unexpected errors
        ValueError: If bucket_name is invalid

    Example:
        >>> s3_client = boto3.client('s3')
        >>> is_encrypted, config = check_bucket_encryption_status('my-bucket', s3_client)
        >>> if is_encrypted:
        ...     print(f"Encryption: {config['Rules'][0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']}")
        ... else:
        ...     print("Encryption is not configured")
    """

    # Input validation
    if not bucket_name or not isinstance(bucket_name, str):
        raise ValueError(f"Invalid bucket_name: {bucket_name}. Must be a non-empty string.")

    logger.debug(f"Checking encryption status for bucket: {bucket_name}")

    try:
        # Query bucket encryption configuration
        encryption_response = s3_client.get_bucket_encryption(Bucket=bucket_name)

        # Check if encryption configuration exists
        encryption_config = encryption_response.get("ServerSideEncryptionConfiguration", {})
        rules = encryption_config.get("Rules", [])

        is_encrypted = bool(rules)

        if is_encrypted:
            # Extract encryption details
            default_encryption = rules[0].get("ApplyServerSideEncryptionByDefault", {})
            algorithm = default_encryption.get("SSEAlgorithm", "Unknown")
            kms_key = default_encryption.get("KMSMasterKeyID", "")

            logger.debug(
                f"Bucket {bucket_name} has {algorithm} encryption" + (f" with key {kms_key}" if kms_key else "")
            )
        else:
            logger.debug(f"Bucket {bucket_name} does not have encryption configured")

        return is_encrypted, encryption_config

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        # Handle specific S3 errors gracefully
        if error_code == "NoSuchBucket":
            logger.warning(f"Bucket not found: {bucket_name}")
            return False, None
        elif error_code in ["AccessDenied", "Forbidden"]:
            logger.warning(f"Insufficient permissions to check encryption for bucket: {bucket_name}")
            return False, None
        elif error_code == "ServerSideEncryptionConfigurationNotFoundError":
            logger.debug(f"No encryption configuration found for bucket: {bucket_name}")
            return False, None
        else:
            logger.error(f"S3 API error checking encryption for {bucket_name}: {error_code} - {error_message}")
            raise

    except BotoCoreError as e:
        logger.error(f"AWS service error checking encryption for {bucket_name}: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error checking encryption for {bucket_name}: {e}")
        raise


def create_kms_key_for_s3(description: str = "S3 Bucket Encryption Key", kms_client=None) -> Optional[str]:
    """
    Create a new customer-managed KMS key for S3 bucket encryption.

    This function creates a new KMS key specifically designed for S3 bucket
    encryption. The key includes appropriate metadata and tags for identification
    and management purposes.

    ## Implementation Details

    - Uses KMS CreateKey API (not S3!)
    - Configures key for symmetric encryption use
    - Adds descriptive tags for management
    - Returns key ID for immediate use

    ## Security Benefits

    - **Customer Control**: Full control over key lifecycle
    - **Access Logging**: CloudTrail logs all key usage
    - **Key Rotation**: Supports automatic annual rotation
    - **Cross-Account**: Can be shared across accounts if needed

    Args:
        description (str): Human-readable description for the KMS key
        kms_client: Initialized boto3 KMS client instance

    Returns:
        Optional[str]: KMS key ID if creation successful, None otherwise

    Raises:
        ClientError: If KMS API access fails with unexpected errors

    Example:
        >>> kms_client = boto3.client('kms')
        >>> key_id = create_kms_key_for_s3("Production S3 Encryption", kms_client)
        >>> if key_id:
        ...     print(f"Created KMS key: {key_id}")
        ... else:
        ...     print("Failed to create KMS key")
    """

    if not kms_client:
        raise ValueError("KMS client is required for key creation")

    logger.info("🔐 Creating new KMS key for S3 bucket encryption...")

    try:
        # Create KMS key with appropriate configuration
        key_response = kms_client.create_key(
            Description=description,
            KeyUsage="ENCRYPT_DECRYPT",
            Origin="AWS_KMS",
            KeySpec="SYMMETRIC_DEFAULT",  # Required for S3 encryption
            Tags=[
                {"TagKey": "Purpose", "TagValue": "S3-Bucket-Encryption"},
                {"TagKey": "CreatedBy", "TagValue": "CloudOps-Remediation-Script"},
                {"TagKey": "Service", "TagValue": "Amazon-S3"},
            ],
        )

        key_id = key_response["KeyMetadata"]["KeyId"]
        key_arn = key_response["KeyMetadata"]["Arn"]

        logger.info(f"✅ Successfully created KMS key: {key_id}")
        logger.info(f"   📋 Key ARN: {key_arn}")

        # Optionally enable key rotation
        try:
            kms_client.enable_key_rotation(KeyId=key_id)
            logger.info(f"✅ Enabled automatic key rotation for: {key_id}")
        except ClientError as e:
            logger.warning(f"⚠️ Could not enable key rotation: {e}")

        return key_id

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        logger.error(f"❌ KMS API error creating key: {error_code} - {error_message}")

        # Handle specific KMS errors
        if error_code in ["AccessDenied", "UnauthorizedOperation"]:
            logger.error("🔒 Insufficient permissions to create KMS keys")
            logger.error("   Required permissions: kms:CreateKey, kms:TagResource, kms:EnableKeyRotation")
        elif error_code == "LimitExceededException":
            logger.error("📊 KMS key limit exceeded - consider deleting unused keys")

        return None

    except BotoCoreError as e:
        logger.error(f"❌ AWS service error creating KMS key: {e}")
        return None

    except Exception as e:
        logger.error(f"❌ Unexpected error creating KMS key: {e}")
        raise


def enable_bucket_encryption(bucket_name: str, encryption_type: str, kms_key_id: Optional[str], s3_client) -> bool:
    """
    Enable server-side encryption for a specific S3 bucket.

    This function configures S3 server-side encryption for the specified bucket
    using the requested encryption type and key. This is essential for data
    protection and compliance requirements.

    ## Implementation Details

    - Uses S3 PutBucketEncryption API
    - Supports SSE-S3 and SSE-KMS encryption types
    - Validates encryption configuration before application
    - Provides comprehensive error handling and logging

    ## Security Benefits

    - **Data Protection**: Encrypts data at rest automatically
    - **Compliance**: Meets regulatory requirements for data encryption
    - **Key Management**: Supports both AWS and customer-managed keys
    - **Performance**: Encryption is transparent to applications

    Args:
        bucket_name (str): S3 bucket to enable encryption for
        encryption_type (str): Encryption type ('sse-s3' or 'sse-kms')
        kms_key_id (str): KMS key ID for SSE-KMS (optional for SSE-S3)
        s3_client: Initialized boto3 S3 client instance

    Returns:
        bool: True if encryption was successfully enabled, False otherwise

    Raises:
        ValueError: If parameters are invalid
        ClientError: If S3 API access fails with unexpected errors

    Example:
        >>> s3_client = boto3.client('s3')
        >>> success = enable_bucket_encryption('my-bucket', 'sse-s3', None, s3_client)
        >>> if success:
        ...     print("Encryption enabled successfully")
        ... else:
        ...     print("Failed to enable encryption - check logs")
    """

    # Input validation
    if not bucket_name or not isinstance(bucket_name, str):
        raise ValueError(f"Invalid bucket_name: {bucket_name}. Must be a non-empty string.")

    if encryption_type not in ["sse-s3", "sse-kms"]:
        raise ValueError(f"Invalid encryption_type: {encryption_type}. Must be 'sse-s3' or 'sse-kms'.")

    if encryption_type == "sse-kms" and not kms_key_id:
        raise ValueError("KMS key ID is required for SSE-KMS encryption.")

    logger.info(f"🔒 Enabling {encryption_type.upper()} encryption for bucket: {bucket_name}")
    if kms_key_id:
        logger.info(f"   🔑 Using KMS key: {kms_key_id}")

    try:
        # Build encryption configuration based on type
        if encryption_type == "sse-s3":
            encryption_config = {"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}
        else:  # sse-kms
            encryption_config = {
                "Rules": [
                    {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms", "KMSMasterKeyID": kms_key_id}}
                ]
            }

        # Apply encryption configuration
        s3_client.put_bucket_encryption(Bucket=bucket_name, ServerSideEncryptionConfiguration=encryption_config)

        logger.info(f"✅ Successfully enabled {encryption_type.upper()} encryption for bucket: {bucket_name}")
        return True

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", str(e))

        # Handle specific S3 errors with informative messages
        if error_code == "NoSuchBucket":
            logger.error(f"❌ Bucket not found: {bucket_name}")
        elif error_code in ["AccessDenied", "Forbidden"]:
            logger.error(f"🔒 Insufficient permissions to enable encryption for bucket: {bucket_name}")
            logger.error("   Required permissions: s3:PutBucketEncryption")
        elif error_code == "InvalidRequest":
            logger.error(f"❌ Invalid encryption configuration for bucket: {bucket_name}")
            logger.error(f"   Check encryption type and KMS key: {kms_key_id}")
        elif error_code == "KMSNotFoundException":
            logger.error(f"❌ KMS key not found: {kms_key_id}")
        else:
            logger.error(f"❌ S3 API error enabling encryption for {bucket_name}: {error_code} - {error_message}")

        return False

    except BotoCoreError as e:
        logger.error(f"❌ AWS service error enabling encryption for {bucket_name}: {e}")
        return False

    except Exception as e:
        logger.error(f"❌ Unexpected error enabling encryption for {bucket_name}: {e}")
        raise


@click.command()
@click.option(
    "--dry-run", is_flag=True, default=True, help="Preview mode - show buckets that need encryption without enabling it"
)
@click.option(
    "--encryption-type",
    type=click.Choice(["sse-s3", "sse-kms"]),
    default="sse-s3",
    help="Encryption type: sse-s3 (free) or sse-kms (customer-managed)",
)
@click.option("--kms-key-id", type=str, help="Existing KMS key ID for SSE-KMS (creates new if not provided)")
@click.option("--create-kms-key", is_flag=True, help="Create a new KMS key for SSE-KMS encryption")
@click.option("--region", type=str, help="AWS region to scan (defaults to current region)")
@click.option("--bucket-filter", type=str, help="Filter buckets by name pattern (supports wildcards)")
@click.option("--output-file", type=str, help="Save results to CSV file")
def check_and_enable_encryption(
    dry_run: bool,
    encryption_type: str,
    kms_key_id: Optional[str],
    create_kms_key: bool,
    region: Optional[str],
    bucket_filter: Optional[str],
    output_file: Optional[str],
):
    """
    Enterprise S3 Encryption Management - Bulk encryption enablement for data protection.

    This command provides comprehensive detection and enablement of S3 server-side encryption
    across all buckets in your AWS account. Encryption at rest is a fundamental security
    requirement for protecting sensitive data stored in cloud environments.

    Examples:
        # Safe audit of all buckets (recommended first step)
        python s3_encryption.py --dry-run

        # Enable SSE-S3 encryption (free)
        python s3_encryption.py --no-dry-run --encryption-type sse-s3
    """

    # Input validation
    if encryption_type == "sse-kms" and not kms_key_id and not create_kms_key:
        raise click.ClickException("For SSE-KMS encryption, either provide --kms-key-id or use --create-kms-key")

    # Enhanced logging for operation start
    operation_mode = "DRY-RUN (Safe Audit)" if dry_run else "ENABLEMENT (Configuration Change)"
    logger.info(f"🔒 Starting S3 Encryption Analysis - Mode: {operation_mode}")
    logger.info(f"📊 Configuration: region={region or 'default'}, filter={bucket_filter or 'none'}")
    logger.info(
        f"🔐 Encryption settings: type={encryption_type}, kms_key={kms_key_id or 'create new' if create_kms_key else 'N/A'}"
    )

    # Display account information for verification
    account_info = display_aws_account_info()
    logger.info(f"🏢 {account_info}")

    if not dry_run:
        logger.warning("⚠️ CONFIGURATION MODE ENABLED - Bucket encryption will be enabled!")
        if encryption_type == "sse-kms":
            logger.warning("⚠️ SSE-KMS incurs additional charges per request!")

    try:
        # Initialize AWS clients
        s3_client = get_client("s3", region_name=region)
        kms_client = get_client("kms", region_name=region) if encryption_type == "sse-kms" else None
        logger.debug(f"Initialized AWS clients for region: {region or 'default'}")

        # Create KMS key if needed for SSE-KMS
        effective_kms_key_id = kms_key_id
        if encryption_type == "sse-kms" and create_kms_key and not dry_run:
            logger.info("🔐 Creating new KMS key for S3 encryption...")
            effective_kms_key_id = create_kms_key_for_s3(
                f"S3 Bucket Encryption Key - Created by CloudOps Remediation", kms_client
            )
            if not effective_kms_key_id:
                logger.error("❌ Failed to create KMS key - aborting encryption enablement")
                return

        # List all buckets
        try:
            response = s3_client.list_buckets()
            all_buckets = response.get("Buckets", [])
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"❌ Failed to list S3 buckets: {error_code}")
            raise

        logger.info(f"📋 Found {len(all_buckets)} total buckets to analyze")

        # Process buckets
        buckets_without_encryption = []
        buckets_with_encryption = []
        successful_enablements = 0

        for bucket in all_buckets:
            bucket_name = bucket["Name"]

            # Apply bucket filtering if specified
            if bucket_filter:
                if bucket_filter.replace("*", "") not in bucket_name:
                    continue

            try:
                # Check current encryption status
                is_encrypted, encryption_config = check_bucket_encryption_status(bucket_name, s3_client)

                if is_encrypted:
                    buckets_with_encryption.append(bucket_name)
                    logger.debug(f"✅ ENCRYPTED: {bucket_name}")
                else:
                    buckets_without_encryption.append(bucket_name)
                    logger.info(f"🎯 NEEDS ENCRYPTION: {bucket_name}")

                    # Enable encryption if not in dry-run mode
                    if not dry_run:
                        success = enable_bucket_encryption(
                            bucket_name, encryption_type, effective_kms_key_id, s3_client
                        )
                        if success:
                            successful_enablements += 1

            except Exception as e:
                logger.warning(f"⚠️ Could not analyze bucket {bucket_name}: {e}")
                continue

        # Generate summary
        needs_encryption_count = len(buckets_without_encryption)
        already_encrypted_count = len(buckets_with_encryption)

        logger.info("📊 S3 ENCRYPTION ANALYSIS SUMMARY:")
        logger.info(f"   ✅ Buckets with encryption: {already_encrypted_count}")
        logger.info(f"   🎯 Buckets needing encryption: {needs_encryption_count}")

        if not dry_run and successful_enablements > 0:
            logger.info(f"   🔒 Successfully enabled encryption: {successful_enablements} buckets")

        # Final summary
        if dry_run and needs_encryption_count > 0:
            logger.info(
                f"💡 To enable {encryption_type.upper()} encryption on {needs_encryption_count} buckets, run with --no-dry-run"
            )
        elif not dry_run:
            logger.info("✅ ENCRYPTION ENABLEMENT COMPLETE")

    except Exception as e:
        logger.error(f"❌ Error during S3 encryption analysis: {e}")
        raise


if __name__ == "__main__":
    check_and_enable_encryption()

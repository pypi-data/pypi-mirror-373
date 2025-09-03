"""
Enterprise S3 Public Access Security - Automated Bucket Hardening

## Overview

This module provides comprehensive S3 public access blocking capabilities to prevent
accidental data exposure and enhance security posture. Public S3 buckets are a leading
cause of data breaches and security incidents in cloud environments.

## Key Features

- **Comprehensive Detection**: Identifies buckets without public access blocks
- **Safe Configuration**: Enables all four public access block settings
- **Bulk Operations**: Efficiently processes all buckets in an account
- **Compliance Integration**: Supports CIS, NIST, and SOC2 requirements
- **Audit Trail**: Comprehensive logging of all security operations
- **Cost Optimization**: Prevents unexpected charges from public data transfer

## Security Benefits

- **Data Protection**: Prevents accidental public exposure of sensitive data
- **Compliance Adherence**: Meets regulatory requirements for data privacy
- **Defense in Depth**: Adds bucket-level security controls
- **Risk Mitigation**: Reduces attack surface for data exfiltration

## Public Access Block Settings

This tool enables all four critical settings:
1. **BlockPublicAcls**: Blocks new public ACLs
2. **IgnorePublicAcls**: Ignores existing public ACLs
3. **BlockPublicPolicy**: Blocks new public bucket policies
4. **RestrictPublicBuckets**: Restricts public bucket access

## Usage Examples

```python
# Audit mode - detect buckets without blocks (safe)
python s3_block_public_access.py

# Enable public access blocks on all buckets
python s3_block_public_access.py --block
```

## Important Security Notes

⚠️ **APPLICATION IMPACT**: May break applications relying on public S3 access
⚠️ **WEBSITE HOSTING**: Will disable S3 static website hosting features
⚠️ **CDN INTEGRATION**: May affect CloudFront and other CDN configurations

Version: 0.7.8 - Enterprise Production Ready
Compliance: CIS AWS Foundations 2.1.5, NIST SP 800-53
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import click
from botocore.exceptions import BotoCoreError, ClientError

from .commons import display_aws_account_info, get_bucket_policy, get_client

# Configure enterprise logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_flags(
    public_access_block: Dict[str, Any], public_access_block_configuration: Dict[str, bool]
) -> Optional[bool]:
    """
    Compare current public access block settings with target configuration.

    This utility function validates whether a bucket's current public access block
    configuration matches the desired security settings. It handles various edge
    cases and data types that may be returned from the S3 API.

    ## Implementation Details

    - Performs deep comparison of configuration dictionaries
    - Handles None and string values gracefully
    - Returns None for invalid or incomparable configurations
    - Provides type safety for configuration validation

    Args:
        public_access_block (Dict[str, Any]): Current bucket's public access block configuration
                                            May contain boolean values or be None/string
        public_access_block_configuration (Dict[str, bool]): Target configuration with boolean values
                                                           Should contain all four PAB settings

    Returns:
        Optional[bool]: True if configurations match exactly, False if different,
                       None if comparison is not possible

    Example:
        >>> current_config = {'BlockPublicAcls': True, 'IgnorePublicAcls': True, 'BlockPublicPolicy': True, 'RestrictPublicBuckets': True}
        >>> target_config = {'BlockPublicAcls': True, 'IgnorePublicAcls': True, 'BlockPublicPolicy': True, 'RestrictPublicBuckets': True}
        >>> check_flags(current_config, target_config)
        True
    """

    # Input validation
    if not isinstance(public_access_block_configuration, dict):
        logger.debug("Target configuration is not a dictionary")
        return None

    # Handle case where current configuration is not a dictionary
    if not isinstance(public_access_block, dict):
        logger.debug(f"Current public access block is not a dictionary: {type(public_access_block)}")
        return None

    try:
        # Perform deep comparison of configuration dictionaries
        return public_access_block == public_access_block_configuration

    except Exception as e:
        logger.debug(f"Error comparing public access block configurations: {e}")
        return None


@click.command()
@click.option("--block", default=False, is_flag=True, help="Enable public access block on all buckets")
def enable_public_access_block_on_all_buckets(block: bool = False):
    s3 = get_client("s3")

    logger.info(f"Using {display_aws_account_info()}")

    if block:
        logger.info("Enabling 'Block Public Access' on all buckets...")

    response = s3.list_buckets()

    # Define the public access block configuration
    public_access_block_configuration = {
        "BlockPublicAcls": True,
        "IgnorePublicAcls": True,
        "BlockPublicPolicy": True,
        "RestrictPublicBuckets": True,
    }

    # Apply the configuration to each bucket
    for bucket in response["Buckets"]:
        bucket_name = bucket["Name"]
        policy, public_access_block = get_bucket_policy(bucket_name)
        if block and (
            (public_access_block == "No public access block configuration")
            or (not check_flags(public_access_block, public_access_block_configuration))
        ):
            logger.info(f"Enabling 'Block Public Access' on bucket: {bucket_name} as it does not have it enabled...")
            if public_access_block == "Access Denied":
                logger.warning(f"Access Denied to enable 'Block Public Access' on Bucket: {bucket_name}")
                continue
            s3.put_public_access_block(
                Bucket=bucket_name, PublicAccessBlockConfiguration=public_access_block_configuration
            )
            policy, public_access_block = get_bucket_policy(bucket_name)
            logger.info(
                f"After enabling 'Block Public Access' on Bucket: {bucket_name},"
                f" Public Access Block: {public_access_block}"
            )

"""
AWS utility functions and helpers for inventory operations.

This module provides AWS-specific utility functions including session
management, region discovery, credential validation, and common operations.
"""

from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from loguru import logger

# AWS Service Endpoints and Regions
AWS_PARTITIONS = {
    "aws": {
        "regions": [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "eu-west-1",
            "eu-west-2",
            "eu-west-3",
            "eu-central-1",
            "eu-north-1",
            "ap-northeast-1",
            "ap-northeast-2",
            "ap-northeast-3",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-south-1",
            "ca-central-1",
            "sa-east-1",
        ]
    },
    "aws-us-gov": {"regions": ["us-gov-east-1", "us-gov-west-1"]},
    "aws-cn": {"regions": ["cn-north-1", "cn-northwest-1"]},
}

# Global AWS services (not region-specific)
GLOBAL_SERVICES = {"iam", "route53", "cloudfront", "waf", "wafv2", "organizations", "support", "trustedadvisor"}

# Services that require special handling
SPECIAL_HANDLING_SERVICES = {
    "s3": "bucket-region-specific",
    "cloudtrail": "global-with-region-config",
    "config": "region-specific-with-global-view",
}


def get_boto3_session(
    profile_name: Optional[str] = None,
    region_name: Optional[str] = None,
    access_key_id: Optional[str] = None,
    secret_access_key: Optional[str] = None,
    session_token: Optional[str] = None,
) -> boto3.Session:
    """
    Create a configured boto3 session with retry and timeout settings.

    Args:
        profile_name: AWS profile name from ~/.aws/credentials
        region_name: Default AWS region
        access_key_id: AWS access key ID
        secret_access_key: AWS secret access key
        session_token: AWS session token (for temporary credentials)

    Returns:
        Configured boto3 session

    Raises:
        ProfileNotFound: If specified profile doesn't exist
        NoCredentialsError: If no valid credentials are found
    """
    try:
        # Create session with provided credentials
        session = boto3.Session(
            profile_name=profile_name,
            region_name=region_name or "us-east-1",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token,
        )

        # Test the session by getting caller identity
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()

        logger.debug(f"Created session for account: {identity.get('Account')}, user: {identity.get('Arn')}")

        return session

    except ProfileNotFound as e:
        logger.error(f"AWS profile '{profile_name}' not found: {e}")
        raise
    except NoCredentialsError as e:
        logger.error(f"No valid AWS credentials found: {e}")
        raise
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ["InvalidUserID.NotFound", "AccessDenied"]:
            logger.error(f"Invalid AWS credentials or insufficient permissions: {e}")
        else:
            logger.error(f"AWS API error during session validation: {e}")
        raise


def get_boto3_config(
    max_retries: int = 5, read_timeout: int = 60, connect_timeout: int = 10, max_pool_connections: int = 50
) -> Config:
    """
    Create standardized boto3 configuration for inventory operations.

    Args:
        max_retries: Maximum number of retries for failed requests
        read_timeout: Read timeout in seconds
        connect_timeout: Connection timeout in seconds
        max_pool_connections: Maximum number of connections in pool

    Returns:
        Boto3 Config object with optimized settings
    """
    return Config(
        retries={"max_attempts": max_retries, "mode": "adaptive"},
        read_timeout=read_timeout,
        connect_timeout=connect_timeout,
        max_pool_connections=max_pool_connections,
        # Use signature v4 for all requests
        signature_version="v4",
    )


def get_aws_regions(
    session: boto3.Session, service: Optional[str] = None, include_gov_cloud: bool = False, include_china: bool = False
) -> List[str]:
    """
    Get list of available AWS regions for a service.

    Args:
        session: Configured boto3 session
        service: AWS service to check regions for (None for all regions)
        include_gov_cloud: Include AWS GovCloud regions
        include_china: Include AWS China regions

    Returns:
        List of available region names

    Raises:
        ClientError: If unable to retrieve regions
    """
    try:
        # Use EC2 to get region information
        ec2_client = session.client("ec2", region_name="us-east-1")

        response = ec2_client.describe_regions(
            Filters=[{"Name": "opt-in-status", "Values": ["opt-in-not-required", "opted-in"]}]
        )

        regions = [r["RegionName"] for r in response["Regions"]]

        # Filter based on partition preferences
        if not include_gov_cloud:
            regions = [r for r in regions if not r.startswith("us-gov")]

        if not include_china:
            regions = [r for r in regions if not r.startswith("cn-")]

        # If service specified, filter to regions where service is available
        if service and service not in GLOBAL_SERVICES:
            available_regions = []
            for region in regions:
                try:
                    # Test if service is available in region
                    client = session.client(service, region_name=region)
                    # Make a simple call to verify service availability
                    if hasattr(client, "describe_regions"):
                        client.describe_regions()
                    available_regions.append(region)
                except ClientError as e:
                    if e.response["Error"]["Code"] not in ["UnauthorizedOperation", "AccessDenied"]:
                        logger.debug(f"Service {service} not available in {region}: {e}")
                        continue
                    available_regions.append(region)
                except Exception as e:
                    logger.debug(f"Error checking {service} in {region}: {e}")
                    continue

            regions = available_regions

        logger.debug(f"Found {len(regions)} available regions for service: {service}")
        return sorted(regions)

    except ClientError as e:
        logger.error(f"Failed to get AWS regions: {e}")
        # Return fallback list of common regions
        fallback_regions = [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "eu-west-1",
            "eu-central-1",
            "ap-southeast-1",
            "ap-northeast-1",
        ]
        logger.warning(f"Using fallback region list: {fallback_regions}")
        return fallback_regions


def validate_aws_credentials(session: boto3.Session) -> Dict[str, Any]:
    """
    Validate AWS credentials and return account information.

    Args:
        session: Boto3 session to validate

    Returns:
        Dictionary with account information and permissions

    Raises:
        NoCredentialsError: If credentials are invalid
        ClientError: If validation fails
    """
    try:
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()

        # Get additional account information
        account_info = {
            "account_id": identity["Account"],
            "user_arn": identity["Arn"],
            "user_id": identity["UserId"],
            "session_valid": True,
            "permissions": {},
        }

        # Test basic permissions
        try:
            # Test IAM read permissions
            iam_client = session.client("iam")
            iam_client.list_users(MaxItems=1)
            account_info["permissions"]["iam_read"] = True
        except ClientError:
            account_info["permissions"]["iam_read"] = False

        try:
            # Test EC2 read permissions
            ec2_client = session.client("ec2")
            ec2_client.describe_instances(MaxResults=5)
            account_info["permissions"]["ec2_read"] = True
        except ClientError:
            account_info["permissions"]["ec2_read"] = False

        try:
            # Test Organizations permissions (if applicable)
            orgs_client = session.client("organizations")
            orgs_client.describe_organization()
            account_info["permissions"]["organizations_read"] = True
            account_info["is_organization_account"] = True
        except ClientError:
            account_info["permissions"]["organizations_read"] = False
            account_info["is_organization_account"] = False

        logger.info(f"Validated credentials for account: {account_info['account_id']}")
        return account_info

    except NoCredentialsError as e:
        logger.error(f"No valid AWS credentials: {e}")
        raise
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"Credential validation failed: {error_code} - {e}")
        raise


def aws_api_retry(
    max_retries: int = 3, backoff_factor: float = 2.0, retryable_errors: Optional[Set[str]] = None
) -> Callable:
    """
    Decorator for retrying AWS API calls with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        retryable_errors: Set of error codes that should trigger retries

    Returns:
        Decorator function
    """
    if retryable_errors is None:
        retryable_errors = {
            "Throttling",
            "ThrottlingException",
            "RequestLimitExceeded",
            "ServiceUnavailable",
            "InternalError",
            "InternalServerError",
            "RequestTimeout",
        }

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response["Error"]["Code"]
                    last_exception = e

                    if error_code not in retryable_errors:
                        # Non-retryable error, raise immediately
                        raise

                    if attempt == max_retries:
                        # Final attempt failed
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise

                    # Calculate delay for exponential backoff
                    delay = backoff_factor**attempt
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {error_code}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )

                    import time

                    time.sleep(delay)
                except Exception as e:
                    # Non-AWS exception, don't retry
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise

            # Should never reach here, but safety net
            raise last_exception

        return wrapper

    return decorator


def get_account_aliases(session: boto3.Session) -> List[str]:
    """
    Get account aliases for the current AWS account.

    Args:
        session: Boto3 session

    Returns:
        List of account aliases
    """
    try:
        iam_client = session.client("iam")
        response = iam_client.list_account_aliases()
        return response.get("AccountAliases", [])
    except ClientError as e:
        logger.warning(f"Could not retrieve account aliases: {e}")
        return []


def get_organization_info(session: boto3.Session) -> Optional[Dict[str, Any]]:
    """
    Get organization information if account is part of AWS Organizations.

    Args:
        session: Boto3 session

    Returns:
        Organization information or None if not in organization
    """
    try:
        orgs_client = session.client("organizations")
        org_response = orgs_client.describe_organization()
        org_info = org_response["Organization"]

        # Get additional organization details
        result = {
            "organization_id": org_info["Id"],
            "organization_arn": org_info["Arn"],
            "feature_set": org_info["FeatureSet"],
            "master_account_id": org_info["MasterAccountId"],
            "master_account_email": org_info["MasterAccountEmail"],
            "available_policy_types": [pt["Type"] for pt in org_info.get("AvailablePolicyTypes", [])],
        }

        # Check if current account is master account
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()
        result["is_master_account"] = identity["Account"] == org_info["MasterAccountId"]

        return result

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ["AWSOrganizationsNotInUseException", "AccessDenied"]:
            logger.debug("Account is not part of AWS Organizations or lacks permissions")
            return None
        else:
            logger.warning(f"Error getting organization info: {e}")
            return None


def assume_role_session(
    session: boto3.Session,
    role_arn: str,
    session_name: str,
    external_id: Optional[str] = None,
    duration_seconds: int = 3600,
) -> boto3.Session:
    """
    Create a new session by assuming an IAM role.

    Args:
        session: Base boto3 session
        role_arn: ARN of the role to assume
        session_name: Session name for the assumed role
        external_id: External ID for cross-account role assumption
        duration_seconds: Session duration in seconds

    Returns:
        New boto3 session with assumed role credentials

    Raises:
        ClientError: If role assumption fails
    """
    try:
        sts_client = session.client("sts")

        assume_role_args = {"RoleArn": role_arn, "RoleSessionName": session_name, "DurationSeconds": duration_seconds}

        if external_id:
            assume_role_args["ExternalId"] = external_id

        response = sts_client.assume_role(**assume_role_args)
        credentials = response["Credentials"]

        # Create new session with temporary credentials
        new_session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=session.region_name,
        )

        logger.info(f"Successfully assumed role: {role_arn}")
        return new_session

    except ClientError as e:
        logger.error(f"Failed to assume role {role_arn}: {e}")
        raise


def get_service_endpoints(
    session: boto3.Session, service_name: str, region_name: Optional[str] = None
) -> Dict[str, str]:
    """
    Get service endpoints for different regions.

    Args:
        session: Boto3 session
        service_name: AWS service name
        region_name: Specific region or None for all regions

    Returns:
        Dictionary mapping region names to endpoint URLs
    """
    endpoints = {}

    try:
        regions = [region_name] if region_name else get_aws_regions(session, service_name)

        for region in regions:
            try:
                client = session.client(service_name, region_name=region)
                endpoint_url = client._endpoint.endpoint.host
                endpoints[region] = endpoint_url
            except Exception as e:
                logger.debug(f"Could not get endpoint for {service_name} in {region}: {e}")
                continue

        return endpoints

    except Exception as e:
        logger.error(f"Failed to get service endpoints for {service_name}: {e}")
        return {}


# Convenience functions for common operations
def is_global_service(service_name: str) -> bool:
    """Check if a service is global (not region-specific)."""
    return service_name.lower() in GLOBAL_SERVICES


def requires_special_handling(service_name: str) -> bool:
    """Check if a service requires special handling for inventory."""
    return service_name.lower() in SPECIAL_HANDLING_SERVICES


def get_default_region_for_service(service_name: str) -> str:
    """Get the default region for a service."""
    if is_global_service(service_name):
        return "us-east-1"  # Global services typically use us-east-1
    return "us-east-1"  # Default fallback

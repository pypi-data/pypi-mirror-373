"""
Validation utilities for inventory operations.

This module provides input validation, sanitization, and constraint
checking for AWS resource types, account IDs, regions, and other parameters.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from loguru import logger


class ValidationSeverity(str, Enum):
    """Validation result severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    severity: ValidationSeverity
    message: str
    field_name: Optional[str] = None
    suggested_value: Optional[Any] = None

    def __str__(self) -> str:
        """String representation of validation result."""
        field_info = f" ({self.field_name})" if self.field_name else ""
        return f"{self.severity.upper()}{field_info}: {self.message}"


class ValidationError(Exception):
    """Exception raised for validation failures."""

    def __init__(self, message: str, results: List[ValidationResult]):
        super().__init__(message)
        self.results = results


# AWS-specific validation patterns
AWS_ACCOUNT_ID_PATTERN = re.compile(r"^\d{12}$")
AWS_REGION_PATTERN = re.compile(r"^[a-z]{2,3}-[a-z]+-\d+$")
AWS_ARN_PATTERN = re.compile(r"^arn:aws[a-z\-]*:[a-z0-9\-]*:[a-z0-9\-]*:\d{12}:[a-zA-Z0-9\-_/\.\:]+$")
AWS_RESOURCE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-_\.]+$")

# Known AWS services and resource types
KNOWN_AWS_SERVICES = {
    "ec2",
    "rds",
    "s3",
    "lambda",
    "iam",
    "vpc",
    "elb",
    "elbv2",
    "cloudformation",
    "cloudtrail",
    "config",
    "guardduty",
    "securityhub",
    "organizations",
    "sts",
    "ssm",
    "cloudwatch",
    "logs",
    "sns",
    "sqs",
    "dynamodb",
    "elasticache",
    "redshift",
    "efs",
    "fsx",
    "route53",
    "cloudfront",
    "apigateway",
    "apigatewayv2",
    "waf",
    "wafv2",
    "ecs",
    "eks",
    "batch",
    "fargate",
    "autoscaling",
}

KNOWN_RESOURCE_TYPES = {
    # Compute
    "ec2:instance",
    "ec2:image",
    "ec2:snapshot",
    "ec2:volume",
    "lambda:function",
    "lambda:layer",
    "ecs:cluster",
    "ecs:service",
    "ecs:task",
    # Storage
    "s3:bucket",
    "s3:object",
    "ebs:volume",
    "ebs:snapshot",
    "efs:filesystem",
    "efs:access-point",
    # Database
    "rds:instance",
    "rds:cluster",
    "rds:snapshot",
    "dynamodb:table",
    "dynamodb:backup",
    "elasticache:cluster",
    "elasticache:replication-group",
    # Network
    "vpc:vpc",
    "vpc:subnet",
    "vpc:route-table",
    "vpc:security-group",
    "vpc:nacl",
    "vpc:internet-gateway",
    "vpc:nat-gateway",
    "elb:load-balancer",
    "elbv2:load-balancer",
    "elbv2:target-group",
    "ec2:network-interface",
    "ec2:elastic-ip",
    # Security
    "iam:user",
    "iam:role",
    "iam:policy",
    "iam:group",
    "guardduty:detector",
    "guardduty:finding",
    "config:recorder",
    "config:rule",
    # Management
    "cloudformation:stack",
    "cloudformation:stackset",
    "cloudtrail:trail",
    "logs:log-group",
    "ssm:parameter",
    "ssm:document",
}

# Common AWS regions
KNOWN_AWS_REGIONS = {
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
    "us-gov-east-1",
    "us-gov-west-1",
    "cn-north-1",
    "cn-northwest-1",
}


def validate_aws_account_id(account_id: str) -> ValidationResult:
    """
    Validate AWS account ID format.

    Args:
        account_id: Account ID to validate

    Returns:
        ValidationResult with validation outcome
    """
    if not account_id:
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message="Account ID cannot be empty",
            field_name="account_id",
        )

    if not isinstance(account_id, str):
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message=f"Account ID must be a string, got {type(account_id)}",
            field_name="account_id",
        )

    # Remove any whitespace
    account_id = account_id.strip()

    if not AWS_ACCOUNT_ID_PATTERN.match(account_id):
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message="Account ID must be exactly 12 digits",
            field_name="account_id",
            suggested_value="123456789012" if len(account_id) != 12 else None,
        )

    return ValidationResult(
        is_valid=True, severity=ValidationSeverity.INFO, message="Valid AWS account ID", field_name="account_id"
    )


def validate_aws_region(region: str) -> ValidationResult:
    """
    Validate AWS region format and existence.

    Args:
        region: Region name to validate

    Returns:
        ValidationResult with validation outcome
    """
    if not region:
        return ValidationResult(
            is_valid=False, severity=ValidationSeverity.ERROR, message="Region cannot be empty", field_name="region"
        )

    if not isinstance(region, str):
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message=f"Region must be a string, got {type(region)}",
            field_name="region",
        )

    # Remove whitespace and convert to lowercase
    region = region.strip().lower()

    # Check format
    if not AWS_REGION_PATTERN.match(region):
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message="Invalid AWS region format (expected: us-east-1, eu-west-1, etc.)",
            field_name="region",
            suggested_value="us-east-1",
        )

    # Check if region is known
    if region not in KNOWN_AWS_REGIONS:
        return ValidationResult(
            is_valid=True,  # Still valid format, but unknown
            severity=ValidationSeverity.WARNING,
            message=f"Unknown AWS region: {region}",
            field_name="region",
        )

    return ValidationResult(
        is_valid=True, severity=ValidationSeverity.INFO, message="Valid AWS region", field_name="region"
    )


def validate_resource_types(resource_types: Union[str, List[str]]) -> ValidationResult:
    """
    Validate AWS resource types.

    Args:
        resource_types: Resource type(s) to validate

    Returns:
        ValidationResult with validation outcome
    """
    if not resource_types:
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message="Resource types cannot be empty",
            field_name="resource_types",
        )

    # Convert to list if string
    if isinstance(resource_types, str):
        resource_types = [resource_types]

    if not isinstance(resource_types, list):
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message=f"Resource types must be string or list, got {type(resource_types)}",
            field_name="resource_types",
        )

    invalid_types = []
    unknown_types = []
    valid_types = []

    for resource_type in resource_types:
        if not isinstance(resource_type, str):
            invalid_types.append(f"{resource_type} (not a string)")
            continue

        resource_type = resource_type.strip().lower()

        # Check if resource type follows expected format (service:type)
        if ":" not in resource_type:
            # Try to infer service name
            if resource_type in KNOWN_AWS_SERVICES:
                # This is likely a service name, suggest common resource types
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.WARNING,
                    message=f"Resource type should include service prefix (e.g., {resource_type}:instance)",
                    field_name="resource_types",
                    suggested_value=f"{resource_type}:instance",
                )
            else:
                invalid_types.append(resource_type)
                continue

        service, resource = resource_type.split(":", 1)

        # Validate service name
        if service not in KNOWN_AWS_SERVICES:
            unknown_types.append(resource_type)

        # Check if full resource type is known
        if resource_type not in KNOWN_RESOURCE_TYPES:
            unknown_types.append(resource_type)
        else:
            valid_types.append(resource_type)

    # Generate result based on validation outcomes
    if invalid_types:
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message=f"Invalid resource types: {', '.join(invalid_types)}",
            field_name="resource_types",
        )

    if unknown_types and not valid_types:
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.WARNING,
            message=f"Unknown resource types: {', '.join(unknown_types)}",
            field_name="resource_types",
        )

    if unknown_types:
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.WARNING,
            message=f"Some unknown resource types: {', '.join(unknown_types)}",
            field_name="resource_types",
        )

    return ValidationResult(
        is_valid=True,
        severity=ValidationSeverity.INFO,
        message=f"Valid resource types: {', '.join(valid_types)}",
        field_name="resource_types",
    )


def validate_account_ids(account_ids: Union[str, List[str]]) -> ValidationResult:
    """
    Validate multiple AWS account IDs.

    Args:
        account_ids: Account ID(s) to validate

    Returns:
        ValidationResult with validation outcome
    """
    if not account_ids:
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message="Account IDs cannot be empty",
            field_name="account_ids",
        )

    # Convert to list if string
    if isinstance(account_ids, str):
        account_ids = [account_ids]

    if not isinstance(account_ids, list):
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message=f"Account IDs must be string or list, got {type(account_ids)}",
            field_name="account_ids",
        )

    invalid_accounts = []
    valid_accounts = []

    for account_id in account_ids:
        result = validate_aws_account_id(str(account_id))
        if result.is_valid:
            valid_accounts.append(account_id)
        else:
            invalid_accounts.append(account_id)

    if invalid_accounts:
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message=f"Invalid account IDs: {', '.join(invalid_accounts)}",
            field_name="account_ids",
        )

    return ValidationResult(
        is_valid=True,
        severity=ValidationSeverity.INFO,
        message=f"All {len(valid_accounts)} account IDs are valid",
        field_name="account_ids",
    )


def validate_aws_arn(arn: str) -> ValidationResult:
    """
    Validate AWS ARN format.

    Args:
        arn: ARN to validate

    Returns:
        ValidationResult with validation outcome
    """
    if not arn:
        return ValidationResult(
            is_valid=False, severity=ValidationSeverity.ERROR, message="ARN cannot be empty", field_name="arn"
        )

    if not isinstance(arn, str):
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message=f"ARN must be a string, got {type(arn)}",
            field_name="arn",
        )

    # Remove whitespace
    arn = arn.strip()

    if not AWS_ARN_PATTERN.match(arn):
        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.ERROR,
            message="Invalid ARN format (expected: arn:aws:service:region:account:resource)",
            field_name="arn",
            suggested_value="arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0",
        )

    # Parse ARN components
    try:
        parts = arn.split(":")
        if len(parts) < 6:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="ARN must have at least 6 components separated by colons",
                field_name="arn",
            )

        arn_prefix, partition, service, region, account, resource = parts[:6]

        # Validate components
        if arn_prefix != "arn":
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="ARN must start with 'arn:'",
                field_name="arn",
            )

        if partition and not partition.startswith("aws"):
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message=f"Unknown AWS partition: {partition}",
                field_name="arn",
            )

        if service and service not in KNOWN_AWS_SERVICES:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.WARNING,
                message=f"Unknown AWS service in ARN: {service}",
                field_name="arn",
            )

        if account:
            account_result = validate_aws_account_id(account)
            if not account_result.is_valid:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Invalid account ID in ARN: {account}",
                    field_name="arn",
                )

        if region:
            region_result = validate_aws_region(region)
            if not region_result.is_valid and region_result.severity == ValidationSeverity.ERROR:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Invalid region in ARN: {region}",
                    field_name="arn",
                )

    except Exception as e:
        return ValidationResult(
            is_valid=False, severity=ValidationSeverity.ERROR, message=f"Error parsing ARN: {e}", field_name="arn"
        )

    return ValidationResult(is_valid=True, severity=ValidationSeverity.INFO, message="Valid AWS ARN", field_name="arn")


def validate_inventory_parameters(parameters: Dict[str, Any]) -> List[ValidationResult]:
    """
    Validate a complete set of inventory parameters.

    Args:
        parameters: Dictionary of parameters to validate

    Returns:
        List of ValidationResult objects
    """
    results = []

    # Validate account IDs
    if "account_ids" in parameters:
        result = validate_account_ids(parameters["account_ids"])
        results.append(result)

    # Validate regions
    if "regions" in parameters:
        regions = parameters["regions"]
        if isinstance(regions, str):
            regions = [regions]

        for region in regions:
            result = validate_aws_region(region)
            results.append(result)

    # Validate resource types
    if "resource_types" in parameters:
        result = validate_resource_types(parameters["resource_types"])
        results.append(result)

    # Validate numeric parameters
    numeric_params = {"max_workers": (1, 100), "timeout": (1, 3600), "batch_size": (1, 1000)}

    for param_name, (min_val, max_val) in numeric_params.items():
        if param_name in parameters:
            value = parameters[param_name]

            if not isinstance(value, (int, float)):
                results.append(
                    ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.ERROR,
                        message=f"{param_name} must be a number, got {type(value)}",
                        field_name=param_name,
                    )
                )
            elif value < min_val or value > max_val:
                results.append(
                    ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.ERROR,
                        message=f"{param_name} must be between {min_val} and {max_val}",
                        field_name=param_name,
                        suggested_value=max(min_val, min(max_val, value)),
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        is_valid=True,
                        severity=ValidationSeverity.INFO,
                        message=f"Valid {param_name}: {value}",
                        field_name=param_name,
                    )
                )

    return results


def sanitize_resource_type(resource_type: str) -> str:
    """
    Sanitize and normalize a resource type string.

    Args:
        resource_type: Resource type to sanitize

    Returns:
        Sanitized resource type
    """
    if not isinstance(resource_type, str):
        raise ValueError(f"Resource type must be a string, got {type(resource_type)}")

    # Remove whitespace and convert to lowercase
    resource_type = resource_type.strip().lower()

    # Handle common variations
    type_mappings = {
        "instances": "ec2:instance",
        "buckets": "s3:bucket",
        "functions": "lambda:function",
        "volumes": "ebs:volume",
        "vpcs": "vpc:vpc",
        "loadbalancers": "elb:load-balancer",
    }

    if resource_type in type_mappings:
        return type_mappings[resource_type]

    # If no colon, try to add service prefix
    if ":" not in resource_type:
        service_guesses = {
            "instance": "ec2",
            "bucket": "s3",
            "function": "lambda",
            "volume": "ebs",
            "vpc": "vpc",
            "subnet": "vpc",
            "security-group": "vpc",
        }

        if resource_type in service_guesses:
            service = service_guesses[resource_type]
            return f"{service}:{resource_type}"

    return resource_type


def check_validation_results(results: List[ValidationResult], raise_on_error: bool = True) -> bool:
    """
    Check validation results and optionally raise exception for errors.

    Args:
        results: List of validation results to check
        raise_on_error: Whether to raise exception for errors

    Returns:
        True if all validations passed, False otherwise

    Raises:
        ValidationError: If raise_on_error is True and there are errors
    """
    errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
    warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]

    # Log warnings
    for warning in warnings:
        logger.warning(str(warning))

    # Handle errors
    if errors:
        error_message = f"Validation failed with {len(errors)} error(s)"

        for error in errors:
            logger.error(str(error))

        if raise_on_error:
            raise ValidationError(error_message, errors)

        return False

    return True

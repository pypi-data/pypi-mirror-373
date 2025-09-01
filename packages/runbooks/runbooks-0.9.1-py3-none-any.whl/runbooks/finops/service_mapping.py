#!/usr/bin/env python3
"""
AWS Service Name Mapping and Standardization
Provides comprehensive mapping of AWS service names to standardized abbreviations
for space-efficient display in FinOps dashboards and reports.
"""

from typing import Dict

# Comprehensive AWS Service Name Mapping Dictionary
# Maps full AWS service names to standardized short names for display
AWS_SERVICE_MAPPING: Dict[str, str] = {
    # Compute Services
    "Amazon Elastic Compute Cloud - Compute": "EC2",
    "EC2 - Other": "EC2-Other",
    "AWS Lambda": "Lambda",
    "Amazon Elastic Container Service": "ECS",
    "Amazon Elastic Kubernetes Service": "EKS",
    "AWS Batch": "Batch",
    "AWS Fargate": "Fargate",
    # Storage Services
    "Amazon Simple Storage Service": "S3",
    "Amazon Elastic Block Store": "EBS",
    "Amazon Elastic File System": "EFS",
    "AWS Storage Gateway": "Storage-GW",
    "Amazon FSx": "FSx",
    # Database Services
    "Amazon Relational Database Service": "RDS",
    "Amazon DynamoDB": "DynamoDB",
    "Amazon Redshift": "Redshift",
    "Amazon ElastiCache": "ElastiCache",
    "Amazon DocumentDB": "DocumentDB",
    "Amazon Neptune": "Neptune",
    "Amazon Timestream": "Timestream",
    # Networking Services
    "Amazon Virtual Private Cloud": "VPC",
    "Amazon CloudFront": "CloudFront",
    "Amazon Route 53": "Route53",
    "AWS Direct Connect": "DirectConnect",
    "Elastic Load Balancing": "ELB",
    "Amazon API Gateway": "API-Gateway",
    "AWS Transit Gateway": "Transit-GW",
    # Monitoring & Management
    "AmazonCloudWatch": "CloudWatch",
    "AWS CloudTrail": "CloudTrail",
    "AWS Config": "Config",
    "AWS Systems Manager": "SSM",
    "AWS X-Ray": "X-Ray",
    "Amazon Inspector": "Inspector",
    # Security Services
    "AWS Identity and Access Management": "IAM",
    "AWS Certificate Manager": "ACM",
    "AWS Key Management Service": "KMS",
    "AWS Secrets Manager": "Secrets-Mgr",
    "Amazon Cognito": "Cognito",
    "AWS Security Hub": "Security-Hub",
    "Amazon GuardDuty": "GuardDuty",
    # Analytics Services
    "AWS Glue": "Glue",
    "Amazon Kinesis": "Kinesis",
    "Amazon EMR": "EMR",
    "Amazon Athena": "Athena",
    "Amazon QuickSight": "QuickSight",
    "AWS Data Pipeline": "Data-Pipeline",
    # Application Integration
    "Amazon Simple Queue Service": "SQS",
    "Amazon Simple Notification Service": "SNS",
    "Amazon EventBridge": "EventBridge",
    "AWS Step Functions": "Step-Functions",
    "Amazon MQ": "MQ",
    # Developer Tools
    "AWS CodeCommit": "CodeCommit",
    "AWS CodeBuild": "CodeBuild",
    "AWS CodeDeploy": "CodeDeploy",
    "AWS CodePipeline": "CodePipeline",
    "AWS CodeStar": "CodeStar",
    # Business Applications
    "Amazon WorkSpaces": "WorkSpaces",
    "Amazon AppStream 2.0": "AppStream",
    "Amazon Connect": "Connect",
    "Amazon Chime": "Chime",
    # Cost Management
    "AWS Cost Explorer": "Cost-Explorer",
    "AWS Budgets": "Budgets",
    "Savings Plans for AWS Compute usage": "Savings-Plans",
    # Support & Billing
    "AWS Support (Business)": "Support",
    "AWS Support (Enterprise)": "Support-Ent",
    "AWS Payment Cryptography": "Payment-Crypto",
    # Special Cases and Variations
    "Simple Storage Service": "S3",
    "Virtual Private Cloud": "VPC",
    "Elastic Compute Cloud": "EC2",
    "Simple Queue Service": "SQS",
    "Simple Notification Service": "SNS",
    "Key Management Service": "KMS",
    "Identity and Access Management": "IAM",
    # Directory Services
    "AWS Directory Service": "Directory",
    "AWS Managed Microsoft AD": "Managed-AD",
    # Machine Learning
    "Amazon SageMaker": "SageMaker",
    "Amazon Rekognition": "Rekognition",
    "Amazon Comprehend": "Comprehend",
    "Amazon Translate": "Translate",
    # IoT Services
    "AWS IoT Core": "IoT-Core",
    "AWS IoT Device Management": "IoT-Device",
    "AWS IoT Analytics": "IoT-Analytics",
    # Transfer Services
    "AWS Transfer Family": "Transfer",
    "AWS DataSync": "DataSync",
    "AWS Snow Family": "Snow",
    # Contact Center
    "Contact Center Telecommunications": "Contact-Center",
    "Contact Lens for Amazon Connect": "Contact-Lens",
    # WAF & Shield
    "AWS WAF": "WAF",
    "AWS Shield": "Shield",
    # Email
    "Amazon Simple Email Service": "SES",
    # Tax
    "Tax": "Tax",  # Usually filtered out, but included for completeness
}


def get_service_display_name(service_name: str) -> str:
    """
    Get standardized display name for AWS service.

    Args:
        service_name: Full AWS service name

    Returns:
        Standardized short name for display
    """
    # Direct mapping lookup
    if service_name in AWS_SERVICE_MAPPING:
        return AWS_SERVICE_MAPPING[service_name]

    # Fallback: Clean up common patterns
    cleaned = service_name

    # Remove common AWS prefixes
    cleaned = cleaned.replace("Amazon ", "").replace("AWS ", "")

    # Remove common suffixes
    cleaned = cleaned.replace(" Service", "").replace(" (Business)", "")

    # Handle long names by truncating intelligently
    if len(cleaned) > 15:
        # Try to get meaningful abbreviation
        words = cleaned.split()
        if len(words) > 1:
            # Take first letter of each word for abbreviation
            cleaned = "".join(word[0].upper() for word in words if word)
            # If still too long, take first 12 characters
            if len(cleaned) > 12:
                cleaned = cleaned[:12]
        else:
            # Single long word, truncate with ellipsis
            cleaned = cleaned[:12] + ("..." if len(cleaned) > 12 else "")

    return cleaned


def get_top_services_display(services_dict: Dict[str, float], limit: int = 3) -> str:
    """
    Format top services for display with standardized names.

    Args:
        services_dict: Dictionary of service names to costs
        limit: Number of top services to display

    Returns:
        Formatted string for display
    """
    if not services_dict:
        return "[dim]None[/]"

    # Sort by cost and take top services
    sorted_services = sorted(services_dict.items(), key=lambda x: x[1], reverse=True)
    top_services = sorted_services[:limit]

    # Format for display
    services_text = []
    for service, cost in top_services:
        display_name = get_service_display_name(service)
        services_text.append(f"{display_name}: ${cost:.0f}")

    return "\n".join(services_text)


# Export for other modules
__all__ = ["AWS_SERVICE_MAPPING", "get_service_display_name", "get_top_services_display"]

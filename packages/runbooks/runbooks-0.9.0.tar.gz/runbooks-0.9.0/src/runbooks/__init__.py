"""
CloudOps Runbooks - Enterprise AWS Automation & Cloud Foundations Toolkit

A comprehensive enterprise-grade automation platform for AWS cloud operations,
designed for CloudOps, DevOps, and SRE teams managing multi-account environments.

## Core Capabilities

### 🔍 Discovery & Assessment
- **Cloud Foundations Assessment Tool (CFAT)**: Automated AWS environment discovery
  and best practices assessment with actionable remediation guidance
- **Multi-Account Inventory**: Comprehensive resource discovery across AWS Organizations
- **Security Baseline Assessment**: Automated security posture evaluation
- **Cost & Financial Operations**: Resource utilization and cost optimization analysis

### ⚙️ Operations & Automation
- **AWS Resource Operations**: Enterprise-grade EC2, S3, DynamoDB management
- **Organization Management**: AWS Organizations structure and account automation
- **Identity & Access Management**: Cross-account IAM role and policy management
- **Infrastructure Automation**: CloudFormation, networking, and compliance operations

### 🏛️ Enterprise Features
- **Multi-Deployment Support**: CLI, Docker, AWS Lambda, Kubernetes ready
- **Environment Configuration**: Comprehensive environment variable support
- **Monitoring & Notifications**: SNS integration and operational awareness
- **KISS Architecture**: Simple, maintainable, no-legacy-complexity design

## Documentation

For comprehensive documentation, examples, and best practices:
https://cloudops.oceansoft.io/cloud-foundation/cfat-assessment-tool.html

## Quick Start

```python
# Assessment and Discovery
from runbooks.cfat import AssessmentRunner
from runbooks.inventory import InventoryCollector
from runbooks.security import SecurityBaselineTester

# Operations and Automation
from runbooks.operate import EC2Operations, S3Operations, DynamoDBOperations

# Assessment
runner = AssessmentRunner()
results = runner.run_assessment()

# Resource Operations
ec2_ops = EC2Operations()
s3_ops = S3Operations()
```

## Target Audience

- **CloudOps Engineers**: Multi-account AWS environment management
- **DevOps Teams**: Infrastructure automation and CI/CD integration
- **Site Reliability Engineers (SRE)**: Operational excellence and monitoring
- **Security Engineers**: Compliance assessment and remediation
- **FinOps Practitioners**: Cost optimization and resource governance
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

# Keep package version in sync with distribution metadata
try:
    __version__ = _pkg_version("runbooks")
except Exception:
    # Fallback if metadata is unavailable during editable installs
    __version__ = "0.9.0"

# Core module exports
from runbooks.config import RunbooksConfig, load_config, save_config
from runbooks.utils import ensure_directory, setup_logging, validate_aws_profile

# Enterprise module exports with graceful degradation
try:
    # Assessment and Discovery
    from runbooks.cfat.runner import AssessmentRunner
    from runbooks.inventory.collectors.aws_management import OrganizationsManager
    from runbooks.inventory.core.collector import InventoryCollector
    from runbooks.operate.cloudformation_operations import CloudFormationOperations
    from runbooks.operate.cloudwatch_operations import CloudWatchOperations
    from runbooks.operate.dynamodb_operations import DynamoDBOperations

    # Operations and Automation
    from runbooks.operate.ec2_operations import EC2Operations
    from runbooks.operate.iam_operations import IAMOperations
    from runbooks.operate.s3_operations import S3Operations
    from runbooks.security.security_baseline_tester import SecurityBaselineTester

    _enterprise_exports = [
        "AssessmentRunner",
        "InventoryCollector",
        "OrganizationsManager",
        "SecurityBaselineTester",
        "EC2Operations",
        "S3Operations",
        "DynamoDBOperations",
        "CloudFormationOperations",
        "IAMOperations",
        "CloudWatchOperations",
    ]
except ImportError as e:
    # Graceful degradation if enterprise dependencies aren't available
    _enterprise_exports = []

# FinOps exports
from runbooks.finops import get_cost_data, get_trend, run_dashboard

# Consolidated exports for enterprise CloudOps platform
__all__ = [
    # Core utilities
    "__version__",
    "setup_logging",
    "load_config",
    "save_config",
    "RunbooksConfig",
    "ensure_directory",
    "validate_aws_profile",
    # FinOps capabilities
    "run_dashboard",
    "get_cost_data",
    "get_trend",
] + _enterprise_exports

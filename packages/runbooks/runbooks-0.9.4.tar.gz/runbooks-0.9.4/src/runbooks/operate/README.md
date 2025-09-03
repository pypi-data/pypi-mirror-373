# AWS Resource Operations (CLI)

The AWS Resource Operations module is an enterprise-grade command-line tool for AWS resource lifecycle management. Built with the Rich library for beautiful terminal output, it provides safe, automated operations across EC2, S3, DynamoDB, and CloudFormation resources with comprehensive safety controls and professional reporting.

## 📈 *operate-runbooks*.md Enterprise Rollout

Following proven **99/100 manager score** success patterns established in FinOps:

### **Rollout Strategy**: Progressive *-runbooks*.md standardization 
- **Phase 2**: Operate rollout with *operate-runbooks*.md framework ✅
- **Phase 3**: Security rollout with *security-runbooks*.md standards (Next)
- **Phase 4**: VPC rollout with *vpc-runbooks*.md patterns (Planned)

## Why AWS Resource Operations?

Managing AWS resources safely across multiple accounts and environments requires enterprise-grade tooling with built-in safety controls. The AWS Resource Operations CLI aims to provide controlled, auditable resource management with comprehensive logging and rollback capabilities.

Key features include:
- **Unified Interface**: Consolidated resource operations from EC2 to CloudFormation
- **Safety First**: Default dry-run mode with explicit approval gates
- **Rich Console Output**: Beautiful terminal UI with progress indicators and status displays
- **Multi-Account Support**: Cross-account operations with role-based authentication
- **Comprehensive Logging**: Full audit trails and operation history

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [AWS CLI Profile Setup](#aws-cli-profile-setup)
- [Command Line Usage](#command-line-usage)
  - [Options](#command-line-options)
  - [Examples](#examples)
- [Resource Operations](#resource-operations)
  - [EC2 Instance Management](#ec2-instance-management)
  - [S3 Bucket Operations](#s3-bucket-operations)
  - [DynamoDB Management](#dynamodb-management)
  - [CloudFormation Operations](#cloudformation-operations)
- [Safety Controls](#safety-controls)
- [Export Formats](#export-formats)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **EC2 Instance Operations**: 
  - Start, stop, reboot instances with safety checks
  - Batch operations with progress tracking
  - Instance state validation and reporting
- **S3 Bucket Management**: 
  - Bucket lifecycle operations with confirmation prompts
  - Object-level operations with versioning support
  - Public access validation and remediation
- **DynamoDB Operations**: 
  - Table management with backup validation
  - Point-in-time recovery operations
  - Capacity scaling with safety limits
- **CloudFormation Management**: 
  - Stack deployments with rollback capabilities
  - Template validation and drift detection
  - Cross-account stack operations
- **Safety Controls**:
  - Default dry-run mode for all destructive operations
  - Explicit approval gates for production environments
  - Comprehensive audit logging with rollback capabilities
  - Multi-factor authentication support for critical operations
- **Profile Management**:
  - Automatic profile detection
  - Cross-account role assumption
  - AWS SSO integration
  - Multi-profile batch operations
- **Rich Terminal UI**: Styled with the Rich library for professional experience
- **Export Options**:
  - JSON export for automation integration
  - CSV export for reporting and analysis
  - HTML reports for stakeholder communication

---

## Prerequisites

- **Python 3.8 or later**: Ensure you have the required Python version installed
- **AWS CLI configured with named profiles**: Set up your AWS CLI profiles for seamless integration
- **AWS credentials with permissions**:
  - `ec2:*` (for EC2 operations)
  - `s3:*` (for S3 operations)  
  - `dynamodb:*` (for DynamoDB operations)
  - `cloudformation:*` (for CloudFormation operations)
  - `sts:AssumeRole` (for cross-account operations)
  - `sts:GetCallerIdentity` (for identity validation)

---

## Installation

There are several ways to install the AWS Resource Operations CLI:

### Option 1: Using uv (Fast Python Package Installer)
[uv](https://github.com/astral-sh/uv) is a modern Python package installer and resolver that's extremely fast.

```bash
# Install runbooks with resource operations
uv pip install runbooks
```

### Option 2: Using pip
```bash
# Install runbooks package
pip install runbooks
```

---

## AWS CLI Profile Setup

If you haven't already, configure your named profiles using the AWS CLI:

```bash
aws configure --profile production-ops
aws configure --profile development-ops
aws configure --profile staging-ops
# ... etc ...
```

For multi-account operations, ensure you have appropriate cross-account roles configured.

---

## Command Line Usage

Run resource operations using `runbooks operate` followed by options:

```bash
runbooks operate [resource-type] [operation] [options]
```

### Command Line Options

| Flag | Description |
|---|---|
| `--profile`, `-p` | AWS profile to use for operations |
| `--region`, `-r` | AWS region to target (default: us-east-1) |
| `--dry-run` | Execute in dry-run mode (default: enabled) |
| `--force` | Disable dry-run mode for actual execution |
| `--batch-size` | Number of resources to process in parallel |
| `--timeout` | Operation timeout in seconds |
| `--output-format` | Output format: table, json, csv |
| `--log-level` | Logging level: INFO, DEBUG, WARNING, ERROR |

### Examples

```bash
# EC2 Instance Operations
runbooks operate ec2 start --instance-ids i-1234567890abcdef0 --profile production
runbooks operate ec2 stop --instance-ids i-1234567890abcdef0 --dry-run
runbooks operate ec2 reboot --instance-ids i-1234567890abcdef0 --force

# S3 Bucket Operations  
runbooks operate s3 create --bucket-name my-new-bucket --profile development
runbooks operate s3 delete --bucket-name old-bucket --force --profile development

# DynamoDB Operations
runbooks operate dynamodb backup --table-name users --profile production
runbooks operate dynamodb restore --table-name users --backup-arn arn:aws:dynamodb:... --profile production

# CloudFormation Operations
runbooks operate cloudformation deploy --stack-name web-app --template-file template.yaml --profile production
runbooks operate cloudformation delete --stack-name old-stack --force --profile development
```

---

## Resource Operations

### EC2 Instance Management

**Start Instances**:
```bash
# Start single instance
runbooks operate ec2 start --instance-ids i-1234567890abcdef0 --profile production

# Start multiple instances
runbooks operate ec2 start --instance-ids i-123,i-456,i-789 --profile production --batch-size 3

# Dry-run mode (default)
runbooks operate ec2 start --instance-ids i-1234567890abcdef0 --dry-run
```

**Stop Instances**:
```bash
# Stop single instance with confirmation
runbooks operate ec2 stop --instance-ids i-1234567890abcdef0 --profile production

# Force stop without confirmation
runbooks operate ec2 stop --instance-ids i-1234567890abcdef0 --force --profile production
```

**Instance Status Monitoring**:
```bash
# Monitor instance status changes
runbooks operate ec2 status --instance-ids i-1234567890abcdef0 --profile production --watch
```

### S3 Bucket Operations

**Create Bucket**:
```bash
# Create bucket with versioning
runbooks operate s3 create --bucket-name my-app-storage --enable-versioning --profile production

# Create bucket with encryption
runbooks operate s3 create --bucket-name secure-storage --enable-encryption --kms-key-id arn:aws:kms:... --profile production
```

**Delete Bucket**:
```bash
# Delete empty bucket
runbooks operate s3 delete --bucket-name old-bucket --profile development --dry-run

# Force delete bucket with contents (dangerous)
runbooks operate s3 delete --bucket-name old-bucket --delete-contents --force --profile development
```

### DynamoDB Management

**Backup Operations**:
```bash
# Create on-demand backup
runbooks operate dynamodb backup --table-name users --backup-name users-backup-$(date +%Y%m%d) --profile production

# List available backups
runbooks operate dynamodb list-backups --table-name users --profile production
```

**Restore Operations**:
```bash
# Restore from backup
runbooks operate dynamodb restore --source-backup-arn arn:aws:dynamodb:... --target-table-name users-restored --profile production
```

### CloudFormation Operations

**Deploy Stack**:
```bash
# Deploy new stack
runbooks operate cloudformation deploy --stack-name web-app --template-file infrastructure.yaml --profile production

# Deploy with parameters
runbooks operate cloudformation deploy --stack-name web-app --template-file infrastructure.yaml --parameters EnvironmentName=prod --profile production

# Deploy with changeset preview
runbooks operate cloudformation deploy --stack-name web-app --template-file infrastructure.yaml --create-changeset --profile production
```

**Delete Stack**:
```bash
# Delete stack with confirmation
runbooks operate cloudformation delete --stack-name old-stack --profile development

# Force delete with retain policy
runbooks operate cloudformation delete --stack-name old-stack --retain-resources --force --profile development
```

---

## Safety Controls

### Default Dry-Run Mode
All destructive operations default to dry-run mode:

```bash
# This will NOT actually delete the bucket (dry-run default)
runbooks operate s3 delete --bucket-name test-bucket --profile development

# This will actually delete the bucket (force required)
runbooks operate s3 delete --bucket-name test-bucket --force --profile development
```

### Approval Gates
Critical operations require explicit confirmation:

```bash
# Production operations require approval
runbooks operate ec2 stop --instance-ids i-prod-server --profile production
> WARNING: This will stop production instance i-prod-server
> Type 'YES' to confirm: YES
```

### Audit Logging
All operations are logged for compliance:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "operation": "ec2:stop",
  "resource": "i-1234567890abcdef0",
  "profile": "production",
  "user": "john.doe@company.com",
  "status": "success",
  "dry_run": false
}
```

---

## Export Formats

### JSON Output Format

```bash
runbooks operate ec2 status --instance-ids i-123 --output-format json --profile production
```

```json
{
  "operation": "ec2:status",
  "timestamp": "2024-01-15T10:30:00Z",
  "resources": [
    {
      "instance_id": "i-1234567890abcdef0",
      "state": "running",
      "instance_type": "t3.medium",
      "availability_zone": "us-east-1a"
    }
  ]
}
```

### CSV Output Format

```bash
runbooks operate ec2 list --output-format csv --profile production > instances.csv
```

### HTML Report Format

```bash
runbooks operate cloudformation status --stack-name web-app --output-format html --profile production > stack_report.html
```

---

## 💰 Operations Cost Awareness

### Cost-Conscious Operations
The operations module includes cost awareness features:

- **Instance Type Recommendations**: Suggests cost-optimal instance types during resize operations
- **Resource Cleanup**: Identifies unused resources during inventory operations
- **Cost Impact Warnings**: Shows estimated cost impact before starting expensive operations

### Cost Monitoring Integration
```bash
# Operations with cost monitoring
runbooks operate ec2 start --instance-ids i-123 --show-cost-impact --profile production
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](../../../CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/1xOps/CloudOps-Runbooks.git
cd CloudOps-Runbooks
uv sync --all-extras
uv run python -m runbooks operate --help
```

### Running Tests
```bash
uv run pytest tests/operate/ -v
```

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../../../LICENSE) file for details.

---

## Enterprise Support

For enterprise support, professional services, and custom integrations:
- **Email**: [info@oceansoft.io](mailto:info@oceansoft.io)
- **GitHub**: [CloudOps Runbooks Issues](https://github.com/1xOps/CloudOps-Runbooks/issues)
- **Documentation**: [Enterprise Documentation](https://docs.cloudops-runbooks.io)

Let's build reliable, safe AWS operations together. 🚀
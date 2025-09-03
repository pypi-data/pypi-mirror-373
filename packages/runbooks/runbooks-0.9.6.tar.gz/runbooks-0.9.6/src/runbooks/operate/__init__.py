"""
Enterprise AWS Operations Module - Production-Ready Infrastructure Automation

## Overview

The `runbooks.operate` module provides enterprise-grade AWS operational capabilities
designed for CloudOps, DevOps, and SRE teams managing large-scale, multi-account
AWS environments. This module transforms infrastructure operations from manual,
error-prone tasks into automated, auditable, and repeatable workflows.

## Design Philosophy

**KISS Architecture**: Simple, maintainable operations without legacy complexity
**Enterprise Ready**: Multi-deployment support (CLI, Lambda, Docker, Kubernetes)
**Safety First**: Comprehensive dry-run, validation, and confirmation workflows
**AI-Agent Optimized**: Predictable patterns for automation integration

## Core Capabilities

### 🖥️ **Compute Operations (EC2)**
- **Instance Lifecycle**: Start, stop, reboot, terminate with safety validations
- **Image Management**: AMI creation, cross-region copying with encryption
- **Volume Operations**: Cleanup unused EBS volumes, snapshot management
- **Network Resources**: Elastic IP cleanup and management
- **Advanced Features**: Block device mappings, monitoring, SNS notifications

### 🗄️ **Storage Operations (S3)**
- **Bucket Lifecycle**: Creation with region-specific constraints and validation
- **Object Operations**: Upload, download, delete with ACL management
- **Data Migration**: Cross-bucket synchronization with filtering
- **Compliance**: Public access block configuration and enforcement
- **Advanced Features**: Pagination, prefix filtering, size optimization

### 🗃️ **Database Operations (DynamoDB)**
- **Table Management**: Creation, deletion with billing mode optimization
- **Data Operations**: CRUD operations with batch processing
- **Backup & Recovery**: Point-in-time recovery and backup automation
- **Performance**: Throughput scaling and optimization
- **Advanced Features**: Resource-based operations, environment configuration

### 🏗️ **Infrastructure Operations**
- **CloudFormation**: Stack and StackSet operations with drift detection
- **IAM**: Cross-account role management and policy automation
- **CloudWatch**: Log retention and monitoring configuration
- **Tagging**: Cross-service resource tagging for governance

## Enterprise Features

### 🔒 **Safety & Security**
```python
# Dry-run mode for all operations
ec2_ops = EC2Operations(dry_run=True)
results = ec2_ops.terminate_instances(instance_ids)

# Confirmation prompts for destructive operations
s3_ops = S3Operations()
s3_ops.delete_bucket_and_objects("critical-bucket")  # Requires confirmation
```

### 🌍 **Multi-Deployment Support**
```bash
# CLI execution
runbooks operate ec2 start --instance-ids i-123 --dry-run

# Environment variables for containers
export AWS_REGION=us-west-2
export DRY_RUN=true
python -m runbooks.operate.ec2_operations start

# Lambda handlers for serverless
from runbooks.operate.ec2_operations import lambda_handler_terminate_instances
```

### 📊 **Monitoring & Notifications**
```python
# SNS integration for operational awareness
ec2_ops = EC2Operations(sns_topic_arn="arn:aws:sns:us-east-1:123:alerts")
results = ec2_ops.cleanup_unused_volumes()  # Sends cleanup summary
```

### 🎯 **Advanced Configuration**
```python
# Environment-driven configuration
ec2_ops = EC2Operations()  # Reads AWS_PROFILE, AWS_REGION, DRY_RUN
s3_ops = S3Operations()    # Reads S3_BUCKET, S3_KEY, LOCAL_FILE_PATH
db_ops = DynamoDBOperations()  # Reads TABLE_NAME, MAX_BATCH_ITEMS
```

## Production Examples

### Multi-Account EC2 Management
```python
from runbooks.operate import EC2Operations
from runbooks.inventory.models.account import AWSAccount

# Production environment instance restart
ec2_ops = EC2Operations(profile="production", region="us-east-1")
context = OperationContext(
    account=AWSAccount("123456789012", "production"),
    region="us-east-1",
    dry_run=False
)

# Restart instances with monitoring
results = ec2_ops.restart_instances(
    context,
    instance_ids=["i-prod123", "i-prod456"],
    enable_monitoring=True
)
```

### S3 Data Migration
```python
from runbooks.operate import S3Operations

# Cross-region bucket synchronization
s3_ops = S3Operations(profile="data-migration")
results = s3_ops.sync_objects(
    context,
    source_bucket="prod-data-us-east-1",
    destination_bucket="prod-data-us-west-2",
    delete_removed=True
)
```

### DynamoDB Batch Processing
```python
from runbooks.operate import DynamoDBOperations

# High-volume data loading
db_ops = DynamoDBOperations(table_name="user-events")
results = db_ops.batch_write_items_enhanced(
    context,
    batch_size=500  # Optimized for high throughput
)
```

## CLI Integration

All operations integrate seamlessly with the standardized CLI:

```bash
# Resource Operations with Safety
runbooks operate ec2 terminate --instance-ids i-123 --confirm --region us-west-2
runbooks operate s3 create-bucket --bucket-name analytics-2024 --region eu-west-1
runbooks operate dynamodb create-table --table-name events --billing-mode PAY_PER_REQUEST

# Cleanup Operations
runbooks operate ec2 cleanup-unused-volumes --region us-east-1 --force
runbooks operate ec2 cleanup-unused-eips --profile production

# Advanced Operations
runbooks operate cloudformation move-stack-instances --source-stackset networking
runbooks operate iam update-roles-cross-accounts --role-name deployment-role
```

## Documentation & Support

- **Documentation**: https://cloudops.oceansoft.io/cloud-foundation/cfat-assessment-tool.html
- **Architecture**: KISS principle - no legacy complexity
- **Testing**: Comprehensive mocking and integration test coverage
- **Monitoring**: Built-in operational telemetry and alerting

## Target Users

- **CloudOps Engineers**: Multi-account infrastructure lifecycle management
- **DevOps Teams**: CI/CD pipeline integration and infrastructure automation
- **SRE Teams**: Operational excellence and incident response automation
- **Platform Teams**: Self-service infrastructure capabilities
- **Security Teams**: Compliance automation and policy enforcement

Version: 0.7.8 - Enterprise Production Ready
Compatibility: AWS SDK v3, Python 3.8+, Multi-deployment ready
"""

from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus
from runbooks.operate.cloudformation_operations import CloudFormationOperations
from runbooks.operate.cloudwatch_operations import CloudWatchOperations
from runbooks.operate.dynamodb_operations import DynamoDBOperations
from runbooks.operate.ec2_operations import EC2Operations
from runbooks.operate.iam_operations import IAMOperations
from runbooks.operate.s3_operations import S3Operations
from runbooks.operate.tagging_operations import TaggingOperations

# Import centralized version from main runbooks package
from runbooks import __version__

# Version info
__author__ = "CloudOps Runbooks Team"

# Public API exports
__all__ = [
    # Core functionality
    "BaseOperation",
    "OperationContext",
    "OperationResult",
    "OperationStatus",
    # Service operations
    "EC2Operations",
    "S3Operations",
    "DynamoDBOperations",
    "TaggingOperations",
    "CloudFormationOperations",
    "IAMOperations",
    "CloudWatchOperations",
    # Module metadata
    "__version__",
    "__author__",
]

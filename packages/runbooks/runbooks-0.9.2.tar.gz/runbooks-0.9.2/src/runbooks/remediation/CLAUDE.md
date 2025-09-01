# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based security remediation tool for resolving Dome9 (now Check Point CloudGuard) compliance issues across AWS accounts. The tool provides both individual command execution and bulk operations across multiple AWS accounts.

## Development Setup

### Prerequisites
- Conda environment
- AWS credentials configured (either via credentials file or AWS SSO)

### Installation
```bash
pip install -r requirements.txt
```

## Commands and Usage

### Individual Command Execution
Use the CLI interface for single-account operations:
```bash
python src/cli.py s3 list
python src/cli.py s3 block_public_access
python src/cli.py api_gateway list
python src/cli.py lambda list
python src/cli.py cognito list_active_users
```

### Bulk Operations Across Multiple Accounts
Use `bulk_run.py` for multi-account operations:
```bash
python src/bulk_run.py --function enable_public_access_block_on_all_buckets --credentials-path ../credentials
python src/bulk_run.py --function list_lambda_functions --credentials-path ../credentials
python src/bulk_run.py --function kms_operations_enable_key_rotation --credentials-path ../credentials
python src/bulk_run.py --function find_object_in_s3 --kwargs 'object_to_find:my-object' --credentials-path ../credentials
```

### Testing
Run unit tests using:
```bash
python -m unittest Tests.update_policy
```

## Architecture

### Core Components

**CLI Interface (`src/cli.py`)**
- Main entry point for single-account operations
- Uses Click framework for command grouping
- Groups commands by AWS service (s3, api_gateway, lambda, cognito)

**Bulk Operations (`src/bulk_run.py`)**
- Handles multi-account remediation across AWS organizations
- Supports both file-based credentials and AWS SSO authentication
- Contains a registry of all available functions for bulk execution
- Implements comprehensive logging to both console and files

**AWS Commons (`src/aws/commons.py`)**
- Central utilities for AWS client/resource creation
- AWS SSO authentication flow with browser-based device authorization
- Credentials management for both static files and SSO tokens
- Common helper functions for AWS API operations (pricing, CloudWatch metrics, etc.)
- Caching decorators for performance optimization

### AWS Service Modules Structure
All AWS-specific functionality is organized under `src/aws/` with individual modules for each service and operation:

- **S3 Operations**: Bucket management, public access blocking, encryption, SSL policies
- **EC2 Operations**: Security group management, EBS volume cleanup, public IP management
- **IAM/Security**: KMS key rotation, certificate management
- **Serverless**: Lambda function management, API Gateway operations
- **Data Services**: DynamoDB encryption and optimization, RDS management
- **Monitoring**: CloudTrail modifications, CloudWatch integration
- **Identity**: Cognito user management and operations

### Authentication Patterns

The tool supports two authentication methods:

1. **File-based Credentials**: Traditional AWS credentials file with access keys
2. **AWS SSO**: Modern SSO flow with device authorization and browser-based authentication

The commons module automatically handles credential refresh and multi-account iteration, making it transparent to individual remediation functions.

### Logging and Output

- Dual logging to console and file (configurable via `DOME9_REMEDIATION_FILE_LOG` environment variable)
- CSV output generation for analysis and reporting
- CloudWatch metrics integration for cost and usage analysis

## Environment Variables

- `ACCESS_PORTAL_URL`: AWS SSO start URL (default: "https://d-976752e8d5.awsapps.com/start")
- `DOME9_REMEDIATION_FILE_LOG`: Custom log file path
- `AWS_REGION`: Default AWS region for operations
- Standard AWS environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`)
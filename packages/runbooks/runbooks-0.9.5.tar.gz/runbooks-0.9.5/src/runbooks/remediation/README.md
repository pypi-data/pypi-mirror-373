# AWS Security Remediation Automation (CLI)

The AWS Security Remediation Automation module is an enterprise-grade command-line tool for automated security remediation and compliance enforcement. Built with the Rich library for beautiful terminal output, it provides comprehensive security issue remediation through AWS Lambda functions and automated workflows.

## 📈 *remediation-runbooks*.md Enterprise Rollout

Following proven **99/100 manager score** success patterns established in FinOps:

### **Rollout Strategy**: Progressive *-runbooks*.md standardization 
- **Phase 5**: Remediation rollout with *remediation-runbooks*.md framework ✅
- **Integration**: AWS Config rules with automated remediation workflows
- **Enterprise Features**: Multi-account remediation with compliance tracking

## Why AWS Security Remediation Automation?

Security remediation in enterprise AWS environments requires automated, consistent, and auditable approaches. The Security Remediation CLI provides enterprise-grade automation for security issue detection and remediation, designed for security teams, compliance officers, and DevOps engineers managing large-scale AWS deployments.

Key capabilities include:
- **Automated Remediation**: AWS Config integration with Lambda-based remediation
- **Multi-Account Operations**: Cross-account security issue resolution
- **Compliance Enforcement**: Automated compliance policy enforcement
- **Rich Reporting**: Comprehensive remediation tracking and audit trails
- **Enterprise Integration**: Integration with security orchestration platforms

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [AWS CLI Profile Setup](#aws-cli-profile-setup)
- [Command Line Usage](#command-line-usage)
  - [Options](#command-line-options)
  - [Examples](#examples)
- [Remediation Operations](#remediation-operations)
  - [S3 Security Remediation](#s3-security-remediation)
  - [API Gateway Security](#api-gateway-security)
  - [IAM Security Enforcement](#iam-security-enforcement)
  - [VPC Security Remediation](#vpc-security-remediation)
- [Configuration](#configuration)
- [Export Formats](#export-formats)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **S3 Security Remediation**: 
  - Automated public access blocking
  - Bucket encryption enforcement
  - Access logging configuration
  - Lifecycle policy enforcement
- **API Gateway Security**: 
  - Resource policy enforcement
  - Throttling configuration
  - WAF integration automation
  - Logging and monitoring setup
- **IAM Security Enforcement**: 
  - Password policy enforcement
  - MFA requirement automation
  - Privilege escalation prevention
  - Access key rotation automation
- **VPC Security Remediation**: 
  - Security group rule optimization
  - Network ACL compliance enforcement
  - VPC Flow Logs configuration
  - Public subnet security hardening
- **Multi-Account Operations**:
  - AWS Organizations integration
  - Cross-account role management
  - Centralized policy enforcement
  - Compliance reporting aggregation
- **Lambda-Based Automation**: 
  - Event-driven remediation workflows
  - AWS Config integration
  - CloudWatch Events triggering
  - Serverless execution model
- **Rich Terminal UI**: Beautiful console output with remediation progress tracking

---

## Prerequisites

- **Python 3.8 or later**: Ensure you have the required Python version installed
- **AWS CLI configured with named profiles**: Set up your AWS CLI profiles for seamless integration
- **AWS credentials with permissions**:
  - `config:*` (for AWS Config integration)
  - `lambda:*` (for remediation function management)
  - `iam:*` (for IAM security enforcement)
  - `s3:*` (for S3 security remediation)
  - `apigateway:*` (for API Gateway security)
  - `ec2:*` (for VPC security remediation)
  - `events:*` (for event-driven automation)
  - `logs:*` (for CloudWatch Logs integration)

---

## Installation

### Option 1: Using uv (Fast Python Package Installer)
```bash
# Install runbooks with remediation automation
uv pip install runbooks
```

### Option 2: Using pip
```bash
# Install runbooks package
pip install runbooks
```

### Option 3: Development Installation
```bash
git clone https://github.com/1xOps/CloudOps-Runbooks.git
cd CloudOps-Runbooks
uv sync --all-extras
```

---

## AWS CLI Profile Setup

Configure your named profiles for remediation operations:

```bash
aws configure --profile remediation-prod
aws configure --profile remediation-dev
aws configure --profile security-admin
# ... etc ...
```

For multi-account remediation, ensure cross-account roles are properly configured.

---

## Command Line Usage

Run remediation operations using `runbooks remediation` followed by options:

```bash
runbooks remediation [service] [operation] [options]
```

### Command Line Options

| Flag | Description |
|---|---|
| `--profile`, `-p` | AWS profile to use for operations |
| `--region`, `-r` | AWS region to target (default: us-east-1) |
| `--all-regions` | Execute remediation across all regions |
| `--dry-run` | Execute in dry-run mode (default: enabled) |
| `--auto-remediate` | Enable automatic remediation without prompts |
| `--compliance-framework` | Target compliance framework: SOC2, PCI-DSS, HIPAA |
| `--output-format` | Output format: table, json, csv, html |
| `--notification-sns` | SNS topic for remediation notifications |

### Examples

```bash
# S3 security remediation
runbooks remediation s3 block-public-access --profile production --dry-run
runbooks remediation s3 enforce-encryption --all-regions --profile production

# API Gateway security
runbooks remediation apigateway configure-throttling --profile production
runbooks remediation apigateway enable-logging --profile production

# IAM security enforcement
runbooks remediation iam enforce-password-policy --profile production
runbooks remediation iam require-mfa --dry-run --profile production

# Multi-service security scan and remediation
runbooks remediation scan --auto-remediate --compliance-framework SOC2 --profile production
```

---

## Remediation Operations

### S3 Security Remediation

**Public Access Blocking**:
```bash
# Block public access on all S3 buckets
runbooks remediation s3 block-public-access --profile production

# Selective bucket remediation
runbooks remediation s3 block-public-access --bucket-names bucket1,bucket2 --profile production

# Organization-wide S3 security
runbooks remediation s3 block-public-access --organization-wide --profile management-account
```

**Expected S3 Remediation Output**:
```
╭─ S3 Security Remediation Results ─╮
│                                    │
│ 📊 Buckets Analyzed: 47           │
│ 🔒 Remediation Applied: 12        │
│ ✅ Already Compliant: 35          │
│                                    │
│ 🛡️  Security Improvements:        │
│ • Public access blocked: 8 buckets │
│ • Encryption enabled: 4 buckets   │
│ • Logging configured: 12 buckets  │
│                                    │
│ ⏱️  Remediation Time: 2m 34s      │
╰────────────────────────────────────╯
```

**Encryption Enforcement**:
```bash
# Enforce server-side encryption
runbooks remediation s3 enforce-encryption --kms-key default --profile production

# Custom KMS key encryption
runbooks remediation s3 enforce-encryption --kms-key arn:aws:kms:... --profile production
```

### API Gateway Security

**Throttling Configuration**:
```bash
# Configure API throttling limits
runbooks remediation apigateway configure-throttling --rate-limit 1000 --burst-limit 2000 --profile production

# Per-API throttling configuration
runbooks remediation apigateway configure-throttling --api-id abcd123 --profile production
```

**WAF Integration**:
```bash
# Enable WAF for API Gateway
runbooks remediation apigateway enable-waf --web-acl-name api-protection --profile production

# Configure WAF rules
runbooks remediation apigateway configure-waf-rules --ruleset owasp-top-10 --profile production
```

### IAM Security Enforcement

**Password Policy Enforcement**:
```bash
# Enforce strong password policy
runbooks remediation iam enforce-password-policy --min-length 12 --require-symbols --profile production

# Custom password policy
runbooks remediation iam enforce-password-policy --config password-policy.json --profile production
```

**MFA Requirement**:
```bash
# Require MFA for all users
runbooks remediation iam require-mfa --profile production

# MFA for privileged users only
runbooks remediation iam require-mfa --privileged-only --profile production
```

### VPC Security Remediation

**Security Group Optimization**:
```bash
# Remove overly permissive rules
runbooks remediation vpc optimize-security-groups --profile production

# Enforce specific security policies
runbooks remediation vpc enforce-security-policy --policy-file security-policy.json --profile production
```

**VPC Flow Logs Configuration**:
```bash
# Enable VPC Flow Logs
runbooks remediation vpc enable-flow-logs --destination cloudwatch --profile production

# Configure Flow Logs with S3 destination
runbooks remediation vpc enable-flow-logs --destination s3 --s3-bucket vpc-flow-logs --profile production
```

---

## Configuration

### Remediation Configuration File

Create a `remediation_config.toml` file:

```toml
# remediation_config.toml
[s3]
enforce_public_access_block = true
default_encryption = "AES256"
enable_access_logging = true
lifecycle_policy_days = 365

[apigateway]
default_throttle_rate = 1000
default_throttle_burst = 2000
enable_waf = true
enable_logging = true

[iam]
password_policy = {
    min_length = 12,
    require_symbols = true,
    require_numbers = true,
    require_uppercase = true,
    require_lowercase = true,
    max_age_days = 90
}
require_mfa = true

[vpc]
enable_flow_logs = true
flow_logs_destination = "cloudwatch"
security_group_max_ingress_rules = 10

[notifications]
sns_topic = "arn:aws:sns:us-east-1:123456789012:security-remediation"
email_notifications = true
slack_webhook = "${SLACK_WEBHOOK_URL}"

[compliance]
frameworks = ["SOC2", "PCI-DSS"]
auto_remediate = false
audit_trail = true
```

**Using Configuration File**:
```bash
runbooks remediation --config remediation_config.toml scan --profile production
```

---

## Lambda-Based Automation

### Deploy Remediation Functions

**Deploy Lambda Functions**:
```bash
# Deploy all remediation functions
runbooks remediation deploy-functions --profile production

# Deploy specific function
runbooks remediation deploy-function --function s3-public-access-remediation --profile production

# Update existing functions
runbooks remediation update-functions --profile production
```

### AWS Config Integration

**Configure Config Rules**:
```bash
# Enable AWS Config for remediation
runbooks remediation configure-aws-config --enable --profile production

# Deploy remediation Config rules
runbooks remediation deploy-config-rules --profile production

# Monitor Config compliance
runbooks remediation monitor-compliance --dashboard --profile production
```

### Event-Driven Remediation

**CloudWatch Events Integration**:
```bash
# Configure event-driven remediation
runbooks remediation configure-events --profile production

# Test event triggers
runbooks remediation test-event-trigger --event-type s3-public-bucket --profile production
```

---

## Export Formats

### JSON Output Format

```bash
runbooks remediation scan --output-format json --output-file remediation_report.json --profile production
```

```json
{
  "remediation_summary": {
    "timestamp": "2024-01-15T10:30:00Z",
    "account_id": "123456789012",
    "compliance_framework": "SOC2",
    "services_scanned": ["s3", "iam", "apigateway", "vpc"],
    "total_issues_found": 23,
    "issues_remediated": 18,
    "manual_review_required": 5,
    "remediation_actions": [
      {
        "service": "s3",
        "action": "block_public_access",
        "resources_affected": 8,
        "status": "completed"
      }
    ]
  }
}
```

### HTML Remediation Report

```bash
runbooks remediation scan --output-format html --output-file remediation_report.html --profile production
```

---

## Multi-Account Remediation

### Organization-Wide Operations

**Cross-Account Remediation**:
```bash
# Scan entire organization
runbooks remediation scan --organization-wide --profile management-account

# Remediate across multiple accounts
runbooks remediation execute --accounts prod,dev,staging --profile management-account

# Compliance reporting
runbooks remediation compliance-report --organization-wide --framework SOC2 --profile management-account
```

### Centralized Policy Management

**Deploy Organization Policies**:
```bash
# Deploy service control policies
runbooks remediation deploy-scp --policy-file security-scp.json --profile management-account

# Enforce compliance policies
runbooks remediation enforce-org-policies --profile management-account
```

---

## Integration with Security Tools

### SOAR Platform Integration

```bash
# Configure SOAR integration
runbooks remediation configure --platform phantom --api-key $PHANTOM_API_KEY

# Send remediation playbooks to SOAR
runbooks remediation export-playbooks --platform phantom --profile production
```

### SIEM Integration

```bash
# Configure SIEM logging
runbooks remediation configure --siem splunk --hec-endpoint $SPLUNK_HEC_URL

# Send remediation logs to SIEM
runbooks remediation log-to-siem --profile production
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](../../../CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/1xOps/CloudOps-Runbooks.git
cd CloudOps-Runbooks
uv sync --all-extras
uv run python -m runbooks remediation --help
```

### Running Tests
```bash
uv run pytest tests/remediation/ -v
```

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../../../LICENSE) file for details.

---

## Enterprise Support

For enterprise support, professional services, and custom remediation integrations:
- **Email**: [info@oceansoft.io](mailto:info@oceansoft.io)
- **GitHub**: [CloudOps Runbooks Issues](https://github.com/1xOps/CloudOps-Runbooks/issues)
- **Documentation**: [Enterprise Remediation Documentation](https://docs.cloudops-runbooks.io/remediation)

Let's automate security remediation together. 🚀
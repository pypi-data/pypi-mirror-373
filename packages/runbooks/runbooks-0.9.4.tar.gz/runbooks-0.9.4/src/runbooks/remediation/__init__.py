"""
Enterprise AWS Remediation Module - Automated Security & Compliance Fixes

The `runbooks.remediation` module provides enterprise-grade automated remediation
capabilities for AWS security and compliance findings, completing the CloudOps
automation lifecycle by bridging assessment findings to automated fixes.

## CloudOps Automation Lifecycle

1. **🔍 DISCOVER** (`runbooks.inventory`) - Multi-account resource discovery
2. **📊 ASSESS** (`runbooks.security`, `runbooks.cfat`) - Security posture evaluation
3. **🔧 REMEDIATE** (`runbooks.remediation`) - **Automated fix implementation**
4. **⚙️ OPERATE** (`runbooks.operate`) - Ongoing resource lifecycle management

## Core Capabilities

### 🗄️ S3 Security & Compliance (9 Operations)
- Public Access Control, Encryption Enforcement, Access Logging
- Policy Enforcement, Configuration Auditing

### 🖥️ EC2 & Networking Security (4 Operations)
- Security Group Hardening, Network Security, Resource Cleanup
- Compliance Automation

### 🔐 Encryption & Key Management (2 Operations)
- KMS Key Rotation, Database Encryption, Cross-Service Encryption

### 🗃️ Database & Storage Security (4 Operations)
- RDS Security, DynamoDB Optimization, Snapshot Management
- Storage Compliance

### ☁️ Serverless & API Security (4 Operations)
- Lambda Security, API Gateway Hardening, Cognito Management
- Serverless Compliance

### 🏅 Certificate & Identity Management (6 Operations)
- ACM Certificate Lifecycle Management, Cognito User Security
- SSL/TLS Certificate Cleanup, User Authentication Controls

### 📋 Audit & Monitoring (5 Operations)
- CloudTrail Policy Analysis & Reversion, Resource Scanning
- Workspace Management, Cross-Service Utilities

Version: 0.7.8 - Enterprise Production Ready
Compatibility: AWS SDK v3, Python 3.8+, Multi-deployment ready
"""

from runbooks.remediation.acm_remediation import ACMRemediation
from runbooks.remediation.base import (
    BaseRemediation,
    ComplianceMapping,
    RemediationContext,
    RemediationResult,
    RemediationStatus,
)
from runbooks.remediation.cloudtrail_remediation import CloudTrailRemediation
from runbooks.remediation.cognito_remediation import CognitoRemediation
from runbooks.remediation.dynamodb_remediation import DynamoDBRemediation
from runbooks.remediation.ec2_remediation import EC2SecurityRemediation
from runbooks.remediation.kms_remediation import KMSSecurityRemediation
from runbooks.remediation.lambda_remediation import LambdaSecurityRemediation
from runbooks.remediation.multi_account import MultiAccountRemediator
from runbooks.remediation.rds_remediation import RDSSecurityRemediation

# Import remediation operations
from runbooks.remediation.s3_remediation import S3SecurityRemediation

# Import centralized version from main runbooks package
from runbooks import __version__

# Version info
__author__ = "CloudOps Runbooks Team"

# Public API exports
__all__ = [
    # Core architecture
    "BaseRemediation",
    "RemediationContext",
    "RemediationResult",
    "RemediationStatus",
    "ComplianceMapping",
    # Service-specific remediation
    "S3SecurityRemediation",
    "EC2SecurityRemediation",
    "KMSSecurityRemediation",
    "DynamoDBRemediation",
    "RDSSecurityRemediation",
    "LambdaSecurityRemediation",
    "ACMRemediation",
    "CognitoRemediation",
    "CloudTrailRemediation",
    # Enterprise features
    "MultiAccountRemediator",
    # Module metadata
    "__version__",
    "__author__",
]

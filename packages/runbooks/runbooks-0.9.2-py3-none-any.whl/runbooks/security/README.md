# AWS Security Baseline Assessment (CLI)

The AWS Security Baseline Assessment module is an enterprise-grade command-line tool for comprehensive AWS security evaluation. Built with the Rich library for beautiful terminal output, it provides automated security assessment with multilingual reporting, parallel execution, and actionable remediation guidance.

## 📈 *security-runbooks*.md Enterprise Rollout

Following proven **99/100 manager score** success patterns established in FinOps:

### **Rollout Strategy**: Progressive *-runbooks*.md standardization 
- **Phase 4**: Security rollout with *security-runbooks*.md standards ✅
- **Integration**: 15+ critical security checks with enterprise compliance
- **Multi-Language**: Professional reports in EN, JP, KR, VN

## 📖 Overview

The **CloudOps Runbooks: Security Baseline Assessment** is a comprehensive tool designed to evaluate the security of AWS environments in accordance with basic security advisories. It provides a structured way to assess your account and workload configurations against **AWS security best practices** and the **AWS Startup Security Baseline (SSB)**. 

**Fully integrated with the CloudOps Runbooks CLI**, this tool offers enterprise-grade security assessment capabilities with multilingual reporting, parallel execution, and comprehensive remediation guidance. The tool is designed for DevOps teams, SRE engineers, and security professionals who need automated, actionable security insights.

By automating **15+ critical AWS account security and workload security checks**, this solution empowers startups, enterprises, and DevOps teams to validate their cloud security posture, generate actionable reports, and align with AWS Well-Architected principles.

Key capabilities include:
- **Enterprise CLI Integration**: Seamlessly integrated with `runbooks security` commands
- **Multilingual Reports**: Generate reports in English, Japanese, Korean, and Vietnamese
- **Parallel Execution**: Fast assessment with configurable worker pools
- **Rich Console Output**: Beautiful terminal output with progress indicators
- **Multiple Output Formats**: HTML reports with actionable remediation steps

In the **Test Report**, we provide numerous techniques for successfully responding to security threats on AWS with minimal resources. This script is appropriate for usage by early-stage businesses that cannot afford to invest much in security. 


## ✨ Features: Core Capabilities

1. **🚀 Enterprise CLI Integration**:
   - Seamlessly integrated with `runbooks security` commands for professional workflows
   - Rich console output with progress indicators and beautiful terminal formatting
   - Unified CLI interface with other CloudOps tools (CFAT, inventory, organizations)

2. **🌍 Multilingual Reporting**:
   - Generate reports in **4 languages**: English, Korean, Japanese, Vietnamese
   - Localized error messages and remediation guidance
   - Cultural context for international DevOps teams

3. **⚡ Performance & Scalability**:
   - Parallel execution with configurable worker pools for faster assessments
   - Modern dependency management with UV (Rust-based package manager)
   - Optimized AWS API calls to minimize execution time

4. **📊 Comprehensive Security Coverage**:
   - **15+ critical security checks** covering account, IAM, infrastructure, and operational security
   - Validates IAM configurations, S3 bucket policies, VPC security groups, and CloudTrail settings
   - Aligned with AWS Security Best Practices and Well-Architected Framework

5. **🔧 Multiple Output Formats**:
   - **HTML reports** with interactive elements and remediation links
   - **JSON output** for programmatic processing and CI/CD integration
   - **Console output** for immediate feedback and debugging

6. **🛡️ Enterprise Security Features**:
   - Support for multiple AWS authentication methods (IAM roles, SSO, CloudShell)
   - Read-only permissions ensuring compliance with **least privilege principle**
   - Audit trail and logging for compliance requirements

7. **🔄 CI/CD Integration Ready**:
   - Designed for automated security scanning in pipelines
   - JSON output format for integration with security dashboards
   - Exit codes and structured logging for automation scripts

---

## 📂 File Structure

This modular structure ensures maintainability and supports seamless integration into pipelines or ad hoc testing.

```plaintext
src/runbooks/
├── security/                       # Integrated security module
│   ├── checklist/                  # Security check modules
│   │   ├── iam_password_policy.py  # Checks IAM password policy
│   │   ├── bucket_public_access.py # Validates S3 bucket policies
│   │   ├── root_mfa.py            # Root account MFA validation
│   │   ├── cloudtrail_enabled.py  # CloudTrail configuration checks
│   │   └── ...                     # More checks for IAM, S3, CloudTrail, etc.
│   ├── utils/                      # Core utilities and constants
│   │   ├── common.py               # Shared helper functions
│   │   ├── enums.py                # Enumerations for reporting
│   │   ├── language.py             # Multi-language support
│   │   └── permission_list.py      # IAM permissions for checks
│   ├── config.json                 # Configurable parameters for checks
│   ├── permission.json             # IAM policy for execution
│   ├── report_generator.py         # HTML report generator
│   ├── security_baseline_tester.py # Core assessment engine
│   ├── run_script.py               # Legacy script support
│   ├── __init__.py                 # Module exports and API
│   └── report_template_*.html     # Multilingual report templates
├── cfat/                           # Cloud Foundations Assessment Tool
├── inventory/                      # Multi-account resource discovery
├── organizations/                  # AWS Organizations management
└── main.py                         # Central CLI entry point
```

---


## 🚀 Deployment and Usage

The security baseline assessment is fully integrated into the CloudOps Runbooks CLI, providing enterprise-grade security assessment capabilities with a simple, intuitive interface.

> **⚡ Quick Start**: `pip install runbooks && runbooks security assess`

### **Option 1: Install via PyPI (Recommended)**

1. **Install the Package**:
   ```bash
   pip install runbooks
   ```

2. **Run Security Assessment**:
   ```bash
   # Basic security assessment
   runbooks security assess
   
   # Assessment with specific AWS profile and language
   runbooks security assess --profile production --language EN
   
   # Generate Korean language report
   runbooks security assess --language KR --output ./security-reports
   ```

3. **List Available Security Checks**:
   ```bash
   runbooks security list-checks
   ```

---

### **Option 2: Development Installation**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/1xOps/CloudOps-Runbooks.git
   cd CloudOps-Runbooks
   ```

2. **Install Dependencies using UV** (Rust-based package manager):
   ```bash
   # Install UV if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies and activate environment
   uv sync --all-extras
   ```

3. **Run Security Assessment**:
   ```bash
   uv run python -m runbooks security assess --profile PROFILE_NAME --language EN
   ```

---

### **Option 3: Using Task Automation**

1. **Prerequisites Check**:
   ```bash
   task -d ~ check-tools
   task -d ~ check-aws
   ```

2. **Install and Run**:
   ```bash
   task install
   task security.assess
   ```

---

### **CLI Command Reference**

```bash
# Main security commands
runbooks security --help                    # Show security help
runbooks security assess                    # Run comprehensive assessment
runbooks security assess --profile prod     # Use specific AWS profile  
runbooks security assess --language KR      # Generate Korean report
runbooks security assess --output /reports  # Custom output directory

# Individual security checks
runbooks security check root_mfa            # Check root MFA
runbooks security check iam_password_policy # Check IAM password policy
runbooks security list-checks               # List all available checks

# Advanced usage
runbooks security assess --format html      # HTML report (default)
runbooks security assess --format json      # JSON output
runbooks security assess --format console   # Console output only
```

---

## 🛡️ Security Checks Included

The following checks are aligned with the [AWS Startup Security Baseline (SSB)](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/welcome.html):

1. **Account-Level Security**:
   - Root account MFA enabled
   - No root access keys
   - Alternate contacts configured

2. **IAM Best Practices**:
   - Password policies enforced
   - MFA for IAM users
   - Attached policies preferred over inline policies

3. **Monitoring and Logging**:
   - CloudTrail enabled across all regions
   - GuardDuty activated
   - CloudWatch alarms configured for critical events

4. **S3 Bucket Policies**:
   - Public access block enabled
   - Encryption enforced for bucket objects

5. **VPC and Network Security**:
   - Validates security group configurations
   - Multi-region usage of resources (e.g., EC2 instances, S3 buckets)

---

## 📊 Reports and Insights

- **Format**: HTML reports generated in the `results/` directory.
- **Languages**: Supported in English, Korean, and Japanese.
- **Insights**:
  - Passed, failed, and skipped checks with detailed descriptions.
  - Direct remediation steps with links to AWS documentation.

Sample Report:

| Check ID | Description                 | Result   | Remediation Steps                  |
|----------|-----------------------------|----------|------------------------------------|
| 01       | Root account MFA enabled    | ✅ Pass  | N/A                                |
| 02       | CloudTrail enabled          | ❌ Fail  | [Enable CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-create-and-update-a-trail.html) |
| 03       | S3 bucket public access     | ✅ Pass  | N/A                                |

---

## 📋 Prerequisites

### **IAM Permissions**

Attach the policy defined in `permission.json` to the IAM user or role executing the script. This policy ensures **read-only access**, except for specific actions like `iam:GenerateCredentialReport`.

### **AWS CLI Configuration**
- Set up credentials in the `~/.aws/credentials` file or use AWS CloudShell.

---

## 🔮 Future Enhancements

1. **Multi-Account Scans**:
   - Expand to support AWS Organizations for enterprise-wide checks.
2. **AI Integration**:
   - Leverage machine learning for automated anomaly detection and remediation suggestions.
3. **Visualization Dashboards**:
   - Integrate with AWS QuickSight or Grafana for real-time security monitoring.

---

## 📢 Feedback and Contributions

We value your feedback! Share your ideas or report issues via:
- **GitHub**: [CloudOps Runbooks Repository](https://github.com/nnthanh101/cloudops-runbooks/issues)
- **Email**: [support@nnthanh101.com](mailto:support@nnthanh101.com)

Let’s work together to make cloud security accessible, effective, and scalable for everyone. 🚀

---

### **Create an IAM User with Permissions**

1. **Navigate to IAM in the AWS Console**:
   - Go to the **IAM service** on the AWS Management Console.

2. **Add a New User**:
   - Select **Users** from the navigation pane, then click **Add users**.
   - Enter a username for the new user under **User name**.

3. **Assign Permissions**:
   - Choose **Attach policies directly** on the **Set permissions** page.
   - Click **Create Policy**, then switch to the **JSON** tab and paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SSBUserPermission",
            "Effect": "Allow",
            "Action": [
                "iam:GenerateCredentialReport",
                "s3:GetBucketPublicAccessBlock",
                "iam:GetAccountPasswordPolicy",
                "cloudtrail:GetTrail",
                "ec2:DescribeInstances",
                "guardduty:ListDetectors",
                "cloudtrail:GetTrailStatus",
                "account:GetAlternateContact",
                "ec2:DescribeRegions",
                "s3:ListBucket",
                "iam:ListUserPolicies",
                "support:DescribeTrustedAdvisorChecks",
                "guardduty:GetDetector",
                "cloudtrail:DescribeTrails",
                "s3:GetAccountPublicAccessBlock",
                "s3:ListAllMyBuckets",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeVpcs",
                "iam:ListAttachedUserPolicies",
                "cloudwatch:DescribeAlarms",
                "iam:ListUsers",
                "sts:GetCallerIdentity",
                "iam:GetCredentialReport",
                "ec2:DescribeSubnets"
            ],
            "Resource": "*"
        }
    ]
}
```

4. **Additional Permissions for CloudShell** *(Optional)*:
   - Add the **AWSCloudShellFullAccess** policy if you plan to use AWS CloudShell for assessments.

5. **Complete User Creation**:
   - Attach the policy to the user, then finish user creation by clicking **Next**.

6. **Generate Access Key**:
   - On the user’s **Security credentials** tab, click **Create access key** to generate the key. [Learn more about creating access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey).

7. **Configure AWS CLI**:
   - Set up your AWS credentials by editing the `~/.aws/credentials` file or use AWS CloudShell directly. [AWS CLI configuration guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

---

### **Quick Start Examples**

1. **Basic Security Assessment**:
   ```bash
   runbooks security assess
   ```

2. **Assessment with Custom Profile and Language**:
   ```bash
   runbooks security assess --profile production --language EN
   ```
   - Supported languages: **English (EN)**, **Korean (KR)**, **Japanese (JP)**, **Vietnamese (VN)**.

3. **Generate Reports in Different Languages**:
   ```bash
   # English report
   runbooks security assess --language EN --output ./reports/english
   
   # Korean report
   runbooks security assess --language KR --output ./reports/korean
   
   # Japanese report  
   runbooks security assess --language JP --output ./reports/japanese
   
   # Vietnamese report
   runbooks security assess --language VN --output ./reports/vietnamese
   ```

4. **View Results**:
   - Upon completion, an HTML report will be generated in the specified output directory (default: `./results/`)
   - The CLI provides rich console output with immediate feedback on security findings
   - Reports include actionable remediation steps with links to AWS documentation

5. **List Available Security Checks**:
   ```bash
   runbooks security list-checks
   ```

6. **Run Individual Security Checks** *(Coming Soon)*:
   ```bash
   runbooks security check root_mfa
   runbooks security check iam_password_policy
   ```

> ![Sample Report](./images/report_sample_en.png)

> ![Sample Report](./images/report_sample_vn.png)

---

## FAQ: Frequently Asked Questions

### **1. How can I test additional security items to enhance AWS account security?**

To test a broader range of security configurations, consider using [AWS Trusted Advisor](https://aws.amazon.com/blogs/aws/aws-trusted-advisor-new-priority-capability/).
This service regularly analyzes your AWS accounts and helps you implement AWS security best practices aligned with the AWS Well-Architected Framework. By managing your security settings through Trusted Advisor, you can systematically improve the security posture of your AWS environment.

---

### **2. Where can I find more information or guidelines to improve AWS security?**

AWS provides the [AWS Well-Architected Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/intro.html), a comprehensive cloud service for evaluating and optimizing your architecture.
This tool includes a **Security Pillar**, which outlines detailed best practices for securing your AWS workloads. Use these guidelines to design, assess, and enhance your security strategy effectively.

---

### **3. Can I scan multiple AWS accounts within the same AWS Organization simultaneously?**

No, this script currently supports scanning a **single AWS account** at a time.
To scan additional AWS accounts in the same organization, you must:
- Create a separate IAM user with the required permissions in each account.
- Run the script individually for each account.

**Note**: Organization-level security settings cannot be assessed using this script. Consider AWS services like **AWS Organizations** for managing policies at scale.

---

### **4. Can I use this tool without an IAM Access Key?**

Yes, you can run the security assessment without an IAM Access Key by leveraging IAM roles.
The integrated `runbooks security` CLI fully supports IAM roles and various AWS authentication methods.

**Supported Authentication Methods**:
1. **IAM Roles** (Recommended): Configure and use IAM roles instead of access keys
2. **AWS SSO**: Use AWS Single Sign-On for centralized authentication
3. **Environment Variables**: Set AWS credentials via environment variables
4. **Instance Profiles**: Automatically use instance profiles when running on EC2
5. **AWS CloudShell**: Run directly in AWS CloudShell without any setup

**Setup Examples**:

**Using IAM Roles**:
1. Configure a role profile in AWS CLI: [IAM roles guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-role.html#cli-role-overview)
2. Run the assessment:
   ```bash
   runbooks security assess --profile ROLE_PROFILE_NAME --language EN
   ```

**Using AWS SSO**:
1. Configure SSO profile: `aws configure sso`
2. Run the assessment:
   ```bash
   runbooks security assess --profile sso-profile --language EN
   ```

**Using AWS CloudShell**:
```bash
pip install runbooks
runbooks security assess --language EN
```

This approach enhances security by reducing the dependency on long-term access keys and provides enterprise-grade authentication options.

---

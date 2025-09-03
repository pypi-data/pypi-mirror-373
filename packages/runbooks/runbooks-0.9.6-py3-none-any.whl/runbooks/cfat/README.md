# AWS Cloud Foundations Assessment Tool (CLI)

The AWS Cloud Foundations Assessment Tool (CFAT) is an enterprise-grade command-line tool for automated discovery and assessment of AWS environments and multi-account architectures. Built with the Rich library for beautiful terminal output, it provides comprehensive evaluation against Cloud Foundations best practices with advanced enterprise features.

## 📈 *cfat-runbooks*.md Enterprise Rollout

Following proven **99/100 manager score** success patterns established in FinOps:

### **Rollout Strategy**: Progressive *-runbooks*.md standardization 
- **Phase 1**: CFAT rollout with *cfat-runbooks*.md framework ✅
- **Integration**: Multi-format reporting with project management export
- **Enterprise Features**: SOC2, PCI-DSS, HIPAA alignment support

**CFAT** is an enterprise-grade, open-source solution designed to provide automated discovery and assessment of AWS environments and multi-account architectures. **Fully integrated with the CloudOps Runbooks CLI**, CFAT offers comprehensive evaluation against Cloud Foundations best practices with advanced enterprise features.

CFAT reviews your environment, checking for common configurations and security best practices across your AWS Organization. The tool produces actionable findings with detailed remediation guidance, exportable to popular project management platforms.

**Key Enterprise Features:**
- 🚀 **Integrated CLI Experience**: Seamlessly integrated with `runbooks cfat` commands
- 📊 **Multi-Format Reporting**: HTML, CSV, JSON, Markdown, and interactive web reports
- ⚡ **Parallel Execution**: Configurable worker pools for fast assessment
- 🎯 **Compliance Frameworks**: SOC2, PCI-DSS, HIPAA alignment support
- 🔗 **Project Management Integration**: Direct export to Jira, Asana, ServiceNow
- 🌐 **Interactive Web Reports**: Built-in web server for live report viewing
- 🎚️ **Advanced Configuration**: Category filtering, severity thresholds, check customization

>**Note:** CFAT operates with `READONLY` permissions to ensure security and compliance. The tool does not make any changes to your AWS environment - all outputs are generated locally for your analysis.

## 🚀 Quick Start

> **⚡ Enterprise Installation**: `pip install runbooks && runbooks cfat assess`

### **Option 1: Install via PyPI (Recommended)**

1. **Install the Package**:
   ```bash
   pip install runbooks
   ```

2. **Run Cloud Foundations Assessment**:
   ```bash
   # Basic comprehensive assessment
   runbooks cfat assess
   
   # Assessment with HTML report
   runbooks cfat assess --output html --output-file cfat_report.html
   
   # Target specific categories with critical severity
   runbooks cfat assess --categories iam,cloudtrail --severity CRITICAL
   ```

3. **Advanced Usage Examples**:
   ```bash
   # Parallel execution with multiple output formats
   runbooks cfat assess --parallel --max-workers 8 --output all
   
   # Compliance framework assessment
   runbooks cfat assess --compliance-framework SOC2 --output json
   
   # Export to project management tools
   runbooks cfat assess --export-jira findings.csv --export-asana tasks.csv
   
   # Interactive web report
   runbooks cfat assess --serve-web --web-port 8080
   ```

---

### **Option 2: Development Installation**

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/1xOps/CloudOps-Runbooks.git
   cd CloudOps-Runbooks
   
   # Install with UV (Rust-based package manager)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv sync --all-extras
   ```

2. **Run Assessment**:
   ```bash
   uv run python -m runbooks cfat assess --profile production
   ```

---

### **Option 3: AWS CloudShell (Zero Setup)**

1. **Open AWS CloudShell** in your Management Account
2. **Install and Run**:
   ```bash
   pip install runbooks
   runbooks cfat assess --output html
   ```
3. **Download Results** using CloudShell's download feature

---

### **CLI Command Reference**

```bash
# Main CFAT commands
runbooks cfat --help                           # Show CFAT help
runbooks cfat assess                           # Run comprehensive assessment
runbooks cfat assess --output all              # Generate all report formats
runbooks cfat assess --categories iam,vpc      # Assess specific categories
runbooks cfat assess --severity CRITICAL       # Show only critical findings

# Advanced features
runbooks cfat assess --parallel --max-workers 10    # Fast parallel execution
runbooks cfat assess --compliance-framework SOC2    # Compliance alignment
runbooks cfat assess --export-jira jira.csv         # Export to Jira
runbooks cfat assess --serve-web --web-port 8080    # Interactive web report
```

### **Prerequisites**

For least privilege readonly access, leverage these IAM Managed Policies:
- `arn:aws:iam::aws:policy/ReadOnlyAccess`
- `arn:aws:iam::aws:policy/AWSCloudShellFullAccess` (if using CloudShell)

**Supported Authentication Methods:**
- AWS Profiles (recommended)
- IAM Roles
- AWS SSO
- Environment Variables
- Instance Profiles
- AWS CloudShell (automatic)

## 📊 Generated Reports and Artifacts

CFAT generates comprehensive, multi-format reports designed for different audiences and use cases. The modern integrated CLI provides multiple output options for maximum flexibility.

### **Output Formats**

1. **📋 HTML Reports** (Default)
   - Interactive, styled reports with charts and filtering
   - Remediation links directly to AWS documentation
   - Executive summary with compliance scoring
   - Technical details with step-by-step guidance
   ```bash
   runbooks cfat assess --output html --output-file assessment_report.html
   ```

2. **📈 JSON Output** (Programmatic Integration)
   - Structured data for CI/CD pipelines
   - API integration and automation workflows
   - Custom dashboard development
   ```bash
   runbooks cfat assess --output json --output-file findings.json
   ```

3. **📊 CSV Export** (Data Analysis)
   - Spreadsheet-compatible format
   - Sorting and filtering capabilities
   - Project tracking and progress monitoring
   ```bash
   runbooks cfat assess --output csv --output-file assessment_data.csv
   ```

4. **📝 Markdown Reports** (Documentation)
   - Documentation-friendly format
   - GitHub/GitLab integration
   - Wiki and knowledge base publishing
   ```bash
   runbooks cfat assess --output markdown --output-file assessment.md
   ```

5. **🌐 Interactive Web Reports**
   - Live web server with real-time filtering
   - Collaborative review and discussion
   - Professional presentation format
   ```bash
   runbooks cfat assess --serve-web --web-port 8080
   ```

### **Project Management Integration**

**Direct Export to Popular Platforms:**

1. **Jira Integration**
   ```bash
   runbooks cfat assess --export-jira jira_backlog.csv
   ```
   - Pre-formatted for Jira import
   - Issue types and priorities mapped
   - Sprint planning ready

2. **Asana Integration**
   ```bash
   runbooks cfat assess --export-asana asana_tasks.csv
   ```
   - Task hierarchy and dependencies
   - Team assignment capabilities
   - Progress tracking features

3. **ServiceNow Integration**
   ```bash
   runbooks cfat assess --export-servicenow snow_incidents.json
   ```
   - Enterprise ITSM compatibility
   - Incident and change management
   - SLA and priority mapping

### **All-in-One Export**

Generate all formats simultaneously:
```bash
runbooks cfat assess --output all
```

This creates:
- `cfat_report_TIMESTAMP.html` - Interactive HTML report
- `cfat_report_TIMESTAMP.json` - Structured data export
- `cfat_report_TIMESTAMP.csv` - Spreadsheet-compatible data
- `cfat_report_TIMESTAMP.md` - Documentation format

## 🎯 Assessment Capabilities

### **Multi-Account Architecture Discovery**
- **Organization Mapping**: Automatic discovery of AWS Organizations structure
- **Account Inventory**: Comprehensive multi-account resource discovery  
- **Cross-Account Analysis**: Consolidated findings across organizational units
- **Resource Relationships**: Dependency mapping and service interconnections

### **Security & Compliance Assessment**
- **Cloud Foundations Alignment**: AWS best practices validation
- **Security Posture Evaluation**: IAM, network, data protection analysis
- **Compliance Framework Support**: SOC2, PCI-DSS, HIPAA alignment
- **Risk Scoring**: Weighted risk assessment with remediation prioritization

### **Operational Excellence**
- **Configuration Drift Detection**: Identification of non-compliant configurations
- **Performance Optimization**: Resource utilization and cost efficiency analysis
- **Automation Readiness**: Infrastructure as Code (IaC) compatibility assessment
- **Monitoring Coverage**: CloudTrail, CloudWatch, and logging evaluation

### **Enterprise Integration**
- **CI/CD Pipeline Ready**: JSON output for automated workflows
- **Project Management Export**: Native integration with Jira, Asana, ServiceNow
- **Dashboard Compatible**: Structured data for custom visualization
- **API Integration**: Programmatic access for enterprise tooling

### **Modern Technology Stack**
- **Python & AWS SDK**: Built with latest boto3 and enterprise Python patterns
- **Parallel Processing**: Configurable worker pools for optimal performance
- **Pydantic Models**: Type-safe data validation and serialization
- **UV Package Management**: Rust-based dependency management for speed
- **Ruff Formatting**: Modern code quality and formatting standards

## 🔒 Security Considerations

### **Least Privilege Principle**
- **Read-Only Access**: CFAT operates exclusively with `ReadOnlyAccess` permissions
- **No Modifications**: Zero-write operations ensure your environment remains unchanged
- **Audit Compliance**: All activities are logged through standard AWS CloudTrail
- **Local Data Processing**: Assessment data is processed locally without external transmission

### **Authentication & Authorization**
- **Multiple Auth Methods**: Support for AWS profiles, IAM roles, SSO, CloudShell
- **MFA Compatible**: Full support for multi-factor authentication requirements
- **Cross-Account Roles**: Secure assessment across multiple AWS accounts
- **Session Management**: Automatic credential refresh and secure session handling

### **Data Protection**
- **Local Storage Only**: All reports generated and stored locally
- **No External Dependencies**: Assessment runs entirely within your AWS environment
- **Encryption in Transit**: All AWS API calls use HTTPS/TLS encryption
- **Temporary Credentials**: Support for temporary credential mechanisms

### **Enterprise Security Features**
- **Access Logging**: Comprehensive logging of all assessment activities
- **Configuration Validation**: Security configuration assessment without exposure
- **Compliance Reporting**: Security findings aligned with industry frameworks
- **Audit Trail**: Complete audit trail for security and compliance teams

### **Required IAM Permissions**

**Minimum Required Policy** (Read-Only):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:Get*",
                "iam:List*",
                "iam:GenerateCredentialReport",
                "organizations:List*",
                "organizations:Describe*",
                "cloudtrail:Get*",
                "cloudtrail:Describe*",
                "config:Get*",
                "config:Describe*",
                "ec2:Describe*",
                "s3:GetBucket*",
                "s3:ListAllMyBuckets",
                "cloudwatch:Describe*",
                "cloudwatch:Get*"
            ],
            "Resource": "*"
        }
    ]
}
```

**Recommended Managed Policies:**
- `arn:aws:iam::aws:policy/ReadOnlyAccess`
- `arn:aws:iam::aws:policy/AWSCloudShellFullAccess` (if using CloudShell)

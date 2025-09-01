# AWS VPC Networking Operations (CLI)

The AWS VPC Networking Operations module is an enterprise-grade command-line tool for AWS VPC analysis, cost optimization, and network management. Built with the Rich library for beautiful terminal output, it provides comprehensive VPC insights with cost analysis, security assessment, and automated optimization recommendations.

## 📈 *vpc-runbooks*.md Enterprise Rollout

Following proven **99/100 manager score** success patterns established in FinOps:

### **Rollout Strategy**: Progressive *-runbooks*.md standardization 
- **Phase 3**: VPC rollout with *vpc-runbooks*.md framework ✅
- **Phase 4**: Enhanced networking operations with enterprise patterns (Next)
- **Integration**: Complete cost optimization with FinOps module alignment

## Why AWS VPC Networking Operations?

Managing VPC networking across multiple AWS accounts requires sophisticated analysis and optimization capabilities. The VPC Operations CLI provides enterprise-grade network analysis, cost optimization insights, and security assessment tools designed for cloud architects and network engineers.

Key capabilities include:
- **VPC Cost Analysis**: Detailed cost breakdown and optimization recommendations
- **Network Security Assessment**: Comprehensive security group and NACL analysis
- **Resource Utilization**: Unused resource identification and cleanup recommendations
- **Multi-Account Support**: Cross-account VPC analysis and management
- **Rich Terminal UI**: Professional console output with charts and detailed reporting

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [AWS CLI Profile Setup](#aws-cli-profile-setup)
- [Command Line Usage](#command-line-usage)
  - [Options](#command-line-options)
  - [Examples](#examples)
- [VPC Analysis Operations](#vpc-analysis-operations)
  - [Cost Analysis](#cost-analysis)
  - [Network Security Assessment](#network-security-assessment)
  - [Resource Optimization](#resource-optimization)
  - [Multi-Account Operations](#multi-account-operations)
- [Configuration](#configuration)
- [Export Formats](#export-formats)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **VPC Cost Analysis**: 
  - Detailed cost breakdown by service and resource type
  - NAT Gateway cost optimization recommendations (up to 30% savings)
  - Unused resource identification and cleanup suggestions
  - Historical cost trending and projection analysis
- **Network Security Assessment**: 
  - Security group rule analysis and optimization
  - Network ACL configuration validation
  - VPC Flow Logs compliance checking
  - Public access exposure identification
- **Resource Optimization**: 
  - Unused Elastic IP identification
  - Idle Load Balancer detection
  - VPC Endpoint optimization recommendations
  - Subnet utilization analysis
- **Multi-Account Support**:
  - Cross-account VPC analysis
  - AWS Organizations integration
  - Consolidated reporting across accounts
  - Role-based access management
- **Configuration Management**:
  - Centralized configuration via TOML files
  - Environment-specific settings
  - Profile-based authentication management
- **Rich Terminal UI**: Beautiful terminal output with progress indicators and charts
- **Export Options**:
  - JSON export for automation integration
  - CSV export for spreadsheet analysis  
  - HTML reports for stakeholder communication
  - PDF reports for executive summaries

---

## Prerequisites

- **Python 3.8 or later**: Ensure you have the required Python version installed
- **AWS CLI configured with named profiles**: Set up your AWS CLI profiles for seamless integration
- **AWS credentials with permissions**:
  - `ec2:Describe*` (for VPC and networking resource discovery)
  - `ce:GetCostAndUsage` (for cost analysis)
  - `ce:GetUsageReport` (for usage analysis)
  - `organizations:List*` (for multi-account operations)
  - `sts:AssumeRole` (for cross-account access)
  - `sts:GetCallerIdentity` (for identity validation)

---

## Installation

There are several ways to install the AWS VPC Operations CLI:

### Option 1: Using uv (Fast Python Package Installer)
[uv](https://github.com/astral-sh/uv) is a modern Python package installer and resolver that's extremely fast.

```bash
# Install runbooks with VPC operations
uv pip install runbooks
```

### Option 2: Using pip
```bash
# Install runbooks package
pip install runbooks
```

---

## AWS CLI Profile Setup

Configure your named profiles for VPC operations:

```bash
aws configure --profile vpc-production
aws configure --profile vpc-development  
aws configure --profile vpc-management
# ... etc ...
```

For multi-account VPC analysis, ensure cross-account roles are properly configured.

---

## Command Line Usage

Run VPC operations using `runbooks vpc` followed by options:

```bash
runbooks vpc [operation] [options]
```

### Command Line Options

| Flag | Description |
|---|---|
| `--profile`, `-p` | AWS profile to use for operations |
| `--region`, `-r` | AWS region to analyze (default: us-east-1) |
| `--all-regions` | Analyze VPCs across all available regions |
| `--account-id` | Specific AWS account to analyze |
| `--output-format` | Output format: table, json, csv, html |
| `--output-file` | Save results to specified file |
| `--cost-analysis` | Include detailed cost analysis |
| `--security-analysis` | Include security assessment |
| `--optimization-recommendations` | Generate optimization recommendations |

### Examples

```bash
# Basic VPC analysis
runbooks vpc analyze --profile production

# Multi-region VPC analysis with cost breakdown
runbooks vpc analyze --profile production --all-regions --cost-analysis

# Security-focused VPC assessment
runbooks vpc analyze --profile production --security-analysis --output-format html

# Optimization recommendations
runbooks vpc optimize --profile production --region us-east-1

# Multi-account VPC analysis
runbooks vpc analyze --profile management-account --organization-wide
```

---

## VPC Analysis Operations

### Cost Analysis

**Comprehensive Cost Breakdown**:
```bash
# Detailed VPC cost analysis
runbooks vpc analyze --cost-analysis --profile production --region us-east-1

# Multi-region cost analysis
runbooks vpc analyze --cost-analysis --all-regions --profile production

# NAT Gateway cost optimization
runbooks vpc optimize --focus nat-gateways --profile production
```

**Expected Output**:
```
╭─ VPC Cost Analysis Summary ─╮
│ Total Monthly Cost: $2,847.50 │
│ NAT Gateway Costs: $1,245.60  │  
│ Data Transfer: $892.30        │
│ Load Balancers: $709.60       │
│                               │
│ 💡 Optimization Potential:    │
│ • NAT Gateway: 30% savings    │
│ • Unused EIPs: $45.60/month   │
│ • Idle LBs: $180.20/month     │
╰───────────────────────────────╯
```

### Network Security Assessment

**Security Group Analysis**:
```bash
# Comprehensive security assessment
runbooks vpc analyze --security-analysis --profile production

# Focus on public access exposure
runbooks vpc security --check-public-exposure --profile production

# Security group rule optimization
runbooks vpc security --optimize-rules --profile production
```

**Security Assessment Report**:
```
╭─ VPC Security Assessment ─╮
│ Security Groups: 47        │
│ • Compliant: 42 (89%)      │
│ • Issues Found: 5 (11%)    │
│                            │
│ Network ACLs: 12           │
│ • Default: 8               │
│ • Custom: 4                │
│                            │
│ 🚨 Critical Issues:        │
│ • Open SSH (0.0.0.0/0): 2  │
│ • Open RDP (0.0.0.0/0): 1  │
╰────────────────────────────╯
```

### Resource Optimization

**Unused Resource Detection**:
```bash
# Find unused VPC resources
runbooks vpc optimize --find-unused --profile production

# Cleanup recommendations
runbooks vpc cleanup --dry-run --profile production

# Resource utilization analysis
runbooks vpc analyze --utilization --profile production
```

**Optimization Recommendations**:
```
╭─ VPC Optimization Recommendations ─╮
│                                     │
│ 💰 Cost Savings Opportunities:      │
│ • Replace NAT Gateway with NAT      │
│   Instance: $372.60/month savings   │
│ • Remove 8 unused Elastic IPs:     │
│   $36.48/month savings             │
│ • Terminate idle Load Balancer:    │
│   $180.20/month savings            │
│                                     │
│ 🛠️  Implementation Priority:        │
│ 1. High Impact: NAT optimization    │
│ 2. Medium Impact: EIP cleanup       │
│ 3. Low Impact: LB consolidation     │
╰─────────────────────────────────────╯
```

### Multi-Account Operations

**Organization-Wide Analysis**:
```bash
# Analyze VPCs across AWS Organization
runbooks vpc analyze --organization-wide --profile management-account

# Cross-account cost comparison
runbooks vpc cost-comparison --accounts prod,dev,staging --profile management-account

# Organization security assessment
runbooks vpc security --organization-wide --profile management-account
```

---

## Configuration

### Configuration File Support

Create a `vpc_config.toml` file for centralized configuration:

```toml
# vpc_config.toml
[profiles]
production = "vpc-prod-profile"
development = "vpc-dev-profile"
management = "vpc-mgmt-profile"

[regions]
primary = ["us-east-1", "us-west-2"]
secondary = ["eu-west-1", "ap-southeast-2"]

[cost_analysis]
include_data_transfer = true
include_nat_gateway_hours = true
currency = "USD"

[optimization]
nat_gateway_threshold = 1000.0  # Monthly cost threshold
eip_unused_days = 7
load_balancer_idle_threshold = 0.01  # Request per minute

[security]
check_public_access = true
validate_flow_logs = true
assess_nacls = true

[output]
default_format = "table"
export_directory = "./vpc-reports"
```

**Using Configuration File**:
```bash
runbooks vpc analyze --config vpc_config.toml
```

### Environment-Specific Configuration

**Development Environment**:
```bash
runbooks vpc analyze --profile development --config dev_vpc.toml
```

**Production Environment**:
```bash  
runbooks vpc analyze --profile production --config prod_vpc.toml --security-analysis
```

---

## Export Formats

### JSON Output Format

```bash
runbooks vpc analyze --output-format json --output-file vpc_analysis.json --profile production
```

```json
{
  "vpc_analysis": {
    "timestamp": "2024-01-15T10:30:00Z",
    "account_id": "123456789012",
    "region": "us-east-1",
    "total_vpcs": 5,
    "cost_analysis": {
      "total_monthly_cost": 2847.50,
      "nat_gateway_cost": 1245.60,
      "data_transfer_cost": 892.30,
      "load_balancer_cost": 709.60
    },
    "optimization_recommendations": [
      {
        "type": "nat_gateway_optimization",
        "potential_savings": 372.60,
        "priority": "high"
      }
    ]
  }
}
```

### CSV Output Format

```bash
runbooks vpc analyze --output-format csv --output-file vpc_analysis.csv --profile production
```

### HTML Report Format

```bash
runbooks vpc analyze --output-format html --output-file vpc_report.html --profile production
```

---

## 💰 VPC Cost Optimization Framework

### NAT Gateway Optimization

**30% Cost Savings Strategy**:
```bash
# Analyze NAT Gateway costs
runbooks vpc optimize --focus nat-gateways --profile production

# Implement NAT instance alternative
runbooks vpc optimize --implement nat-instance --profile production --dry-run
```

### Resource Cleanup

**Unused Resource Management**:
```bash
# Identify unused Elastic IPs
runbooks vpc cleanup --resource-type eip --profile production

# Clean up unused security groups
runbooks vpc cleanup --resource-type security-groups --profile production --dry-run
```

### Multi-Account Cost Comparison

**Enterprise Cost Management**:
```bash
# Compare costs across accounts
runbooks vpc cost-comparison --accounts all --profile management-account

# Generate executive cost report
runbooks vpc cost-report --format executive --profile management-account
```

---

## Integration with Other Modules

### FinOps Integration

**Combined Cost Analysis**:
```bash
# Run VPC analysis alongside FinOps dashboard
runbooks vpc analyze --profile production --integration finops

# Export for FinOps dashboard consumption
runbooks vpc analyze --output-format json --finops-compatible --profile production
```

### Security Module Integration

**Comprehensive Security Assessment**:
```bash
# Combined VPC and security baseline analysis
runbooks vpc analyze --security-analysis --integration security --profile production
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](../../../CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/1xOps/CloudOps-Runbooks.git
cd CloudOps-Runbooks
uv sync --all-extras
uv run python -m runbooks vpc --help
```

### Running Tests
```bash
uv run pytest tests/vpc/ -v
```

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../../../LICENSE) file for details.

---

## Enterprise Support

For enterprise support, professional services, and custom integrations:
- **Email**: [info@oceansoft.io](mailto:info@oceansoft.io)
- **GitHub**: [CloudOps Runbooks Issues](https://github.com/1xOps/CloudOps-Runbooks/issues)
- **Documentation**: [Enterprise VPC Documentation](https://docs.cloudops-runbooks.io/vpc)

Let's optimize your AWS networking costs together. 🚀
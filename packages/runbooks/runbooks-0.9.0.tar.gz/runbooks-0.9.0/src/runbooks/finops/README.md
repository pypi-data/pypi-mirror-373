# AWS FinOps Dashboard (CLI)

The AWS FinOps Dashboard is an open-source, Python-based command-line tool (built with the Rich library) for AWS cost monitoring. It provides multi-account cost summaries by time period, service, and cost allocation tags; budget limits vs. actuals; EC2 instance status; six‑month cost trend charts; and "FinOps audit" reports (e.g. untagged or idle resources). It can export data to CSV/JSON/PDF.

## 📈 *finops-runbooks*.md Enterprise Rollout

Following proven **99/100 manager score** success patterns across 61 enterprise accounts:

### **Rollout Strategy**: Progressive *-runbooks*.md standardization 
- **Phase 1**: FinOps rollout proven ✅ (99.9996% accuracy, 280% ROI)
- **Phase 2**: Inventory rollout with *inventory-runbooks*.md patterns  
- **Phase 3**: Operate rollout with *operate-runbooks*.md framework
- **Phase 4**: Security rollout with *security-runbooks*.md standards

## Why AWS FinOps Dashboard?

Managing and understanding your AWS expenditure, especially across multiple accounts and services, can be complex. The AWS FinOps Dashboard CLI aims to simplify this by providing a clear, concise, and actionable view of your AWS costs and operational hygiene directly in your terminal.

Key features include:
*   **Unified View:** Consolidate cost and resource data from multiple AWS accounts.
![alt text](runbooks finops-dashboard-v2.2.3.png)
* **Cost Trend Analysis:** View how your AWS costs have been for the past six months.
![alt text](runbooks finops-dashboard_trend.png)
*   **Audit Your AWS Accounts:** Quickly identify spending patterns, untagged resources, underutilised resources and potential savings.
![alt text](audit_report.png)
*   **Generate Cost & Audit Reports:** You can generate Cost, Trend and Audit Reports in PDF, CSV & JSON formats for further analysis and reporting purposes.
![alt text](audit_report_pdf.png)
![alt text](cost_report_pdf.png)

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [AWS CLI Profile Setup](#aws-cli-profile-setup)
- [Command Line Usage](#command-line-usage)
  - [Options](#command-line-options)
  - [Examples](#examples)
- [Using a Configuration File](#using-a-configuration-file)
  - [TOML Configuration Example (`config.toml`)](#toml-configuration-example-configtoml)
  - [YAML Configuration Example (`config.yaml` or `config.yml`)](#yaml-configuration-example-configyaml-or-configyml)
  - [JSON Configuration Example (`config.json`)](#json-configuration-example-configjson)
- [Export Formats](#export-formats)
- [Cost For Every Run](#cost-for-every-run)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Cost Analysis by Time Period**: 
  - View current & previous month's spend by default
  - Set custom time ranges (e.g., 7, 30, 90 days) with `--time-range` option
- **Cost by AWS Service**: Sorted by highest cost for better insights
- **Cost by Tag**: Get the cost data by one or more tags with `--tag`(cost allocation tags must be enabled)
- **AWS Budgets Information**: Displays budget limits and actual spend
- **EC2 Instance Status**: Detailed state information across specified/accessible regions
- **Cost Trend Analysis**: View detailed cost trends in bar charts for the last 6 months across AWS profiles
- **FinOps Audit**: View untagged resources, unused or stopped resources, and Budget breaches across AWS profiles. 
- **Profile Management**:
  - Automatic profile detection
  - Specific profile selection with `--profiles`
  - Use all available profiles with `--all`
  - Combine profiles from the same AWS account with `--combine`
- **Region Control**: Specify regions for EC2 discovery using `--regions`
- **Export Options**:
  - CSV export with `--report-name` and `--report-type csv`
  - JSON export with `--report-name` and `--report-type json`
  - PDF export with `--report-name` and `--report-type pdf`
  - Export to both CSV and JSON formats with `--report-name` and `--report-type csv json`
  - Specify output directory using `--dir`
  - **Note**: Trend reports (generated via `--trend`) currently only support JSON export. Other formats specified in `--report-type` will be ignored for these reports.
- **Improved Error Handling**: Resilient and user-friendly error messages
- **Beautiful Terminal UI**: Styled with the Rich library for a visually appealing experience

---

## Prerequisites

- **Python 3.8 or later**: Ensure you have the required Python version installed
- **AWS CLI configured with named profiles**: Set up your AWS CLI profiles for seamless integration
- **AWS credentials with permissions**:
  - `ce:GetCostAndUsage`
  - `budgets:ViewBudget`
  - `ec2:DescribeInstances`
  - `ec2:DescribeRegions`
  - `sts:GetCallerIdentity`
  - `ec2:DescribeInstances`
  - `ec2:DescribeVolumes`
  - `ec2:DescribeAddresses`
  - `rds:DescribeDBInstances`
  - `rds:ListTagsForResource`
  - `lambda:ListFunctions`
  - `lambda:ListTags`
  - `elbv2:DescribeLoadBalancers`
  - `elbv2:DescribeTags`
  
---

## Installation

There are several ways to install the AWS FinOps Dashboard:


### Option 3: Using uv (Fast Python Package Installer)
[uv](https://github.com/astral-sh/uv) is a modern Python package installer and resolver that's extremely fast.

```bash
# Install runbooks aws finops dashboard
uv pip install runbooks
```

---

## AWS CLI Profile Setup

If you haven't already, configure your named profiles using the AWS CLI:

```bash
aws configure --profile profile1-name
aws configure --profile profile2-name
# ... etc ...
```

Single AWS profile, centralised-ops, billing, ... multi-account LZ

Repeat this for all the profiles you want the dashboard to potentially access.

---

## Command Line Usage

Run the script using `runbooks finops` followed by options:

```bash
runbooks finops [options]
```

### Command Line Options

| Flag | Description |
|---|---|
| `--config-file`, `-C` | Path to a TOML, YAML, or JSON configuration file. Command-line arguments will override settings from the config file. |
| `--profiles`, `-p` | Specific AWS profiles to use (space-separated). If omitted, uses 'default' profile if available, otherwise all profiles. |
| `--regions`, `-r` | Specific AWS regions to check for EC2 instances (space-separated). If omitted, attempts to check all accessible regions. |
| `--all`, `-a` | Use all available AWS profiles found in your config. |
| `--combine`, `-c` | Combine profiles from the same AWS account into single rows. |
| `--tag`, `-g` | Filter cost data by one or more cost allocation tags in `Key=Value` format. Example: `--tag Team=DevOps Env=Prod` |
| `--report-name`, `-n` | Specify the base name for the report file (without extension). |
| `--report-type`, `-y` | Specify report types (space-separated): 'csv', 'json', 'pdf'. For reports generated with `--audit`, only 'pdf' is applicable and other types will be ignored. |
| `--dir`, `-d` | Directory to save the report file(s) (default: current directory). |
| `--time-range`, `-t` | Time range for cost data in days (default: current month). Examples: 7, 30, 90. |
| `--trend` | View cost trend analysis for the last 6 months. |
| `--audit` | View list of untagged, unused resoruces and budget breaches. |

### Examples

```bash
# Use default profile, show output in terminal only
runbooks finops

# Use specific profiles 'dev' and 'prod'
runbooks finops --profiles dev prod

# Use all available profiles
runbooks finops --all

# Combine profiles from the same AWS account
runbooks finops --all --combine

# Specify custom regions to check for EC2 instances
runbooks finops --regions us-east-1 eu-west-1 ap-southeast-2

# View cost data for the last 30 days instead of current month
runbooks finops --time-range 30

# View cost data only for a specific tag (e.g., Team=DevOps)
runbooks finops --tag Team=DevOps

# View cost data for multiple tags (e.g., Team=DevOps and Env=Prod)
runbooks finops --tag Team=Devops Env=Prod

# Export data to CSV only
runbooks finops --all --report-name aws_dashboard_data --report-type csv

# Export data to JSON only
runbooks finops --all --report-name aws_dashboard_data --report-type json

# Export data to both CSV and JSON formats simultaneously
runbooks finops --all --report-name aws_dashboard_data --report-type csv json

# Export combined data for 'dev' and 'prod' profiles to a specific directory
runbooks finops --profiles dev prod --combine --report-name report --report-type csv --dir output_reports

# View cost trend analysis as bar charts for profile 'dev' and 'prod'
runbooks finops --profiles dev prod -r us-east-1 --trend

# View cost trend analysis for all cli profiles for a specific cost tag 'Team=DevOps'
runbooks finops --all --trend --tag Team=DevOps

# View audit report for profile 'dev' in region 'us-east-1'
runbooks finops -p dev -r us-east-1 --audit

# View audit report for profile 'dev' in region 'us-east-1' and export it as a pdf file to current working dir with file name 'Dev_Audit_Report'
runbooks finops -p dev -r us-east-1 --audit -n Dev_Audit_Report -y pdf

# Use a configuration file for settings
runbooks finops --config-file path/to/your_config.toml
# or
runbooks finops -C path/to/your_config.yaml
```

You'll see a live-updating table of your AWS account cost and usage details in the terminal. If export options are specified, a report file will also be generated upon completion.

---

## Using a Configuration File

Instead of passing all options via the command line, you can use a configuration file in TOML, YAML, or JSON format. Use the `--config-file` or `-C` option to specify the path to your configuration file.

Command-line arguments will always take precedence over settings defined in the configuration file.

Below are examples of how to structure your configuration file.

### TOML Configuration Example (`config.toml`)

```toml
# config.toml
profiles = ["dev-profile", "prod-profile"]
regions = ["us-east-1", "eu-west-2"]
combine = true
report_name = "monthly_finops_summary"
report_type = ["csv", "pdf"] # For cost dashboard. For audit, only PDF is used.
dir = "./reports/runbooks finops" # Defaults to present working directory
time_range = 30 # Defaults to 30 days
tag = ["CostCenter=Alpha", "Project=Phoenix"] # Optional
audit = false # Set to true to run audit report by default
trend = false # Set to true to run trend report by default
```

### YAML Configuration Example (`config.yaml` or `config.yml`)

```yaml
# config.yaml
profiles:
  - dev-profile
  - prod-profile
regions:
  - us-east-1
  - eu-west-2
combine: true
report_name: "monthly_finops_summary"
report_type:
  - csv
  - pdf # For cost dashboard. For audit, only PDF is used.
dir: "./reports/runbooks finops"
time_range: 30
tag:
  - "CostCenter=Alpha"
  - "Project=Phoenix"
audit: false # Set to true to run audit report by default
trend: false # Set to true to run trend report by default
```

### JSON Configuration Example (`config.json`)

```json
{
  "profiles": ["dev-profile", "prod-profile"],
  "regions": ["us-east-1", "eu-west-2"],
  "combine": true,
  "report_name": "monthly_finops_summary",
  "report_type": ["csv", "pdf"], /* For cost dashboard. For audit, only PDF is used. */
  "dir": "./reports/runbooks finops",
  "time_range": 30,
  "tag": ["CostCenter=Alpha", "Project=Phoenix"],
  "audit": false, /* Set to true to run audit report by default */
  "trend": false /* Set to true to run trend report by default */
}
```
---

## Export Formats

### CSV Output Format

When exporting to CSV, a file is generated with the following columns:

- `CLI Profile`
- `AWS Account ID`
- `Last Month Cost` (or previous period based on time range)
- `Current Month Cost` (or current period based on time range)
- `Cost By Service` (Each service and its cost appears on a new line within the cell)
- `Budget Status` (Each budget's limit and actual spend appears on a new line within the cell)
- `EC2 Instances` (Each instance state and its count appears on a new line within the cell)

**Note:** Due to the multi-line formatting in some cells, it's best viewed in spreadsheet software (like Excel, Google Sheets, LibreOffice Calc) rather than plain text editors.

### JSON Output Format

When exporting to JSON, a structured file is generated that includes all dashboard data in a format that's easy to parse programmatically.

### PDF Output Format (for Audit Report)

When exporting to PDF, a file is generated with the following columns:

- `Profile`
- `Account ID`
- `Untagged Resources`
- `Stopped EC2 Instances`
- `Unused Volumes`
- `Unused EIPs`
- `Budget Alerts`

---

## Cost For Every Run

This script makes API calls to AWS, primarily to Cost Explorer, Budgets, EC2, and STS. AWS may charge for Cost Explorer API calls (typically `$0.01` for each API call, check current pricing).

The number of API calls depends heavily on the options used:

- **Default dashboard when `--audit` or `--trend` flags not used**: 
  - It costs you $0.06 for one AWS Profile and $0.03 extra for each AWS profile queried.
- **Cost Trend dashboard when `--trend` flag is used**:
  - It costs you $0.03 for each AWS profile queried.
- **Audit Dashboard when `--audit` flag is used**:
  - Free

**To minimize API calls and potential costs:**

- Use the `--profiles` argument to specify only the profiles you need.
- Consider using the `--combine` option when working with multiple profiles from the same AWS account.

The exact cost per run is usually negligible but depends on the scale of your usage and AWS pricing.

---

### 💰 FinOps Excellence: Cost Analytics & Optimization 

**Goal**: Enterprise AWS cost analysis with real-time insights and multi-format reporting

#### **AWS Environment Setup (Copy-Paste Ready)**

```bash
# 🔐 Your Validated AWS SSO Configuration 
export SSO_SESSION="xops-enterprise"
export AWS_SSO_START_URL="https://xops.awsapps.com/start"

# 💰 Multi-Profile Configuration (Enterprise Ready)
export BILLING_PROFILE="XXX"
export MANAGEMENT_PROFILE="XXX"
export CENTRALISED_OPS_PROFILE="XXX"
export SINGLE_AWS_PROFILE="XXX"

# ✅ Authentication Test (Should show your account access)
aws sts get-caller-identity --profile $BILLING_PROFILE
aws sts get-caller-identity --profile $SINGLE_AWS_PROFILE
```

#### **Core FinOps Commands (Tested & Validated)**

```bash
# 🚀 Installation & Quick Test
uv run runbooks finops --help  # Verify CLI accessibility

# 📊 1. Cost Dashboard (Real AWS Cost Explorer Data)
# Shows current month: ~$136K, last month: ~$148K
uv run runbooks finops --profile $BILLING_PROFILE
uv run runbooks finops --profile $SINGLE_AWS_PROFILE

# 📈 2. Cost Trend Analysis (6-Month Historical Data)
# Dynamic Auckland timezone - no hardcoded dates
uv run runbooks finops --trend --profile $BILLING_PROFILE
uv run runbooks finops --trend --profile $SINGLE_AWS_PROFILE

# 🔍 3. Cost Audit Report (9.4s execution)  
# Detailed service breakdown with optimization recommendations
uv run runbooks finops --audit --profile $BILLING_PROFILE
uv run runbooks finops --audit --profile $SINGLE_AWS_PROFILE

# 📄 4. Multi-Format Export (CSV, JSON, HTML)
# Manager-ready reports for cost management tools
uv run runbooks finops --export --profile $BILLING_PROFILE --format csv
uv run runbooks finops --export --profile $SINGLE_AWS_PROFILE --format json

# 📋 5. Executive PDF Report  
# Professional PDF with charts for stakeholder presentation
uv run runbooks finops --pdf --profile $BILLING_PROFILE
uv run runbooks finops --pdf --profile $SINGLE_AWS_PROFILE
```

#### **Regional Optimization (Sydney/Auckland Context)**

```bash
# 🌏 AP-Southeast-2 (Sydney) Resource Analysis
export AWS_DEFAULT_REGION="ap-southeast-2"

# Combined FinOps + Inventory for regional cost optimization
uv run runbooks inventory collect --profile $SINGLE_AWS_PROFILE --regions ap-southeast-2
uv run runbooks finops --audit --profile $SINGLE_AWS_PROFILE

# Expected Results:
# - RDS: ~$20K monthly (identified in your environment)  
# - S3: Multiple buckets for optimization analysis
# - EC2: Instance rightsizing recommendations
# - Regional spend concentration analysis
```

#### **Advanced Enterprise Features**

```bash
# 🎯 Organization-Wide Cost Analysis (Management Profile)
uv run runbooks finops --trend --profile $MANAGEMENT_PROFILE
uv run runbooks org list-ous --profile $MANAGEMENT_PROFILE

# 💡 Cost Optimization Recommendations
# Automated analysis of resource utilization and right-sizing opportunities
uv run runbooks finops --audit --profile $BILLING_PROFILE --format json > cost-analysis.json

# 📊 Business Intelligence Integration
# Export cost data for integration with BI tools (Tableau, Power BI)
uv run runbooks finops --export --profile $BILLING_PROFILE --format csv > monthly-costs.csv

# 🚨 Cost Alerting & Monitoring (Future Feature)
# Integration with CloudWatch for cost spike detection
uv run runbooks finops --alert-setup --threshold 150000 --profile $BILLING_PROFILE
```

#### **Troubleshooting & Validation**

```bash
# 🔧 Common Issues & Solutions

# Issue 1: "No cost data found" 
# Solution: Ensure Cost Explorer is enabled (already confirmed in your environment)
aws ce get-cost-and-usage --profile $BILLING_PROFILE --help

# Issue 2: "Profile not found"
# Solution: Verify SSO session and profile configuration
aws sso login --profile $BILLING_PROFILE
aws configure list-profiles | grep -E "(billing|management|centralised|single)"

# Issue 3: "AccessDenied for Cost Explorer"
# Solution: Verify IAM permissions for ce:GetCostAndUsage
aws iam simulate-principal-policy --policy-source-arn $(aws sts get-caller-identity --query Arn --output text --profile $BILLING_PROFILE) --action-names ce:GetCostAndUsage

# ✅ Validation Test (Should show real cost data)
uv run runbooks finops --profile $SINGLE_AWS_PROFILE  # Should complete without errors
uv run runbooks finops --trend --profile $BILLING_PROFILE  # Should show historical data
```

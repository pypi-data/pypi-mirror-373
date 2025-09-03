# AWS SRE Automation & Reliability Engineering (CLI)

The AWS SRE Automation module is an enterprise-grade Site Reliability Engineering toolkit for AWS environments. Built with the Rich library and advanced MCP (Model Context Protocol) integration, it provides comprehensive reliability monitoring, automated incident response, and performance optimization capabilities.

## 📈 *sre-runbooks*.md Enterprise Rollout

Following proven **99/100 manager score** success patterns established in FinOps:

### **Rollout Strategy**: Progressive *-runbooks*.md standardization 
- **Phase 4**: SRE rollout with *sre-runbooks*.md framework ✅
- **Integration**: MCP reliability engine with real-time monitoring
- **DORA Metrics**: Enterprise-grade DevOps performance measurement

## Why AWS SRE Automation?

Site Reliability Engineering requires sophisticated automation, monitoring, and incident response capabilities. The SRE Automation CLI provides enterprise-grade reliability tools designed for SRE teams, DevOps engineers, and platform engineers managing large-scale AWS environments.

Key capabilities include:
- **DORA Metrics Collection**: Lead Time, Deploy Frequency, MTTR, Change Failure Rate
- **MCP Reliability Engine**: Advanced Model Context Protocol integration for intelligent monitoring
- **Automated Incident Response**: AI-powered incident detection and automated remediation
- **Performance Monitoring**: Real-time system health and performance tracking
- **Chaos Engineering**: Controlled failure injection and resilience testing

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [AWS CLI Profile Setup](#aws-cli-profile-setup)
- [Command Line Usage](#command-line-usage)
  - [Options](#command-line-options)
  - [Examples](#examples)
- [SRE Operations](#sre-operations)
  - [DORA Metrics Collection](#dora-metrics-collection)
  - [MCP Reliability Engine](#mcp-reliability-engine)
  - [Incident Response Automation](#incident-response-automation)
  - [Performance Monitoring](#performance-monitoring)
  - [Chaos Engineering](#chaos-engineering)
- [Configuration](#configuration)
- [Export Formats](#export-formats)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **DORA Metrics Implementation**: 
  - Lead Time measurement and tracking
  - Deployment Frequency monitoring
  - Mean Time To Recovery (MTTR) calculation
  - Change Failure Rate analysis
  - Historical trending and benchmarking
- **MCP Reliability Engine**: 
  - Intelligent system monitoring using Model Context Protocol
  - AI-powered anomaly detection
  - Predictive failure analysis
  - Automated remediation recommendations
- **Incident Response Automation**: 
  - Automated incident detection and classification
  - Escalation path management
  - Post-incident review automation
  - Runbook execution and validation
- **Performance Monitoring**: 
  - Real-time system health dashboards
  - Application performance monitoring
  - Infrastructure utilization tracking
  - Cost-performance optimization
- **Chaos Engineering**: 
  - Controlled failure injection
  - Resilience testing automation
  - Failure scenario simulation
  - Recovery validation
- **Enterprise Integration**:
  - PagerDuty and ServiceNow integration
  - Slack and Teams notifications
  - Jira and Confluence automation
  - Custom webhook support
- **Rich Terminal UI**: Beautiful console output with real-time metrics and charts

---

## Prerequisites

- **Python 3.8 or later**: Ensure you have the required Python version installed
- **AWS CLI configured with named profiles**: Set up your AWS CLI profiles for seamless integration
- **AWS credentials with permissions**:
  - `cloudwatch:*` (for metrics collection and monitoring)
  - `logs:*` (for log analysis and aggregation)
  - `events:*` (for event-driven automation)
  - `lambda:*` (for serverless automation functions)
  - `sns:*` (for notification management)
  - `sts:GetCallerIdentity` (for identity validation)

---

## Installation

### Option 1: Using uv (Fast Python Package Installer)
```bash
# Install runbooks with SRE automation
uv pip install runbooks
```

### Option 2: Using pip
```bash
# Install runbooks package
pip install runbooks
```

---

## Command Line Usage

Run SRE operations using `runbooks sre` followed by options:

```bash
runbooks sre [operation] [options]
```

### Command Line Options

| Flag | Description |
|---|---|
| `--profile`, `-p` | AWS profile to use for operations |
| `--region`, `-r` | AWS region to monitor (default: us-east-1) |
| `--all-regions` | Monitor across all available regions |
| `--time-range` | Time range for metrics: 1h, 6h, 24h, 7d, 30d |
| `--output-format` | Output format: table, json, csv, html |
| `--dashboard` | Launch interactive dashboard |
| `--real-time` | Enable real-time monitoring mode |
| `--mcp-enabled` | Enable MCP reliability engine |

### Examples

```bash
# DORA metrics collection
runbooks sre dora --time-range 30d --profile production

# MCP reliability engine monitoring
runbooks sre monitor --mcp-enabled --dashboard --profile production

# Incident response automation
runbooks sre incident respond --incident-id INC-12345 --profile production

# Performance monitoring dashboard
runbooks sre performance --dashboard --real-time --profile production

# Chaos engineering experiment
runbooks sre chaos --experiment network-partition --duration 300s --profile staging
```

---

## SRE Operations

### DORA Metrics Collection

**Comprehensive DORA Metrics**:
```bash
# Collect all DORA metrics
runbooks sre dora --metrics all --time-range 30d --profile production

# Lead Time analysis
runbooks sre dora --metrics lead-time --time-range 7d --profile production

# Deployment frequency tracking
runbooks sre dora --metrics deployment-frequency --profile production

# MTTR calculation
runbooks sre dora --metrics mttr --time-range 90d --profile production
```

**Expected DORA Output**:
```
╭─ DORA Metrics Summary (Last 30 Days) ─╮
│                                        │
│ 🚀 Lead Time: 2.4 hours               │
│    Target: <4 hours ✅                 │
│                                        │
│ 📊 Deployment Frequency: 12.3/day     │
│    Target: Daily ✅                    │
│                                        │
│ ⚡ MTTR: 47 minutes                    │
│    Target: <1 hour ✅                  │
│                                        │
│ ❌ Change Failure Rate: 3.2%           │
│    Target: <5% ✅                      │
│                                        │
│ 🏆 Overall DORA Score: Elite (95/100) │
╰────────────────────────────────────────╯
```

### MCP Reliability Engine

**Intelligent Monitoring with MCP**:
```bash
# Enable MCP reliability engine
runbooks sre mcp-engine start --profile production

# AI-powered anomaly detection
runbooks sre mcp-engine analyze --anomaly-detection --profile production

# Predictive failure analysis
runbooks sre mcp-engine predict --lookback 7d --forecast 24h --profile production

# Automated remediation suggestions
runbooks sre mcp-engine remediate --incident-type high-cpu --profile production
```

**MCP Engine Output**:
```
╭─ MCP Reliability Engine Status ─╮
│                                  │
│ 🧠 AI Analysis: Active          │
│ 📈 Anomalies Detected: 3        │
│ ⚠️  Predictions: 2 warnings     │
│ 🔧 Auto-Remediation: Enabled    │
│                                  │
│ 🎯 Current Reliability Score:   │
│    97.8% (Target: 99.9%)        │
│                                  │
│ 🚨 Recent Alerts:               │
│ • High CPU: web-server-01       │
│ • Memory leak: api-service-03   │
│ • Disk usage: db-server-02      │
╰──────────────────────────────────╯
```

### Incident Response Automation

**Automated Incident Management**:
```bash
# Detect and classify incidents
runbooks sre incident detect --auto-classify --profile production

# Automated response execution
runbooks sre incident respond --incident-id INC-12345 --auto-remediate --profile production

# Post-incident review automation
runbooks sre incident review --incident-id INC-12345 --generate-report --profile production

# Runbook execution
runbooks sre runbook execute --runbook-id rb-high-cpu-response --profile production
```

### Performance Monitoring

**Real-Time Performance Dashboard**:
```bash
# Launch performance dashboard
runbooks sre performance --dashboard --real-time --profile production

# Application performance monitoring
runbooks sre monitor --application web-app --profile production

# Infrastructure utilization
runbooks sre monitor --infrastructure --include-costs --profile production

# Custom metrics collection
runbooks sre monitor --custom-metrics config.yaml --profile production
```

### Chaos Engineering

**Controlled Failure Testing**:
```bash
# Network partition experiment
runbooks sre chaos --experiment network-partition --target web-tier --duration 300s --profile staging

# CPU stress testing
runbooks sre chaos --experiment cpu-stress --intensity 80% --duration 600s --profile staging

# Memory exhaustion test
runbooks sre chaos --experiment memory-leak --rate 10MB/s --duration 300s --profile staging

# Service dependency failure
runbooks sre chaos --experiment service-failure --target payment-service --profile staging
```

---

## Configuration

### SRE Configuration File

Create an `sre_config.toml` file:

```toml
# sre_config.toml
[dora_metrics]
lead_time_target = "4h"
deployment_frequency_target = "daily" 
mttr_target = "1h"
change_failure_rate_target = "5%"

[mcp_engine]
enabled = true
anomaly_threshold = 0.95
prediction_window = "24h"
auto_remediation = true

[monitoring]
dashboard_refresh = "30s"
alert_threshold = "95th_percentile"
notification_channels = ["slack", "pagerduty", "email"]

[chaos_engineering]
enabled_environments = ["staging", "pre-prod"]
max_blast_radius = "10%"
safety_checks = true

[integrations]
pagerduty_api_key = "${PAGERDUTY_API_KEY}"
slack_webhook = "${SLACK_WEBHOOK_URL}"
jira_url = "${JIRA_BASE_URL}"

[profiles]
production = "sre-prod-profile"
staging = "sre-staging-profile"
```

**Using Configuration File**:
```bash
runbooks sre --config sre_config.toml dora --metrics all
```

---

## Export Formats

### JSON Output Format

```bash
runbooks sre dora --output-format json --output-file dora_metrics.json --profile production
```

```json
{
  "dora_metrics": {
    "timestamp": "2024-01-15T10:30:00Z",
    "time_range": "30d",
    "lead_time": {
      "value": 2.4,
      "unit": "hours",
      "target": 4,
      "status": "meeting_target"
    },
    "deployment_frequency": {
      "value": 12.3,
      "unit": "per_day", 
      "target": "daily",
      "status": "exceeding_target"
    },
    "mttr": {
      "value": 47,
      "unit": "minutes",
      "target": 60,
      "status": "meeting_target"
    },
    "change_failure_rate": {
      "value": 3.2,
      "unit": "percent",
      "target": 5,
      "status": "meeting_target"
    }
  }
}
```

### HTML Dashboard Export

```bash
runbooks sre dashboard --export-html --output-file sre_dashboard.html --profile production
```

---

## Enterprise Integration

### PagerDuty Integration

```bash
# Configure PagerDuty integration
runbooks sre configure --service pagerduty --api-key $PAGERDUTY_API_KEY

# Automated incident creation
runbooks sre incident create --severity critical --title "High CPU Alert" --service web-app
```

### Slack Notifications

```bash
# Configure Slack notifications
runbooks sre configure --service slack --webhook $SLACK_WEBHOOK_URL

# Send status updates
runbooks sre notify --channel "#sre-alerts" --message "DORA metrics updated"
```

### ServiceNow Integration

```bash
# ServiceNow incident management
runbooks sre incident create --platform servicenow --category performance --priority high
```

---

## Advanced MCP Features

### MCP Reliability Health Checker

The MCP reliability engine includes a comprehensive health checking system:

```bash
# Run MCP health checks
runbooks sre mcp-health-check --profile production

# Deep system analysis
runbooks sre mcp-analyze --deep-scan --profile production

# Generate reliability report
runbooks sre mcp-report --comprehensive --output reliability_report.html
```

### AI-Powered Remediation

```bash
# Get AI remediation suggestions
runbooks sre ai-remediate --issue high-latency --context "web application" --profile production

# Execute automated fixes
runbooks sre ai-remediate --auto-execute --confirm --profile production
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](../../../CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/1xOps/CloudOps-Runbooks.git
cd CloudOps-Runbooks
uv sync --all-extras
uv run python -m runbooks sre --help
```

### Running Tests
```bash
uv run pytest tests/sre/ -v
```

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../../../LICENSE) file for details.

---

## Enterprise Support

For enterprise support, professional services, and custom SRE integrations:
- **Email**: [info@oceansoft.io](mailto:info@oceansoft.io)
- **GitHub**: [CloudOps Runbooks Issues](https://github.com/1xOps/CloudOps-Runbooks/issues)
- **Documentation**: [Enterprise SRE Documentation](https://docs.cloudops-runbooks.io/sre)

Let's build reliable, automated systems together. 🚀
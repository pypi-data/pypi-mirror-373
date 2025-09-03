"""
Cloud Foundations Assessment Tool (CFAT) - Enterprise CloudOps Assessment.

This module provides comprehensive AWS account assessment capabilities
following Cloud Foundations best practices with enterprise-grade
features including:

- Multi-format reporting (HTML, CSV, JSON, Markdown)
- Parallel assessment execution
- Customizable check configurations
- Compliance framework alignment
- Advanced scoring and risk analysis

The CFAT module is designed for DevOps and SRE teams to automate
compliance validation, security assessment, and operational
readiness evaluation across AWS environments.

Example:
    ```python
    from runbooks.cfat import AssessmentRunner, Severity

    # Initialize and configure assessment
    runner = AssessmentRunner(profile="prod", region="us-east-1")
    runner.set_min_severity(Severity.WARNING)

    # Run assessment
    report = runner.run_assessment()

    # Export results
    report.to_html("assessment_report.html")
    report.to_json("findings.json")

    # Rich console output for better formatting
    from rich.console import Console
    console = Console()

    console.print(f"[green]Compliance Score: {report.summary.compliance_score}/100[/green]")
    console.print(f"[red]Critical Issues: {report.summary.critical_issues}[/red]")
    ```

Version: 0.7.8 (Latest with enhanced CLI integration, rust tooling, and modern dependency stack)
"""

# Core assessment engine
# Enhanced data models
from runbooks.cfat.models import (
    AssessmentConfig,
    # Core models
    AssessmentReport,
    AssessmentResult,
    AssessmentSummary,
    CheckConfig,
    CheckStatus,
    # Enums
    Severity,
)
from runbooks.cfat.runner import AssessmentRunner

# Import centralized version from main runbooks package
from runbooks import __version__

# Version info
__author__ = "CloudOps Runbooks Team"

# Public API exports
__all__ = [
    # Core functionality
    "AssessmentRunner",
    # Data models
    "AssessmentReport",
    "AssessmentResult",
    "AssessmentSummary",
    "AssessmentConfig",
    "CheckConfig",
    # Enums
    "Severity",
    "CheckStatus",
    # Metadata
    "__version__",
]

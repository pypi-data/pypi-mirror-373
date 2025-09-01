"""
Reporting Module for Cloud Foundations Assessment Tool.

This module provides comprehensive report generation capabilities
in multiple formats including:

- Interactive HTML reports with charts and filtering
- CSV exports for spreadsheet analysis
- JSON data for programmatic processing
- Markdown documentation format
- Executive summaries for management

The reporting system supports:
- Customizable templates and styling
- Real-time data visualization
- Multi-format export capabilities
- Project management tool integration
- Compliance framework reporting
"""

from runbooks.cfat.reporting.exporters import (
    AsanaExporter,
    JiraExporter,
    ServiceNowExporter,
)
from runbooks.cfat.reporting.formatters import (
    HTMLReportGenerator,
)
from runbooks.cfat.reporting.templates import (
    ComplianceTemplate,
    ExecutiveTemplate,
    TechnicalTemplate,
)

__all__ = [
    # Report generators
    "HTMLReportGenerator",
    # Report templates
    "ExecutiveTemplate",
    "TechnicalTemplate",
    "ComplianceTemplate",
    # Export integrations
    "JiraExporter",
    "AsanaExporter",
    "ServiceNowExporter",
]

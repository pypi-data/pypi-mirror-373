"""
Export Integrations for Cloud Foundations Assessment.

This module provides integration with popular project management
and ticketing systems for automated task creation and tracking:

- Jira integration for development workflows
- Asana integration for project management
- ServiceNow integration for enterprise ITSM
- Generic CSV/JSON exports for custom integrations

Each exporter formats assessment findings as actionable tasks
with appropriate priority, assignee, and remediation guidance.
"""

import csv
import json
from abc import ABC, abstractmethod
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Optional

from loguru import logger

from runbooks.cfat.models import AssessmentReport, AssessmentResult, Severity


class BaseExporter(ABC):
    """Base class for assessment result exporters."""

    @abstractmethod
    def export(self, report: AssessmentReport, output_path: Optional[str] = None) -> str:
        """Export assessment results to target system."""
        pass

    @abstractmethod
    def get_exporter_name(self) -> str:
        """Get exporter name."""
        pass

    def _map_severity_to_priority(self, severity: Severity) -> str:
        """Map assessment severity to priority level."""
        mapping = {Severity.CRITICAL: "Critical", Severity.WARNING: "High", Severity.INFO: "Medium"}
        return mapping.get(severity, "Medium")


class JiraExporter(BaseExporter):
    """Jira integration for creating tickets from assessment findings."""

    def get_exporter_name(self) -> str:
        return "jira"

    def export(self, report: AssessmentReport, output_path: Optional[str] = None) -> str:
        """
        Export assessment findings as Jira-compatible CSV.

        Args:
            report: Assessment report to export
            output_path: Output file path (optional)

        Returns:
            CSV content for Jira import
        """
        logger.info("Exporting assessment results for Jira import")

        # Jira CSV headers
        headers = ["Summary", "Issue Type", "Priority", "Description", "Labels", "Components", "Assignee", "Reporter"]

        rows = []
        failed_results = report.get_failed_results()

        for result in failed_results:
            # Create Jira-compatible task
            summary = f"[CFAT] {result.check_name}: {result.message[:100]}"

            description = self._create_jira_description(result, report)

            priority = self._map_severity_to_priority(result.severity)

            labels = f"cfat,{result.check_category},{result.severity.value.lower()}"

            row = {
                "Summary": summary,
                "Issue Type": "Task",
                "Priority": priority,
                "Description": description,
                "Labels": labels,
                "Components": f"AWS-{result.check_category.upper()}",
                "Assignee": "",  # To be assigned
                "Reporter": "CFAT-Assessment-Tool",
            }
            rows.append(row)

        # Generate CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

        csv_content = output.getvalue()

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(csv_content)
            logger.info(f"Jira export saved to: {output_path}")

        return csv_content

    def _create_jira_description(self, result: AssessmentResult, report: AssessmentReport) -> str:
        """Create detailed Jira task description."""
        lines = [
            f"*Assessment Finding*: {result.finding_id}",
            f"*Severity*: {result.severity.value}",
            f"*Category*: {result.check_category}",
            f"*Status*: {result.status.value}",
            "",
            "*Description*:",
            result.message,
            "",
            "*AWS Resource*:",
            result.resource_arn or "N/A",
            "",
            "*Recommendations*:",
        ]

        for rec in result.recommendations:
            lines.append(f"• {rec}")

        lines.extend(
            [
                "",
                f"*Assessment Details*:",
                f"• Account ID: {report.account_id}",
                f"• Region: {report.region}",
                f"• Assessment Date: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                f"• Execution Time: {result.execution_time:.2f}s",
            ]
        )

        return "\n".join(lines)


class AsanaExporter(BaseExporter):
    """Asana integration for project task creation."""

    def get_exporter_name(self) -> str:
        return "asana"

    def export(self, report: AssessmentReport, output_path: Optional[str] = None) -> str:
        """
        Export assessment findings as Asana-compatible CSV.

        Args:
            report: Assessment report to export
            output_path: Output file path (optional)

        Returns:
            CSV content for Asana import
        """
        logger.info("Exporting assessment results for Asana import")

        # Asana CSV headers
        headers = ["Name", "Notes", "Priority", "Tags", "Projects", "Due Date", "Assignee"]

        rows = []
        failed_results = report.get_failed_results()

        for result in failed_results:
            # Create Asana-compatible task
            name = f"[CFAT] Fix {result.check_name}"

            notes = self._create_asana_notes(result, report)

            priority = self._map_severity_to_priority(result.severity)

            tags = f"cfat,{result.check_category},{result.severity.value.lower()}"

            # Set due date based on severity
            due_date = self._calculate_due_date(result.severity)

            row = {
                "Name": name,
                "Notes": notes,
                "Priority": priority,
                "Tags": tags,
                "Projects": "AWS Security Remediation",
                "Due Date": due_date,
                "Assignee": "",
            }
            rows.append(row)

        # Generate CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

        csv_content = output.getvalue()

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(csv_content)
            logger.info(f"Asana export saved to: {output_path}")

        return csv_content

    def _create_asana_notes(self, result: AssessmentResult, report: AssessmentReport) -> str:
        """Create Asana task notes."""
        lines = [f"Finding: {result.finding_id}", f"Issue: {result.message}", "", "Recommended Actions:"]

        for rec in result.recommendations:
            lines.append(f"- {rec}")

        return "\n".join(lines)

    def _calculate_due_date(self, severity: Severity) -> str:
        """Calculate due date based on severity."""
        from datetime import timedelta

        today = datetime.now()

        if severity == Severity.CRITICAL:
            due = today + timedelta(days=7)  # 1 week
        elif severity == Severity.WARNING:
            due = today + timedelta(days=30)  # 1 month
        else:
            due = today + timedelta(days=90)  # 3 months

        return due.strftime("%Y-%m-%d")


class ServiceNowExporter(BaseExporter):
    """ServiceNow integration for enterprise ITSM."""

    def get_exporter_name(self) -> str:
        return "servicenow"

    def export(self, report: AssessmentReport, output_path: Optional[str] = None) -> str:
        """
        Export assessment findings as ServiceNow JSON.

        Args:
            report: Assessment report to export
            output_path: Output file path (optional)

        Returns:
            JSON content for ServiceNow import
        """
        logger.info("Exporting assessment results for ServiceNow import")

        incidents = []
        failed_results = report.get_failed_results()

        for result in failed_results:
            incident = {
                "short_description": f"CFAT: {result.check_name}",
                "description": result.message,
                "category": "Security",
                "subcategory": result.check_category.upper(),
                "priority": self._map_severity_to_snow_priority(result.severity),
                "impact": self._map_severity_to_impact(result.severity),
                "urgency": self._map_severity_to_urgency(result.severity),
                "assignment_group": "Cloud Security Team",
                "work_notes": "\n".join(result.recommendations),
                "cmdb_ci": result.resource_arn or report.account_id,
                "business_service": "AWS Infrastructure",
            }
            incidents.append(incident)

        export_data = {
            "incidents": incidents,
            "metadata": {
                "assessment_id": f"cfat-{report.timestamp.strftime('%Y%m%d-%H%M%S')}",
                "account_id": report.account_id,
                "assessment_date": report.timestamp.isoformat(),
                "total_findings": len(failed_results),
                "compliance_score": report.summary.compliance_score,
            },
        }

        json_content = json.dumps(export_data, indent=2, default=str)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            logger.info(f"ServiceNow export saved to: {output_path}")

        return json_content

    def _map_severity_to_snow_priority(self, severity: Severity) -> str:
        """Map severity to ServiceNow priority."""
        mapping = {Severity.CRITICAL: "1 - Critical", Severity.WARNING: "2 - High", Severity.INFO: "3 - Moderate"}
        return mapping.get(severity, "3 - Moderate")

    def _map_severity_to_impact(self, severity: Severity) -> str:
        """Map severity to ServiceNow impact."""
        mapping = {Severity.CRITICAL: "1 - High", Severity.WARNING: "2 - Medium", Severity.INFO: "3 - Low"}
        return mapping.get(severity, "3 - Low")

    def _map_severity_to_urgency(self, severity: Severity) -> str:
        """Map severity to ServiceNow urgency."""
        mapping = {Severity.CRITICAL: "1 - High", Severity.WARNING: "2 - Medium", Severity.INFO: "3 - Low"}
        return mapping.get(severity, "3 - Low")


# Exporter registry
EXPORTERS = {
    "jira": JiraExporter,
    "asana": AsanaExporter,
    "servicenow": ServiceNowExporter,
}


def get_exporter(exporter_name: str) -> Optional[BaseExporter]:
    """
    Get exporter instance by name.

    Args:
        exporter_name: Name of the exporter

    Returns:
        Exporter instance or None if not found
    """
    exporter_class = EXPORTERS.get(exporter_name.lower())
    if exporter_class:
        return exporter_class()
    return None


def list_available_exporters() -> List[str]:
    """
    Get list of available exporters.

    Returns:
        List of available exporter names
    """
    return list(EXPORTERS.keys())

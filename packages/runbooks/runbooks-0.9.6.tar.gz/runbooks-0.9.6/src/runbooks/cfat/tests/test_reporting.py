"""
Tests for CFAT reporting functionality.

Tests report generation, export formats, and project management
integrations to ensure reliable multi-format output generation.
"""

import csv
import json
import os
import tempfile
from io import StringIO
from pathlib import Path

import pytest

from runbooks.cfat.models import AssessmentReport, CheckStatus, Severity
from runbooks.cfat.reporting.exporters import (
    AsanaExporter,
    JiraExporter,
    ServiceNowExporter,
    get_exporter,
    list_available_exporters,
)
from runbooks.cfat.tests import create_sample_assessment_report


@pytest.mark.reporting
class TestReportGeneration:
    """Test assessment report generation in various formats."""

    def setup_method(self):
        """Set up test environment."""
        self.report = create_sample_assessment_report(num_results=10)
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_json_export(self):
        """Test JSON report generation."""
        json_file = os.path.join(self.temp_dir, "test_report.json")

        # Generate JSON report
        self.report.to_json(json_file)

        # Verify file was created
        assert os.path.exists(json_file)

        # Verify JSON content
        with open(json_file, "r") as f:
            data = json.load(f)

        assert data["account_id"] == self.report.account_id
        assert data["region"] == self.report.region
        assert len(data["results"]) == len(self.report.results)
        assert "summary" in data
        assert data["summary"]["total_checks"] == self.report.summary.total_checks

    def test_csv_export(self):
        """Test CSV report generation."""
        csv_file = os.path.join(self.temp_dir, "test_report.csv")

        # Generate CSV report
        self.report.to_csv(csv_file)

        # Verify file was created
        assert os.path.exists(csv_file)

        # Verify CSV content
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == len(self.report.results)

        # Check required columns
        expected_columns = ["finding_id", "check_name", "category", "status", "severity", "message", "execution_time"]
        for col in expected_columns:
            assert col in reader.fieldnames

        # Verify data integrity
        first_row = rows[0]
        first_result = self.report.results[0]
        assert first_row["finding_id"] == first_result.finding_id
        assert first_row["check_name"] == first_result.check_name
        assert first_row["status"] == first_result.status.value

    def test_html_export(self):
        """Test HTML report generation."""
        html_file = os.path.join(self.temp_dir, "test_report.html")

        # Generate HTML report
        self.report.to_html(html_file)

        # Verify file was created
        assert os.path.exists(html_file)

        # Verify HTML content
        with open(html_file, "r") as f:
            html_content = f.read()

        assert "<!DOCTYPE html>" in html_content
        assert "Cloud Foundations Assessment Report" in html_content
        assert self.report.account_id in html_content
        assert str(self.report.summary.total_checks) in html_content

    def test_markdown_export(self):
        """Test Markdown report generation."""
        md_file = os.path.join(self.temp_dir, "test_report.md")

        # Generate Markdown report
        self.report.to_markdown(md_file)

        # Verify file was created
        assert os.path.exists(md_file)

        # Verify Markdown content
        with open(md_file, "r") as f:
            md_content = f.read()

        assert "# Cloud Foundations Assessment Report" in md_content
        assert f"**Account:** {self.report.account_id}" in md_content
        assert f"**Total Checks:** {self.report.summary.total_checks}" in md_content
        assert f"**Compliance Score:** {self.report.summary.compliance_score}" in md_content

    def test_export_with_failed_results(self):
        """Test export handling when there are failed results."""
        # Create report with failed results
        from runbooks.cfat.tests import create_sample_assessment_result

        failed_result = create_sample_assessment_result(
            finding_id="FAIL-001",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            message="Critical security issue",
            check_name="security_check",
        )

        # Add to report
        self.report.results.append(failed_result)

        # Test markdown export shows critical findings
        md_file = os.path.join(self.temp_dir, "failed_report.md")
        self.report.to_markdown(md_file)

        with open(md_file, "r") as f:
            content = f.read()

        assert "🚨 Critical Findings" in content
        assert "FAIL-001" in content


@pytest.mark.reporting
class TestProjectManagementExporters:
    """Test project management tool exporters."""

    def setup_method(self):
        """Set up test environment."""
        # Create report with some failed results for export
        self.report = create_sample_assessment_report(num_results=5)

        # Ensure we have some failed results
        from runbooks.cfat.tests import create_sample_assessment_result

        failed_result = create_sample_assessment_result(
            finding_id="CRITICAL-001",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            message="Critical security vulnerability requires immediate attention",
            check_name="security_critical_check",
        )
        failed_result.recommendations = ["Enable MFA for root account", "Review IAM policies for least privilege"]
        self.report.results.append(failed_result)

        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_jira_exporter(self):
        """Test Jira CSV export functionality."""
        exporter = JiraExporter()
        assert exporter.get_exporter_name() == "jira"

        # Test export to file
        jira_file = os.path.join(self.temp_dir, "jira_export.csv")
        csv_content = exporter.export(self.report, jira_file)

        # Verify file was created
        assert os.path.exists(jira_file)

        # Verify CSV content structure
        assert isinstance(csv_content, str)
        assert "Summary,Issue Type,Priority" in csv_content
        assert "[CFAT]" in csv_content

        # Parse CSV to verify structure
        csv_reader = csv.DictReader(StringIO(csv_content))
        rows = list(csv_reader)

        # Should have at least one row for failed results
        failed_results = self.report.get_failed_results()
        assert len(rows) >= len(failed_results)

        # Check required Jira columns
        expected_columns = ["Summary", "Issue Type", "Priority", "Description", "Labels"]
        for col in expected_columns:
            assert col in csv_reader.fieldnames

    def test_asana_exporter(self):
        """Test Asana CSV export functionality."""
        exporter = AsanaExporter()
        assert exporter.get_exporter_name() == "asana"

        # Test export
        asana_file = os.path.join(self.temp_dir, "asana_export.csv")
        csv_content = exporter.export(self.report, asana_file)

        # Verify file and content
        assert os.path.exists(asana_file)
        assert isinstance(csv_content, str)
        assert "Name,Notes,Priority" in csv_content

        # Parse and verify structure
        csv_reader = csv.DictReader(StringIO(csv_content))
        rows = list(csv_reader)
        assert len(rows) > 0

        # Check Asana-specific columns
        expected_columns = ["Name", "Notes", "Priority", "Tags", "Due Date"]
        for col in expected_columns:
            assert col in csv_reader.fieldnames

    def test_servicenow_exporter(self):
        """Test ServiceNow JSON export functionality."""
        exporter = ServiceNowExporter()
        assert exporter.get_exporter_name() == "servicenow"

        # Test export
        snow_file = os.path.join(self.temp_dir, "servicenow_export.json")
        json_content = exporter.export(self.report, snow_file)

        # Verify file and content
        assert os.path.exists(snow_file)
        assert isinstance(json_content, str)

        # Parse JSON to verify structure
        data = json.loads(json_content)
        assert "incidents" in data
        assert "metadata" in data

        # Verify incident structure
        incidents = data["incidents"]
        assert len(incidents) > 0

        incident = incidents[0]
        required_fields = ["short_description", "description", "category", "priority", "impact", "urgency"]
        for field in required_fields:
            assert field in incident

        # Verify metadata
        metadata = data["metadata"]
        assert metadata["account_id"] == self.report.account_id
        assert "assessment_date" in metadata

    def test_severity_mapping(self):
        """Test severity to priority mapping in exporters."""
        jira_exporter = JiraExporter()

        # Test severity mapping
        assert jira_exporter._map_severity_to_priority(Severity.CRITICAL) == "Critical"
        assert jira_exporter._map_severity_to_priority(Severity.WARNING) == "High"
        assert jira_exporter._map_severity_to_priority(Severity.INFO) == "Medium"

    def test_exporter_registry(self):
        """Test exporter registry functionality."""
        # Test getting exporters by name
        jira_exporter = get_exporter("jira")
        assert isinstance(jira_exporter, JiraExporter)

        asana_exporter = get_exporter("asana")
        assert isinstance(asana_exporter, AsanaExporter)

        snow_exporter = get_exporter("servicenow")
        assert isinstance(snow_exporter, ServiceNowExporter)

        # Test invalid exporter
        invalid_exporter = get_exporter("invalid")
        assert invalid_exporter is None

        # Test listing available exporters
        available = list_available_exporters()
        assert "jira" in available
        assert "asana" in available
        assert "servicenow" in available

    def test_export_with_no_failed_results(self):
        """Test exporters handle reports with no failed results gracefully."""
        # Create report with only passed results
        from runbooks.cfat.tests import create_sample_assessment_result

        passed_report = create_sample_assessment_report(num_results=0)
        passed_result = create_sample_assessment_result(status=CheckStatus.PASS, severity=Severity.INFO)
        passed_report.results = [passed_result]

        # Test Jira exporter
        jira_exporter = JiraExporter()
        jira_file = os.path.join(self.temp_dir, "jira_empty.csv")
        csv_content = jira_exporter.export(passed_report, jira_file)

        # Should still create file with headers but no data rows
        assert os.path.exists(jira_file)
        csv_reader = csv.DictReader(StringIO(csv_content))
        rows = list(csv_reader)
        assert len(rows) == 0  # No failed results to export

    def test_large_export(self):
        """Test exporters handle large numbers of findings."""
        # Create report with many failed results
        large_report = create_sample_assessment_report(num_results=0)

        from runbooks.cfat.tests import create_sample_assessment_result

        for i in range(100):
            failed_result = create_sample_assessment_result(
                finding_id=f"LARGE-{i:03d}",
                status=CheckStatus.FAIL,
                severity=Severity.WARNING,
                message=f"Large test finding {i}",
                check_name=f"large_check_{i}",
            )
            large_report.results.append(failed_result)

        # Test Jira export handles large data
        jira_exporter = JiraExporter()
        jira_file = os.path.join(self.temp_dir, "jira_large.csv")
        csv_content = jira_exporter.export(large_report, jira_file)

        # Verify all results were exported
        csv_reader = csv.DictReader(StringIO(csv_content))
        rows = list(csv_reader)
        assert len(rows) == 100

        # Verify file size is reasonable
        file_size = os.path.getsize(jira_file)
        assert file_size > 1000  # Should be substantial but not enormous
        assert file_size < 1000000  # Should be less than 1MB

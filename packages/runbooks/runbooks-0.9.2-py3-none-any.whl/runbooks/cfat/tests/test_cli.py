"""
CLI tests for Cloud Foundations Assessment Tool.

Tests command-line interface argument parsing, validation, and integration
with the assessment engine. These tests focus on CLI behavior separately
from AWS API interactions.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from runbooks.cfat.tests import create_sample_assessment_report
from runbooks.main import assess, cfat, main


@pytest.mark.cli
class TestCFATCLI:
    """Test CFAT CLI functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.sample_report = create_sample_assessment_report()

    def test_cfat_help_command(self):
        """Test CFAT help command."""
        result = self.runner.invoke(main, ["cfat", "--help"])

        assert result.exit_code == 0
        assert "Cloud Foundations Assessment Tool" in result.output
        assert "assess" in result.output

    def test_assess_help_command(self):
        """Test assess command help."""
        result = self.runner.invoke(main, ["cfat", "assess", "--help"])

        assert result.exit_code == 0
        assert "Run enhanced Cloud Foundations assessment" in result.output
        assert "--output" in result.output
        assert "--severity" in result.output
        assert "--parallel" in result.output
        assert "--export-jira" in result.output

    def test_assess_basic_arguments(self):
        """Test basic assess command arguments."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_runner.return_value = mock_instance

            result = self.runner.invoke(main, ["cfat", "assess", "--output", "console", "--severity", "WARNING"])

            # Should complete successfully
            assert result.exit_code == 0

            # Verify runner was initialized and configured
            mock_runner.assert_called_once()
            mock_instance.set_min_severity.assert_called_with("WARNING")
            mock_instance.run_assessment.assert_called_once()

    def test_assess_output_formats(self):
        """Test different output formats."""
        formats = ["console", "html", "csv", "json", "markdown"]

        for format_type in formats:
            with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
                mock_instance = MagicMock()
                mock_instance.run_assessment.return_value = self.sample_report
                mock_runner.return_value = mock_instance

                result = self.runner.invoke(main, ["cfat", "assess", "--output", format_type])

                assert result.exit_code == 0, f"Failed for format: {format_type}"

    def test_assess_all_output_format(self):
        """Test 'all' output format generates multiple files."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_runner.return_value = mock_instance

            with tempfile.TemporaryDirectory() as temp_dir:
                original_cwd = os.getcwd()
                try:
                    os.chdir(temp_dir)

                    result = self.runner.invoke(main, ["cfat", "assess", "--output", "all"])

                    assert result.exit_code == 0
                    assert "Generated files:" in result.output

                finally:
                    os.chdir(original_cwd)

    def test_assess_specific_checks(self):
        """Test specifying specific checks to run."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_runner.return_value = mock_instance

            result = self.runner.invoke(
                main, ["cfat", "assess", "--checks", "iam_root_mfa", "--checks", "cloudtrail_enabled"]
            )

            assert result.exit_code == 0
            mock_instance.set_checks.assert_called_with(["iam_root_mfa", "cloudtrail_enabled"])

    def test_assess_skip_checks(self):
        """Test skipping specific checks."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_runner.return_value = mock_instance

            result = self.runner.invoke(
                main, ["cfat", "assess", "--skip-checks", "ec2_instances", "--skip-checks", "rds_instances"]
            )

            assert result.exit_code == 0
            mock_instance.skip_checks.assert_called_with(["ec2_instances", "rds_instances"])

    def test_assess_categories(self):
        """Test specifying assessment categories."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_instance.assessment_config = MagicMock()
            mock_runner.return_value = mock_instance

            result = self.runner.invoke(
                main, ["cfat", "assess", "--categories", "iam", "--categories", "vpc", "--skip-categories", "ec2"]
            )

            assert result.exit_code == 0

            # Verify categories were set
            assert mock_instance.assessment_config.included_categories == ["iam", "vpc"]
            assert mock_instance.assessment_config.excluded_categories == ["ec2"]

    def test_assess_parallel_execution_options(self):
        """Test parallel execution configuration."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_instance.assessment_config = MagicMock()
            mock_runner.return_value = mock_instance

            # Test parallel execution
            result = self.runner.invoke(main, ["cfat", "assess", "--parallel", "--max-workers", "5"])

            assert result.exit_code == 0
            assert mock_instance.assessment_config.parallel_execution is True
            assert mock_instance.assessment_config.max_workers == 5

            # Test sequential execution
            result = self.runner.invoke(main, ["cfat", "assess", "--sequential"])

            assert result.exit_code == 0
            assert mock_instance.assessment_config.parallel_execution is False

    def test_assess_compliance_framework(self):
        """Test compliance framework specification."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_instance.assessment_config = MagicMock()
            mock_runner.return_value = mock_instance

            result = self.runner.invoke(main, ["cfat", "assess", "--compliance-framework", "SOC2"])

            assert result.exit_code == 0
            assert mock_instance.assessment_config.compliance_framework == "SOC2"

    def test_assess_export_integrations(self):
        """Test export to project management tools."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            with patch("runbooks.cfat.reporting.exporters.JiraExporter") as mock_jira:
                with patch("runbooks.cfat.reporting.exporters.AsanaExporter") as mock_asana:
                    mock_instance = MagicMock()
                    mock_instance.run_assessment.return_value = self.sample_report
                    mock_runner.return_value = mock_instance

                    mock_jira_instance = MagicMock()
                    mock_asana_instance = MagicMock()
                    mock_jira.return_value = mock_jira_instance
                    mock_asana.return_value = mock_asana_instance

                    with tempfile.TemporaryDirectory() as temp_dir:
                        jira_file = os.path.join(temp_dir, "jira.csv")
                        asana_file = os.path.join(temp_dir, "asana.csv")

                        result = self.runner.invoke(
                            main, ["cfat", "assess", "--export-jira", jira_file, "--export-asana", asana_file]
                        )

                        assert result.exit_code == 0

                        # Verify exporters were called
                        mock_jira_instance.export.assert_called_once_with(self.sample_report, jira_file)
                        mock_asana_instance.export.assert_called_once_with(self.sample_report, asana_file)

    def test_assess_web_server_option(self):
        """Test web server option (without actually starting server)."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            with patch("runbooks.main.start_web_server") as mock_web_server:
                mock_instance = MagicMock()
                mock_instance.run_assessment.return_value = self.sample_report
                mock_runner.return_value = mock_instance

                result = self.runner.invoke(main, ["cfat", "assess", "--serve-web", "--web-port", "9000"])

                assert result.exit_code == 0
                mock_web_server.assert_called_once_with(self.sample_report, 9000)

    def test_assess_output_file_specification(self):
        """Test specifying custom output file."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_runner.return_value = mock_instance

            with tempfile.TemporaryDirectory() as temp_dir:
                output_file = os.path.join(temp_dir, "custom_report.html")

                result = self.runner.invoke(main, ["cfat", "assess", "--output", "html", "--output-file", output_file])

                assert result.exit_code == 0

    def test_assess_invalid_arguments(self):
        """Test handling of invalid arguments."""
        # Test invalid output format
        result = self.runner.invoke(main, ["cfat", "assess", "--output", "invalid_format"])
        assert result.exit_code != 0

        # Test invalid severity
        result = self.runner.invoke(main, ["cfat", "assess", "--severity", "INVALID"])
        assert result.exit_code != 0

        # Test invalid max-workers
        result = self.runner.invoke(main, ["cfat", "assess", "--max-workers", "0"])
        # This should succeed at CLI level but may fail in assessment config validation
        assert result.exit_code in [0, 1]  # Either CLI rejects or assessment validates

    def test_assess_error_handling(self):
        """Test CLI error handling when assessment fails."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.side_effect = Exception("Assessment failed")
            mock_runner.return_value = mock_instance

            result = self.runner.invoke(main, ["cfat", "assess"])

            assert result.exit_code == 1
            assert "Assessment failed" in result.output

    def test_profile_and_region_options(self):
        """Test AWS profile and region options."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_runner.return_value = mock_instance

            result = self.runner.invoke(main, ["--profile", "test-profile", "--region", "eu-west-1", "cfat", "assess"])

            assert result.exit_code == 0

            # Verify runner was initialized with correct profile and region
            mock_runner.assert_called_once()
            call_args = mock_runner.call_args
            assert call_args[1]["profile"] == "test-profile"
            assert call_args[1]["region"] == "eu-west-1"

    def test_debug_mode(self):
        """Test debug mode activation."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            mock_instance = MagicMock()
            mock_instance.run_assessment.return_value = self.sample_report
            mock_runner.return_value = mock_instance

            result = self.runner.invoke(main, ["--debug", "cfat", "assess"])

            assert result.exit_code == 0

    def test_comprehensive_cli_workflow(self):
        """Test comprehensive CLI workflow with multiple options."""
        with patch("runbooks.cfat.runner.AssessmentRunner") as mock_runner:
            with patch("runbooks.cfat.reporting.exporters.JiraExporter") as mock_jira:
                mock_instance = MagicMock()
                mock_instance.run_assessment.return_value = self.sample_report
                mock_instance.assessment_config = MagicMock()
                mock_runner.return_value = mock_instance

                mock_jira_instance = MagicMock()
                mock_jira.return_value = mock_jira_instance

                with tempfile.TemporaryDirectory() as temp_dir:
                    jira_file = os.path.join(temp_dir, "jira_export.csv")

                    result = self.runner.invoke(
                        main,
                        [
                            "--profile",
                            "production",
                            "--region",
                            "us-west-2",
                            "--debug",
                            "cfat",
                            "assess",
                            "--output",
                            "all",
                            "--categories",
                            "iam",
                            "cloudtrail",
                            "--skip-checks",
                            "ec2_unused_instances",
                            "--severity",
                            "CRITICAL",
                            "--parallel",
                            "--max-workers",
                            "8",
                            "--compliance-framework",
                            "SOC2",
                            "--export-jira",
                            jira_file,
                        ],
                    )

                    assert result.exit_code == 0

                    # Verify all configurations were applied
                    assert mock_instance.assessment_config.included_categories == ["iam", "cloudtrail"]
                    assert mock_instance.assessment_config.excluded_checks == ["ec2_unused_instances"]
                    assert mock_instance.assessment_config.parallel_execution is True
                    assert mock_instance.assessment_config.max_workers == 8
                    assert mock_instance.assessment_config.compliance_framework == "SOC2"

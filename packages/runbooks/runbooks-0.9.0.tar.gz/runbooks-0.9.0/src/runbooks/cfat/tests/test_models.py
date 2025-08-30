"""
Unit tests for CFAT data models.

Tests comprehensive validation, serialization, and business logic
of enhanced Pydantic models including field validation, type checking,
and model consistency.
"""

import json
from datetime import datetime
from typing import Any, Dict

import pytest

from runbooks.cfat.models import (
    AssessmentConfig,
    AssessmentReport,
    AssessmentResult,
    AssessmentSummary,
    CheckConfig,
    CheckStatus,
    Severity,
)
from runbooks.cfat.tests import (
    TEST_ACCOUNT_ID,
    TEST_PROFILE,
    TEST_REGION,
    create_sample_assessment_report,
    create_sample_assessment_result,
    create_sample_assessment_summary,
)


class TestSeverityEnum:
    """Test Severity enumeration."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert Severity.INFO == "INFO"
        assert Severity.WARNING == "WARNING"
        assert Severity.CRITICAL == "CRITICAL"

    def test_severity_ordering(self):
        """Test severity enum values."""
        # String enums can't be compared directly, but we can check the values
        severity_order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.CRITICAL: 2}
        assert severity_order[Severity.INFO] < severity_order[Severity.WARNING] < severity_order[Severity.CRITICAL]


class TestCheckStatusEnum:
    """Test CheckStatus enumeration."""

    def test_status_values(self):
        """Test status enum values."""
        assert CheckStatus.PASS == "PASS"
        assert CheckStatus.FAIL == "FAIL"
        assert CheckStatus.SKIP == "SKIP"
        assert CheckStatus.ERROR == "ERROR"


@pytest.mark.models
class TestAssessmentResult:
    """Test AssessmentResult model."""

    def test_create_valid_result(self):
        """Test creating valid assessment result."""
        result = create_sample_assessment_result()

        assert result.finding_id == "TEST-001"
        assert result.check_name == "test_check"
        assert result.check_category == "test"
        assert result.status == CheckStatus.PASS
        assert result.severity == Severity.INFO
        assert result.message == "Test check passed"
        assert result.execution_time == 0.1
        assert isinstance(result.timestamp, datetime)

    def test_result_properties(self):
        """Test assessment result properties."""
        passed_result = create_sample_assessment_result(status=CheckStatus.PASS)
        assert passed_result.passed is True
        assert passed_result.failed is False

        failed_result = create_sample_assessment_result(status=CheckStatus.FAIL)
        assert failed_result.passed is False
        assert failed_result.failed is True

    def test_severity_properties(self):
        """Test severity-based properties."""
        critical_result = create_sample_assessment_result(severity=Severity.CRITICAL)
        assert critical_result.is_critical is True
        assert critical_result.is_warning is False

        warning_result = create_sample_assessment_result(severity=Severity.WARNING)
        assert warning_result.is_critical is False
        assert warning_result.is_warning is True

    def test_finding_id_validation(self):
        """Test finding ID validation and formatting."""
        result = AssessmentResult(
            finding_id="iam-001",  # lowercase
            check_name="test",
            check_category="iam",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="test",
            execution_time=0.1,
        )
        # Should be converted to uppercase
        assert result.finding_id == "IAM-001"

    def test_finding_id_empty_validation(self):
        """Test finding ID cannot be empty."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="String should have at least 1 character"):
            AssessmentResult(
                finding_id="",
                check_name="test",
                check_category="iam",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="test",
                execution_time=0.1,
            )

    def test_arn_validation(self):
        """Test AWS ARN validation."""
        # Valid ARN should pass
        result = AssessmentResult(
            finding_id="TEST-001",
            check_name="test",
            check_category="iam",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="test",
            resource_arn="arn:aws:iam::123456789012:user/test",
            execution_time=0.1,
        )
        assert result.resource_arn == "arn:aws:iam::123456789012:user/test"

        # Invalid ARN should log warning but not fail
        result = AssessmentResult(
            finding_id="TEST-002",
            check_name="test",
            check_category="iam",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="test",
            resource_arn="invalid-arn",
            execution_time=0.1,
        )
        assert result.resource_arn == "invalid-arn"

    def test_add_recommendation(self):
        """Test adding recommendations."""
        result = create_sample_assessment_result()

        result.add_recommendation("New recommendation")
        assert "New recommendation" in result.recommendations

        # Adding duplicate should not create duplicate
        result.add_recommendation("New recommendation")
        assert result.recommendations.count("New recommendation") == 1

    def test_category_prefix(self):
        """Test category prefix extraction."""
        result = create_sample_assessment_result(finding_id="IAM-001")
        assert result.category_prefix == "IAM"

        result_no_dash = create_sample_assessment_result(finding_id="NOHYPHEN")
        assert result_no_dash.category_prefix == "TEST"  # Falls back to category

    def test_to_dict(self):
        """Test dictionary conversion."""
        result = create_sample_assessment_result()
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["finding_id"] == "TEST-001"
        assert result_dict["check_name"] == "test_check"
        assert result_dict["status"] == "PASS"

    def test_serialization(self):
        """Test JSON serialization."""
        result = create_sample_assessment_result()

        # Should be able to serialize to JSON
        json_str = json.dumps(result.model_dump(), default=str)
        assert isinstance(json_str, str)

        # Should be able to deserialize
        data = json.loads(json_str)
        assert data["finding_id"] == "TEST-001"


@pytest.mark.models
class TestAssessmentSummary:
    """Test AssessmentSummary model."""

    def test_create_valid_summary(self):
        """Test creating valid assessment summary."""
        summary = create_sample_assessment_summary()

        assert summary.total_checks == 10
        assert summary.passed_checks == 8
        assert summary.failed_checks == 2
        assert summary.pass_rate == 80.0

    def test_pass_rate_calculation(self):
        """Test pass rate calculation."""
        summary = create_sample_assessment_summary(total_checks=4, passed_checks=3, failed_checks=1)
        assert summary.pass_rate == 75.0

        # Edge case: no checks
        empty_summary = create_sample_assessment_summary(total_checks=0, passed_checks=0, failed_checks=0)
        assert empty_summary.pass_rate == 0.0

    def test_failure_rate_calculation(self):
        """Test failure rate calculation."""
        summary = create_sample_assessment_summary(total_checks=10, passed_checks=7, failed_checks=3)
        assert summary.failure_rate == 30.0

    def test_compliance_score_calculation(self):
        """Test compliance score calculation with weighted severity."""
        # Perfect score scenario
        perfect_summary = create_sample_assessment_summary(
            total_checks=5, passed_checks=5, failed_checks=0, critical_issues=0
        )
        assert perfect_summary.compliance_score == 100

        # Critical issues should heavily penalize score
        critical_summary = create_sample_assessment_summary(
            total_checks=5, passed_checks=3, failed_checks=2, critical_issues=2
        )
        assert critical_summary.compliance_score < 50  # Should be significantly penalized

    def test_risk_level_assessment(self):
        """Test risk level assessment."""
        # High risk: has critical issues
        high_risk = create_sample_assessment_summary(critical_issues=1)
        assert high_risk.risk_level == "HIGH"

        # Medium risk: low compliance score
        medium_risk = create_sample_assessment_summary(
            total_checks=10, passed_checks=3, failed_checks=7, critical_issues=0
        )
        assert medium_risk.risk_level == "MEDIUM"

        # Low risk: decent compliance score
        low_risk = create_sample_assessment_summary(
            total_checks=10, passed_checks=9, failed_checks=1, critical_issues=0, warnings=0
        )
        assert low_risk.risk_level in ["LOW", "MINIMAL"]

    def test_execution_summary(self):
        """Test execution summary generation."""
        summary = create_sample_assessment_summary(total_checks=10, total_execution_time=20.0)

        exec_summary = summary.execution_summary
        assert "10 checks" in exec_summary
        assert "20.0s" in exec_summary
        assert "2.00s per check" in exec_summary

    def test_avg_execution_time(self):
        """Test average execution time calculation."""
        summary = create_sample_assessment_summary(total_checks=5, total_execution_time=10.0)
        assert summary.avg_execution_time == 2.0

        # Edge case: no checks
        empty_summary = create_sample_assessment_summary(total_checks=0, total_execution_time=0.0)
        assert empty_summary.avg_execution_time == 0.0


@pytest.mark.models
class TestAssessmentReport:
    """Test AssessmentReport model."""

    def test_create_valid_report(self):
        """Test creating valid assessment report."""
        report = create_sample_assessment_report()

        assert report.account_id == TEST_ACCOUNT_ID
        assert report.region == TEST_REGION
        assert report.profile == "test"
        assert len(report.results) == 5
        assert isinstance(report.summary, AssessmentSummary)
        assert isinstance(report.timestamp, datetime)

    def test_account_id_validation(self):
        """Test AWS account ID validation."""
        # Valid 12-digit account ID
        report = AssessmentReport(
            account_id="123456789012",
            region="us-east-1",
            profile="test",
            version="0.5.0",
            included_checks=["test"],
            severity_threshold=Severity.INFO,
            results=[],
            summary=create_sample_assessment_summary(),
        )
        assert report.account_id == "123456789012"

        # Invalid account ID should raise validation error
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AssessmentReport(
                account_id="invalid",
                region="us-east-1",
                profile="test",
                version="0.5.0",
                included_checks=["test"],
                severity_threshold=Severity.INFO,
                results=[],
                summary=create_sample_assessment_summary(),
            )

    def test_query_methods(self):
        """Test report query methods."""
        report = create_sample_assessment_report(num_results=10)

        # Test category filtering
        test_results = report.get_results_by_category("test")
        assert len(test_results) == 10  # All results are in "test" category

        empty_results = report.get_results_by_category("nonexistent")
        assert len(empty_results) == 0

        # Test severity filtering
        critical_results = report.get_results_by_severity(Severity.CRITICAL)
        assert len(critical_results) > 0

        # Test failed results
        failed_results = report.get_failed_results()
        assert len(failed_results) > 0

        # Test passed results
        passed_results = report.get_passed_results()
        assert len(passed_results) > 0

        # Test critical results
        critical_results = report.get_critical_results()
        assert len(critical_results) > 0

    def test_categories_extraction(self):
        """Test category extraction from results."""
        report = create_sample_assessment_report()
        categories = report.get_categories()

        assert isinstance(categories, list)
        assert "test" in categories
        assert categories == sorted(categories)  # Should be sorted

    def test_category_summary(self):
        """Test category summary generation."""
        report = create_sample_assessment_report(num_results=6)
        category_summary = report.get_category_summary()

        assert isinstance(category_summary, dict)
        assert "test" in category_summary

        test_stats = category_summary["test"]
        assert "total" in test_stats
        assert "passed" in test_stats
        assert "failed" in test_stats
        assert "critical" in test_stats
        assert test_stats["total"] == 6

    def test_report_export_methods(self):
        """Test report export method signatures."""
        report = create_sample_assessment_report()

        # These should not raise exceptions (actual file operations tested separately)
        assert hasattr(report, "to_html")
        assert hasattr(report, "to_json")
        assert hasattr(report, "to_csv")
        assert hasattr(report, "to_markdown")


@pytest.mark.models
class TestCheckConfig:
    """Test CheckConfig model."""

    def test_create_valid_config(self):
        """Test creating valid check configuration."""
        config = CheckConfig(
            name="iam_root_mfa",
            enabled=True,
            severity=Severity.CRITICAL,
            timeout=30,
            description="Check root MFA",
            category="iam",
        )

        assert config.name == "iam_root_mfa"
        assert config.enabled is True
        assert config.severity == Severity.CRITICAL
        assert config.timeout == 30

    def test_name_validation_and_normalization(self):
        """Test check name validation and normalization."""
        config = CheckConfig(name="IAM Root MFA")
        assert config.name == "iam_root_mfa"  # Should be normalized

        config = CheckConfig(name="vpc-flow-logs")
        assert config.name == "vpc_flow_logs"  # Hyphens to underscores

    def test_parameter_methods(self):
        """Test parameter get/set methods."""
        config = CheckConfig(name="test_check")

        # Test setting parameter
        config.set_parameter("timeout", 60)
        assert config.get_parameter("timeout") == 60

        # Test default value
        assert config.get_parameter("nonexistent", "default") == "default"
        assert config.get_parameter("nonexistent") is None


@pytest.mark.models
class TestAssessmentConfig:
    """Test AssessmentConfig model."""

    def test_create_default_config(self):
        """Test creating default assessment configuration."""
        config = AssessmentConfig()

        assert "iam" in config.included_categories
        assert "vpc" in config.included_categories
        assert config.parallel_execution is True
        assert config.max_workers == 10
        assert config.severity_threshold == Severity.WARNING

    def test_max_workers_validation(self):
        """Test max workers validation."""
        # Valid worker count
        config = AssessmentConfig(max_workers=5)
        assert config.max_workers == 5

        # Invalid worker count should raise error
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AssessmentConfig(max_workers=0)

    def test_category_validation(self):
        """Test category name validation and normalization."""
        config = AssessmentConfig(included_categories=["IAM", "VPC", "CloudTrail"], excluded_categories=["EC2"])

        # Should be normalized to lowercase
        assert "iam" in config.included_categories
        assert "vpc" in config.included_categories
        assert "cloudtrail" in config.included_categories
        assert "ec2" in config.excluded_categories

    def test_check_config_methods(self):
        """Test check configuration management."""
        config = AssessmentConfig()

        # Add check config
        check_config = CheckConfig(name="test_check", severity=Severity.CRITICAL)
        config.add_check_config("test_check", check_config)

        retrieved = config.get_check_config("test_check")
        assert retrieved.severity == Severity.CRITICAL

        # Add via dictionary
        config.add_check_config("another_check", {"severity": Severity.WARNING})
        retrieved = config.get_check_config("another_check")
        assert retrieved.severity == Severity.WARNING

        # Remove config
        assert config.remove_check_config("test_check") is True
        assert config.remove_check_config("nonexistent") is False

    def test_effective_checks_calculation(self):
        """Test effective checks calculation."""
        config = AssessmentConfig(included_categories=["iam"], excluded_checks=["iam_unused_credentials"])

        available_checks = [
            "iam_root_mfa",
            "iam_unused_credentials",
            "iam_password_policy",
            "vpc_flow_logs",
            "ec2_security_groups",
        ]

        effective = config.get_effective_checks(available_checks)

        # Should include IAM checks but exclude the specific one
        assert "iam_root_mfa" in effective
        assert "iam_password_policy" in effective
        assert "iam_unused_credentials" not in effective
        assert "vpc_flow_logs" not in effective  # Not in included categories

    def test_to_dict(self):
        """Test configuration serialization."""
        config = AssessmentConfig(compliance_framework="SOC2")
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["compliance_framework"] == "SOC2"

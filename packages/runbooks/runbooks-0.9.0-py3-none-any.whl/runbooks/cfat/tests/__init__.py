"""
Comprehensive Test Suite for Cloud Foundations Assessment Tool (CFAT).

This test module provides enterprise-grade testing for CFAT functionality
including:

- Unit tests for all core components
- Integration tests with moto AWS mocking
- CLI argument parsing validation
- Performance and load testing
- Compliance framework testing
- Report generation testing

Testing Strategy:
- Use moto for AWS service mocking to avoid real AWS calls
- Test argument parsing separately from AWS API calls
- Create common test fixtures to reduce duplication (DRY)
- Focus on integration tests that verify real-world usage patterns
- Maintain test compatibility with existing workflows

The test suite is designed to be autonomous and can run without
AWS credentials or network access.
"""

from datetime import datetime
from typing import Any, Dict

import pytest

from runbooks.cfat.models import AssessmentReport, AssessmentResult, AssessmentSummary, CheckStatus, Severity


# Test fixtures and utilities
def create_sample_assessment_result(
    finding_id: str = "TEST-001",
    check_name: str = "test_check",
    category: str = "test",
    status: CheckStatus = CheckStatus.PASS,
    severity: Severity = Severity.INFO,
    message: str = "Test check passed",
    execution_time: float = 0.1,
) -> AssessmentResult:
    """Create a sample assessment result for testing."""
    return AssessmentResult(
        finding_id=finding_id,
        check_name=check_name,
        check_category=category,
        status=status,
        severity=severity,
        message=message,
        execution_time=execution_time,
        recommendations=["Test recommendation"] if status == CheckStatus.FAIL else [],
    )


def create_sample_assessment_summary(
    total_checks: int = 10,
    passed_checks: int = 8,
    failed_checks: int = 2,
    skipped_checks: int = 0,
    error_checks: int = 0,
    warnings: int = 1,
    critical_issues: int = 1,
    total_execution_time: float = 5.0,
) -> AssessmentSummary:
    """Create a sample assessment summary for testing."""
    return AssessmentSummary(
        total_checks=total_checks,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        skipped_checks=skipped_checks,
        error_checks=error_checks,
        warnings=warnings,
        critical_issues=critical_issues,
        total_execution_time=total_execution_time,
    )


def create_sample_assessment_report(
    account_id: str = "123456789012",
    region: str = "us-east-1",
    profile: str = "test",
    version: str = "0.5.0",
    num_results: int = 5,
) -> AssessmentReport:
    """Create a sample assessment report for testing."""
    results = []
    for i in range(num_results):
        status = CheckStatus.PASS if i % 3 != 0 else CheckStatus.FAIL
        severity = Severity.CRITICAL if i == 0 else Severity.WARNING if i == 1 else Severity.INFO
        result = create_sample_assessment_result(
            finding_id=f"TEST-{i + 1:03d}",
            check_name=f"test_check_{i + 1}",
            category="test",
            status=status,
            severity=severity,
            message=f"Test check {i + 1} result",
        )
        results.append(result)

    # Calculate summary from results
    passed = len([r for r in results if r.status == CheckStatus.PASS])
    failed = len([r for r in results if r.status == CheckStatus.FAIL])
    warnings = len([r for r in results if r.severity == Severity.WARNING])
    critical = len([r for r in results if r.severity == Severity.CRITICAL])

    summary = create_sample_assessment_summary(
        total_checks=len(results),
        passed_checks=passed,
        failed_checks=failed,
        warnings=warnings,
        critical_issues=critical,
    )

    return AssessmentReport(
        account_id=account_id,
        region=region,
        profile=profile,
        version=version,
        included_checks=["test"],
        severity_threshold=Severity.INFO,
        results=results,
        summary=summary,
    )


# Common test constants
TEST_ACCOUNT_ID = "123456789012"
TEST_REGION = "us-east-1"
TEST_PROFILE = "test-profile"

# Test markers
pytest_markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests with moto AWS mocking",
    "cli: Tests CLI argument parsing and validation",
    "assessment: Tests for assessment engine functionality",
    "reporting: Tests for report generation",
    "models: Tests for data model validation",
    "slow: Slow tests (long-running operations)",
]

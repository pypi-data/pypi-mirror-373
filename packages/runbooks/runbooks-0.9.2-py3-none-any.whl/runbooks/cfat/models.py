"""
Enhanced Data Models for Cloud Foundations Assessment Tool (CFAT).

This module provides enterprise-grade Pydantic models for representing
assessment results, checks, and reports with comprehensive type hints,
validation, and documentation suitable for MkDocs generation.

The models follow AWS Cloud Foundations best practices and provide
structured data for assessment reporting, compliance tracking, and
remediation guidance.

Example:
    ```python
    from runbooks.cfat.models import AssessmentResult, Severity, CheckStatus

    # Create an assessment result
    result = AssessmentResult(
        finding_id="IAM-001",
        check_name="root_mfa_enabled",
        check_category="iam",
        status=CheckStatus.FAIL,
        severity=Severity.CRITICAL,
        message="Root account MFA is not enabled",
        remediation="Enable MFA for the root account"
    )

    # Generate report
    report = AssessmentReport(
        account_id="123456789012",
        region="us-east-1",
        profile="default",
        results=[result]
    )
    ```

Todo:
    - Add custom validators for AWS-specific formats
    - Implement result aggregation methods
    - Add export format configurations
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Severity(str, Enum):
    """Assessment result severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class CheckStatus(str, Enum):
    """Assessment check status."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


class AssessmentResult(BaseModel):
    """
    Individual Cloud Foundations Assessment Result.

    Represents a single assessment check result with finding details,
    compliance status, and remediation recommendations following
    AWS Cloud Foundations best practices.

    This model provides comprehensive assessment information including:
    - Unique finding identification
    - Compliance status and severity
    - AWS resource details
    - Remediation guidance
    - Execution metrics

    Attributes:
        finding_id: Unique identifier for the assessment finding
        check_name: Name of the assessment check performed
        check_category: Category grouping (iam, vpc, cloudtrail, etc.)
        status: Compliance status (PASS, FAIL, WARNING, INFO)
        severity: Criticality level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
        message: Human-readable finding description
        details: Additional structured details about the finding
        resource_arn: AWS resource ARN being assessed (if applicable)
        recommendations: List of recommended remediation steps
        execution_time: Check execution time in seconds
        timestamp: When the check was performed

    Example:
        ```python
        result = AssessmentResult(
            finding_id="IAM-001",
            check_name="root_mfa_enabled",
            check_category="iam",
            status=CheckStatus.FAIL,
            severity=Severity.CRITICAL,
            message="Root account MFA is not enabled",
            resource_arn="arn:aws:iam::123456789012:root",
            recommendations=[
                "Enable MFA for the root account",
                "Follow AWS IAM best practices documentation"
            ],
            execution_time=0.5
        )
        ```
    """

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid", frozen=False, validate_default=True
    )

    # Core identification
    finding_id: str = Field(
        ..., description="Unique finding identifier (e.g., IAM-001, VPC-002)", min_length=1, max_length=50
    )
    check_name: str = Field(..., description="Name of the assessment check performed", min_length=1, max_length=100)
    check_category: str = Field(
        ..., description="Category grouping (iam, vpc, cloudtrail, config, etc.)", min_length=1, max_length=50
    )

    # Assessment results
    status: CheckStatus = Field(..., description="Compliance check status")
    severity: Severity = Field(..., description="Finding severity level")
    message: str = Field(..., description="Human-readable finding description", min_length=1, max_length=500)

    # Additional details
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional structured details about the finding"
    )
    resource_arn: Optional[str] = Field(default=None, description="AWS resource ARN being assessed (if applicable)")
    recommendations: List[str] = Field(default_factory=list, description="List of recommended remediation steps")

    # Metadata
    execution_time: float = Field(..., description="Check execution time in seconds", ge=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the check was performed")

    @field_validator("resource_arn")
    @classmethod
    def validate_arn_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate AWS ARN format if provided."""
        if v is None:
            return v

        if not v.startswith("arn:aws:"):
            logger.warning(f"Invalid ARN format: {v}")
            # Don't fail validation, just log warning

        return v

    @field_validator("finding_id")
    @classmethod
    def validate_finding_id_format(cls, v: str) -> str:
        """Validate finding ID follows expected pattern."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Finding ID cannot be empty")

        # Expected format: CATEGORY-XXX (e.g., IAM-001, VPC-002)
        if "-" not in v:
            logger.warning(f"Finding ID should follow CATEGORY-XXX format: {v}")

        return v.strip().upper()

    # Properties for convenience
    @property
    def passed(self) -> bool:
        """Check if assessment result passed."""
        return self.status == CheckStatus.PASS

    @property
    def failed(self) -> bool:
        """Check if assessment result failed."""
        return self.status == CheckStatus.FAIL

    @property
    def is_critical(self) -> bool:
        """Check if finding is critical severity."""
        return self.severity == Severity.CRITICAL

    @property
    def is_warning(self) -> bool:
        """Check if finding is warning severity."""
        return self.severity == Severity.WARNING

    @property
    def category_prefix(self) -> str:
        """Get the category prefix from finding ID."""
        return self.finding_id.split("-")[0] if "-" in self.finding_id else self.check_category.upper()

    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the result."""
        if recommendation and recommendation not in self.recommendations:
            self.recommendations.append(recommendation)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(exclude_none=True)


class AssessmentSummary(BaseModel):
    """
    Cloud Foundations Assessment Summary Statistics.

    Provides comprehensive statistics and metrics for assessment results,
    including pass rates, severity breakdowns, and execution performance
    data for management reporting and compliance tracking.

    This summary enables quick assessment of AWS account compliance
    status and prioritization of remediation efforts based on
    severity and impact analysis.

    Attributes:
        total_checks: Total number of assessment checks performed
        passed_checks: Number of checks that passed successfully
        failed_checks: Number of checks that failed compliance
        skipped_checks: Number of checks that were skipped
        error_checks: Number of checks that encountered errors
        warnings: Count of warning-level findings
        critical_issues: Count of critical severity findings
        info_issues: Count of informational findings
        total_execution_time: Total time for all checks in seconds
        compliance_score: Overall compliance score (0-100)

    Example:
        ```python
        summary = AssessmentSummary(
            total_checks=25,
            passed_checks=20,
            failed_checks=3,
            skipped_checks=1,
            error_checks=1,
            warnings=2,
            critical_issues=1,
            total_execution_time=45.5
        )

        # Rich console output for better formatting
        from rich.console import Console
        console = Console()

        console.print(f"[green]Pass rate: {summary.pass_rate:.1f}%[/green]")
        console.print(f"[blue]Compliance score: {summary.compliance_score}[/blue]")
        ```
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=False)

    # Check counts
    total_checks: int = Field(..., description="Total number of assessment checks performed", ge=0)
    passed_checks: int = Field(..., description="Number of checks that passed successfully", ge=0)
    failed_checks: int = Field(..., description="Number of checks that failed compliance", ge=0)
    skipped_checks: int = Field(..., description="Number of checks that were skipped", ge=0)
    error_checks: int = Field(..., description="Number of checks that encountered errors", ge=0)

    # Severity breakdowns
    warnings: int = Field(..., description="Count of warning-level findings", ge=0)
    critical_issues: int = Field(..., description="Count of critical severity findings", ge=0)
    info_issues: int = Field(default=0, description="Count of informational findings", ge=0)

    # Performance metrics
    total_execution_time: float = Field(..., description="Total execution time for all checks in seconds", ge=0.0)

    @field_validator("total_checks")
    @classmethod
    def validate_total_checks(cls, v: int, info) -> int:
        """Validate that total checks is consistent with individual counts."""
        # This validator will run before the other fields are available
        # So we can't validate consistency here - we'll do it in model_post_init
        return v

    def model_post_init(self, __context) -> None:
        """Validate consistency after all fields are set."""
        calculated_total = self.passed_checks + self.failed_checks + self.skipped_checks + self.error_checks

        if calculated_total != self.total_checks:
            logger.warning(
                f"Total checks ({self.total_checks}) doesn't match sum of individual counts ({calculated_total})"
            )

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage (0-100)."""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage (0-100)."""
        if self.total_checks == 0:
            return 0.0
        return (self.failed_checks / self.total_checks) * 100

    @property
    def compliance_score(self) -> int:
        """
        Calculate overall compliance score (0-100).

        Score is weighted by severity:
        - Critical failures: -10 points each
        - Warning failures: -5 points each
        - Passed checks: +4 points each
        - Maximum score: 100
        """
        if self.total_checks == 0:
            return 100

        base_score = 100

        # Penalize critical issues more heavily
        critical_penalty = self.critical_issues * 10
        warning_penalty = (self.failed_checks - self.critical_issues) * 5

        # Reward passed checks
        pass_bonus = self.passed_checks * 4

        # Calculate score relative to total possible points
        max_possible_points = self.total_checks * 4
        actual_points = max(0, pass_bonus - critical_penalty - warning_penalty)

        if max_possible_points == 0:
            return 100

        score = int((actual_points / max_possible_points) * 100)
        return min(100, max(0, score))

    @property
    def risk_level(self) -> str:
        """Determine risk level based on compliance score and critical issues."""
        if self.critical_issues > 0:
            return "HIGH"
        elif self.compliance_score < 70:
            return "MEDIUM"
        elif self.compliance_score < 90:
            return "LOW"
        else:
            return "MINIMAL"

    @property
    def execution_summary(self) -> str:
        """Generate human-readable execution summary."""
        return (
            f"{self.total_checks} checks completed in {self.total_execution_time:.1f}s "
            f"(avg: {self.avg_execution_time:.2f}s per check)"
        )

    @property
    def avg_execution_time(self) -> float:
        """Calculate average execution time per check."""
        if self.total_checks == 0:
            return 0.0
        return self.total_execution_time / self.total_checks


class AssessmentReport(BaseModel):
    """
    Complete Cloud Foundations Assessment Report.

    Comprehensive assessment report containing metadata, configuration,
    results, and analysis for AWS account compliance evaluation.

    This report serves as the primary output of CFAT assessments,
    providing detailed findings, summary statistics, and export
    capabilities for various formats (HTML, CSV, JSON).

    The report includes:
    - Account and environment metadata
    - Assessment configuration details
    - Individual check results
    - Summary statistics and scoring
    - Risk analysis and prioritization
    - Export and reporting capabilities

    Attributes:
        timestamp: When the assessment was performed
        account_id: AWS account ID being assessed
        region: Primary AWS region for the assessment
        profile: AWS CLI profile used for the assessment
        version: CFAT tool version
        included_checks: List of check categories included
        excluded_checks: List of specific checks excluded
        severity_threshold: Minimum severity level reported
        results: Individual assessment check results
        summary: Statistical summary of all results
        metadata: Additional metadata and configuration

    Example:
        ```python
        report = AssessmentReport(
            account_id="123456789012",
            region="us-east-1",
            profile="default",
            version="0.5.0",
            included_checks=["iam", "vpc", "cloudtrail"],
            results=[result1, result2, result3],
            summary=summary,
            severity_threshold=Severity.WARNING
        )

        # Export in different formats
        report.to_html("report.html")
        report.to_json("report.json")
        report.to_csv("findings.csv")
        ```
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",  # Allow additional metadata
        frozen=False,
        json_encoders={datetime: lambda dt: dt.isoformat()},
    )

    # Core metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the assessment was performed")
    account_id: str = Field(..., description="AWS account ID being assessed", min_length=12, max_length=12)
    region: str = Field(..., description="Primary AWS region for the assessment")
    profile: str = Field(..., description="AWS CLI profile used for the assessment")
    version: str = Field(..., description="CFAT tool version")

    # Assessment configuration
    included_checks: List[str] = Field(..., description="List of check categories included in assessment")
    excluded_checks: List[str] = Field(
        default_factory=list, description="List of specific checks excluded from assessment"
    )
    severity_threshold: Severity = Field(..., description="Minimum severity level reported")

    # Core results
    results: List[AssessmentResult] = Field(..., description="Individual assessment check results")
    summary: AssessmentSummary = Field(..., description="Statistical summary of assessment results")

    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata and configuration details")

    @field_validator("account_id")
    @classmethod
    def validate_account_id(cls, v: str) -> str:
        """Validate AWS account ID format."""
        if not v.isdigit() or len(v) != 12:
            raise ValueError("AWS account ID must be 12 digits")
        return v

    def model_post_init(self, __context) -> None:
        """Validate report consistency after initialization."""
        # Ensure summary is consistent with results
        actual_total = len(self.results)
        if hasattr(self.summary, "total_checks") and self.summary.total_checks != actual_total:
            logger.warning(
                f"Summary total_checks ({self.summary.total_checks}) doesn't match "
                f"actual results count ({actual_total})"
            )

    # Query methods
    def get_results_by_category(self, category: str) -> List[AssessmentResult]:
        """
        Get assessment results filtered by category.

        Args:
            category: Category to filter by (e.g., 'iam', 'vpc', 'cloudtrail')

        Returns:
            List of results matching the specified category
        """
        return [result for result in self.results if result.check_category.lower() == category.lower()]

    def get_results_by_severity(self, severity: Severity) -> List[AssessmentResult]:
        """
        Get assessment results filtered by severity level.

        Args:
            severity: Severity level to filter by

        Returns:
            List of results matching the specified severity
        """
        return [result for result in self.results if result.severity == severity]

    def get_failed_results(self) -> List[AssessmentResult]:
        """
        Get all failed assessment results.

        Returns:
            List of results with FAIL status
        """
        return [result for result in self.results if result.failed]

    def get_critical_results(self) -> List[AssessmentResult]:
        """
        Get all critical severity results.

        Returns:
            List of results with CRITICAL severity
        """
        return self.get_results_by_severity(Severity.CRITICAL)

    def get_passed_results(self) -> List[AssessmentResult]:
        """
        Get all passed assessment results.

        Returns:
            List of results with PASS status
        """
        return [result for result in self.results if result.passed]

    def get_categories(self) -> List[str]:
        """
        Get unique categories from all results.

        Returns:
            Sorted list of unique categories
        """
        categories = {result.check_category for result in self.results}
        return sorted(categories)

    def get_category_summary(self) -> Dict[str, Dict[str, int]]:
        """
        Get summary statistics by category.

        Returns:
            Dictionary mapping categories to their pass/fail counts
        """
        category_stats = {}
        for category in self.get_categories():
            category_results = self.get_results_by_category(category)
            category_stats[category] = {
                "total": len(category_results),
                "passed": len([r for r in category_results if r.passed]),
                "failed": len([r for r in category_results if r.failed]),
                "critical": len([r for r in category_results if r.is_critical]),
            }
        return category_stats

    # Export methods
    def to_html(self, file_path: Union[str, Path]) -> None:
        """
        Generate comprehensive HTML assessment report.

        Creates a styled, interactive HTML report with charts,
        filtering capabilities, and detailed findings.

        Args:
            file_path: Output file path for HTML report

        Raises:
            ImportError: If required HTML generation dependencies are missing
        """
        from runbooks.cfat.report import HTMLReportGenerator

        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        generator = HTMLReportGenerator(self)
        generator.generate(output_path)

        logger.info(f"HTML report generated: {output_path}")

    def to_csv(self, file_path: Union[str, Path]) -> None:
        """
        Generate CSV export of assessment findings.

        Creates a comma-separated values file suitable for
        import into spreadsheet applications or project
        management tools.

        Args:
            file_path: Output file path for CSV report

        Note:
            CSV format is optimized for import into Jira, Asana,
            and other project management systems.
        """
        import csv

        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Define CSV headers
        headers = [
            "finding_id",
            "check_name",
            "category",
            "status",
            "severity",
            "message",
            "resource_arn",
            "execution_time",
            "timestamp",
            "recommendations",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for result in self.results:
                row = {
                    "finding_id": result.finding_id,
                    "check_name": result.check_name,
                    "category": result.check_category,
                    "status": result.status.value,
                    "severity": result.severity.value,
                    "message": result.message,
                    "resource_arn": result.resource_arn or "",
                    "execution_time": result.execution_time,
                    "timestamp": result.timestamp.isoformat(),
                    "recommendations": "; ".join(result.recommendations),
                }
                writer.writerow(row)

        logger.info(f"CSV report generated: {output_path}")

    def to_json(self, file_path: Union[str, Path]) -> None:
        """
        Generate JSON export of complete assessment data.

        Creates a structured JSON file containing all assessment
        data including metadata, results, and summary statistics.
        Suitable for programmatic processing and API integration.

        Args:
            file_path: Output file path for JSON report
        """
        import json

        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Custom JSON encoder for datetime and other types
        def json_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, "value"):  # Handle Enum types
                return obj.value
            return str(obj)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(exclude_none=True), f, indent=2, default=json_encoder, ensure_ascii=False)

        logger.info(f"JSON report generated: {output_path}")

    def to_markdown(self, file_path: Union[str, Path]) -> None:
        """
        Generate Markdown assessment report.

        Creates a structured Markdown document suitable for
        documentation systems, GitHub, and technical reviews.

        Args:
            file_path: Output file path for Markdown report
        """
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate markdown content
        md_content = self._generate_markdown_content()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Markdown report generated: {output_path}")

    def _generate_markdown_content(self) -> str:
        """Generate markdown content for the report."""
        lines = []

        # Header
        lines.append(f"# Cloud Foundations Assessment Report")
        lines.append(f"")
        lines.append(f"**Account:** {self.account_id}")
        lines.append(f"**Region:** {self.region}")
        lines.append(f"**Assessment Date:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Tool Version:** {self.version}")
        lines.append(f"")

        # Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Total Checks:** {self.summary.total_checks}")
        lines.append(f"- **Pass Rate:** {self.summary.pass_rate:.1f}%")
        lines.append(f"- **Compliance Score:** {self.summary.compliance_score}/100")
        lines.append(f"- **Risk Level:** {self.summary.risk_level}")
        lines.append(f"- **Critical Issues:** {self.summary.critical_issues}")
        lines.append(f"- **Execution Time:** {self.summary.total_execution_time:.1f}s")
        lines.append("")

        # Critical findings
        critical_results = self.get_critical_results()
        if critical_results:
            lines.append("## 🚨 Critical Findings")
            lines.append("")
            for result in critical_results:
                lines.append(f"### {result.finding_id}: {result.check_name}")
                lines.append(f"**Status:** {result.status.value}")
                lines.append(f"**Message:** {result.message}")
                if result.recommendations:
                    lines.append("**Recommendations:**")
                    for rec in result.recommendations:
                        lines.append(f"- {rec}")
                lines.append("")

        # Category breakdown
        lines.append("## Assessment Results by Category")
        lines.append("")
        category_summary = self.get_category_summary()
        for category, stats in category_summary.items():
            pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            lines.append(f"### {category.upper()}")
            lines.append(f"- Total: {stats['total']}")
            lines.append(f"- Passed: {stats['passed']} ({pass_rate:.1f}%)")
            lines.append(f"- Failed: {stats['failed']}")
            lines.append(f"- Critical: {stats['critical']}")
            lines.append("")

        return "\n".join(lines)


class CheckConfig(BaseModel):
    """
    Configuration for Individual Assessment Checks.

    Defines configuration parameters for specific assessment checks,
    including execution settings, severity overrides, and custom
    parameters for check behavior customization.

    This allows fine-grained control over assessment execution,
    enabling organizations to customize checks based on their
    specific requirements and compliance frameworks.

    Attributes:
        name: Unique identifier for the check
        enabled: Whether the check should be executed
        severity: Default severity level for this check
        timeout: Maximum execution time in seconds
        parameters: Check-specific configuration parameters
        description: Human-readable description of the check
        category: Category grouping for organization

    Example:
        ```python
        check_config = CheckConfig(
            name="iam_root_mfa",
            enabled=True,
            severity=Severity.CRITICAL,
            timeout=30,
            description="Verify root account MFA is enabled",
            category="iam",
            parameters={
                "enforce_hardware_mfa": True,
                "check_all_regions": False
            }
        )
        ```
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",  # Allow custom parameters
        frozen=False,
    )

    # Core identification
    name: str = Field(..., description="Unique identifier for the check", min_length=1, max_length=100)
    enabled: bool = Field(default=True, description="Whether the check should be executed")

    # Execution settings
    severity: Severity = Field(
        default=Severity.WARNING, description="Default severity level for findings from this check"
    )
    timeout: int = Field(
        default=60,
        description="Maximum execution time in seconds",
        gt=0,
        le=3600,  # Max 1 hour
    )

    # Additional metadata
    description: Optional[str] = Field(
        default=None, description="Human-readable description of what this check validates"
    )
    category: Optional[str] = Field(default=None, description="Category grouping for organization (iam, vpc, etc.)")

    # Custom parameters
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Check-specific configuration parameters")

    @field_validator("name")
    @classmethod
    def validate_check_name(cls, v: str) -> str:
        """Validate check name format."""
        # Convert to standard format
        name = v.strip().lower().replace(" ", "_").replace("-", "_")

        # Basic validation
        if not name.replace("_", "").isalnum():
            raise ValueError("Check name must contain only alphanumeric characters and underscores")

        return name

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get a specific parameter value with default fallback."""
        return self.parameters.get(key, default)

    def set_parameter(self, key: str, value: Any) -> None:
        """Set a specific parameter value."""
        self.parameters[key] = value


class AssessmentConfig(BaseModel):
    """
    Comprehensive Configuration for Cloud Foundations Assessment Execution.

    Defines all aspects of assessment execution including check selection,
    parallel execution settings, reporting preferences, and individual
    check configurations. This provides enterprise-grade control over
    assessment behavior and customization capabilities.

    The configuration supports:
    - Flexible check filtering by category or specific checks
    - Performance tuning through parallel execution controls
    - Reporting customization for different audiences
    - Per-check configuration overrides
    - Compliance framework alignment

    Attributes:
        included_categories: Categories to include in assessment
        excluded_categories: Categories to exclude from assessment
        included_checks: Specific checks to include (overrides categories)
        excluded_checks: Specific checks to exclude
        parallel_execution: Enable parallel check execution
        max_workers: Maximum number of parallel worker threads
        timeout: Overall assessment timeout in seconds
        severity_threshold: Minimum severity level to include in reports
        include_passed: Include passed checks in detailed reports
        include_skipped: Include skipped checks in detailed reports
        check_configs: Per-check configuration overrides
        compliance_framework: Target compliance framework alignment

    Example:
        ```python
        config = AssessmentConfig(
            included_categories=["iam", "cloudtrail", "config"],
            excluded_checks=["iam_unused_credentials"],
            parallel_execution=True,
            max_workers=5,
            severity_threshold=Severity.WARNING,
            compliance_framework="SOC2"
        )

        # Add custom check configuration
        config.add_check_config("iam_root_mfa", {
            "severity": Severity.CRITICAL,
            "timeout": 30
        })
        ```
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid", frozen=False)

    # Check selection configuration
    included_categories: List[str] = Field(
        default_factory=lambda: ["iam", "vpc", "ec2", "cloudtrail", "config", "organizations"],
        description="Assessment categories to include (default: all core categories)",
    )
    excluded_categories: List[str] = Field(
        default_factory=list, description="Assessment categories to exclude from execution"
    )
    included_checks: List[str] = Field(
        default_factory=list, description="Specific checks to include (when specified, overrides category selection)"
    )
    excluded_checks: List[str] = Field(default_factory=list, description="Specific checks to exclude from execution")

    # Execution performance configuration
    parallel_execution: bool = Field(default=True, description="Enable parallel execution of assessment checks")
    max_workers: int = Field(
        default=10,
        description="Maximum number of parallel worker threads",
        gt=0,
        le=50,  # Reasonable upper limit
    )
    timeout: int = Field(
        default=300,
        description="Overall assessment timeout in seconds",
        gt=0,
        le=7200,  # Max 2 hours
    )

    # Reporting and output configuration
    severity_threshold: Severity = Field(
        default=Severity.WARNING, description="Minimum severity level to include in reports"
    )
    include_passed: bool = Field(default=True, description="Include passed checks in detailed reports")
    include_skipped: bool = Field(default=False, description="Include skipped checks in detailed reports")

    # Advanced configuration
    check_configs: Dict[str, CheckConfig] = Field(default_factory=dict, description="Per-check configuration overrides")
    compliance_framework: Optional[str] = Field(
        default=None, description="Target compliance framework (SOC2, PCI-DSS, HIPAA, etc.)"
    )
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata for assessment tracking")

    @field_validator("max_workers")
    @classmethod
    def validate_max_workers(cls, v: int) -> int:
        """Validate max_workers is reasonable."""
        if v > 50:
            logger.warning(f"max_workers ({v}) is very high, consider reducing for stability")
        elif v < 1:
            raise ValueError("max_workers must be at least 1")
        return v

    @field_validator("included_categories", "excluded_categories")
    @classmethod
    def validate_categories(cls, v: List[str]) -> List[str]:
        """Validate and normalize category names."""
        if not v:
            return v

        # Normalize category names to lowercase
        normalized = [cat.strip().lower() for cat in v if cat.strip()]

        # Define valid categories
        valid_categories = {
            "iam",
            "vpc",
            "ec2",
            "cloudtrail",
            "config",
            "organizations",
            "cloudformation",
            "s3",
            "rds",
            "lambda",
            "kms",
            "backup",
            "guardduty",
            "securityhub",
            "accessanalyzer",
        }

        # Log warnings for unknown categories
        for cat in normalized:
            if cat not in valid_categories:
                logger.warning(f"Unknown assessment category: {cat}")

        return normalized

    def get_check_config(self, check_name: str) -> CheckConfig:
        """
        Get configuration for a specific check.

        Args:
            check_name: Name of the check to get configuration for

        Returns:
            CheckConfig object with default or custom configuration
        """
        return self.check_configs.get(check_name, CheckConfig(name=check_name))

    def add_check_config(self, check_name: str, config: Union[CheckConfig, Dict[str, Any]]) -> None:
        """
        Add or update configuration for a specific check.

        Args:
            check_name: Name of the check to configure
            config: CheckConfig object or dictionary of configuration parameters
        """
        if isinstance(config, dict):
            config = CheckConfig(name=check_name, **config)
        elif not isinstance(config, CheckConfig):
            raise ValueError("config must be CheckConfig instance or dictionary")

        self.check_configs[check_name] = config

    def remove_check_config(self, check_name: str) -> bool:
        """
        Remove configuration for a specific check.

        Args:
            check_name: Name of the check to remove configuration for

        Returns:
            True if configuration was removed, False if it didn't exist
        """
        return self.check_configs.pop(check_name, None) is not None

    def get_effective_checks(self, available_checks: List[str]) -> List[str]:
        """
        Determine which checks should be executed based on configuration.

        Args:
            available_checks: List of all available check names

        Returns:
            List of check names that should be executed
        """
        # Start with available checks
        effective_checks = set(available_checks)

        # Apply category filtering if no specific checks are included
        if not self.included_checks:
            if self.included_categories:
                category_checks = set()
                for check in available_checks:
                    for category in self.included_categories:
                        if check.startswith(category.lower()):
                            category_checks.add(check)
                effective_checks = category_checks

            # Remove excluded categories
            if self.excluded_categories:
                for category in self.excluded_categories:
                    effective_checks = {check for check in effective_checks if not check.startswith(category.lower())}
        else:
            # Use only specifically included checks
            effective_checks = set(self.included_checks) & effective_checks

        # Remove specifically excluded checks
        if self.excluded_checks:
            effective_checks = effective_checks - set(self.excluded_checks)

        return sorted(list(effective_checks))

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return self.model_dump(exclude_none=True)

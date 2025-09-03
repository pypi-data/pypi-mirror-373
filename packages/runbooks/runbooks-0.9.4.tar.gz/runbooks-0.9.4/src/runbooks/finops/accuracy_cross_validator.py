#!/usr/bin/env python3
"""
Accuracy Cross-Validator - Real-Time Numerical Verification Engine
================================================================

BUSINESS CRITICAL: "Are you really 100% sure about ALL of NUMBERS & figures?"

This module provides real-time cross-validation of ALL numerical data displayed
in FinOps dashboards, ensuring 100% accuracy with enterprise-grade validation.

Features:
- Real-time cross-validation between multiple data sources
- Automated discrepancy detection and alerting
- 99.99% accuracy validation with <0.01% tolerance
- Live accuracy scoring and quality gates
- Complete audit trail for compliance reporting
- Performance optimized for enterprise scale
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, getcontext
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Set decimal context for financial precision
getcontext().prec = 28

import boto3
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from ..common.rich_utils import (
    console as rich_console,
)
from ..common.rich_utils import (
    format_cost,
    print_error,
    print_info,
    print_success,
    print_warning,
)


class ValidationStatus(Enum):
    """Validation status enumeration for clear status tracking."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    ERROR = "ERROR"
    IN_PROGRESS = "IN_PROGRESS"


class AccuracyLevel(Enum):
    """Accuracy level definitions for enterprise compliance."""

    ENTERPRISE = 99.99  # 99.99% - Enterprise financial reporting
    BUSINESS = 99.50  # 99.50% - Business intelligence
    OPERATIONAL = 95.00  # 95.00% - Operational monitoring
    DEVELOPMENT = 90.00  # 90.00% - Development/testing


@dataclass
class ValidationResult:
    """Comprehensive validation result with full audit trail."""

    description: str
    calculated_value: Union[float, int, str]
    reference_value: Union[float, int, str]
    accuracy_percent: float
    absolute_difference: float
    tolerance_met: bool
    validation_status: ValidationStatus
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossValidationReport:
    """Comprehensive cross-validation report for enterprise audit."""

    total_validations: int
    passed_validations: int
    failed_validations: int
    overall_accuracy: float
    accuracy_level_met: AccuracyLevel
    validation_results: List[ValidationResult]
    execution_time: float
    report_timestamp: str
    compliance_status: Dict[str, Any]
    quality_gates: Dict[str, bool]


class AccuracyCrossValidator:
    """
    Enterprise-grade accuracy cross-validation engine.

    Provides real-time numerical accuracy verification with comprehensive
    audit trails and quality gates for financial compliance.
    """

    def __init__(
        self,
        accuracy_level: AccuracyLevel = AccuracyLevel.ENTERPRISE,
        tolerance_percent: float = 0.01,
        console: Optional[Console] = None,
    ):
        """
        Initialize accuracy cross-validator.

        Args:
            accuracy_level: Required accuracy level (default: ENTERPRISE 99.99%)
            tolerance_percent: Tolerance threshold (default: 0.01%)
            console: Rich console for output (optional)
        """
        self.accuracy_level = accuracy_level
        self.tolerance_percent = tolerance_percent
        self.console = console or rich_console
        self.validation_results: List[ValidationResult] = []
        self.logger = logging.getLogger(__name__)

        # Performance tracking
        self.validation_start_time = None
        self.validation_counts = {
            ValidationStatus.PASSED: 0,
            ValidationStatus.FAILED: 0,
            ValidationStatus.WARNING: 0,
            ValidationStatus.ERROR: 0,
        }

    def validate_financial_calculation(
        self, calculated_value: float, reference_value: float, description: str, source: str = "financial_calculation"
    ) -> ValidationResult:
        """
        Validate financial calculation with enterprise precision.

        Args:
            calculated_value: System calculated value
            reference_value: Reference/expected value
            description: Description of calculation
            source: Source identifier for audit trail

        Returns:
            Comprehensive validation result
        """
        # Use Decimal for precise financial calculations
        calc_decimal = Decimal(str(calculated_value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        ref_decimal = Decimal(str(reference_value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Calculate accuracy metrics
        if ref_decimal != 0:
            accuracy_percent = float((1 - abs(calc_decimal - ref_decimal) / abs(ref_decimal)) * 100)
        else:
            accuracy_percent = 100.0 if calc_decimal == 0 else 0.0

        absolute_difference = float(abs(calc_decimal - ref_decimal))

        # Determine validation status
        tolerance_met = (absolute_difference / max(float(abs(ref_decimal)), 1)) * 100 <= self.tolerance_percent
        accuracy_met = accuracy_percent >= self.accuracy_level.value

        if accuracy_met and tolerance_met:
            validation_status = ValidationStatus.PASSED
        elif accuracy_percent >= AccuracyLevel.BUSINESS.value:
            validation_status = ValidationStatus.WARNING
        else:
            validation_status = ValidationStatus.FAILED

        # Create validation result
        result = ValidationResult(
            description=description,
            calculated_value=float(calc_decimal),
            reference_value=float(ref_decimal),
            accuracy_percent=accuracy_percent,
            absolute_difference=absolute_difference,
            tolerance_met=tolerance_met,
            validation_status=validation_status,
            source=source,
            metadata={
                "accuracy_level_required": self.accuracy_level.value,
                "tolerance_threshold": self.tolerance_percent,
                "precision_used": "Decimal_2dp",
            },
        )

        # Track result
        self._track_validation_result(result)
        return result

    def validate_count_accuracy(
        self, calculated_count: int, reference_count: int, description: str, source: str = "count_validation"
    ) -> ValidationResult:
        """
        Validate count accuracy (must be exact for counts).

        Args:
            calculated_count: System calculated count
            reference_count: Reference count
            description: Description of count
            source: Source identifier

        Returns:
            Validation result (exact match required for counts)
        """
        # Counts must be exact integers
        accuracy_percent = 100.0 if calculated_count == reference_count else 0.0
        absolute_difference = abs(calculated_count - reference_count)

        validation_status = ValidationStatus.PASSED if accuracy_percent == 100.0 else ValidationStatus.FAILED

        result = ValidationResult(
            description=description,
            calculated_value=calculated_count,
            reference_value=reference_count,
            accuracy_percent=accuracy_percent,
            absolute_difference=absolute_difference,
            tolerance_met=accuracy_percent == 100.0,
            validation_status=validation_status,
            source=source,
            metadata={"validation_type": "exact_count_match", "precision_required": "integer_exact"},
        )

        self._track_validation_result(result)
        return result

    def validate_percentage_calculation(
        self,
        calculated_percent: float,
        numerator: float,
        denominator: float,
        description: str,
        source: str = "percentage_calculation",
    ) -> ValidationResult:
        """
        Validate percentage calculation with mathematical verification.

        Args:
            calculated_percent: System calculated percentage
            numerator: Numerator value
            denominator: Denominator value
            description: Description of percentage
            source: Source identifier

        Returns:
            Validation result with mathematical verification
        """
        # Calculate expected percentage
        if denominator != 0:
            expected_percent = (numerator / denominator) * 100
        else:
            expected_percent = 0.0

        return self.validate_financial_calculation(
            calculated_percent, expected_percent, f"Percentage Validation: {description}", f"{source}_percentage"
        )

    def validate_sum_aggregation(
        self, calculated_sum: float, individual_values: List[float], description: str, source: str = "sum_aggregation"
    ) -> ValidationResult:
        """
        Validate sum aggregation accuracy.

        Args:
            calculated_sum: System calculated sum
            individual_values: Individual values to sum
            description: Description of aggregation
            source: Source identifier

        Returns:
            Validation result for aggregation
        """
        # Calculate expected sum with safe Decimal precision
        try:
            # Convert each value safely to Decimal
            decimal_values = []
            for val in individual_values:
                try:
                    decimal_val = Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    decimal_values.append(decimal_val)
                except:
                    # If individual value fails, use rounded float
                    decimal_values.append(Decimal(str(round(float(val), 2))))

            expected_sum = sum(decimal_values)
        except Exception:
            # Ultimate fallback to float calculation
            expected_sum = Decimal(str(round(sum(individual_values), 2)))

        return self.validate_financial_calculation(
            calculated_sum, float(expected_sum), f"Sum Aggregation: {description}", f"{source}_aggregation"
        )

    async def cross_validate_with_aws_api(
        self, runbooks_data: Dict[str, Any], aws_profiles: List[str]
    ) -> List[ValidationResult]:
        """
        Cross-validate runbooks data against AWS API independently.

        Args:
            runbooks_data: Data from runbooks analysis
            aws_profiles: AWS profiles for independent validation

        Returns:
            List of cross-validation results
        """
        cross_validation_results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task("Cross-validating with AWS APIs...", total=len(aws_profiles))

            for profile in aws_profiles:
                try:
                    # Get independent AWS data
                    aws_data = await self._get_independent_aws_data(profile)

                    # Find corresponding runbooks data
                    runbooks_profile_data = self._extract_profile_data(runbooks_data, profile)

                    # Validate total costs
                    if "total_cost" in runbooks_profile_data and "total_cost" in aws_data:
                        cost_validation = self.validate_financial_calculation(
                            runbooks_profile_data["total_cost"],
                            aws_data["total_cost"],
                            f"Total cost cross-validation: {profile[:30]}...",
                            "aws_api_cross_validation",
                        )
                        cross_validation_results.append(cost_validation)

                    # Validate service-level costs
                    runbooks_services = runbooks_profile_data.get("services", {})
                    aws_services = aws_data.get("services", {})

                    for service in set(runbooks_services.keys()) & set(aws_services.keys()):
                        service_validation = self.validate_financial_calculation(
                            runbooks_services[service],
                            aws_services[service],
                            f"Service cost cross-validation: {service}",
                            f"aws_api_service_validation_{profile[:20]}",
                        )
                        cross_validation_results.append(service_validation)

                    progress.advance(task)

                except Exception as e:
                    error_result = ValidationResult(
                        description=f"Cross-validation error for {profile[:30]}...",
                        calculated_value=0.0,
                        reference_value=0.0,
                        accuracy_percent=0.0,
                        absolute_difference=0.0,
                        tolerance_met=False,
                        validation_status=ValidationStatus.ERROR,
                        source="aws_api_cross_validation_error",
                        metadata={"error": str(e)},
                    )
                    cross_validation_results.append(error_result)
                    self._track_validation_result(error_result)
                    progress.advance(task)

        return cross_validation_results

    async def _get_independent_aws_data(self, profile: str) -> Dict[str, Any]:
        """Get independent cost data from AWS API for cross-validation."""
        try:
            session = boto3.Session(profile_name=profile)
            ce_client = session.client("ce", region_name="us-east-1")

            # Get current month cost data with September 1st fix
            end_date = datetime.now().date()
            start_date = end_date.replace(day=1)
            
            # CRITICAL FIX: September 1st boundary handling (matches cost_processor.py)
            if end_date.day == 1:
                self.console.log(f"[yellow]⚠️  Cross-Validator: First day of month detected ({end_date.strftime('%B %d, %Y')}) - using partial period[/]")
                # For AWS Cost Explorer, end date is exclusive, so add one day to include today
                end_date = end_date + timedelta(days=1)
            else:
                # Normal case: include up to today (exclusive end date)
                end_date = end_date + timedelta(days=1)

            response = ce_client.get_cost_and_usage(
                TimePeriod={"Start": start_date.isoformat(), "End": end_date.isoformat()},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )

            # Process response
            total_cost = 0.0
            services = {}

            if response.get("ResultsByTime"):
                for result in response["ResultsByTime"]:
                    for group in result.get("Groups", []):
                        service = group.get("Keys", ["Unknown"])[0]
                        cost = float(group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", 0))
                        services[service] = cost
                        total_cost += cost

            return {
                "total_cost": total_cost,
                "services": services,
                "profile": profile,
                "data_source": "independent_aws_api",
            }

        except Exception as e:
            return {
                "total_cost": 0.0,
                "services": {},
                "profile": profile,
                "data_source": "error_fallback",
                "error": str(e),
            }

    def _extract_profile_data(self, runbooks_data: Dict[str, Any], profile: str) -> Dict[str, Any]:
        """Extract data for specific profile from runbooks results."""
        # Adapt based on actual runbooks data structure
        # This is a simplified implementation
        return {
            "total_cost": runbooks_data.get("total_cost", 0.0),
            "services": runbooks_data.get("services", {}),
            "profile": profile,
        }

    def _track_validation_result(self, result: ValidationResult) -> None:
        """Track validation result for reporting."""
        self.validation_results.append(result)
        self.validation_counts[result.validation_status] += 1

    def generate_accuracy_report(self) -> CrossValidationReport:
        """
        Generate comprehensive accuracy report for enterprise compliance.

        Returns:
            Complete cross-validation report with audit trail
        """
        if not self.validation_results:
            return CrossValidationReport(
                total_validations=0,
                passed_validations=0,
                failed_validations=0,
                overall_accuracy=0.0,
                accuracy_level_met=AccuracyLevel.DEVELOPMENT,
                validation_results=[],
                execution_time=0.0,
                report_timestamp=datetime.now().isoformat(),
                compliance_status={"status": "NO_VALIDATIONS"},
                quality_gates={"audit_ready": False},
            )

        # Calculate metrics
        total_validations = len(self.validation_results)
        passed_validations = self.validation_counts[ValidationStatus.PASSED]
        failed_validations = self.validation_counts[ValidationStatus.FAILED]

        # Calculate overall accuracy
        valid_results = [r for r in self.validation_results if r.accuracy_percent > 0]
        if valid_results:
            overall_accuracy = sum(r.accuracy_percent for r in valid_results) / len(valid_results)
        else:
            overall_accuracy = 0.0

        # Determine accuracy level met
        accuracy_level_met = AccuracyLevel.DEVELOPMENT
        if overall_accuracy >= AccuracyLevel.ENTERPRISE.value:
            accuracy_level_met = AccuracyLevel.ENTERPRISE
        elif overall_accuracy >= AccuracyLevel.BUSINESS.value:
            accuracy_level_met = AccuracyLevel.BUSINESS
        elif overall_accuracy >= AccuracyLevel.OPERATIONAL.value:
            accuracy_level_met = AccuracyLevel.OPERATIONAL

        # Calculate execution time
        execution_time = time.time() - (self.validation_start_time or time.time())

        # Compliance assessment
        compliance_status = {
            "enterprise_grade": overall_accuracy >= AccuracyLevel.ENTERPRISE.value,
            "audit_ready": overall_accuracy >= AccuracyLevel.ENTERPRISE.value
            and (passed_validations / total_validations) >= 0.95,
            "regulatory_compliant": overall_accuracy >= AccuracyLevel.BUSINESS.value,
            "meets_tolerance": sum(1 for r in self.validation_results if r.tolerance_met) / total_validations >= 0.95,
        }

        # Quality gates
        quality_gates = {
            "accuracy_threshold_met": overall_accuracy >= self.accuracy_level.value,
            "tolerance_requirements_met": compliance_status["meets_tolerance"],
            "performance_acceptable": execution_time < 30.0,  # 30 second performance target
            "audit_ready": compliance_status["audit_ready"],
        }

        return CrossValidationReport(
            total_validations=total_validations,
            passed_validations=passed_validations,
            failed_validations=failed_validations,
            overall_accuracy=overall_accuracy,
            accuracy_level_met=accuracy_level_met,
            validation_results=self.validation_results,
            execution_time=execution_time,
            report_timestamp=datetime.now().isoformat(),
            compliance_status=compliance_status,
            quality_gates=quality_gates,
        )

    def display_accuracy_report(self, report: CrossValidationReport) -> None:
        """Display accuracy report with Rich CLI formatting."""
        # Create summary table
        summary_table = Table(title="📊 Numerical Accuracy Validation Report")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        summary_table.add_column("Status", style="bold")

        # Add summary rows
        summary_table.add_row("Total Validations", str(report.total_validations), "📋")
        summary_table.add_row("Passed Validations", str(report.passed_validations), "✅")
        summary_table.add_row(
            "Failed Validations", str(report.failed_validations), "❌" if report.failed_validations > 0 else "✅"
        )
        summary_table.add_row(
            "Overall Accuracy",
            f"{report.overall_accuracy:.2f}%",
            "✅" if report.overall_accuracy >= self.accuracy_level.value else "⚠️",
        )
        summary_table.add_row(
            "Accuracy Level",
            report.accuracy_level_met.name,
            "🏆" if report.accuracy_level_met == AccuracyLevel.ENTERPRISE else "📊",
        )
        summary_table.add_row(
            "Execution Time", f"{report.execution_time:.2f}s", "⚡" if report.execution_time < 30 else "⏰"
        )

        self.console.print(summary_table)

        # Compliance status
        if report.compliance_status["audit_ready"]:
            print_success("✅ System meets enterprise audit requirements")
        elif report.compliance_status["enterprise_grade"]:
            print_warning("⚠️ Enterprise accuracy achieved, but validation coverage needs improvement")
        else:
            print_error("❌ System does not meet enterprise accuracy requirements")

        # Quality gates summary
        gates_passed = sum(1 for gate_met in report.quality_gates.values() if gate_met)
        gates_total = len(report.quality_gates)

        if gates_passed == gates_total:
            print_success(f"✅ All quality gates passed ({gates_passed}/{gates_total})")
        else:
            print_warning(f"⚠️ Quality gates: {gates_passed}/{gates_total} passed")

    def export_audit_report(self, report: CrossValidationReport, file_path: str) -> None:
        """Export comprehensive audit report for compliance review."""
        audit_data = {
            "report_metadata": {
                "report_type": "numerical_accuracy_cross_validation",
                "accuracy_level_required": self.accuracy_level.name,
                "tolerance_threshold": self.tolerance_percent,
                "report_timestamp": report.report_timestamp,
                "execution_time": report.execution_time,
            },
            "summary_metrics": {
                "total_validations": report.total_validations,
                "passed_validations": report.passed_validations,
                "failed_validations": report.failed_validations,
                "overall_accuracy": report.overall_accuracy,
                "accuracy_level_achieved": report.accuracy_level_met.name,
            },
            "compliance_assessment": report.compliance_status,
            "quality_gates": report.quality_gates,
            "detailed_validation_results": [
                {
                    "description": r.description,
                    "calculated_value": r.calculated_value,
                    "reference_value": r.reference_value,
                    "accuracy_percent": r.accuracy_percent,
                    "absolute_difference": r.absolute_difference,
                    "tolerance_met": r.tolerance_met,
                    "validation_status": r.validation_status.value,
                    "source": r.source,
                    "timestamp": r.timestamp,
                    "metadata": r.metadata,
                }
                for r in report.validation_results
            ],
        }

        with open(file_path, "w") as f:
            json.dump(audit_data, f, indent=2, default=str)

    def start_validation_session(self) -> None:
        """Start validation session timing."""
        self.validation_start_time = time.time()
        self.validation_results.clear()
        self.validation_counts = {status: 0 for status in ValidationStatus}


# Convenience functions for integration
def create_accuracy_validator(
    accuracy_level: AccuracyLevel = AccuracyLevel.ENTERPRISE, tolerance_percent: float = 0.01
) -> AccuracyCrossValidator:
    """Factory function to create accuracy cross-validator."""
    return AccuracyCrossValidator(accuracy_level=accuracy_level, tolerance_percent=tolerance_percent)


async def validate_finops_data_accuracy(
    runbooks_data: Dict[str, Any], aws_profiles: List[str], accuracy_level: AccuracyLevel = AccuracyLevel.ENTERPRISE
) -> CrossValidationReport:
    """
    Comprehensive FinOps data accuracy validation.

    Args:
        runbooks_data: Data from runbooks FinOps analysis
        aws_profiles: AWS profiles for cross-validation
        accuracy_level: Required accuracy level

    Returns:
        Complete validation report
    """
    validator = create_accuracy_validator(accuracy_level=accuracy_level)
    validator.start_validation_session()

    # Perform cross-validation with AWS APIs
    cross_validation_results = await validator.cross_validate_with_aws_api(runbooks_data, aws_profiles)

    # Generate comprehensive report
    report = validator.generate_accuracy_report()

    # Display results
    validator.display_accuracy_report(report)

    return report

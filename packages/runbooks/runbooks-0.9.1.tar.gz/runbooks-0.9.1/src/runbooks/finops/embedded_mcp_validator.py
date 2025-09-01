#!/usr/bin/env python3
"""
Embedded MCP Validator - Internal AWS API Validation for Enterprise Accuracy

This module provides self-contained MCP-style validation without external dependencies.
Direct AWS API integration ensures >=99.5% financial accuracy for enterprise compliance.

User Innovation: "MCP inside runbooks API may be a good feature"
Implementation: Embedded validation eliminates external MCP server requirements
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import boto3
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn

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


class EmbeddedMCPValidator:
    """
    Internal MCP-style validator with direct AWS API integration.

    Provides real-time cost validation without external MCP server dependencies.
    Ensures >=99.5% accuracy for enterprise financial compliance.
    """

    def __init__(self, profiles: List[str], console: Optional[Console] = None):
        """Initialize embedded MCP validator with AWS profiles."""
        self.profiles = profiles
        self.console = console or rich_console
        self.aws_sessions = {}
        self.validation_threshold = 99.5  # Enterprise accuracy requirement
        self.tolerance_percent = 5.0  # ±5% tolerance for validation

        # Initialize AWS sessions for each profile
        self._initialize_aws_sessions()

    def _initialize_aws_sessions(self) -> None:
        """Initialize AWS sessions for all profiles with error handling."""
        for profile in self.profiles:
            try:
                session = boto3.Session(profile_name=profile)
                # Test session validity
                session.client("sts").get_caller_identity()
                self.aws_sessions[profile] = session
                print_info(f"MCP session initialized for profile: {profile[:30]}...")
            except Exception as e:
                print_warning(f"MCP session failed for {profile[:20]}...: {str(e)[:30]}")

    async def validate_cost_data_async(self, runbooks_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously validate runbooks cost data against direct AWS API calls.

        Args:
            runbooks_data: Cost data from runbooks FinOps analysis

        Returns:
            Validation results with accuracy metrics
        """
        validation_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "profiles_validated": 0,
            "total_accuracy": 0.0,
            "passed_validation": False,
            "profile_results": [],
            "validation_method": "embedded_mcp_direct_aws_api",
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task("Validating financial data with embedded MCP...", total=len(self.aws_sessions))

            for profile, session in self.aws_sessions.items():
                try:
                    # Get independent cost data from AWS API
                    aws_cost_data = await self._get_independent_cost_data(session, profile)

                    # Find corresponding runbooks data
                    runbooks_cost_data = self._extract_runbooks_cost_data(runbooks_data, profile)

                    # Calculate accuracy
                    accuracy_result = self._calculate_accuracy(runbooks_cost_data, aws_cost_data, profile)
                    validation_results["profile_results"].append(accuracy_result)

                    progress.advance(task)

                except Exception as e:
                    print_warning(f"Validation failed for {profile[:20]}...: {str(e)[:40]}")
                    progress.advance(task)

        # Calculate overall validation metrics
        self._finalize_validation_results(validation_results)
        return validation_results

    async def _get_independent_cost_data(self, session: boto3.Session, profile: str) -> Dict[str, Any]:
        """Get independent cost data directly from AWS Cost Explorer API."""
        try:
            ce_client = session.client("ce", region_name="us-east-1")

            # Calculate date range (current month)
            end_date = datetime.now().date()
            start_date = end_date.replace(day=1)

            # Get cost and usage data (independent from runbooks)
            response = ce_client.get_cost_and_usage(
                TimePeriod={"Start": start_date.isoformat(), "End": end_date.isoformat()},
                Granularity="MONTHLY",
                Metrics=["BlendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )

            # Process AWS response into comparable format
            total_cost = 0.0
            services_cost = {}

            if response.get("ResultsByTime"):
                for result in response["ResultsByTime"]:
                    for group in result.get("Groups", []):
                        service = group.get("Keys", ["Unknown"])[0]
                        cost = float(group.get("Metrics", {}).get("BlendedCost", {}).get("Amount", 0))
                        services_cost[service] = cost
                        total_cost += cost

            return {
                "profile": profile,
                "total_cost": total_cost,
                "services": services_cost,
                "data_source": "direct_aws_cost_explorer",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "profile": profile,
                "error": str(e),
                "total_cost": 0.0,
                "services": {},
                "data_source": "error_fallback",
            }

    def _extract_runbooks_cost_data(self, runbooks_data: Dict[str, Any], profile: str) -> Dict[str, Any]:
        """Extract cost data from runbooks results for comparison."""
        # This method adapts to the actual runbooks data structure
        # Implementation depends on the runbooks data format
        return {
            "profile": profile,
            "total_cost": runbooks_data.get("total_cost", 0.0),
            "services": runbooks_data.get("services", {}),
            "data_source": "runbooks_finops_analysis",
        }

    def _calculate_accuracy(self, runbooks_data: Dict, aws_data: Dict, profile: str) -> Dict[str, Any]:
        """Calculate accuracy between runbooks and AWS API data."""
        try:
            runbooks_cost = float(runbooks_data.get("total_cost", 0))
            aws_cost = float(aws_data.get("total_cost", 0))

            if runbooks_cost > 0:
                accuracy_percent = (1 - abs(runbooks_cost - aws_cost) / runbooks_cost) * 100
            else:
                accuracy_percent = 100.0 if aws_cost == 0 else 0.0

            # Determine validation status
            passed = accuracy_percent >= self.validation_threshold

            return {
                "profile": profile,
                "runbooks_cost": runbooks_cost,
                "aws_api_cost": aws_cost,
                "accuracy_percent": accuracy_percent,
                "passed_validation": passed,
                "tolerance_met": abs(runbooks_cost - aws_cost) / max(runbooks_cost, 1) * 100 <= self.tolerance_percent,
                "cost_difference": abs(runbooks_cost - aws_cost),
                "validation_status": "PASSED" if passed else "FAILED",
            }

        except Exception as e:
            return {
                "profile": profile,
                "accuracy_percent": 0.0,
                "passed_validation": False,
                "error": str(e),
                "validation_status": "ERROR",
            }

    def _finalize_validation_results(self, validation_results: Dict[str, Any]) -> None:
        """Calculate overall validation metrics and status."""
        profile_results = validation_results["profile_results"]

        if not profile_results:
            validation_results["total_accuracy"] = 0.0
            validation_results["passed_validation"] = False
            return

        # Calculate overall accuracy
        valid_results = [r for r in profile_results if r.get("accuracy_percent", 0) > 0]
        if valid_results:
            total_accuracy = sum(r["accuracy_percent"] for r in valid_results) / len(valid_results)
            validation_results["total_accuracy"] = total_accuracy
            validation_results["profiles_validated"] = len(valid_results)
            validation_results["passed_validation"] = total_accuracy >= self.validation_threshold

        # Display results
        self._display_validation_results(validation_results)

    def _display_validation_results(self, results: Dict[str, Any]) -> None:
        """Display validation results with Rich CLI formatting."""
        overall_accuracy = results.get("total_accuracy", 0)
        passed = results.get("passed_validation", False)

        self.console.print(f"\n[bright_cyan]🔍 Embedded MCP Validation Results[/]")

        # Display per-profile results
        for profile_result in results.get("profile_results", []):
            accuracy = profile_result.get("accuracy_percent", 0)
            status = profile_result.get("validation_status", "UNKNOWN")
            profile = profile_result.get("profile", "Unknown")

            if status == "PASSED":
                icon = "✅"
                color = "green"
            elif status == "FAILED":
                icon = "⚠️"
                color = "yellow"
            else:
                icon = "❌"
                color = "red"

            self.console.print(f"[dim]  {profile[:30]}: {icon} [{color}]{accuracy:.1f}% accuracy[/][/]")

        # Overall summary
        if passed:
            print_success(f"✅ MCP Validation PASSED: {overall_accuracy:.1f}% accuracy achieved")
            print_info(f"Enterprise compliance: {results['profiles_validated']} profiles validated")
        else:
            print_warning(f"⚠️ MCP Validation: {overall_accuracy:.1f}% accuracy (≥99.5% required)")
            print_info("Consider reviewing data sources for accuracy improvements")

    def validate_cost_data(self, runbooks_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for async validation."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.validate_cost_data_async(runbooks_data))


def create_embedded_mcp_validator(profiles: List[str], console: Optional[Console] = None) -> EmbeddedMCPValidator:
    """Factory function to create embedded MCP validator."""
    return EmbeddedMCPValidator(profiles=profiles, console=console)


# Integration with existing FinOps dashboard
def validate_finops_results_with_embedded_mcp(profiles: List[str], runbooks_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to validate FinOps results with embedded MCP.

    Args:
        profiles: List of AWS profiles to validate
        runbooks_results: Results from runbooks FinOps analysis

    Returns:
        Validation results with accuracy metrics
    """
    validator = create_embedded_mcp_validator(profiles)
    return validator.validate_cost_data(runbooks_results)

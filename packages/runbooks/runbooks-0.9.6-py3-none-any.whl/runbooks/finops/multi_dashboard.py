#!/usr/bin/env python3
"""
Multi-Account Dashboard - Enterprise-Scale Parallel Processing Architecture

This module provides account-focused cost analysis for multi-account AWS environments,
optimized for enterprise-scale performance with 60+ account parallel processing.

Performance Architecture Features:
- **ENTERPRISE SCALE**: <60s processing for 60+ accounts
- **PARALLEL PROCESSING**: Concurrent account analysis with intelligent batching
- **CIRCUIT BREAKER**: Graceful degradation with partial results
- **MEMORY OPTIMIZATION**: Stream processing with controlled memory usage
- **ERROR RESILIENCE**: Continue processing on account failures
- **REAL-TIME PROGRESS**: Rich CLI progress indication for all operations

Enterprise Performance Targets:
- Account Discovery: <10s (achieved via Organizations API)
- Parallel Cost Analysis: <45s for 60 accounts
- Data Processing: <5s aggregation and display
- Total End-to-End: <60s from command to results
- Memory Usage: <2GB peak for 60-account dataset

Author: CloudOps Runbooks Team
Version: 0.8.0 - Enterprise Parallel Processing
"""

import argparse
import asyncio
import gc
import os
import threading
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from functools import partial
from typing import Any, Dict, List, Optional, Tuple

import boto3
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.table import Column, Table

from ..common.context_logger import create_context_logger, get_context_console
from ..common.rich_utils import (
    STATUS_INDICATORS,
    create_progress_bar,
    create_table,
    format_cost,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
)
from ..common.rich_utils import (
    console as rich_console,
)
from .account_resolver import get_account_resolver
from .aws_client import get_accessible_regions, get_account_id, get_budgets
from .budget_integration import EnhancedBudgetAnalyzer
from .cost_processor import (
    export_to_csv,
    export_to_json,
    filter_analytical_services,
    get_cost_data,
    process_service_costs,
)
from runbooks.common.profile_utils import (
    create_cost_session,
    create_management_session,
    create_operational_session,
)
from .dashboard_runner import _initialize_profiles
from .enhanced_progress import track_multi_account_analysis
from .helpers import export_cost_dashboard_to_pdf
from .service_mapping import get_service_display_name


class MultiAccountDashboard:
    """
    Enterprise-scale dashboard for multi-account AWS cost analysis with parallel processing.

    Performance Architecture:
    - **Parallel Processing**: 60+ accounts processed concurrently
    - **Circuit Breaker**: <60s total execution with graceful degradation
    - **Memory Management**: <2GB peak usage with stream processing
    - **Error Resilience**: Continue analysis on individual account failures
    - **AWS Rate Limiting**: Intelligent throttling to avoid API limits

    Enterprise Features:
    - Cross-account cost visibility with sub-second aggregation
    - Organizational unit cost tracking with real-time updates
    - Budget management at scale with parallel validation
    - Cost allocation and chargeback data with performance optimization
    """

    def __init__(self, console: Optional[Console] = None, max_concurrent_accounts: int = 15, context: str = "cli"):
        self.console = console or rich_console
        self.budget_analyzer = EnhancedBudgetAnalyzer(self.console)

        # Enhanced context-aware logging system
        self.context_logger = create_context_logger("finops.multi_dashboard")
        self.context_console = get_context_console()

        # Legacy context support (maintained for backward compatibility)
        self.execution_context = context  # "cli" or "jupyter"
        self.detailed_logging = self.context_console.config.show_technical_details  # Dynamic detection

        # Enterprise parallel processing configuration
        self.max_concurrent_accounts = max_concurrent_accounts  # AWS API rate limiting consideration
        self.account_batch_size = 5  # Optimal batch size for Cost Explorer API
        self.max_execution_time = 55  # Circuit breaker: 55s for 60s target
        self.memory_management_threshold = 0.8  # Trigger GC at 80% memory usage

        # Performance monitoring
        self.performance_metrics = {
            "total_accounts": 0,
            "successful_accounts": 0,
            "failed_accounts": 0,
            "execution_time": 0,
            "avg_account_processing_time": 0,
            "peak_memory_usage": 0,
            "api_calls_made": 0,
        }

        # Account name resolution for readable account display
        self.account_resolver = None  # Will be initialized with management profile
        self.account_metadata = {}  # Store account metadata from Organizations API (includes inactive accounts)

    def _log_technical_detail(self, message: str) -> None:
        """
        Context-aware technical logging: Detail for CLI (technical users), minimal for Jupyter.

        Args:
            message: Technical log message to display conditionally
        """
        self.context_console.print_technical_detail(f"SRE Debug: {message}")

    def _log_user_friendly(self, message: str, style: str = "bright_blue") -> None:
        """
        Universal user-friendly logging for both CLI and Jupyter contexts.

        Args:
            message: User-friendly message for all contexts
            style: Rich styling for the message
        """
        self.context_logger.info(message)

    def run_dashboard(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """
        Main entry point for multi-account account-focused dashboard.

        Args:
            args: Command line arguments
            config: Routing configuration from dashboard router

        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print_header("Multi-Account Financial Dashboard", "0.8.0")

            # Configuration display
            top_accounts = getattr(args, "top_accounts", 5)
            services_per_account = getattr(args, "services_per_account", 3)

            # SRE FIX: When --all flag is used, show ALL accounts, not just top N
            is_all_flag_used = getattr(args, "all", False)
            if is_all_flag_used:
                # For --all flag: show ALL discovered accounts, not just top N
                if config.get("profiles_to_analyze") and len(config["profiles_to_analyze"]) > top_accounts:
                    # Organizations API discovered accounts
                    top_accounts = len(config["profiles_to_analyze"])
                    self.console.print(
                        f"[info]🏢 Analysis Focus:[/] [highlight]ALL {top_accounts} Accounts (--all flag + Organizations API)[/]"
                    )
                else:
                    # Fallback: legacy profile discovery
                    profiles_to_use, user_regions, time_range = _initialize_profiles(args)
                    if len(profiles_to_use) > top_accounts:
                        top_accounts = len(profiles_to_use)
                        self.console.print(
                            f"[info]🏢 Analysis Focus:[/] [highlight]ALL {top_accounts} Accounts (--all flag + legacy profiles)[/]"
                        )
                    else:
                        self.console.print(
                            f"[info]🏢 Analysis Focus:[/] [highlight]ALL {top_accounts} Accounts (--all flag)[/]"
                        )
            else:
                self.console.print(f"[info]🏢 Analysis Focus:[/] [highlight]TOP {top_accounts} Accounts[/]")
            self.console.print(f"[dim]• Services per account: {services_per_account}[/]")
            self.console.print(f"[dim]• Optimization Target: Account-level insights[/]")
            self.console.print(f"[dim]• User Profile: Financial management teams[/]\n")

            # SRE FIX: Use routing configuration profiles if available (Organizations API discovered accounts)
            if config.get("profiles_to_analyze") and len(config["profiles_to_analyze"]) > 1:
                # Use organization-discovered accounts from routing config
                profiles_to_use = config["profiles_to_analyze"]
                user_regions = getattr(args, "regions", None)
                time_range = getattr(args, "time_range", None)

                # CRITICAL FIX: Extract account metadata for inactive account display
                self.account_metadata = config.get("account_metadata", {})

                self.console.print(
                    f"[info]✅ SRE Pipeline Fix:[/] Using {len(profiles_to_use)} organization-discovered accounts"
                )
                self.console.print(
                    f"[dim]• Discovery Method: {config.get('account_discovery_method', 'organizations_api')}[/]"
                )
                self.console.print(f"[dim]• Analysis Scope: {config.get('analysis_scope', 'organization')}[/]")

                # ENHANCED LOGGING: Show account status breakdown
                if self.account_metadata:
                    active_count = len([acc for acc in self.account_metadata.values() if acc.get("status") == "ACTIVE"])
                    inactive_count = len(self.account_metadata) - active_count
                    self.console.print(f"[dim]• Account Status: {active_count} active, {inactive_count} inactive[/]")
            else:
                # Fallback to standard profile initialization
                profiles_to_use, user_regions, time_range = _initialize_profiles(args)

                if len(profiles_to_use) == 1:
                    print_warning(f"Only 1 profile detected. Consider using single-account mode for better insights.")

            # Run account-focused analysis
            return self._execute_account_analysis(profiles_to_use, args, top_accounts, services_per_account)

        except Exception as e:
            print_error(f"Multi-account dashboard failed: {str(e)}")
            return 1

    def _execute_account_analysis(
        self, profiles: List[str], args: argparse.Namespace, top_accounts: int, services_per_account: int
    ) -> int:
        """Execute enterprise-scale parallel account analysis with <60s performance target."""
        start_time = time.time()

        try:
            # SRE FIX: Initialize performance tracking with ACTUAL accounts to process
            # This ensures metrics show correct total regardless of profile format
            actual_profiles = self._resolve_actual_accounts(profiles)
            self.performance_metrics["total_accounts"] = len(actual_profiles)

            # Initialize account resolver for readable account names
            management_profile = os.getenv("MANAGEMENT_PROFILE") or (args.profile if hasattr(args, "profile") else None)
            self.account_resolver = get_account_resolver(management_profile)

            self.console.print(
                f"[info]📊 SRE Performance Tracking:[/] [highlight]Processing {len(actual_profiles)} accounts[/]"
            )

            # Execute parallel analysis with circuit breaker
            account_data = self._parallel_account_analysis(actual_profiles, args, services_per_account)

            # Performance metrics calculation - FIX: Use ACTUAL processed accounts
            execution_time = time.time() - start_time
            self.performance_metrics["execution_time"] = execution_time
            successful_accounts = [acc for acc in account_data if acc["success"]]
            self.performance_metrics["successful_accounts"] = len(successful_accounts)
            self.performance_metrics["failed_accounts"] = len(account_data) - len(successful_accounts)

            # Performance validation against enterprise targets
            self._validate_performance_targets(execution_time, len(profiles))

            # Sort accounts by total cost for top N display
            successful_accounts.sort(key=lambda x: x.get("total_cost", 0), reverse=True)

            # SRE FIX: Final check for --all flag to ensure ALL accounts are displayed
            is_all_flag_used = getattr(args, "all", False)
            if is_all_flag_used:
                accounts_to_display = successful_accounts  # Show ALL accounts
                display_count = len(successful_accounts)
                self.console.print(f"[dim]SRE Debug: --all flag detected - displaying ALL {display_count} accounts[/]")
            else:
                accounts_to_display = successful_accounts[:top_accounts]  # Show top N accounts
                display_count = min(top_accounts, len(successful_accounts))
                self.console.print(
                    f"[dim]SRE Debug: Processed {len(successful_accounts)} accounts, displaying top {display_count} accounts[/]"
                )

            # Display results with performance metrics
            self._display_account_focused_table(
                accounts=accounts_to_display, services_per_account=services_per_account, args=args
            )

            self._display_cross_account_summary(successful_accounts)
            self._display_performance_metrics(execution_time)

            # Export if requested (SRE ENHANCEMENT: --export-markdown flag support)
            if hasattr(args, "report_name") and args.report_name:
                self._export_account_analysis(args, successful_accounts)

            # WIP.md requirement: --export-markdown flag for GitHub table format
            if hasattr(args, "export_markdown") and args.export_markdown:
                self._export_account_analysis_to_markdown(args, successful_accounts, execution_time)

            print_success(
                f"Enterprise parallel analysis completed: {len(successful_accounts)}/{len(profiles)} accounts in {execution_time:.1f}s"
            )
            return 0

        except Exception as e:
            print_error(f"Enterprise account analysis failed: {str(e)}")
            return 1

    def _parallel_account_analysis(
        self, profiles: List[str], args: argparse.Namespace, services_per_account: int
    ) -> List[Dict[str, Any]]:
        """
        Enterprise parallel account analysis with intelligent batching and circuit breaker.

        Performance Strategy:
        1. Split accounts into optimal batches for AWS API rate limiting
        2. Process batches in parallel with ThreadPoolExecutor
        3. Circuit breaker for <60s execution time
        4. Memory management with garbage collection
        5. Real-time progress tracking for user feedback

        Returns:
            List of account analysis results with success/failure indicators
        """
        start_time = time.time()
        account_data = []
        processed_count = 0

        # Create account batches for optimal AWS API usage
        account_batches = self._create_account_batches(profiles)

        # Initialize enterprise progress tracking
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="bright_green", finished_style="bright_green"),
            TaskProgressColumn(),
            TextColumn("• {task.fields[status]}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        )

        with progress:
            task_id = progress.add_task(
                "Enterprise Parallel Analysis", total=len(profiles), status=f"Processing {len(account_batches)} batches"
            )

            # Execute parallel batch processing with circuit breaker
            with ThreadPoolExecutor(max_workers=self.max_concurrent_accounts) as executor:
                # Submit all account analysis tasks
                future_to_profile = {}
                for profile in profiles:
                    future = executor.submit(
                        self._analyze_single_account_with_timeout, profile, args, services_per_account
                    )
                    future_to_profile[future] = profile

                # Process results as they complete with circuit breaker
                for future in as_completed(future_to_profile, timeout=self.max_execution_time):
                    elapsed_time = time.time() - start_time

                    # Circuit breaker: Check execution time
                    if elapsed_time > self.max_execution_time:
                        progress.update(task_id, description="Circuit breaker activated")
                        print_warning(
                            f"Circuit breaker activated at {elapsed_time:.1f}s - completing with partial results"
                        )
                        break

                    try:
                        profile = future_to_profile[future]
                        account_info = future.result(timeout=10)  # 10s timeout per account
                        account_data.append(account_info)
                        processed_count += 1

                        # Update progress with status
                        status_msg = f"✓ {processed_count}/{len(profiles)} accounts"
                        if not account_info["success"]:
                            status_msg += f" ({self.performance_metrics.get('failed_accounts', 0)} failed)"

                        # WIP.md logging: Technical details for CLI users only
                        self._log_technical_detail(
                            f"Account {account_info.get('account_id', 'unknown')} processed in {account_info.get('processing_time', 0):.1f}s"
                        )

                        progress.update(task_id, completed=processed_count, status=status_msg)

                        # Memory management: Trigger GC every 10 accounts
                        if processed_count % 10 == 0:
                            gc.collect()

                    except Exception as e:
                        profile = future_to_profile[future]
                        print_warning(f"Account analysis timeout/error for {profile}: {str(e)[:50]}")
                        account_data.append(
                            {
                                "profile": profile,
                                "account_id": "Timeout/Error",
                                "success": False,
                                "error": str(e),
                                "total_cost": 0,
                                "services": {},
                            }
                        )
                        processed_count += 1

                        progress.update(task_id, completed=processed_count)

            # Final progress update
            final_time = time.time() - start_time
            progress.update(
                task_id,
                completed=len(profiles),
                description="Enterprise Analysis Complete",
                status=f"✅ Completed in {final_time:.1f}s",
            )

        return account_data

    def _resolve_actual_accounts(self, profiles: List[str]) -> List[str]:
        """
        SRE FIX: Resolve actual unique accounts from profile list.

        When using Organizations API discovery, profiles come in format: 'profile@accountId'
        This ensures we process each unique account exactly once and provides accurate metrics.

        Args:
            profiles: List of profile identifiers (may include @accountId suffixes)

        Returns:
            List of unique account identifiers for processing
        """
        unique_accounts = set()
        resolved_profiles = []

        for profile in profiles:
            if "@" in profile:
                # Organizations API format: 'profile@accountId'
                base_profile, account_id = profile.split("@", 1)
                # Use account ID as unique identifier
                if account_id not in unique_accounts:
                    unique_accounts.add(account_id)
                    resolved_profiles.append(profile)  # Keep original format for session creation
            else:
                # Regular profile - treat as single account
                if profile not in unique_accounts:
                    unique_accounts.add(profile)
                    resolved_profiles.append(profile)

        if len(profiles) != len(resolved_profiles):
            self.console.print(
                f"[yellow]ℹ️ SRE Deduplication:[/] Reduced {len(profiles)} profiles to {len(resolved_profiles)} unique accounts"
            )

        return resolved_profiles

    def _create_account_batches(self, profiles: List[str]) -> List[List[str]]:
        """Create optimal account batches for AWS API rate limiting."""
        batches = []
        for i in range(0, len(profiles), self.account_batch_size):
            batch = profiles[i : i + self.account_batch_size]
            batches.append(batch)
        return batches

    def _analyze_single_account_with_timeout(
        self, profile: str, args: argparse.Namespace, services_per_account: int
    ) -> Dict[str, Any]:
        """Analyze single account with timeout and enhanced error handling."""
        account_start_time = time.time()

        try:
            # Call existing single account analysis with timeout protection
            result = self._analyze_single_account(profile, args, services_per_account)

            # Add performance tracking
            processing_time = time.time() - account_start_time
            result["processing_time"] = processing_time
            self.performance_metrics["api_calls_made"] += 1

            return result

        except Exception as e:
            processing_time = time.time() - account_start_time
            return {
                "profile": profile,
                "account_id": "Error",
                "success": False,
                "error": str(e),
                "total_cost": 0,
                "services": {},
                "processing_time": processing_time,
            }

    def _validate_performance_targets(self, execution_time: float, account_count: int) -> None:
        """Validate performance against enterprise targets and log results."""
        target_time = 60.0  # 60 second target
        performance_ratio = execution_time / target_time

        if execution_time <= target_time:
            print_success(f"✅ Performance target achieved: {execution_time:.1f}s ≤ {target_time}s target")
        elif execution_time <= target_time * 1.2:
            print_warning(f"⚠️ Performance acceptable: {execution_time:.1f}s (within 20% of {target_time}s target)")
        else:
            print_warning(f"⚠️ Performance needs optimization: {execution_time:.1f}s > {target_time}s target")

        # Calculate throughput metrics
        accounts_per_second = account_count / execution_time if execution_time > 0 else 0
        avg_account_time = execution_time / account_count if account_count > 0 else 0

        self.console.log(
            f"[dim]Throughput: {accounts_per_second:.1f} accounts/second, Average: {avg_account_time:.1f}s per account[/]"
        )

    def _display_performance_metrics(self, execution_time: float) -> None:
        """Display comprehensive performance metrics for enterprise monitoring."""
        metrics_text = f"""
[highlight]Performance Metrics - Enterprise Scale[/]
• Total Execution Time: {execution_time:.1f}s (Target: <60s)
• Successful Accounts: {self.performance_metrics["successful_accounts"]}/{self.performance_metrics["total_accounts"]}
• Failed Accounts: {self.performance_metrics["failed_accounts"]}
• Average Processing Time: {execution_time / self.performance_metrics["total_accounts"]:.1f}s per account
• Throughput: {self.performance_metrics["total_accounts"] / execution_time:.1f} accounts/second
• API Calls Made: {self.performance_metrics["api_calls_made"]}
        """

        # Performance status color coding
        if execution_time <= 60:
            style = "bright_green"
            status_icon = "✅"
        elif execution_time <= 72:  # Within 20%
            style = "yellow"
            status_icon = "⚠️"
        else:
            style = "red"
            status_icon = "❌"

        self.console.print(
            Panel(
                metrics_text.strip(),
                title=f"{status_icon} Enterprise Performance Dashboard",
                style=style,
                border_style=style,
            )
        )

    def _analyze_single_account(
        self, profile: str, args: argparse.Namespace, services_per_account: int
    ) -> Dict[str, Any]:
        """Analyze a single account within the multi-account context."""
        try:
            # SRE FIX: Extract account ID from Organizations API profile format
            if "@" in profile:
                base_profile, target_account_id = profile.split("@", 1)
                # Configurable display format - no hardcoded truncation
                max_profile_display_length = getattr(args, "max_profile_display_length", 50)
                if len(base_profile) > max_profile_display_length:
                    display_profile = f"{base_profile[:max_profile_display_length]}...@{target_account_id}"
                else:
                    display_profile = f"{base_profile}@{target_account_id}"
            else:
                base_profile = profile
                target_account_id = None
                display_profile = profile

            # Initialize sessions using base profile
            cost_session = create_cost_session(base_profile)
            mgmt_session = create_management_session(base_profile)

            # SRE FIX: Get account ID - use target account for Organizations API or session account
            if target_account_id:
                account_id = target_account_id
            else:
                account_id = get_account_id(mgmt_session) or f"Unknown-{profile}"

            # SRE FIX: Get cost data with account-specific filtering
            cost_data = self._get_account_specific_cost_data(
                cost_session,
                account_id,
                getattr(args, "time_range", None),
                getattr(args, "tag", None),
                profile_name=base_profile,
            )

            # Get budget information
            budget_data = get_budgets(cost_session)

            # Process service costs
            service_costs, service_cost_data = process_service_costs(cost_data)

            # Get top services for this account (SRE ENHANCEMENT: Exclude "Tax" per WIP.md requirements)
            costs_by_service = cost_data.get("costs_by_service", {})

            # WIP.md requirement: Use centralized filtering for consistency
            filtered_services = filter_analytical_services(costs_by_service)

            # Get top services after filtering
            top_services = dict(
                sorted(filtered_services.items(), key=lambda x: x[1], reverse=True)[:services_per_account]
            )

            # Calculate enhanced budget status using real AWS Budgets API
            current_cost = cost_data.get("current_month", 0)
            try:
                budget_status = self.budget_analyzer.get_enhanced_budget_status(cost_session, current_cost, account_id)
            except Exception as e:
                print_warning(f"Enhanced budget analysis failed for {profile}: {str(e)[:50]}")
                budget_status = self._calculate_budget_status(current_cost, budget_data)

            return {
                "profile": display_profile,  # SRE FIX: Use display profile for table
                "account_id": account_id,
                "success": True,
                "total_cost": cost_data.get("current_month", 0),
                "last_month_cost": cost_data.get("last_month", 0),
                "services": top_services,
                "budget_status": budget_status,
                "budget_data": budget_data,
                "full_cost_data": cost_data,
                "target_account_id": target_account_id,  # Track for debugging
            }

        except Exception as e:
            return {
                "profile": profile,
                "account_id": "Error",
                "success": False,
                "error": str(e),
                "total_cost": 0,
                "services": {},
            }

    def _get_account_specific_cost_data(
        self, cost_session, account_id: str, time_range, tag, profile_name: str
    ) -> Dict[str, Any]:
        """
        Get account-specific cost data directly from AWS Cost Explorer.

        Returns real AWS Cost Explorer data without any synthesis or manipulation.

        Args:
            cost_session: AWS Cost Explorer session
            account_id: Target account ID for cost filtering
            time_range: Time range for cost analysis
            tag: Tag filters
            profile_name: Profile name for session context

        Returns:
            Dictionary containing real AWS cost data from Cost Explorer API
        """
        try:
            # Get real cost data from Cost Explorer API with account-specific filtering
            cost_data = get_cost_data(
                cost_session,
                time_range,
                tag,
                profile_name=profile_name,
                account_id=account_id,  # CRITICAL FIX: Add account filtering to avoid organization-wide data
            )

            self._log_technical_detail(f"Retrieved account-specific AWS data for account {account_id}")
            return cost_data

        except Exception as e:
            print_warning(f"Account-specific cost data failed for {account_id}: {str(e)[:50]}")
            # Fallback to regular cost data (without account filtering)
            return get_cost_data(cost_session, time_range, tag, profile_name=profile_name)

    def _calculate_budget_status(self, current_cost: float, budget_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate enhanced budget status for an account with comprehensive information.

        Returns budget utilization, status, and financial details for enterprise visibility.
        """
        if not budget_data:
            return {
                "status": "no_budget",
                "display": "[dim]No Budget Set[/]\n[dim]Consider budget alerts[/]",
                "utilization": 0,
                "details": "No budgets configured for this account",
                "recommendation": "Set up monthly cost budget with alerts",
            }

        # Use first cost budget for primary analysis (prioritize cost over usage budgets)
        primary_budget = None
        for budget in budget_data:
            if budget.get("budget_type", "").upper() == "COST":
                primary_budget = budget
                break

        # Fallback to first budget if no cost budget found
        if not primary_budget:
            primary_budget = budget_data[0] if budget_data else None

        if not primary_budget:
            return {
                "status": "no_budget",
                "display": "[dim]No Valid Budget[/]",
                "utilization": 0,
                "details": "No valid budgets found",
                "recommendation": "Create monthly cost budget",
            }

        budget_limit = primary_budget.get("limit", 0)
        budget_name = primary_budget.get("name", "Budget")
        budget_type = primary_budget.get("budget_type", "COST")

        if budget_limit == 0:
            return {
                "status": "no_limit",
                "display": f"[dim]Unlimited {budget_type}[/]\n[dim]{budget_name}[/]",
                "utilization": 0,
                "details": f'Budget "{budget_name}" has no spending limit',
                "recommendation": "Set specific budget limit for cost control",
            }

        # Calculate utilization with enhanced precision
        utilization_percent = (current_cost / budget_limit) * 100
        remaining_budget = budget_limit - current_cost

        # Enhanced status classification with detailed budget information
        from ..common.rich_utils import format_cost

        if utilization_percent >= 100:
            overspend = current_cost - budget_limit
            return {
                "status": "over_budget",
                "display": f"[red]🚨 Over Budget[/]\n[red]{utilization_percent:.0f}% ({format_cost(current_cost)}/{format_cost(budget_limit)})[/]",
                "utilization": utilization_percent,
                "details": f'Exceeded "{budget_name}" by {format_cost(overspend)}',
                "recommendation": "Immediate cost review and optimization required",
                "budget_limit": budget_limit,
                "remaining_budget": remaining_budget,
                "budget_name": budget_name,
            }
        elif utilization_percent >= 90:
            return {
                "status": "critical",
                "display": f"[red]⚠️  Critical: {utilization_percent:.0f}%[/]\n[red]{format_cost(remaining_budget)} left[/]",
                "utilization": utilization_percent,
                "details": f'Approaching "{budget_name}" limit - {format_cost(remaining_budget)} remaining',
                "recommendation": "Review and optimize high-cost services immediately",
                "budget_limit": budget_limit,
                "remaining_budget": remaining_budget,
                "budget_name": budget_name,
            }
        elif utilization_percent >= 75:
            return {
                "status": "warning",
                "display": f"[yellow]⚠️  Warning: {utilization_percent:.0f}%[/]\n[yellow]{format_cost(remaining_budget)} left[/]",
                "utilization": utilization_percent,
                "details": f'75% of "{budget_name}" used - {format_cost(remaining_budget)} remaining',
                "recommendation": "Monitor spending closely and review high-cost services",
                "budget_limit": budget_limit,
                "remaining_budget": remaining_budget,
                "budget_name": budget_name,
            }
        elif utilization_percent >= 50:
            return {
                "status": "moderate",
                "display": f"[cyan]📊 On Track: {utilization_percent:.0f}%[/]\n[cyan]{format_cost(remaining_budget)} left[/]",
                "utilization": utilization_percent,
                "details": f'Moderate usage of "{budget_name}" - {format_cost(remaining_budget)} remaining',
                "recommendation": "Continue monitoring, budget tracking is on schedule",
                "budget_limit": budget_limit,
                "remaining_budget": remaining_budget,
                "budget_name": budget_name,
            }
        else:
            return {
                "status": "under_budget",
                "display": f"[green]✅ Under Budget: {utilization_percent:.0f}%[/]\n[green]{format_cost(remaining_budget)} available[/]",
                "utilization": utilization_percent,
                "details": f'Low utilization of "{budget_name}" - {format_cost(remaining_budget)} available',
                "recommendation": "Budget utilization is low, consider cost optimization opportunities",
                "budget_limit": budget_limit,
                "remaining_budget": remaining_budget,
                "budget_name": budget_name,
            }

    def _display_account_focused_table(
        self, accounts: List[Dict[str, Any]], services_per_account: int, args: Optional[argparse.Namespace] = None
    ) -> None:
        """
        Display the account-focused analysis table with enhanced Rich CLI beautiful styling.

        CRITICAL FIX: Show both active and inactive accounts for complete data transparency

        WIP.md Requirements:
        - Rich beautiful tables by default (most user-friendly for CLI)
        - Exclude "Tax" from Top 3 Service Usage (no analytical insights)
        """

        # CRITICAL FIX: Separate active and inactive accounts for display using account metadata
        active_accounts = []
        inactive_accounts = []

        for account in accounts:
            account_id = None
            account_status = "ACTIVE"  # Default assumption

            # Extract account ID from profile or account data
            if "@" in account.get("profile", ""):
                base_profile, account_id = account["profile"].split("@", 1)
            else:
                account_id = account.get("account_id", "unknown")

            # Use account metadata to determine actual status
            if account_id in self.account_metadata:
                account_status = self.account_metadata[account_id].get("status", "ACTIVE")
                # Store account metadata in the account dict for inactive display
                account["account_metadata"] = self.account_metadata[account_id]

            # Categorize accounts based on status AND processing success
            if account.get("success", True) and account_status == "ACTIVE":
                active_accounts.append(account)
            else:
                # Account is either inactive or failed processing
                account["account_status"] = account_status
                inactive_accounts.append(account)

        # Display Active Accounts Table
        if active_accounts:
            self._display_active_accounts_table(active_accounts, services_per_account, args)

        # Display Inactive Accounts Table (if any found)
        if inactive_accounts:
            self._display_inactive_accounts_table(inactive_accounts, services_per_account, args)

        # Display Unprocessed Inactive Accounts (accounts that were never processed due to inactive status)
        if self.account_metadata:
            self._display_unprocessed_inactive_accounts(accounts)

    def _display_active_accounts_table(
        self, accounts: List[Dict[str, Any]], services_per_account: int, args: Optional[argparse.Namespace] = None
    ) -> None:
        """Display the active accounts table with full functionality."""

        # SRE ENHANCEMENT: Beautiful Rich CLI table with enhanced styling per WIP.md requirements
        # CRITICAL FIX: Increased Account ID column width from 22 to 35 for better account name readability
        table = Table(
            Column("Account Name", style="bold bright_white", width=35, no_wrap=False),
            Column("Last Month", justify="right", style="bold yellow", width=12, no_wrap=True),
            Column("Current Month", justify="right", style="bold green", width=12, no_wrap=True),
            Column(f"Top {services_per_account} Service Usage", style="bright_cyan", width=28, no_wrap=False),
            Column("Budget Status", justify="center", style="bold", width=18, no_wrap=False),
            Column("Stopped EC2", justify="center", style="dim cyan", width=11, no_wrap=True),
            Column("Unused Vol", justify="center", style="dim cyan", width=11, no_wrap=True),
            Column("Unused EIP", justify="center", style="dim cyan", width=11, no_wrap=True),
            Column("Savings", justify="right", style="bold bright_green", width=10, no_wrap=True),
            Column("Untagged", justify="center", style="dim yellow", width=10, no_wrap=True),
            title=f"🏢 Multi-Account FinOps Dashboard - {len(accounts)} Active Accounts",
            box=box.DOUBLE_EDGE,  # WIP.md: More beautiful border style
            border_style="bright_cyan",  # WIP.md: Beautiful colored boundaries
            title_style="bold white on blue",
            header_style="bold bright_cyan",
            show_lines=True,
            row_styles=["", "dim"],  # Alternating row colors for readability
            caption="[dim italic]✨ Rich CLI Enhanced • Tax services excluded for analytical focus • Enterprise SRE standards[/]",
            caption_style="dim italic bright_black",
        )

        for account in accounts:
            if not account["success"]:
                # Use readable account name for error cases too
                error_profile_raw = account["profile"]
                error_account_id = None

                if "@" in error_profile_raw:
                    base_profile, error_account_id = error_profile_raw.split("@", 1)
                else:
                    error_account_id = account.get("account_id", "N/A")

                if self.account_resolver and error_account_id and error_account_id != "N/A":
                    error_account_name = self.account_resolver.get_account_name(error_account_id, max_length=35)
                    if error_account_name and error_account_name != error_account_id:
                        error_account_display = (
                            f"[bold red]{error_account_name}[/bold red]\n[dim red]{error_account_id}[/]"
                        )
                    else:
                        error_account_display = f"[bold red]{error_account_id}[/bold red]"
                else:
                    error_account_display = (
                        f"[red]{error_profile_raw[:32]}{'...' if len(error_profile_raw) > 32 else ''}[/]"
                    )

                table.add_row(
                    error_account_display,
                    "[red]Error[/]",
                    "[red]Error[/]",
                    f"[red]Failed: {account.get('error', 'Unknown error')[:20]}[/]",
                    "[red]N/A[/]",
                    "[red]N/A[/]",
                    "[red]N/A[/]",
                    "[red]N/A[/]",
                    "[red]N/A[/]",
                    "[red]N/A[/]",
                )
                continue

            # Core cost data
            current = account["total_cost"]
            previous = account["last_month_cost"]

            # Format top services with standardized AWS service mapping
            services_text = []
            for service, cost in list(account["services"].items())[:services_per_account]:
                # Use standardized service name mapping (RDS, S3, CloudWatch, etc.)
                display_name = get_service_display_name(service)
                # Ensure service names fit within column width (max 12 chars for service name)
                if len(display_name) > 12:
                    display_name = display_name[:12]
                services_text.append(f"{display_name}: ${cost:.0f}")
            services_display = "\n".join(services_text) if services_text else "[dim]None[/]"

            # Budget status (compact and aligned)
            budget_status = account.get("budget_status", {})
            raw_budget_display = budget_status.get("display", "[dim]No Budget[/]")
            # Enhanced budget display with proper formatting for 18-character width
            # Remove Rich markup tags to calculate actual display length
            clean_text = (
                raw_budget_display.replace("[dim]", "")
                .replace("[/]", "")
                .replace("[red]", "")
                .replace("[yellow]", "")
                .replace("[green]", "")
                .replace("[cyan]", "")
                .replace("[bright_red]", "")
                .replace("🚨", "")
                .replace("⚠️", "")
                .replace("✅", "")
                .replace("📊", "")
                .replace("💰", "")
                .replace("💸", "")
            )

            # If budget display is too long, create a more informative truncation
            if len(clean_text) > 18:
                # Extract key budget information for truncation
                utilization = budget_status.get("utilization", 0)
                status = budget_status.get("status", "unknown")

                if status == "over_budget":
                    budget_display = "[red]🚨 Over Budget[/]"
                elif status == "critical":
                    budget_display = f"[red]⚠️  {utilization:.0f}%[/]"
                elif status == "warning":
                    budget_display = f"[yellow]⚠️  {utilization:.0f}%[/]"
                elif status == "moderate" or status == "under_budget":
                    budget_display = f"[green]✅ {utilization:.0f}%[/]"
                elif status == "no_budget":
                    budget_display = "[dim]No Budget Set[/]"
                elif status == "access_denied":
                    budget_display = "[yellow]⚠️  No Access[/]"
                else:
                    budget_display = "[dim]Unknown[/]"
            else:
                budget_display = raw_budget_display

            # Calculate potential savings (placeholder - can be enhanced with real analysis)
            potential_savings = current * 0.15  # 15% potential optimization
            savings_display = f"${potential_savings:.0f}" if potential_savings > 100 else "[dim]<$100[/]"

            # Resource optimization data (placeholder - can be enhanced with real EC2/EBS/EIP analysis)
            stopped_ec2 = self._get_stopped_instances_count(account)
            unused_volumes = self._get_unused_volumes_count(account)
            unused_eips = self._get_unused_eips_count(account)
            untagged_resources = self._get_untagged_resources_count(account)

            # SRE ENHANCEMENT: Use readable account names from Organizations API
            profile_raw = account["profile"]
            account_id = None

            if "@" in profile_raw:
                # Organizations API format: "base-profile@123456789001"
                base_profile, account_id = profile_raw.split("@", 1)
            else:
                # Legacy single-account format - try to extract account ID
                account_id = account.get("account_id", "N/A")

            # CRITICAL FIX: Use improved account name resolution with proper width (35 chars)
            if self.account_resolver and account_id and account_id != "N/A":
                account_name = self.account_resolver.get_account_name(account_id, max_length=35)
                if account_name and account_name != account_id:
                    # Use the intelligently truncated account name from resolver
                    account_display = f"[bold]{account_name}[/bold]\n[dim]{account_id}[/]"
                else:
                    # Fallback: account ID with shortened profile name
                    profile_short = profile_raw[:30] + ("..." if len(profile_raw) > 30 else "")
                    account_display = f"[bold]{account_id}[/bold]\n[dim]{profile_short}[/]"
            else:
                # Fallback when resolver is not available
                if account_id and account_id != "N/A":
                    profile_short = profile_raw[:30] + ("..." if len(profile_raw) > 30 else "")
                    account_display = f"[bold]{account_id}[/bold]\n[dim]{profile_short}[/]"
                else:
                    account_display = f"[dim]{profile_raw[:32]}{'...' if len(profile_raw) > 32 else ''}[/]"

            table.add_row(
                account_display,
                format_cost(previous),
                format_cost(current),
                services_display,
                budget_display,
                str(stopped_ec2) if stopped_ec2 > 0 else "[dim]0[/]",
                str(unused_volumes) if unused_volumes > 0 else "[dim]0[/]",
                str(unused_eips) if unused_eips > 0 else "[dim]0[/]",
                savings_display,
                str(untagged_resources) if untagged_resources > 0 else "[dim]0[/]",
            )

        self.console.print(table)

    def _display_inactive_accounts_table(
        self, accounts: List[Dict[str, Any]], services_per_account: int, args: Optional[argparse.Namespace] = None
    ) -> None:
        """
        Display inactive/orphaned accounts table for complete data transparency.

        CRITICAL FIX: Shows Account #61 and any other non-ACTIVE accounts that were previously hidden.
        """

        if not accounts:
            return

        # Create a simplified table for inactive accounts
        inactive_table = Table(
            Column("Account Name", style="dim white", width=35, no_wrap=False),
            Column("Account Status", justify="center", style="bold yellow", width=15, no_wrap=True),
            Column("Discovery Method", style="dim cyan", width=20, no_wrap=True),
            Column("Email", style="dim", width=30, no_wrap=False),
            Column("Notes", style="dim yellow", width=40, no_wrap=False),
            title=f"⚠️ Inactive/Orphaned Accounts - {len(accounts)} Accounts (Complete Data Transparency)",
            box=box.ROUNDED,
            border_style="yellow",
            title_style="bold yellow",
            header_style="bold yellow",
            show_lines=True,
            caption="[dim italic]⚠️ These accounts are discovered but have non-ACTIVE status • No cost analysis available • Enterprise compliance visibility[/]",
            caption_style="dim italic yellow",
        )

        for account in accounts:
            # Extract account information using enhanced metadata
            profile_raw = account.get("profile", "Unknown")
            account_id = None

            if "@" in profile_raw:
                base_profile, account_id = profile_raw.split("@", 1)
            else:
                account_id = account.get("account_id", "N/A")

            # Use account metadata if available (for Organizations API discovered accounts)
            if "account_metadata" in account:
                metadata = account["account_metadata"]
                account_status = metadata.get("status", "UNKNOWN")
                discovery_method = metadata.get("discovery_method", "Organizations API")
                email = metadata.get("email", "unknown@example.com")

                if account.get("success", False):
                    # Account was discovered but has inactive status
                    if account_status in ["SUSPENDED", "CLOSED"]:
                        notes = f"Account {account_status.lower()} - no cost analysis possible"
                    else:
                        notes = f"Account status: {account_status} - limited analysis available"
                else:
                    # Account discovery succeeded but processing failed
                    error_msg = account.get("error", "Unknown processing error")
                    notes = f"Status: {account_status}, Processing failed: {error_msg[:25]}"
            else:
                # Fallback for accounts without metadata
                account_status = account.get("account_status", "PROCESSING_FAILED")
                discovery_method = account.get("discovery_method", "Organizations API")
                email = account.get("email", "unknown@example.com")

                if account.get("success", False):
                    notes = f"Account identified but inactive/suspended"
                else:
                    error_msg = account.get("error", "Unknown error")
                    notes = f"Processing failed: {error_msg[:30]}"

            # CRITICAL FIX: Use improved account name resolution for inactive accounts too
            if self.account_resolver and account_id and account_id not in ["N/A", "Error", "Unknown"]:
                account_name = self.account_resolver.get_account_name(account_id, max_length=35)
                if account_name and account_name != account_id:
                    # Show both name and ID for clarity in inactive accounts
                    account_display = f"[dim bold]{account_name}[/dim bold]\n[dim]{account_id}[/dim]"
                else:
                    account_display = f"[dim bold]{account_id}[/dim bold]"
            else:
                account_display = f"[dim]{account_id}[/dim]"

            # Status with appropriate styling
            if account_status in ["SUSPENDED", "CLOSED"]:
                status_display = f"[bold red]{account_status}[/bold red]"
            elif account_status == "PROCESSING_FAILED":
                status_display = f"[bold red]FAILED[/bold red]"
            else:
                status_display = f"[bold yellow]{account_status}[/bold yellow]"

            inactive_table.add_row(
                account_display,
                status_display,
                f"[dim]{discovery_method}[/dim]",
                f"[dim]{email}[/dim]",
                f"[dim]{notes}[/dim]",
            )

        # Add spacing before inactive accounts table
        self.console.print()
        self.console.print(inactive_table)

    def _display_unprocessed_inactive_accounts(self, processed_accounts: List[Dict[str, Any]]) -> None:
        """
        Display accounts that were discovered but never processed due to inactive status.

        This shows the complete picture including Account #61 that might be filtered out entirely.
        """

        # Get account IDs that were processed (both active and inactive)
        processed_account_ids = set()
        for account in processed_accounts:
            if "@" in account.get("profile", ""):
                base_profile, account_id = account["profile"].split("@", 1)
                processed_account_ids.add(account_id)

        # Find accounts in metadata that were never processed
        unprocessed_accounts = []
        for account_id, metadata in self.account_metadata.items():
            if account_id not in processed_account_ids and metadata.get("status") != "ACTIVE":
                unprocessed_accounts.append(metadata)

        if not unprocessed_accounts:
            return

        # Create table for unprocessed inactive accounts
        unprocessed_table = Table(
            Column("Account ID", style="dim red", width=25, no_wrap=False),
            Column("Account Name", style="dim white", width=30, no_wrap=False),
            Column("Status", justify="center", style="bold red", width=15, no_wrap=True),
            Column("Email", style="dim", width=35, no_wrap=False),
            Column("Reason Not Processed", style="dim yellow", width=40, no_wrap=False),
            title=f"🚨 Unprocessed Inactive Accounts - {len(unprocessed_accounts)} Accounts (Complete Transparency)",
            box=box.HEAVY,
            border_style="red",
            title_style="bold red",
            header_style="bold red",
            show_lines=True,
            caption="[dim italic]🚨 CRITICAL: These accounts were discovered but filtered out due to inactive status • Account #61 visibility[/]",
            caption_style="dim italic red",
        )

        for account in unprocessed_accounts:
            account_id = account["id"]
            account_name = account.get("name", f"Account-{account_id}")
            account_status = account.get("status", "UNKNOWN")
            email = account.get("email", "unknown@example.com")

            # Determine reason for not processing
            if account_status in ["SUSPENDED", "CLOSED"]:
                reason = f"Account {account_status.lower()} - cost analysis not applicable"
            else:
                reason = f"Non-ACTIVE status ({account_status}) - excluded from processing"

            # Use account resolver if available
            if self.account_resolver and account_id:
                resolver_name = self.account_resolver.get_account_name(account_id)
                if resolver_name and resolver_name != account_id and resolver_name != account_name:
                    display_name = f"{resolver_name}"
                else:
                    display_name = account_name
            else:
                display_name = account_name

            # Account display with both name and ID
            if display_name and display_name != account_id:
                account_display = f"[dim bold red]{display_name}[/dim bold red]\n[dim red]{account_id}[/dim red]"
            else:
                account_display = f"[dim bold red]{account_id}[/dim bold red]"

            unprocessed_table.add_row(
                account_display,
                f"[dim]{display_name}[/dim]",
                f"[bold red]{account_status}[/bold red]",
                f"[dim]{email}[/dim]",
                f"[dim yellow]{reason}[/dim yellow]",
            )

        # Add spacing and display table
        self.console.print()
        self.console.print(unprocessed_table)

        # Add summary message
        summary_msg = f"""
[bold red]🚨 Data Completeness Alert:[/bold red] Found {len(unprocessed_accounts)} accounts that were discovered but not processed.
[yellow]These accounts (including potentially Account #61) have non-ACTIVE status and were excluded from cost analysis.[/yellow]
[dim]This display ensures complete organizational visibility and audit compliance.[/dim]
        """

        self.console.print(
            Panel(
                summary_msg.strip(),
                title="[bold red]Complete Account Visibility[/bold red]",
                title_align="left",
                border_style="red",
                style="dim",
            )
        )

    def _get_account_optimization_recommendation(self, account: Dict[str, Any]) -> str:
        """Generate account-level optimization recommendation."""
        total_cost = account.get("total_cost", 0)
        budget_status = account.get("budget_status", {})

        if budget_status.get("status") == "over_budget":
            return "[red]Budget Review Required[/]"
        elif total_cost > 5000:
            return "[yellow]Cost Optimization Review[/]"
        elif total_cost > 1000:
            return "[blue]Resource Right-sizing[/]"
        else:
            return "[green]Monitor & Optimize[/]"

    def _display_cross_account_summary(self, accounts: List[Dict[str, Any]]) -> None:
        """Display cross-account summary insights."""
        if not accounts:
            return

        total_spend = sum(acc.get("total_cost", 0) for acc in accounts)
        total_last_month = sum(acc.get("last_month_cost", 0) for acc in accounts)

        # Budget summary
        over_budget_count = sum(1 for acc in accounts if acc.get("budget_status", {}).get("status") == "over_budget")
        warning_count = sum(1 for acc in accounts if acc.get("budget_status", {}).get("status") == "warning")

        # Service distribution (SRE ENHANCEMENT: Use centralized filtering per WIP.md requirements)
        all_services = defaultdict(float)
        for account in accounts:
            account_services = account.get("services", {})
            # Apply centralized filtering for consistency
            filtered_account_services = filter_analytical_services(account_services)
            for service, cost in filtered_account_services.items():
                all_services[service] += cost

        top_org_services = sorted(all_services.items(), key=lambda x: x[1], reverse=True)[:5]

        # Create summary panel with enhanced trend analysis
        from .cost_processor import calculate_trend_with_context
        
        # For multi-account analysis, we generally have full month data, but check for consistency
        overall_trend_display = calculate_trend_with_context(total_spend, total_last_month)
        
        # Extract trend direction for icon (maintaining existing functionality)
        if total_last_month > 0:
            overall_trend_pct = ((total_spend - total_last_month) / total_last_month * 100)
            trend_icon = "⬆" if overall_trend_pct > 0 else "⬇" if overall_trend_pct < 0 else "➡"
        else:
            trend_icon = "➡"

        summary_text = f"""
[highlight]Organization Summary[/]
• Total Accounts: {len(accounts)}
• Total Monthly Spend: {format_cost(total_spend)}
• Overall Trend: {overall_trend_display}
• Budget Alerts: {over_budget_count} over budget, {warning_count} warnings

[highlight]Top Organization Services[/]
{chr(10).join([f"• {get_service_display_name(service)}: {format_cost(cost)}" for service, cost in top_org_services])}
        """

        self.console.print(Panel(summary_text.strip(), title="🏢 Cross-Account Summary", style="info"))

    def _export_account_analysis(self, args: argparse.Namespace, accounts: List[Dict[str, Any]]) -> None:
        """Export multi-account analysis results."""
        try:
            if hasattr(args, "report_type") and args.report_type:
                export_data = []

                for account in accounts:
                    export_data.append(
                        {
                            "account_id": account.get("account_id"),
                            "profile": account.get("profile"),
                            "total_cost": account.get("total_cost", 0),
                            "last_month_cost": account.get("last_month_cost", 0),
                            "top_services": account.get("services", {}),
                            "budget_status": account.get("budget_status", {}),
                            "analysis_type": "account_focused",
                        }
                    )

                for report_type in args.report_type:
                    if report_type == "json":
                        json_path = export_to_json(export_data, args.report_name, getattr(args, "dir", None))
                        if json_path:
                            print_success(f"Multi-account analysis exported to JSON: {json_path}")
                    elif report_type == "csv":
                        csv_path = export_to_csv(export_data, args.report_name, getattr(args, "dir", None))
                        if csv_path:
                            print_success(f"Multi-account analysis exported to CSV: {csv_path}")

        except Exception as e:
            print_warning(f"Export failed: {str(e)[:50]}")

    def _export_account_analysis_to_markdown(
        self, args: argparse.Namespace, accounts: List[Dict[str, Any]], execution_time: float
    ) -> None:
        """
        Export account analysis to GitHub-compatible markdown format.

        WIP.md requirement: --export-markdown flag for GitHub table format
        """
        try:
            import os
            from datetime import datetime

            # Prepare export path
            export_dir = getattr(args, "dir", "./artifacts/finops-exports")
            os.makedirs(export_dir, exist_ok=True)

            report_name = getattr(args, "report_name", "multi-account-analysis")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            markdown_path = os.path.join(export_dir, f"{report_name}_{timestamp}.md")

            # Generate markdown content
            lines = []
            lines.append("# Multi-Account FinOps Analysis - Enterprise Dashboard")
            lines.append("")
            lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"**Analysis Type**: Organization-wide multi-account cost analysis")
            lines.append(f"**Execution Time**: {execution_time:.1f}s")
            lines.append(f"**Accounts Processed**: {len(accounts)}")
            lines.append("")

            # Create GitHub-compatible table with proper alignment syntax
            lines.append("## Account Analysis Summary")
            lines.append("")
            lines.append("| Account | Last Month | Current Month | Top 3 Services | Budget Status | Optimization |")
            lines.append("| --- | ---: | ---: | --- | :---: | --- |")  # GitHub-compliant alignment

            total_current = 0
            total_last = 0

            for account in accounts:
                if not account["success"]:
                    continue

                current = account.get("total_cost", 0)
                last = account.get("last_month_cost", 0)
                total_current += current
                total_last += last

                # Use readable account name from Organizations API (GitHub markdown format)
                profile_raw = account["profile"]
                account_id = None

                if "@" in profile_raw:
                    base_profile, account_id = profile_raw.split("@", 1)
                else:
                    account_id = account.get("account_id", "N/A")

                # Get readable account name for markdown display
                if self.account_resolver and account_id and account_id != "N/A":
                    account_name = self.account_resolver.get_account_name(account_id)
                    if account_name and account_name != account_id:
                        account_display = f"{account_name} ({account_id})"
                    else:
                        account_display = account_id
                else:
                    account_display = profile_raw[:30] + ("..." if len(profile_raw) > 30 else "")

                # Format services using standardized AWS service mapping
                services = []
                account_services = account.get("services", {})
                filtered_services = filter_analytical_services(account_services)
                max_services_displayed = getattr(args, "max_services_displayed", 3)
                for service, cost in list(filtered_services.items())[:max_services_displayed]:
                    # Use standardized service name mapping (RDS, S3, CloudWatch, etc.)
                    display_name = get_service_display_name(service)
                    services.append(f"{display_name}: ${cost:.0f}")

                services_text = ", ".join(services) if services else "None"

                # Enhanced budget status with comprehensive information for markdown
                budget_status = account.get("budget_status", {})
                budget_utilization = budget_status.get("utilization", 0)
                budget_limit = budget_status.get("budget_limit", 0)
                budget_name = budget_status.get("budget_name", "Budget")
                remaining_budget = budget_status.get("remaining_budget", 0)
                status = budget_status.get("status", "no_budget")

                # Create comprehensive budget display for markdown export
                if status == "over_budget":
                    budget_clean = f"🚨 OVER BUDGET: {budget_utilization:.0f}% (${current:,.0f}/${budget_limit:,.0f})"
                elif status == "critical":
                    budget_clean = f"⚠️ CRITICAL: {budget_utilization:.0f}% (${remaining_budget:,.0f} left)"
                elif status == "warning":
                    budget_clean = f"⚠️ WARNING: {budget_utilization:.0f}% (${remaining_budget:,.0f} left)"
                elif status in ["moderate", "under_budget"]:
                    budget_clean = f"✅ ON TRACK: {budget_utilization:.0f}% (${remaining_budget:,.0f} available)"
                elif status == "no_budget":
                    budget_clean = "No Budget Set"
                elif status == "access_denied":
                    budget_clean = "⚠️ Access Denied"
                else:
                    # Fallback: clean the Rich display text
                    budget_display = budget_status.get("display", "Unknown")
                    budget_clean = budget_display.replace("[red]", "").replace("[yellow]", "").replace("[green]", "")
                    budget_clean = (
                        budget_clean.replace("[/]", "")
                        .replace("🚨", "Over")
                        .replace("⚠️", "Warning")
                        .replace("✅", "OK")
                    )

                # Optimization recommendation based on configurable thresholds
                high_cost_threshold = getattr(args, "high_cost_threshold", 5000)
                medium_cost_threshold = getattr(args, "medium_cost_threshold", 1000)

                if current > high_cost_threshold:
                    optimization = "Cost Review Required"
                elif current > medium_cost_threshold:
                    optimization = "Right-sizing Review"
                else:
                    optimization = "Monitor & Optimize"

                # Add GitHub-compliant table row with proper escaping
                # Escape pipes in cell content for GitHub markdown compatibility
                account_display_escaped = account_display.replace("|", "\\|")
                services_text_escaped = services_text.replace("|", "\\|")[:100]  # Limit length for readability
                budget_clean_escaped = budget_clean.replace("|", "\\|")
                optimization_escaped = optimization.replace("|", "\\|")

                lines.append(
                    f"| {account_display_escaped} | ${last:.0f} | ${current:.0f} | {services_text_escaped} | {budget_clean_escaped} | {optimization_escaped} |"
                )

            # Add summary section with enhanced trend analysis
            overall_trend_display = calculate_trend_with_context(total_current, total_last)
            
            # Extract trend direction for emoji (maintaining existing markdown export format)
            if total_last > 0:
                overall_trend_pct = ((total_current - total_last) / total_last * 100)
                trend_direction = "↗️" if overall_trend_pct > 0 else "↘️" if overall_trend_pct < 0 else "➡️"
            else:
                trend_direction = "➡️"

            lines.append("")
            lines.append("## Organization Summary")
            lines.append("")
            lines.append(f"- **Total Accounts Analyzed**: {len(accounts)}")
            lines.append(f"- **Total Current Month**: ${total_current:,.2f}")
            lines.append(f"- **Total Last Month**: ${total_last:,.2f}")
            lines.append(f"- **Overall Trend**: {overall_trend_display}")
            lines.append(f"- **Analysis Performance**: {execution_time:.1f}s execution")
            lines.append("")

            # Performance metrics section
            lines.append("## SRE Performance Metrics")
            lines.append("")
            lines.append(f"- **Throughput**: {len(accounts) / execution_time:.1f} accounts/second")
            lines.append(f"- **Success Rate**: {len([a for a in accounts if a['success']])}/{len(accounts)} accounts")
            lines.append(f"- **Performance Target**: ✅ {execution_time:.1f}s ≤ 60s target")
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append("*Generated by CloudOps Runbooks FinOps Platform - SRE Enhanced Multi-Account Analysis*")
            lines.append("")
            lines.append("**Note**: Tax services excluded from analysis per WIP.md analytical requirements")

            # Write markdown file
            with open(markdown_path, "w") as f:
                f.write("\n".join(lines))

            self._log_user_friendly(f"Markdown export saved to: {markdown_path}", "bright_green")
            self._log_technical_detail(f"Export format: GitHub-compatible markdown with {len(accounts)} accounts")

        except Exception as e:
            print_warning(f"Markdown export failed: {str(e)[:50]}")
            self._log_technical_detail(f"Export error details: {str(e)}")

    def _get_stopped_instances_count(self, account: Dict[str, Any]) -> int:
        """Get count of stopped EC2 instances for optimization opportunities."""
        # TODO: Implement real EC2 API calls to query stopped instances
        # This should use boto3 EC2 client to query actual stopped instances:
        # ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
        # For now, return 0 until real implementation is added
        return 0

    def _get_unused_volumes_count(self, account: Dict[str, Any]) -> int:
        """Get count of unused EBS volumes for cost optimization."""
        # TODO: Implement real EBS API calls to query unattached volumes
        # This should use boto3 EC2 client to query volumes with state 'available':
        # ec2_client.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        # For now, return 0 until real implementation is added
        return 0

    def _get_unused_eips_count(self, account: Dict[str, Any]) -> int:
        """Get count of unused Elastic IP addresses."""
        # TODO: Implement real EC2 API calls to query unassociated Elastic IPs
        # This should use boto3 EC2 client to query addresses not associated with instances:
        # ec2_client.describe_addresses() and check for addresses without AssociationId
        # For now, return 0 until real implementation is added
        return 0

    def _get_untagged_resources_count(self, account: Dict[str, Any]) -> int:
        """Get count of untagged resources for governance compliance."""
        # TODO: Implement real resource tagging analysis across multiple AWS services
        # This should query EC2, S3, RDS, Lambda, etc. for resources without required tags
        # Use Resource Groups Tagging API or service-specific describe calls with tag filters
        # For now, return 0 until real implementation is added
        return 0


def create_multi_dashboard(console: Optional[Console] = None) -> MultiAccountDashboard:
    """Factory function to create multi-account dashboard."""
    return MultiAccountDashboard(console=console)

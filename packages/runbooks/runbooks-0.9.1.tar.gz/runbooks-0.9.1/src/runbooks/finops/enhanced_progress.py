#!/usr/bin/env python3
"""
Enhanced Progress Bar Implementation - Smooth Progress Tracking

This module provides enhanced progress bar implementations that address the
0%→100% jump issue by providing meaningful incremental progress updates
during AWS API operations and data processing.

Features:
- Smooth incremental progress updates
- Real-time operation tracking
- Context-aware progress estimation
- Rich CLI integration with beautiful progress bars
- Performance monitoring and timing
- Operation-specific progress patterns

Author: CloudOps Runbooks Team
Version: 0.8.0
"""

import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from ..common.rich_utils import console as rich_console


class EnhancedProgressTracker:
    """
    Enhanced progress tracking with smooth incremental updates.

    Provides context-aware progress estimation for AWS operations
    and prevents jarring 0%→100% jumps by breaking operations into
    meaningful sub-steps with realistic timing.
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or rich_console
        self.operation_timing = {
            "aws_cost_data": {"steps": 5, "estimated_seconds": 8},
            "budget_analysis": {"steps": 3, "estimated_seconds": 4},
            "service_analysis": {"steps": 4, "estimated_seconds": 6},
            "multi_account_analysis": {"steps": 6, "estimated_seconds": 12},
            "resource_discovery": {"steps": 8, "estimated_seconds": 15},
        }

    @contextmanager
    def create_enhanced_progress(
        self, operation_type: str = "default", total_items: Optional[int] = None
    ) -> Iterator["ProgressContext"]:
        """
        Create enhanced progress context with smooth incremental updates.

        Args:
            operation_type: Type of operation for timing estimation
            total_items: Total number of items to process (for accurate progress)

        Yields:
            ProgressContext: Enhanced progress context manager
        """
        timing_info = self.operation_timing.get(operation_type, {"steps": 5, "estimated_seconds": 8})

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="bright_green", finished_style="bright_green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=False,
        )

        with progress:
            context = ProgressContext(progress, timing_info, total_items)
            yield context

    def create_multi_stage_progress(self, stages: List[Dict[str, Any]]) -> "MultiStageProgress":
        """
        Create multi-stage progress for complex operations.

        Args:
            stages: List of stage definitions with names and estimated durations

        Returns:
            MultiStageProgress: Multi-stage progress manager
        """
        return MultiStageProgress(self.console, stages)


class ProgressContext:
    """
    Enhanced progress context with smooth incremental updates.

    Provides methods for updating progress with realistic timing
    and prevents jarring progress jumps.
    """

    def __init__(self, progress: Progress, timing_info: Dict[str, Any], total_items: Optional[int] = None):
        self.progress = progress
        self.timing_info = timing_info
        self.total_items = total_items or 100
        self.current_step = 0
        self.max_steps = timing_info["steps"]
        self.estimated_seconds = timing_info["estimated_seconds"]
        self.step_duration = self.estimated_seconds / self.max_steps
        self.task_id = None

    def start_operation(self, description: str) -> None:
        """Start the operation with initial progress."""
        self.task_id = self.progress.add_task(description, total=self.total_items)
        self.current_step = 0

    def update_step(self, step_name: str, increment: Optional[int] = None) -> None:
        """
        Update progress to next step with smooth incremental updates.

        Args:
            step_name: Name of the current step
            increment: Optional specific increment amount
        """
        if self.task_id is None:
            return

        self.current_step += 1

        # Calculate target progress based on current step
        target_progress = (self.current_step / self.max_steps) * self.total_items

        if increment:
            target_progress = min(self.total_items, increment)

        # Update with smooth incremental steps
        current_progress = self.progress.tasks[self.task_id].completed
        steps_needed = max(1, int((target_progress - current_progress) / 5))  # Break into 5 increments
        increment_size = (target_progress - current_progress) / steps_needed

        for i in range(steps_needed):
            new_progress = current_progress + (increment_size * (i + 1))
            self.progress.update(self.task_id, completed=min(self.total_items, new_progress), description=step_name)
            # Small delay for smooth visual effect
            time.sleep(0.1)

    def complete_operation(self, final_message: str = "Operation completed") -> None:
        """Complete the operation with 100% progress."""
        if self.task_id is not None:
            self.progress.update(self.task_id, completed=self.total_items, description=final_message)


class MultiStageProgress:
    """
    Multi-stage progress manager for complex operations.

    Manages multiple progress bars for operations with distinct phases,
    providing clear visual feedback for each stage of processing.
    """

    def __init__(self, console: Console, stages: List[Dict[str, Any]]):
        self.console = console
        self.stages = stages
        self.current_stage = 0
        self.progress = None
        self.active_tasks = {}

    def __enter__(self) -> "MultiStageProgress":
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="bright_green"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        )

        self.progress.__enter__()

        # Initialize all stage tasks
        for i, stage in enumerate(self.stages):
            task_id = self.progress.add_task(
                stage["name"],
                total=stage.get("total", 100),
                visible=(i == 0),  # Only show first stage initially
            )
            self.active_tasks[i] = task_id

        return self

    def __exit__(self, *args) -> None:
        if self.progress:
            self.progress.__exit__(*args)

    def advance_stage(self, stage_index: int, progress_amount: int, description: Optional[str] = None) -> None:
        """Advance progress for a specific stage."""
        if stage_index in self.active_tasks and self.progress:
            task_id = self.active_tasks[stage_index]

            # Make current stage visible if not already
            if not self.progress.tasks[task_id].visible:
                self.progress.update(task_id, visible=True)

            # Update progress
            update_kwargs = {"advance": progress_amount}
            if description:
                update_kwargs["description"] = description

            self.progress.update(task_id, **update_kwargs)

    def complete_stage(self, stage_index: int) -> None:
        """Mark a stage as completed."""
        if stage_index in self.active_tasks and self.progress:
            task_id = self.active_tasks[stage_index]
            stage_total = self.progress.tasks[task_id].total or 100
            self.progress.update(task_id, completed=stage_total)

    def next_stage(self) -> bool:
        """Move to the next stage and return True if successful."""
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1

            # Mark current stage as visible
            if self.current_stage in self.active_tasks and self.progress:
                task_id = self.active_tasks[self.current_stage]
                self.progress.update(task_id, visible=True)

            return True
        return False


# Convenience functions for common progress patterns


def track_aws_cost_analysis(items: List[Any], console: Optional[Console] = None) -> Iterator[Any]:
    """
    Track AWS cost analysis with enhanced progress.

    Args:
        items: Items to process
        console: Optional console instance

    Yields:
        Items with progress tracking
    """
    tracker = EnhancedProgressTracker(console)

    with tracker.create_enhanced_progress("aws_cost_data", len(items)) as progress:
        progress.start_operation("Analyzing AWS cost data...")

        for i, item in enumerate(items):
            progress.update_step(f"Processing item {i + 1}/{len(items)}", i + 1)
            yield item

        progress.complete_operation("Cost analysis completed")


def track_multi_account_analysis(accounts: List[str], console: Optional[Console] = None) -> Iterator[str]:
    """
    Track multi-account analysis with enhanced progress.

    Args:
        accounts: Account profiles to process
        console: Optional console instance

    Yields:
        Account profiles with progress tracking
    """
    tracker = EnhancedProgressTracker(console)

    with tracker.create_enhanced_progress("multi_account_analysis", len(accounts)) as progress:
        progress.start_operation("Analyzing multiple accounts...")

        for i, account in enumerate(accounts):
            progress.update_step(f"Analyzing account: {account}", i + 1)
            yield account

        progress.complete_operation("Multi-account analysis completed")


@contextmanager
def enhanced_finops_progress(
    operation_name: str, total_steps: int = 100, console: Optional[Console] = None
) -> Iterator[Callable[[int, str], None]]:
    """
    Context manager for enhanced FinOps operations progress.

    Args:
        operation_name: Name of the operation
        total_steps: Total number of progress steps
        console: Optional console instance

    Yields:
        Progress update function: (step, description) -> None
    """
    console = console or rich_console

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="bright_green", finished_style="bright_green"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )

    with progress:
        task_id = progress.add_task(operation_name, total=total_steps)

        def update_progress(step: int, description: str) -> None:
            progress.update(task_id, completed=step, description=description)

        yield update_progress


def create_progress_tracker(console: Optional[Console] = None) -> EnhancedProgressTracker:
    """Factory function to create enhanced progress tracker."""
    return EnhancedProgressTracker(console=console)

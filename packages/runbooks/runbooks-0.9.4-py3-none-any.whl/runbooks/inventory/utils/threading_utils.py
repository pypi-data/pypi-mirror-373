"""
Threading and concurrency utilities for inventory operations.

This module provides thread pool management, concurrent execution helpers,
and progress tracking for multi-threaded inventory collection operations.
"""

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from loguru import logger


@dataclass
class TaskResult:
    """Result from a threaded task execution."""

    task_id: str
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None

    def mark_completed(self, success: bool, result: Any = None, error: Optional[Exception] = None):
        """Mark task as completed with result or error."""
        self.success = success
        self.result = result
        self.error = error
        self.end_time = datetime.utcnow()
        self.duration = self.end_time - self.start_time

    def get_duration_seconds(self) -> float:
        """Get task duration in seconds."""
        if self.duration:
            return self.duration.total_seconds()
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.utcnow() - self.start_time).total_seconds()


@dataclass
class ProgressMetrics:
    """Progress tracking metrics for threaded operations."""

    total_tasks: int = 0
    completed_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    start_time: datetime = field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = None

    def update_progress(self, success: bool):
        """Update progress metrics with task completion."""
        self.completed_tasks += 1
        if success:
            self.successful_tasks += 1
        else:
            self.failed_tasks += 1

        # Update estimated completion time
        if self.completed_tasks > 0:
            elapsed = datetime.utcnow() - self.start_time
            rate = self.completed_tasks / elapsed.total_seconds()
            if rate > 0:
                remaining_seconds = (self.total_tasks - self.completed_tasks) / rate
                self.estimated_completion = datetime.utcnow() + timedelta(seconds=remaining_seconds)

    def get_completion_percentage(self) -> float:
        """Get completion percentage (0-100)."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100

    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        if self.completed_tasks == 0:
            return 0.0
        return (self.successful_tasks / self.completed_tasks) * 100

    def is_complete(self) -> bool:
        """Check if all tasks are completed."""
        return self.completed_tasks >= self.total_tasks

    def get_remaining_tasks(self) -> int:
        """Get number of remaining tasks."""
        return max(0, self.total_tasks - self.completed_tasks)


class ThreadPoolManager:
    """
    Advanced thread pool manager for inventory operations.

    Provides thread pool management with progress tracking, error handling,
    and resource management for concurrent AWS API operations.
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        thread_name_prefix: str = "InventoryWorker",
        progress_callback: Optional[Callable[[ProgressMetrics], None]] = None,
    ):
        """
        Initialize thread pool manager.

        Args:
            max_workers: Maximum number of worker threads (None for auto-detect)
            thread_name_prefix: Prefix for worker thread names
            progress_callback: Callback function for progress updates
        """
        # Auto-detect optimal worker count if not specified
        if max_workers is None:
            import os

            max_workers = min(32, (os.cpu_count() or 1) + 4)

        self.max_workers = max_workers
        self.thread_name_prefix = thread_name_prefix
        self.progress_callback = progress_callback

        self._executor: Optional[ThreadPoolExecutor] = None
        self._futures: Dict[str, Future] = {}
        self._results: Dict[str, TaskResult] = {}
        self._metrics = ProgressMetrics()
        self._lock = threading.Lock()

        logger.debug(f"Initialized ThreadPoolManager with {max_workers} workers")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()

    def start(self):
        """Start the thread pool."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=self.max_workers, thread_name_prefix=self.thread_name_prefix
            )
            logger.debug("Thread pool started")

    def shutdown(self, wait: bool = True):
        """
        Shutdown the thread pool.

        Args:
            wait: Whether to wait for all tasks to complete
        """
        if self._executor:
            self._executor.shutdown(wait=wait)
            self._executor = None
            logger.debug("Thread pool shutdown")

    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> Future:
        """
        Submit a task to the thread pool.

        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Future object for the submitted task

        Raises:
            RuntimeError: If thread pool is not started
        """
        if not self._executor:
            raise RuntimeError("Thread pool not started. Call start() first.")

        # Create task result placeholder
        task_result = TaskResult(task_id=task_id)

        with self._lock:
            self._results[task_id] = task_result
            self._metrics.total_tasks += 1

        # Submit task to executor
        future = self._executor.submit(self._execute_task, task_id, func, *args, **kwargs)
        self._futures[task_id] = future

        logger.debug(f"Submitted task: {task_id}")
        return future

    def _execute_task(self, task_id: str, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a task with error handling and metrics tracking.

        Args:
            task_id: Task identifier
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        result = None
        error = None
        success = False

        try:
            logger.debug(f"Executing task: {task_id}")
            result = func(*args, **kwargs)
            success = True
            logger.debug(f"Task completed successfully: {task_id}")

        except Exception as e:
            error = e
            logger.error(f"Task failed: {task_id} - {e}")

        # Update task result
        with self._lock:
            if task_id in self._results:
                self._results[task_id].mark_completed(success, result, error)
                self._metrics.update_progress(success)

                # Call progress callback if provided
                if self.progress_callback:
                    try:
                        self.progress_callback(self._metrics)
                    except Exception as cb_error:
                        logger.warning(f"Progress callback error: {cb_error}")

        if not success:
            raise error

        return result

    def submit_batch(self, tasks: List[Tuple[str, Callable, tuple, dict]]) -> Dict[str, Future]:
        """
        Submit a batch of tasks to the thread pool.

        Args:
            tasks: List of (task_id, function, args, kwargs) tuples

        Returns:
            Dictionary mapping task IDs to Future objects
        """
        futures = {}

        for task_id, func, args, kwargs in tasks:
            future = self.submit_task(task_id, func, *args, **kwargs)
            futures[task_id] = future

        logger.info(f"Submitted batch of {len(tasks)} tasks")
        return futures

    def wait_for_completion(
        self, timeout: Optional[float] = None, progress_interval: float = 5.0
    ) -> Dict[str, TaskResult]:
        """
        Wait for all submitted tasks to complete.

        Args:
            timeout: Maximum time to wait in seconds
            progress_interval: Interval for progress logging in seconds

        Returns:
            Dictionary mapping task IDs to TaskResult objects
        """
        if not self._futures:
            return self._results.copy()

        logger.info(f"Waiting for {len(self._futures)} tasks to complete")

        start_time = time.time()
        last_progress_time = start_time

        try:
            for future in as_completed(self._futures.values(), timeout=timeout):
                # Log progress periodically
                current_time = time.time()
                if current_time - last_progress_time >= progress_interval:
                    self._log_progress()
                    last_progress_time = current_time

                # Check timeout
                if timeout and (current_time - start_time) >= timeout:
                    logger.warning(f"Timeout reached after {timeout} seconds")
                    break

            # Final progress log
            self._log_progress()

        except TimeoutError:
            logger.error(f"Tasks did not complete within {timeout} seconds")

        # Clean up futures
        self._futures.clear()

        total_time = time.time() - start_time
        logger.info(
            f"Task completion finished in {total_time:.2f} seconds. "
            f"Success rate: {self._metrics.get_success_rate():.1f}%"
        )

        return self._results.copy()

    def get_results(self, completed_only: bool = True) -> Dict[str, TaskResult]:
        """
        Get task results.

        Args:
            completed_only: Whether to return only completed tasks

        Returns:
            Dictionary of task results
        """
        with self._lock:
            if completed_only:
                return {task_id: result for task_id, result in self._results.items() if result.end_time is not None}
            return self._results.copy()

    def get_metrics(self) -> ProgressMetrics:
        """Get current progress metrics."""
        with self._lock:
            return self._metrics

    def get_successful_results(self) -> Dict[str, Any]:
        """Get results from successful tasks only."""
        return {
            task_id: result.result
            for task_id, result in self.get_results().items()
            if result.success and result.result is not None
        }

    def get_failed_tasks(self) -> Dict[str, Exception]:
        """Get errors from failed tasks."""
        return {
            task_id: result.error
            for task_id, result in self.get_results().items()
            if not result.success and result.error is not None
        }

    def _log_progress(self):
        """Log current progress metrics."""
        metrics = self._metrics
        logger.info(
            f"Progress: {metrics.completed_tasks}/{metrics.total_tasks} "
            f"({metrics.get_completion_percentage():.1f}%) - "
            f"Success rate: {metrics.get_success_rate():.1f}%"
        )

        if metrics.estimated_completion:
            remaining = metrics.estimated_completion - datetime.utcnow()
            if remaining.total_seconds() > 0:
                logger.info(f"Estimated completion in {remaining}")

    def cancel_remaining_tasks(self):
        """Cancel all pending tasks."""
        cancelled_count = 0

        for task_id, future in self._futures.items():
            if not future.done() and future.cancel():
                cancelled_count += 1
                logger.debug(f"Cancelled task: {task_id}")

        if cancelled_count > 0:
            logger.info(f"Cancelled {cancelled_count} pending tasks")

    def is_active(self) -> bool:
        """Check if there are active tasks."""
        return bool(self._futures)

    def get_active_task_count(self) -> int:
        """Get number of active (not completed) tasks."""
        return len([f for f in self._futures.values() if not f.done()])


class BatchProcessor:
    """
    Utility for processing large batches of items with threading.

    Provides higher-level batch processing capabilities with automatic
    chunking, error handling, and progress tracking.
    """

    def __init__(
        self,
        batch_size: int = 50,
        max_workers: Optional[int] = None,
        progress_callback: Optional[Callable[[ProgressMetrics], None]] = None,
    ):
        """
        Initialize batch processor.

        Args:
            batch_size: Number of items to process per batch
            max_workers: Maximum number of worker threads
            progress_callback: Callback for progress updates
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.progress_callback = progress_callback

    def process_items(
        self,
        items: List[Any],
        processor_func: Callable[[List[Any]], Any],
        item_id_func: Optional[Callable[[Any], str]] = None,
    ) -> Dict[str, Any]:
        """
        Process a list of items in batches using threading.

        Args:
            items: List of items to process
            processor_func: Function to process each batch
            item_id_func: Function to generate task IDs from items

        Returns:
            Dictionary of batch results
        """
        # Split items into batches
        batches = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            batch_id = f"batch_{i // self.batch_size + 1}"
            batches.append((batch_id, batch))

        logger.info(f"Processing {len(items)} items in {len(batches)} batches")

        # Process batches using thread pool
        with ThreadPoolManager(max_workers=self.max_workers, progress_callback=self.progress_callback) as pool:
            # Submit all batches
            for batch_id, batch in batches:
                pool.submit_task(batch_id, processor_func, batch)

            # Wait for completion
            results = pool.wait_for_completion()

        # Extract successful results
        return pool.get_successful_results()


def run_with_timeout(func: Callable, timeout: float, *args, **kwargs) -> Any:
    """
    Run a function with a timeout using threading.

    Args:
        func: Function to run
        timeout: Timeout in seconds
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result

    Raises:
        TimeoutError: If function doesn't complete within timeout
    """
    result = Queue()
    exception = Queue()

    def target():
        try:
            ret = func(*args, **kwargs)
            result.put(ret)
        except Exception as e:
            exception.put(e)

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        # Thread is still running, timeout occurred
        raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")

    # Check for exceptions
    if not exception.empty():
        raise exception.get()

    # Return result
    if not result.empty():
        return result.get()

    # Should not reach here
    raise RuntimeError("Function completed but no result or exception found")

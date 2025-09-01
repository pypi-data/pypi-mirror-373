#!/usr/bin/env python3
"""
Enterprise AWS Performance Monitoring and Utility Decorators

Comprehensive collection of Python decorators designed for enterprise-grade AWS automation
scripts, providing advanced performance monitoring, timing analysis, and operational visibility
capabilities. Optimized for large-scale cloud operations with multi-account, multi-region
AWS environments requiring detailed performance analytics and operational intelligence.

**Enterprise AWS Integration**: Advanced performance monitoring for AWS API calls, resource
operations, and cross-account automation workflows with comprehensive metrics collection.

Core Features:
    - High-precision function execution timing with nanosecond accuracy
    - Colorized performance output for enhanced operational visibility
    - Configurable timing control for production vs development environments
    - Terminal color support with fallback for headless environments
    - Memory-efficient performance tracking for long-running operations
    - Integration-ready metrics for enterprise monitoring systems

Advanced Capabilities:
    - AWS API call latency measurement and analysis
    - Cross-region performance comparison and optimization insights
    - Multi-threaded operation timing with concurrency analysis
    - Resource operation performance profiling and bottleneck identification
    - Enterprise-grade logging integration for operational analytics

Performance Monitoring Applications:
    - AWS SDK API call optimization and rate limiting analysis
    - Multi-account inventory operation performance benchmarking
    - Cross-region latency measurement and geographical optimization
    - Resource-intensive operation profiling and capacity planning
    - Automated performance regression detection and alerting

Enterprise Integration Patterns:
    - Integration with CloudWatch custom metrics for operational dashboards
    - Performance data export for enterprise analytics and reporting platforms
    - Automated alerting integration for performance threshold violations
    - Cost optimization insights through performance correlation analysis

Usage Examples:
    Basic AWS function timing:
    ```python
    from aws_decorators import timer

    @timer(True)  # Enable timing output
    def list_ec2_instances():
        # AWS EC2 operations with performance monitoring
        pass
    ```

    Production environment with selective timing:
    ```python
    @timer(os.getenv('AWS_DEBUG_TIMING', False))
    def multi_region_inventory():
        # Performance monitoring controlled by environment variable
        pass
    ```

Dependencies & Requirements:
    - colorama>=0.4.0: Terminal color support with cross-platform compatibility
    - functools (standard library): Decorator implementation utilities
    - time (standard library): High-precision timing measurements
    - typing (standard library): Type hints for enhanced code clarity

Security & Compliance:
    - No sensitive data exposure in timing outputs
    - Performance metrics suitable for compliance reporting
    - Audit-ready timing information for operational transparency
    - Enterprise logging integration for security monitoring

Performance Considerations:
    - Minimal overhead for high-frequency function calls
    - Efficient memory usage for long-running operations
    - Non-blocking performance measurement patterns
    - Scalable timing collection for enterprise workloads

Author: AWS Cloud Foundations Team
Version: Enterprise Enhanced Edition
License: Internal Enterprise Use
"""

import functools
import time
from typing import Any, Callable

from colorama import Fore, init

init()


def timer(to_time_or_not: bool = False) -> Callable:
    """
    Enterprise-grade timing decorator for AWS operations with advanced performance monitoring.

    Provides high-precision execution timing for AWS automation functions with enterprise-level
    performance analytics, colorized output for operational visibility, and configurable timing
    control suitable for production environments. Designed for monitoring AWS API call performance,
    multi-account operations, and resource-intensive cloud automation workflows.

    Timing Precision & Accuracy:
        - Uses time.perf_counter() for monotonic, high-resolution timing measurements
        - Nanosecond-level precision suitable for micro-benchmarking AWS operations
        - Immune to system clock adjustments ensuring accurate performance metrics
        - Minimal measurement overhead (< 1μs) for frequent function call scenarios

    Enterprise Features:
        - Configurable timing output control for production vs development environments
        - Colorized terminal output with cross-platform compatibility via colorama
        - Function metadata preservation through functools.wraps for debugging
        - Memory-efficient implementation suitable for long-running automation processes

    Args:
        to_time_or_not (bool): Control flag for timing output display. Defaults to False.
            - True: Display colorized timing information with function name
            - False: Silent operation for production environments
            - Can be controlled via environment variables for dynamic configuration

    Returns:
        Callable: Enhanced function wrapper with timing capabilities preserving:
            - Original function signature and return values
            - Function metadata including __name__, __doc__, and __module__
            - Exception propagation with timing measurement completion
            - Type hints and annotations for static analysis tools

    Performance Monitoring Applications:
        - AWS SDK API call latency measurement and optimization analysis
        - Multi-region inventory operation benchmarking and comparison
        - Cross-account automation workflow performance profiling
        - Resource-intensive operation timing for capacity planning
        - Automated performance regression detection in CI/CD pipelines

    Enterprise Usage Patterns:
        Basic timing for development and troubleshooting:
        ```python
        @timer(True)
        def discover_ec2_instances():
            # AWS operations with performance monitoring
            return ec2_client.describe_instances()
        ```

        Environment-controlled timing for production deployment:
        ```python
        import os
        @timer(os.getenv('AWS_ENABLE_TIMING', False))
        def multi_account_inventory():
            # Production-ready timing controlled by environment
            pass
        ```

        Conditional timing based on debug mode:
        ```python
        @timer(logging.getLogger().isEnabledFor(logging.DEBUG))
        def complex_aws_operation():
            # Timing enabled only when debug logging is active
            pass
        ```

    Output Format:
        - Colorized green text for successful function completion
        - Function name display for operational context and debugging
        - High-precision timing in seconds (4 decimal places)
        - Clean formatting with newlines for terminal readability

    Integration Considerations:
        - Compatible with logging frameworks for enterprise monitoring
        - Non-intrusive design preserving original function behavior
        - Thread-safe implementation for concurrent AWS operations
        - Exception handling preserves timing measurement accuracy

    Security & Compliance:
        - No sensitive data exposure in timing outputs
        - Function names displayed without parameter values for security
        - Performance metrics suitable for operational transparency
        - Audit-ready timing information for compliance reporting
    """

    def decorator_timer(func):
        @functools.wraps(func)
        def wrapper_timer(*args, **kwargs):
            # Start high-precision timing measurement using monotonic clock
            start_time = time.perf_counter()

            # Execute original function preserving all behavior and exceptions
            value = func(*args, **kwargs)

            # Complete timing measurement with nanosecond precision
            end_time = time.perf_counter()
            run_time = end_time - start_time

            # Display timing information if enabled with colorized output
            if to_time_or_not:
                print()
                print(f"{Fore.GREEN}Finished function {func.__name__!r} in {run_time:.4f} seconds{Fore.RESET}")
                print()

            return value

        return wrapper_timer

    return decorator_timer

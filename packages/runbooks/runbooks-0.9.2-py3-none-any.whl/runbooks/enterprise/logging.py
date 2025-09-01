"""
Enterprise-grade structured logging for CloudOps-Runbooks.

This module provides structured logging capabilities for enterprise environments,
including audit trails, performance monitoring, and compliance logging.
"""

import json
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    from loguru import logger as loguru_logger

    _HAS_LOGURU = True
except ImportError:
    import logging

    loguru_logger = logging.getLogger(__name__)
    _HAS_LOGURU = False


class EnterpriseLogger:
    """Enterprise-grade logger with structured logging capabilities."""

    def __init__(
        self,
        name: str = "runbooks",
        level: str = "INFO",
        log_dir: Optional[Path] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_audit: bool = True,
        correlation_id: Optional[str] = None,
    ):
        """
        Initialize enterprise logger.

        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            enable_console: Enable console logging
            enable_file: Enable file logging
            enable_audit: Enable audit logging
            correlation_id: Correlation ID for tracking operations
        """
        self.name = name
        self.level = level
        self.log_dir = log_dir or Path.home() / ".runbooks" / "logs"
        self.correlation_id = correlation_id or self._generate_correlation_id()

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging handlers
        if _HAS_LOGURU:
            self._setup_loguru_logging(enable_console, enable_file, enable_audit)
        else:
            self._setup_standard_logging(enable_console, enable_file)

    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for tracking operations."""
        import uuid

        return f"runbooks-{int(time.time())}-{str(uuid.uuid4())[:8]}"

    def _setup_loguru_logging(self, enable_console: bool, enable_file: bool, enable_audit: bool) -> None:
        """Setup Loguru-based logging."""
        # Remove default handler
        loguru_logger.remove()

        # Console handler
        if enable_console:
            loguru_logger.add(
                sys.stderr,
                level=self.level,
                format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[correlation_id]}</cyan> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>",
                colorize=True,
                filter=lambda record: record["extra"].setdefault("correlation_id", self.correlation_id),
            )

        # Application log file
        if enable_file:
            app_log_file = self.log_dir / "runbooks.log"
            loguru_logger.add(
                app_log_file,
                level="DEBUG",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[correlation_id]} | "
                "{name}:{function}:{line} - {message}",
                rotation="10 MB",
                retention="30 days",
                compression="zip",
                filter=lambda record: record["extra"].setdefault("correlation_id", self.correlation_id),
            )

        # Audit log file
        if enable_audit:
            audit_log_file = self.log_dir / "audit.log"
            loguru_logger.add(
                audit_log_file,
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {extra[correlation_id]} | {message}",
                rotation="50 MB",
                retention="365 days",
                compression="zip",
                filter=lambda record: (
                    record["extra"].setdefault("correlation_id", self.correlation_id)
                    or record.get("extra", {}).get("audit", False)
                ),
            )

        # Performance log file
        performance_log_file = self.log_dir / "performance.log"
        loguru_logger.add(
            performance_log_file,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {extra[correlation_id]} | {message}",
            rotation="20 MB",
            retention="7 days",
            filter=lambda record: (
                record["extra"].setdefault("correlation_id", self.correlation_id)
                or record.get("extra", {}).get("performance", False)
            ),
        )

        # Bind correlation ID
        loguru_logger = loguru_logger.bind(correlation_id=self.correlation_id)

    def _setup_standard_logging(self, enable_console: bool, enable_file: bool) -> None:
        """Setup standard logging as fallback."""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.level))

        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stderr)
            console_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # File handler
        if enable_file:
            file_handler = logging.FileHandler(self.log_dir / "runbooks.log")
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        if _HAS_LOGURU:
            loguru_logger.bind(**kwargs).info(message)
        else:
            logging.getLogger(self.name).info(message)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        if _HAS_LOGURU:
            loguru_logger.bind(**kwargs).debug(message)
        else:
            logging.getLogger(self.name).debug(message)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        if _HAS_LOGURU:
            loguru_logger.bind(**kwargs).warning(message)
        else:
            logging.getLogger(self.name).warning(message)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        if _HAS_LOGURU:
            loguru_logger.bind(**kwargs).error(message)
        else:
            logging.getLogger(self.name).error(message)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        if _HAS_LOGURU:
            loguru_logger.bind(**kwargs).critical(message)
        else:
            logging.getLogger(self.name).critical(message)


class AuditLogger:
    """Specialized logger for audit trails and compliance."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize audit logger."""
        self.log_dir = log_dir or Path.home() / ".runbooks" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.log_dir / "audit.log"

    def log_operation(
        self,
        operation: str,
        user: Optional[str] = None,
        resource: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Log audit operation.

        Args:
            operation: Operation performed
            user: User who performed the operation
            resource: Resource affected
            success: Whether operation was successful
            details: Additional operation details
            correlation_id: Correlation ID for tracking
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "operation": operation,
            "user": user or "system",
            "resource": resource,
            "success": success,
            "details": details or {},
        }

        if _HAS_LOGURU:
            loguru_logger.bind(audit=True, **audit_entry).info(
                f"AUDIT: {operation} - {'SUCCESS' if success else 'FAILED'}"
            )
        else:
            # Fallback to direct file writing
            with open(self.audit_file, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")


class PerformanceLogger:
    """Specialized logger for performance monitoring."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize performance logger."""
        self.log_dir = log_dir or Path.home() / ".runbooks" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.performance_file = self.log_dir / "performance.log"

    def log_performance(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Log performance metrics.

        Args:
            operation: Operation name
            duration: Duration in seconds
            success: Whether operation was successful
            details: Additional performance details
            correlation_id: Correlation ID for tracking
        """
        perf_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "operation": operation,
            "duration_seconds": round(duration, 3),
            "success": success,
            "details": details or {},
        }

        if _HAS_LOGURU:
            loguru_logger.bind(performance=True, **perf_entry).info(
                f"PERFORMANCE: {operation} completed in {duration:.3f}s"
            )
        else:
            # Fallback to direct file writing
            with open(self.performance_file, "a") as f:
                f.write(json.dumps(perf_entry) + "\n")

    @contextmanager
    def measure_operation(
        self,
        operation: str,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        """
        Context manager for measuring operation performance.

        Args:
            operation: Operation name
            details: Additional performance details
            correlation_id: Correlation ID for tracking
        """
        start_time = time.time()
        success = True
        try:
            yield
        except Exception:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            self.log_performance(
                operation=operation,
                duration=duration,
                success=success,
                details=details,
                correlation_id=correlation_id,
            )


def configure_enterprise_logging(
    level: str = "INFO",
    log_dir: Optional[Union[str, Path]] = None,
    correlation_id: Optional[str] = None,
    enable_audit: bool = True,
    enable_performance: bool = True,
) -> EnterpriseLogger:
    """
    Configure enterprise logging for the application.

    Args:
        level: Log level
        log_dir: Log directory path
        correlation_id: Correlation ID for tracking
        enable_audit: Enable audit logging
        enable_performance: Enable performance logging

    Returns:
        Configured enterprise logger
    """
    if isinstance(log_dir, str):
        log_dir = Path(log_dir)

    return EnterpriseLogger(
        level=level,
        log_dir=log_dir,
        correlation_id=correlation_id,
        enable_audit=enable_audit,
    )


def log_operation_performance(
    operation_name: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
):
    """
    Decorator for logging operation performance.

    Args:
        operation_name: Name of operation (defaults to function name)
        details: Additional details to log
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            perf_logger = PerformanceLogger()

            with perf_logger.measure_operation(
                operation=op_name,
                details=details,
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def log_audit_operation(
    operation_name: Optional[str] = None,
    resource_extractor: Optional[callable] = None,
):
    """
    Decorator for logging audit operations.

    Args:
        operation_name: Name of operation (defaults to function name)
        resource_extractor: Function to extract resource from arguments
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            resource = None

            if resource_extractor:
                try:
                    resource = resource_extractor(*args, **kwargs)
                except Exception:
                    pass

            audit_logger = AuditLogger()
            success = True

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                audit_logger.log_operation(
                    operation=op_name,
                    resource=resource,
                    success=success,
                )

        return wrapper

    return decorator


# Global logger instance
_global_logger: Optional[EnterpriseLogger] = None


def get_logger() -> EnterpriseLogger:
    """Get global enterprise logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = configure_enterprise_logging()
    return _global_logger

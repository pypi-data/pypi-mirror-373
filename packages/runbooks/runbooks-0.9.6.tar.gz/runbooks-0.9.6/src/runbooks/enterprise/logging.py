"""
Enterprise-grade structured logging for CloudOps-Runbooks.

This module provides structured logging capabilities for enterprise environments,
including audit trails, performance monitoring, and compliance logging with
Rich CLI integration for user-type specific output.
"""

import json
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Literal

try:
    from loguru import logger as loguru_logger
    _HAS_LOGURU = True
except ImportError:
    import logging
    loguru_logger = logging.getLogger(__name__)
    _HAS_LOGURU = False

# Rich CLI integration
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

# User type definitions for logging levels
UserType = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class EnterpriseRichLogger:
    """Enterprise-grade logger with Rich CLI integration and user-type specific output."""

    def __init__(
        self,
        name: str = "runbooks",
        level: str = "INFO", 
        log_dir: Optional[Path] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_audit: bool = True,
        correlation_id: Optional[str] = None,
        rich_console: Optional[Console] = None,
        json_output: bool = False,
    ):
        """
        Initialize enterprise logger with Rich CLI integration.

        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            enable_console: Enable console logging
            enable_file: Enable file logging
            enable_audit: Enable audit logging
            correlation_id: Correlation ID for tracking operations
            rich_console: Rich console instance for beautiful output
            json_output: Enable structured JSON output for programmatic use
        """
        self.name = name
        self.level = level.upper()
        self.log_dir = log_dir or Path.home() / ".runbooks" / "logs"
        self.correlation_id = correlation_id or self._generate_correlation_id()
        self.json_output = json_output
        
        # Initialize Rich console for beautiful output
        self.console = rich_console or (Console() if _HAS_RICH else None)
        
        # User-type specific styling
        self.level_styles = {
            "DEBUG": {"style": "dim white", "icon": "🔧", "label": "TECH"},
            "INFO": {"style": "cyan", "icon": "ℹ️", "label": "INFO"},
            "WARNING": {"style": "yellow bold", "icon": "⚠️", "label": "BIZ"},
            "ERROR": {"style": "red bold", "icon": "❌", "label": "ALL"},
            "CRITICAL": {"style": "red bold reverse", "icon": "🚨", "label": "ALL"}
        }

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

    def _should_log(self, level: str) -> bool:
        """Determine if message should be logged based on current log level."""
        level_hierarchy = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        return level_hierarchy.get(level, 0) >= level_hierarchy.get(self.level, 1)
    
    def _rich_log(self, level: str, message: str, details: Optional[Dict[str, Any]] = None, progress: Optional[Progress] = None) -> None:
        """Enhanced logging with Rich CLI formatting and user-type specific content."""
        if not self._should_log(level):
            return
            
        # Get level-specific styling
        level_config = self.level_styles.get(level, self.level_styles["INFO"])
        icon = level_config["icon"]
        style = level_config["style"]
        label = level_config["label"]
        
        # Handle JSON output for programmatic use
        if self.json_output:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "correlation_id": self.correlation_id,
                "message": message,
                "details": details or {}
            }
            if self.console:
                self.console.print_json(data=log_entry)
            else:
                print(json.dumps(log_entry))
            return
            
        # Rich console output with user-type specific formatting
        if self.console and _HAS_RICH:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # User-type specific message formatting
            if level == "DEBUG":
                # Tech users - Full details with timing and API info
                self.console.print(f"[dim]{timestamp}[/] {icon} [bold]{label}[/] {message}")
                if details and "aws_api" in details and details["aws_api"]:
                    api_details = details["aws_api"]
                    self.console.print(f"    └─ [dim]API: {api_details.get('service', 'unknown')} / {api_details.get('operation', 'unknown')}[/]")
                    if details.get("request_id"):
                        self.console.print(f"    └─ [dim]Request ID: {details['request_id']}[/]")
                if details.get("duration"):
                    duration_color = "green" if details["duration"] < 1.0 else "yellow" if details["duration"] < 5.0 else "red"
                    self.console.print(f"    └─ [dim]Duration: [{duration_color}]{details['duration']:.3f}s[/dim][/]")
                if details.get("memory_usage"):
                    memory_mb = details["memory_usage"] / 1024 / 1024
                    memory_color = "green" if memory_mb < 50 else "yellow" if memory_mb < 200 else "red"
                    self.console.print(f"    └─ [dim]Memory: [{memory_color}]{memory_mb:.1f}MB[/dim][/]")
                    
            elif level == "INFO":
                # Standard users - Clean status with progress bars
                if progress:
                    self.console.print(f"{icon} {message}", style=style)
                else:
                    info_text = f"[{style}]{icon} {message}[/]"
                    if details.get("resource_count"):
                        info_text += f" ({details['resource_count']} resources)"
                    if details.get("operation_status"):
                        status_color = "green" if details["operation_status"] == "completed" else "yellow"
                        info_text += f" [{status_color}][{details['operation_status']}][/]"
                    self.console.print(info_text)
                    
            elif level == "WARNING":
                # Business users - Recommendations and alerts
                self.console.print(f"{icon} [bold]{label}[/] [{style}]{message}[/]")
                if details.get("recommendation"):
                    self.console.print(f"    💡 [bright_cyan]Recommendation:[/] {details['recommendation']}")
                if details.get("cost_impact"):
                    impact_color = "red" if details["cost_impact"] > 1000 else "yellow" if details["cost_impact"] > 100 else "green"
                    self.console.print(f"    💰 [{impact_color}]Cost Impact:[/] ${details['cost_impact']:,.2f}/month")
                if details.get("savings_opportunity"):
                    self.console.print(f"    💎 [bright_green]Savings Opportunity:[/] ${details['savings_opportunity']:,.2f}/month")
                if details.get("business_impact"):
                    self.console.print(f"    📊 [bright_blue]Business Impact:[/] {details['business_impact']}")
                    
            elif level in ["ERROR", "CRITICAL"]:
                # All users - Clear errors with solutions
                self.console.print(f"{icon} [bold]{label}[/] [{style}]{message}[/]")
                if details.get("solution"):
                    self.console.print(f"    🔧 [bright_blue]Solution:[/] {details['solution']}")
                if details.get("suggested_command"):
                    self.console.print(f"    ⚡ [bright_yellow]Try this command:[/] [cyan]{details['suggested_command']}[/]")
                if details.get("aws_error"):
                    self.console.print(f"    📋 [dim]AWS Error:[/] {details['aws_error']}")
                if details.get("troubleshooting_steps"):
                    self.console.print(f"    📝 [bright_magenta]Troubleshooting Steps:[/]")
                    for i, step in enumerate(details["troubleshooting_steps"], 1):
                        self.console.print(f"       {i}. {step}")
        else:
            # Fallback to standard logging
            print(f"[{level}] {message}")
        
        # Always log to file systems
        if _HAS_LOGURU:
            loguru_logger.bind(correlation_id=self.correlation_id, **(details or {})).info(f"[{level}] {message}")
        else:
            logging.getLogger(self.name).info(f"[{level}] {message}")

    def debug_tech(self, message: str, aws_api: Optional[Dict[str, str]] = None, duration: Optional[float] = None, 
                   memory_usage: Optional[int] = None, request_id: Optional[str] = None, **kwargs) -> None:
        """Log debug message for tech users (SRE/DevOps) with full API details."""
        details = {
            "aws_api": aws_api or {}, 
            "duration": duration, 
            "memory_usage": memory_usage,
            "request_id": request_id,
            **kwargs
        }
        self._rich_log("DEBUG", message, details)

    def info_standard(self, message: str, progress: Optional[Progress] = None, resource_count: Optional[int] = None, 
                     operation_status: Optional[str] = None, **kwargs) -> None:
        """Log info message for standard users with progress indicators."""
        details = {
            "resource_count": resource_count,
            "operation_status": operation_status,
            **kwargs
        }
        self._rich_log("INFO", message, details, progress)

    def warning_business(self, message: str, recommendation: Optional[str] = None, cost_impact: Optional[float] = None, 
                        savings_opportunity: Optional[float] = None, business_impact: Optional[str] = None, **kwargs) -> None:
        """Log warning message for business users with recommendations and cost impact."""
        details = {
            "recommendation": recommendation, 
            "cost_impact": cost_impact,
            "savings_opportunity": savings_opportunity,
            "business_impact": business_impact,
            **kwargs
        }
        self._rich_log("WARNING", message, details)

    def error_all(self, message: str, solution: Optional[str] = None, aws_error: Optional[str] = None, 
                 suggested_command: Optional[str] = None, troubleshooting_steps: Optional[List[str]] = None, **kwargs) -> None:
        """Log error message for all users with clear solutions."""
        details = {
            "solution": solution, 
            "aws_error": aws_error,
            "suggested_command": suggested_command,
            "troubleshooting_steps": troubleshooting_steps or [],
            **kwargs
        }
        self._rich_log("ERROR", message, details)

    # Backward compatibility methods
    def info(self, message: str, **kwargs) -> None:
        """Log info message (backward compatibility)."""
        self.info_standard(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message (backward compatibility)."""
        self.debug_tech(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message (backward compatibility)."""
        self.warning_business(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message (backward compatibility)."""
        self.error_all(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._rich_log("CRITICAL", message, kwargs)

    # Convenience methods for common operations
    def log_aws_operation(self, operation: str, service: str, duration: Optional[float] = None, 
                         success: bool = True, resource_count: Optional[int] = None, **kwargs) -> None:
        """Log AWS operation with appropriate level based on success and duration."""
        if not success:
            self.error_all(
                f"AWS {service} {operation} failed",
                solution=f"Check AWS permissions for {service}:{operation}",
                aws_error=kwargs.get("error"),
                suggested_command=f"aws {service} {operation.replace('_', '-')} --help"
            )
        elif self.level == "DEBUG":
            self.debug_tech(
                f"AWS {service} {operation} completed",
                aws_api={"service": service, "operation": operation},
                duration=duration,
                **kwargs
            )
        else:
            status = "completed" if success else "failed"
            self.info_standard(
                f"{service.upper()} {operation.replace('_', ' ')} {status}",
                resource_count=resource_count,
                operation_status=status
            )

    def log_cost_analysis(self, operation: str, cost_impact: Optional[float] = None, 
                         savings_opportunity: Optional[float] = None, recommendation: Optional[str] = None) -> None:
        """Log cost analysis with business-focused messaging."""
        if cost_impact and cost_impact > 100:  # Significant cost impact
            self.warning_business(
                f"Cost analysis: {operation}",
                cost_impact=cost_impact,
                savings_opportunity=savings_opportunity,
                recommendation=recommendation or f"Review {operation} for optimization opportunities"
            )
        else:
            self.info_standard(f"Cost analysis completed: {operation}")

    def log_performance_metric(self, operation: str, duration: float, threshold: float = 5.0, 
                              memory_usage: Optional[int] = None) -> None:
        """Log performance metrics with appropriate warnings."""
        if duration > threshold:
            self.warning_business(
                f"Performance alert: {operation} took {duration:.2f}s",
                recommendation=f"Consider optimizing {operation} - target: <{threshold}s",
                business_impact="May affect user experience during peak hours"
            )
        elif self.level == "DEBUG":
            self.debug_tech(
                f"Performance: {operation}",
                duration=duration,
                memory_usage=memory_usage
            )
        else:
            self.info_standard(f"{operation} completed", operation_status="completed")

    def log_security_finding(self, finding: str, severity: str = "medium", 
                           remediation_steps: Optional[List[str]] = None) -> None:
        """Log security finding with appropriate level and remediation."""
        if severity.lower() in ["high", "critical"]:
            self.error_all(
                f"Security finding: {finding}",
                solution=f"Immediate action required for {severity} severity finding",
                troubleshooting_steps=remediation_steps or [
                    "Review security policies",
                    "Apply security patches",
                    "Contact security team if needed"
                ]
            )
        elif severity.lower() == "medium":
            self.warning_business(
                f"Security alert: {finding}",
                recommendation="Schedule remediation within next maintenance window",
                business_impact="Potential security risk if not addressed"
            )
        else:
            self.info_standard(f"Security scan: {finding} ({severity} severity)")

    @contextmanager
    def operation_context(self, operation_name: str, **context_details):
        """Context manager for logging operation start/end with performance tracking."""
        import time
        start_time = time.time()
        
        if self.level == "DEBUG":
            self.debug_tech(f"Starting {operation_name}", **context_details)
        else:
            self.info_standard(f"Starting {operation_name}")
        
        success = True
        try:
            yield self
        except Exception as e:
            success = False
            self.error_all(
                f"Operation failed: {operation_name}",
                solution="Check logs above for detailed error information",
                aws_error=str(e)
            )
            raise
        finally:
            duration = time.time() - start_time
            if success:
                if self.level == "DEBUG":
                    self.debug_tech(
                        f"Completed {operation_name}",
                        duration=duration,
                        **context_details
                    )
                else:
                    self.info_standard(
                        f"Completed {operation_name}",
                        operation_status="completed"
                    )
            else:
                self.error_all(f"Failed {operation_name} after {duration:.2f}s")


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
    rich_console: Optional[Console] = None,
    json_output: bool = False,
) -> EnterpriseRichLogger:
    """
    Configure enhanced enterprise logging with Rich CLI integration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Log directory path
        correlation_id: Correlation ID for tracking
        enable_audit: Enable audit logging
        enable_performance: Enable performance logging
        rich_console: Rich console instance for beautiful output
        json_output: Enable structured JSON output

    Returns:
        Configured enterprise logger with Rich CLI support
    """
    if isinstance(log_dir, str):
        log_dir = Path(log_dir)

    return EnterpriseRichLogger(
        level=level,
        log_dir=log_dir,
        correlation_id=correlation_id,
        enable_audit=enable_audit,
        rich_console=rich_console,
        json_output=json_output,
    )

# Backward compatibility alias
EnterpriseLogger = EnterpriseRichLogger


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
_global_logger: Optional[EnterpriseRichLogger] = None


def get_logger() -> EnterpriseRichLogger:
    """Get global enterprise logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = configure_enterprise_logging()
    return _global_logger


def get_context_logger(level: str = "INFO", json_output: bool = False) -> EnterpriseRichLogger:
    """
    Get context-aware enterprise logger with Rich CLI integration.
    
    This is the recommended way to get a logger instance with proper
    Rich CLI integration and user-type specific formatting.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: Enable structured JSON output
        
    Returns:
        Configured enterprise logger with Rich CLI support
    """
    try:
        from runbooks.common.rich_utils import get_context_aware_console
        rich_console = get_context_aware_console()
    except ImportError:
        rich_console = Console() if _HAS_RICH else None
        
    return configure_enterprise_logging(
        level=level,
        rich_console=rich_console,
        json_output=json_output
    )


def get_module_logger(module_name: str, level: str = "INFO", json_output: bool = False) -> EnterpriseRichLogger:
    """
    Get a module-specific enhanced logger with automatic correlation ID and module identification.
    
    This is the recommended method for modules to get their logger instance.
    
    Args:
        module_name: Name of the module (e.g., 'finops', 'inventory', 'security')
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: Enable structured JSON output
        
    Returns:
        Configured enterprise logger with module-specific identification
        
    Example:
        >>> from runbooks.enterprise.logging import get_module_logger
        >>> logger = get_module_logger("finops", level="INFO")
        >>> logger.info_standard("Starting cost analysis", resource_count=10)
        >>> logger.log_cost_analysis("monthly_spend", cost_impact=1500.0, savings_opportunity=450.0)
    """
    try:
        from runbooks.common.rich_utils import get_context_aware_console
        rich_console = get_context_aware_console()
    except ImportError:
        rich_console = Console() if _HAS_RICH else None
        
    logger = EnterpriseRichLogger(
        name=f"runbooks.{module_name}",
        level=level,
        rich_console=rich_console,
        json_output=json_output
    )
    
    # Add module-specific initialization message
    if level == "DEBUG":
        logger.debug_tech(
            f"Module logger initialized for {module_name}",
            aws_api={"service": "logging", "operation": "module_init"},
            duration=0.001
        )
    
    return logger

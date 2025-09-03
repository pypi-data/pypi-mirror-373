"""
Enterprise-grade error handling for CloudOps-Runbooks.

This module provides comprehensive error handling with actionable user guidance,
structured error logging, and user-friendly error messages that help users
resolve issues quickly.
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import click
from loguru import logger

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False


class RunbooksException(Exception):
    """Base exception for all CloudOps-Runbooks errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "RUNBOOKS_ERROR",
        suggestion: Optional[str] = None,
        documentation_url: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize enterprise exception.

        Args:
            message: Error message
            error_code: Unique error code for troubleshooting
            suggestion: Actionable suggestion to resolve the issue
            documentation_url: URL to relevant documentation
            context: Additional context for debugging
        """
        super().__init__(message)
        self.error_code = error_code
        self.suggestion = suggestion
        self.documentation_url = documentation_url
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()


class ConfigurationError(RunbooksException):
    """Configuration-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="CONFIG_ERROR",
            documentation_url="https://cloudops.oceansoft.io/configuration/",
            **kwargs,
        )


class ValidationError(RunbooksException):
    """Input validation errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            documentation_url="https://cloudops.oceansoft.io/validation/",
            **kwargs,
        )


class SecurityError(RunbooksException):
    """Security-related errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message, error_code="SECURITY_ERROR", documentation_url="https://cloudops.oceansoft.io/security/", **kwargs
        )


class AWSServiceError(RunbooksException):
    """AWS service operation errors."""

    def __init__(
        self,
        message: str,
        service: str = "unknown",
        operation: str = "unknown",
        aws_error_code: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            message,
            error_code=f"AWS_{service.upper()}_ERROR",
            documentation_url=f"https://cloudops.oceansoft.io/aws/{service}/",
            **kwargs,
        )
        self.service = service
        self.operation = operation
        self.aws_error_code = aws_error_code


class EnterpriseErrorHandler:
    """Enterprise-grade error handler with comprehensive error management."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize error handler."""
        self.console = console or Console()
        self.error_registry: Dict[str, Dict[str, Any]] = {}
        self._setup_error_registry()

    def _setup_error_registry(self) -> None:
        """Setup common error patterns and their solutions."""
        self.error_registry = {
            "NoCredentialsError": {
                "title": "AWS Credentials Not Found",
                "suggestion": "Configure AWS credentials using 'aws configure' or set environment variables",
                "commands": ["aws configure", "export AWS_PROFILE=your-profile"],
                "documentation": "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html",
            },
            "UnauthorizedOperation": {
                "title": "AWS Permission Denied",
                "suggestion": "Check your AWS IAM permissions for the required service",
                "commands": ["aws sts get-caller-identity", "runbooks security assess --profile your-profile"],
                "documentation": "https://cloudops.oceansoft.io/security/permissions/",
            },
            "ProfileNotFound": {
                "title": "AWS Profile Not Found",
                "suggestion": "Verify the AWS profile exists in ~/.aws/credentials or ~/.aws/config",
                "commands": ["aws configure list-profiles", "runbooks --profile default"],
                "documentation": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html",
            },
            "InvalidRegion": {
                "title": "Invalid AWS Region",
                "suggestion": "Use a valid AWS region (e.g., us-east-1, eu-west-1)",
                "commands": ["aws ec2 describe-regions", "runbooks --region us-east-1"],
                "documentation": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html",
            },
            "FileNotFoundError": {
                "title": "Configuration File Not Found",
                "suggestion": "Initialize configuration or check file path",
                "commands": ["runbooks --help", "runbooks cfat assess --create-config"],
                "documentation": "https://cloudops.oceansoft.io/configuration/",
            },
        }

    def handle_exception(
        self,
        exc: Exception,
        command_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        show_traceback: bool = False,
    ) -> None:
        """
        Handle exception with enterprise-grade error reporting.

        Args:
            exc: Exception to handle
            command_name: Name of command that failed
            context: Additional context information
            show_traceback: Whether to show full traceback
        """
        error_info = self._analyze_exception(exc, context)

        # Log structured error for monitoring
        logger.error(
            "Enterprise error handler activated",
            error_type=type(exc).__name__,
            error_code=getattr(exc, "error_code", "UNKNOWN"),
            command=command_name,
            context=context,
            error_message=str(exc),
        )

        # Display user-friendly error
        self._display_user_error(error_info, show_traceback)

        # Save error details for support
        self._save_error_details(exc, error_info, context)

    def _analyze_exception(self, exc: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze exception and determine appropriate response."""
        exc_name = type(exc).__name__
        exc_str = str(exc)

        # Check for known patterns
        error_pattern = None
        for pattern, info in self.error_registry.items():
            if pattern in exc_name or pattern.lower() in exc_str.lower():
                error_pattern = info
                break

        # Handle RunbooksException instances
        if isinstance(exc, RunbooksException):
            return {
                "title": exc.error_code.replace("_", " ").title(),
                "message": str(exc),
                "suggestion": exc.suggestion,
                "documentation": exc.documentation_url,
                "context": exc.context,
                "commands": [],
                "error_code": exc.error_code,
            }

        # Use pattern if found
        if error_pattern:
            return {
                **error_pattern,
                "message": str(exc),
                "context": context or {},
                "error_code": exc_name,
            }

        # Generic error handling
        return {
            "title": "Unexpected Error",
            "message": str(exc),
            "suggestion": "This appears to be an unexpected error. Please check the logs for details.",
            "commands": ["runbooks --debug", "Check logs in ~/.runbooks/logs/"],
            "documentation": "https://cloudops.oceansoft.io/troubleshooting/",
            "context": context or {},
            "error_code": exc_name,
        }

    def _display_user_error(self, error_info: Dict[str, Any], show_traceback: bool = False) -> None:
        """Display user-friendly error information."""
        if _HAS_RICH:
            self._display_rich_error(error_info, show_traceback)
        else:
            self._display_plain_error(error_info, show_traceback)

    def _display_rich_error(self, error_info: Dict[str, Any], show_traceback: bool = False) -> None:
        """Display error using Rich formatting."""
        # Main error panel
        error_text = Text()
        error_text.append("❌ ", style="red bold")
        error_text.append(error_info["title"], style="red bold")
        error_text.append(f"\n\n{error_info['message']}", style="red")

        if error_info.get("suggestion"):
            error_text.append(f"\n\n💡 Suggestion: {error_info['suggestion']}", style="yellow")

        panel = Panel(
            error_text,
            title="CloudOps Runbooks Error",
            title_align="left",
            border_style="red",
            padding=(1, 2),
        )
        self.console.print(panel)

        # Commands to try
        if error_info.get("commands"):
            self.console.print("\n🔧 Try these commands:", style="cyan bold")
            for cmd in error_info["commands"]:
                self.console.print(f"  {cmd}", style="cyan")

        # Documentation link
        if error_info.get("documentation"):
            self.console.print(f"\n📖 Documentation: {error_info['documentation']}", style="blue underline")

        # Error code for support
        if error_info.get("error_code"):
            self.console.print(f"\n🏷️  Error Code: {error_info['error_code']}", style="dim")

        # Traceback if requested
        if show_traceback:
            self.console.print("\n📋 Traceback:", style="dim")
            self.console.print(traceback.format_exc(), style="dim")

    def _display_plain_error(self, error_info: Dict[str, Any], show_traceback: bool = False) -> None:
        """Display error using plain text formatting."""
        print(f"\n❌ {error_info['title']}")
        print(f"\n{error_info['message']}")

        if error_info.get("suggestion"):
            print(f"\n💡 Suggestion: {error_info['suggestion']}")

        if error_info.get("commands"):
            print(f"\n🔧 Try these commands:")
            for cmd in error_info["commands"]:
                print(f"  {cmd}")

        if error_info.get("documentation"):
            print(f"\n📖 Documentation: {error_info['documentation']}")

        if error_info.get("error_code"):
            print(f"\n🏷️  Error Code: {error_info['error_code']}")

        if show_traceback:
            print(f"\n📋 Traceback:")
            print(traceback.format_exc())

    def _save_error_details(
        self, exc: Exception, error_info: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save error details for support and debugging."""
        try:
            error_log_dir = Path.home() / ".runbooks" / "logs" / "errors"
            error_log_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_file = error_log_dir / f"error_{timestamp}.json"

            error_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "error_info": error_info,
                "context": context,
                "traceback": traceback.format_exc(),
                "system_info": {
                    "python_version": sys.version,
                    "platform": sys.platform,
                },
            }

            import json

            with open(error_file, "w") as f:
                json.dump(error_data, f, indent=2, default=str)

            logger.debug(f"Error details saved to {error_file}")

        except Exception as save_error:
            logger.error(f"Failed to save error details: {save_error}")


def create_user_friendly_error(
    message: str,
    error_type: Type[Exception] = RunbooksException,
    suggestion: Optional[str] = None,
    commands: Optional[List[str]] = None,
    **kwargs,
) -> Exception:
    """
    Create a user-friendly error with actionable guidance.

    Args:
        message: Error message
        error_type: Type of exception to create
        suggestion: Suggested solution
        commands: List of commands to try
        **kwargs: Additional arguments for exception

    Returns:
        Configured exception instance
    """
    if issubclass(error_type, RunbooksException):
        return error_type(message=message, suggestion=suggestion, **kwargs)
    else:
        return error_type(message)


# Global error handler instance
_global_error_handler: Optional[EnterpriseErrorHandler] = None


def get_error_handler() -> EnterpriseErrorHandler:
    """Get global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = EnterpriseErrorHandler()
    return _global_error_handler


def handle_cli_exception(exc: Exception, command_name: Optional[str] = None, debug: bool = False) -> None:
    """
    Handle CLI exception with proper error reporting.

    Args:
        exc: Exception to handle
        command_name: Name of CLI command that failed
        debug: Whether to show debug information
    """
    handler = get_error_handler()
    handler.handle_exception(
        exc,
        command_name=command_name,
        show_traceback=debug,
    )


def enterprise_exception_handler(func):
    """Decorator for enterprise exception handling."""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handler = get_error_handler()
            handler.handle_exception(
                e,
                command_name=func.__name__,
                context={"args": str(args), "kwargs": str(kwargs)},
            )
            raise

    return wrapper

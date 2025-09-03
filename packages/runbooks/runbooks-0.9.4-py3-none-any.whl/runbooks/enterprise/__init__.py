"""
Enterprise enhancements for CloudOps-Runbooks.

This module provides enterprise-grade enhancements including:
- Advanced error handling with actionable guidance
- Structured logging for enterprise monitoring
- Security hardening and compliance validation
- Enhanced configuration management
- Professional documentation standards
"""

from .error_handling import (
    AWSServiceError,
    ConfigurationError,
    EnterpriseErrorHandler,
    RunbooksException,
    SecurityError,
    ValidationError,
    create_user_friendly_error,
)
from .logging import (
    AuditLogger,
    EnterpriseLogger,
    PerformanceLogger,
    configure_enterprise_logging,
)
from .security import (
    ComplianceChecker,
    SecurityValidator,
    ZeroTrustValidator,
    sanitize_input,
    validate_aws_permissions,
)
from .validation import (
    ConfigValidator,
    InputValidator,
    TypeValidator,
    validate_configuration,
    validate_user_input,
)

__all__ = [
    # Error handling
    "EnterpriseErrorHandler",
    "RunbooksException",
    "ConfigurationError",
    "ValidationError",
    "SecurityError",
    "AWSServiceError",
    "create_user_friendly_error",
    # Logging
    "EnterpriseLogger",
    "AuditLogger",
    "PerformanceLogger",
    "configure_enterprise_logging",
    # Security
    "SecurityValidator",
    "ComplianceChecker",
    "ZeroTrustValidator",
    "sanitize_input",
    "validate_aws_permissions",
    # Validation
    "ConfigValidator",
    "InputValidator",
    "TypeValidator",
    "validate_configuration",
    "validate_user_input",
]

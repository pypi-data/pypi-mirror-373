"""
Enterprise AWS Inventory System.

This module provides comprehensive AWS resource discovery and inventory
capabilities across multiple accounts and regions with enterprise-grade
architecture, validation, and automation.

Architecture:
    - core/: Main business logic and orchestration
    - collectors/: Specialized resource collectors by service category
    - models/: Pydantic data models with validation
    - utils/: Reusable utilities and helpers
    - legacy/: Deprecated scripts for backward compatibility

Components:
    - InventoryCollector: Main orchestration engine
    - InventoryFormatter: Multi-format output handling
    - BaseResourceCollector: Abstract base for all collectors
    - AWSResource/AWSAccount: Core data models
    - Validation utilities and AWS helpers
"""

# Core components
# Base collector for extending
from runbooks.inventory.collectors.base import BaseResourceCollector
from runbooks.inventory.core.collector import InventoryCollector
from runbooks.inventory.core.formatter import InventoryFormatter

# Data models
from runbooks.inventory.models.account import AWSAccount, OrganizationAccount
from runbooks.inventory.models.inventory import InventoryMetadata, InventoryResult
from runbooks.inventory.models.resource import AWSResource, ResourceState, ResourceType
from runbooks.inventory.utils.aws_helpers import get_boto3_session, validate_aws_credentials

# Utilities
from runbooks.inventory.utils.validation import validate_aws_account_id, validate_resource_types

__version__ = "1.0.0"

__all__ = [
    # Core functionality
    "InventoryCollector",
    "InventoryFormatter",
    # Base classes for extension
    "BaseResourceCollector",
    # Data models
    "AWSAccount",
    "OrganizationAccount",
    "AWSResource",
    "InventoryResult",
    "InventoryMetadata",
    # Enums
    "ResourceState",
    "ResourceType",
    # Utilities
    "validate_aws_account_id",
    "validate_resource_types",
    "get_boto3_session",
    "validate_aws_credentials",
    # Version
    "__version__",
]

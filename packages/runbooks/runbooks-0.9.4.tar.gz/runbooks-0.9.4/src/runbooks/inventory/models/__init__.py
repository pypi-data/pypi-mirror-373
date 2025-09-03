"""
Data models for AWS inventory system.

This module provides Pydantic-based models for representing AWS accounts,
resources, and inventory results with proper validation and serialization.

Models:
    - account: AWS account representation and organization structure
    - resource: Individual AWS resource models with metadata
    - inventory: Inventory collection results and aggregations
"""

from runbooks.inventory.models.account import AWSAccount, OrganizationAccount
from runbooks.inventory.models.inventory import InventoryMetadata, InventoryResult
from runbooks.inventory.models.resource import AWSResource, ResourceMetadata

__all__ = [
    "AWSAccount",
    "OrganizationAccount",
    "AWSResource",
    "ResourceMetadata",
    "InventoryResult",
    "InventoryMetadata",
]

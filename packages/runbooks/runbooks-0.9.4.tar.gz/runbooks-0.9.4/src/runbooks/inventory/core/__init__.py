"""
Core inventory engine for AWS resource discovery.

This module contains the main business logic for orchestrating inventory
collection across multiple AWS accounts and regions.

Components:
    - collector: Main inventory orchestration
    - formatter: Output formatting and export capabilities
    - session_manager: AWS session and credential management
"""

from runbooks.inventory.core.collector import InventoryCollector
from runbooks.inventory.core.formatter import InventoryFormatter

__all__ = [
    "InventoryCollector",
    "InventoryFormatter",
]

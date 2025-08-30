"""
FinOps Dashboard Configuration - Backward Compatibility Module

This module provides backward compatibility for tests and legacy code that expect
the FinOpsConfig class and related enterprise dashboard components.

Note: Core functionality has been integrated into dashboard_runner.py for better
maintainability following "less code = better code" principle.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FinOpsConfig:
    """
    Backward compatibility configuration class for FinOps dashboard.
    
    This class provides a simple configuration interface for tests and legacy
    components while the main functionality has been integrated into
    dashboard_runner.py for better maintainability.
    """
    profiles: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    time_range: Optional[int] = None
    export_formats: List[str] = field(default_factory=lambda: ['json'])
    include_budget_data: bool = True
    include_resource_analysis: bool = True
    
    def __post_init__(self):
        """Initialize default values if needed."""
        if not self.profiles:
            self.profiles = ["default"]
        
        if not self.regions:
            self.regions = ["us-east-1", "us-west-2", "ap-southeast-2"]


# Export for backward compatibility
__all__ = ["FinOpsConfig"]
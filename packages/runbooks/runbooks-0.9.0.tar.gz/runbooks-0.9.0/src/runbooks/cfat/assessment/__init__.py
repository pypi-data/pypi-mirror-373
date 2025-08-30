"""
Assessment Engine for Cloud Foundations Assessment Tool.

This module contains the core assessment logic including:
- Assessment execution orchestration
- AWS resource collectors
- Compliance rule validation
- Check discovery and management

The assessment engine provides modular, extensible assessment
capabilities with enterprise-grade performance and reliability.
"""

from runbooks.cfat.assessment.collectors import (
    CloudTrailCollector,
    ConfigCollector,
    EC2Collector,
    IAMCollector,
    OrganizationsCollector,
    VPCCollector,
)
from runbooks.cfat.assessment.runner import CloudFoundationsAssessment
from runbooks.cfat.assessment.validators import (
    ComplianceValidator,
    OperationalValidator,
    SecurityValidator,
)

__all__ = [
    "CloudFoundationsAssessment",
    "IAMCollector",
    "VPCCollector",
    "CloudTrailCollector",
    "ConfigCollector",
    "OrganizationsCollector",
    "EC2Collector",
    "ComplianceValidator",
    "SecurityValidator",
    "OperationalValidator",
]

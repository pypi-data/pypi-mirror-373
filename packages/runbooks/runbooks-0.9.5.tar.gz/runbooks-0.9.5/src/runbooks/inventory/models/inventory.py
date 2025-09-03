"""
Inventory result models for collection aggregation.

This module provides models for representing the results of inventory
collection operations, including metadata, statistics, and aggregations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, validator

from runbooks.inventory.models.account import AWSAccount
from runbooks.inventory.models.resource import AWSResource


class InventoryStatus(str, Enum):
    """Inventory collection status."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    CANCELLED = "cancelled"


class CollectionScope(str, Enum):
    """Scope of inventory collection."""

    SINGLE_ACCOUNT = "single_account"
    ORGANIZATION = "organization"
    MULTI_ACCOUNT = "multi_account"
    CUSTOM = "custom"


@dataclass
class CollectionError:
    """Error information from collection operations."""

    account_id: str
    region: str
    service: str
    error_code: str
    error_message: str
    timestamp: datetime
    retry_count: int = 0

    def is_retryable(self) -> bool:
        """Check if this error type is retryable."""
        retryable_codes = {"Throttling", "RequestLimitExceeded", "ServiceUnavailable", "InternalError", "NetworkError"}
        return self.error_code in retryable_codes


@dataclass
class InventoryStatistics:
    """Statistical summary of inventory collection."""

    # Resource counts
    total_resources: int = 0
    resources_by_type: Dict[str, int] = field(default_factory=dict)
    resources_by_account: Dict[str, int] = field(default_factory=dict)
    resources_by_region: Dict[str, int] = field(default_factory=dict)
    resources_by_service: Dict[str, int] = field(default_factory=dict)

    # State distribution
    active_resources: int = 0
    inactive_resources: int = 0
    billable_resources: int = 0

    # Cost information
    total_estimated_cost: float = 0.0
    cost_by_account: Dict[str, float] = field(default_factory=dict)
    cost_by_service: Dict[str, float] = field(default_factory=dict)

    # Collection metrics
    accounts_scanned: int = 0
    regions_scanned: int = 0
    services_scanned: int = 0
    api_calls_made: int = 0

    # Error tracking
    total_errors: int = 0
    errors_by_service: Dict[str, int] = field(default_factory=dict)

    def add_resource(self, resource: AWSResource) -> None:
        """Add a resource to the statistics."""
        self.total_resources += 1

        # Update type count
        resource_type = resource.resource_type
        self.resources_by_type[resource_type] = self.resources_by_type.get(resource_type, 0) + 1

        # Update account count
        account_id = resource.account_id
        self.resources_by_account[account_id] = self.resources_by_account.get(account_id, 0) + 1

        # Update region count
        region = resource.region
        self.resources_by_region[region] = self.resources_by_region.get(region, 0) + 1

        # Update service count
        service = resource.get_service_name()
        self.resources_by_service[service] = self.resources_by_service.get(service, 0) + 1

        # Update state counts
        if resource.is_active():
            self.active_resources += 1
        else:
            self.inactive_resources += 1

        if resource.is_billable():
            self.billable_resources += 1

        # Update cost information
        cost = resource.get_cost_estimate()
        if cost > 0:
            self.total_estimated_cost += cost

            self.cost_by_account[account_id] = self.cost_by_account.get(account_id, 0.0) + cost

            self.cost_by_service[service] = self.cost_by_service.get(service, 0.0) + cost

    def add_error(self, error: CollectionError) -> None:
        """Add an error to the statistics."""
        self.total_errors += 1

        service = error.service
        self.errors_by_service[service] = self.errors_by_service.get(service, 0) + 1

    def get_success_rate(self) -> float:
        """Calculate collection success rate."""
        total_operations = self.total_resources + self.total_errors
        if total_operations == 0:
            return 0.0
        return (self.total_resources / total_operations) * 100

    def get_top_resource_types(self, limit: int = 10) -> List[tuple]:
        """Get top resource types by count."""
        return sorted(self.resources_by_type.items(), key=lambda x: x[1], reverse=True)[:limit]

    def get_most_expensive_services(self, limit: int = 10) -> List[tuple]:
        """Get most expensive services by cost."""
        return sorted(self.cost_by_service.items(), key=lambda x: x[1], reverse=True)[:limit]


class InventoryMetadata(BaseModel):
    """
    Metadata about an inventory collection operation.

    Provides comprehensive information about when, how, and what
    was collected during an inventory operation.
    """

    # Collection identification
    collection_id: str = Field(..., description="Unique identifier for this collection")

    collection_name: Optional[str] = Field(None, description="Human-readable name for this collection")

    # Timing information
    start_time: datetime = Field(..., description="Collection start timestamp")

    end_time: Optional[datetime] = Field(None, description="Collection completion timestamp")

    duration: Optional[timedelta] = Field(None, description="Total collection duration")

    # Scope and configuration
    scope: CollectionScope = Field(..., description="Scope of this collection")

    target_accounts: List[str] = Field(default_factory=list, description="Account IDs that were targeted")

    target_regions: List[str] = Field(default_factory=list, description="Regions that were scanned")

    target_resource_types: Set[str] = Field(default_factory=set, description="Resource types that were collected")

    # Collection parameters
    include_costs: bool = Field(False, description="Whether cost information was collected")

    parallel_execution: bool = Field(True, description="Whether collection used parallel processing")

    max_workers: Optional[int] = Field(None, description="Maximum number of worker threads used")

    # Collector information
    collector_version: str = Field(..., description="Version of collector used")

    collector_config: Dict[str, Any] = Field(default_factory=dict, description="Collector configuration parameters")

    # Status and results
    status: InventoryStatus = Field(InventoryStatus.IN_PROGRESS, description="Current collection status")

    status_message: Optional[str] = Field(None, description="Additional status information")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            timedelta: lambda v: v.total_seconds(),
            set: lambda v: list(v),
        }

    def mark_completed(self, status: InventoryStatus = InventoryStatus.SUCCESS) -> None:
        """Mark collection as completed."""
        self.end_time = datetime.utcnow()
        self.duration = self.end_time - self.start_time
        self.status = status

    def get_duration_seconds(self) -> float:
        """Get collection duration in seconds."""
        if self.duration:
            return self.duration.total_seconds()
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.utcnow() - self.start_time).total_seconds()


class InventoryResult(BaseModel):
    """
    Complete results from an inventory collection operation.

    Aggregates all resources discovered, statistics, errors, and metadata
    from a complete inventory collection run.
    """

    # Core data
    metadata: InventoryMetadata = Field(..., description="Collection metadata and configuration")

    resources: List[AWSResource] = Field(default_factory=list, description="All discovered resources")

    accounts: List[AWSAccount] = Field(default_factory=list, description="Account information for scanned accounts")

    # Statistics and analytics
    statistics: InventoryStatistics = Field(
        default_factory=InventoryStatistics, description="Statistical summary of collection"
    )

    # Error tracking
    errors: List[CollectionError] = Field(default_factory=list, description="Errors encountered during collection")

    # Performance metrics
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance and timing metrics")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat(), timedelta: lambda v: v.total_seconds()}

    def add_resource(self, resource: AWSResource) -> None:
        """Add a resource to the results."""
        self.resources.append(resource)
        self.statistics.add_resource(resource)

    def add_error(self, error: CollectionError) -> None:
        """Add an error to the results."""
        self.errors.append(error)
        self.statistics.add_error(error)

    def get_resources_by_type(self, resource_type: str) -> List[AWSResource]:
        """Get all resources of a specific type."""
        return [r for r in self.resources if r.resource_type == resource_type]

    def get_resources_by_account(self, account_id: str) -> List[AWSResource]:
        """Get all resources from a specific account."""
        return [r for r in self.resources if r.account_id == account_id]

    def get_resources_by_region(self, region: str) -> List[AWSResource]:
        """Get all resources from a specific region."""
        return [r for r in self.resources if r.region == region]

    def get_active_resources(self) -> List[AWSResource]:
        """Get all active resources."""
        return [r for r in self.resources if r.is_active()]

    def get_billable_resources(self) -> List[AWSResource]:
        """Get all billable resources."""
        return [r for r in self.resources if r.is_billable()]

    def get_resources_with_tag(self, key: str, value: Optional[str] = None) -> List[AWSResource]:
        """Get resources that have a specific tag."""
        return [r for r in self.resources if r.has_tag(key, value)]

    def get_total_cost_estimate(self) -> float:
        """Get total estimated monthly cost."""
        return self.statistics.total_estimated_cost

    def get_collection_summary(self) -> Dict[str, Any]:
        """Get a summary of the collection results."""
        return {
            "collection_id": self.metadata.collection_id,
            "status": self.metadata.status,
            "duration_seconds": self.metadata.get_duration_seconds(),
            "total_resources": self.statistics.total_resources,
            "total_accounts": len(self.accounts),
            "total_regions": self.statistics.regions_scanned,
            "total_errors": self.statistics.total_errors,
            "success_rate": self.statistics.get_success_rate(),
            "total_cost_estimate": self.statistics.total_estimated_cost,
            "scope": self.metadata.scope,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return self.dict()

    def __len__(self) -> int:
        """Return number of resources collected."""
        return len(self.resources)

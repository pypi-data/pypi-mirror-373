"""
AWS resource models for inventory system.

This module provides Pydantic models for representing individual AWS
resources with proper validation, metadata, and cost information.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class ResourceState(str, Enum):
    """AWS resource state enumeration."""

    RUNNING = "running"
    STOPPED = "stopped"
    PENDING = "pending"
    TERMINATED = "terminated"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    IN_USE = "in-use"
    CREATING = "creating"
    DELETING = "deleting"
    UNKNOWN = "unknown"


class ResourceType(str, Enum):
    """Supported AWS resource types."""

    # Compute
    EC2_INSTANCE = "ec2:instance"
    LAMBDA_FUNCTION = "lambda:function"
    ECS_CLUSTER = "ecs:cluster"
    ECS_SERVICE = "ecs:service"
    ECS_TASK = "ecs:task"

    # Storage
    S3_BUCKET = "s3:bucket"
    EBS_VOLUME = "ebs:volume"
    EBS_SNAPSHOT = "ebs:snapshot"
    EFS_FILESYSTEM = "efs:filesystem"

    # Database
    RDS_INSTANCE = "rds:instance"
    RDS_CLUSTER = "rds:cluster"
    DYNAMODB_TABLE = "dynamodb:table"
    ELASTICACHE_CLUSTER = "elasticache:cluster"

    # Network
    VPC = "vpc:vpc"
    SUBNET = "vpc:subnet"
    SECURITY_GROUP = "vpc:security-group"
    LOAD_BALANCER = "elb:load-balancer"
    ENI = "ec2:network-interface"

    # Security & Identity
    IAM_USER = "iam:user"
    IAM_ROLE = "iam:role"
    IAM_POLICY = "iam:policy"
    GUARDDUTY_DETECTOR = "guardduty:detector"

    # Management & Governance
    CLOUDFORMATION_STACK = "cloudformation:stack"
    CLOUDFORMATION_STACKSET = "cloudformation:stackset"
    CONFIG_RECORDER = "config:recorder"
    CLOUDTRAIL_TRAIL = "cloudtrail:trail"


@dataclass
class ResourceCost:
    """Cost information for an AWS resource."""

    monthly_cost: Optional[float] = None
    currency: str = "USD"
    cost_center: Optional[str] = None
    billing_period: Optional[str] = None
    cost_breakdown: Dict[str, float] = None

    def __post_init__(self):
        """Initialize cost breakdown if not provided."""
        if self.cost_breakdown is None:
            self.cost_breakdown = {}


class ResourceMetadata(BaseModel):
    """
    Metadata for AWS resource collection and management.

    Provides context about when and how the resource was discovered,
    along with collection-specific information.
    """

    account_id: str = Field(..., pattern=r"^\d{12}$", description="AWS account ID where resource exists")

    region: str = Field(..., description="AWS region where resource is located")

    service_category: str = Field(..., description="AWS service category (compute, storage, etc.)")

    collection_timestamp: datetime = Field(..., description="When this resource was discovered")

    collector_version: Optional[str] = Field(None, description="Version of collector that discovered this resource")

    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw AWS API response data")

    discovery_method: str = Field("api", description="How this resource was discovered (api, cloudtrail, etc.)")

    confidence_score: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in resource data accuracy (0.0-1.0)")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class AWSResource(BaseModel):
    """
    Comprehensive model for AWS resources.

    Represents any AWS resource with standardized fields for identification,
    state management, cost tracking, and metadata.
    """

    # Core identification
    resource_id: str = Field(..., description="AWS resource identifier (instance ID, bucket name, etc.)")

    resource_type: str = Field(..., description="Type of AWS resource")

    resource_arn: Optional[str] = Field(None, description="Amazon Resource Name (ARN) if available")

    resource_name: Optional[str] = Field(None, description="Human-readable resource name")

    # State and lifecycle
    state: ResourceState = Field(ResourceState.UNKNOWN, description="Current resource state")

    creation_date: Optional[datetime] = Field(None, description="Resource creation timestamp")

    last_modified_date: Optional[datetime] = Field(None, description="Last modification timestamp")

    # Location and organization
    account_id: str = Field(..., pattern=r"^\d{12}$", description="AWS account ID")

    region: str = Field(..., description="AWS region")

    availability_zone: Optional[str] = Field(None, description="Availability zone if applicable")

    # Configuration and properties
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Resource-specific configuration details")

    tags: Dict[str, str] = Field(default_factory=dict, description="Resource tags")

    # Security and compliance
    security_groups: List[str] = Field(default_factory=list, description="Associated security group IDs")

    encryption_status: Optional[str] = Field(None, description="Encryption status (encrypted, not-encrypted, unknown)")

    public_access: bool = Field(False, description="Whether resource has public internet access")

    # Cost information
    cost_info: Optional[ResourceCost] = Field(None, description="Cost information if available")

    # Metadata
    metadata: ResourceMetadata = Field(..., description="Collection and discovery metadata")

    # Relationships
    dependencies: List[str] = Field(default_factory=list, description="List of resource ARNs this resource depends on")

    dependents: List[str] = Field(
        default_factory=list, description="List of resource ARNs that depend on this resource"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

    @validator("resource_arn")
    def validate_arn_format(cls, v):
        """Validate ARN format if provided."""
        if v and not v.startswith("arn:aws:"):
            raise ValueError('ARN must start with "arn:aws:"')
        return v

    @validator("account_id")
    def validate_account_id(cls, v):
        """Validate account ID format."""
        if not v.isdigit() or len(v) != 12:
            raise ValueError("Account ID must be exactly 12 digits")
        return v

    def is_active(self) -> bool:
        """Check if resource is in an active state."""
        active_states = {ResourceState.RUNNING, ResourceState.AVAILABLE, ResourceState.IN_USE}
        return self.state in active_states

    def is_billable(self) -> bool:
        """Check if resource is likely to incur costs."""
        # Most resources are billable unless explicitly stopped/terminated
        non_billable_states = {ResourceState.STOPPED, ResourceState.TERMINATED, ResourceState.UNAVAILABLE}
        return self.state not in non_billable_states

    def get_cost_estimate(self) -> float:
        """Get monthly cost estimate for this resource."""
        if self.cost_info and self.cost_info.monthly_cost:
            return self.cost_info.monthly_cost
        return 0.0

    def has_tag(self, key: str, value: Optional[str] = None) -> bool:
        """Check if resource has a specific tag."""
        if key not in self.tags:
            return False
        if value is None:
            return True
        return self.tags[key] == value

    def get_tag(self, key: str, default: str = "") -> str:
        """Get tag value with optional default."""
        return self.tags.get(key, default)

    def add_dependency(self, resource_arn: str) -> None:
        """Add a resource dependency."""
        if resource_arn not in self.dependencies:
            self.dependencies.append(resource_arn)

    def add_dependent(self, resource_arn: str) -> None:
        """Add a dependent resource."""
        if resource_arn not in self.dependents:
            self.dependents.append(resource_arn)

    def get_service_name(self) -> str:
        """Extract AWS service name from resource type."""
        if ":" in self.resource_type:
            return self.resource_type.split(":")[0]
        return self.resource_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return self.dict()

    def __str__(self) -> str:
        """String representation."""
        name = self.resource_name or self.resource_id
        return f"AWSResource({self.resource_type}: {name})"

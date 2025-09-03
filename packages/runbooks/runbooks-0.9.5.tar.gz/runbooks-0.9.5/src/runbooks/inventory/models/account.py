"""
AWS account models for inventory operations.

This module provides Pydantic models representing AWS accounts and
organization structures with proper validation and type safety.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field, validator


class AccountStatus(str, Enum):
    """AWS account status enumeration."""

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_CLOSURE = "PENDING_CLOSURE"


class OrganizationUnitType(str, Enum):
    """Organization unit type enumeration."""

    ROOT = "ROOT"
    ORGANIZATIONAL_UNIT = "ORGANIZATIONAL_UNIT"


@dataclass
class AWSCredentials:
    """AWS credentials for account access."""

    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
    profile_name: Optional[str] = None
    role_arn: Optional[str] = None
    external_id: Optional[str] = None

    def __post_init__(self):
        """Validate credentials configuration."""
        has_keys = self.access_key_id and self.secret_access_key
        has_profile = self.profile_name
        has_role = self.role_arn

        if not any([has_keys, has_profile, has_role]):
            raise ValueError("Must provide either access keys, profile name, or role ARN")


class AWSAccount(BaseModel):
    """
    Represents an AWS account with metadata and access information.

    This model provides a comprehensive representation of an AWS account
    including organization context, contact information, and access credentials.
    """

    account_id: str = Field(..., pattern=r"^\d{12}$", description="12-digit AWS account ID")

    account_name: Optional[str] = Field(None, description="Human-readable account name")

    email: Optional[str] = Field(None, description="Root email address for the account")

    status: AccountStatus = Field(AccountStatus.ACTIVE, description="Current account status")

    creation_date: Optional[datetime] = Field(None, description="Account creation timestamp")

    # Organization information
    organization_id: Optional[str] = Field(None, description="AWS Organizations ID if account is in an organization")

    organizational_unit_id: Optional[str] = Field(None, description="Organizational Unit ID containing this account")

    organizational_unit_name: Optional[str] = Field(None, description="Organizational Unit name")

    is_management_account: bool = Field(False, description="Whether this is the organization management account")

    # Access and permissions
    default_region: str = Field("us-east-1", description="Default AWS region for operations")

    available_regions: Set[str] = Field(default_factory=set, description="Set of available/enabled regions")

    # Metadata
    tags: Dict[str, str] = Field(default_factory=dict, description="Account-level tags")

    discovered_services: Set[str] = Field(default_factory=set, description="AWS services discovered in this account")

    last_inventory_date: Optional[datetime] = Field(None, description="Last successful inventory collection timestamp")

    # Cost and billing (if available)
    monthly_cost_estimate: Optional[float] = Field(None, description="Monthly cost estimate in USD")

    cost_center: Optional[str] = Field(None, description="Cost center or billing code")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        extra = "forbid"
        json_encoders = {datetime: lambda v: v.isoformat(), set: lambda v: list(v)}

    @validator("account_id")
    def validate_account_id(cls, v):
        """Validate account ID format."""
        if not v.isdigit() or len(v) != 12:
            raise ValueError("Account ID must be exactly 12 digits")
        return v

    @validator("available_regions")
    def validate_regions(cls, v):
        """Validate region format."""
        valid_region_pattern = r"^[a-z]{2,3}-[a-z]+-\d+$"
        import re

        for region in v:
            if not re.match(valid_region_pattern, region):
                raise ValueError(f"Invalid region format: {region}")
        return v

    def is_in_organization(self) -> bool:
        """Check if account is part of an AWS Organization."""
        return self.organization_id is not None

    def add_discovered_service(self, service: str) -> None:
        """Add a service to the discovered services set."""
        self.discovered_services.add(service)

    def get_region_count(self) -> int:
        """Get the number of available regions."""
        return len(self.available_regions)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return self.dict()

    def __str__(self) -> str:
        """String representation."""
        name = self.account_name or "Unnamed"
        return f"AWSAccount({self.account_id}, {name})"


class OrganizationAccount(AWSAccount):
    """
    Extended account model for organization management accounts.

    Provides additional capabilities for managing organization-wide
    operations and cross-account resource discovery.
    """

    child_accounts: List[AWSAccount] = Field(
        default_factory=list, description="List of child accounts in this organization"
    )

    organizational_units: Dict[str, str] = Field(default_factory=dict, description="Mapping of OU IDs to OU names")

    service_control_policies: List[str] = Field(
        default_factory=list, description="List of SCP IDs attached to the organization"
    )

    feature_set: str = Field("ALL", description="Organization feature set (ALL or CONSOLIDATED_BILLING)")

    def add_child_account(self, account: AWSAccount) -> None:
        """Add a child account to the organization."""
        account.organization_id = self.organization_id
        self.child_accounts.append(account)

    def get_child_account(self, account_id: str) -> Optional[AWSAccount]:
        """Get a specific child account by ID."""
        for account in self.child_accounts:
            if account.account_id == account_id:
                return account
        return None

    def get_accounts_by_ou(self, ou_id: str) -> List[AWSAccount]:
        """Get all accounts in a specific organizational unit."""
        return [account for account in self.child_accounts if account.organizational_unit_id == ou_id]

    def get_total_accounts(self) -> int:
        """Get total number of accounts in organization (including management)."""
        return len(self.child_accounts) + 1

    def get_organization_summary(self) -> Dict:
        """Get organization summary statistics."""
        return {
            "management_account": self.account_id,
            "total_accounts": self.get_total_accounts(),
            "organizational_units": len(self.organizational_units),
            "service_control_policies": len(self.service_control_policies),
            "feature_set": self.feature_set,
            "active_accounts": sum(1 for acc in self.child_accounts if acc.status == AccountStatus.ACTIVE),
        }

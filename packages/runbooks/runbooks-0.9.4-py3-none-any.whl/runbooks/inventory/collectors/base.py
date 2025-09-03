"""
Base collector class for AWS resource discovery.

This module provides the abstract base class that all resource collectors
must implement, ensuring consistent interfaces and patterns across all
AWS service categories.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger

from runbooks.inventory.models.account import AWSAccount
from runbooks.inventory.models.resource import AWSResource, ResourceMetadata


@dataclass
class CollectionContext:
    """Context information for resource collection operations."""

    account: AWSAccount
    region: str
    resource_types: Set[str]
    include_costs: bool = False
    dry_run: bool = False
    collection_timestamp: datetime = None

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.collection_timestamp is None:
            self.collection_timestamp = datetime.utcnow()


class BaseResourceCollector(ABC):
    """
    Abstract base class for AWS resource collectors.

    All resource collectors must inherit from this class and implement
    the required abstract methods. This ensures consistent behavior
    and interfaces across all AWS service categories.

    Attributes:
        service_category: AWS service category (e.g., 'compute', 'storage')
        supported_resources: Set of resource types this collector handles
        requires_org_access: Whether collector needs organization-level permissions
    """

    service_category: str = ""
    supported_resources: Set[str] = set()
    requires_org_access: bool = False

    def __init__(self, session: boto3.Session):
        """
        Initialize the collector with an AWS session.

        Args:
            session: Configured boto3 session with appropriate credentials

        Raises:
            NoCredentialsError: If session lacks valid AWS credentials
            ValueError: If session is invalid or missing required permissions
        """
        self.session = session
        self._validate_session()
        self._clients = {}
        self._region_cache = {}

        logger.debug(f"Initialized {self.__class__.__name__} for category '{self.service_category}'")

    def _validate_session(self) -> None:
        """
        Validate the AWS session has required credentials.

        Raises:
            NoCredentialsError: If no credentials are available
            ValueError: If credentials are invalid
        """
        try:
            # Test credentials by getting caller identity
            sts_client = self.session.client("sts")
            identity = sts_client.get_caller_identity()
            logger.debug(f"Session validated for account: {identity.get('Account')}")
        except NoCredentialsError:
            raise NoCredentialsError("AWS session lacks valid credentials")
        except ClientError as e:
            raise ValueError(f"Invalid AWS session: {e}")

    def get_client(self, service: str, region: str) -> boto3.client:
        """
        Get a cached boto3 client for the specified service and region.

        Args:
            service: AWS service name (e.g., 'ec2', 's3')
            region: AWS region name

        Returns:
            Configured boto3 client
        """
        client_key = f"{service}:{region}"
        if client_key not in self._clients:
            self._clients[client_key] = self.session.client(service, region_name=region)
        return self._clients[client_key]

    @abstractmethod
    def collect_resources(
        self, context: CollectionContext, resource_filters: Optional[Dict[str, Any]] = None
    ) -> List[AWSResource]:
        """
        Collect AWS resources for this service category.

        Args:
            context: Collection context with account, region, and options
            resource_filters: Optional filters to apply during collection

        Returns:
            List of discovered AWS resources

        Raises:
            ClientError: If AWS API calls fail
            ValueError: If context or filters are invalid
        """
        pass

    @abstractmethod
    def get_resource_costs(self, resources: List[AWSResource], context: CollectionContext) -> Dict[str, float]:
        """
        Get cost information for the collected resources.

        Args:
            resources: List of resources to get costs for
            context: Collection context

        Returns:
            Dictionary mapping resource ARNs to costs

        Note:
            This method should gracefully handle cases where cost
            information is not available or accessible.
        """
        pass

    def can_collect_resource_type(self, resource_type: str) -> bool:
        """
        Check if this collector can handle the specified resource type.

        Args:
            resource_type: Resource type to check

        Returns:
            True if this collector supports the resource type
        """
        return resource_type in self.supported_resources

    def get_available_regions(self, service: str = None) -> List[str]:
        """
        Get list of available AWS regions for this service category.

        Args:
            service: Specific service to check regions for

        Returns:
            List of available region names
        """
        if service in self._region_cache:
            return self._region_cache[service]

        try:
            # Use EC2 as default service for region discovery
            check_service = service or "ec2"
            ec2_client = self.session.client("ec2", region_name="us-east-1")

            response = ec2_client.describe_regions(
                Filters=[{"Name": "opt-in-status", "Values": ["opt-in-not-required", "opted-in"]}]
            )

            regions = [r["RegionName"] for r in response["Regions"]]
            self._region_cache[service] = regions
            return regions

        except ClientError as e:
            logger.warning(f"Failed to get regions for {service}: {e}")
            # Return common regions as fallback
            return [
                "us-east-1",
                "us-east-2",
                "us-west-1",
                "us-west-2",
                "eu-west-1",
                "eu-central-1",
                "ap-southeast-1",
                "ap-northeast-1",
            ]

    def _create_resource_metadata(self, context: CollectionContext, resource_data: Dict[str, Any]) -> ResourceMetadata:
        """
        Create resource metadata from AWS API response data.

        Args:
            context: Collection context
            resource_data: Raw resource data from AWS API

        Returns:
            Structured resource metadata
        """
        return ResourceMetadata(
            account_id=context.account.account_id,
            region=context.region,
            service_category=self.service_category,
            collection_timestamp=context.collection_timestamp,
            raw_data=resource_data,
        )

    def __repr__(self) -> str:
        """String representation of the collector."""
        return (
            f"{self.__class__.__name__}(category='{self.service_category}', resources={len(self.supported_resources)})"
        )

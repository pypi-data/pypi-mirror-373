"""
Base classes for Cloud Foundations modules.

This module provides common base classes and utilities used across
all Cloud Foundations components including CFAT, inventory, and organizations.
"""

import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from loguru import logger

try:
    from pydantic import BaseModel
except ImportError:
    # Fallback BaseModel
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def model_dump(self, exclude_none=True):
            result = {}
            for key, value in self.__dict__.items():
                if not exclude_none or value is not None:
                    result[key] = value
            return result


from runbooks.config import RunbooksConfig
from runbooks.utils import retry_with_backoff


class CloudFoundationsResult(BaseModel):
    """Base result model for Cloud Foundations operations."""

    timestamp: datetime
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = []

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda dt: dt.isoformat()}


class CloudFoundationsBase(ABC):
    """
    Abstract base class for Cloud Foundations components.

    Provides common functionality for AWS operations, error handling,
    session management, and result formatting.
    """

    def __init__(
        self, profile: Optional[str] = None, region: Optional[str] = None, config: Optional[RunbooksConfig] = None
    ):
        """
        Initialize base Cloud Foundations component.

        Args:
            profile: AWS profile name
            region: AWS region
            config: Runbooks configuration
        """
        self.config = config or RunbooksConfig()
        self.profile = profile or self.config.aws_profile
        self.region = region or self.config.aws_region
        self._session = None
        self._clients = {}

        logger.debug(f"Initialized {self.__class__.__name__} with profile: {self.profile}, region: {self.region}")

    @property
    def session(self) -> boto3.Session:
        """Get or create boto3 session."""
        if self._session is None:
            self._session = self._create_session()
        return self._session

    def _create_session(self) -> boto3.Session:
        """Create boto3 session with appropriate configuration."""
        # Use environment variable first, then profile parameter, then default
        profile = os.environ.get("AWS_PROFILE") or self.profile

        session_kwargs = {"profile_name": profile}
        if self.region:
            session_kwargs["region_name"] = self.region

        try:
            session = boto3.Session(**session_kwargs)
            # Test session by getting caller identity
            sts = session.client("sts")
            identity = sts.get_caller_identity()
            logger.debug(f"Session created for account: {identity.get('Account')}")
            return session
        except Exception as e:
            logger.error(f"Failed to create AWS session: {e}")
            raise

    def get_client(self, service_name: str, region: Optional[str] = None) -> Any:
        """
        Get or create AWS service client with caching.

        Args:
            service_name: AWS service name (e.g., 'ec2', 's3')
            region: Optional region override

        Returns:
            Boto3 client for the service
        """
        client_region = region or self.region
        cache_key = f"{service_name}:{client_region}"

        if cache_key not in self._clients:
            client_kwargs = {}
            if client_region:
                client_kwargs["region_name"] = client_region

            self._clients[cache_key] = self.session.client(service_name, **client_kwargs)
            logger.debug(f"Created {service_name} client for region: {client_region}")

        return self._clients[cache_key]

    def get_resource(self, service_name: str, region: Optional[str] = None) -> Any:
        """
        Get AWS service resource.

        Args:
            service_name: AWS service name (e.g., 'ec2', 's3')
            region: Optional region override

        Returns:
            Boto3 resource for the service
        """
        resource_kwargs = {}
        if region or self.region:
            resource_kwargs["region_name"] = region or self.region

        return self.session.resource(service_name, **resource_kwargs)

    @retry_with_backoff(max_retries=3, backoff_factor=1.0)
    def _make_aws_call(self, client_method, **kwargs) -> Any:
        """
        Make AWS API call with retry logic.

        Args:
            client_method: Boto3 client method to call
            **kwargs: Arguments for the method

        Returns:
            API response
        """
        try:
            return client_method(**kwargs)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"AWS API error ({error_code}): {error_message}")
            raise
        except BotoCoreError as e:
            logger.error(f"AWS SDK error: {e}")
            raise

    def get_account_id(self) -> str:
        """Get current AWS account ID."""
        try:
            sts = self.get_client("sts")
            response = self._make_aws_call(sts.get_caller_identity)
            return response["Account"]
        except Exception as e:
            logger.error(f"Failed to get account ID: {e}")
            raise

    def get_available_regions(self, service_name: str = "ec2") -> List[str]:
        """
        Get list of available AWS regions for a service.

        Args:
            service_name: AWS service name

        Returns:
            List of region names
        """
        try:
            client = self.get_client(service_name)
            response = self._make_aws_call(client.describe_regions)
            return [region["RegionName"] for region in response["Regions"]]
        except Exception as e:
            logger.error(f"Failed to get available regions: {e}")
            return []

    def validate_permissions(self, required_actions: List[str]) -> Dict[str, bool]:
        """
        Validate that current credentials have required permissions.

        Args:
            required_actions: List of IAM actions to check

        Returns:
            Dictionary mapping actions to permission status
        """
        results = {}
        iam = self.get_client("iam")

        for action in required_actions:
            try:
                # Use simulate_principal_policy to check permissions
                response = self._make_aws_call(
                    iam.simulate_principal_policy,
                    PolicySourceArn=f"arn:aws:iam::{self.get_account_id()}:user/*",
                    ActionNames=[action],
                )

                if response["EvaluationResults"]:
                    decision = response["EvaluationResults"][0]["EvalDecision"]
                    results[action] = decision == "allowed"
                else:
                    results[action] = False

            except Exception as e:
                logger.warning(f"Could not check permission for {action}: {e}")
                results[action] = False

        return results

    @abstractmethod
    def run(self) -> CloudFoundationsResult:
        """
        Run the main operation for this component.

        Returns:
            Result object with operation status and data
        """
        pass

    def create_result(
        self, success: bool, message: str, data: Optional[Dict[str, Any]] = None, errors: Optional[List[str]] = None
    ) -> CloudFoundationsResult:
        """
        Create a standardized result object.

        Args:
            success: Whether operation succeeded
            message: Result message
            data: Optional result data
            errors: Optional list of errors

        Returns:
            CloudFoundationsResult object
        """
        return CloudFoundationsResult(
            timestamp=datetime.now(), success=success, message=message, data=data or {}, errors=errors or []
        )


class CloudFoundationsFormatter:
    """Base formatter for Cloud Foundations output."""

    def __init__(self, data: Any):
        """Initialize formatter with data."""
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        """Convert data to dictionary format."""
        if hasattr(self.data, "model_dump"):
            return self.data.model_dump()
        elif hasattr(self.data, "dict"):
            return self.data.dict()
        else:
            return {"data": self.data}

    def to_json(self, file_path: Union[str, Path]) -> None:
        """Save data as JSON file."""
        import json

        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

        logger.info(f"JSON output saved to: {output_path}")

    def to_csv(self, file_path: Union[str, Path]) -> None:
        """Save data as CSV file."""
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas is required for CSV export. Install with: pip install pandas")
            return

        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame
        if isinstance(self.data, list):
            df = pd.DataFrame(self.data)
        else:
            df = pd.DataFrame([self.to_dict()])

        df.to_csv(output_path, index=False)
        logger.info(f"CSV output saved to: {output_path}")

    def to_excel(self, file_path: Union[str, Path]) -> None:
        """Save data as Excel file."""
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas is required for Excel export. Install with: pip install pandas")
            return

        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame
        if isinstance(self.data, list):
            df = pd.DataFrame(self.data)
        else:
            df = pd.DataFrame([self.to_dict()])

        df.to_excel(output_path, index=False)
        logger.info(f"Excel output saved to: {output_path}")


class ProgressTracker:
    """Simple progress tracking for long-running operations."""

    def __init__(self, total: int, description: str = "Processing"):
        """Initialize progress tracker."""
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()

    def update(self, increment: int = 1, status: Optional[str] = None) -> None:
        """Update progress."""
        self.current += increment
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0

        elapsed = datetime.now() - self.start_time

        status_msg = f" - {status}" if status else ""
        logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%){status_msg}")

    def complete(self, message: Optional[str] = None) -> None:
        """Mark progress as complete."""
        elapsed = datetime.now() - self.start_time
        final_msg = message or f"{self.description} completed"
        logger.info(f"{final_msg} in {elapsed.total_seconds():.1f}s")

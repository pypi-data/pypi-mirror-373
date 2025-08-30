#!/usr/bin/env python3
"""
AWS Account Name Resolution Module for CloudOps Runbooks FinOps

This module provides account ID to account name mapping functionality using
the AWS Organizations API for readable account display in FinOps dashboards.

Features:
- Organizations API integration for account discovery
- Fallback to account ID when Organizations access unavailable
- Caching for performance optimization
- Profile-aware session management
- Error handling with graceful degradation

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import functools
import time
from typing import Dict, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from runbooks.common.rich_utils import console, print_error, print_info, print_warning


class AccountResolver:
    """AWS account name resolution using Organizations API."""

    def __init__(self, management_profile: Optional[str] = None):
        """
        Initialize account resolver with management profile.

        Args:
            management_profile: AWS profile with Organizations read access
        """
        self.management_profile = management_profile
        self._account_cache: Dict[str, str] = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes cache TTL

    @functools.lru_cache(maxsize=1)
    def _get_organizations_client(self) -> Optional[boto3.client]:
        """
        Get Organizations client with error handling.

        Returns:
            Boto3 Organizations client or None if unavailable
        """
        try:
            if self.management_profile:
                session = boto3.Session(profile_name=self.management_profile)
            else:
                session = boto3.Session()

            # Use us-east-1 for Organizations API (global service)
            client = session.client("organizations", region_name="us-east-1")

            # Test connectivity with a simple API call
            client.describe_organization()
            return client

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "AccessDeniedException":
                print_warning(f"Organizations access denied for profile '{self.management_profile}'")
            elif error_code == "AWSOrganizationsNotInUseException":
                print_info("AWS Organizations not enabled for this account")
            else:
                print_warning(f"Organizations API error: {error_code}")
            return None

        except NoCredentialsError:
            print_warning("AWS credentials not available for Organizations API")
            return None

        except Exception as e:
            print_warning(f"Unexpected error accessing Organizations API: {e}")
            return None

    def _refresh_account_cache(self) -> bool:
        """
        Refresh account cache from Organizations API.

        Returns:
            True if cache was refreshed successfully
        """
        current_time = time.time()

        # Check if cache is still valid
        if self._account_cache and (current_time - self._cache_timestamp) < self._cache_ttl:
            return True

        client = self._get_organizations_client()
        if not client:
            return False

        try:
            print_info("Refreshing account names from Organizations API...")

            # List all accounts in the organization
            paginator = client.get_paginator("list_accounts")
            accounts = {}

            for page in paginator.paginate():
                for account in page.get("Accounts", []):
                    account_id = account.get("Id", "")
                    account_name = account.get("Name", account_id)

                    # Clean up account name for display
                    display_name = self._clean_account_name(account_name)
                    accounts[account_id] = display_name

            # Update cache
            self._account_cache = accounts
            self._cache_timestamp = current_time

            print_info(f"✅ Loaded {len(accounts)} account names from Organizations API")
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            print_warning(f"Failed to refresh account cache: {error_code}")
            return False

        except Exception as e:
            print_error(f"Unexpected error refreshing account cache: {e}")
            return False

    def _clean_account_name(self, account_name: str, max_length: int = 40) -> str:
        """
        Clean up account name for display with intelligent truncation.

        Args:
            account_name: Raw account name from Organizations API
            max_length: Maximum display length (default 40 for better readability)

        Returns:
            Cleaned account name suitable for enterprise display
        """
        if not account_name:
            return "Unknown"

        # Remove common prefixes and suffixes for cleaner display
        cleaned = account_name

        # Remove common organizational prefixes (be more selective)
        prefixes_to_remove = ["ams-", "aws-", "org-", "account-"]
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix) :]
                break

        # Remove common suffixes (be more selective to preserve meaningful info)
        suffixes_to_remove = ["-account"]  # Only remove truly redundant suffixes
        for suffix in suffixes_to_remove:
            if cleaned.lower().endswith(suffix):
                cleaned = cleaned[: -len(suffix)]
                break

        # Capitalize first letter of each word for professional presentation
        cleaned = " ".join(word.capitalize() for word in cleaned.replace("-", " ").replace("_", " ").split())

        # Smart truncation - preserve meaningful parts
        if len(cleaned) > max_length:
            # Strategy 1: Try to truncate at word boundaries
            words = cleaned.split()
            if len(words) > 2:
                # Keep first two meaningful words and truncate
                truncated = f"{words[0]} {words[1]}..."
                if len(truncated) <= max_length:
                    return truncated

            # Strategy 2: Truncate with ellipsis, preserving more characters
            cleaned = cleaned[: max_length - 3] + "..."

        return cleaned or "Unknown"

    def get_account_name(self, account_id: str, max_length: int = 40) -> str:
        """
        Get readable account name for account ID with configurable length.

        Args:
            account_id: AWS account ID
            max_length: Maximum display length for the name

        Returns:
            Readable account name or account ID if resolution fails
        """
        if not account_id:
            return "Unknown"

        # Try to refresh cache if needed
        self._refresh_account_cache()

        # Get cached name or fallback to account ID
        cached_name = self._account_cache.get(account_id, account_id)

        # If we have a resolved name and it's different from account ID, apply length constraint
        if cached_name != account_id:
            return self._clean_account_name(cached_name, max_length)

        return cached_name

    def get_full_account_name(self, account_id: str) -> str:
        """
        Get full, untruncated account name for account ID.

        Args:
            account_id: AWS account ID

        Returns:
            Full readable account name or account ID if resolution fails
        """
        if not account_id:
            return "Unknown"

        # Try to refresh cache if needed
        self._refresh_account_cache()

        # Return raw cached name without truncation
        return self._account_cache.get(account_id, account_id)

    def get_account_names(self, account_ids: list) -> Dict[str, str]:
        """
        Get readable account names for multiple account IDs.

        Args:
            account_ids: List of AWS account IDs

        Returns:
            Dictionary mapping account IDs to readable names
        """
        if not account_ids:
            return {}

        # Refresh cache once for all accounts
        self._refresh_account_cache()

        # Build result dictionary
        result = {}
        for account_id in account_ids:
            result[account_id] = self._account_cache.get(account_id, account_id)

        return result


def get_account_resolver(management_profile: Optional[str] = None) -> AccountResolver:
    """
    Get account resolver instance with specified profile.

    Args:
        management_profile: AWS profile with Organizations read access

    Returns:
        AccountResolver instance
    """
    return AccountResolver(management_profile)


def resolve_account_name(account_id: str, management_profile: Optional[str] = None) -> str:
    """
    Convenience function to resolve single account name.

    Args:
        account_id: AWS account ID to resolve
        management_profile: AWS profile with Organizations read access

    Returns:
        Readable account name or account ID if resolution fails
    """
    resolver = get_account_resolver(management_profile)
    return resolver.get_account_name(account_id)


# Export public interface
__all__ = ["AccountResolver", "get_account_resolver", "resolve_account_name"]

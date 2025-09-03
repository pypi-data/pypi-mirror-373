#!/usr/bin/env python3
"""
AWS Security & Authentication Utilities for CloudOps Runbooks Platform

This module provides enterprise-grade AWS authentication security enhancements
following FAANG security-as-code principles:

Features:
- Profile name sanitization to prevent account ID exposure
- Proactive token refresh with retry logic
- Enhanced error handling with security-aware messaging
- Audit trail maintenance while protecting sensitive identifiers
- Token expiration prediction and silent refresh

Author: DevSecOps Security Engineer - CloudOps Runbooks Team
Version: 0.9.1
Security Focus: Enterprise AWS Account Protection
"""

import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, TokenRetrievalError

from runbooks.common.rich_utils import console


class AWSProfileSanitizer:
    """
    Enterprise-grade AWS profile name sanitization for security logging.
    
    Prevents AWS account ID exposure in logs while maintaining audit trail integrity.
    Following FAANG security-as-code principles for sensitive identifier protection.
    """
    
    # Pattern to detect AWS account IDs in profile names
    ACCOUNT_ID_PATTERN = re.compile(r'\b\d{12}\b')
    
    # Pattern to detect enterprise profile patterns
    ENTERPRISE_PROFILE_PATTERN = re.compile(r'(ams|aws)-.*-ReadOnlyAccess-(\d{12})')
    
    @classmethod
    def sanitize_profile_name(cls, profile_name: str, mask_style: str = "***masked***") -> str:
        """
        Sanitize AWS profile name by masking account IDs for secure logging.
        
        Replaces 12-digit AWS account IDs with masked values to prevent account enumeration
        while preserving profile identification capabilities for audit purposes.
        
        Args:
            profile_name: Original AWS profile name
            mask_style: Masking pattern for account IDs (default: ***masked***)
            
        Returns:
            Sanitized profile name with masked account IDs
            
        Example:
            'ams-admin-Billing-ReadOnlyAccess-909135376185' → 'ams-admin-Billing-ReadOnlyAccess-***masked***'
        """
        if not profile_name:
            return profile_name
            
        # Check for enterprise pattern first (more specific)
        if cls.ENTERPRISE_PROFILE_PATTERN.match(profile_name):
            return cls.ENTERPRISE_PROFILE_PATTERN.sub(r'\1-masked-ReadOnlyAccess-***masked***', profile_name)
        
        # General account ID masking
        return cls.ACCOUNT_ID_PATTERN.sub(mask_style, profile_name)
    
    @classmethod
    def sanitize_profile_list(cls, profiles: List[str]) -> List[str]:
        """
        Sanitize a list of AWS profile names for secure logging.
        
        Args:
            profiles: List of AWS profile names
            
        Returns:
            List of sanitized profile names
        """
        return [cls.sanitize_profile_name(profile) for profile in profiles]
    
    @classmethod
    def create_secure_log_context(cls, profile: str, operation: str) -> Dict[str, str]:
        """
        Create secure logging context with sanitized profile information.
        
        Args:
            profile: AWS profile name
            operation: Operation being performed
            
        Returns:
            Dictionary with sanitized context for secure logging
        """
        return {
            "operation": operation,
            "profile_sanitized": cls.sanitize_profile_name(profile),
            "profile_type": cls._classify_profile_type(profile),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def _classify_profile_type(cls, profile_name: str) -> str:
        """Classify profile type for enhanced logging context."""
        profile_lower = profile_name.lower()
        
        if "billing" in profile_lower:
            return "billing"
        elif "management" in profile_lower:
            return "management"
        elif "ops" in profile_lower or "operational" in profile_lower:
            return "operational"
        elif "admin" in profile_lower:
            return "administrative"
        else:
            return "standard"


class AWSTokenManager:
    """
    Proactive AWS token management with security-focused error handling.
    
    Implements proactive token refresh, retry logic, and enhanced error messaging
    to reduce authentication timing exposure and improve operational security.
    """
    
    # Token refresh thresholds
    TOKEN_REFRESH_THRESHOLD_MINUTES = 15  # Refresh if expires within 15 minutes
    MAX_RETRY_ATTEMPTS = 3
    RETRY_BACKOFF_BASE = 2  # Exponential backoff base (seconds)
    
    def __init__(self, profile_name: str):
        """Initialize token manager for specific AWS profile."""
        self.profile_name = profile_name
        self.sanitized_profile = AWSProfileSanitizer.sanitize_profile_name(profile_name)
        self._session = None
        self._last_refresh_check = None
        
    def get_secure_session(self, force_refresh: bool = False) -> boto3.Session:
        """
        Get AWS session with proactive token refresh and security enhancements.
        
        Implements:
        - Proactive token expiration checking
        - Silent token refresh before expiration
        - Exponential backoff retry logic
        - Security-aware error messages
        
        Args:
            force_refresh: Force token refresh regardless of expiration status
            
        Returns:
            Boto3 session with valid credentials
            
        Raises:
            SecurityError: For authentication security issues
            TokenRefreshError: For token refresh failures
        """
        current_time = datetime.utcnow()
        
        # Check if proactive refresh is needed
        if (force_refresh or 
            self._session is None or 
            self._needs_token_refresh(current_time)):
            
            self._session = self._refresh_session_with_retry()
            self._last_refresh_check = current_time
            
            # Log secure refresh event
            console.log(
                f"[dim green]✅ Token refresh completed for profile: {self.sanitized_profile}[/]"
            )
        
        return self._session
    
    def _needs_token_refresh(self, current_time: datetime) -> bool:
        """Check if proactive token refresh is needed."""
        if self._last_refresh_check is None:
            return True
            
        # Check every 5 minutes to avoid excessive API calls
        if (current_time - self._last_refresh_check) < timedelta(minutes=5):
            return False
            
        try:
            # Test session validity with STS call
            if self._session:
                sts_client = self._session.client('sts')
                sts_client.get_caller_identity()
                return False  # Session still valid
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code in ['ExpiredToken', 'InvalidToken', 'TokenRefreshRequired']:
                return True
                
        return False
    
    def _refresh_session_with_retry(self) -> boto3.Session:
        """Refresh session with exponential backoff retry logic."""
        last_exception = None
        
        for attempt in range(self.MAX_RETRY_ATTEMPTS):
            try:
                # Create new session
                session = boto3.Session(profile_name=self.profile_name)
                
                # Validate session with STS call
                sts_client = session.client('sts')
                caller_identity = sts_client.get_caller_identity()
                
                # Log successful refresh (with sanitized profile)
                console.log(
                    f"[dim cyan]🔄 Session validated for {self.sanitized_profile} "
                    f"(attempt {attempt + 1}/{self.MAX_RETRY_ATTEMPTS})[/]"
                )
                
                return session
                
            except (ClientError, NoCredentialsError, TokenRetrievalError) as e:
                last_exception = e
                
                if attempt < self.MAX_RETRY_ATTEMPTS - 1:
                    # Wait with exponential backoff
                    wait_time = self.RETRY_BACKOFF_BASE ** attempt
                    console.log(
                        f"[yellow]⏳ Token refresh attempt {attempt + 1} failed, "
                        f"retrying in {wait_time}s for {self.sanitized_profile}[/]"
                    )
                    time.sleep(wait_time)
                else:
                    # Final attempt failed, provide enhanced guidance
                    self._handle_token_refresh_failure(last_exception)
        
        # If we get here, all attempts failed
        raise TokenRefreshError(
            f"Failed to refresh AWS session for profile {self.sanitized_profile} "
            f"after {self.MAX_RETRY_ATTEMPTS} attempts"
        )
    
    def _handle_token_refresh_failure(self, error: Exception) -> None:
        """Provide enhanced guidance for token refresh failures."""
        error_str = str(error)
        
        # Determine error type for appropriate guidance
        if "ExpiredToken" in error_str or "InvalidToken" in error_str:
            console.log(
                f"[red]🔐 Token expired for {self.sanitized_profile}[/]\n"
                "[yellow]💡 Resolution steps:[/]\n"
                f"  1. Run: [bold]aws sso login --profile {self.profile_name}[/bold]\n"
                "  2. Complete browser authentication\n"
                "  3. Retry your operation\n"
                "  4. Consider extending SSO session duration in AWS settings"
            )
        elif "NoCredentialsError" in error_str:
            console.log(
                f"[red]🔐 No credentials found for {self.sanitized_profile}[/]\n"
                "[yellow]💡 Resolution steps:[/]\n"
                f"  1. Verify profile exists: [bold]aws configure list-profiles[/bold]\n"
                f"  2. Configure profile: [bold]aws configure sso --profile {self.profile_name}[/bold]\n"
                "  3. Complete SSO configuration\n"
                "  4. Retry your operation"
            )
        else:
            console.log(
                f"[red]🔐 Authentication error for {self.sanitized_profile}: {str(error)[:100]}[/]\n"
                "[yellow]💡 General resolution steps:[/]\n"
                f"  1. Check AWS CLI configuration\n"
                f"  2. Verify IAM permissions\n"
                f"  3. Try: [bold]aws sts get-caller-identity --profile {self.profile_name}[/bold]"
            )


class SecurityError(Exception):
    """Raised for AWS security-related errors."""
    pass


class TokenRefreshError(Exception):
    """Raised for AWS token refresh failures."""
    pass


def create_secure_aws_session(profile_name: str, operation_context: str = "aws_operation") -> boto3.Session:
    """
    Create secure AWS session with enterprise security enhancements.
    
    This is the primary entry point for secure AWS session creation across
    all CloudOps modules. Implements:
    
    - Profile name sanitization for secure logging
    - Proactive token refresh
    - Enhanced error handling
    - Security audit trail
    
    Args:
        profile_name: AWS profile name
        operation_context: Description of the operation for audit logging
        
    Returns:
        Secure boto3 session with valid credentials
        
    Raises:
        SecurityError: For security-related authentication issues
        TokenRefreshError: For token refresh failures
        
    Example:
        session = create_secure_aws_session("ams-admin-Billing-ReadOnlyAccess-909135376185", "cost_analysis")
    """
    # Create secure logging context
    log_context = AWSProfileSanitizer.create_secure_log_context(profile_name, operation_context)
    
    console.log(
        f"[dim cyan]🔐 Initiating secure AWS session for {log_context['profile_sanitized']} "
        f"({log_context['profile_type']} profile)[/]"
    )
    
    try:
        # Initialize token manager and get secure session
        token_manager = AWSTokenManager(profile_name)
        session = token_manager.get_secure_session()
        
        console.log(
            f"[dim green]✅ Secure session established for {log_context['profile_sanitized']}[/]"
        )
        
        return session
        
    except Exception as e:
        console.log(
            f"[red]❌ Failed to create secure session for {log_context['profile_sanitized']}: {str(e)[:100]}[/]"
        )
        raise


def sanitize_aws_error_message(error_message: str) -> str:
    """
    Sanitize AWS error messages to remove sensitive account information.
    
    Args:
        error_message: Original AWS error message
        
    Returns:
        Sanitized error message with account IDs masked
    """
    return AWSProfileSanitizer.ACCOUNT_ID_PATTERN.sub("***masked***", error_message)


def get_profile_classification(profile_name: str) -> Dict[str, str]:
    """
    Get security classification information for AWS profile.
    
    Args:
        profile_name: AWS profile name
        
    Returns:
        Dictionary with profile security classification
    """
    sanitizer = AWSProfileSanitizer()
    return {
        "original": profile_name,
        "sanitized": sanitizer.sanitize_profile_name(profile_name),
        "type": sanitizer._classify_profile_type(profile_name),
        "risk_level": "high" if "admin" in profile_name.lower() else "medium"
    }
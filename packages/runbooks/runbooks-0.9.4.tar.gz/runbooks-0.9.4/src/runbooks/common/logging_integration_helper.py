#!/usr/bin/env python3
"""
Logging Integration Helper

This module provides helper functions to make it easy for existing modules
to upgrade to the enhanced multi-level logging architecture.

Author: CloudOps Runbooks Team
"""

from typing import Optional, Dict, Any, Callable
from functools import wraps
import time
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from runbooks.enterprise.logging import get_module_logger, EnterpriseRichLogger


def create_enhanced_module_logger(module_name: str, log_level: Optional[str] = None, 
                                 json_output: bool = False) -> EnterpriseRichLogger:
    """
    Create an enhanced logger for a module with automatic level detection.
    
    Args:
        module_name: Name of the module (e.g., 'finops', 'inventory') 
        log_level: Override log level, or None to use CLI/environment setting
        json_output: Enable JSON output for programmatic use
        
    Returns:
        Configured enhanced logger
    """
    # Try to detect log level from CLI context if not provided
    if log_level is None:
        import os
        import sys
        
        # Check if we're in a CLI context
        log_level = os.getenv('RUNBOOKS_LOG_LEVEL', 'INFO')
        
        # Check command line arguments for log level
        for arg in sys.argv:
            if arg.startswith('--log-level'):
                if '=' in arg:
                    log_level = arg.split('=')[1].upper()
                else:
                    # Next argument should be the level
                    try:
                        idx = sys.argv.index(arg)
                        if idx + 1 < len(sys.argv):
                            log_level = sys.argv[idx + 1].upper()
                    except (ValueError, IndexError):
                        pass
                break
    
    return get_module_logger(module_name, level=log_level or 'INFO', json_output=json_output)


def log_aws_operation(func: Callable) -> Callable:
    """
    Decorator to automatically log AWS operations with enhanced context.
    
    Usage:
        @log_aws_operation
        def describe_instances(session, region):
            client = session.client('ec2', region_name=region)
            return client.describe_instances()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Try to extract module name from function
        module_name = func.__module__.split('.')[-1] if hasattr(func, '__module__') else 'unknown'
        logger = create_enhanced_module_logger(module_name)
        
        # Extract operation details from function name and arguments
        operation_name = func.__name__
        service_name = 'aws'  # Default, could be improved by parsing function or args
        
        start_time = time.time()
        success = True
        result = None
        error_details = None
        
        try:
            result = func(*args, **kwargs)
            return result
        except (ClientError, BotoCoreError) as e:
            success = False
            error_details = str(e)
            logger.error_all(
                f"AWS operation failed: {operation_name}",
                solution=f"Check AWS permissions and service availability",
                aws_error=error_details,
                suggested_command=f"aws {service_name} {operation_name.replace('_', '-')} --help"
            )
            raise
        except Exception as e:
            success = False
            error_details = str(e)
            logger.error_all(
                f"Operation failed: {operation_name}",
                solution="Check the error details above and verify inputs",
                aws_error=error_details
            )
            raise
        finally:
            duration = time.time() - start_time
            if success:
                resource_count = None
                # Try to extract resource count from result
                if isinstance(result, dict):
                    if 'Reservations' in result:
                        resource_count = sum(len(r.get('Instances', [])) for r in result['Reservations'])
                    elif 'Buckets' in result:
                        resource_count = len(result['Buckets'])
                    elif isinstance(result.get('ResponseMetadata'), dict):
                        # It's an AWS response, try to count items
                        for key, value in result.items():
                            if isinstance(value, list) and key != 'ResponseMetadata':
                                resource_count = len(value)
                                break
                
                logger.log_aws_operation(
                    operation=operation_name,
                    service=service_name,
                    duration=duration,
                    success=True,
                    resource_count=resource_count
                )
    
    return wrapper


def log_cost_operation(func: Callable) -> Callable:
    """
    Decorator to automatically log cost-related operations.
    
    Usage:
        @log_cost_operation  
        def analyze_monthly_costs(cost_data):
            # ... cost analysis logic ...
            return {"total_cost": 1500.0, "savings": 300.0}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        module_name = func.__module__.split('.')[-1] if hasattr(func, '__module__') else 'finops'
        logger = create_enhanced_module_logger(module_name)
        
        operation_name = func.__name__
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Extract cost information from result
            cost_impact = None
            savings_opportunity = None
            
            if isinstance(result, dict):
                cost_impact = result.get('total_cost') or result.get('cost_impact') 
                savings_opportunity = result.get('savings') or result.get('savings_opportunity')
            
            logger.log_cost_analysis(
                operation=operation_name,
                cost_impact=cost_impact,
                savings_opportunity=savings_opportunity
            )
            
            # Also log performance if it's slow
            logger.log_performance_metric(operation_name, duration)
            
            return result
            
        except Exception as e:
            logger.error_all(
                f"Cost analysis failed: {operation_name}",
                solution="Check input data format and AWS permissions",
                aws_error=str(e)
            )
            raise
    
    return wrapper


def log_security_operation(func: Callable) -> Callable:
    """
    Decorator to automatically log security operations.
    
    Usage:
        @log_security_operation
        def scan_s3_permissions(bucket_name):
            # ... security scan logic ...
            return {"findings": [...], "severity": "medium"}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        module_name = func.__module__.split('.')[-1] if hasattr(func, '__module__') else 'security'
        logger = create_enhanced_module_logger(module_name)
        
        operation_name = func.__name__
        
        try:
            result = func(*args, **kwargs)
            
            # Extract security findings from result
            if isinstance(result, dict) and 'findings' in result:
                findings = result['findings']
                severity = result.get('severity', 'medium')
                
                if findings:
                    for finding in findings:
                        if isinstance(finding, dict):
                            logger.log_security_finding(
                                finding=finding.get('description', str(finding)),
                                severity=finding.get('severity', severity),
                                remediation_steps=finding.get('remediation_steps')
                            )
                        else:
                            logger.log_security_finding(str(finding), severity=severity)
                else:
                    logger.info_standard(f"Security scan completed: {operation_name} (no findings)")
            
            return result
            
        except Exception as e:
            logger.error_all(
                f"Security operation failed: {operation_name}",
                solution="Check security scan configuration and permissions",
                aws_error=str(e)
            )
            raise
    
    return wrapper


class LoggingMigrationHelper:
    """Helper class to assist with migrating existing modules to enhanced logging."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = create_enhanced_module_logger(module_name)
    
    def replace_print_statements(self, message: str, level: str = "info", **kwargs):
        """
        Replace print statements with appropriate logging calls.
        
        Args:
            message: The message to log
            level: Log level (debug, info, warning, error)
            **kwargs: Additional context for enhanced logging
        """
        if level.lower() == "debug":
            self.logger.debug_tech(message, **kwargs)
        elif level.lower() == "warning":
            self.logger.warning_business(message, **kwargs)
        elif level.lower() == "error":
            self.logger.error_all(message, **kwargs)
        else:
            self.logger.info_standard(message, **kwargs)
    
    def log_operation_start(self, operation: str, **context):
        """Log the start of an operation."""
        return self.logger.operation_context(operation, **context)
    
    def log_aws_call(self, service: str, operation: str, duration: float = None, 
                     success: bool = True, **kwargs):
        """Log an AWS API call."""
        self.logger.log_aws_operation(
            operation=operation,
            service=service,
            duration=duration,
            success=success,
            **kwargs
        )
    
    def log_cost_finding(self, operation: str, cost: float = None, savings: float = None, 
                        recommendation: str = None):
        """Log a cost-related finding."""
        self.logger.log_cost_analysis(
            operation=operation,
            cost_impact=cost,
            savings_opportunity=savings,
            recommendation=recommendation
        )


# Convenience functions for quick integration
def quick_log_info(module_name: str, message: str, **kwargs):
    """Quick logging for info messages."""
    logger = create_enhanced_module_logger(module_name)
    logger.info_standard(message, **kwargs)


def quick_log_error(module_name: str, message: str, solution: str = None, **kwargs):
    """Quick logging for error messages."""
    logger = create_enhanced_module_logger(module_name)
    logger.error_all(message, solution=solution, **kwargs)


def quick_log_warning(module_name: str, message: str, recommendation: str = None, **kwargs):
    """Quick logging for warning messages.""" 
    logger = create_enhanced_module_logger(module_name)
    logger.warning_business(message, recommendation=recommendation, **kwargs)


def quick_log_debug(module_name: str, message: str, **kwargs):
    """Quick logging for debug messages."""
    logger = create_enhanced_module_logger(module_name)
    logger.debug_tech(message, **kwargs)


# Module upgrade checklist function
def print_upgrade_checklist(module_name: str):
    """Print upgrade checklist for a module."""
    print(f"\n📋 ENHANCED LOGGING UPGRADE CHECKLIST FOR {module_name.upper()}")
    print("=" * 60)
    print("1. Replace logger imports:")
    print(f"   OLD: from logging import getLogger")
    print(f"   NEW: from runbooks.common.logging_integration_helper import create_enhanced_module_logger")
    print()
    print("2. Update logger initialization:")
    print(f"   OLD: logger = getLogger(__name__)")
    print(f"   NEW: logger = create_enhanced_module_logger('{module_name}')")
    print()
    print("3. Replace print statements:")
    print(f"   OLD: print('Operation completed')")
    print(f"   NEW: logger.info_standard('Operation completed', operation_status='completed')")
    print()
    print("4. Use context-aware logging methods:")
    print(f"   • logger.debug_tech() - for technical details")
    print(f"   • logger.info_standard() - for standard operations") 
    print(f"   • logger.warning_business() - for business insights")
    print(f"   • logger.error_all() - for errors with solutions")
    print()
    print("5. Use convenience methods:")
    print(f"   • logger.log_aws_operation() - for AWS API calls")
    print(f"   • logger.log_cost_analysis() - for cost operations")
    print(f"   • logger.log_security_finding() - for security scans")
    print()
    print("6. Use operation context:")
    print(f"   with logger.operation_context('operation_name'):")
    print(f"       # ... operation code ...")
    print()
    print("✅ After upgrade, users can control output with --log-level DEBUG|INFO|WARNING|ERROR")
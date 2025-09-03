#!/usr/bin/env python3
"""
Enhanced Logging Integration Example for CloudOps Runbooks

This module demonstrates how to integrate the enhanced multi-level logging system
with Rich CLI formatting across different user types and scenarios.
"""

import time
from typing import Dict, Any, Optional

# Import enhanced logging capabilities
from runbooks.enterprise.logging import get_context_logger, EnterpriseRichLogger


class EnhancedLoggingExample:
    """Demonstrates enhanced logging integration patterns for different user types."""
    
    def __init__(self, log_level: str = "INFO", json_output: bool = False):
        """
        Initialize with enhanced logger.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            json_output: Enable structured JSON output
        """
        self.logger = get_context_logger(level=log_level, json_output=json_output)
        self.log_level = log_level.upper()
    
    def demonstrate_debug_logging(self):
        """Demonstrate DEBUG level logging for tech users (SRE/DevOps)."""
        print("\n=== DEBUG Level Logging (Tech Users) ===")
        
        # AWS API tracing example
        start_time = time.time()
        
        # Simulate AWS API call
        time.sleep(0.1)
        duration = time.time() - start_time
        
        self.logger.debug_tech(
            "EC2 instances discovered in region us-east-1",
            aws_api={
                "service": "ec2",
                "operation": "describe_instances",
                "region": "us-east-1"
            },
            duration=duration,
            request_id="12345-abcde-67890",
            resource_count=42
        )
        
        # Performance metrics
        self.logger.debug_tech(
            "Cost analysis query executed",
            aws_api={
                "service": "ce",
                "operation": "get_cost_and_usage"
            },
            duration=2.435,
            data_points=1500,
            cache_hit=False
        )
    
    def demonstrate_info_logging(self):
        """Demonstrate INFO level logging for standard users."""
        print("\n=== INFO Level Logging (Standard Users) ===")
        
        # Standard operation status
        self.logger.info_standard("Starting cost analysis for account 123456789012")
        
        # Progress indication
        self.logger.info_standard("Processing 15 AWS services across 3 regions")
        
        # Completion status
        self.logger.info_standard(
            "Cost analysis completed successfully",
            execution_time="12.3s",
            resources_analyzed=245
        )
    
    def demonstrate_warning_logging(self):
        """Demonstrate WARNING level logging for business users."""
        print("\n=== WARNING Level Logging (Business Users) ===")
        
        # Cost alerts with recommendations
        self.logger.warning_business(
            "High storage costs detected in S3",
            recommendation="Consider implementing lifecycle policies for objects older than 90 days",
            cost_impact=2847.50,
            affected_buckets=12
        )
        
        # Resource optimization alerts
        self.logger.warning_business(
            "Underutilized EC2 instances found",
            recommendation="Review instance sizing for potential rightsizing opportunities",
            cost_impact=1250.00,
            instance_count=8
        )
        
        # Budget threshold warnings
        self.logger.warning_business(
            "Monthly budget threshold exceeded",
            recommendation="Review cost allocation and consider implementing cost controls",
            cost_impact=450.75,
            budget_utilization="105%"
        )
    
    def demonstrate_error_logging(self):
        """Demonstrate ERROR level logging for all users."""
        print("\n=== ERROR Level Logging (All Users) ===")
        
        # AWS authentication errors
        self.logger.error_all(
            "Unable to access Cost Explorer API",
            solution="Run 'aws sso login' to refresh your authentication tokens",
            aws_error="ExpiredToken: Token has expired",
            profile="billing-profile"
        )
        
        # Configuration errors
        self.logger.error_all(
            "Invalid AWS profile configuration",
            solution="Check your ~/.aws/config file or contact your AWS administrator",
            aws_error="ProfileNotFound: The config profile (invalid-profile) could not be found"
        )
        
        # Service access errors
        self.logger.error_all(
            "Insufficient permissions for Organizations API",
            solution="Request 'organizations:ListAccounts' permission or use a different profile",
            aws_error="AccessDenied: User is not authorized to perform organizations:ListAccounts"
        )
    
    def demonstrate_structured_logging(self):
        """Demonstrate structured JSON logging for programmatic use."""
        print("\n=== Structured JSON Logging (Programmatic Use) ===")
        
        # Create JSON logger
        json_logger = get_context_logger(level=self.log_level, json_output=True)
        
        # JSON structured logs
        json_logger.info_standard(
            "Cost analysis completed",
            total_cost=15432.75,
            account_count=5,
            service_breakdown={
                "EC2": 8750.25,
                "S3": 3200.50,
                "RDS": 2482.00,
                "Lambda": 1000.00
            }
        )
        
        json_logger.warning_business(
            "Budget variance detected",
            recommendation="Implement cost controls",
            cost_impact=2500.00,
            variance_percentage=15.2
        )
    
    def demonstrate_contextual_logging(self):
        """Demonstrate context-aware logging based on execution environment."""
        print("\n=== Context-Aware Logging ===")
        
        # Logging adapts to CLI vs Jupyter vs CI/CD environments
        self.logger.info_standard("Environment-aware logging initialized")
        
        # Performance logging with context
        with self.logger_performance_context("cost_analysis_operation") as perf:
            # Simulate work
            time.sleep(0.2)
            perf.add_metric("accounts_processed", 12)
            perf.add_metric("cost_data_points", 1500)


def demo_user_type_scenarios():
    """
    Demonstrate logging for different user types and scenarios.
    """
    print("Enhanced Multi-Level Logging System Demo")
    print("=" * 50)
    
    # Tech users (DEBUG level)
    print("\n🔧 TECH USER SCENARIO (--log-level DEBUG)")
    tech_demo = EnhancedLoggingExample(log_level="DEBUG")
    tech_demo.demonstrate_debug_logging()
    
    # Standard users (INFO level) 
    print("\n👥 STANDARD USER SCENARIO (--log-level INFO)")
    standard_demo = EnhancedLoggingExample(log_level="INFO")
    standard_demo.demonstrate_info_logging()
    
    # Business users (WARNING level)
    print("\n💼 BUSINESS USER SCENARIO (--log-level WARNING)")
    business_demo = EnhancedLoggingExample(log_level="WARNING")
    business_demo.demonstrate_warning_logging()
    
    # Error scenarios (ERROR level)
    print("\n🚨 ERROR SCENARIOS (--log-level ERROR)")
    error_demo = EnhancedLoggingExample(log_level="ERROR")
    error_demo.demonstrate_error_logging()
    
    # JSON output for automation
    print("\n📄 STRUCTURED JSON OUTPUT (--json-output)")
    json_demo = EnhancedLoggingExample(log_level="INFO", json_output=True)
    json_demo.demonstrate_structured_logging()


# Performance context manager for demonstration
class MockPerformanceContext:
    """Mock performance context for demonstration."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.metrics = {}
        self.start_time = time.time()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        print(f"Performance: {self.operation_name} completed in {duration:.3f}s")
        if self.metrics:
            print(f"Metrics: {self.metrics}")
    
    def add_metric(self, key: str, value: Any):
        self.metrics[key] = value


# Add performance context to logger class for demo
EnhancedLoggingExample.logger_performance_context = lambda self, name: MockPerformanceContext(name)


if __name__ == "__main__":
    """Run the enhanced logging demonstration."""
    demo_user_type_scenarios()
#!/usr/bin/env python3
"""
Enhanced Multi-Level Logging Integration Example

This example demonstrates how modules can integrate with the enhanced
multi-level logging architecture for user-type specific content.

## Usage Examples by Log Level

### Tech Users (DEBUG level)
```bash
runbooks finops --log-level DEBUG --profile my-profile
```

### Standard Users (INFO level - default)  
```bash
runbooks finops --profile my-profile
```

### Business Users (WARNING level)
```bash
runbooks finops --log-level WARNING --profile my-profile  
```

### Error Focus (ERROR level)
```bash
runbooks finops --log-level ERROR --profile my-profile
```

Author: CloudOps Runbooks Team
"""

import time
from typing import Optional, Dict, Any, List

try:
    import boto3
except ImportError:
    boto3 = None

from runbooks.enterprise.logging import get_module_logger


class EnhancedLoggingIntegrationExample:
    """Example class demonstrating enhanced logging integration patterns."""

    def __init__(self, module_name: str = "example", log_level: str = "INFO", json_output: bool = False):
        """
        Initialize with enhanced logging.
        
        Args:
            module_name: Name of the module
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            json_output: Enable JSON output for programmatic use
        """
        self.logger = get_module_logger(module_name, level=log_level, json_output=json_output)
        self.log_level = log_level.upper()

    def demonstrate_aws_operation_logging(self):
        """Demonstrate AWS operation logging with different levels."""
        print(f"\n📊 AWS OPERATION LOGGING EXAMPLES ({self.log_level} level)")
        print("=" * 60)

        # Simulate AWS operations with different outcomes
        operations = [
            {"service": "cost-explorer", "operation": "get_cost_and_usage", "duration": 0.8, "success": True, "resource_count": 25},
            {"service": "ec2", "operation": "describe_instances", "duration": 1.2, "success": True, "resource_count": 10},
            {"service": "s3", "operation": "list_buckets", "duration": 0.3, "success": True, "resource_count": 5},
            {"service": "iam", "operation": "get_account_summary", "duration": 15.2, "success": False, "error": "AccessDenied: Insufficient permissions"}
        ]

        for op in operations:
            self.logger.log_aws_operation(
                operation=op["operation"],
                service=op["service"], 
                duration=op["duration"],
                success=op["success"],
                resource_count=op.get("resource_count"),
                error=op.get("error"),
                request_id=f"req-{int(time.time())}-{hash(op['service']) % 10000}"
            )
            time.sleep(0.1)  # Brief pause for demonstration

    def demonstrate_cost_analysis_logging(self):
        """Demonstrate cost analysis logging with business focus."""
        print(f"\n💰 COST ANALYSIS LOGGING EXAMPLES ({self.log_level} level)")
        print("=" * 60)

        cost_scenarios = [
            {
                "operation": "monthly_ec2_spend_analysis", 
                "cost_impact": 2500.0, 
                "savings_opportunity": 750.0,
                "recommendation": "Consider Reserved Instances for consistent workloads"
            },
            {
                "operation": "s3_storage_optimization",
                "cost_impact": 150.0,
                "savings_opportunity": 45.0, 
                "recommendation": "Implement lifecycle policies for infrequent access data"
            },
            {
                "operation": "unused_eip_analysis",
                "cost_impact": 50.0,
                "savings_opportunity": 50.0,
                "recommendation": "Release 10 unused Elastic IPs immediately"
            }
        ]

        for scenario in cost_scenarios:
            self.logger.log_cost_analysis(**scenario)
            time.sleep(0.1)

    def demonstrate_performance_logging(self):
        """Demonstrate performance metric logging."""
        print(f"\n⚡ PERFORMANCE LOGGING EXAMPLES ({self.log_level} level)")
        print("=" * 60)

        performance_scenarios = [
            {"operation": "inventory_collection", "duration": 2.1, "threshold": 5.0, "memory_usage": 52428800},  # Fast operation
            {"operation": "large_cost_analysis", "duration": 8.5, "threshold": 5.0, "memory_usage": 104857600},  # Slow operation
            {"operation": "security_scan", "duration": 0.8, "threshold": 2.0, "memory_usage": 26214400}  # Quick scan
        ]

        for scenario in performance_scenarios:
            self.logger.log_performance_metric(**scenario)
            time.sleep(0.1)

    def demonstrate_security_logging(self):
        """Demonstrate security finding logging."""
        print(f"\n🔒 SECURITY LOGGING EXAMPLES ({self.log_level} level)")
        print("=" * 60)

        security_findings = [
            {
                "finding": "S3 bucket with public read access detected",
                "severity": "high",
                "remediation_steps": [
                    "Review bucket policy for public access",
                    "Remove public read permissions if not required", 
                    "Enable bucket logging for audit trail"
                ]
            },
            {
                "finding": "IAM user without MFA enabled",
                "severity": "medium",
                "remediation_steps": [
                    "Enable MFA for the affected user",
                    "Review IAM policies for excessive permissions",
                    "Consider using IAM roles instead of users"
                ]
            },
            {
                "finding": "Security group with overly permissive rules",
                "severity": "low",
                "remediation_steps": ["Review and tighten security group rules"]
            }
        ]

        for finding in security_findings:
            self.logger.log_security_finding(**finding)
            time.sleep(0.1)

    def demonstrate_operation_context(self):
        """Demonstrate operation context logging."""
        print(f"\n🔄 OPERATION CONTEXT EXAMPLES ({self.log_level} level)")
        print("=" * 60)

        # Successful operation
        with self.logger.operation_context("cost_dashboard_generation", account_count=5, region_count=3):
            time.sleep(1.0)  # Simulate work
            self.logger.info_standard("Generated cost dashboard", resource_count=25)

        time.sleep(0.2)

        # Failed operation (simulated)
        try:
            with self.logger.operation_context("unauthorized_operation", api_call="iam:GetAccountSummary"):
                time.sleep(0.5)
                raise PermissionError("Access denied: Insufficient IAM permissions for operation")
        except PermissionError:
            pass  # Expected for demonstration

    def demonstrate_json_output(self):
        """Demonstrate JSON output for programmatic use."""
        print(f"\n📋 JSON OUTPUT EXAMPLE ({self.log_level} level)")
        print("=" * 60)
        
        # Create a JSON logger
        json_logger = get_module_logger("example_json", level=self.log_level, json_output=True)
        
        json_logger.info_standard("JSON output demonstration", resource_count=42, operation_status="completed")
        json_logger.log_cost_analysis(
            "json_cost_analysis",
            cost_impact=1200.0,
            savings_opportunity=360.0,
            recommendation="Optimize resource allocation for cost efficiency"
        )

    def run_all_demonstrations(self):
        """Run all logging demonstrations."""
        print(f"\n🎯 ENHANCED MULTI-LEVEL LOGGING DEMONSTRATION")
        print(f"Current Log Level: {self.log_level}")
        print(f"User Type Focus: {self._get_user_type_description()}")
        print("=" * 80)

        self.demonstrate_aws_operation_logging()
        self.demonstrate_cost_analysis_logging()
        self.demonstrate_performance_logging()
        self.demonstrate_security_logging()
        self.demonstrate_operation_context()
        
        if not hasattr(self.logger, 'json_output') or not self.logger.json_output:
            self.demonstrate_json_output()

    def _get_user_type_description(self) -> str:
        """Get user type description for current log level."""
        descriptions = {
            "DEBUG": "Tech Users (SRE/DevOps) - Full technical details, API traces, performance metrics",
            "INFO": "Standard Users - Clean operation status, progress indicators, business-friendly output",
            "WARNING": "Business Users - Cost insights, recommendations, optimization opportunities", 
            "ERROR": "All Users - Clear error messages with solutions and troubleshooting steps"
        }
        return descriptions.get(self.log_level, "Unknown user type")


def main():
    """Main demonstration function."""
    print("🚀 ENHANCED MULTI-LEVEL LOGGING ARCHITECTURE DEMONSTRATION")
    print("=" * 80)
    print("This demonstration shows how logging adapts content based on user type:")
    print("• DEBUG Level: Technical users (SRE/DevOps)")
    print("• INFO Level: Standard users (default)")  
    print("• WARNING Level: Business users")
    print("• ERROR Level: All users (minimal output)")
    print("=" * 80)

    # Test all log levels
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    
    for level in log_levels:
        demo = EnhancedLoggingIntegrationExample("enhanced_logging_demo", level)
        demo.run_all_demonstrations()
        
        if level != "ERROR":  # Add separator except for last level
            print(f"\n{'=' * 80}\n")

    print("\n✅ DEMONSTRATION COMPLETE")
    print("\nTo use enhanced logging in your module:")
    print("1. from runbooks.enterprise.logging import get_module_logger")  
    print("2. logger = get_module_logger('your_module_name')")
    print("3. Use logger.info_standard(), logger.debug_tech(), logger.warning_business(), etc.")
    print("4. Use logger.log_aws_operation(), logger.log_cost_analysis() for convenience")


if __name__ == "__main__":
    main()
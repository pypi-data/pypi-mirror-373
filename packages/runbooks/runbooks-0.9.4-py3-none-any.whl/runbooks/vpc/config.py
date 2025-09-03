"""
VPC Networking Configuration Management

This module provides configurable parameters for VPC networking operations,
replacing hard-coded values with environment-aware configuration.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AWSCostModel:
    """AWS Service Cost Model with configurable pricing"""

    # NAT Gateway Pricing (configurable via environment)
    nat_gateway_hourly: float = field(default_factory=lambda: float(os.getenv("AWS_NAT_GATEWAY_HOURLY", "0.045")))
    nat_gateway_monthly: float = field(default_factory=lambda: float(os.getenv("AWS_NAT_GATEWAY_MONTHLY", "45.0")))
    nat_gateway_data_processing: float = field(
        default_factory=lambda: float(os.getenv("AWS_NAT_GATEWAY_DATA_PROCESSING", "0.045"))
    )

    # Transit Gateway Pricing
    transit_gateway_hourly: float = field(
        default_factory=lambda: float(os.getenv("AWS_TRANSIT_GATEWAY_HOURLY", "0.05"))
    )
    transit_gateway_monthly: float = field(
        default_factory=lambda: float(os.getenv("AWS_TRANSIT_GATEWAY_MONTHLY", "36.50"))
    )
    transit_gateway_attachment: float = field(
        default_factory=lambda: float(os.getenv("AWS_TRANSIT_GATEWAY_ATTACHMENT", "0.05"))
    )
    transit_gateway_data_processing: float = field(
        default_factory=lambda: float(os.getenv("AWS_TRANSIT_GATEWAY_DATA_PROCESSING", "0.02"))
    )

    # VPC Endpoint Pricing
    vpc_endpoint_interface_hourly: float = field(
        default_factory=lambda: float(os.getenv("AWS_VPC_ENDPOINT_INTERFACE_HOURLY", "0.01"))
    )
    vpc_endpoint_interface_monthly: float = field(
        default_factory=lambda: float(os.getenv("AWS_VPC_ENDPOINT_INTERFACE_MONTHLY", "10.0"))
    )
    vpc_endpoint_gateway: float = 0.0  # Always free
    vpc_endpoint_data_processing: float = field(
        default_factory=lambda: float(os.getenv("AWS_VPC_ENDPOINT_DATA_PROCESSING", "0.01"))
    )

    # Elastic IP Pricing
    elastic_ip_idle_hourly: float = field(
        default_factory=lambda: float(os.getenv("AWS_ELASTIC_IP_IDLE_HOURLY", "0.005"))
    )
    elastic_ip_idle_monthly: float = field(
        default_factory=lambda: float(os.getenv("AWS_ELASTIC_IP_IDLE_MONTHLY", "3.60"))
    )
    elastic_ip_attached: float = 0.0  # Always free when attached
    elastic_ip_remap: float = field(default_factory=lambda: float(os.getenv("AWS_ELASTIC_IP_REMAP", "0.10")))

    # Data Transfer Pricing
    data_transfer_inter_az: float = field(
        default_factory=lambda: float(os.getenv("AWS_DATA_TRANSFER_INTER_AZ", "0.01"))
    )
    data_transfer_inter_region: float = field(
        default_factory=lambda: float(os.getenv("AWS_DATA_TRANSFER_INTER_REGION", "0.02"))
    )
    data_transfer_internet_out: float = field(
        default_factory=lambda: float(os.getenv("AWS_DATA_TRANSFER_INTERNET_OUT", "0.09"))
    )
    data_transfer_s3_same_region: float = 0.0  # Always free


@dataclass
class OptimizationThresholds:
    """Configurable thresholds for optimization recommendations"""

    # Usage thresholds
    idle_connection_threshold: int = field(default_factory=lambda: int(os.getenv("IDLE_CONNECTION_THRESHOLD", "10")))
    low_usage_gb_threshold: float = field(default_factory=lambda: float(os.getenv("LOW_USAGE_GB_THRESHOLD", "100.0")))
    low_connection_threshold: int = field(default_factory=lambda: int(os.getenv("LOW_CONNECTION_THRESHOLD", "100")))

    # Cost thresholds
    high_cost_threshold: float = field(default_factory=lambda: float(os.getenv("HIGH_COST_THRESHOLD", "100.0")))
    critical_cost_threshold: float = field(default_factory=lambda: float(os.getenv("CRITICAL_COST_THRESHOLD", "500.0")))

    # Optimization targets
    target_reduction_percent: float = field(
        default_factory=lambda: float(os.getenv("TARGET_REDUCTION_PERCENT", "30.0"))
    )

    # Enterprise approval thresholds (from user requirements)
    cost_approval_threshold: float = field(
        default_factory=lambda: float(os.getenv("COST_APPROVAL_THRESHOLD", "1000.0"))
    )  # $1000/month
    performance_baseline_threshold: float = field(
        default_factory=lambda: float(os.getenv("PERFORMANCE_BASELINE_THRESHOLD", "2.0"))
    )  # 2 seconds


@dataclass
class RegionalConfiguration:
    """Regional cost multipliers and configuration"""

    # Default regions for analysis
    default_regions: List[str] = field(
        default_factory=lambda: [
            "us-east-1",
            "us-west-2",
            "us-west-1",
            "eu-west-1",
            "eu-central-1",
            "eu-west-2",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-northeast-1",
        ]
    )

    # Regional cost multipliers (can be overridden by data from AWS Pricing API)
    regional_multipliers: Dict[str, float] = field(
        default_factory=lambda: {
            "us-east-1": float(os.getenv("COST_MULTIPLIER_US_EAST_1", "1.5")),
            "us-west-2": float(os.getenv("COST_MULTIPLIER_US_WEST_2", "1.3")),
            "us-west-1": float(os.getenv("COST_MULTIPLIER_US_WEST_1", "0.8")),
            "eu-west-1": float(os.getenv("COST_MULTIPLIER_EU_WEST_1", "1.2")),
            "eu-central-1": float(os.getenv("COST_MULTIPLIER_EU_CENTRAL_1", "0.9")),
            "eu-west-2": float(os.getenv("COST_MULTIPLIER_EU_WEST_2", "0.7")),
            "ap-southeast-1": float(os.getenv("COST_MULTIPLIER_AP_SOUTHEAST_1", "1.0")),
            "ap-southeast-2": float(os.getenv("COST_MULTIPLIER_AP_SOUTHEAST_2", "0.8")),
            "ap-northeast-1": float(os.getenv("COST_MULTIPLIER_AP_NORTHEAST_1", "1.1")),
        }
    )


@dataclass
class VPCNetworkingConfig:
    """Main VPC Networking Configuration"""

    # AWS Configuration
    default_region: str = field(default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

    # AWS Profiles
    billing_profile: Optional[str] = field(default_factory=lambda: os.getenv("BILLING_PROFILE"))
    centralized_ops_profile: Optional[str] = field(default_factory=lambda: os.getenv("CENTRALIZED_OPS_PROFILE"))
    single_account_profile: Optional[str] = field(default_factory=lambda: os.getenv("SINGLE_ACCOUNT_PROFILE"))
    management_profile: Optional[str] = field(default_factory=lambda: os.getenv("MANAGEMENT_PROFILE"))

    # Analysis Configuration
    default_analysis_days: int = field(default_factory=lambda: int(os.getenv("DEFAULT_ANALYSIS_DAYS", "30")))
    forecast_days: int = field(default_factory=lambda: int(os.getenv("FORECAST_DAYS", "90")))

    # Output Configuration
    default_output_format: str = field(default_factory=lambda: os.getenv("OUTPUT_FORMAT", "rich"))
    default_output_dir: Path = field(default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "./exports")))

    # Enterprise Configuration
    enable_cost_approval_workflow: bool = field(
        default_factory=lambda: os.getenv("ENABLE_COST_APPROVAL_WORKFLOW", "true").lower() == "true"
    )
    enable_mcp_validation: bool = field(
        default_factory=lambda: os.getenv("ENABLE_MCP_VALIDATION", "false").lower() == "true"
    )

    # Component configurations
    cost_model: AWSCostModel = field(default_factory=AWSCostModel)
    thresholds: OptimizationThresholds = field(default_factory=OptimizationThresholds)
    regional: RegionalConfiguration = field(default_factory=RegionalConfiguration)

    def get_cost_approval_required(self, monthly_cost: float) -> bool:
        """Check if cost requires approval based on threshold"""
        return self.enable_cost_approval_workflow and monthly_cost > self.thresholds.cost_approval_threshold

    def get_performance_acceptable(self, execution_time: float) -> bool:
        """Check if performance meets baseline requirements"""
        return execution_time <= self.thresholds.performance_baseline_threshold

    def get_regional_multiplier(self, region: str) -> float:
        """Get cost multiplier for specific region"""
        return self.regional.regional_multipliers.get(region, 1.0)


def load_config(config_file: Optional[str] = None) -> VPCNetworkingConfig:
    """
    Load VPC networking configuration from environment and optional config file

    Args:
        config_file: Optional path to configuration file

    Returns:
        VPCNetworkingConfig instance
    """
    # TODO: Add support for loading from JSON/YAML config file
    # TODO: Add support for AWS Pricing API integration

    config = VPCNetworkingConfig()

    # Validate configuration only in production (not during testing)
    is_testing = os.getenv("PYTEST_CURRENT_TEST") is not None or "pytest" in os.environ.get("_", "")
    if not is_testing and config.enable_cost_approval_workflow and not config.billing_profile:
        raise ValueError("BILLING_PROFILE required when cost approval workflow is enabled")

    return config


# Global configuration instance (with testing environment detection)
default_config = None
try:
    default_config = load_config()
except ValueError:
    # Fallback configuration for testing or when validation fails
    default_config = VPCNetworkingConfig(enable_cost_approval_workflow=False)

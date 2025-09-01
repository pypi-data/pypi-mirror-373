"""
Tests for VPC Configuration Management

Tests the configuration system for VPC networking operations,
including environment variable handling and validation.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from runbooks.vpc.config import (
    AWSCostModel,
    OptimizationThresholds,
    RegionalConfiguration,
    VPCNetworkingConfig,
    load_config,
)


@pytest.mark.unit
class TestAWSCostModel:
    """Test AWS Cost Model configuration."""

    def test_default_cost_model(self):
        """Test default AWS cost model values."""
        cost_model = AWSCostModel()

        # NAT Gateway pricing defaults
        assert cost_model.nat_gateway_hourly == 0.045
        assert cost_model.nat_gateway_monthly == 45.0
        assert cost_model.nat_gateway_data_processing == 0.045

        # Transit Gateway pricing defaults
        assert cost_model.transit_gateway_hourly == 0.05
        assert cost_model.transit_gateway_monthly == 36.50
        assert cost_model.transit_gateway_attachment == 0.05
        assert cost_model.transit_gateway_data_processing == 0.02

        # VPC Endpoint pricing defaults
        assert cost_model.vpc_endpoint_interface_hourly == 0.01
        assert cost_model.vpc_endpoint_interface_monthly == 10.0
        assert cost_model.vpc_endpoint_gateway == 0.0
        assert cost_model.vpc_endpoint_data_processing == 0.01

        # Elastic IP pricing defaults
        assert cost_model.elastic_ip_idle_hourly == 0.005
        assert cost_model.elastic_ip_idle_monthly == 3.60
        assert cost_model.elastic_ip_attached == 0.0
        assert cost_model.elastic_ip_remap == 0.10

    def test_cost_model_with_environment_variables(self):
        """Test cost model with custom environment variables."""
        env_vars = {
            "AWS_NAT_GATEWAY_HOURLY": "0.050",
            "AWS_NAT_GATEWAY_MONTHLY": "50.0",
            "AWS_VPC_ENDPOINT_INTERFACE_MONTHLY": "12.0",
            "AWS_ELASTIC_IP_IDLE_MONTHLY": "4.0",
        }

        with patch.dict(os.environ, env_vars):
            cost_model = AWSCostModel()

            assert cost_model.nat_gateway_hourly == 0.050
            assert cost_model.nat_gateway_monthly == 50.0
            assert cost_model.vpc_endpoint_interface_monthly == 12.0
            assert cost_model.elastic_ip_idle_monthly == 4.0

    def test_cost_model_data_transfer_pricing(self):
        """Test data transfer pricing configuration."""
        cost_model = AWSCostModel()

        assert cost_model.data_transfer_inter_az == 0.01
        assert cost_model.data_transfer_inter_region == 0.02
        assert cost_model.data_transfer_internet_out == 0.09
        assert cost_model.data_transfer_s3_same_region == 0.0  # Always free


@pytest.mark.unit
class TestOptimizationThresholds:
    """Test optimization thresholds configuration."""

    def test_default_optimization_thresholds(self):
        """Test default optimization threshold values."""
        thresholds = OptimizationThresholds()

        # Usage thresholds
        assert thresholds.idle_connection_threshold == 10
        assert thresholds.low_usage_gb_threshold == 100.0
        assert thresholds.low_connection_threshold == 100

        # Cost thresholds
        assert thresholds.high_cost_threshold == 100.0
        assert thresholds.critical_cost_threshold == 500.0

        # Optimization targets
        assert thresholds.target_reduction_percent == 30.0

        # Enterprise thresholds
        assert thresholds.cost_approval_threshold == 1000.0
        assert thresholds.performance_baseline_threshold == 2.0

    def test_optimization_thresholds_with_environment(self):
        """Test optimization thresholds with environment variables."""
        env_vars = {
            "IDLE_CONNECTION_THRESHOLD": "20",
            "LOW_USAGE_GB_THRESHOLD": "150.0",
            "TARGET_REDUCTION_PERCENT": "40.0",
            "COST_APPROVAL_THRESHOLD": "2000.0",
            "PERFORMANCE_BASELINE_THRESHOLD": "1.5",
        }

        with patch.dict(os.environ, env_vars):
            thresholds = OptimizationThresholds()

            assert thresholds.idle_connection_threshold == 20
            assert thresholds.low_usage_gb_threshold == 150.0
            assert thresholds.target_reduction_percent == 40.0
            assert thresholds.cost_approval_threshold == 2000.0
            assert thresholds.performance_baseline_threshold == 1.5

    def test_threshold_validation_logic(self):
        """Test threshold validation and logic."""
        thresholds = OptimizationThresholds()

        # Test threshold relationships
        assert thresholds.idle_connection_threshold < thresholds.low_connection_threshold
        assert thresholds.high_cost_threshold < thresholds.critical_cost_threshold
        assert 0 < thresholds.target_reduction_percent < 100


@pytest.mark.unit
class TestRegionalConfiguration:
    """Test regional configuration settings."""

    def test_default_regional_configuration(self):
        """Test default regional configuration."""
        regional = RegionalConfiguration()

        # Default regions
        expected_regions = [
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
        assert regional.default_regions == expected_regions

        # Regional multipliers
        assert "us-east-1" in regional.regional_multipliers
        assert "eu-west-1" in regional.regional_multipliers
        assert "ap-southeast-1" in regional.regional_multipliers

        # Validate multiplier values are positive
        for region, multiplier in regional.regional_multipliers.items():
            assert multiplier > 0, f"Invalid multiplier for {region}: {multiplier}"

    def test_regional_multipliers_with_environment(self):
        """Test regional multipliers with environment variables."""
        env_vars = {
            "COST_MULTIPLIER_US_EAST_1": "2.0",
            "COST_MULTIPLIER_EU_WEST_1": "1.5",
            "COST_MULTIPLIER_AP_SOUTHEAST_1": "1.8",
        }

        with patch.dict(os.environ, env_vars):
            regional = RegionalConfiguration()

            assert regional.regional_multipliers["us-east-1"] == 2.0
            assert regional.regional_multipliers["eu-west-1"] == 1.5
            assert regional.regional_multipliers["ap-southeast-1"] == 1.8

    def test_regional_configuration_coverage(self):
        """Test that regional configuration covers major AWS regions."""
        regional = RegionalConfiguration()

        # Check major regions are covered
        major_regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        for region in major_regions:
            assert region in regional.default_regions
            assert region in regional.regional_multipliers


@pytest.mark.unit
class TestVPCNetworkingConfig:
    """Test main VPC networking configuration."""

    def test_default_vpc_networking_config(self):
        """Test default VPC networking configuration."""
        config = VPCNetworkingConfig()

        # AWS configuration
        assert config.default_region == "us-east-1"
        assert config.billing_profile is None
        assert config.centralized_ops_profile is None
        assert config.single_account_profile is None
        assert config.management_profile is None

        # Analysis configuration
        assert config.default_analysis_days == 30
        assert config.forecast_days == 90

        # Output configuration
        assert config.default_output_format == "rich"
        assert str(config.default_output_dir) in ["./exports", "exports"]

        # Enterprise configuration
        assert config.enable_cost_approval_workflow is True
        assert config.enable_mcp_validation is False

        # Component configurations
        assert isinstance(config.cost_model, AWSCostModel)
        assert isinstance(config.thresholds, OptimizationThresholds)
        assert isinstance(config.regional, RegionalConfiguration)

    def test_vpc_config_with_environment_variables(self):
        """Test VPC configuration with environment variables."""
        env_vars = {
            "AWS_DEFAULT_REGION": "us-west-2",
            "BILLING_PROFILE": "test-billing-profile",
            "CENTRALIZED_OPS_PROFILE": "test-ops-profile",
            "SINGLE_ACCOUNT_PROFILE": "test-single-profile",
            "MANAGEMENT_PROFILE": "test-mgmt-profile",
            "DEFAULT_ANALYSIS_DAYS": "45",
            "FORECAST_DAYS": "120",
            "OUTPUT_FORMAT": "json",
            "OUTPUT_DIR": "/tmp/vpc-exports",
            "ENABLE_COST_APPROVAL_WORKFLOW": "false",
            "ENABLE_MCP_VALIDATION": "true",
        }

        with patch.dict(os.environ, env_vars):
            config = VPCNetworkingConfig()

            assert config.default_region == "us-west-2"
            assert config.billing_profile == "test-billing-profile"
            assert config.centralized_ops_profile == "test-ops-profile"
            assert config.single_account_profile == "test-single-profile"
            assert config.management_profile == "test-mgmt-profile"
            assert config.default_analysis_days == 45
            assert config.forecast_days == 120
            assert config.default_output_format == "json"
            assert str(config.default_output_dir) == "/tmp/vpc-exports"
            assert config.enable_cost_approval_workflow is False
            assert config.enable_mcp_validation is True

    def test_cost_approval_required_method(self):
        """Test cost approval required logic."""
        config = VPCNetworkingConfig()

        # Test below threshold
        assert not config.get_cost_approval_required(500.0)

        # Test above threshold
        assert config.get_cost_approval_required(1500.0)

        # Test with disabled approval workflow
        config.enable_cost_approval_workflow = False
        assert not config.get_cost_approval_required(1500.0)

    def test_performance_acceptable_method(self):
        """Test performance acceptable logic."""
        config = VPCNetworkingConfig()

        # Test acceptable performance
        assert config.get_performance_acceptable(1.5)

        # Test unacceptable performance
        assert not config.get_performance_acceptable(3.0)

        # Test exact threshold
        assert config.get_performance_acceptable(2.0)

    def test_regional_multiplier_method(self):
        """Test regional multiplier retrieval."""
        config = VPCNetworkingConfig()

        # Test known region
        multiplier = config.get_regional_multiplier("us-east-1")
        assert multiplier > 0

        # Test unknown region (should return default)
        multiplier = config.get_regional_multiplier("unknown-region")
        assert multiplier == 1.0

    def test_config_component_relationships(self):
        """Test relationships between configuration components."""
        config = VPCNetworkingConfig()

        # Validate cost model thresholds align with optimization thresholds
        assert config.cost_model.nat_gateway_monthly == 45.0
        assert config.thresholds.cost_approval_threshold == 1000.0

        # Validate that approval threshold is reasonable compared to costs
        monthly_nat_cost = config.cost_model.nat_gateway_monthly
        approval_threshold = config.thresholds.cost_approval_threshold
        assert approval_threshold > monthly_nat_cost * 10  # Should require many resources


@pytest.mark.unit
class TestLoadConfig:
    """Test configuration loading function."""

    def test_load_default_config(self):
        """Test loading default configuration."""
        config = load_config()

        assert isinstance(config, VPCNetworkingConfig)
        assert isinstance(config.cost_model, AWSCostModel)
        assert isinstance(config.thresholds, OptimizationThresholds)
        assert isinstance(config.regional, RegionalConfiguration)

    def test_load_config_validation_success(self):
        """Test configuration validation success."""
        env_vars = {"BILLING_PROFILE": "test-billing-profile", "ENABLE_COST_APPROVAL_WORKFLOW": "true"}

        with patch.dict(os.environ, env_vars):
            config = load_config()

            assert config.billing_profile == "test-billing-profile"
            assert config.enable_cost_approval_workflow is True

    def test_load_config_validation_failure(self):
        """Test configuration validation failure."""
        env_vars = {
            "ENABLE_COST_APPROVAL_WORKFLOW": "true",
            "BILLING_PROFILE": "",  # Empty billing profile
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="BILLING_PROFILE required"):
                load_config()

    def test_load_config_with_file_parameter(self):
        """Test loading configuration with config file parameter."""
        # TODO: Implement when config file support is added
        config = load_config(config_file=None)

        # Should work with None (uses environment variables)
        assert isinstance(config, VPCNetworkingConfig)

    @pytest.mark.integration
    def test_configuration_environment_isolation(self):
        """Test that configuration properly isolates environment variables."""
        # Set initial environment
        initial_env = {"AWS_DEFAULT_REGION": "us-east-1", "BILLING_PROFILE": "initial-profile"}

        with patch.dict(os.environ, initial_env, clear=True):
            config1 = load_config()
            assert config1.default_region == "us-east-1"
            assert config1.billing_profile == "initial-profile"

        # Change environment
        changed_env = {"AWS_DEFAULT_REGION": "us-west-2", "BILLING_PROFILE": "changed-profile"}

        with patch.dict(os.environ, changed_env, clear=True):
            config2 = load_config()
            assert config2.default_region == "us-west-2"
            assert config2.billing_profile == "changed-profile"

        # Confirm original config unchanged
        assert config1.default_region == "us-east-1"
        assert config1.billing_profile == "initial-profile"


@pytest.mark.performance
class TestConfigurationPerformance:
    """Test configuration loading performance."""

    def test_config_loading_performance(self):
        """Test configuration loading performance benchmark."""
        import time

        start_time = time.time()

        # Load configuration multiple times
        for _ in range(10):
            config = load_config()

        execution_time = time.time() - start_time

        # Configuration loading should be very fast
        assert execution_time < 1.0, f"Configuration loading too slow: {execution_time:.2f}s"

    def test_config_memory_usage(self):
        """Test configuration memory efficiency."""
        import sys

        # Get initial memory usage
        initial_size = sys.getsizeof({})

        config = load_config()

        # Configuration should not use excessive memory
        config_size = sys.getsizeof(config.__dict__)

        # Should be reasonable for configuration data
        assert config_size < 10000, f"Configuration using too much memory: {config_size} bytes"


@pytest.mark.security
class TestConfigurationSecurity:
    """Test configuration security aspects."""

    def test_no_credentials_in_config(self):
        """Test that configuration doesn't expose credentials."""
        config = load_config()

        # Convert config to string representation
        config_str = str(config.__dict__)

        # Check for common credential patterns
        sensitive_patterns = ["AKIA", "SECRET", "TOKEN", "PASSWORD", "KEY"]
        for pattern in sensitive_patterns:
            assert pattern not in config_str.upper(), f"Potentially sensitive pattern '{pattern}' found in config"

    def test_profile_name_validation(self):
        """Test profile name validation and sanitization."""
        # Test with potentially dangerous profile names
        dangerous_profiles = ["profile; rm -rf /", "profile && malicious_command", "profile | grep secrets"]

        for dangerous_profile in dangerous_profiles:
            env_vars = {"BILLING_PROFILE": dangerous_profile}

            with patch.dict(os.environ, env_vars):
                config = load_config()

                # Profile name should be stored as-is (validation happens at usage)
                assert config.billing_profile == dangerous_profile

    def test_environment_variable_precedence(self):
        """Test environment variable precedence and override behavior."""
        # Set base environment
        base_env = {"AWS_DEFAULT_REGION": "us-east-1", "BILLING_PROFILE": "base-profile"}

        with patch.dict(os.environ, base_env):
            config = load_config()

            # Verify base values
            assert config.default_region == "us-east-1"
            assert config.billing_profile == "base-profile"

        # Override with new values
        override_env = {"AWS_DEFAULT_REGION": "eu-west-1", "BILLING_PROFILE": "override-profile"}

        with patch.dict(os.environ, override_env):
            config_override = load_config()

            # Verify override values
            assert config_override.default_region == "eu-west-1"
            assert config_override.billing_profile == "override-profile"

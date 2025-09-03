"""
Tests for VPC CLI Integration

Tests the VPC command-line interface integration with the main runbooks CLI.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from runbooks.main import main


@pytest.mark.cli
class TestVPCCLIIntegration:
    """Test VPC CLI integration with main runbooks CLI."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_vpc_help_command(self):
        """Test VPC help command."""
        result = self.runner.invoke(main, ["vpc", "--help"])

        assert result.exit_code == 0
        assert "VPC Networking Analysis" in result.output or "vpc" in result.output.lower()

    def test_vpc_analyze_help_command(self):
        """Test VPC analyze command help."""
        result = self.runner.invoke(main, ["vpc", "analyze", "--help"])

        assert result.exit_code == 0
        assert "--profile" in result.output
        assert "--region" in result.output
        assert "--days" in result.output

    def test_vpc_heatmap_help_command(self):
        """Test VPC heatmap command help."""
        result = self.runner.invoke(main, ["vpc", "heatmap", "--help"])

        assert result.exit_code == 0
        assert "--account-scope" in result.output

    def test_vpc_optimize_help_command(self):
        """Test VPC optimize command help."""
        result = self.runner.invoke(main, ["vpc", "optimize", "--help"])

        assert result.exit_code == 0
        assert "--target-reduction" in result.output

    @pytest.mark.integration
    def test_vpc_analyze_command_execution(self):
        """Test VPC analyze command execution."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            # Configure mock wrapper
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {
                "nat_gateways": [],
                "total_cost": 0.0,
                "optimization_potential": 0.0,
                "recommendations": [],
            }
            mock_wrapper.analyze_vpc_endpoints.return_value = {
                "vpc_endpoints": [],
                "total_cost": 0.0,
                "optimization_potential": 0.0,
                "recommendations": [],
            }
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(
                main, ["vpc", "analyze", "--profile", "test-profile", "--region", "us-east-1", "--days", "30"]
            )

            assert result.exit_code == 0

            # Verify wrapper was initialized with correct parameters
            mock_wrapper_class.assert_called_once()
            init_args = mock_wrapper_class.call_args
            assert init_args[1]["profile"] == "test-profile"
            assert init_args[1]["region"] == "us-east-1"

            # Verify analysis methods were called
            mock_wrapper.analyze_nat_gateways.assert_called_once_with(days=30)
            mock_wrapper.analyze_vpc_endpoints.assert_called_once()

    @pytest.mark.integration
    def test_vpc_heatmap_command_execution(self):
        """Test VPC heatmap command execution."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            # Configure mock wrapper
            mock_wrapper = Mock()
            mock_wrapper.generate_cost_heatmaps.return_value = {
                "heatmap_data": "sample_data",
                "regions": ["us-east-1", "us-west-2"],
            }
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(
                main, ["vpc", "heatmap", "--account-scope", "single", "--profile", "test-profile"]
            )

            assert result.exit_code == 0

            # Verify wrapper was initialized
            mock_wrapper_class.assert_called_once()

            # Verify heatmap generation was called
            mock_wrapper.generate_cost_heatmaps.assert_called_once_with(account_scope="single")

    @pytest.mark.integration
    def test_vpc_optimize_command_execution(self):
        """Test VPC optimize command execution."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            # Configure mock wrapper
            mock_wrapper = Mock()
            mock_wrapper.optimize_networking_costs.return_value = {
                "current_monthly_cost": 100.0,
                "potential_savings": 30.0,
                "projected_monthly_cost": 70.0,
                "recommendations": [],
                "implementation_plan": [],
            }
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(
                main, ["vpc", "optimize", "--target-reduction", "30", "--profile", "test-profile"]
            )

            assert result.exit_code == 0

            # Verify wrapper was initialized
            mock_wrapper_class.assert_called_once()

            # Verify optimization was called with correct target
            mock_wrapper.optimize_networking_costs.assert_called_once_with(target_reduction=30.0)

    def test_vpc_analyze_with_invalid_profile(self):
        """Test VPC analyze with invalid profile handling."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            # Configure wrapper to simulate connection failure
            mock_wrapper = Mock()
            mock_wrapper.session = None  # No session indicates connection failure
            mock_wrapper.analyze_nat_gateways.return_value = {
                "nat_gateways": [],
                "total_cost": 0.0,
                "optimization_potential": 0.0,
                "recommendations": [],
            }
            mock_wrapper.analyze_vpc_endpoints.return_value = {
                "vpc_endpoints": [],
                "total_cost": 0.0,
                "optimization_potential": 0.0,
                "recommendations": [],
            }
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(main, ["vpc", "analyze", "--profile", "invalid-profile"])

            # Should still succeed but with empty results
            assert result.exit_code == 0

    def test_vpc_command_with_output_format_json(self):
        """Test VPC command with JSON output format."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {
                "nat_gateways": [{"id": "nat-123", "cost": 45.0}],
                "total_cost": 45.0,
            }
            mock_wrapper.analyze_vpc_endpoints.return_value = {
                "vpc_endpoints": [{"id": "vpce-123", "cost": 10.0}],
                "total_cost": 10.0,
            }
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(main, ["vpc", "analyze", "--output-format", "json"])

            assert result.exit_code == 0

            # Verify wrapper was initialized with JSON output format
            init_args = mock_wrapper_class.call_args
            assert init_args[1]["output_format"] == "json"

    @pytest.mark.performance
    def test_vpc_cli_response_time(self, performance_benchmarks, assert_performance_benchmark):
        """Test VPC CLI response time performance."""
        import time

        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            # Configure fast mock response
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {"nat_gateways": []}
            mock_wrapper.analyze_vpc_endpoints.return_value = {"vpc_endpoints": []}
            mock_wrapper_class.return_value = mock_wrapper

            start_time = time.time()
            result = self.runner.invoke(main, ["vpc", "analyze"])
            execution_time = time.time() - start_time

            assert result.exit_code == 0

            # Assert CLI response time benchmark
            assert_performance_benchmark(execution_time, "cli_response_max_time", performance_benchmarks)

    def test_vpc_analyze_with_billing_profile(self):
        """Test VPC analyze with separate billing profile."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {"nat_gateways": []}
            mock_wrapper.analyze_vpc_endpoints.return_value = {"vpc_endpoints": []}
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(
                main, ["vpc", "analyze", "--profile", "ops-profile", "--billing-profile", "billing-profile"]
            )

            assert result.exit_code == 0

            # Verify both profiles were passed
            init_args = mock_wrapper_class.call_args
            assert init_args[1]["profile"] == "ops-profile"
            assert init_args[1]["billing_profile"] == "billing-profile"

    def test_vpc_heatmap_multi_account_scope(self):
        """Test VPC heatmap with multi-account scope."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.generate_cost_heatmaps.return_value = {
                "accounts": ["123456789012", "123456789013"],
                "heatmap_data": "multi_account_data",
            }
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(main, ["vpc", "heatmap", "--account-scope", "multi"])

            assert result.exit_code == 0

            # Verify multi-account scope was passed
            mock_wrapper.generate_cost_heatmaps.assert_called_once_with(account_scope="multi")

    def test_vpc_optimize_with_high_target_reduction(self):
        """Test VPC optimize with high target reduction."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.optimize_networking_costs.return_value = {
                "target_reduction": 50.0,
                "achievable_reduction": 35.0,
                "recommendations": ["Remove idle NAT Gateways"],
            }
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(main, ["vpc", "optimize", "--target-reduction", "50"])

            assert result.exit_code == 0

            # Verify high target reduction was passed
            mock_wrapper.optimize_networking_costs.assert_called_once_with(target_reduction=50.0)

    @pytest.mark.error_handling
    def test_vpc_command_with_import_error(self):
        """Test VPC command behavior when import fails."""
        with patch("runbooks.main.VPCNetworkingWrapper", side_effect=ImportError("Module not found")):
            result = self.runner.invoke(main, ["vpc", "analyze"])

            # Should handle import error gracefully
            assert result.exit_code != 0
            assert "error" in result.output.lower() or "failed" in result.output.lower()

    @pytest.mark.error_handling
    def test_vpc_analyze_with_aws_error(self):
        """Test VPC analyze command with AWS service error."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            # Configure wrapper to raise AWS error
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.side_effect = Exception("AWS API Error")
            mock_wrapper.analyze_vpc_endpoints.return_value = {"vpc_endpoints": []}
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(main, ["vpc", "analyze", "--profile", "test-profile"])

            # Command should handle error gracefully
            assert result.exit_code == 0  # CLI should not crash

    def test_vpc_command_parameter_validation(self):
        """Test VPC command parameter validation."""
        # Test invalid target reduction
        result = self.runner.invoke(
            main,
            [
                "vpc",
                "optimize",
                "--target-reduction",
                "-10",  # Negative value
            ],
        )

        # Should validate parameters
        assert result.exit_code != 0 or "invalid" in result.output.lower()

        # Test invalid account scope
        result = self.runner.invoke(main, ["vpc", "heatmap", "--account-scope", "invalid-scope"])

        # Should validate parameters
        assert result.exit_code != 0 or "invalid" in result.output.lower()

    @pytest.mark.integration
    def test_vpc_analyze_full_output_verification(self):
        """Test VPC analyze command with comprehensive output verification."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            # Configure detailed mock response
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {
                "nat_gateways": [
                    {
                        "id": "nat-0123456789abcdef0",
                        "state": "available",
                        "monthly_cost": 45.0,
                        "optimization": {"recommendation": "Optimize usage"},
                    }
                ],
                "total_cost": 45.0,
                "optimization_potential": 15.0,
                "recommendations": ["Reduce idle time"],
            }
            mock_wrapper.analyze_vpc_endpoints.return_value = {
                "vpc_endpoints": [
                    {
                        "id": "vpce-0123456789abcdef0",
                        "type": "Interface",
                        "service": "com.amazonaws.us-east-1.s3",
                        "monthly_cost": 20.0,
                    }
                ],
                "total_cost": 20.0,
                "optimization_potential": 5.0,
                "recommendations": ["Reduce AZ coverage"],
            }
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(
                main, ["vpc", "analyze", "--profile", "test-profile", "--output-format", "rich"]
            )

            assert result.exit_code == 0

            # Verify both analysis methods were called
            mock_wrapper.analyze_nat_gateways.assert_called_once()
            mock_wrapper.analyze_vpc_endpoints.assert_called_once()

    @pytest.mark.security
    def test_vpc_cli_credential_handling(self):
        """Test that VPC CLI doesn't expose credentials in output."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            # Configure wrapper with potential credential exposure
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {
                "profile_info": "AKIATEST123456",  # Simulate credential leak
                "nat_gateways": [],
            }
            mock_wrapper.analyze_vpc_endpoints.return_value = {"vpc_endpoints": []}
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(main, ["vpc", "analyze", "--profile", "test-profile"])

            # Verify no credentials in output
            sensitive_patterns = ["AKIA", "SECRET", "TOKEN"]
            for pattern in sensitive_patterns:
                assert pattern not in result.output.upper()

    @pytest.mark.integration
    def test_vpc_command_chaining_workflow(self):
        """Test VPC command workflow integration."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()

            # Configure responses for chained operations
            mock_wrapper.analyze_nat_gateways.return_value = {
                "nat_gateways": [{"id": "nat-123", "monthly_cost": 45.0}],
                "total_cost": 45.0,
                "optimization_potential": 15.0,
            }
            mock_wrapper.analyze_vpc_endpoints.return_value = {
                "vpc_endpoints": [{"id": "vpce-123", "monthly_cost": 10.0}],
                "total_cost": 10.0,
                "optimization_potential": 3.0,
            }
            mock_wrapper.optimize_networking_costs.return_value = {
                "current_monthly_cost": 55.0,
                "potential_savings": 18.0,
                "recommendations": ["Remove idle NAT Gateway"],
            }
            mock_wrapper.generate_cost_heatmaps.return_value = {"heatmap_data": "comprehensive_data"}
            mock_wrapper_class.return_value = mock_wrapper

            # Execute analyze command
            analyze_result = self.runner.invoke(main, ["vpc", "analyze", "--profile", "test-profile"])
            assert analyze_result.exit_code == 0

            # Execute optimize command
            optimize_result = self.runner.invoke(
                main, ["vpc", "optimize", "--profile", "test-profile", "--target-reduction", "30"]
            )
            assert optimize_result.exit_code == 0

            # Execute heatmap command
            heatmap_result = self.runner.invoke(main, ["vpc", "heatmap", "--profile", "test-profile"])
            assert heatmap_result.exit_code == 0

            # Verify all methods were called across commands
            assert mock_wrapper.analyze_nat_gateways.call_count >= 2  # Called in analyze and optimize
            assert mock_wrapper.analyze_vpc_endpoints.call_count >= 2  # Called in analyze and optimize
            assert mock_wrapper.optimize_networking_costs.call_count == 1
            assert mock_wrapper.generate_cost_heatmaps.call_count == 1


@pytest.mark.cli
class TestVPCCLIArgumentHandling:
    """Test VPC CLI argument handling and validation."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_vpc_analyze_default_parameters(self):
        """Test VPC analyze with default parameters."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {"nat_gateways": []}
            mock_wrapper.analyze_vpc_endpoints.return_value = {"vpc_endpoints": []}
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(main, ["vpc", "analyze"])

            assert result.exit_code == 0

            # Verify default parameters were used
            init_args = mock_wrapper_class.call_args
            # Profile should be None by default
            assert init_args[1].get("profile") is None
            # Region should default to us-east-1
            assert init_args[1].get("region") == "us-east-1"
            # Output format should default to rich
            assert init_args[1].get("output_format") == "rich"

    def test_vpc_analyze_custom_days_parameter(self):
        """Test VPC analyze with custom days parameter."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {"nat_gateways": []}
            mock_wrapper.analyze_vpc_endpoints.return_value = {"vpc_endpoints": []}
            mock_wrapper_class.return_value = mock_wrapper

            result = self.runner.invoke(main, ["vpc", "analyze", "--days", "60"])

            assert result.exit_code == 0

            # Verify custom days parameter was passed
            mock_wrapper.analyze_nat_gateways.assert_called_once_with(days=60)

    def test_vpc_optimize_target_reduction_bounds(self):
        """Test VPC optimize target reduction parameter bounds."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.optimize_networking_costs.return_value = {"recommendations": []}
            mock_wrapper_class.return_value = mock_wrapper

            # Test maximum valid target reduction
            result = self.runner.invoke(main, ["vpc", "optimize", "--target-reduction", "100"])

            if result.exit_code == 0:
                mock_wrapper.optimize_networking_costs.assert_called_with(target_reduction=100.0)

    def test_vpc_heatmap_account_scope_validation(self):
        """Test VPC heatmap account scope validation."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.generate_cost_heatmaps.return_value = {"heatmap_data": "test"}
            mock_wrapper_class.return_value = mock_wrapper

            # Test valid single scope
            result = self.runner.invoke(main, ["vpc", "heatmap", "--account-scope", "single"])
            assert result.exit_code == 0

            # Test valid multi scope
            result = self.runner.invoke(main, ["vpc", "heatmap", "--account-scope", "multi"])
            assert result.exit_code == 0

    def test_vpc_command_region_parameter(self):
        """Test VPC command with region parameter."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {"nat_gateways": []}
            mock_wrapper.analyze_vpc_endpoints.return_value = {"vpc_endpoints": []}
            mock_wrapper_class.return_value = mock_wrapper

            regions_to_test = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]

            for region in regions_to_test:
                result = self.runner.invoke(main, ["vpc", "analyze", "--region", region])

                assert result.exit_code == 0

                # Verify correct region was passed
                init_args = mock_wrapper_class.call_args
                assert init_args[1]["region"] == region

    def test_vpc_command_output_format_parameter(self):
        """Test VPC command with different output formats."""
        with patch("runbooks.vpc.VPCNetworkingWrapper") as mock_wrapper_class:
            mock_wrapper = Mock()
            mock_wrapper.analyze_nat_gateways.return_value = {"nat_gateways": []}
            mock_wrapper.analyze_vpc_endpoints.return_value = {"vpc_endpoints": []}
            mock_wrapper_class.return_value = mock_wrapper

            output_formats = ["rich", "json", "csv"]

            for output_format in output_formats:
                result = self.runner.invoke(main, ["vpc", "analyze", "--output-format", output_format])

                assert result.exit_code == 0

                # Verify correct output format was passed
                init_args = mock_wrapper_class.call_args
                assert init_args[1]["output_format"] == output_format

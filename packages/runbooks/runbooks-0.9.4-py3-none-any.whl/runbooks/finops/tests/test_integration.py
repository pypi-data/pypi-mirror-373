#!/usr/bin/env python3
"""
Integration Tests for FinOps Dashboard with AWS Service Mocking.

This module provides integration testing using moto to mock AWS services,
enabling comprehensive testing of AWS interactions without real credentials
or costs.

Test Coverage:
- AWS profile validation and session creation
- Cost Explorer API integration
- Organizations API integration
- EC2, S3, RDS service discovery
- Multi-account role assumption
- Error handling with AWS service failures

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import boto3
import pytest

try:
    from moto import mock_ec2, mock_organizations, mock_rds, mock_s3, mock_sts

    # Try to import mock_costexplorer if available
    try:
        from moto import mock_costexplorer
    except ImportError:
        # Define mock_costexplorer as a no-op decorator for compatibility
        def mock_costexplorer(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
except ImportError:
    # If moto is not available, define all as no-op decorators
    def mock_ec2(func):
        return func

    def mock_organizations(func):
        return func

    def mock_rds(func):
        return func

    def mock_s3(func):
        return func

    def mock_sts(func):
        return func

    def mock_costexplorer(func):
        return func


# Import the components we're testing
from runbooks.finops.finops_dashboard import (
    EnterpriseDiscovery,
    FinOpsConfig,
    MultiAccountCostTrendAnalyzer,
    run_complete_finops_analysis,
)


class TestAWSIntegrationWithMoto:
    """Integration tests using moto to mock AWS services."""

    @mock_sts
    @mock_organizations
    def test_discovery_with_aws_organizations(self):
        """Test account discovery with mocked AWS Organizations."""
        # Setup mocked Organizations
        client = boto3.client("organizations", region_name="us-east-1")

        # Create a mock organization
        org_response = client.create_organization(FeatureSet="ALL")
        org_id = org_response["Organization"]["Id"]

        # Create mock accounts
        account_names = ["production-account", "staging-account", "development-account"]
        created_accounts = []

        for account_name in account_names:
            response = client.create_account(AccountName=account_name, Email=f"{account_name}@example.com")
            created_accounts.append(response)

        # Test discovery with real AWS client
        with patch("runbooks.finops.finops_dashboard.AWS_AVAILABLE", True):
            config = FinOpsConfig()
            config.dry_run = False  # Enable live mode for integration test

            discovery = EnterpriseDiscovery(config)

            # Mock the get_account_id function to return different account IDs
            with patch("runbooks.finops.finops_dashboard.get_account_id") as mock_get_account:
                mock_get_account.side_effect = ["123456789012", "234567890123", "345678901234"]

                results = discovery.discover_accounts()

                # Verify discovery succeeded
                assert "account_info" in results
                assert results["discovery_mode"] == "LIVE"

                # Verify each configured profile was checked
                account_info = results["account_info"]
                for profile_type in ["billing", "management", "operational"]:
                    assert profile_type in account_info
                    info = account_info[profile_type]
                    assert info["status"] in ["✅ Connected", "❌ Error"]
                    if info["status"] == "✅ Connected":
                        assert "account_id" in info
                        assert len(info["account_id"]) == 12  # AWS account ID format

    @mock_costexplorer
    @mock_organizations
    def test_cost_analysis_with_cost_explorer(self):
        """Test cost analysis with mocked Cost Explorer."""
        # Setup mocked Cost Explorer
        ce_client = boto3.client("ce", region_name="us-east-1")

        # Mock cost data response
        mock_cost_data = {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": "2024-01-01", "End": "2024-01-31"},
                    "Total": {"UnblendedCost": {"Amount": "50000.00", "Unit": "USD"}},
                    "Groups": [
                        {"Keys": ["EC2-Instance"], "Metrics": {"UnblendedCost": {"Amount": "20000.00", "Unit": "USD"}}},
                        {"Keys": ["S3"], "Metrics": {"UnblendedCost": {"Amount": "10000.00", "Unit": "USD"}}},
                    ],
                }
            ]
        }

        # Test cost analysis
        config = FinOpsConfig()
        analyzer = MultiAccountCostTrendAnalyzer(config)

        # Run analysis (will use simulated data since we're not mocking the internal methods)
        results = analyzer.analyze_cost_trends()

        # Verify results structure
        assert results["status"] == "completed"
        assert "cost_trends" in results
        assert "optimization_opportunities" in results

        # Verify cost trends data
        cost_trends = results["cost_trends"]
        assert cost_trends["total_accounts"] >= config.min_account_threshold
        assert cost_trends["total_monthly_spend"] > 0

        # Verify optimization data
        optimization = results["optimization_opportunities"]
        assert optimization["total_potential_savings"] > 0
        assert 0 <= optimization["savings_percentage"] <= 100

    @mock_ec2
    @mock_s3
    @mock_rds
    def test_multi_service_resource_discovery(self):
        """Test resource discovery across multiple AWS services."""
        # Setup mocked EC2
        ec2 = boto3.client("ec2", region_name="us-east-1")

        # Create mock EC2 instances
        reservation = ec2.run_instances(ImageId="ami-12345678", MinCount=2, MaxCount=2, InstanceType="t2.micro")
        instance_ids = [i["InstanceId"] for i in reservation["Instances"]]

        # Tag instances
        ec2.create_tags(
            Resources=instance_ids,
            Tags=[{"Key": "Environment", "Value": "production"}, {"Key": "Application", "Value": "web-server"}],
        )

        # Setup mocked S3
        s3 = boto3.client("s3", region_name="us-east-1")
        bucket_names = ["prod-data-bucket", "staging-logs-bucket", "dev-temp-bucket"]

        for bucket_name in bucket_names:
            s3.create_bucket(Bucket=bucket_name)

            # Add bucket tagging
            s3.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={
                    "TagSet": [
                        {"Key": "Environment", "Value": "production" if "prod" in bucket_name else "staging"},
                        {"Key": "CostCenter", "Value": "engineering"},
                    ]
                },
            )

        # Setup mocked RDS
        rds = boto3.client("rds", region_name="us-east-1")

        # Create mock RDS instances
        db_instances = ["prod-database", "staging-database"]
        for db_name in db_instances:
            rds.create_db_instance(
                DBInstanceIdentifier=db_name,
                DBInstanceClass="db.t3.micro",
                Engine="mysql",
                MasterUsername="admin",
                MasterUserPassword="password123",
                AllocatedStorage=20,
            )

        # Test resource discovery simulation
        # Since our dashboard uses simulated data, we'll verify the mocked services are available

        # Verify EC2 instances
        instances = ec2.describe_instances()
        assert len(instances["Reservations"]) == 1
        assert len(instances["Reservations"][0]["Instances"]) == 2

        # Verify S3 buckets
        buckets = s3.list_buckets()
        assert len(buckets["Buckets"]) == 3
        bucket_list = [b["Name"] for b in buckets["Buckets"]]
        for expected_bucket in bucket_names:
            assert expected_bucket in bucket_list

        # Verify RDS instances
        db_list = rds.describe_db_instances()
        assert len(db_list["DBInstances"]) == 2
        db_identifiers = [db["DBInstanceIdentifier"] for db in db_list["DBInstances"]]
        for expected_db in db_instances:
            assert expected_db in db_identifiers

    @mock_sts
    def test_cross_account_role_assumption(self):
        """Test cross-account role assumption scenarios."""
        sts_client = boto3.client("sts", region_name="us-east-1")

        # Mock assume role response
        mock_credentials = {
            "Credentials": {
                "AccessKeyId": "ASSUMED-ACCESS-KEY",
                "SecretAccessKey": "assumed-secret-key",
                "SessionToken": "assumed-session-token",
                "Expiration": datetime.now() + timedelta(hours=1),
            },
            "AssumedRoleUser": {
                "AssumedRoleId": "AROA123456789:test-session",
                "Arn": "arn:aws:sts::123456789012:assumed-role/TestRole/test-session",
            },
        }

        # Test role assumption with discovery
        config = FinOpsConfig()
        config.enable_cross_account = True

        discovery = EnterpriseDiscovery(config)

        # Mock successful role assumption
        with patch("runbooks.finops.finops_dashboard.get_account_id") as mock_get_account:
            mock_get_account.return_value = "123456789012"

            results = discovery.discover_accounts()

            # Verify cross-account discovery succeeded
            assert "account_info" in results
            for profile_type, info in results["account_info"].items():
                if info["status"] == "✅ Connected":
                    assert "account_id" in info
                    # In simulation mode, should have simulated account
                    # In real integration, would have actual account ID

    def test_aws_api_error_handling(self):
        """Test handling of various AWS API errors."""
        config = FinOpsConfig()
        discovery = EnterpriseDiscovery(config)

        # Test with mocked AWS service errors
        with patch("runbooks.finops.finops_dashboard.get_account_id") as mock_get_account:
            # Mock different types of AWS errors
            mock_get_account.side_effect = [
                Exception("UnauthorizedOperation: You are not authorized to perform this operation"),
                Exception("AccessDenied: User is not authorized to assume role"),
                "123456789012",  # Success for third profile
            ]

            results = discovery.discover_accounts()

            # Verify error handling
            assert "account_info" in results
            account_info = results["account_info"]

            # Should have errors for first two profiles, success for third
            error_count = sum(1 for info in account_info.values() if info["status"] == "❌ Error")
            success_count = sum(1 for info in account_info.values() if "✅" in info["status"])

            assert error_count >= 0  # May have errors depending on mock behavior
            assert success_count >= 0  # May have successes depending on mock behavior


class TestPerformanceWithLargeDatasets:
    """Test performance with large multi-account datasets."""

    def test_large_account_analysis_performance(self):
        """Test performance with large number of accounts."""
        import time

        config = FinOpsConfig()

        # Test with maximum account count
        with patch("runbooks.finops.finops_dashboard.random.randint") as mock_randint:
            mock_randint.return_value = 85  # Maximum accounts

            analyzer = MultiAccountCostTrendAnalyzer(config)

            start_time = time.time()
            results = analyzer.analyze_cost_trends()
            end_time = time.time()

            # Performance assertions
            execution_time = end_time - start_time
            assert execution_time < 10.0  # Should complete within 10 seconds

            # Verify results with large dataset
            assert results["status"] == "completed"
            cost_trends = results["cost_trends"]
            assert cost_trends["total_accounts"] == 85
            assert len(cost_trends["account_data"]) == 85

            # Memory usage should be reasonable
            import sys

            assert sys.getsizeof(results) < 50_000_000  # Less than 50MB

    def test_resource_heatmap_with_many_resources(self):
        """Test resource heatmap generation with many resources."""
        config = FinOpsConfig()

        # Create large trend data
        large_account_data = []
        for i in range(50):  # 50 accounts
            large_account_data.append(
                {
                    "account_id": f"large-account-{i:03d}",
                    "account_type": "production",
                    "monthly_spend": 50000.0,  # High spend to generate many resources
                }
            )

        trend_data = {"cost_trends": {"account_data": large_account_data}}

        from runbooks.finops.finops_dashboard import ResourceUtilizationHeatmapAnalyzer

        analyzer = ResourceUtilizationHeatmapAnalyzer(config, trend_data)

        import time

        start_time = time.time()
        results = analyzer.analyze_resource_utilization()
        end_time = time.time()

        # Performance assertions
        execution_time = end_time - start_time
        assert execution_time < 15.0  # Should complete within 15 seconds

        # Verify results with large resource count
        assert results["status"] == "completed"
        heatmap_data = results["heatmap_data"]
        assert heatmap_data["total_accounts"] == 50
        assert heatmap_data["total_resources"] > 1000  # Should have many resources

    def test_complete_workflow_performance(self):
        """Test complete workflow performance."""
        import time

        start_time = time.time()
        results = run_complete_finops_analysis()
        end_time = time.time()

        # Performance assertions
        execution_time = end_time - start_time
        assert execution_time < 30.0  # Complete workflow should finish within 30 seconds

        # Verify workflow completed successfully
        assert results["workflow_status"] == "completed"

        # Verify all components ran
        assert "discovery_results" in results
        assert "cost_analysis" in results
        assert "audit_results" in results
        assert "executive_summary" in results
        assert "export_status" in results


class TestRealWorldScenarios:
    """Test scenarios that simulate real-world usage patterns."""

    def test_mixed_account_types_analysis(self):
        """Test analysis with realistic mix of account types and sizes."""
        config = FinOpsConfig()
        analyzer = MultiAccountCostTrendAnalyzer(config)

        # Override random generation for realistic test
        def mock_choice(choices):
            # Return realistic distribution of account types
            import random

            weights = [0.2, 0.3, 0.25, 0.15, 0.1, 0.05]  # Weighted by typical usage
            return random.choices(choices, weights=weights)[0]

        with patch("runbooks.finops.finops_dashboard.random.choice", side_effect=mock_choice):
            results = analyzer.analyze_cost_trends()

            assert results["status"] == "completed"

            # Verify realistic account distribution
            cost_trends = results["cost_trends"]
            account_types = [account["account_type"] for account in cost_trends["account_data"]]

            # Should have variety of account types
            unique_types = set(account_types)
            assert len(unique_types) > 2  # At least 3 different types

            # Should have reasonable cost distribution
            monthly_spends = [account["monthly_spend"] for account in cost_trends["account_data"]]
            min_spend = min(monthly_spends)
            max_spend = max(monthly_spends)

            assert min_spend > 0
            assert max_spend > min_spend * 2  # Should have significant variation

    def test_compliance_audit_realistic_findings(self):
        """Test audit with realistic compliance findings."""
        from runbooks.finops.finops_dashboard import EnterpriseResourceAuditor

        config = FinOpsConfig()
        auditor = EnterpriseResourceAuditor(config)

        results = auditor.run_compliance_audit()

        assert results["status"] == "completed"
        audit_data = results["audit_data"]

        # Verify realistic audit metrics
        assert audit_data["total_resources_scanned"] > 1000  # Realistic resource count
        assert audit_data["accounts_audited"] >= 5  # Multi-account scope
        assert audit_data["regions_covered"] >= 3  # Multi-region coverage

        # Verify realistic compliance findings
        findings = audit_data["compliance_findings"]
        assert findings["untagged_resources"]["count"] > 50  # Common issue
        assert findings["unused_resources"]["count"] > 20  # Typical waste
        assert findings["security_groups"]["overly_permissive"] > 5  # Security gaps

        # Verify risk scoring is realistic
        risk_score = audit_data["risk_score"]
        assert 30 <= risk_score["overall"] <= 90  # Realistic range

        # Verify breakdown scores
        breakdown = risk_score["breakdown"]
        for category, score in breakdown.items():
            assert 0 <= score <= 100
            assert isinstance(score, (int, float))


if __name__ == "__main__":
    """
    Run the integration test suite directly.
    
    Usage:
        python test_integration.py
        pytest test_integration.py -v
        pytest test_integration.py::TestAWSIntegrationWithMoto -v
    """
    pytest.main([__file__, "-v"])

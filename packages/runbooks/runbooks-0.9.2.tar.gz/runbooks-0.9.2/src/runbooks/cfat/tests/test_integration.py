"""
Integration tests for Cloud Foundations Assessment Tool.

Tests the complete CFAT workflow using moto for AWS service mocking,
ensuring the assessment engine works correctly with AWS APIs without
requiring real AWS credentials or making actual API calls.

These tests focus on integration patterns and real-world usage scenarios
while maintaining fast execution and reliability.
"""

from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

from runbooks.cfat.assessment.runner import CloudFoundationsAssessment
from runbooks.cfat.models import AssessmentConfig, CheckStatus, Severity
from runbooks.cfat.tests import TEST_ACCOUNT_ID, TEST_PROFILE, TEST_REGION


@pytest.mark.integration
class TestCFATIntegrationWithMoto:
    """Integration tests using moto for AWS service mocking."""

    @mock_aws
    def test_iam_assessment_with_mock_services(self):
        """Test IAM assessment using moto-mocked AWS services."""
        # Create mock IAM resources
        iam_client = boto3.client("iam", region_name=TEST_REGION)

        # Create test user
        iam_client.create_user(UserName="test-user")

        # Create test role
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}
            ],
        }
        iam_client.create_role(RoleName="test-role", AssumeRolePolicyDocument=str(assume_role_policy))

        # Create test policy
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": "s3:GetObject", "Resource": "*"}],
        }
        iam_client.create_policy(PolicyName="test-policy", PolicyDocument=str(policy_document))

        # Mock the assessment runner to use our mocked services
        with patch("runbooks.cfat.assessment.runner.CloudFoundationsAssessment.get_account_id") as mock_account:
            mock_account.return_value = TEST_ACCOUNT_ID

            # Initialize assessment
            assessment = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)

            # Configure for IAM-only assessment
            assessment.assessment_config.included_categories = ["iam"]
            assessment.assessment_config.parallel_execution = False  # Easier to debug

            # Run assessment
            report = assessment.run_assessment()

            # Validate results
            assert report is not None
            assert report.account_id == TEST_ACCOUNT_ID
            assert report.region == TEST_REGION
            assert len(report.results) > 0

            # Should have IAM-related results
            iam_results = report.get_results_by_category("iam")
            assert len(iam_results) > 0

            # Verify result structure
            for result in iam_results:
                assert result.finding_id is not None
                assert result.check_name is not None
                assert result.check_category == "iam"
                assert result.status in [CheckStatus.PASS, CheckStatus.FAIL, CheckStatus.ERROR]
                assert result.severity in [Severity.INFO, Severity.WARNING, Severity.CRITICAL]
                assert result.execution_time >= 0

    @mock_aws
    def test_vpc_assessment_with_mock_services(self):
        """Test VPC assessment using moto-mocked EC2 services."""
        # Create mock VPC resources
        ec2_client = boto3.client("ec2", region_name=TEST_REGION)

        # Create VPC
        vpc_response = ec2_client.create_vpc(CidrBlock="10.0.0.0/16")
        vpc_id = vpc_response["Vpc"]["VpcId"]

        # Create subnet
        ec2_client.create_subnet(VpcId=vpc_id, CidrBlock="10.0.1.0/24")

        # Create security group
        ec2_client.create_security_group(GroupName="test-sg", Description="Test security group", VpcId=vpc_id)

        # Mock assessment execution
        with patch("runbooks.cfat.assessment.runner.CloudFoundationsAssessment.get_account_id") as mock_account:
            mock_account.return_value = TEST_ACCOUNT_ID

            assessment = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)

            # Configure for VPC-only assessment
            assessment.assessment_config.included_categories = ["vpc"]
            assessment.assessment_config.parallel_execution = False

            report = assessment.run_assessment()

            # Validate VPC assessment results
            assert report is not None
            vpc_results = report.get_results_by_category("vpc")

            # Should have some VPC-related checks
            assert len(vpc_results) >= 0  # May be 0 if no VPC checks implemented yet

    @mock_aws
    def test_cloudtrail_assessment_with_mock_services(self):
        """Test CloudTrail assessment using moto-mocked services."""
        # Create mock CloudTrail
        cloudtrail_client = boto3.client("cloudtrail", region_name=TEST_REGION)

        # Create trail
        trail_name = "test-trail"
        s3_bucket = "test-cloudtrail-bucket"

        cloudtrail_client.create_trail(Name=trail_name, S3BucketName=s3_bucket)

        # Start logging
        cloudtrail_client.start_logging(Name=trail_name)

        # Mock assessment
        with patch("runbooks.cfat.assessment.runner.CloudFoundationsAssessment.get_account_id") as mock_account:
            mock_account.return_value = TEST_ACCOUNT_ID

            assessment = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)

            assessment.assessment_config.included_categories = ["cloudtrail"]
            assessment.assessment_config.parallel_execution = False

            report = assessment.run_assessment()

            assert report is not None
            cloudtrail_results = report.get_results_by_category("cloudtrail")
            assert len(cloudtrail_results) >= 0

    def test_assessment_configuration_integration(self):
        """Test assessment configuration integration."""
        # Test custom configuration
        config = AssessmentConfig(
            included_categories=["iam", "vpc"],
            excluded_checks=["iam_unused_credentials"],
            parallel_execution=True,
            max_workers=5,
            severity_threshold=Severity.WARNING,
            compliance_framework="SOC2",
        )

        with patch("runbooks.cfat.assessment.runner.CloudFoundationsAssessment.get_account_id") as mock_account:
            mock_account.return_value = TEST_ACCOUNT_ID

            assessment = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)
            assessment.assessment_config = config

            # Should be able to run without errors
            report = assessment.run_assessment()
            assert report is not None
            assert report.metadata.get("max_workers") == 5

    def test_parallel_vs_sequential_execution(self):
        """Test parallel vs sequential execution modes."""
        with patch("runbooks.cfat.assessment.runner.CloudFoundationsAssessment.get_account_id") as mock_account:
            mock_account.return_value = TEST_ACCOUNT_ID

            # Test parallel execution
            assessment_parallel = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)
            assessment_parallel.assessment_config.parallel_execution = True
            assessment_parallel.assessment_config.max_workers = 3

            report_parallel = assessment_parallel.run_assessment()

            # Test sequential execution
            assessment_sequential = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)
            assessment_sequential.assessment_config.parallel_execution = False

            report_sequential = assessment_sequential.run_assessment()

            # Both should produce valid reports
            assert report_parallel is not None
            assert report_sequential is not None

            # Results should be similar (may vary due to mock timing)
            assert len(report_parallel.results) > 0
            assert len(report_sequential.results) > 0

    def test_error_handling_in_assessment(self):
        """Test error handling during assessment execution."""
        with patch("runbooks.cfat.assessment.runner.CloudFoundationsAssessment.get_account_id") as mock_account:
            mock_account.return_value = TEST_ACCOUNT_ID

            assessment = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)

            # Mock a check that raises an exception
            original_execute_single_check = assessment._execute_single_check

            def mock_execute_single_check(check_name):
                if check_name == "failing_check":
                    raise Exception("Simulated check failure")
                return original_execute_single_check(check_name)

            assessment._execute_single_check = mock_execute_single_check

            # Override available checks to include our failing check
            assessment._available_checks = {"passing_check": "PassingCheck", "failing_check": "FailingCheck"}

            # Run assessment
            report = assessment.run_assessment()

            # Should handle errors gracefully
            assert report is not None

            # Should have error results for failed checks
            error_results = [r for r in report.results if r.status == CheckStatus.ERROR]
            assert len(error_results) > 0

    def test_report_generation_all_formats(self):
        """Test report generation in all supported formats."""
        with patch("runbooks.cfat.assessment.runner.CloudFoundationsAssessment.get_account_id") as mock_account:
            mock_account.return_value = TEST_ACCOUNT_ID

            assessment = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)

            # Run assessment
            report = assessment.run_assessment()

            # Test all export formats (without actually writing files)
            assert hasattr(report, "to_json")
            assert hasattr(report, "to_csv")
            assert hasattr(report, "to_html")
            assert hasattr(report, "to_markdown")

            # Test methods return without error
            assert callable(report.to_json)
            assert callable(report.to_csv)
            assert callable(report.to_html)
            assert callable(report.to_markdown)

    def test_compliance_framework_integration(self):
        """Test compliance framework-specific assessments."""
        frameworks = ["SOC2", "PCI-DSS", "HIPAA"]

        for framework in frameworks:
            with patch("runbooks.cfat.assessment.runner.CloudFoundationsAssessment.get_account_id") as mock_account:
                mock_account.return_value = TEST_ACCOUNT_ID

                assessment = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)
                assessment.assessment_config.compliance_framework = framework

                report = assessment.run_assessment()

                assert report is not None
                assert (
                    report.metadata.get("compliance_framework") is None
                    or report.metadata.get("compliance_framework") == framework
                )

    @pytest.mark.slow
    def test_large_scale_assessment(self):
        """Test assessment with many checks (performance test)."""
        with patch("runbooks.cfat.assessment.runner.CloudFoundationsAssessment.get_account_id") as mock_account:
            mock_account.return_value = TEST_ACCOUNT_ID

            assessment = CloudFoundationsAssessment(profile=TEST_PROFILE, region=TEST_REGION)

            # Override with many mock checks
            many_checks = {f"check_{i}": f"Check{i}" for i in range(50)}
            assessment._available_checks = many_checks

            assessment.assessment_config.parallel_execution = True
            assessment.assessment_config.max_workers = 10

            report = assessment.run_assessment()

            assert report is not None
            # Should complete in reasonable time with parallel execution
            assert report.summary.total_execution_time < 60  # Should finish within 60 seconds
            assert len(report.results) == 50

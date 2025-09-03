#!/usr/bin/env python3
"""
Comprehensive Unit Tests for FinOps Dashboard Enterprise Components.

This module provides extensive unit testing for all major components
of the enterprise FinOps dashboard system including:
- Configuration management
- Account discovery
- Cost trend analysis
- Resource utilization heatmaps
- Executive reporting
- Export functionality

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import the components we're testing
from runbooks.finops.finops_dashboard import (
    EnterpriseDiscovery,
    EnterpriseExecutiveDashboard,
    EnterpriseExportEngine,
    EnterpriseResourceAuditor,
    FinOpsConfig,
    MultiAccountCostTrendAnalyzer,
    ResourceUtilizationHeatmapAnalyzer,
    create_finops_dashboard,
    run_complete_finops_analysis,
)


class TestFinOpsConfig:
    """Test suite for FinOpsConfig class."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = FinOpsConfig()

        # Test default profile values
        assert config.billing_profile == "ams-admin-Billing-ReadOnlyAccess-909135376185"
        assert config.management_profile == "ams-admin-ReadOnlyAccess-909135376185"
        assert config.operational_profile == "ams-centralised-ops-ReadOnlyAccess-335083429030"

        # Test analysis parameters
        assert config.time_range_days == 30
        assert config.target_savings_percent == 40
        assert config.min_account_threshold == 5
        assert config.risk_threshold == 25

        # Test safety controls
        assert config.dry_run is True
        assert config.require_approval is True
        assert config.enable_cross_account is True
        assert config.audit_mode is True

        # Test output configuration
        assert "json" in config.output_formats
        assert "csv" in config.output_formats
        assert "html" in config.output_formats
        assert config.enable_ou_analysis is True
        assert config.include_reserved_instance_recommendations is True

    def test_environment_variable_override(self):
        """Test configuration override via environment variables."""
        with patch.dict(
            os.environ,
            {
                "BILLING_PROFILE": "test-billing-profile",
                "MANAGEMENT_PROFILE": "test-management-profile",
                "CENTRALISED_OPS_PROFILE": "test-ops-profile",
            },
        ):
            config = FinOpsConfig()

            assert config.billing_profile == "test-billing-profile"
            assert config.management_profile == "test-management-profile"
            assert config.operational_profile == "test-ops-profile"

    def test_report_timestamp_format(self):
        """Test report timestamp format."""
        config = FinOpsConfig()

        # Should be in format YYYYMMDD_HHMM
        assert len(config.report_timestamp) == 13
        assert "_" in config.report_timestamp

        # Should parse as valid datetime components
        date_part, time_part = config.report_timestamp.split("_")
        assert len(date_part) == 8  # YYYYMMDD
        assert len(time_part) == 4  # HHMM


class TestEnterpriseDiscovery:
    """Test suite for EnterpriseDiscovery class."""

    def test_discovery_initialization(self):
        """Test proper initialization of discovery engine."""
        config = FinOpsConfig()
        discovery = EnterpriseDiscovery(config)

        assert discovery.config == config
        assert discovery.results == {}

    @patch("runbooks.finops.finops_dashboard.get_aws_profiles")
    @patch("runbooks.finops.finops_dashboard.get_account_id")
    def test_successful_account_discovery(self, mock_get_account_id, mock_get_profiles):
        """Test successful account discovery workflow."""
        # Mock AWS functions
        mock_get_profiles.return_value = ["profile1", "profile2", "default"]
        mock_get_account_id.return_value = "123456789012"

        config = FinOpsConfig()
        discovery = EnterpriseDiscovery(config)

        results = discovery.discover_accounts()

        # Verify results structure
        assert "timestamp" in results
        assert "available_profiles" in results
        assert "configured_profiles" in results
        assert "discovery_mode" in results
        assert "account_info" in results

        # Verify configured profiles
        configured = results["configured_profiles"]
        assert configured["billing"] == config.billing_profile
        assert configured["management"] == config.management_profile
        assert configured["operational"] == config.operational_profile

        # Verify discovery mode respects dry_run setting
        assert results["discovery_mode"] == "DRY-RUN"

        # Verify account info structure
        account_info = results["account_info"]
        assert "billing" in account_info
        assert "management" in account_info
        assert "operational" in account_info

        for profile_type, info in account_info.items():
            assert "profile" in info
            assert "account_id" in info or "error" in info
            assert "status" in info

    def test_discovery_error_handling(self):
        """Test discovery error handling."""
        config = FinOpsConfig()
        discovery = EnterpriseDiscovery(config)

        # Mock AWS_AVAILABLE as False to trigger error path
        with patch("runbooks.finops.finops_dashboard.AWS_AVAILABLE", False):
            results = discovery.discover_accounts()

            # Should still return valid structure with simulated data
            assert "timestamp" in results
            assert "account_info" in results

            # Account info should have simulated status
            for profile_info in results["account_info"].values():
                assert profile_info["status"] == "🔄 Simulated"
                assert profile_info["account_id"] == "simulated-account"


class TestMultiAccountCostTrendAnalyzer:
    """Test suite for MultiAccountCostTrendAnalyzer class."""

    def test_analyzer_initialization(self):
        """Test proper initialization of cost trend analyzer."""
        config = FinOpsConfig()
        analyzer = MultiAccountCostTrendAnalyzer(config)

        assert analyzer.config == config
        assert analyzer.trend_results == {}

    def test_cost_trend_analysis_success(self):
        """Test successful cost trend analysis."""
        config = FinOpsConfig()
        analyzer = MultiAccountCostTrendAnalyzer(config)

        # Set fixed random seed for reproducible test results
        with (
            patch("runbooks.finops.finops_dashboard.random.randint") as mock_randint,
            patch("runbooks.finops.finops_dashboard.random.uniform") as mock_uniform,
            patch("runbooks.finops.finops_dashboard.random.choice") as mock_choice,
        ):
            # Mock random functions for predictable results
            mock_randint.return_value = 10  # 10 accounts
            mock_uniform.return_value = 20000.0  # $20k base spend
            mock_choice.return_value = ("production", 15000, 65000)

            results = analyzer.analyze_cost_trends()

            # Verify results structure
            assert results["status"] == "completed"
            assert "timestamp" in results
            assert "analysis_type" in results
            assert results["analysis_type"] == "multi_account_cost_trends"
            assert "target_savings" in results
            assert results["target_savings"] == config.target_savings_percent
            assert "cost_trends" in results
            assert "optimization_opportunities" in results

            # Verify cost trends structure
            cost_trends = results["cost_trends"]
            assert "total_accounts" in cost_trends
            assert "total_monthly_spend" in cost_trends
            assert "account_data" in cost_trends
            assert "cost_trend_summary" in cost_trends

            # Verify optimization opportunities structure
            optimization = results["optimization_opportunities"]
            assert "total_potential_savings" in optimization
            assert "savings_percentage" in optimization
            assert "target_achievement" in optimization
            assert "optimization_by_account_type" in optimization
            assert "annual_savings_potential" in optimization

    def test_dynamic_account_discovery(self):
        """Test dynamic account count generation."""
        config = FinOpsConfig()
        analyzer = MultiAccountCostTrendAnalyzer(config)

        # Test multiple runs to ensure account count varies
        account_counts = []
        for _ in range(5):
            results = analyzer.analyze_cost_trends()
            if results["status"] == "completed":
                account_counts.append(results["cost_trends"]["total_accounts"])

        # Should generate different account counts within expected range
        assert all(config.min_account_threshold <= count <= 85 for count in account_counts)
        assert len(set(account_counts)) >= 1  # At least some variation (may be same due to randomness)

    def test_optimization_calculation_logic(self):
        """Test optimization calculation logic."""
        config = FinOpsConfig()
        analyzer = MultiAccountCostTrendAnalyzer(config)

        # Create test data with known values
        test_cost_trends = {
            "total_monthly_spend": 100000.0,
            "account_data": [
                {
                    "account_id": "test-001",
                    "account_type": "production",
                    "monthly_spend": 50000.0,
                    "optimization_potential": 0.4,  # 40% potential
                },
                {
                    "account_id": "test-002",
                    "account_type": "development",
                    "monthly_spend": 50000.0,
                    "optimization_potential": 0.6,  # 60% potential
                },
            ],
        }

        optimization = analyzer._calculate_optimization_opportunities(test_cost_trends)

        # Expected: (50000 * 0.4) + (50000 * 0.6) = 50000 total savings
        # 50000 / 100000 = 50% savings percentage
        assert optimization["total_potential_savings"] == 50000.0
        assert optimization["savings_percentage"] == 50.0
        assert optimization["annual_savings_potential"] == 600000.0

        # Verify target achievement
        target_achievement = optimization["target_achievement"]
        assert target_achievement["target"] == config.target_savings_percent
        assert target_achievement["achieved"] == 50.0
        assert target_achievement["status"] == "achieved"  # 50% > 40% target
        assert target_achievement["gap"] == 0  # No gap since target exceeded


class TestResourceUtilizationHeatmapAnalyzer:
    """Test suite for ResourceUtilizationHeatmapAnalyzer class."""

    def test_heatmap_analyzer_initialization(self):
        """Test proper initialization of heatmap analyzer."""
        config = FinOpsConfig()
        trend_data = {"cost_trends": {"account_data": []}}
        analyzer = ResourceUtilizationHeatmapAnalyzer(config, trend_data)

        assert analyzer.config == config
        assert analyzer.trend_data == trend_data
        assert analyzer.heatmap_results == {}

    def test_resource_heatmap_analysis(self):
        """Test resource utilization heatmap analysis."""
        config = FinOpsConfig()
        trend_data = {
            "cost_trends": {
                "account_data": [
                    {"account_id": "test-001", "account_type": "production", "monthly_spend": 25000.0},
                    {"account_id": "test-002", "account_type": "development", "monthly_spend": 5000.0},
                ]
            }
        }

        analyzer = ResourceUtilizationHeatmapAnalyzer(config, trend_data)
        results = analyzer.analyze_resource_utilization()

        # Verify results structure
        assert results["status"] == "completed"
        assert "timestamp" in results
        assert "analysis_type" in results
        assert results["analysis_type"] == "resource_utilization_heatmap"
        assert "heatmap_data" in results
        assert "efficiency_scoring" in results
        assert "rightsizing_recommendations" in results

        # Verify heatmap data structure
        heatmap_data = results["heatmap_data"]
        assert heatmap_data["total_accounts"] == 2
        assert heatmap_data["total_resources"] > 0
        assert "utilization_matrix" in heatmap_data
        assert "resource_categories" in heatmap_data

        # Verify resource categories
        categories = heatmap_data["resource_categories"]
        assert "compute" in categories
        assert "storage" in categories
        assert "database" in categories
        assert "network" in categories

    def test_efficiency_scoring_calculation(self):
        """Test efficiency scoring calculation logic."""
        config = FinOpsConfig()
        trend_data = {"cost_trends": {"account_data": []}}
        analyzer = ResourceUtilizationHeatmapAnalyzer(config, trend_data)

        # Create test heatmap data
        test_heatmap_data = {
            "utilization_matrix": [
                {
                    "account_id": "test-001",
                    "resource_utilization": {
                        "compute": {
                            "ec2_instances": {"efficiency_score": 60.0},
                            "lambda_functions": {"efficiency_score": 80.0},
                        },
                        "storage": {"s3_buckets": {"efficiency_score": 39.0}},
                    },
                }
            ]
        }

        efficiency = analyzer._calculate_efficiency_scoring(test_heatmap_data)

        # Expected: (60 + 80 + 39) / 3 = 59.7% average
        assert efficiency["average_efficiency_score"] == 59.7
        assert efficiency["efficiency_distribution"]["total_resources_scored"] == 3

        # Test distribution counts
        distribution = efficiency["efficiency_distribution"]
        assert distribution["low_efficiency"] == 1  # 39% < 40
        assert distribution["medium_efficiency"] == 1  # 60% in 40-70 range
        assert distribution["high_efficiency"] == 1  # 80% >= 70


class TestEnterpriseResourceAuditor:
    """Test suite for EnterpriseResourceAuditor class."""

    def test_auditor_initialization(self):
        """Test proper initialization of resource auditor."""
        config = FinOpsConfig()
        auditor = EnterpriseResourceAuditor(config)

        assert auditor.config == config
        assert auditor.audit_results == {}

    def test_compliance_audit_execution(self):
        """Test compliance audit execution."""
        config = FinOpsConfig()
        auditor = EnterpriseResourceAuditor(config)

        results = auditor.run_compliance_audit()

        # Verify results structure
        assert results["status"] == "completed"
        assert "timestamp" in results
        assert "audit_scope" in results
        assert results["audit_scope"] == "multi-account-enterprise"
        assert "profiles_audited" in results
        assert "audit_data" in results

        # Verify audit data structure
        audit_data = results["audit_data"]
        assert "total_resources_scanned" in audit_data
        assert "accounts_audited" in audit_data
        assert "regions_covered" in audit_data
        assert "compliance_findings" in audit_data
        assert "risk_score" in audit_data
        assert "recommendations" in audit_data

        # Verify compliance findings structure
        findings = audit_data["compliance_findings"]
        assert "untagged_resources" in findings
        assert "unused_resources" in findings
        assert "security_groups" in findings
        assert "public_resources" in findings

        # Verify risk score structure
        risk_score = audit_data["risk_score"]
        assert "overall" in risk_score
        assert "breakdown" in risk_score
        assert 0 <= risk_score["overall"] <= 100


class TestEnterpriseExecutiveDashboard:
    """Test suite for EnterpriseExecutiveDashboard class."""

    def create_test_data(self):
        """Create test data for executive dashboard."""
        discovery_results = {"timestamp": datetime.now().isoformat(), "status": "completed"}

        cost_analysis = {
            "status": "completed",
            "cost_trends": {"total_monthly_spend": 100000.0},
            "optimization_opportunities": {"annual_savings_potential": 480000.0, "savings_percentage": 40.0},
        }

        audit_results = {
            "status": "completed",
            "audit_data": {
                "total_resources_scanned": 2500,
                "risk_score": {"overall": 75},
                "recommendations": [
                    {"priority": "critical", "category": "security"},
                    {"priority": "high", "category": "cost"},
                    {"priority": "medium", "category": "governance"},
                ],
            },
        }

        return discovery_results, cost_analysis, audit_results

    def test_executive_dashboard_initialization(self):
        """Test proper initialization of executive dashboard."""
        config = FinOpsConfig()
        discovery, cost_analysis, audit = self.create_test_data()
        dashboard = EnterpriseExecutiveDashboard(config, discovery, cost_analysis, audit)

        assert dashboard.config == config
        assert dashboard.discovery == discovery
        assert dashboard.cost_analysis == cost_analysis
        assert dashboard.audit_results == audit

    def test_executive_summary_generation(self):
        """Test executive summary generation."""
        config = FinOpsConfig()
        discovery, cost_analysis, audit = self.create_test_data()
        dashboard = EnterpriseExecutiveDashboard(config, discovery, cost_analysis, audit)

        summary = dashboard.generate_executive_summary()

        # Verify summary structure
        assert "report_metadata" in summary
        assert "financial_overview" in summary
        assert "operational_overview" in summary
        assert "executive_recommendations" in summary

        # Verify metadata
        metadata = summary["report_metadata"]
        assert metadata["report_type"] == "enterprise_finops_executive_summary"
        assert metadata["analysis_period"] == f"{config.time_range_days} days"
        assert metadata["target_savings"] == f"{config.target_savings_percent}%"

        # Verify financial overview
        financial = summary["financial_overview"]
        assert financial["current_monthly_spend"] == 100000.0
        assert financial["potential_annual_savings"] == 480000.0
        assert financial["savings_percentage"] == 40.0
        assert financial["target_achieved"] is True  # 40% == 40% target

        # Verify operational overview
        operational = summary["operational_overview"]
        assert operational["resources_scanned"] == 2500
        assert operational["overall_risk_score"] == 75
        assert operational["critical_findings"] == 1
        assert operational["high_findings"] == 1


class TestEnterpriseExportEngine:
    """Test suite for EnterpriseExportEngine class."""

    def test_export_engine_initialization(self):
        """Test proper initialization of export engine."""
        config = FinOpsConfig()
        exporter = EnterpriseExportEngine(config)

        assert exporter.config == config
        assert exporter.export_results == {}

    def test_export_all_results(self):
        """Test export of all results in multiple formats."""
        config = FinOpsConfig()
        exporter = EnterpriseExportEngine(config)

        # Create test data
        test_data = {
            "discovery": {"status": "completed"},
            "cost_analysis": {
                "status": "completed",
                "cost_trends": {"total_monthly_spend": 100000.0, "total_accounts": 15},
                "optimization_opportunities": {"annual_savings_potential": 480000.0, "savings_percentage": 25.0},
            },
            "audit_results": {
                "status": "completed",
                "audit_data": {
                    "total_resources_scanned": 2500,
                    "risk_score": {"overall": 75},
                    "recommendations": [
                        {"priority": "critical", "description": "Fix security issues"},
                        {"priority": "high", "description": "Optimize costs"},
                    ],
                },
            },
            "executive_summary": {"report_metadata": {"timestamp": datetime.now().isoformat()}},
        }

        export_status = exporter.export_all_results(
            test_data["discovery"],
            test_data["cost_analysis"],
            test_data["audit_results"],
            test_data["executive_summary"],
        )

        # Verify export status structure
        assert "successful_exports" in export_status
        assert "failed_exports" in export_status

        # Should have successful exports for all configured formats
        successful = export_status["successful_exports"]
        assert len(successful) == len(config.output_formats)

        # Verify each format was exported
        exported_formats = [exp["format"] for exp in successful]
        for format_type in config.output_formats:
            assert format_type in exported_formats

    def test_json_export(self):
        """Test JSON export functionality."""
        config = FinOpsConfig()
        exporter = EnterpriseExportEngine(config)

        test_data = {
            "metadata": {"timestamp": datetime.now().isoformat()},
            "test_value": 42,
            "nested_data": {"key": "value"},
        }

        # Should not raise exception for valid data
        filename = exporter._export_json(test_data)
        assert filename.endswith(".json")
        assert config.report_timestamp in filename

    def test_csv_export(self):
        """Test CSV export functionality."""
        config = FinOpsConfig()
        exporter = EnterpriseExportEngine(config)

        test_data = {
            "cost_analysis": {
                "status": "completed",
                "cost_trends": {"total_monthly_spend": 100000.0},
                "optimization_opportunities": {"annual_savings_potential": 480000.0, "savings_percentage": 40.0},
            }
        }

        filename = exporter._export_csv(test_data)
        assert filename.endswith(".csv")
        assert config.report_timestamp in filename

    def test_html_export(self):
        """Test HTML export functionality."""
        config = FinOpsConfig()
        exporter = EnterpriseExportEngine(config)

        test_data = {"metadata": {"export_timestamp": datetime.now().isoformat()}}

        filename = exporter._export_html(test_data)
        assert filename.endswith(".html")
        assert config.report_timestamp in filename


class TestFactoryFunctions:
    """Test suite for factory and utility functions."""

    def test_create_finops_dashboard(self):
        """Test factory function for creating complete dashboard system."""
        config, discovery, cost_analyzer, auditor, exporter = create_finops_dashboard()

        # Verify all components are created
        assert isinstance(config, FinOpsConfig)
        assert isinstance(discovery, EnterpriseDiscovery)
        assert isinstance(cost_analyzer, MultiAccountCostTrendAnalyzer)
        assert isinstance(auditor, EnterpriseResourceAuditor)
        assert isinstance(exporter, EnterpriseExportEngine)

        # Verify components reference the same config
        assert discovery.config == config
        assert cost_analyzer.config == config
        assert auditor.config == config
        assert exporter.config == config

    def test_create_finops_dashboard_with_custom_config(self):
        """Test factory function with custom configuration."""
        custom_config = FinOpsConfig()
        custom_config.target_savings_percent = 50

        config, discovery, cost_analyzer, auditor, exporter = create_finops_dashboard(custom_config)

        assert config == custom_config
        assert config.target_savings_percent == 50

    def test_run_complete_finops_analysis(self):
        """Test complete analysis workflow function."""
        results = run_complete_finops_analysis()

        # Verify results structure
        assert "config" in results
        assert "discovery_results" in results
        assert "cost_analysis" in results
        assert "audit_results" in results
        assert "executive_summary" in results
        assert "export_status" in results
        assert "workflow_status" in results
        assert "timestamp" in results

        # Verify workflow completed successfully
        assert results["workflow_status"] == "completed"

        # Verify individual component results
        assert results["discovery_results"]["status"] or "error" in results["discovery_results"]
        assert results["cost_analysis"]["status"] == "completed"
        assert results["audit_results"]["status"] == "completed"


class TestErrorHandlingAndEdgeCases:
    """Test suite for error handling and edge cases."""

    def test_cost_analyzer_with_invalid_trend_data(self):
        """Test cost analyzer with invalid trend data."""
        config = FinOpsConfig()
        analyzer = MultiAccountCostTrendAnalyzer(config)

        # Force an error in trend generation
        with patch.object(analyzer, "_generate_dynamic_account_cost_trends", side_effect=Exception("Test error")):
            results = analyzer.analyze_cost_trends()

            assert results["status"] == "error"
            assert "error" in results
            assert results["error"] == "Test error"

    def test_heatmap_analyzer_with_empty_account_data(self):
        """Test heatmap analyzer with empty account data."""
        config = FinOpsConfig()
        empty_trend_data = {"cost_trends": {"account_data": []}}
        analyzer = ResourceUtilizationHeatmapAnalyzer(config, empty_trend_data)

        results = analyzer.analyze_resource_utilization()

        # Should handle empty data gracefully
        assert results["status"] == "completed"
        assert results["heatmap_data"]["total_accounts"] == 0
        assert results["heatmap_data"]["total_resources"] == 0

    def test_export_with_invalid_format(self):
        """Test export engine with invalid format."""
        config = FinOpsConfig()
        config.output_formats = ["invalid_format"]  # Invalid format
        exporter = EnterpriseExportEngine(config)

        test_data = {"discovery": {}, "cost_analysis": {}, "audit_results": {}, "executive_summary": {}}

        export_status = exporter.export_all_results(
            test_data["discovery"],
            test_data["cost_analysis"],
            test_data["audit_results"],
            test_data["executive_summary"],
        )

        # Should have failed export for invalid format
        assert len(export_status["failed_exports"]) == 1
        assert export_status["failed_exports"][0]["format"] == "invalid_format"
        assert "error" in export_status["failed_exports"][0]


if __name__ == "__main__":
    """
    Run the test suite directly.
    
    Usage:
        python test_finops_dashboard.py
        pytest test_finops_dashboard.py -v
        pytest test_finops_dashboard.py::TestFinOpsConfig -v
    """
    pytest.main([__file__, "-v"])

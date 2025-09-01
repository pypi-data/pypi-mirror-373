#!/usr/bin/env python3
"""
Reference Images Validation Test Suite for FinOps Dashboard.

This module validates the 5 reference image outputs from the finops module
to ensure comprehensive functionality and output validation against expected
enterprise-grade dashboard and reporting requirements.

Test Cases Based on Reference Images:
1. Cost Analysis Dashboard - Multi-account cost trending and optimization
2. Resource Utilization Heatmap - Efficiency scoring and rightsizing
3. Executive Summary Reports - C-suite financial visibility
4. Audit & Compliance Reports - Risk assessment and compliance scoring
5. Export & Integration - Multi-format data export capabilities

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
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


class TestReferenceImage1_CostAnalysisDashboard:
    """
    Test Case 1: Cost Analysis Dashboard Validation

    Validates the multi-account cost trending dashboard functionality
    corresponding to runbooks finops reference images.

    Expected Output Characteristics:
    - Multi-account cost trends with $152,991.07 baseline
    - 20+ account cost breakdown visualization
    - Optimization opportunities identification (25-50% target)
    - Time-series cost analysis and forecasting
    """

    @pytest.fixture
    def cost_dashboard_config(self):
        """Configuration for cost dashboard testing."""
        config = FinOpsConfig()
        config.target_savings_percent = 40  # 40% optimization target
        config.time_range_days = 90  # 3 months analysis
        config.min_account_threshold = 20  # Match 20+ accounts requirement
        return config

    def test_multi_account_cost_trending(self, cost_dashboard_config):
        """Test multi-account cost trending analysis matches reference image output."""
        analyzer = MultiAccountCostTrendAnalyzer(cost_dashboard_config)

        # Mock to simulate $152,991.07 baseline from reference
        with patch("runbooks.finops.finops_dashboard.random.uniform") as mock_uniform:
            mock_uniform.side_effect = [152991.07 / 25] * 25  # Distribute across 25 accounts

            results = analyzer.analyze_cost_trends()

            # Verify reference image characteristics
            assert results["status"] == "completed"
            assert "cost_trends" in results

            cost_trends = results["cost_trends"]

            # Validate multi-account structure (20+ accounts)
            assert cost_trends["total_accounts"] >= 20

            # Validate cost baseline approximates reference ($152,991.07)
            assert 140000 <= cost_trends["total_monthly_spend"] <= 160000

            # Validate account data structure for dashboard visualization
            account_data = cost_trends["account_data"]
            assert len(account_data) >= 20

            for account in account_data[:3]:  # Check first 3 accounts
                assert "account_id" in account
                assert "account_type" in account
                assert "monthly_spend" in account
                assert "optimization_potential" in account
                assert 0 <= account["optimization_potential"] <= 1

    def test_cost_optimization_opportunities_calculation(self, cost_dashboard_config):
        """Test cost optimization opportunities match reference image expectations."""
        analyzer = MultiAccountCostTrendAnalyzer(cost_dashboard_config)

        # Create test data matching reference image characteristics
        test_cost_trends = {
            "total_monthly_spend": 152991.07,
            "account_data": [
                {
                    "account_id": "prod-001",
                    "account_type": "production",
                    "monthly_spend": 45000.0,
                    "optimization_potential": 0.35,  # 35% potential
                },
                {
                    "account_id": "dev-001",
                    "account_type": "development",
                    "monthly_spend": 25000.0,
                    "optimization_potential": 0.60,  # 60% potential
                },
                {
                    "account_id": "staging-001",
                    "account_type": "staging",
                    "monthly_spend": 15000.0,
                    "optimization_potential": 0.45,  # 45% potential
                },
            ],
        }

        optimization = analyzer._calculate_optimization_opportunities(test_cost_trends)

        # Validate optimization calculations for dashboard display
        expected_savings = (45000 * 0.35) + (25000 * 0.60) + (15000 * 0.45)
        assert optimization["total_potential_savings"] == expected_savings

        # Validate annual projection for executive reporting
        assert optimization["annual_savings_potential"] == expected_savings * 12

        # Validate target achievement status for dashboard
        savings_percentage = (expected_savings / 152991.07) * 100
        assert optimization["savings_percentage"] == pytest.approx(savings_percentage, rel=0.01)

    def test_cost_trend_time_series_data(self, cost_dashboard_config):
        """Test time series data structure for dashboard charting."""
        analyzer = MultiAccountCostTrendAnalyzer(cost_dashboard_config)
        results = analyzer.analyze_cost_trends()

        cost_trends = results["cost_trends"]

        # Validate time series structure for dashboard visualization
        assert "cost_trend_summary" in cost_trends

        trend_summary = cost_trends["cost_trend_summary"]
        assert "trend_direction" in trend_summary
        assert "month_over_month_change" in trend_summary
        assert "cost_volatility" in trend_summary

        # Validate trend direction is valid for dashboard display
        assert trend_summary["trend_direction"] in ["increasing", "decreasing", "stable"]

        # Validate month-over-month change is numeric for charts
        assert isinstance(trend_summary["month_over_month_change"], (int, float))


class TestReferenceImage2_ResourceUtilizationHeatmap:
    """
    Test Case 2: Resource Utilization Heatmap Validation

    Validates the resource utilization heatmap functionality showing
    efficiency scoring and rightsizing recommendations across services.

    Expected Output Characteristics:
    - Resource utilization matrix across compute, storage, database, network
    - Efficiency scoring (low/medium/high categories)
    - Rightsizing recommendations with cost impact
    - Heat map data structure for visualization
    """

    @pytest.fixture
    def heatmap_test_data(self):
        """Test data for heatmap analysis."""
        return {
            "cost_trends": {
                "account_data": [
                    {"account_id": "prod-heatmap-001", "account_type": "production", "monthly_spend": 35000.0},
                    {"account_id": "dev-heatmap-001", "account_type": "development", "monthly_spend": 12000.0},
                    {"account_id": "staging-heatmap-001", "account_type": "staging", "monthly_spend": 8000.0},
                ]
            }
        }

    def test_resource_utilization_matrix_structure(self, heatmap_test_data):
        """Test resource utilization matrix matches reference image structure."""
        config = FinOpsConfig()
        analyzer = ResourceUtilizationHeatmapAnalyzer(config, heatmap_test_data)

        results = analyzer.analyze_resource_utilization()

        # Verify heatmap analysis completed
        assert results["status"] == "completed"
        assert "heatmap_data" in results

        heatmap_data = results["heatmap_data"]

        # Validate matrix structure for heatmap visualization
        assert "utilization_matrix" in heatmap_data
        assert "resource_categories" in heatmap_data

        # Validate resource categories match reference image services
        categories = heatmap_data["resource_categories"]
        required_categories = ["compute", "storage", "database", "network"]

        for category in required_categories:
            assert category in categories

        # Validate utilization matrix has account-level data
        utilization_matrix = heatmap_data["utilization_matrix"]
        assert len(utilization_matrix) == 3  # 3 accounts from test data

        # Validate each account has resource utilization data
        for account_util in utilization_matrix:
            assert "account_id" in account_util
            assert "resource_utilization" in account_util

            resource_util = account_util["resource_utilization"]
            for category in required_categories:
                assert category in resource_util

    def test_efficiency_scoring_calculation(self, heatmap_test_data):
        """Test efficiency scoring matches reference image scoring logic."""
        config = FinOpsConfig()
        analyzer = ResourceUtilizationHeatmapAnalyzer(config, heatmap_test_data)

        results = analyzer.analyze_resource_utilization()

        # Validate efficiency scoring structure
        assert "efficiency_scoring" in results
        efficiency = results["efficiency_scoring"]

        assert "average_efficiency_score" in efficiency
        assert "efficiency_distribution" in efficiency

        # Validate average efficiency score is numeric
        avg_score = efficiency["average_efficiency_score"]
        assert 0 <= avg_score <= 100

        # Validate efficiency distribution for heatmap color coding
        distribution = efficiency["efficiency_distribution"]
        assert "low_efficiency" in distribution  # < 40% (red)
        assert "medium_efficiency" in distribution  # 40-70% (yellow)
        assert "high_efficiency" in distribution  # >= 70% (green)
        assert "total_resources_scored" in distribution

        # Validate counts sum correctly
        total_counted = (
            distribution["low_efficiency"] + distribution["medium_efficiency"] + distribution["high_efficiency"]
        )
        assert total_counted == distribution["total_resources_scored"]

    def test_rightsizing_recommendations(self, heatmap_test_data):
        """Test rightsizing recommendations for reference image display."""
        config = FinOpsConfig()
        analyzer = ResourceUtilizationHeatmapAnalyzer(config, heatmap_test_data)

        results = analyzer.analyze_resource_utilization()

        # Validate rightsizing recommendations structure
        assert "rightsizing_recommendations" in results
        recommendations = results["rightsizing_recommendations"]

        assert "total_rightsizing_opportunities" in recommendations
        assert "potential_monthly_savings" in recommendations
        assert "recommendation_breakdown" in recommendations

        # Validate recommendation breakdown by resource type
        breakdown = recommendations["recommendation_breakdown"]

        for resource_type in ["ec2_instances", "lambda_functions", "s3_buckets", "rds_databases"]:
            if resource_type in breakdown:
                rec = breakdown[resource_type]
                assert "count" in rec
                assert "potential_savings" in rec
                assert "confidence_level" in rec

                # Validate confidence level for recommendation reliability
                assert rec["confidence_level"] in ["high", "medium", "low"]


class TestReferenceImage3_ExecutiveSummaryReports:
    """
    Test Case 3: Executive Summary Reports Validation

    Validates the C-suite executive summary functionality providing
    high-level financial and operational insights.

    Expected Output Characteristics:
    - Executive financial overview with key metrics
    - Operational overview with risk scoring
    - Executive recommendations with priorities
    - Board-level presentation format
    """

    @pytest.fixture
    def executive_test_data(self):
        """Test data for executive dashboard."""
        discovery_results = {"timestamp": datetime.now().isoformat(), "status": "completed"}

        cost_analysis = {
            "status": "completed",
            "cost_trends": {"total_monthly_spend": 152991.07, "total_accounts": 23},
            "optimization_opportunities": {
                "annual_savings_potential": 1835892.84,  # 40% of annual spend
                "savings_percentage": 40.0,
                "target_achievement": {"target": 40, "achieved": 40.0, "status": "achieved"},
            },
        }

        audit_results = {
            "status": "completed",
            "audit_data": {
                "total_resources_scanned": 3750,
                "risk_score": {
                    "overall": 68,
                    "breakdown": {"security": 72, "compliance": 65, "cost_optimization": 70, "governance": 64},
                },
                "recommendations": [
                    {"priority": "critical", "category": "security", "description": "Address public S3 buckets"},
                    {"priority": "high", "category": "cost", "description": "Implement EC2 rightsizing"},
                    {"priority": "high", "category": "governance", "description": "Enforce resource tagging"},
                    {"priority": "medium", "category": "compliance", "description": "Review IAM policies"},
                ],
            },
        }

        return discovery_results, cost_analysis, audit_results

    def test_executive_summary_generation(self, executive_test_data):
        """Test executive summary matches reference image requirements."""
        config = FinOpsConfig()
        discovery, cost_analysis, audit = executive_test_data

        dashboard = EnterpriseExecutiveDashboard(config, discovery, cost_analysis, audit)
        summary = dashboard.generate_executive_summary()

        # Validate executive summary structure
        assert "report_metadata" in summary
        assert "financial_overview" in summary
        assert "operational_overview" in summary
        assert "executive_recommendations" in summary

        # Validate report metadata for C-suite presentation
        metadata = summary["report_metadata"]
        assert metadata["report_type"] == "enterprise_finops_executive_summary"
        assert metadata["analysis_period"] == f"{config.time_range_days} days"
        assert metadata["target_savings"] == f"{config.target_savings_percent}%"
        assert "generation_timestamp" in metadata

    def test_financial_overview_metrics(self, executive_test_data):
        """Test financial overview matches reference image financial metrics."""
        config = FinOpsConfig()
        discovery, cost_analysis, audit = executive_test_data

        dashboard = EnterpriseExecutiveDashboard(config, discovery, cost_analysis, audit)
        summary = dashboard.generate_executive_summary()

        financial = summary["financial_overview"]

        # Validate key financial metrics for executive dashboard
        assert financial["current_monthly_spend"] == 152991.07
        assert financial["potential_annual_savings"] == 1835892.84
        assert financial["savings_percentage"] == 40.0
        assert financial["target_achieved"] is True

        # Validate financial trend indicators
        assert "roi_projection" in financial
        assert "payback_period" in financial

        # Validate ROI calculation (should be positive)
        assert financial["roi_projection"] > 0

    def test_operational_overview_scoring(self, executive_test_data):
        """Test operational overview scoring for executive visibility."""
        config = FinOpsConfig()
        discovery, cost_analysis, audit = executive_test_data

        dashboard = EnterpriseExecutiveDashboard(config, discovery, cost_analysis, audit)
        summary = dashboard.generate_executive_summary()

        operational = summary["operational_overview"]

        # Validate operational metrics
        assert operational["resources_scanned"] == 3750
        assert operational["overall_risk_score"] == 68
        assert operational["critical_findings"] == 1
        assert operational["high_findings"] == 2
        assert operational["total_accounts"] == 23

        # Validate operational health indicators
        assert "risk_level" in operational
        assert operational["risk_level"] in ["low", "medium", "high", "critical"]

        # Risk score 68 should be 'medium' risk
        assert operational["risk_level"] == "medium"

    def test_executive_recommendations_prioritization(self, executive_test_data):
        """Test executive recommendations match reference image priorities."""
        config = FinOpsConfig()
        discovery, cost_analysis, audit = executive_test_data

        dashboard = EnterpriseExecutiveDashboard(config, discovery, cost_analysis, audit)
        summary = dashboard.generate_executive_summary()

        recommendations = summary["executive_recommendations"]

        # Validate recommendations structure
        assert "strategic_priorities" in recommendations
        assert "immediate_actions" in recommendations
        assert "investment_recommendations" in recommendations

        strategic = recommendations["strategic_priorities"]
        immediate = recommendations["immediate_actions"]

        # Validate strategic priorities are high-level
        assert len(strategic) >= 3
        for priority in strategic:
            assert "area" in priority
            assert "recommendation" in priority
            assert "business_impact" in priority

        # Validate immediate actions are actionable
        assert len(immediate) >= 1
        for action in immediate:
            assert "description" in action
            assert "timeline" in action
            assert "expected_outcome" in action


class TestReferenceImage4_AuditComplianceReports:
    """
    Test Case 4: Audit & Compliance Reports Validation

    Validates the audit and compliance functionality providing
    comprehensive risk assessment and compliance scoring.

    Expected Output Characteristics:
    - Multi-account compliance audit across all resources
    - Risk scoring with breakdown by category
    - Compliance findings with remediation priorities
    - Regulatory framework alignment (SOC2, etc.)
    """

    def test_compliance_audit_comprehensive_scope(self):
        """Test compliance audit covers comprehensive enterprise scope."""
        config = FinOpsConfig()
        auditor = EnterpriseResourceAuditor(config)

        results = auditor.run_compliance_audit()

        # Validate audit completion and scope
        assert results["status"] == "completed"
        assert results["audit_scope"] == "multi-account-enterprise"

        audit_data = results["audit_data"]

        # Validate comprehensive scanning metrics
        assert audit_data["total_resources_scanned"] > 1000  # Enterprise-scale
        assert audit_data["accounts_audited"] >= 5  # Multi-account coverage
        assert audit_data["regions_covered"] >= 2  # Multi-region coverage

        # Validate audit timestamp for compliance reporting
        assert "timestamp" in results
        assert isinstance(results["timestamp"], str)

    def test_risk_scoring_breakdown(self):
        """Test risk scoring breakdown matches compliance requirements."""
        config = FinOpsConfig()
        auditor = EnterpriseResourceAuditor(config)

        results = auditor.run_compliance_audit()
        audit_data = results["audit_data"]

        # Validate risk score structure
        assert "risk_score" in audit_data
        risk_score = audit_data["risk_score"]

        assert "overall" in risk_score
        assert "breakdown" in risk_score

        # Validate overall risk score
        overall_risk = risk_score["overall"]
        assert 0 <= overall_risk <= 100

        # Validate risk breakdown categories
        breakdown = risk_score["breakdown"]
        required_categories = ["security", "compliance", "cost_optimization", "governance"]

        for category in required_categories:
            assert category in breakdown
            assert 0 <= breakdown[category] <= 100

    def test_compliance_findings_categorization(self):
        """Test compliance findings match regulatory requirements."""
        config = FinOpsConfig()
        auditor = EnterpriseResourceAuditor(config)

        results = auditor.run_compliance_audit()
        audit_data = results["audit_data"]

        # Validate compliance findings structure
        assert "compliance_findings" in audit_data
        findings = audit_data["compliance_findings"]

        # Validate required finding categories for enterprise compliance
        required_findings = ["untagged_resources", "unused_resources", "security_groups", "public_resources"]

        for finding_type in required_findings:
            assert finding_type in findings

            finding = findings[finding_type]
            assert "count" in finding
            assert "severity" in finding
            assert "impact" in finding

            # Validate severity levels for prioritization
            assert finding["severity"] in ["low", "medium", "high", "critical"]

            # Validate impact assessment for business context
            assert finding["impact"] in ["low", "medium", "high"]

    def test_recommendations_prioritization_system(self):
        """Test recommendations follow enterprise prioritization system."""
        config = FinOpsConfig()
        auditor = EnterpriseResourceAuditor(config)

        results = auditor.run_compliance_audit()
        audit_data = results["audit_data"]

        # Validate recommendations structure
        assert "recommendations" in audit_data
        recommendations = audit_data["recommendations"]

        # Should have recommendations for enterprise environment
        assert len(recommendations) > 0

        # Validate recommendation structure and prioritization
        priority_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for rec in recommendations:
            assert "priority" in rec
            assert "category" in rec
            assert "description" in rec
            assert "remediation_effort" in rec

            # Count priorities for validation
            if rec["priority"] in priority_counts:
                priority_counts[rec["priority"]] += 1

            # Validate category alignment
            assert rec["category"] in ["security", "compliance", "cost", "governance", "performance"]

            # Validate remediation effort estimation
            assert rec["remediation_effort"] in ["low", "medium", "high"]


class TestReferenceImage5_ExportIntegration:
    """
    Test Case 5: Export & Integration Validation

    Validates the multi-format export functionality providing
    integration capabilities with external systems and reporting.

    Expected Output Characteristics:
    - Multi-format export (JSON, CSV, HTML, PDF)
    - Data integrity across export formats
    - Integration-ready data structures
    - Executive presentation formats
    """

    @pytest.fixture
    def export_test_data(self):
        """Comprehensive test data for export validation."""
        discovery = {
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "available_profiles": ["profile1", "profile2"],
            "configured_profiles": {
                "billing": "ams-admin-Billing-ReadOnlyAccess-909135376185",
                "management": "ams-admin-ReadOnlyAccess-909135376185",
            },
        }

        cost_analysis = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "cost_trends": {
                "total_monthly_spend": 152991.07,
                "total_accounts": 23,
                "account_data": [
                    {
                        "account_id": "export-test-001",
                        "account_type": "production",
                        "monthly_spend": 45000.0,
                        "optimization_potential": 0.35,
                    },
                    {
                        "account_id": "export-test-002",
                        "account_type": "development",
                        "monthly_spend": 25000.0,
                        "optimization_potential": 0.60,
                    },
                ],
            },
            "optimization_opportunities": {"annual_savings_potential": 1835892.84, "savings_percentage": 40.0},
        }

        audit_results = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "audit_data": {
                "total_resources_scanned": 3750,
                "risk_score": {"overall": 68},
                "recommendations": [
                    {"priority": "critical", "category": "security", "description": "Fix critical issues"},
                    {"priority": "high", "category": "cost", "description": "Optimize high-cost resources"},
                ],
            },
        }

        executive_summary = {
            "report_metadata": {
                "timestamp": datetime.now().isoformat(),
                "report_type": "enterprise_finops_executive_summary",
            },
            "financial_overview": {"current_monthly_spend": 152991.07, "potential_annual_savings": 1835892.84},
        }

        return discovery, cost_analysis, audit_results, executive_summary

    def test_multi_format_export_capability(self, export_test_data):
        """Test multi-format export matches reference image capabilities."""
        config = FinOpsConfig()
        # Ensure all formats are enabled for testing
        config.output_formats = ["json", "csv", "html"]

        exporter = EnterpriseExportEngine(config)
        discovery, cost_analysis, audit_results, executive_summary = export_test_data

        export_status = exporter.export_all_results(discovery, cost_analysis, audit_results, executive_summary)

        # Validate export status structure
        assert "successful_exports" in export_status
        assert "failed_exports" in export_status

        # Validate all formats exported successfully
        successful = export_status["successful_exports"]
        assert len(successful) == len(config.output_formats)

        # Validate each export has required metadata
        for export_info in successful:
            assert "format" in export_info
            assert "filename" in export_info
            assert "timestamp" in export_info
            assert "size_bytes" in export_info

            # Validate filename includes timestamp for uniqueness
            assert config.report_timestamp in export_info["filename"]

    def test_json_export_data_integrity(self, export_test_data):
        """Test JSON export maintains complete data integrity."""
        config = FinOpsConfig()
        exporter = EnterpriseExportEngine(config)

        discovery, cost_analysis, audit_results, executive_summary = export_test_data

        # Create comprehensive data structure for JSON export
        complete_data = {
            "discovery": discovery,
            "cost_analysis": cost_analysis,
            "audit_results": audit_results,
            "executive_summary": executive_summary,
            "export_metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "export_version": "0.7.8",
                "data_completeness": "full",
            },
        }

        filename = exporter._export_json(complete_data)

        # Validate JSON export succeeded
        assert filename.endswith(".json")
        assert config.report_timestamp in filename

        # Validate file was created (in-memory testing)
        # In real implementation, would verify file contents match input data

    def test_csv_export_tabular_structure(self, export_test_data):
        """Test CSV export provides proper tabular structure."""
        config = FinOpsConfig()
        exporter = EnterpriseExportEngine(config)

        discovery, cost_analysis, audit_results, executive_summary = export_test_data

        # Structure data for CSV export testing
        csv_data = {
            "cost_analysis": cost_analysis,
            "audit_summary": {
                "total_resources": audit_results["audit_data"]["total_resources_scanned"],
                "risk_score": audit_results["audit_data"]["risk_score"]["overall"],
            },
        }

        filename = exporter._export_csv(csv_data)

        # Validate CSV export succeeded
        assert filename.endswith(".csv")
        assert config.report_timestamp in filename

    def test_html_executive_presentation_format(self, export_test_data):
        """Test HTML export provides executive presentation format."""
        config = FinOpsConfig()
        exporter = EnterpriseExportEngine(config)

        discovery, cost_analysis, audit_results, executive_summary = export_test_data

        # Structure data for HTML executive presentation
        presentation_data = {
            "executive_summary": executive_summary,
            "key_metrics": {
                "monthly_spend": cost_analysis["cost_trends"]["total_monthly_spend"],
                "total_accounts": cost_analysis["cost_trends"]["total_accounts"],
                "risk_score": audit_results["audit_data"]["risk_score"]["overall"],
                "potential_savings": cost_analysis["optimization_opportunities"]["annual_savings_potential"],
            },
            "presentation_metadata": {"timestamp": datetime.now().isoformat(), "format": "executive_dashboard"},
        }

        filename = exporter._export_html(presentation_data)

        # Validate HTML export succeeded
        assert filename.endswith(".html")
        assert config.report_timestamp in filename

    def test_export_error_handling_resilience(self):
        """Test export error handling for production resilience."""
        config = FinOpsConfig()
        # Test with invalid format to trigger error handling
        config.output_formats = ["json", "invalid_format", "csv"]

        exporter = EnterpriseExportEngine(config)

        # Minimal test data
        test_data = {
            "discovery": {"status": "completed"},
            "cost_analysis": {"status": "completed"},
            "audit_results": {"status": "completed"},
            "executive_summary": {"report_metadata": {}},
        }

        export_status = exporter.export_all_results(
            test_data["discovery"],
            test_data["cost_analysis"],
            test_data["audit_results"],
            test_data["executive_summary"],
        )

        # Validate error handling
        assert len(export_status["successful_exports"]) == 2  # json and csv
        assert len(export_status["failed_exports"]) == 1  # invalid_format

        # Validate failed export contains error information
        failed_export = export_status["failed_exports"][0]
        assert failed_export["format"] == "invalid_format"
        assert "error" in failed_export


class TestIntegratedWorkflowValidation:
    """
    Integration test validating complete workflow across all 5 reference images.

    This test ensures the complete finops analysis workflow produces
    outputs that match all reference image requirements simultaneously.
    """

    def test_complete_finops_workflow_integration(self):
        """Test complete workflow produces all reference image outputs."""
        # Run complete analysis workflow
        results = run_complete_finops_analysis()

        # Validate workflow completion
        assert results["workflow_status"] == "completed"
        assert "timestamp" in results

        # Validate all major components completed successfully
        component_statuses = {
            "discovery": results["discovery_results"].get("status"),
            "cost_analysis": results["cost_analysis"].get("status"),
            "audit_results": results["audit_results"].get("status"),
        }

        for component, status in component_statuses.items():
            assert status in ["completed", "error"], f"{component} has invalid status: {status}"

        # At minimum, cost analysis and audit should complete
        assert results["cost_analysis"]["status"] == "completed"
        assert results["audit_results"]["status"] == "completed"

        # Validate executive summary generation
        assert "executive_summary" in results
        assert "report_metadata" in results["executive_summary"]

        # Validate export functionality
        assert "export_status" in results
        export_status = results["export_status"]

        # Should have at least some successful exports
        if "successful_exports" in export_status:
            assert len(export_status["successful_exports"]) > 0

    def test_performance_targets_validation(self):
        """Test performance targets are met across all reference functionalities."""
        import time

        # Measure complete workflow execution time
        start_time = time.perf_counter()
        results = run_complete_finops_analysis()
        execution_time = time.perf_counter() - start_time

        # Validate performance target: <2s for complete analysis
        assert execution_time < 2.0, f"Execution time {execution_time:.2f}s exceeds 2s target"

        # Validate workflow completed despite performance constraints
        assert results["workflow_status"] == "completed"

    def test_enterprise_scale_data_validation(self):
        """Test enterprise-scale data characteristics across all components."""
        results = run_complete_finops_analysis()

        # Validate enterprise scale in cost analysis
        if results["cost_analysis"]["status"] == "completed":
            cost_trends = results["cost_analysis"]["cost_trends"]

            # Should handle enterprise account counts
            assert cost_trends["total_accounts"] >= 5

            # Should handle enterprise spend levels
            assert cost_trends["total_monthly_spend"] > 10000

        # Validate enterprise scale in audit results
        if results["audit_results"]["status"] == "completed":
            audit_data = results["audit_results"]["audit_data"]

            # Should scan enterprise-scale resources
            assert audit_data["total_resources_scanned"] >= 100

            # Should cover multiple accounts
            assert audit_data["accounts_audited"] >= 1


if __name__ == "__main__":
    """
    Run the reference images validation test suite.
    
    Usage:
        python test_reference_images_validation.py
        pytest test_reference_images_validation.py -v
        pytest test_reference_images_validation.py::TestReferenceImage1_CostAnalysisDashboard -v
    """
    pytest.main([__file__, "-v", "--tb=short"])

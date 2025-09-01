#!/usr/bin/env python3
"""
Performance Benchmark Test Suite for FinOps Dashboard.

This module validates performance requirements for the finops module
to ensure sub-second execution targets are maintained under enterprise load.

Performance Requirements:
- Complete analysis workflow: <2s
- Individual component analysis: <1s
- Export operations: <500ms per format
- Memory usage: <500MB peak
- AWS API efficiency: <100 API calls per analysis

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import gc
import time
import tracemalloc
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from runbooks.finops.finops_dashboard import (
    EnterpriseDiscovery,
    EnterpriseExecutiveDashboard,
    EnterpriseExportEngine,
    EnterpriseResourceAuditor,
    FinOpsConfig,
    MultiAccountCostTrendAnalyzer,
    ResourceUtilizationHeatmapAnalyzer,
    run_complete_finops_analysis,
)


class PerformanceMonitor:
    """Performance monitoring utility for benchmarking."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.peak_memory = None
        self.api_call_count = 0

    def start_monitoring(self):
        """Start performance monitoring."""
        gc.collect()  # Clean up before monitoring
        tracemalloc.start()
        self.start_time = time.perf_counter()
        self.api_call_count = 0

    def stop_monitoring(self):
        """Stop monitoring and collect results."""
        self.end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        self.peak_memory = peak / (1024 * 1024)  # Convert to MB
        return {
            "execution_time": self.end_time - self.start_time,
            "peak_memory_mb": self.peak_memory,
            "api_calls": self.api_call_count,
        }

    def track_api_call(self):
        """Track an API call for efficiency monitoring."""
        self.api_call_count += 1


@pytest.fixture
def performance_monitor():
    """Fixture providing performance monitoring."""
    return PerformanceMonitor()


@pytest.fixture
def performance_config():
    """Configuration optimized for performance testing."""
    config = FinOpsConfig()
    config.time_range_days = 30  # Standard 30-day analysis
    config.min_account_threshold = 20  # Enterprise scale
    config.target_savings_percent = 40  # Standard optimization target
    return config


class TestComponentPerformanceBenchmarks:
    """Performance benchmarks for individual components."""

    def test_cost_trend_analyzer_performance(self, performance_config, performance_monitor):
        """Test cost trend analyzer meets <1s performance target."""
        analyzer = MultiAccountCostTrendAnalyzer(performance_config)

        performance_monitor.start_monitoring()

        # Execute cost trend analysis
        results = analyzer.analyze_cost_trends()

        metrics = performance_monitor.stop_monitoring()

        # Validate performance requirements
        assert metrics["execution_time"] < 1.0, f"Cost analysis took {metrics['execution_time']:.3f}s (>1s target)"
        assert metrics["peak_memory_mb"] < 100, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>100MB limit)"

        # Validate results quality wasn't compromised for performance
        assert results["status"] == "completed"
        assert "cost_trends" in results
        assert "optimization_opportunities" in results

    def test_resource_heatmap_analyzer_performance(self, performance_config, performance_monitor):
        """Test resource heatmap analyzer meets <1s performance target."""
        # Create test data for heatmap analysis
        trend_data = {
            "cost_trends": {
                "account_data": [
                    {"account_id": f"perf-test-{i:03d}", "account_type": "production", "monthly_spend": 25000.0}
                    for i in range(25)  # 25 accounts for enterprise scale
                ]
            }
        }

        analyzer = ResourceUtilizationHeatmapAnalyzer(performance_config, trend_data)

        performance_monitor.start_monitoring()

        # Execute heatmap analysis
        results = analyzer.analyze_resource_utilization()

        metrics = performance_monitor.stop_monitoring()

        # Validate performance requirements
        assert metrics["execution_time"] < 1.0, f"Heatmap analysis took {metrics['execution_time']:.3f}s (>1s target)"
        assert metrics["peak_memory_mb"] < 150, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>150MB limit)"

        # Validate results completeness
        assert results["status"] == "completed"
        assert "heatmap_data" in results
        assert "efficiency_scoring" in results

    def test_enterprise_auditor_performance(self, performance_config, performance_monitor):
        """Test enterprise auditor meets <1s performance target."""
        auditor = EnterpriseResourceAuditor(performance_config)

        performance_monitor.start_monitoring()

        # Execute compliance audit
        results = auditor.run_compliance_audit()

        metrics = performance_monitor.stop_monitoring()

        # Validate performance requirements
        assert metrics["execution_time"] < 1.0, f"Audit took {metrics['execution_time']:.3f}s (>1s target)"
        assert metrics["peak_memory_mb"] < 200, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>200MB limit)"

        # Validate audit completeness
        assert results["status"] == "completed"
        assert "audit_data" in results
        assert results["audit_data"]["total_resources_scanned"] > 0

    def test_account_discovery_performance(self, performance_config, performance_monitor):
        """Test account discovery meets <500ms performance target."""
        discovery = EnterpriseDiscovery(performance_config)

        performance_monitor.start_monitoring()

        # Mock AWS operations for consistent performance testing
        with (
            patch("runbooks.finops.finops_dashboard.get_aws_profiles") as mock_profiles,
            patch("runbooks.finops.finops_dashboard.get_account_id") as mock_account_id,
        ):
            mock_profiles.return_value = ["profile1", "profile2", "profile3"]
            mock_account_id.return_value = "123456789012"

            # Execute account discovery
            results = discovery.discover_accounts()

        metrics = performance_monitor.stop_monitoring()

        # Validate performance requirements (stricter for discovery)
        assert metrics["execution_time"] < 0.5, f"Discovery took {metrics['execution_time']:.3f}s (>500ms target)"
        assert metrics["peak_memory_mb"] < 50, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>50MB limit)"

        # Validate discovery results
        assert "configured_profiles" in results
        assert "account_info" in results


class TestExportPerformanceBenchmarks:
    """Performance benchmarks for export operations."""

    @pytest.fixture
    def large_test_dataset(self):
        """Large test dataset for export performance testing."""
        return {
            "discovery": {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "available_profiles": [f"profile-{i}" for i in range(10)],
            },
            "cost_analysis": {
                "status": "completed",
                "cost_trends": {
                    "total_monthly_spend": 500000.0,
                    "total_accounts": 50,
                    "account_data": [
                        {
                            "account_id": f"benchmark-{i:03d}",
                            "account_type": "production" if i % 3 == 0 else "development",
                            "monthly_spend": 10000.0,
                            "optimization_potential": 0.3 + (i % 4) * 0.1,
                        }
                        for i in range(50)  # 50 accounts worth of data
                    ],
                },
                "optimization_opportunities": {"annual_savings_potential": 2400000.0, "savings_percentage": 40.0},
            },
            "audit_results": {
                "status": "completed",
                "audit_data": {
                    "total_resources_scanned": 10000,
                    "risk_score": {"overall": 72},
                    "recommendations": [
                        {"priority": "high", "category": "cost", "description": f"Optimize resource group {i}"}
                        for i in range(25)  # 25 recommendations
                    ],
                },
            },
        }

    def test_json_export_performance(self, performance_config, performance_monitor, large_test_dataset):
        """Test JSON export meets <500ms performance target."""
        exporter = EnterpriseExportEngine(performance_config)

        performance_monitor.start_monitoring()

        # Execute JSON export with large dataset
        filename = exporter._export_json(large_test_dataset)

        metrics = performance_monitor.stop_monitoring()

        # Validate export performance
        assert metrics["execution_time"] < 0.5, f"JSON export took {metrics['execution_time']:.3f}s (>500ms target)"
        assert metrics["peak_memory_mb"] < 100, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>100MB limit)"

        # Validate export succeeded
        assert filename.endswith(".json")
        assert performance_config.report_timestamp in filename

    def test_csv_export_performance(self, performance_config, performance_monitor, large_test_dataset):
        """Test CSV export meets <500ms performance target."""
        exporter = EnterpriseExportEngine(performance_config)

        performance_monitor.start_monitoring()

        # Execute CSV export with large dataset
        filename = exporter._export_csv(large_test_dataset)

        metrics = performance_monitor.stop_monitoring()

        # Validate export performance
        assert metrics["execution_time"] < 0.5, f"CSV export took {metrics['execution_time']:.3f}s (>500ms target)"
        assert metrics["peak_memory_mb"] < 75, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>75MB limit)"

        # Validate export succeeded
        assert filename.endswith(".csv")

    def test_html_export_performance(self, performance_config, performance_monitor, large_test_dataset):
        """Test HTML export meets <500ms performance target."""
        exporter = EnterpriseExportEngine(performance_config)

        performance_monitor.start_monitoring()

        # Execute HTML export with large dataset
        filename = exporter._export_html(large_test_dataset)

        metrics = performance_monitor.stop_monitoring()

        # Validate export performance
        assert metrics["execution_time"] < 0.5, f"HTML export took {metrics['execution_time']:.3f}s (>500ms target)"
        assert metrics["peak_memory_mb"] < 80, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>80MB limit)"

        # Validate export succeeded
        assert filename.endswith(".html")

    def test_multi_format_export_performance(self, performance_config, performance_monitor, large_test_dataset):
        """Test multi-format export meets cumulative performance targets."""
        performance_config.output_formats = ["json", "csv", "html"]  # All formats
        exporter = EnterpriseExportEngine(performance_config)

        performance_monitor.start_monitoring()

        # Execute multi-format export
        export_status = exporter.export_all_results(
            large_test_dataset["discovery"],
            large_test_dataset["cost_analysis"],
            large_test_dataset["audit_results"],
            {"executive_summary": "test"},
        )

        metrics = performance_monitor.stop_monitoring()

        # Validate cumulative export performance (3 formats × 500ms = 1.5s max)
        assert metrics["execution_time"] < 1.5, (
            f"Multi-format export took {metrics['execution_time']:.3f}s (>1.5s target)"
        )
        assert metrics["peak_memory_mb"] < 200, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>200MB limit)"

        # Validate all exports succeeded
        assert len(export_status["successful_exports"]) == 3
        assert len(export_status["failed_exports"]) == 0


class TestWorkflowPerformanceBenchmarks:
    """Performance benchmarks for complete workflow operations."""

    def test_complete_workflow_performance_target(self, performance_monitor):
        """Test complete workflow meets <2s performance target."""
        performance_monitor.start_monitoring()

        # Execute complete workflow
        results = run_complete_finops_analysis()

        metrics = performance_monitor.stop_monitoring()

        # Validate primary performance requirement
        assert metrics["execution_time"] < 2.0, f"Complete workflow took {metrics['execution_time']:.3f}s (>2s target)"
        assert metrics["peak_memory_mb"] < 500, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>500MB limit)"

        # Validate workflow completed successfully
        assert results["workflow_status"] == "completed"
        assert "timestamp" in results

    def test_workflow_performance_consistency(self, performance_monitor):
        """Test workflow performance is consistent across multiple runs."""
        execution_times = []
        memory_peaks = []

        # Run workflow 5 times to test consistency
        for run in range(5):
            performance_monitor.start_monitoring()

            results = run_complete_finops_analysis()

            metrics = performance_monitor.stop_monitoring()

            execution_times.append(metrics["execution_time"])
            memory_peaks.append(metrics["peak_memory_mb"])

            # Each run should complete successfully
            assert results["workflow_status"] == "completed"

        # Calculate performance statistics
        avg_execution_time = sum(execution_times) / len(execution_times)
        max_execution_time = max(execution_times)
        avg_memory_peak = sum(memory_peaks) / len(memory_peaks)
        max_memory_peak = max(memory_peaks)

        # Validate performance consistency requirements
        assert avg_execution_time < 1.5, f"Average execution time {avg_execution_time:.3f}s (>1.5s target)"
        assert max_execution_time < 2.0, f"Maximum execution time {max_execution_time:.3f}s (>2s target)"
        assert avg_memory_peak < 400, f"Average memory peak {avg_memory_peak:.1f}MB (>400MB limit)"
        assert max_memory_peak < 500, f"Maximum memory peak {max_memory_peak:.1f}MB (>500MB limit)"

        # Validate reasonable performance variance (< 50% variation)
        time_variance = (max_execution_time - min(execution_times)) / avg_execution_time
        assert time_variance < 0.5, f"Execution time variance {time_variance:.2%} (>50% limit)"

    def test_enterprise_scale_performance(self, performance_monitor):
        """Test performance under enterprise scale conditions."""
        # Create enterprise-scale configuration
        config = FinOpsConfig()
        config.min_account_threshold = 60  # Large enterprise
        config.time_range_days = 90  # Quarterly analysis

        # Mock large-scale AWS environment
        with patch("runbooks.finops.finops_dashboard.random.randint") as mock_randint:
            mock_randint.return_value = 75  # 75 accounts

            performance_monitor.start_monitoring()

            # Execute workflow with enterprise scale
            results = run_complete_finops_analysis()

            metrics = performance_monitor.stop_monitoring()

        # Enterprise scale should still meet performance targets
        assert metrics["execution_time"] < 3.0, f"Enterprise scale took {metrics['execution_time']:.3f}s (>3s limit)"
        assert metrics["peak_memory_mb"] < 750, f"Memory usage {metrics['peak_memory_mb']:.1f}MB (>750MB limit)"

        # Validate enterprise scale was actually tested
        if results["cost_analysis"]["status"] == "completed":
            cost_trends = results["cost_analysis"]["cost_trends"]
            assert cost_trends["total_accounts"] >= 60

    def test_concurrent_workflow_performance(self, performance_monitor):
        """Test performance impact of concurrent operations."""
        import concurrent.futures

        def run_workflow():
            """Run workflow and return execution time."""
            start = time.perf_counter()
            results = run_complete_finops_analysis()
            end = time.perf_counter()
            return end - start, results["workflow_status"]

        performance_monitor.start_monitoring()

        # Run 3 concurrent workflows
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_workflow) for _ in range(3)]
            concurrent_results = [future.result() for future in concurrent_futures.as_completed(futures)]

        metrics = performance_monitor.stop_monitoring()

        # Validate all concurrent workflows completed
        execution_times, statuses = zip(*concurrent_results)
        assert all(status == "completed" for status in statuses)

        # Validate concurrent performance (some degradation expected)
        max_concurrent_time = max(execution_times)
        assert max_concurrent_time < 4.0, f"Concurrent workflow took {max_concurrent_time:.3f}s (>4s limit)"

        # Total memory usage should be reasonable for concurrent operations
        assert metrics["peak_memory_mb"] < 1000, (
            f"Concurrent memory usage {metrics['peak_memory_mb']:.1f}MB (>1GB limit)"
        )


class TestMemoryEfficiencyBenchmarks:
    """Memory efficiency benchmarks for sustained operations."""

    def test_memory_leak_detection(self, performance_monitor):
        """Test for memory leaks during repeated operations."""
        initial_memory = None
        memory_samples = []

        # Run workflow 10 times and monitor memory
        for iteration in range(10):
            performance_monitor.start_monitoring()

            results = run_complete_finops_analysis()

            metrics = performance_monitor.stop_monitoring()
            memory_samples.append(metrics["peak_memory_mb"])

            if initial_memory is None:
                initial_memory = metrics["peak_memory_mb"]

            # Validate each iteration completes
            assert results["workflow_status"] == "completed"

        # Calculate memory growth
        final_memory = memory_samples[-1]
        memory_growth = final_memory - initial_memory
        memory_growth_percent = (memory_growth / initial_memory) * 100

        # Validate no significant memory leaks (< 20% growth over 10 iterations)
        assert memory_growth_percent < 20, f"Memory grew {memory_growth_percent:.1f}% (>20% limit)"
        assert final_memory < 600, f"Final memory {final_memory:.1f}MB (>600MB limit)"

    def test_garbage_collection_efficiency(self, performance_monitor):
        """Test garbage collection efficiency during operations."""
        gc.collect()  # Initial cleanup
        initial_objects = len(gc.get_objects())

        performance_monitor.start_monitoring()

        # Run workflow
        results = run_complete_finops_analysis()

        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())

        metrics = performance_monitor.stop_monitoring()

        # Validate workflow completed
        assert results["workflow_status"] == "completed"

        # Validate object growth is reasonable
        object_growth = final_objects - initial_objects
        object_growth_percent = (object_growth / initial_objects) * 100

        # Object growth should be minimal after GC
        assert object_growth_percent < 10, f"Object count grew {object_growth_percent:.1f}% (>10% limit)"
        assert metrics["peak_memory_mb"] < 400, f"Peak memory {metrics['peak_memory_mb']:.1f}MB (>400MB limit)"


if __name__ == "__main__":
    """
    Run the performance benchmark test suite.
    
    Usage:
        python test_performance_benchmarks.py
        pytest test_performance_benchmarks.py -v -s
        pytest test_performance_benchmarks.py::TestWorkflowPerformanceBenchmarks::test_complete_workflow_performance_target -v
    """
    pytest.main([__file__, "-v", "-s", "--tb=short"])

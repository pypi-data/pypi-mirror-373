#!/usr/bin/env python3
"""
Performance Tests for FinOps Dashboard Enterprise Components.

This module provides performance testing to ensure the FinOps dashboard
can handle enterprise-scale workloads efficiently.

Test Coverage:
- Large account dataset processing (100+ accounts)
- High resource count analysis (10,000+ resources)
- Memory usage optimization
- Response time benchmarking
- Concurrent analysis capabilities

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

import psutil
import pytest

# Import the components we're testing
from runbooks.finops.finops_dashboard import (
    EnterpriseResourceAuditor,
    FinOpsConfig,
    MultiAccountCostTrendAnalyzer,
    ResourceUtilizationHeatmapAnalyzer,
    run_complete_finops_analysis,
)


class TestPerformanceBenchmarks:
    """Performance benchmarks for FinOps dashboard components."""

    def test_cost_analysis_response_time(self):
        """Test cost analysis response time with various account counts."""
        config = FinOpsConfig()
        analyzer = MultiAccountCostTrendAnalyzer(config)

        # Test with different account counts
        test_cases = [5, 10, 25, 50, 85]  # Various account counts
        response_times = []

        for account_count in test_cases:
            with patch("runbooks.finops.finops_dashboard.random.randint") as mock_randint:
                mock_randint.return_value = account_count

                start_time = time.perf_counter()
                results = analyzer.analyze_cost_trends()
                end_time = time.perf_counter()

                response_time = end_time - start_time
                response_times.append((account_count, response_time))

                # Verify results are valid
                assert results["status"] == "completed"
                assert results["cost_trends"]["total_accounts"] == account_count

                # Performance assertions
                assert response_time < 5.0, f"Analysis took {response_time:.2f}s for {account_count} accounts"

        # Verify performance scaling is reasonable
        print("\nCost Analysis Response Times:")
        for account_count, response_time in response_times:
            print(f"  {account_count} accounts: {response_time:.3f}s")

        # Response time should scale reasonably with account count
        small_time = response_times[0][1]  # 5 accounts
        large_time = response_times[-1][1]  # 85 accounts

        # Large dataset shouldn't be more than 10x slower
        assert large_time < small_time * 10

    def test_memory_usage_optimization(self):
        """Test memory usage with large datasets."""
        config = FinOpsConfig()

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Run analysis with maximum account count
        with patch("runbooks.finops.finops_dashboard.random.randint") as mock_randint:
            mock_randint.return_value = 85  # Maximum accounts

            analyzer = MultiAccountCostTrendAnalyzer(config)
            results = analyzer.analyze_cost_trends()

            # Check memory usage after analysis
            peak_memory = process.memory_info().rss
            memory_increase = peak_memory - initial_memory

            # Memory increase should be reasonable (less than 100MB)
            assert memory_increase < 100 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"

            # Verify results are valid
            assert results["status"] == "completed"
            assert len(results["cost_trends"]["account_data"]) == 85

            print(f"\nMemory Usage:")
            print(f"  Initial: {initial_memory / 1024 / 1024:.2f}MB")
            print(f"  Peak: {peak_memory / 1024 / 1024:.2f}MB")
            print(f"  Increase: {memory_increase / 1024 / 1024:.2f}MB")

    def test_resource_heatmap_performance(self):
        """Test resource heatmap performance with large resource counts."""
        config = FinOpsConfig()

        # Create large dataset with high-spend accounts (generates more resources)
        large_account_data = []
        for i in range(30):  # 30 high-spend accounts
            large_account_data.append(
                {
                    "account_id": f"perf-test-{i:03d}",
                    "account_type": "production",
                    "monthly_spend": 75000.0,  # High spend = more resources
                }
            )

        trend_data = {"cost_trends": {"account_data": large_account_data}}

        analyzer = ResourceUtilizationHeatmapAnalyzer(config, trend_data)

        # Measure performance
        start_time = time.perf_counter()
        results = analyzer.analyze_resource_utilization()
        end_time = time.perf_counter()

        response_time = end_time - start_time

        # Performance assertions
        assert response_time < 10.0, f"Heatmap analysis took {response_time:.2f}s"

        # Verify results
        assert results["status"] == "completed"
        heatmap_data = results["heatmap_data"]
        assert heatmap_data["total_accounts"] == 30
        assert heatmap_data["total_resources"] > 1000  # Should generate many resources

        print(f"\nResource Heatmap Performance:")
        print(f"  Response time: {response_time:.3f}s")
        print(f"  Total resources: {heatmap_data['total_resources']:,}")
        print(f"  Resources per second: {heatmap_data['total_resources'] / response_time:,.0f}")

    def test_complete_workflow_performance(self):
        """Test complete workflow performance under realistic load."""
        start_time = time.perf_counter()

        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Run complete analysis
        results = run_complete_finops_analysis()

        end_time = time.perf_counter()
        peak_memory = process.memory_info().rss

        total_time = end_time - start_time
        memory_increase = peak_memory - initial_memory

        # Performance assertions
        assert total_time < 30.0, f"Complete workflow took {total_time:.2f}s"
        assert memory_increase < 200 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"

        # Verify workflow completed successfully
        assert results["workflow_status"] == "completed"

        print(f"\nComplete Workflow Performance:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Memory increase: {memory_increase / 1024 / 1024:.2f}MB")

        # Verify all components completed
        assert results["cost_analysis"]["status"] == "completed"
        assert results["audit_results"]["status"] == "completed"
        assert "executive_summary" in results
        assert "export_status" in results


class TestConcurrencyAndThreadSafety:
    """Test concurrent execution and thread safety."""

    def test_concurrent_cost_analysis(self):
        """Test concurrent cost analysis execution."""
        config = FinOpsConfig()

        def run_analysis():
            """Run a single cost analysis."""
            analyzer = MultiAccountCostTrendAnalyzer(config)
            results = analyzer.analyze_cost_trends()
            assert results["status"] == "completed"
            return results

        # Run multiple analyses concurrently
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(run_analysis) for _ in range(4)]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.perf_counter()

        # Verify all analyses completed successfully
        assert len(results) == 4
        for result in results:
            assert result["status"] == "completed"
            assert "cost_trends" in result
            assert "optimization_opportunities" in result

        concurrent_time = end_time - start_time

        # Concurrent execution should be faster than sequential
        print(f"\nConcurrent Analysis Performance:")
        print(f"  4 concurrent analyses: {concurrent_time:.3f}s")

        # Should complete within reasonable time
        assert concurrent_time < 15.0, f"Concurrent analyses took {concurrent_time:.2f}s"

    def test_thread_safety_data_integrity(self):
        """Test data integrity under concurrent access."""
        config = FinOpsConfig()
        results_list = []

        def analyze_and_store():
            """Run analysis and store results."""
            analyzer = MultiAccountCostTrendAnalyzer(config)
            result = analyzer.analyze_cost_trends()
            results_list.append(result)

        # Run multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=analyze_and_store)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify data integrity
        assert len(results_list) == 3
        for result in results_list:
            assert result["status"] == "completed"
            assert isinstance(result["cost_trends"]["total_monthly_spend"], (int, float))
            assert result["cost_trends"]["total_monthly_spend"] > 0


class TestScalabilityLimits:
    """Test system behavior at scalability limits."""

    def test_maximum_account_processing(self):
        """Test processing with maximum supported account count."""
        config = FinOpsConfig()

        # Test with maximum account count
        with patch("runbooks.finops.finops_dashboard.random.randint") as mock_randint:
            mock_randint.return_value = 100  # Beyond normal maximum

            analyzer = MultiAccountCostTrendAnalyzer(config)

            start_time = time.perf_counter()
            results = analyzer.analyze_cost_trends()
            end_time = time.perf_counter()

            response_time = end_time - start_time

            # Should handle large account counts gracefully
            assert results["status"] == "completed"
            assert results["cost_trends"]["total_accounts"] == 100
            assert response_time < 10.0, f"Max account processing took {response_time:.2f}s"

            # Verify data quality isn't compromised
            cost_trends = results["cost_trends"]
            assert len(cost_trends["account_data"]) == 100
            assert cost_trends["total_monthly_spend"] > 0
            assert cost_trends["cost_trend_summary"]["average_account_spend"] > 0

    def test_memory_limits_with_huge_datasets(self):
        """Test memory usage with very large datasets."""
        config = FinOpsConfig()

        # Create dataset with many high-resource accounts
        huge_account_data = []
        for i in range(50):  # 50 very high-spend accounts
            huge_account_data.append(
                {
                    "account_id": f"huge-account-{i:03d}",
                    "account_type": "production",
                    "monthly_spend": 100000.0,  # Very high spend
                }
            )

        trend_data = {"cost_trends": {"account_data": huge_account_data}}

        analyzer = ResourceUtilizationHeatmapAnalyzer(config, trend_data)

        # Monitor memory usage during analysis
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        results = analyzer.analyze_resource_utilization()

        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Verify results
        assert results["status"] == "completed"

        # Memory usage should remain reasonable even with huge datasets
        assert memory_increase < 500 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"

        heatmap_data = results["heatmap_data"]
        print(f"\nHuge Dataset Processing:")
        print(f"  Total resources: {heatmap_data['total_resources']:,}")
        print(f"  Memory increase: {memory_increase / 1024 / 1024:.2f}MB")
        print(f"  Memory per resource: {memory_increase / heatmap_data['total_resources']:.0f} bytes")


class TestResponseTimeConsistency:
    """Test response time consistency and variance."""

    def test_response_time_consistency(self):
        """Test that response times are consistent across multiple runs."""
        config = FinOpsConfig()

        # Run same analysis multiple times
        response_times = []
        account_count = 25  # Fixed account count for consistency

        for _ in range(10):  # 10 runs
            with patch("runbooks.finops.finops_dashboard.random.randint") as mock_randint:
                mock_randint.return_value = account_count

                analyzer = MultiAccountCostTrendAnalyzer(config)

                start_time = time.perf_counter()
                results = analyzer.analyze_cost_trends()
                end_time = time.perf_counter()

                response_time = end_time - start_time
                response_times.append(response_time)

                assert results["status"] == "completed"

        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        variance = sum((t - avg_time) ** 2 for t in response_times) / len(response_times)
        std_dev = variance**0.5

        print(f"\nResponse Time Consistency (10 runs):")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Min: {min_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        print(f"  Std Dev: {std_dev:.3f}s")

        # Response times should be consistent (low variance)
        assert std_dev < avg_time * 0.3, f"High variance in response times: {std_dev:.3f}s"

        # Maximum time shouldn't be more than 2x average
        assert max_time < avg_time * 2, f"Maximum time {max_time:.3f}s too high vs average {avg_time:.3f}s"


if __name__ == "__main__":
    """
    Run the performance test suite directly.
    
    Usage:
        python test_performance.py
        pytest test_performance.py -v -s  # -s to see print output
        pytest test_performance.py::TestPerformanceBenchmarks::test_memory_usage_optimization -v -s
    """
    pytest.main([__file__, "-v", "-s"])

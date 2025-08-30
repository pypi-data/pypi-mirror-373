#!/usr/bin/env python3
"""
Test Runner for FinOps Dashboard Enterprise Components.

This script runs all tests for the FinOps dashboard and provides
a comprehensive validation report.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit-only        # Run only unit tests
    python run_tests.py --integration-only # Run only integration tests
    python run_tests.py --performance-only # Run only performance tests
    python run_tests.py --quick            # Run quick validation tests only

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import argparse
import sys
import time
from pathlib import Path

# Add the finops module to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_basic_validation():
    """Run basic validation to ensure modules can be imported."""
    print("🔍 Running Basic Validation...")

    try:
        # Test basic imports
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

        print("  ✅ All imports successful")

        # Test basic instantiation
        config = FinOpsConfig()
        print("  ✅ FinOpsConfig creation successful")

        discovery = EnterpriseDiscovery(config)
        print("  ✅ EnterpriseDiscovery creation successful")

        cost_analyzer = MultiAccountCostTrendAnalyzer(config)
        print("  ✅ MultiAccountCostTrendAnalyzer creation successful")

        # Test factory function
        components = create_finops_dashboard()
        print("  ✅ Factory function successful")

        print("✅ Basic validation passed\n")
        return True

    except Exception as e:
        print(f"❌ Basic validation failed: {e}\n")
        return False


def run_quick_functional_test():
    """Run quick functional test to verify core functionality."""
    print("🚀 Running Quick Functional Test...")

    try:
        from runbooks.finops.finops_dashboard import run_complete_finops_analysis

        start_time = time.perf_counter()
        results = run_complete_finops_analysis()
        end_time = time.perf_counter()

        # Verify results
        assert results["workflow_status"] == "completed"
        assert "cost_analysis" in results
        assert "audit_results" in results
        assert "executive_summary" in results

        execution_time = end_time - start_time
        print(f"  ✅ Complete workflow executed in {execution_time:.2f}s")

        # Display key metrics
        if results["cost_analysis"]["status"] == "completed":
            cost_data = results["cost_analysis"]["cost_trends"]
            optimization = results["cost_analysis"]["optimization_opportunities"]

            print(f"  📊 Analyzed {cost_data['total_accounts']} accounts")
            print(f"  💰 Total monthly spend: ${cost_data['total_monthly_spend']:,.2f}")
            print(f"  🎯 Potential savings: {optimization['savings_percentage']:.1f}%")
            print(f"  💵 Annual impact: ${optimization['annual_savings_potential']:,.2f}")

        if "export_status" in results:
            successful = len(results["export_status"]["successful_exports"])
            failed = len(results["export_status"]["failed_exports"])
            print(f"  📄 Exports: {successful} successful, {failed} failed")

        print("✅ Quick functional test passed\n")
        return True

    except Exception as e:
        print(f"❌ Quick functional test failed: {e}\n")
        return False


def run_dashboard_runner_integration():
    """Test integration with dashboard_runner module."""
    print("🔗 Testing Dashboard Runner Integration...")

    try:
        from runbooks.finops.dashboard_runner import (
            _run_cost_trend_analysis,
            _run_executive_dashboard,
            _run_resource_heatmap_analysis,
            run_complete_finops_workflow,
        )

        print("  ✅ Dashboard runner imports successful")

        # Test function existence and basic structure
        import inspect

        # Check function signatures
        sig = inspect.signature(_run_cost_trend_analysis)
        assert len(sig.parameters) == 2  # profiles, args
        print("  ✅ _run_cost_trend_analysis signature correct")

        sig = inspect.signature(_run_resource_heatmap_analysis)
        assert len(sig.parameters) == 3  # profiles, cost_data, args
        print("  ✅ _run_resource_heatmap_analysis signature correct")

        sig = inspect.signature(_run_executive_dashboard)
        assert len(sig.parameters) == 4  # discovery, cost, audit, args
        print("  ✅ _run_executive_dashboard signature correct")

        print("✅ Dashboard runner integration verified\n")
        return True

    except Exception as e:
        print(f"❌ Dashboard runner integration failed: {e}\n")
        return False


def run_module_exports_test():
    """Test module exports from __init__.py."""
    print("📦 Testing Module Exports...")

    try:
        from runbooks.finops import (
            EnterpriseDiscovery,
            EnterpriseExecutiveDashboard,
            EnterpriseExportEngine,
            EnterpriseResourceAuditor,
            # New v0.7.8 exports
            FinOpsConfig,
            MultiAccountCostTrendAnalyzer,
            ResourceUtilizationHeatmapAnalyzer,
            _run_cost_trend_analysis,
            _run_executive_dashboard,
            _run_resource_heatmap_analysis,
            create_finops_dashboard,
            get_aws_profiles,
            get_cost_data,
            run_complete_finops_analysis,
            run_complete_finops_workflow,
            # Existing exports
            run_dashboard,
        )

        print("  ✅ All expected exports available")

        # Test version number
        from runbooks.finops import __version__

        assert __version__ == "0.7.8"
        print(f"  ✅ Version {__version__} correct")

        print("✅ Module exports test passed\n")
        return True

    except Exception as e:
        print(f"❌ Module exports test failed: {e}\n")
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="FinOps Dashboard Test Runner")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    parser.add_argument("--performance-only", action="store_true", help="Run only performance tests")
    parser.add_argument("--quick", action="store_true", help="Run quick validation tests only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print("🧪 FinOps Dashboard Test Runner v0.7.8")
    print("=" * 60)

    start_time = time.perf_counter()

    if args.quick:
        # Quick validation mode
        tests = [
            run_basic_validation,
            run_quick_functional_test,
            run_dashboard_runner_integration,
            run_module_exports_test,
        ]
    elif args.unit_only:
        print("Running unit tests with pytest...")
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(Path(__file__).parent / "test_finops_dashboard.py"),
                "-v" if args.verbose else "",
            ],
            capture_output=not args.verbose,
        )
        return result.returncode
    elif args.integration_only:
        print("Running integration tests with pytest...")
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(Path(__file__).parent / "test_integration.py"),
                "-v" if args.verbose else "",
            ],
            capture_output=not args.verbose,
        )
        return result.returncode
    elif args.performance_only:
        print("Running performance tests with pytest...")
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(Path(__file__).parent / "test_performance.py"),
                "-v" if args.verbose else "",
                "-s",
            ],
            capture_output=not args.verbose,
        )
        return result.returncode
    else:
        # Full validation mode
        tests = [
            run_basic_validation,
            run_quick_functional_test,
            run_dashboard_runner_integration,
            run_module_exports_test,
        ]

        print("Note: Use pytest directly to run comprehensive unit/integration/performance tests:")
        print("  pytest src/runbooks/finops/tests/ -v")
        print()

    # Run selected tests
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)

    end_time = time.perf_counter()
    total_time = end_time - start_time

    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total}) in {total_time:.2f}s")
        print("\n✅ FinOps Dashboard v0.7.8 is ready for production deployment!")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total}) in {total_time:.2f}s")
        print("\n⚠️  Please fix failing tests before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

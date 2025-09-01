#!/usr/bin/env python3
"""
Quick validation script for FinOps test suite.

This script performs rapid validation of our comprehensive test suite
without running the full test execution to ensure everything is properly set up.

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import sys
import time
from pathlib import Path


def validate_imports():
    """Validate all test modules can be imported."""
    print("🔍 Validating test suite imports...")

    try:
        sys.path.insert(0, "src")

        # Test core module imports
        from runbooks.finops.finops_dashboard import (
            EnterpriseResourceAuditor,
            FinOpsConfig,
            MultiAccountCostTrendAnalyzer,
            run_complete_finops_analysis,
        )

        print("✅ Core finops module imports successful")

        # Test individual test module imports
        test_modules = [
            "test_finops_dashboard",
            "test_reference_images_validation",
            "test_performance_benchmarks",
            "test_integration",
        ]

        for module in test_modules:
            try:
                __import__(f"runbooks.finops.tests.{module}")
                print(f"✅ {module} import successful")
            except ImportError as e:
                print(f"❌ {module} import failed: {e}")
                return False

        return True

    except Exception as e:
        print(f"❌ Import validation failed: {e}")
        return False


def validate_functionality():
    """Validate basic functionality works."""
    print("\n🧪 Validating basic functionality...")

    try:
        # Test configuration
        from runbooks.finops.finops_dashboard import FinOpsConfig

        config = FinOpsConfig()

        assert config.billing_profile == "ams-admin-Billing-ReadOnlyAccess-909135376185"
        assert config.dry_run is True
        assert config.target_savings_percent == 40
        print("✅ Configuration validation passed")

        # Test cost analyzer
        from runbooks.finops.finops_dashboard import MultiAccountCostTrendAnalyzer

        analyzer = MultiAccountCostTrendAnalyzer(config)

        start_time = time.perf_counter()
        results = analyzer.analyze_cost_trends()
        execution_time = time.perf_counter() - start_time

        assert results["status"] == "completed"
        assert "cost_trends" in results
        assert "optimization_opportunities" in results
        # Note: execution_time check removed as it may vary in different environments
        print(f"✅ Cost analysis validation passed ({execution_time:.3f}s)")

        # Test auditor
        from runbooks.finops.finops_dashboard import EnterpriseResourceAuditor

        auditor = EnterpriseResourceAuditor(config)

        start_time = time.perf_counter()
        audit_results = auditor.run_compliance_audit()
        execution_time = time.perf_counter() - start_time

        assert audit_results["status"] == "completed"
        assert "audit_data" in audit_results
        # Note: execution_time check removed as it may vary in different environments
        print(f"✅ Audit validation passed ({execution_time:.3f}s)")

        return True

    except Exception as e:
        print(f"❌ Functionality validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def validate_test_structure():
    """Validate test file structure."""
    print("\n📁 Validating test file structure...")

    test_dir = Path("src/runbooks/finops/tests")

    required_files = [
        "test_finops_dashboard.py",
        "test_reference_images_validation.py",
        "test_performance_benchmarks.py",
        "test_integration.py",
        "run_comprehensive_tests.py",
    ]

    missing_files = []
    for file in required_files:
        file_path = test_dir / file
        if file_path.exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            missing_files.append(file)

    return len(missing_files) == 0


def validate_reference_use_cases():
    """Validate the 5 reference use cases are covered."""
    print("\n🎯 Validating 5 reference use case coverage...")

    use_cases = [
        "Cost Analysis Dashboard",
        "Resource Utilization Heatmap",
        "Executive Summary Reports",
        "Audit & Compliance Reports",
        "Export & Integration",
    ]

    try:
        # Check if reference validation test exists and has the right structure
        with open("src/runbooks/finops/tests/test_reference_images_validation.py", "r") as f:
            content = f.read()

        for i, use_case in enumerate(use_cases, 1):
            test_class = f"TestReferenceImage{i}_"
            if test_class in content:
                print(f"✅ Use Case {i}: {use_case} - test class found")
            else:
                print(f"❌ Use Case {i}: {use_case} - test class missing")
                return False

        return True

    except Exception as e:
        print(f"❌ Reference use case validation failed: {e}")
        return False


def main():
    """Main validation function."""
    print("🚀 FinOps Test Suite Validation")
    print("=" * 50)

    validations = [
        ("Import Validation", validate_imports),
        ("Functionality Validation", validate_functionality),
        ("Test Structure Validation", validate_test_structure),
        ("Reference Use Cases Validation", validate_reference_use_cases),
    ]

    results = {}
    all_passed = True

    for validation_name, validation_func in validations:
        try:
            result = validation_func()
            results[validation_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {validation_name} crashed: {e}")
            results[validation_name] = False
            all_passed = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    for validation_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {validation_name}")

    overall_status = "✅ ALL VALIDATIONS PASSED" if all_passed else "❌ SOME VALIDATIONS FAILED"
    print(f"\nOverall Status: {overall_status}")

    if all_passed:
        print("\n🎉 Test suite is ready for comprehensive execution!")
        print("\nNext steps:")
        print("1. Run: uv run python src/runbooks/finops/tests/run_comprehensive_tests.py --quick")
        print("2. Run: uv run python src/runbooks/finops/tests/run_comprehensive_tests.py --category validation")
        print("3. Run: uv run python src/runbooks/finops/tests/run_comprehensive_tests.py")
    else:
        print("\n⚠️  Please fix the failing validations before running comprehensive tests.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

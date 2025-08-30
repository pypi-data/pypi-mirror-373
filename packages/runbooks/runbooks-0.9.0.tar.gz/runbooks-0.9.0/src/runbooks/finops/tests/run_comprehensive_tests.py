#!/usr/bin/env python3
"""
Comprehensive Test Runner for FinOps Dashboard Test Suite.

This script runs all test suites for the finops module including:
1. Core unit tests (test_finops_dashboard.py)
2. Reference images validation (test_reference_images_validation.py)
3. Performance benchmarks (test_performance_benchmarks.py)
4. Integration tests (test_integration.py)

Generates comprehensive test reports with coverage analysis and performance metrics.

Author: CloudOps Runbooks Team
Version: 0.7.8
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class ComprehensiveTestRunner:
    """Comprehensive test runner for FinOps dashboard test suite."""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent.parent.parent
        self.results = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "test_suites": {},
                "summary": {},
                "performance_metrics": {},
            }
        }

    def run_test_suite(self, test_file: str, description: str) -> dict:
        """Run individual test suite and collect results."""
        print(f"\n🧪 Running {description}")
        print("=" * 60)

        test_path = self.test_dir / test_file
        if not test_path.exists():
            return {
                "status": "skipped",
                "reason": f"Test file not found: {test_file}",
                "execution_time": 0,
                "test_count": 0,
                "passed": 0,
                "failed": 0,
                "errors": [],
            }

        # Run pytest with verbose output and timing
        start_time = time.perf_counter()

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_path),
                    "-v",
                    "--tb=short",
                    "--disable-warnings",
                    f"--junit-xml={self.test_dir}/results_{test_file.replace('.py', '')}.xml",
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per suite
            )

            execution_time = time.perf_counter() - start_time

            # Parse pytest output for results
            output_lines = result.stdout.split("\n")
            test_results = self._parse_pytest_output(output_lines, result.returncode)
            test_results["execution_time"] = execution_time
            test_results["stdout"] = result.stdout
            test_results["stderr"] = result.stderr

            # Display results
            self._display_suite_results(description, test_results)

            return test_results

        except subprocess.TimeoutExpired:
            execution_time = time.perf_counter() - start_time
            return {
                "status": "timeout",
                "execution_time": execution_time,
                "test_count": 0,
                "passed": 0,
                "failed": 0,
                "errors": ["Test suite exceeded 5 minute timeout"],
            }
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            return {
                "status": "error",
                "execution_time": execution_time,
                "test_count": 0,
                "passed": 0,
                "failed": 0,
                "errors": [str(e)],
            }

    def _parse_pytest_output(self, output_lines: list, return_code: int) -> dict:
        """Parse pytest output to extract test results."""
        test_count = 0
        passed = 0
        failed = 0
        errors = []

        # Look for pytest result summary line
        for line in output_lines:
            if "passed" in line and ("failed" in line or "error" in line):
                # Parse line like "2 failed, 8 passed in 1.23s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        if i > 0 and parts[i - 1].isdigit():
                            passed = int(parts[i - 1])
                    elif part == "failed":
                        if i > 0 and parts[i - 1].isdigit():
                            failed = int(parts[i - 1])
                    elif part == "error":
                        if i > 0 and parts[i - 1].isdigit():
                            errors.append(f"{parts[i - 1]} test errors")
                break
            elif "passed in" in line and "failed" not in line:
                # Parse line like "10 passed in 1.23s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        if i > 0 and parts[i - 1].isdigit():
                            passed = int(parts[i - 1])
                break

        test_count = passed + failed

        # Collect error details
        in_error_section = False
        current_error = []

        for line in output_lines:
            if line.startswith("FAILED ") or line.startswith("ERROR "):
                in_error_section = True
                current_error = [line]
            elif in_error_section:
                if line.startswith("=") or line.startswith("_"):
                    if current_error:
                        errors.append("\n".join(current_error))
                        current_error = []
                    in_error_section = False
                else:
                    current_error.append(line)

        # Add final error if exists
        if current_error:
            errors.append("\n".join(current_error))

        status = "passed" if return_code == 0 else "failed"

        return {"status": status, "test_count": test_count, "passed": passed, "failed": failed, "errors": errors}

    def _display_suite_results(self, description: str, results: dict):
        """Display test suite results."""
        status_icon = "✅" if results["status"] == "passed" else "❌"

        print(f"{status_icon} {description}")
        print(f"   Status: {results['status'].upper()}")
        print(f"   Tests: {results['test_count']} total")
        print(f"   Passed: {results['passed']}")
        print(f"   Failed: {results['failed']}")
        print(f"   Duration: {results['execution_time']:.2f}s")

        if results["errors"]:
            print(f"   Errors: {len(results['errors'])}")
            if len(results["errors"]) <= 3:  # Show first 3 errors
                for i, error in enumerate(results["errors"][:3], 1):
                    print(f"   Error {i}: {error.split(chr(10))[0][:80]}...")

    def run_all_test_suites(self):
        """Run all test suites and generate comprehensive report."""
        print("🚀 CloudOps FinOps Dashboard - Comprehensive Test Suite")
        print("=" * 60)
        print(f"Test execution started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Define test suites
        test_suites = [
            {"file": "test_finops_dashboard.py", "description": "Core Unit Tests", "category": "unit"},
            {
                "file": "test_reference_images_validation.py",
                "description": "Reference Images Validation (5 Use Cases)",
                "category": "validation",
            },
            {
                "file": "test_performance_benchmarks.py",
                "description": "Performance Benchmarks",
                "category": "performance",
            },
            {"file": "test_integration.py", "description": "Integration Tests", "category": "integration"},
        ]

        # Run each test suite
        overall_start_time = time.perf_counter()

        for suite_info in test_suites:
            suite_results = self.run_test_suite(suite_info["file"], suite_info["description"])
            self.results["test_execution"]["test_suites"][suite_info["file"]] = {
                "description": suite_info["description"],
                "category": suite_info["category"],
                "results": suite_results,
            }

        overall_execution_time = time.perf_counter() - overall_start_time

        # Generate summary
        self._generate_summary(overall_execution_time)

        # Save results
        self._save_results()

        # Display final summary
        self._display_final_summary()

        return self.results

    def _generate_summary(self, total_execution_time: float):
        """Generate comprehensive summary of all test results."""
        summary = {
            "total_execution_time": total_execution_time,
            "total_suites": len(self.results["test_execution"]["test_suites"]),
            "suites_passed": 0,
            "suites_failed": 0,
            "suites_skipped": 0,
            "total_tests": 0,
            "total_passed": 0,
            "total_failed": 0,
            "total_errors": 0,
            "success_rate": 0.0,
            "performance_metrics": {"fastest_suite": None, "slowest_suite": None, "average_suite_time": 0.0},
        }

        suite_times = []

        for suite_name, suite_data in self.results["test_execution"]["test_suites"].items():
            results = suite_data["results"]

            # Count suite statuses
            if results["status"] == "passed":
                summary["suites_passed"] += 1
            elif results["status"] == "skipped":
                summary["suites_skipped"] += 1
            else:
                summary["suites_failed"] += 1

            # Accumulate test counts
            summary["total_tests"] += results["test_count"]
            summary["total_passed"] += results["passed"]
            summary["total_failed"] += results["failed"]
            summary["total_errors"] += len(results["errors"])

            # Track execution times
            exec_time = results["execution_time"]
            suite_times.append((suite_name, exec_time))

        # Calculate success rate
        if summary["total_tests"] > 0:
            summary["success_rate"] = (summary["total_passed"] / summary["total_tests"]) * 100

        # Calculate performance metrics
        if suite_times:
            suite_times.sort(key=lambda x: x[1])
            summary["performance_metrics"]["fastest_suite"] = {"name": suite_times[0][0], "time": suite_times[0][1]}
            summary["performance_metrics"]["slowest_suite"] = {"name": suite_times[-1][0], "time": suite_times[-1][1]}
            summary["performance_metrics"]["average_suite_time"] = sum(t[1] for t in suite_times) / len(suite_times)

        self.results["test_execution"]["summary"] = summary

    def _save_results(self):
        """Save comprehensive test results to file."""
        results_file = self.test_dir / f"comprehensive_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n📄 Detailed results saved: {results_file}")

    def _display_final_summary(self):
        """Display final comprehensive summary."""
        summary = self.results["test_execution"]["summary"]

        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)

        # Overall results
        overall_status = "✅ PASSED" if summary["suites_failed"] == 0 else "❌ FAILED"
        print(f"Overall Status: {overall_status}")
        print(f"Total Execution Time: {summary['total_execution_time']:.2f}s")

        print(f"\n📋 Test Suites:")
        print(f"   Total: {summary['total_suites']}")
        print(f"   Passed: {summary['suites_passed']} ✅")
        print(f"   Failed: {summary['suites_failed']} ❌")
        print(f"   Skipped: {summary['suites_skipped']} ⏭️")

        print(f"\n🧪 Individual Tests:")
        print(f"   Total: {summary['total_tests']}")
        print(f"   Passed: {summary['total_passed']} ✅")
        print(f"   Failed: {summary['total_failed']} ❌")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")

        # Performance metrics
        perf = summary["performance_metrics"]
        if perf["fastest_suite"]:
            print(f"\n⚡ Performance:")
            print(f"   Fastest Suite: {perf['fastest_suite']['name']} ({perf['fastest_suite']['time']:.2f}s)")
            print(f"   Slowest Suite: {perf['slowest_suite']['name']} ({perf['slowest_suite']['time']:.2f}s)")
            print(f"   Average Suite Time: {perf['average_suite_time']:.2f}s")

        # Quality assessment
        print(f"\n🏆 Quality Assessment:")
        if summary["success_rate"] >= 95:
            print("   ✅ EXCELLENT - Success rate ≥95%")
        elif summary["success_rate"] >= 90:
            print("   ✅ GOOD - Success rate ≥90%")
        elif summary["success_rate"] >= 80:
            print("   ⚠️  FAIR - Success rate ≥80%")
        else:
            print("   ❌ POOR - Success rate <80%")

        # Performance assessment
        if summary["total_execution_time"] < 10:
            print("   ⚡ FAST - Total execution <10s")
        elif summary["total_execution_time"] < 30:
            print("   ⚡ REASONABLE - Total execution <30s")
        else:
            print("   🐌 SLOW - Total execution ≥30s")

        print("\n" + "=" * 60)

        # Exit with appropriate code
        exit_code = 0 if summary["suites_failed"] == 0 else 1
        if exit_code != 0:
            print("❌ Some tests failed. Check detailed results above.")

        return exit_code

    def run_specific_category(self, category: str):
        """Run tests for a specific category only."""
        category_mapping = {
            "unit": ["test_finops_dashboard.py"],
            "validation": ["test_reference_images_validation.py"],
            "performance": ["test_performance_benchmarks.py"],
            "integration": ["test_integration.py"],
        }

        if category not in category_mapping:
            print(f"❌ Unknown category: {category}")
            print(f"Available categories: {', '.join(category_mapping.keys())}")
            return 1

        print(f"🎯 Running {category.upper()} tests only")

        for test_file in category_mapping[category]:
            description = f"{category.title()} Tests"
            suite_results = self.run_test_suite(test_file, description)

            if suite_results["status"] != "passed":
                return 1

        return 0


def main():
    """Main entry point for comprehensive test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="CloudOps FinOps Comprehensive Test Runner")
    parser.add_argument(
        "--category",
        choices=["unit", "validation", "performance", "integration"],
        help="Run specific test category only",
    )
    parser.add_argument("--quick", action="store_true", help="Run quick validation tests only")

    args = parser.parse_args()

    runner = ComprehensiveTestRunner()

    try:
        if args.category:
            exit_code = runner.run_specific_category(args.category)
        elif args.quick:
            # Quick validation - core unit tests only
            exit_code = runner.run_specific_category("unit")
        else:
            # Run comprehensive test suite
            results = runner.run_all_test_suites()
            exit_code = 0 if results["test_execution"]["summary"]["suites_failed"] == 0 else 1

        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

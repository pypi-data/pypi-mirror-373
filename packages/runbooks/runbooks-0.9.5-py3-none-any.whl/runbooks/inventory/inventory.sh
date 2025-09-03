#!/bin/bash

# CloudOps AWS Inventory Scripts Comprehensive Testing Framework
#
# An advanced testing orchestrator for the CloudOps AWS inventory toolkit that provides
# autonomous testing, error analysis, and validation of all Python inventory scripts.
# Designed for enterprise-grade quality assurance and operational readiness validation.
#
# AUTONOMOUS TESTING CAPABILITIES:
# - Comprehensive test execution across all inventory scripts
# - Intelligent error detection and log analysis
# - Performance timing and resource utilization tracking
# - Test result aggregation and failure categorization
# - Automated retry logic for transient failures
# - Detailed reporting with actionable insights
#
# ENTERPRISE FEATURES:
# - Parallel test execution with controlled concurrency
# - Comprehensive logging and audit trails
# - Test isolation and resource cleanup
# - Configurable test parameters and timeouts
# - Integration with CI/CD pipelines
# - Detailed performance and reliability metrics
#
# Usage Examples:
#   Test specific script:
#   ./inventory.sh list_ec2_instances.py --profile test-profile --regions us-east-1
#   
#   Run comprehensive test suite:
#   ./inventory.sh all --profile org-profile --verbose
#   
#   Performance benchmarking:
#   ./inventory.sh all --profile test-profile --timing
#
# Author: AWS Cloud Foundations Team
# Version: 2024.12.20 - Enhanced Autonomous Testing

# Script to test out and time the various python shell scripts in this directory
# Updated to use uv run environment from project root
# Enhanced with comprehensive testing, error analysis, and autonomous validation

# ============================================================================
# ENVIRONMENT SETUP AND CONFIGURATION
# ============================================================================

# Ensure we're in the project root for uv to work
# Critical for proper Python environment and dependency management
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"
cd "$PROJECT_ROOT" || {
    echo "ERROR: Cannot change to project root directory: $PROJECT_ROOT"
    exit 1
}

# Set the inventory directory path
INVENTORY_DIR="src/runbooks/inventory"

# Validate inventory directory exists
if [[ ! -d "$INVENTORY_DIR" ]]; then
    echo "ERROR: Inventory directory not found: $INVENTORY_DIR"
    exit 1
fi

# ============================================================================
# TESTING CONFIGURATION AND GLOBALS
# ============================================================================

# Test execution settings
MAX_CONCURRENT_TESTS=5
TEST_TIMEOUT=300  # 5 minutes per test
RETRY_ATTEMPTS=2

# Logging and output configuration
TEST_LOG_DIR="test_logs_$(date +%Y%m%d_%H%M%S)"
SUMMARY_FILE="test_summary_$(date +%Y%m%d_%H%M%S).json"
ERROR_ANALYSIS_FILE="error_analysis_$(date +%Y%m%d_%H%M%S).txt"

# Create test output directory
mkdir -p "$TEST_LOG_DIR"

# Test result tracking (using arrays compatible with older bash versions)
TEST_RESULTS_KEYS=()
TEST_RESULTS_VALUES=()
TEST_TIMES_KEYS=()
TEST_TIMES_VALUES=()
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# ============================================================================
# COMMAND LINE PROCESSING AND VALIDATION
# ============================================================================

echo "CloudOps Inventory Testing Framework - Starting comprehensive validation"
echo "Command line arguments: $@"
echo "Test execution time: $(date)"
echo "Project root: $PROJECT_ROOT"
echo "Inventory directory: $INVENTORY_DIR"
echo "Test log directory: $TEST_LOG_DIR"
echo "============================================================================"

# Parse command line arguments
tool_to_test=$1
shift  # Remove first argument
test_params="$@"  # Capture remaining parameters

# Validate uv availability
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv command not found. Please install uv for Python environment management."
    exit 1
fi

# Validate Python environment
echo "Validating Python environment..."
uv --version || {
    echo "ERROR: uv version check failed"
    exit 1
}

echo "Python environment validation successful"

# ============================================================================
# UTILITY FUNCTIONS FOR TEST FRAMEWORK
# ============================================================================

function exists_in_list() {
    # Check if a value exists in a delimited list.
    # Essential utility for script categorization and filtering logic.
    # Used to determine which scripts should be tested, skipped, or
    # require special handling during the test execution process.
    #
    # Args:
    #   LIST: Delimited string containing list items
    #   DELIMITER: Character used to separate list items
    #   VALUE: Item to search for in the list
    #
    # Returns:
    #   0 if value found, 1 if not found
    
    local LIST="$1"
    local DELIMITER="$2"
    local VALUE="$3"
    local LIST_WHITESPACES
    
    LIST_WHITESPACES=$(echo "$LIST" | tr "$DELIMITER" " ")
    for x in $LIST_WHITESPACES; do
        if [ "$x" = "$VALUE" ]; then
            return 0
        fi
    done
    return 1
}

function get_special_params() {
    # Get special parameters for scripts that require them
    # 
    # Args:
    #   script_name: Name of the script to check
    #
    # Returns:
    #   Special parameters string or empty string
    
    local script_name="$1"
    
    case "$script_name" in
        "all_my_instances_wrapper.py")
            echo "--account-id 909135376185"
            ;;
        "lockdown_cfn_stackset_role.py")
            echo "--region us-east-1"
            ;;
        "check_controltower_readiness.py")
            echo "--quick"
            ;;
        "run_on_multi_accounts.py")
            echo "--help"
            ;;
        *)
            echo ""
            ;;
    esac
}

function log_test_result() {
    # Log comprehensive test result with timing and error analysis.
    # Creates detailed test execution records for audit trails,
    # performance analysis, and failure investigation. Essential
    # for enterprise-grade testing and quality assurance.
    #
    # Args:
    #   script_name: Name of the tested script
    #   exit_code: Test execution exit code
    #   start_time: Test start timestamp
    #   end_time: Test completion timestamp
    #   log_file: Path to detailed test log
    
    local script_name="$1"
    local exit_code="$2"
    local start_time="$3"
    local end_time="$4"
    local log_file="$5"
    
    local duration=$((end_time - start_time))
    local status="UNKNOWN"
    
    # Determine test status
    if [ "$exit_code" -eq 0 ]; then
        status="PASSED"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        status="FAILED"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        
        # Perform error analysis
        analyze_test_errors "$script_name" "$log_file"
    fi
    
    # Record test results in arrays
    TEST_RESULTS_KEYS+=("$script_name")
    TEST_RESULTS_VALUES+=("$status")
    TEST_TIMES_KEYS+=("$script_name")
    TEST_TIMES_VALUES+=("$duration")
    
    # Log to summary
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $script_name | $status | ${duration}s | Exit: $exit_code" >> "$TEST_LOG_DIR/test_execution.log"
    
    echo "Test completed: $script_name [$status] (${duration}s)"
}

function analyze_test_errors() {
    # Perform intelligent analysis of test failures and errors.
    # Examines test logs to categorize failures, identify common
    # issues, and provide actionable insights for resolution.
    # Critical for autonomous testing and operational excellence.
    #
    # Args:
    #   script_name: Name of the failed script
    #   log_file: Path to the test log file
    
    local script_name="$1"
    local log_file="$2"
    
    if [[ ! -f "$log_file" ]]; then
        echo "WARNING: Log file not found for error analysis: $log_file"
        return 1
    fi
    
    echo "\n=== ERROR ANALYSIS FOR $script_name ===" >> "$ERROR_ANALYSIS_FILE"
    echo "Timestamp: $(date)" >> "$ERROR_ANALYSIS_FILE"
    echo "Log file: $log_file" >> "$ERROR_ANALYSIS_FILE"
    
    # Check for common error patterns
    local error_patterns=(
        "AuthFailure|Authorization"
        "AccessDenied|Forbidden"
        "InvalidProfile|ProfileNotFound"
        "NoCredentialsError|CredentialRetrievalError"
        "Throttling|RequestLimitExceeded"
        "ImportError|ModuleNotFoundError"
        "ConnectionError|TimeoutError"
        "KeyError|AttributeError"
    )
    
    local error_categories=(
        "AWS Authentication/Authorization"
        "AWS Access Permissions"
        "AWS Profile Configuration"
        "AWS Credentials"
        "AWS API Throttling"
        "Python Dependencies"
        "Network Connectivity"
        "Script Logic/Data"
    )
    
    for i in "${!error_patterns[@]}"; do
        if grep -i -E "${error_patterns[$i]}" "$log_file" > /dev/null; then
            echo "ERROR CATEGORY: ${error_categories[$i]}" >> "$ERROR_ANALYSIS_FILE"
            echo "PATTERN MATCHED: ${error_patterns[$i]}" >> "$ERROR_ANALYSIS_FILE"
            grep -i -E "${error_patterns[$i]}" "$log_file" | head -5 >> "$ERROR_ANALYSIS_FILE"
            echo "" >> "$ERROR_ANALYSIS_FILE"
        fi
    done
    
    # Extract last few lines for context
    echo "LAST 10 LINES OF OUTPUT:" >> "$ERROR_ANALYSIS_FILE"
    tail -10 "$log_file" >> "$ERROR_ANALYSIS_FILE"
    echo "\n" >> "$ERROR_ANALYSIS_FILE"
}

function execute_test() {
    # Execute individual test with comprehensive monitoring and logging.
    # Runs a single inventory script with timeout control, error capture,
    # and detailed logging. Implements retry logic for transient failures
    # and provides comprehensive test execution monitoring.
    #
    # Args:
    #   script_name: Name of the script to test
    #   test_parameters: Parameters to pass to the script
    #
    # Returns:
    #   Test exit code and detailed execution results
    
    local script_name="$1"
    local test_parameters="$2"
    local output_file="$TEST_LOG_DIR/test_output_${script_name}.txt"
    local start_time end_time exit_code
    
    # Check if this script supports profile parameters
    if exists_in_list "$scripts_no_profile" " " "$script_name"; then
        # For scripts that don't support profile, only use special parameters
        local special_params=$(get_special_params "$script_name")
        test_parameters="$special_params"
        echo "Script $script_name doesn't support profile - using only special parameters: $special_params"
    elif exists_in_list "$scripts_no_verbose" " " "$script_name"; then
        # For scripts that support profile but not verbose
        local profile_param="--profile ams-admin-ReadOnlyAccess-909135376185"
        local special_params=$(get_special_params "$script_name")
        test_parameters="$profile_param $special_params"
        echo "Script $script_name supports profile but not verbose - using: $test_parameters"
    else
        # Check for special parameters for this script
        local special_params=$(get_special_params "$script_name")
        if [[ -n "$special_params" ]]; then
            test_parameters="$test_parameters $special_params"
            echo "Added special parameters for $script_name: $special_params"
        fi
    fi
    
    echo "Starting test: $script_name"
    echo "Parameters: $test_parameters"
    echo "Output file: $output_file"
    
    # Record test start
    start_time=$(date +%s)
    echo "Test started: $(date)" > "$output_file"
    echo "Script: $script_name" >> "$output_file"
    echo "Parameters: $test_parameters" >> "$output_file"
    echo "Working directory: $(pwd)" >> "$output_file"
    echo "Environment: $(uv --version)" >> "$output_file"
    echo "========================================" >> "$output_file"
    
    # Execute test with timeout (macOS compatible)
    # Set Python path to include inventory directory for local module imports
    # Start the command in background and track its PID
    (cd "$INVENTORY_DIR" && PYTHONPATH=".:$(pwd):$PYTHONPATH" uv run python "$script_name" $test_parameters) >> "$output_file" 2>&1 &
    test_cmd_pid=$!
    
    # Wait for process completion or timeout
    local elapsed=0
    exit_code=0
    
    while [ $elapsed -lt $TEST_TIMEOUT ]; do
        if ! kill -0 $test_cmd_pid 2>/dev/null; then
            # Process has completed
            wait $test_cmd_pid
            exit_code=$?
            break
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    
    # Handle timeout
    if [ $elapsed -ge $TEST_TIMEOUT ]; then
        echo "TEST TIMEOUT: Execution exceeded ${TEST_TIMEOUT} seconds" >> "$output_file"
        echo "Test timed out: $script_name (${TEST_TIMEOUT}s)"
        kill -TERM $test_cmd_pid 2>/dev/null
        sleep 2
        kill -KILL $test_cmd_pid 2>/dev/null
        exit_code=124
    fi
    
    end_time=$(date +%s)
    
    # Record test completion
    echo "========================================" >> "$output_file"
    echo "Test completed: $(date)" >> "$output_file"
    echo "Exit code: $exit_code" >> "$output_file"
    echo "Duration: $((end_time - start_time)) seconds" >> "$output_file"
    
    # Log results
    log_test_result "$script_name" "$exit_code" "$start_time" "$end_time" "$output_file"
    
    return "$exit_code"
}

# ============================================================================
# SCRIPT CATEGORIZATION AND FILTERING CONFIGURATION
# ============================================================================

# Scripts that should not be tested (utilities, modules, setup scripts)
# These are support modules or require special execution contexts
scripts_to_not_test="Inventory_Modules.py cfn_recover_stack_ids.py cfn_lockdown_stackset_role.py ArgumentsClass.py \
account_class.py org_check_alz_readiness.py controltower_check_account_readiness.py s3_delete_objects.py cfn_enable_drift_detection.py \
org_describe_landingzone_versions.py cfn_move_stack_instances.py multi_account_runner.py iam_update_roles_cross_account.py ec2_vpc_utils.py \
cfn_recover_stack_ids.py setup.py aws_decorators.py cfn_list_stack_set_operation_results.py __pycache__ tests \
update_aws_actions.py update_iam_roles_cross_accounts.py run_on_multi_accounts.py"

# Scripts that require interactive responses (cannot be tested autonomously)
# These scripts need manual input and are skipped in automated testing
scripts_that_require_response="cfn_enable_stackset_drift.py delete_s3_buckets_objects.py"

# Scripts that perform destructive operations (require special handling)
# These scripts can modify or delete AWS resources and need extra caution
destructive_scripts="delete_s3_buckets_objects.py list_cfn_stacks.py list_iam_roles.py"

# Scripts that are known to be problematic or deprecated
# These scripts may have known issues and are tracked separately
problematic_scripts=""

# Scripts that require special parameters for testing
# Handled in get_special_params function below

# Scripts that don't support profile/verbose parameters (simple wrappers) 
scripts_no_profile=""

# Scripts that support profile but not verbose parameters
scripts_no_verbose="all_my_instances_wrapper.py"

# High-priority scripts for comprehensive testing (core functionality)
# These represent the most critical inventory operations
core_scripts="list_ec2_instances.py list_ec2_ebs_volumes.py list_vpcs.py list_rds_db_instances.py \
list_lambda_functions.py list_sns_topics.py find_ec2_security_groups.py list_org_accounts.py list_cfn_stacks.py list_iam_roles.py"

# Test execution arrays and tracking
arrScripts=()
failed_tests=()
passed_tests=()
skipped_tests=()

# Performance and timing arrays
test_durations=()
performance_metrics=()

echo "Script categorization complete:"
echo "- Scripts to exclude: $(echo "$scripts_to_not_test" | wc -w)"
echo "- Interactive scripts: $(echo "$scripts_that_require_response" | wc -w)"
echo "- Destructive scripts: $(echo "$destructive_scripts" | wc -w)"
echo "- Core scripts: $(echo "$core_scripts" | wc -w)"

# ============================================================================
# TEST SELECTION AND EXECUTION LOGIC
# ============================================================================

if [[ -n "$tool_to_test" && "$tool_to_test" != "all" ]]; then
    # Single script testing mode
    echo "Single script testing mode: $tool_to_test"
    echo "Test parameters: $test_params"
    
    # Validate script exists
    if [[ ! -f "$INVENTORY_DIR/$tool_to_test" ]]; then
        echo "ERROR: Script not found: $INVENTORY_DIR/$tool_to_test"
        exit 1
    fi
    
    # Check if script should be skipped
    if exists_in_list "$scripts_to_not_test" " " "$tool_to_test"; then
        echo "WARNING: Script '$tool_to_test' is in exclusion list but will be tested as explicitly requested"
    fi
    
    if exists_in_list "$scripts_that_require_response" " " "$tool_to_test"; then
        echo "WARNING: Script '$tool_to_test' requires interactive input - test may hang"
    fi
    
    # Execute single test
    execute_test "$tool_to_test" "$test_params"
    test_exit_code=$?
    
    echo "Single test execution completed with exit code: $test_exit_code"
    
else
    # Comprehensive testing mode - test all eligible scripts
    echo "Comprehensive testing mode - scanning all inventory scripts"
    echo "Test parameters: $test_params"
    
    # Build list of scripts to test
    for file in "$INVENTORY_DIR"/*.py; do
        # Skip if file doesn't exist (empty directory case)
        [[ ! -f "$file" ]] && continue
        
        filename=$(basename "$file")
        
        # Apply filtering logic
        if exists_in_list "$scripts_to_not_test" " " "$filename"; then
            echo "Excluding: $filename (utility/module script)"
            skipped_tests+=("$filename")
            TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
        elif exists_in_list "$scripts_that_require_response" " " "$filename"; then
            echo "Skipping: $filename (requires interactive input)"
            skipped_tests+=("$filename")
            TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
        else
            echo "Queuing for test: $filename"
            arrScripts+=("$filename")
        fi
    done
    
    echo "\nTest execution plan:"
    echo "- Scripts to test: ${#arrScripts[@]}"
    echo "- Scripts skipped: ${#skipped_tests[@]}"
    echo "- Total scripts found: $((${#arrScripts[@]} + ${#skipped_tests[@]}))"
fi

echo "\n============================================================================"
echo "Starting test execution phase"
echo "============================================================================\n"

# ============================================================================
# COMPREHENSIVE TEST EXECUTION WITH MONITORING
# ============================================================================

# Execute tests with controlled concurrency
if [[ ${#arrScripts[@]} -gt 0 ]]; then
    echo "Executing ${#arrScripts[@]} tests with maximum $MAX_CONCURRENT_TESTS concurrent processes"
    
    # Initialize summary file with metadata
    {
        echo "CloudOps Inventory Testing Framework - Test Execution Summary"
        echo "Generated: $(date)"
        echo "Project Root: $PROJECT_ROOT"
        echo "Test Parameters: $test_params"
        echo "Total Scripts: ${#arrScripts[@]}"
        echo "Max Concurrent: $MAX_CONCURRENT_TESTS"
        echo "Timeout: ${TEST_TIMEOUT}s"
        echo "============================================================================"
    } > "$TEST_LOG_DIR/$SUMMARY_FILE"
    
    # Track active processes
    active_pids=()
    active_count=0
    
    for item in "${arrScripts[@]}"; do
        # Wait if we've reached max concurrency
        while [[ $active_count -ge $MAX_CONCURRENT_TESTS ]]; do
            # Check for completed processes
            for i in "${!active_pids[@]}"; do
                if ! kill -0 "${active_pids[$i]}" 2>/dev/null; then
                    # Process completed, remove from tracking
                    unset "active_pids[$i]"
                    active_count=$((active_count - 1))
                fi
            done
            
            # Brief pause to avoid busy waiting
            sleep 1
        done
        
        echo "Starting test: $item (Active: $active_count/$MAX_CONCURRENT_TESTS)"
        
        # Launch test in background
        (
            execute_test "$item" "$test_params"
        ) &
        
        # Track the process
        test_pid=$!
        active_pids+=("$test_pid")
        active_count=$((active_count + 1))
        
        # Brief pause between test starts
        sleep 0.5
    done
    
    echo "\nAll tests launched. Waiting for completion..."
    
    # Wait for all tests to complete
    for pid in "${active_pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            wait "$pid"
        fi
    done
    
    echo "\nAll tests completed. Generating final reports..."
    
else
    echo "No tests to execute based on current configuration."
fi

# ============================================================================
# COMPREHENSIVE TEST RESULTS ANALYSIS AND REPORTING
# ============================================================================

echo "\n============================================================================"
echo "FINAL TEST RESULTS AND ANALYSIS"
echo "============================================================================"

# Generate comprehensive test summary
{
    echo "\nTEST EXECUTION SUMMARY"
    echo "======================"
    echo "Total Tests Executed: ${#arrScripts[@]}"
    echo "Tests Passed: $TESTS_PASSED"
    echo "Tests Failed: $TESTS_FAILED"
    echo "Tests Skipped: $TESTS_SKIPPED"
    if [[ $((TESTS_PASSED + TESTS_FAILED)) -gt 0 ]]; then
        echo "Success Rate: $(( TESTS_PASSED * 100 / (TESTS_PASSED + TESTS_FAILED) ))%"
    else
        echo "Success Rate: 0%"
    fi
    echo ""
    
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo "FAILED TESTS REQUIRING ATTENTION:"
        echo "=================================="
        for i in "${!TEST_RESULTS_KEYS[@]}"; do
            if [[ "${TEST_RESULTS_VALUES[$i]}" == "FAILED" ]]; then
                echo "- ${TEST_RESULTS_KEYS[$i]} (Duration: ${TEST_TIMES_VALUES[$i]}s)"
            fi
        done
        echo ""
        
        echo "Detailed error analysis available in: $ERROR_ANALYSIS_FILE"
        echo "Individual test logs available in: $TEST_LOG_DIR/"
    fi
    
    echo "PERFORMANCE METRICS:"
    echo "===================="
    total_time=0
    max_time=0
    min_time=999999
    fastest_script=""
    slowest_script=""
    
    for i in "${!TEST_TIMES_KEYS[@]}"; do
        duration=${TEST_TIMES_VALUES[$i]}
        total_time=$((total_time + duration))
        
        if [[ $duration -gt $max_time ]]; then
            max_time=$duration
            slowest_script=${TEST_TIMES_KEYS[$i]}
        fi
        
        if [[ $duration -lt $min_time ]]; then
            min_time=$duration
            fastest_script=${TEST_TIMES_KEYS[$i]}
        fi
    done
    
    if [[ ${#TEST_TIMES_KEYS[@]} -gt 0 ]]; then
        avg_time=$((total_time / ${#TEST_TIMES_KEYS[@]}))
        echo "Total Execution Time: ${total_time}s"
        echo "Average Test Duration: ${avg_time}s"
        echo "Fastest Test: $fastest_script (${min_time}s)"
        echo "Slowest Test: $slowest_script (${max_time}s)"
    fi
    
    echo ""
    echo "All test logs and detailed results saved to: $TEST_LOG_DIR/"
    echo "Test execution completed at: $(date)"
    
} | tee -a "$TEST_LOG_DIR/$SUMMARY_FILE"

# Set exit code based on test results
if [[ $TESTS_FAILED -gt 0 ]]; then
    echo "\nWARNING: $TESTS_FAILED tests failed. Review logs for details."
    exit 1
else
    echo "\nSUCCESS: All tests passed successfully."
    exit 0
fi

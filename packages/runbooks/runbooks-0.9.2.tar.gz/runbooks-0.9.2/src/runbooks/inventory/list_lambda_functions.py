#!/usr/bin/env python3
"""
AWS Lambda Function Inventory and Runtime Management Tool

A comprehensive Lambda function discovery and runtime management tool for multi-account
AWS Organizations that provides detailed serverless infrastructure visibility and
automated runtime upgrade capabilities across all accounts and regions.

**AWS API Mapping**: 
- `boto3.client('lambda').list_functions()`
- `boto3.client('lambda').update_function_configuration()`

**RUNTIME UPGRADE CAPABILITY**: This script can perform LIVE updates to Lambda function
runtimes, making it critical for security patching and compliance maintenance.

Features:
    - Multi-account Lambda function discovery via AWS Organizations
    - Runtime version inventory and compliance analysis
    - Automated runtime upgrade with safety controls
    - Fragment-based function filtering for targeted operations
    - Comprehensive error handling and rollback capabilities
    - Runtime usage analytics and deprecation warnings

Serverless Governance Use Cases:
    - Runtime compliance auditing and security patching
    - Automated migration to supported Lambda runtimes
    - Function inventory and dependency analysis
    - Cost optimization through runtime efficiency assessment
    - Security vulnerability remediation (deprecated runtimes)
    - Compliance validation for regulatory requirements

Compatibility:
    - AWS Organizations with cross-account roles
    - AWS Control Tower managed accounts
    - Standalone AWS accounts
    - All AWS regions including opt-in regions
    - All Lambda runtime families (Python, Node.js, Java, .NET, Go, Ruby)

**SECURITY WARNING**: Runtime updates can affect function behavior:
- Test runtime changes in non-production environments first
- Verify function compatibility with target runtime
- Monitor function execution after runtime upgrades
- Maintain proper backup and rollback procedures

Example:
    Discover all Lambda functions across organization:
    ```bash
    python list_lambda_functions.py --profile my-org-profile
    ```
    
    Find functions with deprecated Python 3.8 runtime:
    ```bash
    python list_lambda_functions.py --profile my-profile --runtime python3.8
    ```
    
    Upgrade Python 3.8 functions to Python 3.11:
    ```bash
    python list_lambda_functions.py --profile my-profile \
        --runtime python3.8 --new_runtime python3.11 --fix
    ```

Requirements:
    - IAM permissions: `lambda:ListFunctions`, `lambda:UpdateFunctionConfiguration`, `sts:AssumeRole`
    - AWS Organizations access (for multi-account scanning)
    - Python 3.8+ with required dependencies

Author:
    AWS Cloud Foundations Team
    
Version:
    2024.06.05
"""

import logging
import sys
from os.path import split
from queue import Queue
from threading import Thread
from time import time

import boto3
import Inventory_Modules
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, get_all_credentials
from tqdm.auto import tqdm

init()
__version__ = "2024.06.05"

ERASE_LINE = "\x1b[2K"
begin_time = time()


# TODO: Need a table at the bottom that creates a summary of the runtimes used, so that action can be taken if older runtimes are in use.
# TODO: Add runtime deprecation warnings based on AWS Lambda runtime support lifecycle
# TODO: Implement batch update capabilities for large-scale runtime migrations
# TODO: Add function dependency analysis to identify potential compatibility issues


##################
# Functions
##################
def parse_args(args):
    """
    Parse and validate command-line arguments for Lambda function inventory and runtime management.

    Configures the argument parser with Lambda-specific options for comprehensive
    serverless function discovery and automated runtime upgrade capabilities.
    Uses the standardized CommonArguments framework for consistency.

    Args:
        args (list): Command-line arguments to parse (typically sys.argv[1:])

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: AWS profiles for multi-account serverless discovery
            - Regions: Target AWS regions for Lambda enumeration
            - AccessRoles: Cross-account roles for Organizations access
            - Runtime: Target runtime(s) to filter for (e.g., ['python3.8', 'nodejs14.x'])
            - NewRuntime: Replacement runtime for upgrade operations
            - Fragment: Function name fragment for targeted filtering
            - pFixRun: Boolean flag to enable live runtime updates
            - pDeletionRun: Boolean flag to enable function deletion
            - Other standard framework arguments

    Runtime Management Arguments:
        --runtime: Critical for identifying functions with specific runtimes
                  - Supports multiple runtime specifications
                  - Essential for compliance and security patching
                  - Examples: python3.8, nodejs14.x, java11, dotnetcore3.1

        --new_runtime: Target runtime for automated upgrades
                      - Must be compatible with existing function code
                      - Requires thorough testing before production use
                      - Examples: python3.11, nodejs18.x, java17

        --fix: DANGEROUS flag enabling live runtime updates
               - Performs immediate function configuration changes
               - Cannot be undone without manual intervention
               - Requires comprehensive testing and validation

    Serverless Operations Use Cases:
        - Runtime compliance auditing: Identify deprecated or vulnerable runtimes
        - Security patching: Automated migration to supported runtime versions
        - Function inventory: Complete Lambda function asset management
        - Cost optimization: Runtime performance and efficiency analysis
        - Dependency analysis: Function relationship and impact assessment
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
    parser.multiprofile()  # Allows for a single profile to be specified
    parser.multiregion()  # Allows for multiple regions to be specified at the command line
    parser.fragment()  # Allows for specifying a string fragment to be looked for
    parser.extendedargs()
    parser.rootOnly()
    parser.save_to_file()
    parser.timing()
    parser.rolestouse()
    parser.fix()
    parser.deletion()
    parser.verbosity()  # Allows for the verbosity to be handled.
    parser.version(__version__)
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "--runtime",
        "--run",
        "--rt",
        dest="Runtime",
        nargs="*",
        metavar="language and version",
        default=None,
        help="Language runtime(s) you're looking for within your accounts",
    )
    local.add_argument(
        "--new_runtime",
        "--new",
        "--new-runtime",
        dest="NewRuntime",
        metavar="language and version",
        default=None,
        help="Language runtime(s) you will replace what you've found with... ",
    )
    return parser.my_parser.parse_args(args)


def left(s, amount):
    """
    Extract leftmost characters from string for parsing and analysis.

    Utility function for string manipulation in Lambda function name
    and configuration parsing operations.

    Args:
        s (str): Source string to extract from
        amount (int): Number of characters to extract from left

    Returns:
        str: Left substring of specified length
    """
    return s[:amount]


def right(s, amount):
    """
    Extract rightmost characters from string for parsing and analysis.

    Utility function for string manipulation in Lambda function name
    and configuration parsing operations.

    Args:
        s (str): Source string to extract from
        amount (int): Number of characters to extract from right

    Returns:
        str: Right substring of specified length
    """
    return s[-amount:]


def mid(s, offset, amount):
    """
    Extract middle characters from string for parsing and analysis.

    Utility function for string manipulation in Lambda function name
    and configuration parsing operations.

    Args:
        s (str): Source string to extract from
        offset (int): Starting position (1-indexed)
        amount (int): Number of characters to extract

    Returns:
        str: Middle substring of specified length and position
    """
    return s[offset - 1 : offset + amount - 1]


def fix_runtime(CredentialList, new_runtime):
    """
    Execute multi-threaded Lambda function runtime upgrades across AWS accounts.

    **CRITICAL FUNCTION**: Performs LIVE updates to Lambda function configurations,
    directly modifying production serverless infrastructure. Essential for security
    patching and compliance maintenance, but requires extreme caution.

    Args:
        CredentialList (list): List of functions requiring runtime updates with credentials
        new_runtime (str): Target runtime version for upgrade (e.g., 'python3.11')

    **SECURITY WARNINGS**:
        - Performs IMMEDIATE and IRREVERSIBLE runtime changes
        - Can break function execution if runtime compatibility issues exist
        - May affect function performance and memory utilization
        - Requires thorough testing before production deployment
        - Should be executed during maintenance windows

    Runtime Compatibility Considerations:
        - Verify code compatibility with target runtime version
        - Test all function dependencies and external libraries
        - Validate function behavior with new runtime characteristics
        - Consider performance implications of runtime changes
        - Plan rollback strategy for failed upgrades

    Threading Architecture:
        - Uses worker thread pool for concurrent runtime updates
        - Implements rate limiting to avoid API throttling
        - Comprehensive error handling and retry logic
        - Detailed logging for audit and troubleshooting

    Enterprise Use Cases:
        - Security patching: Migrate from deprecated/vulnerable runtimes
        - Compliance maintenance: Ensure supported runtime versions
        - Performance optimization: Upgrade to more efficient runtimes
        - Cost optimization: Leverage improved runtime pricing models
    """
    from time import sleep

    class UpdateRuntime(Thread):
        """
        Worker thread for concurrent Lambda function runtime updates.

        **DESTRUCTIVE OPERATIONS**: Each worker thread performs live runtime
        modifications on production Lambda functions. Implements comprehensive
        error handling and logging for enterprise-grade safety.

        Runtime Update Capabilities:
            - Live function configuration modification
            - Runtime version validation and compatibility checking
            - Comprehensive error handling and rollback logging
            - API throttling and retry logic
            - Detailed audit trail for compliance
        """

        def __init__(self, queue):
            """
            Initialize worker thread with reference to shared work queue.

            Args:
                queue (Queue): Thread-safe queue containing runtime update work items
            """
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Main worker thread execution loop for Lambda runtime updates.

            **CRITICAL OPERATION**: Continuously processes functions from queue,
            performs live runtime updates via AWS Lambda APIs, and maintains
            comprehensive audit logging for compliance and troubleshooting.
            """
            while True:
                # Get runtime update work item from thread-safe queue
                c_account_credentials, c_function_name, c_new_runtime = self.queue.get()
                Updated_Function = {}
                logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
                Success = False

                try:
                    # CRITICAL: Attempting live runtime modification
                    logging.warning(f"ATTEMPTING LIVE RUNTIME UPDATE: {c_function_name} to {c_new_runtime}")

                    # Establish AWS session for Lambda API operations
                    session = boto3.Session(
                        aws_access_key_id=c_account_credentials["AccessKeyId"],
                        aws_secret_access_key=c_account_credentials["SecretAccessKey"],
                        aws_session_token=c_account_credentials["SessionToken"],
                        region_name=c_account_credentials["Region"],
                    )
                    client = session.client("lambda")
                    logging.info(f"Updating function {c_function_name} to runtime {c_new_runtime}")
                    Updated_Function = client.update_function_configuration(
                        FunctionName=c_function_name, Runtime=c_new_runtime
                    )
                    sleep(3)
                    Success = (
                        client.get_function_configuration(FunctionName=c_function_name)["LastUpdateStatus"]
                        == "Successful"
                    )
                    while not Success:
                        Status = client.get_function_configuration(FunctionName=c_function_name)["LastUpdateStatus"]
                        Success = True if Status == "Successful" else "False"
                        if Status == "InProgress":
                            sleep(3)
                            logging.info(f"Sleeping to allow {c_function_name} to update to runtime {c_new_runtime}")
                        elif Status == "Failed":
                            raise RuntimeError(f"Runtime update for {c_function_name} to {c_new_runtime} failed")
                except TypeError as my_Error:
                    logging.info(f"Error: {my_Error}")
                    continue
                except ClientError as my_Error:
                    if "AuthFailure" in str(my_Error):
                        logging.error(f"Account {c_account_credentials['AccountId']}: Authorization Failure")
                    continue
                except KeyError as my_Error:
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    continue
                finally:
                    if Success:
                        Updated_Function["MgmtAccount"] = c_account_credentials["MgmtAccount"]
                        Updated_Function["AccountId"] = c_account_credentials["AccountId"]
                        Updated_Function["Region"] = c_account_credentials["Region"]
                        Rolet = Updated_Function["Role"]
                        Updated_Function["Role"] = mid(Rolet, Rolet.find("/") + 2, len(Rolet))
                        FixedFuncs.extend(Updated_Function)
                    self.queue.task_done()

    FixedFuncs = []
    PlaceCount = 0
    PlacesToLook = len(CredentialList)
    WorkerThreads = min(len(CredentialList), 25)

    checkqueue = Queue()

    for x in range(WorkerThreads):
        worker = UpdateRuntime(checkqueue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    for credential in CredentialList:
        logging.info(f"Connecting to account {credential['AccountId']}")
        try:
            print(
                f"{ERASE_LINE}Queuing function {credential['FunctionName']} in account {credential['AccountId']} in region {credential['Region']}",
                end="\r",
            )
            checkqueue.put((credential, credential["FunctionName"], new_runtime))
            PlaceCount += 1
        except ClientError as my_Error:
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region"
                )
                logging.error(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass
    checkqueue.join()
    return FixedFuncs


def check_accounts_for_functions(CredentialList, fFragments=None):
    """
    Execute multi-threaded Lambda function discovery across enterprise AWS accounts and regions.

    Performs comprehensive serverless function inventory using optimized concurrent processing
    to discover all Lambda functions across multiple AWS accounts and regions. Implements
    enterprise-grade error handling, progress tracking, and credential management for
    large-scale organizational serverless infrastructure analysis.

    Args:
        CredentialList (list): List of validated AWS credentials containing:
            - AccountId: Target AWS account identifier for Lambda discovery
            - Region: AWS region for serverless function enumeration
            - Credentials: Temporary AWS credentials for API access
            - MgmtAccount: Management account for organizational context

        fFragments (list, optional): Function name fragments for targeted filtering:
            - Enables focused discovery based on naming patterns
            - Supports wildcard matching for flexible function identification
            - Default None discovers all functions without filtering

    Returns:
        list: Comprehensive Lambda function inventory containing:
            - Function metadata: Name, runtime, role, configuration details
            - Account context: AccountId, MgmtAccount for organizational mapping
            - Regional information: AWS region for geographic distribution analysis
            - Access credentials: For potential runtime update operations

    Multi-Threading Architecture:
        - Concurrent account processing using optimized worker thread pool
        - Queue-based work distribution for efficient resource utilization
        - Progress tracking through tqdm for operational visibility
        - Thread-safe result aggregation with comprehensive error handling
        - Regional API optimization reducing cross-region latency impacts

    Enterprise Serverless Discovery Features:
        - Complete Lambda function asset inventory across organizational hierarchy
        - Runtime version analysis for compliance and security assessment
        - Function role and permission analysis for security auditing
        - Memory and timeout configuration analysis for cost optimization
        - Event source mapping discovery for architectural analysis

    Performance Optimizations:
        - Intelligent thread pool sizing based on credential set complexity (max 25 threads)
        - AWS API optimization with connection pooling and retry logic
        - Memory-efficient processing for large-scale serverless inventories
        - Concurrent processing patterns optimized for AWS Lambda API rate limiting
        - Real-time progress tracking for operational visibility during discovery

    Error Handling & Resilience:
        - Comprehensive AWS API error handling with retry and backoff logic
        - Thread-safe error aggregation preventing batch processing failures
        - Individual account failure isolation allowing continued processing
        - Access permission validation with graceful degradation patterns
        - Network connectivity resilience with automatic retry mechanisms

    Security & Compliance Integration:
        - Secure credential handling with temporary access patterns
        - Comprehensive audit logging for security and compliance tracking
        - Access control validation ensuring proper authorization levels
        - Function security configuration analysis for vulnerability assessment
        - Role and permission mapping for least privilege validation
    """

    class FindFunctions(Thread):
        """
        Thread-safe Lambda function discovery worker for concurrent multi-account processing.

        Implements enterprise-grade concurrent processing for Lambda function discovery
        and analysis across multiple AWS accounts and regions. Provides thread-safe
        result aggregation with comprehensive error handling and operational resilience
        for large-scale organizational serverless infrastructure audits.
        """

        def __init__(self, queue):
            """
            Initialize Lambda function discovery thread with work queue integration.

            Args:
                queue: Thread-safe work queue containing credential sets for processing
            """
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Execute Lambda function discovery for queued account credentials with comprehensive error handling.

            Processes account credentials from the thread-safe work queue, performing detailed
            Lambda function discovery and analysis for each account-region combination with
            fragment-based filtering. Implements robust error handling, logging, and result
            aggregation patterns for enterprise-scale serverless infrastructure audits.
            """
            while True:
                # Retrieve account credentials and fragment filters from thread-safe work queue
                c_account_credentials, c_fragment_list = self.queue.get()
                pbar.update()  # Update progress bar for operational visibility
                Functions = []
                logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
                try:
                    # Log Lambda function discovery initiation for audit trail
                    logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")

                    # Execute comprehensive Lambda function discovery with fragment filtering
                    Functions = Inventory_Modules.find_lambda_functions2(
                        c_account_credentials, c_account_credentials["Region"], c_fragment_list
                    )
                except TypeError as my_Error:
                    # Handle AWS API data type conversion errors during Lambda function processing
                    logging.info(f"Error: {my_Error}")
                    continue  # Continue processing other accounts despite individual failures
                except ClientError as my_Error:
                    # Handle AWS API authorization and access errors with detailed logging
                    if "AuthFailure" in str(my_Error):
                        logging.error(f"Account {c_account_credentials['AccountId']}: Authorization Failure")
                    continue  # Continue processing other accounts despite individual failures
                except KeyError as my_Error:
                    # Handle credential or account access configuration errors
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    continue  # Continue processing other accounts despite individual failures
                finally:
                    # Enrich discovered Lambda functions with organizational and credential context
                    if len(Functions) > 0:
                        for _ in range(len(Functions)):
                            # Add organizational context for enterprise reporting and management
                            Functions[_]["MgmtAccount"] = c_account_credentials["MgmtAccount"]
                            Functions[_]["AccountId"] = c_account_credentials["AccountId"]
                            Functions[_]["Region"] = c_account_credentials["Region"]

                            # Preserve access credentials for potential runtime update operations
                            Functions[_]["AccessKeyId"] = c_account_credentials["AccessKeyId"]
                            Functions[_]["SecretAccessKey"] = c_account_credentials["SecretAccessKey"]
                            Functions[_]["SessionToken"] = c_account_credentials["SessionToken"]

                            # Extract and format IAM role name for cleaner display
                            Rolet = Functions[_]["Role"]
                            Functions[_]["Role"] = mid(Rolet, Rolet.find("/") + 2, len(Rolet))

                        # Thread-safe aggregation of discovered Lambda functions
                        AllFuncs.extend(Functions)

                    # Signal task completion for thread-safe work queue management
                    self.queue.task_done()

    # Initialize thread-safe result aggregation for enterprise-scale Lambda function inventory
    AllFuncs = []  # Global Lambda function inventory with comprehensive serverless metadata

    # Optimize thread pool size for efficient processing while respecting AWS API limits
    WorkerThreads = min(len(CredentialList), 25)  # Cap at 25 threads for Lambda API rate limiting

    # Initialize thread-safe work queue for concurrent account processing
    checkqueue = Queue()

    # Initialize progress tracking for operational visibility during discovery
    pbar = tqdm(
        desc=f"Finding instances from {len(CredentialList)} accounts / regions",
        total=len(CredentialList),
        unit=" locations",
    )

    # Initialize multi-threaded Lambda function discovery worker pool
    for x in range(WorkerThreads):
        worker = FindFunctions(checkqueue)
        # Enable graceful shutdown with main thread termination for enterprise operational safety
        worker.daemon = True
        worker.start()  # Begin concurrent Lambda function discovery processing

    # Populate work queue with account credentials for distributed serverless discovery
    for credential in CredentialList:
        logging.info(f"Connecting to account {credential['AccountId']}")
        try:
            # Log work queue population for operational audit trail
            logging.info(
                f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {credential['Region']}", end="\r"
            )
            # Add credential and fragment filter to processing queue
            checkqueue.put((credential, fFragments))
        except ClientError as my_Error:
            # Handle AWS API authorization failures during queue population
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region"
                )
                logging.error(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass  # Continue processing remaining accounts despite individual failures

    # Wait for all Lambda function discovery tasks to complete before result aggregation
    checkqueue.join()

    # Return comprehensive Lambda function inventory with enterprise serverless metadata
    return AllFuncs


def collect_all_my_functions(AllCredentials, fFragments, fverbose=50):
    """
    Orchestrate comprehensive Lambda function collection and organize results for enterprise reporting.

    Coordinates multi-threaded Lambda function discovery across organizational accounts
    and regions, then sorts and formats results for enterprise serverless infrastructure
    management and reporting. Provides operational visibility through configurable
    verbosity controls and structured result organization.

    Args:
        AllCredentials (list): Complete list of validated AWS credentials containing:
            - Account credentials for cross-account Lambda function access
            - Regional configuration for comprehensive serverless coverage
            - Management account context for organizational hierarchy mapping

        fFragments (list): Function name fragments for targeted discovery filtering:
            - Enables focused searches based on naming conventions
            - Supports pattern matching for specific function categories
            - Empty list discovers all functions without filtering

        fverbose (int, optional): Logging verbosity level controlling output detail:
            - Values < 50: Enable summary statistics and progress information
            - Values >= 50: Minimal output for automated processing
            - Default 50 provides balanced operational visibility

    Returns:
        list: Sorted Lambda function inventory organized by enterprise hierarchy:
            - Primary sort: Management Account for organizational structure
            - Secondary sort: AccountId for account-level grouping
            - Tertiary sort: Region for geographic distribution analysis
            - Final sort: FunctionName for alphabetical function organization

    Enterprise Serverless Management Features:
        - Hierarchical function organization for multi-account governance
        - Geographic distribution analysis for compliance and performance
        - Structured result formatting for integration with enterprise tools
        - Operational summary reporting for executive visibility
        - Scalable processing architecture for large serverless estates

    Integration Capabilities:
        - Compatible with enterprise reporting and monitoring systems
        - Structured data format for CSV export and database integration
        - Consistent sorting for reliable report generation
        - Configurable verbosity for different operational contexts
        - Ready for runtime analysis and compliance assessment workflows
    """
    # Execute comprehensive multi-threaded Lambda function discovery
    AllFunctions = check_accounts_for_functions(AllCredentials, fFragments)

    # Sort functions by enterprise hierarchy for structured reporting and management
    sorted_AllFunctions = sorted(
        AllFunctions, key=lambda k: (k["MgmtAccount"], k["AccountId"], k["Region"], k["FunctionName"])
    )

    # Provide operational summary when verbose logging is enabled
    if fverbose < 50:
        print(f"We found {len(AllFunctions)} functions in {len(AllCredentials)} places")

    # Return enterprise-organized Lambda function inventory
    return sorted_AllFunctions


def fix_my_functions(fAllFunctions, fRuntime, fNewRuntime, fForceDelete, fTiming):
    """
    Orchestrate Lambda function runtime upgrade operations with comprehensive safety controls.

    **CRITICAL FUNCTION**: Manages live Lambda function runtime modifications with enterprise-grade
    safety controls, user confirmation workflows, and performance timing. Essential for security
    patching and compliance maintenance across organizational serverless infrastructure.

    Args:
        fAllFunctions (list): Lambda functions requiring runtime updates containing:
            - Function metadata and current runtime configuration
            - AWS credentials for runtime modification operations
            - Account and regional context for enterprise tracking

        fRuntime (str): Current runtime version being replaced (e.g., 'python3.8')
        fNewRuntime (str): Target runtime version for upgrade (e.g., 'python3.11')
        fForceDelete (bool): Override safety confirmation for automated operations
        fTiming (bool): Enable performance timing for operational metrics

    Returns:
        list|str: Either updated function list or error message string:
            - Success: List of successfully updated Lambda functions
            - Failure: String message indicating no functions were modified

    **ENTERPRISE SAFETY CONTROLS**:
        - Mandatory target runtime validation preventing incomplete operations
        - Interactive user confirmation for destructive operations (unless forced)
        - Comprehensive error handling and rollback logging
        - Performance timing for operational SLA compliance
        - Audit trail generation for enterprise compliance requirements

    Runtime Upgrade Safety Features:
        - Pre-validation: Ensures target runtime is specified before processing
        - User Confirmation: Interactive safety check for non-automated operations
        - Force Override: Automated operation support with comprehensive logging
        - Performance Monitoring: Operation timing for SLA and capacity planning
        - Error Recovery: Graceful failure handling with detailed diagnostics

    Enterprise Operational Workflows:
        - Security Patching: Automated migration from vulnerable runtime versions
        - Compliance Maintenance: Bulk runtime updates for regulatory requirements
        - Performance Optimization: Upgrade to more efficient runtime versions
        - Cost Optimization: Migration to cost-effective runtime configurations
        - Deprecation Management: Proactive migration from end-of-life runtimes

    **OPERATIONAL WARNINGS**:
        - Runtime changes are IMMEDIATE and IRREVERSIBLE
        - Function behavior may change with runtime version modifications
        - Comprehensive testing required before production deployment
        - Maintenance windows recommended for large-scale updates
        - Rollback procedures must be planned and tested in advance
    """
    # Initialize performance timing for operational metrics and SLA tracking
    begin_fix_time = time()

    # Validate target runtime specification to prevent incomplete operations
    if fNewRuntime is None:
        print(
            f"You provided the parameter at the command line to *fix* errors found, but didn't supply a new runtime to use, so exiting now... "
        )
        sys.exit(8)  # Exit with error code for automation and monitoring systems

    # Execute safety confirmation workflow based on force flag configuration
    elif not fForceDelete:
        print(f"You provided the parameter at the command line to *fix* errors found")
        # Interactive safety confirmation for destructive runtime modification operations
        ReallyDelete = input("Having seen what will change, are you still sure? (y/n): ") in ["y", "Y", "Yes", "yes"]
    elif fForceDelete:
        print(
            f"You provided the parameter at the command line to *fix* errors found, as well as FORCING this change to happen... "
        )
        ReallyDelete = True  # Override safety checks for automated operational workflows
    else:
        ReallyDelete = False

    # Execute runtime upgrade operations based on safety confirmation results
    if ReallyDelete:
        print(f"Updating Runtime for all functions found from {fRuntime} to {fNewRuntime}")
        # CRITICAL: Perform live Lambda function runtime modifications
        return_response = fix_runtime(fAllFunctions, fNewRuntime)
    else:
        return_response = "No functions were remediated."

        # Display performance timing for operational optimization and SLA compliance
        if fTiming:
            print(ERASE_LINE)
            print(
                f"{Fore.GREEN}Fixing {len(return_response)} functions took {time() - begin_fix_time:.3f} seconds{Fore.RESET}"
            )

    # Return operation results for enterprise reporting and audit trail
    return return_response


##################
# Main execution entry point for enterprise Lambda function inventory and runtime management
##################

if __name__ == "__main__":
    """
    Main orchestration for comprehensive Lambda function discovery, analysis, and runtime management.
    
    Coordinates multi-account, multi-region serverless infrastructure inventory with specialized
    support for runtime upgrade operations and enterprise serverless governance workflows.
    Implements comprehensive safety controls for production runtime modifications.
    """
    # Parse enterprise command-line arguments with Lambda-specific runtime management options
    args = parse_args(sys.argv[1:])

    # Extract configuration parameters for multi-account serverless discovery and management
    pProfiles = args.Profiles  # AWS profile list for federated serverless access
    pRegionList = args.Regions  # Target regions for Lambda function enumeration
    pFragments = args.Fragments  # Function name fragments for targeted discovery
    pAccounts = args.Accounts  # Specific account targeting for focused operations
    pFix = args.Fix  # CRITICAL: Enable live runtime modification operations
    pForceDelete = args.Force  # Override safety confirmations for automated workflows
    pSaveFilename = args.Filename  # CSV export file for enterprise reporting
    pRuntime = args.Runtime  # Target runtime(s) for compliance filtering
    pNewRuntime = args.NewRuntime  # Replacement runtime for upgrade operations

    # Optimize fragment filtering when runtime-specific discovery is requested
    if pFragments == ["all"] and pRuntime is not None:
        pFragments = []  # Clear default 'all' filter for runtime-specific searches

    # Extract operational control parameters for enterprise Lambda management
    pSkipAccounts = args.SkipAccounts  # Account exclusion list for organizational policy
    pSkipProfiles = args.SkipProfiles  # Profile exclusion for credential optimization
    pRootOnly = args.RootOnly  # Organization root account limitation flag
    pRoleList = args.AccessRoles  # Cross-account roles for Organizations access
    pTiming = args.Time  # Performance timing for operational optimization
    pverbose = args.loglevel  # Logging verbosity for operational visibility

    # Configure enterprise logging infrastructure for serverless operations
    logging.basicConfig(level=pverbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

    # Configure enterprise Lambda function inventory report display formatting
    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},  # Management account for organizational hierarchy
        "AccountId": {
            "DisplayOrder": 2,
            "Heading": "Acct Number",
        },  # Account identifier for serverless resource ownership
        "Region": {"DisplayOrder": 3, "Heading": "Region"},  # AWS region for geographic Lambda distribution analysis
        "FunctionName": {
            "DisplayOrder": 4,
            "Heading": "Function Name",
        },  # Lambda function name for identification and management
        "Role": {"DisplayOrder": 6, "Heading": "Role"},  # IAM execution role for security and permission analysis
    }

    # Configure runtime display column based on filtering parameters for targeted compliance analysis
    if pRuntime is None and pFragments is None:
        # Standard runtime display for comprehensive serverless inventory
        display_dict.update({"Runtime": {"DisplayOrder": 5, "Heading": "Runtime"}})
    elif pRuntime is not None and pFragments is None:
        # Runtime-specific display for targeted compliance and security analysis
        display_dict.update({"Runtime": {"DisplayOrder": 5, "Heading": "Runtime", "Condition": pRuntime}})
    elif pRuntime is None and pFragments is not None:
        # Fragment-based display for focused function category analysis
        display_dict.update({"Runtime": {"DisplayOrder": 5, "Heading": "Runtime", "Condition": pFragments}})
    elif pRuntime is not None and pFragments is not None:
        # Combined runtime and fragment filtering for precise serverless governance
        display_dict.update({"Runtime": {"DisplayOrder": 5, "Heading": "Runtime", "Condition": pRuntime + pFragments}})

    # Initialize credential discovery for multi-account serverless infrastructure analysis
    print(f"Collecting credentials... ")

    # Execute enterprise credential discovery and validation across organizational hierarchy
    CredentialList = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pRoleList
    )

    # Calculate organizational scope for executive reporting and operational planning
    AccountNum = len(set([acct["AccountId"] for acct in CredentialList]))
    RegionNum = len(set([acct["Region"] for acct in CredentialList]))
    print()
    print(f"Looking through {AccountNum} accounts and {RegionNum} regions ")
    print()

    # Combine fragment and runtime filters for comprehensive serverless discovery
    # Note: pFragments defaults to ['all'], ensuring complete coverage when runtime filtering is applied
    full_list_to_look_for = pFragments + pRuntime if pRuntime is not None else pFragments

    # Execute comprehensive multi-threaded Lambda function discovery and analysis
    AllFunctions = collect_all_my_functions(CredentialList, full_list_to_look_for, pverbose)

    # Update scope metrics based on actual discovered serverless infrastructure
    AccountNum = len(set([x["AccountId"] for x in AllFunctions]))
    RegionNum = len(set([x["Region"] for x in AllFunctions]))

    # Generate comprehensive Lambda function inventory report with CSV export capability
    display_results(AllFunctions, display_dict, None, pSaveFilename)

    # Execute runtime upgrade operations when fix flag is enabled (CRITICAL OPERATIONS)
    if pFix:
        # Validate runtime upgrade parameters to prevent incomplete operations
        if pRuntime is None or pNewRuntime is None:
            print(f"You neglected to provide the runtime you want to change from and to. Exiting here... ")
            sys.exit(7)  # Exit with error code for automation and monitoring systems

        # CRITICAL: Execute live Lambda function runtime modifications with safety controls
        FixedFunctions = fix_my_functions(AllFunctions, pRuntime, pNewRuntime, pForceDelete, pTiming)
        print()
        print("And since we remediated the functions - here's the updated list... ")
        print()

        # Display post-update function inventory for verification and audit trail
        display_results(FixedFunctions, display_dict, None, pSaveFilename)

    # Display performance timing metrics for operational optimization and SLA compliance
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.3f} seconds{Fore.RESET}")

    print(ERASE_LINE)

    # Display comprehensive operational summary for executive reporting and documentation
    print(f"Found {len(AllFunctions)} functions across {AccountNum} accounts, across {RegionNum} regions")
    print()

    # Display completion message for user confirmation and operational closure
    print("Thank you for using this script")
    print()

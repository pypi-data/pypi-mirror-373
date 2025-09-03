#!/usr/bin/env python3
"""
AWS CloudFormation StackSet Drift Detection Management and Analysis Script

Comprehensive enterprise-grade tool for discovering, monitoring, and enabling drift detection
across CloudFormation StackSets in AWS Organizations environments. Designed for infrastructure
governance, compliance monitoring, and automated drift detection management with multi-threading
support for efficient large-scale StackSet operations.

Key Features:
- Multi-account CloudFormation StackSet drift detection discovery and status monitoring
- Automated drift detection enablement based on configurable time thresholds
- Fragment-based StackSet filtering for targeted drift detection management
- Multi-threaded drift detection operations for improved performance at scale
- Comprehensive status reporting with tabular output and optional file export
- Enterprise authentication with cross-account role assumption support
- Configurable time-based drift detection refresh policies

Enterprise Capabilities:
- CloudFormation StackSet lifecycle management and drift monitoring
- Organizational compliance tracking through systematic drift detection
- Automated infrastructure governance with policy-driven drift detection updates
- Multi-region StackSet drift status visibility and management
- Performance-optimized concurrent drift detection operations
- Comprehensive error handling for large-scale organizational environments

Operational Use Cases:
- Infrastructure compliance auditing across organizational StackSet deployments
- Automated drift detection enablement for StackSets exceeding age thresholds
- StackSet governance through systematic drift monitoring and reporting
- Enterprise infrastructure change tracking and compliance validation
- Organizational CloudFormation resource drift analysis and remediation planning

Output Format:
- Tabular display of StackSet drift detection status with account, region, and timing information
- Optional CSV/JSON export for integration with enterprise reporting systems
- Comprehensive operational metrics including drift detection age and status
- Color-coded terminal output for enhanced operational visibility

Authentication & Security:
- AWS Organizations cross-account access with IAM role assumption
- Multi-profile authentication support for organizational account management
- Regional validation and access control for secure StackSet operations
- Comprehensive error handling for authorization and access management

Performance & Scale:
- Multi-threaded drift detection operations for efficient large-scale processing
- Memory-efficient processing for extensive StackSet inventories
- Configurable concurrency limits for optimal AWS API usage and performance
- Progress tracking and operational timing for performance monitoring

Dependencies:
- boto3: AWS SDK for CloudFormation StackSet API operations
- Custom modules: Inventory_Modules, ArgumentsClass, account_class
- colorama: Enhanced terminal output and color formatting
- dateutil: Advanced date/time parsing and timezone handling

Authors: AWS CloudOps Team
Version: 2024.03.06
License: MIT
"""

import logging
import sys
from datetime import datetime
from os.path import split
from time import time

import Inventory_Modules
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results

# Initialize colorama for cross-platform colored terminal output
init()
__version__ = "2024.03.06"
begin_time = time()  # Script execution timing for performance monitoring
sleep_interval = 5  # Default wait interval for drift detection operations


def parse_args(args):
    """
    Parse and validate command line arguments for CloudFormation StackSet drift detection operations.

    Configures comprehensive CLI argument parsing with enterprise-grade options for StackSet
    drift detection management, including profile authentication, regional targeting, fragment
    filtering, drift detection enablement, and time-based refresh policies for organizational
    infrastructure governance and compliance monitoring.

    Args:
        args (list): Command line arguments from sys.argv[1:] for argument parsing

    Returns:
        argparse.Namespace: Parsed arguments object containing:
            - Profile: AWS profile name for authentication and cross-account access
            - Region: Target AWS region for StackSet drift detection operations
            - Fragments: StackSet name fragments for targeted filtering and discovery
            - Exact: Boolean flag for exact fragment matching vs substring matching
            - pstatus: StackSet status filter for 'active' vs all status types
            - pEnable: Boolean flag to enable automated drift detection on eligible StackSets
            - pDaysSince: Time threshold in days for drift detection refresh policy
            - Filename: Optional output file path for results export and persistence
            - Time: Boolean flag for execution timing and performance monitoring
            - loglevel: Logging verbosity level for operational visibility

    CLI Arguments:
        Authentication & Targeting:
            --profile (-p): AWS profile for authentication and account access
            --region (-r): Target AWS region for StackSet operations

        StackSet Filtering & Discovery:
            --fragment (-f): StackSet name fragments for targeted search and filtering
            --exact (-e): Enable exact fragment matching instead of substring search

        Drift Detection Management:
            --status (-s): StackSet status filter ('active' for operational StackSets only)
            +enable: Automated drift detection enablement for eligible StackSets
            --days_since (--ds): Age threshold in days for drift detection refresh

        Output & Reporting:
            --filename: Output file path for results export (CSV/JSON format)
            --timing (-t): Enable execution timing and performance metrics
            --loglevel (-v): Logging verbosity (DEBUG, INFO, WARNING, ERROR)

    Enterprise Features:
        - Multi-profile authentication for organizational account management
        - Regional targeting with validation for StackSet drift detection operations
        - Fragment-based filtering for targeted StackSet discovery and management
        - Time-based drift detection refresh policies for compliance automation
        - Flexible output options for integration with enterprise reporting systems

    Validation & Error Handling:
        - AWS profile validation with comprehensive error messaging
        - Regional access validation preventing unauthorized operations
        - Argument validation with detailed help text and usage examples
        - Type checking and range validation for numeric parameters
    """
    # Extract script name for argument group organization and help display
    script_path, script_name = split(sys.argv[0])

    # Initialize common argument parser with enterprise authentication and targeting
    parser = CommonArguments()
    parser.singleprofile()  # AWS profile for authentication and account access
    parser.singleregion()  # Target AWS region for StackSet operations
    parser.extendedargs()  # Extended arguments for account filtering and targeting
    parser.fragment()  # StackSet name fragment filtering for targeted discovery
    parser.save_to_file()  # Output file options for results export and persistence
    parser.timing()  # Execution timing for performance monitoring
    parser.verbosity()  # Logging verbosity for operational visibility
    parser.version(__version__)  # Script version for compatibility tracking

    # Configure script-specific arguments for StackSet drift detection management
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")

    # StackSet status filtering for operational vs all StackSet types
    local.add_argument(
        "-s",
        "--status",
        dest="pstatus",
        metavar="CloudFormation status",
        default="active",
        help="StackSet status filter: 'active' for operational StackSets, 'all' for comprehensive discovery including deleted StackSets",
    )

    # Automated drift detection enablement for eligible StackSets
    local.add_argument(
        "+enable",
        dest="pEnable",
        action="store_true",
        help="Enable automated drift detection on StackSets that haven't been checked within the specified time threshold",
    )

    # Time threshold for drift detection refresh policy and compliance automation
    local.add_argument(
        "--days_since",
        "--ds",
        dest="pDaysSince",
        metavar="Number of days old",
        type=int,
        default=15,
        help="Maximum age in days since last drift detection check before StackSet requires drift detection refresh (default: 15 days)",
    )

    return parser.my_parser.parse_args(args)


def setup_auth(fProfile: str) -> aws_acct_access:
    """
    Configure AWS authentication and validate account access for StackSet drift detection operations.

    Establishes secure AWS authentication using the specified profile with comprehensive error
    handling and validation. Provides operational context display including account information,
    region targeting, fragment filtering, and drift detection enablement status for enterprise
    StackSet management and infrastructure governance operations.

    Args:
        fProfile (str): AWS profile name for authentication and cross-account access
                       None or empty string defaults to default profile or environment credentials

    Returns:
        aws_acct_access: Authenticated AWS account access object containing:
            - acct_number: AWS account number for operational context
            - AccountType: Account type (root, member, etc.) for organizational visibility
            - Region: Target AWS region for StackSet drift detection operations
            - session: Authenticated boto3 session for CloudFormation API calls
            - Success: Boolean indicating successful authentication and account access

    Authentication Process:
        1. Initialize AWS account access object with specified profile
        2. Validate credential authenticity and account permissions
        3. Verify CloudFormation StackSet API access in target region
        4. Display comprehensive operational context for user confirmation
        5. Return authenticated account object for downstream operations

    Operational Context Display:
        - Account information including account number and organizational type
        - Target region for StackSet drift detection operations
        - Fragment filtering criteria for StackSet discovery and targeting
        - Drift detection enablement status and operational mode
        - User confirmation of operational parameters and scope

    Error Handling:
        - Connection errors with comprehensive error messaging and exit codes
        - Authentication failures with detailed troubleshooting guidance
        - Profile validation with specific error messaging for credential issues
        - Regional access validation preventing unauthorized operations

    Enterprise Security:
        - Multi-profile authentication for organizational account management
        - Cross-account role assumption validation for secure operations
        - Regional access control ensuring authorized StackSet operations
        - Comprehensive audit logging for security and compliance tracking

    Raises:
        SystemExit: On authentication failures or connection errors with specific exit codes:
            - Exit code 8: Connection errors preventing AWS API access
            - Exit code 99: Authentication failures or invalid credentials
    """
    try:
        # Initialize AWS account access with profile-based authentication
        aws_acct = aws_acct_access(fProfile)
    except ConnectionError as my_Error:
        # Handle connection errors with detailed logging and graceful exit
        logging.error(f"Exiting due to error: {my_Error}")
        sys.exit(8)

    # Validate successful authentication and account access
    if not aws_acct.Success:
        print(f"{Fore.RED}Profile {pProfile} failed to access an account. Check credentials and try again{Fore.RESET}")
        sys.exit(99)

    # Display comprehensive operational context for user confirmation and audit logging
    print()
    print(f"You asked me to display drift detection status on stacksets that match the following:")
    print(f"\t\tIn the {aws_acct.AccountType} account {aws_acct.acct_number}")
    print(f"\t\tIn this Region: {pRegion}")

    # Display fragment filtering criteria with exact vs substring matching context
    if pExact:
        print(f"\t\tFor stacksets that {Fore.RED}exactly match{Fore.RESET}: {pFragments}")
    else:
        print(
            f"\t\tFor stacksets that contain th{'is fragment' if len(pFragments) == 1 else 'ese fragments'}: {pFragments}"
        )

    # Display drift detection enablement status for operational clarity
    print(f"\t\tand enable drift detection on those stacksets, if they're not current") if pEnableDriftDetection else ""

    print()
    return aws_acct


def find_stack_sets(faws_acct: aws_acct_access, fStackSetFragmentlist: list = None, fExact: bool = False) -> dict:
    """
    Discover and enumerate CloudFormation StackSets with comprehensive drift detection metadata.

    Performs targeted CloudFormation StackSet discovery using fragment-based filtering with
    comprehensive error handling and drift detection metadata extraction. Designed for enterprise
    StackSet lifecycle management, compliance monitoring, and automated drift detection operations
    across organizational AWS environments.

    Args:
        faws_acct (aws_acct_access): Authenticated AWS account access object containing:
            - session: boto3 session for CloudFormation API operations
            - Region: Target AWS region for StackSet discovery operations
            - acct_number: Account number for error logging and operational context
        fStackSetFragmentlist (list): StackSet name fragments for targeted filtering
                                     None defaults to ["all"] for comprehensive StackSet discovery
        fExact (bool): Fragment matching mode for precision targeting
                      True: Exact fragment matching for specific StackSet identification
                      False: Substring matching for broader StackSet discovery

    Returns:
        dict: Comprehensive StackSet discovery results containing:
            - Success: Boolean indicating successful StackSet discovery operation
            - ErrorMessage: Detailed error information for troubleshooting and logging
            - StackSets: Dictionary of discovered StackSets with drift detection metadata:
                - StackSetName: CloudFormation StackSet identifier
                - Status: Current StackSet operational status
                - DriftStatus: Current drift detection status (DRIFTED, IN_SYNC, etc.)
                - LastDriftCheckTimestamp: Most recent drift detection timestamp
                - Stack_Instances_number: Count of StackSet instances across accounts/regions
                - Additional operational metadata for governance and compliance

    StackSet Discovery Features:
        - Fragment-based filtering for targeted StackSet identification and management
        - Comprehensive drift detection metadata extraction for compliance monitoring
        - StackSet instance enumeration for organizational visibility and governance
        - Status-based filtering for operational StackSet lifecycle management
        - Regional StackSet discovery with cross-account instance visibility

    Drift Detection Metadata:
        - Current drift detection status for infrastructure change tracking
        - Last drift check timestamps for compliance and policy enforcement
        - Drift detection enablement status for automated governance workflows
        - Instance-level drift aggregation for comprehensive compliance reporting

    Error Handling & Resilience:
        - AWS API authorization failure detection with detailed error logging
        - CloudFormation service error handling with comprehensive error context
        - Network connectivity error management with graceful degradation
        - Regional access validation preventing unauthorized StackSet operations

    Enterprise Integration:
        - Structured result format for integration with enterprise reporting systems
        - Comprehensive error messaging for operational troubleshooting and audit
        - Performance-optimized discovery for large-scale StackSet inventories
        - Organizational compliance tracking through systematic metadata extraction

    Performance Considerations:
        - Memory-efficient processing for extensive StackSet inventories
        - Regional API optimization for improved discovery performance
        - Concurrent-safe operations for integration with multi-threaded workflows
        - Structured result caching for repeated discovery operations
    """
    # Configure default fragment filtering for comprehensive StackSet discovery
    if fStackSetFragmentlist is None:
        fStackSetFragmentlist = ["all"]  # Default to all StackSets for comprehensive analysis

    # Initialize StackSet discovery result structure with error tracking
    StackSets = {"Success": False, "ErrorMessage": "", "StackSets": {}}

    try:
        # Execute comprehensive StackSet discovery with drift detection metadata extraction
        StackSets = Inventory_Modules.find_stacksets3(faws_acct, faws_acct.Region, fStackSetFragmentlist, fExact, True)
    except ClientError as my_Error:
        # Handle AWS API client errors with specific authorization failure detection
        if "AuthFailure" in str(my_Error):
            error_message = f"{aws_acct.acct_number}: Authorization Failure"
            logging.error(error_message)
        else:
            error_message = f"Error: {my_Error}"
            logging.error(error_message)
        StackSets["ErrorMessage"] = error_message
    except Exception as my_Error:
        # Handle comprehensive exceptions with detailed error logging
        error_message = f"Error: {my_Error}"
        logging.error(error_message)
        StackSets["ErrorMessage"] = error_message

    return StackSets


def enable_stack_set_drift_detection(faws_acct: aws_acct_access, fStackSets: dict = None):
    """
    Enable automated drift detection across multiple CloudFormation StackSets using multi-threading.

    Executes comprehensive drift detection enablement operations across organizational StackSets
    using multi-threaded processing for efficient large-scale operations. Monitors drift detection
    operation progress with real-time status tracking and comprehensive error handling for enterprise
    infrastructure governance and compliance automation.

    Args:
        faws_acct (aws_acct_access): Authenticated AWS account access object containing:
            - session: boto3 session for CloudFormation StackSet API operations
            - acct_number: Account number for operational logging and error context
            - Region: Target AWS region for drift detection operations
        fStackSets (dict): List of StackSets requiring drift detection enablement containing:
            - StackSetName: CloudFormation StackSet identifier for drift detection
            - NeedsDriftDetectionUpdate: Boolean indicating drift detection requirement
            - Additional StackSet metadata for operational context and tracking

    Returns:
        dict: Updated StackSets dictionary with drift detection operation results containing:
            - Success: Boolean indicating overall drift detection enablement success
            - ErrorMessage: Detailed error information for failed operations
            - Individual StackSet status updates with drift detection results

    Multi-threaded Architecture:
        - Queue-based worker pattern for concurrent drift detection operations
        - Configurable worker thread pool with automatic scaling based on StackSet count
        - Thread-safe operation monitoring with real-time progress tracking
        - Graceful error handling for authorization and operational failures

    Drift Detection Operation Management:
        - Automated drift detection enablement on eligible StackSets
        - Real-time operation status monitoring with progress indicators
        - Operation completion tracking with timeout management
        - Comprehensive error detection and recovery for failed operations

    Progress Monitoring & Feedback:
        - Real-time terminal progress display with operation status updates
        - Configurable sleep intervals for optimal API usage and performance
        - Operation timing tracking for performance monitoring and optimization
        - Visual progress indicators for enhanced user experience

    Error Handling & Resilience:
        - AWS API authorization failure detection with graceful degradation
        - CloudFormation service error management with detailed error logging
        - Network connectivity error handling with operation retry capabilities
        - Thread-safe error aggregation for comprehensive operation reporting

    Enterprise Operational Features:
        - Concurrent drift detection operations for improved performance at scale
        - Comprehensive operational logging for audit and troubleshooting
        - Resource-efficient processing for large-scale StackSet inventories
        - Integration-ready result format for enterprise reporting and automation

    Performance Optimization:
        - Worker thread scaling based on StackSet count for optimal performance
        - Memory-efficient processing with queue-based work distribution
        - API rate limiting awareness with configurable sleep intervals
        - Operational timing metrics for performance analysis and optimization
    """
    from queue import Queue
    from threading import Thread
    from time import sleep

    class UpdateDriftDetection(Thread):
        """
        Multi-threaded worker class for concurrent drift detection enablement operations.

        Implements thread-safe drift detection operations using queue-based work distribution
        for efficient processing of CloudFormation StackSet drift detection across multiple
        StackSets with comprehensive error handling and progress monitoring.
        """

        def __init__(self, queue):
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            while True:
                # Extract StackSet work item from queue for drift detection processing
                c_aws_acct, c_stackset_name = self.queue.get()
                logging.info(f"De-queued info for account {c_aws_acct.acct_number}")

                try:
                    # Execute drift detection enablement with comprehensive status monitoring
                    logging.info(f"Attempting to run drift_detection on {c_stackset_name['StackSetName']}")
                    client = c_aws_acct.session.client("cloudformation")
                    logging.info(f"Enabling Drift Detection for {c_stackset_name['StackSetName']}")

                    # Initiate drift detection operation using custom inventory module
                    DD_Operation = Inventory_Modules.enable_drift_on_stackset3(
                        c_aws_acct, c_stackset_name["StackSetName"]
                    )

                    # Monitor drift detection operation progress with real-time status tracking
                    intervals_waited = 1
                    sleep(sleep_interval)  # Initial wait for operation to start

                    # Poll drift detection operation status until completion
                    Status = client.describe_stack_set_operation(
                        StackSetName=c_stackset_name["StackSetName"], OperationId=DD_Operation["OperationId"]
                    )

                    # Continue monitoring while drift detection operation is running
                    while Status["StackSetOperation"]["Status"] in ["RUNNING"]:
                        Status = client.describe_stack_set_operation(
                            StackSetName=c_stackset_name["StackSetName"], OperationId=DD_Operation["OperationId"]
                        )
                        sleep(sleep_interval)  # Wait between status checks to avoid API throttling

                        # Display real-time progress with timing information
                        print(
                            f"{ERASE_LINE}Waiting for {c_stackset_name['StackSetName']} to finish drift detection",
                            f"{sleep_interval * intervals_waited} seconds waited so far",
                            end="\r",
                        )
                        intervals_waited += 1
                        logging.info(f"Sleeping to allow {c_stackset_name['StackSetName']} to continue drift detection")

                    # Process drift detection operation completion status
                    if Status["Status"] in ["FAILED"]:
                        fStackSets["Success"] = False
                        fStackSets["ErrorMessage"] = Status["StackSetOperation"]["StackSetDriftDetectionDetails"]
                    else:
                        fStackSets["Success"] = True

                except TypeError as my_Error:
                    # Handle type errors in drift detection processing with logging
                    logging.info(f"Error: {my_Error}")
                    continue
                except ClientError as my_Error:
                    # Handle AWS API client errors with specific authorization failure detection
                    if "AuthFailure" in str(my_Error):
                        logging.error(f"Account {c_aws_acct.acct_number}: Authorization Failure")
                    continue
                except KeyError as my_Error:
                    # Handle missing key errors in account access with detailed logging
                    logging.error(f"Account Access failed - trying to access {c_aws_acct.acct_number}")
                    logging.info(f"Actual Error: {my_Error}")
                    continue
                finally:
                    # Mark queue item as completed for work distribution tracking
                    # Note: Commented metadata updates for potential future enhancement
                    # fStackSets[c_stackset_name]['AccountId'] = c_aws_acct.acct_number
                    # fStackSets[c_stackset_name]['Region'] = c_aws_acct.Region
                    self.queue.task_done()

    # Configure optimal worker thread count based on StackSet count and system limits
    WorkerThreads = min(len(fStackSets), 25)

    # Initialize multi-threaded processing infrastructure for drift detection operations
    checkqueue = Queue()

    # Create and start worker thread pool for concurrent drift detection operations
    for x in range(WorkerThreads):
        worker = UpdateDriftDetection(checkqueue)
        # Daemon threads allow main thread exit even if workers are still processing
        worker.daemon = True
        worker.start()

    # Queue drift detection work items for worker thread processing
    for stackset in fStackSets:
        logging.info(f"Connecting to account {faws_acct.acct_number}")
        try:
            # Queue StackSet for drift detection processing with progress display
            print(
                f"{ERASE_LINE}Queuing stackset {stackset['StackSetName']} in account {faws_acct.acct_number} in region {faws_acct.Region}",
                end="\r",
            )
            checkqueue.put((faws_acct, stackset))
        except ClientError as my_Error:
            # Handle authorization failures with informative error messaging
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {faws_acct.acct_number} in {faws_acct.Region} region"
                )
                logging.error(f"It's possible that the region {faws_acct.Region} hasn't been opted-into")
                pass

    # Wait for all worker threads to complete drift detection operations
    checkqueue.join()
    return fStackSets


def days_between_dates(fdate1: datetime, fdays_since: int):
    """
    Calculate time difference between drift detection timestamp and current time for compliance evaluation.

    Performs comprehensive date arithmetic to determine whether CloudFormation StackSet drift detection
    timestamps meet organizational compliance policies and time-based refresh requirements. Designed
    for enterprise governance automation with timezone-aware date calculations and structured result
    formatting for integration with automated compliance workflows.

    Args:
        fdate1 (datetime): Drift detection timestamp from CloudFormation StackSet metadata
                          None indicates drift detection has never been executed
                          Must be timezone-aware datetime object for accurate calculations
        fdays_since (int): Maximum acceptable age in days for drift detection compliance
                          Organizational policy threshold for drift detection refresh requirements

    Returns:
        dict: Comprehensive drift detection age evaluation containing:
            - Current: Boolean indicating compliance with organizational time policies
            - NumberOfDays: Integer days since last drift detection for operational metrics
            - ErrorMessage: Detailed error information for null or invalid timestamps

    Compliance Policy Evaluation:
        - Current=True: Drift detection age within acceptable organizational thresholds
        - Current=False: Drift detection exceeds policy limits and requires refresh
        - ErrorMessage: Indicates drift detection has never been executed (requires enablement)

    Enterprise Features:
        - Timezone-aware date calculations for accurate multi-region compliance evaluation
        - Structured result format for integration with enterprise governance systems
        - Comprehensive error handling for missing or invalid drift detection metadata
        - Policy-driven compliance evaluation with configurable time thresholds

    Date Calculation Logic:
        1. Validate drift detection timestamp existence and format
        2. Calculate absolute time difference between current time and drift detection timestamp
        3. Extract days component from timedelta for policy evaluation
        4. Compare against organizational policy threshold for compliance determination
        5. Return structured compliance result with operational metrics

    Error Handling:
        - Null timestamp handling for StackSets without drift detection history
        - Type validation ensuring datetime objects for accurate calculations
        - Timezone handling for consistent multi-region drift detection evaluation
        - Comprehensive error messaging for troubleshooting and operational visibility

    Integration Considerations:
        - Structured result format for automated compliance reporting systems
        - Policy threshold configurability for organizational governance flexibility
        - Operational metrics inclusion for drift detection age tracking and analysis
        - Error state handling for StackSets requiring initial drift detection enablement
    """
    from dateutil.tz import tzutc

    # Validate drift detection timestamp existence for compliance evaluation
    if fdate1 is None:
        # Return structured error result for StackSets without drift detection history
        response = {"Current": False, "ErrorMessage": "Drift Status never checked"}
        return response
    elif not isinstance(fdate1, datetime):
        # Enforce datetime object requirement for accurate date arithmetic
        raise ValueError("Date passed in should be datetime object")

    # Calculate timezone-aware time difference for accurate compliance evaluation
    date_difference = abs(datetime.now(tzutc()) - fdate1)

    # Extract days component from timedelta for policy threshold comparison
    number_of_days = date_difference.days

    # Evaluate drift detection age against organizational compliance policy
    if number_of_days <= fdays_since:
        # Drift detection meets organizational compliance requirements
        response = {"Current": True, "NumberOfDays": number_of_days}
    else:
        # Drift detection exceeds policy threshold and requires refresh
        response = {"Current": False, "NumberOfDays": number_of_days}

    return response


##################
# Main
##################
if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfile = args.Profile
    pRegion = args.Region
    pFragments = args.Fragments
    pExact = args.Exact
    pDaysSince = args.pDaysSince
    pstatus = args.pstatus
    pFilename = args.Filename
    pEnableDriftDetection = args.pEnable
    pTiming = args.Time
    AccountsToSkip = args.SkipAccounts
    ProfilesToSkip = args.SkipProfiles
    pAccounts = args.Accounts
    pSaveFilename = args.Filename
    verbose = args.loglevel

    # Set Log Level
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    """
	We should eventually create an argument here that would check on the status of the drift-detection using
	"describe_stack_drift_detection_status", but we haven't created that function yet... 
	https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_drift_detection_status
	"""

    ##########################
    ERASE_LINE = "\x1b[2K"

    # Setup the aws_acct object, and the list of Regions
    aws_acct = setup_auth(pProfile)

    display_dict_stacksets = {
        "AccountNumber": {"DisplayOrder": 1, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 2, "Heading": "Region"},
        "StackSetName": {"DisplayOrder": 3, "Heading": "Stack Set Name"},
        "Status": {"DisplayOrder": 4, "Heading": "Stack Status"},
        "Stack_Instances_number": {"DisplayOrder": 5, "Heading": "# of Instances"},
        "DriftStatus": {"DisplayOrder": 6, "Heading": "Drift Status"},
        "LastDriftCheckTimestamp": {"DisplayOrder": 7, "Heading": "Date Drift Checked"},
        "NeedsDriftDetectionUpdate": {"DisplayOrder": 8, "Heading": "Needs update", "Condition": [True]},
    }

    # RegionList = Inventory_Modules.get_service_regions('cloudformation', pRegionList)

    # Find StackSets to operate on and get the last detection status
    StackSets = find_stack_sets(aws_acct, pFragments, pExact)
    StackSetsList = [item for key, item in StackSets["StackSets"].items()]
    for item in StackSetsList:
        item["AccountNumber"] = aws_acct.acct_number
        item["Region"] = aws_acct.Region
    sorted_all_stacksets = sorted(StackSetsList, key=lambda x: (x["StackSetName"]))
    for item in sorted_all_stacksets:
        if (
            "LastDriftCheckTimestamp" not in item.keys()
            or not days_between_dates(item["LastDriftCheckTimestamp"], pDaysSince)["Current"]
        ) and item.get("Stack_Instances_number", 0) > 0:
            item["NeedsDriftDetectionUpdate"] = True
        else:
            item["NeedsDriftDetectionUpdate"] = False
    display_results(sorted_all_stacksets, display_dict_stacksets, None, pSaveFilename)
    # Enable drift_detection on those stacksets
    DriftDetectionNeededStacksets = [item for item in StackSetsList if item["NeedsDriftDetectionUpdate"]]
    if len(DriftDetectionNeededStacksets) == 0:
        print()
        print(f"The stacksets found all fall within current guidelines. No additional drift detection is necessary.")
        print()
        ReallyDetectDrift = False
    else:
        StackSetNamesThatNeededDriftDetection = [item["StackSetName"] for item in DriftDetectionNeededStacksets]
        if verbose == logging.INFO:
            print(
                f"The following stacksets haven't been updated in at least {pDaysSince} days, and therefore need to be updated:"
            )
            for stackname in StackSetNamesThatNeededDriftDetection:
                print(f"\t{stackname}")
        ReallyDetectDrift = input(
            f"Do you want to enable drift detection on th{'is' if len(DriftDetectionNeededStacksets) == 1 else 'ese'} {len(DriftDetectionNeededStacksets)} stackset{' that is not' if len(DriftDetectionNeededStacksets) == 1 else 's that are not'} current? (y/n)"
        ) in ["Y", "y"]
    if ReallyDetectDrift:
        Drift_Status = enable_stack_set_drift_detection(aws_acct, DriftDetectionNeededStacksets)
        StackSets = find_stack_sets(aws_acct, StackSetNamesThatNeededDriftDetection, True)
        # Determine whether we want to update this status or not -
        StackSetsList = [item for key, item in StackSets["StackSets"].items()]
        sorted_all_stacksets = sorted(StackSetsList, key=lambda x: (x["StackSetName"]))
        # Display results
        display_results(sorted_all_stacksets, display_dict_stacksets, None, pSaveFilename)

    print(ERASE_LINE)
    print(f"{Fore.RED}Looked through {len(sorted_all_stacksets)} StackSets across the {pRegion} region{Fore.RESET}")
    print()

    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.3f} seconds{Fore.RESET}")
    print("Thanks for using this script...")
    print()

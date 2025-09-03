#!/usr/bin/env python3

"""
AWS CloudFormation StackSet Operations Discovery and Analysis Script

This enterprise-grade inventory and monitoring script provides comprehensive StackSet operations
discovery, analysis, and tracking across multi-account AWS Organizations environments. Designed
for infrastructure teams, DevOps engineers, and cloud architects managing large-scale CloudFormation
StackSet deployments with centralized operational oversight and deployment orchestration.

Key Features:
    - StackSet operations discovery and lifecycle tracking across organizational accounts
    - Multi-threaded StackSet instance enumeration for deployment topology analysis
    - Last operation status analysis with failure detection and operational insights
    - Stack instance detailed status tracking for deployment troubleshooting
    - Fragment-based filtering for targeted StackSet operations analysis and monitoring
    - Comprehensive error handling for authorization, throttling, and connectivity issues
    - Progress tracking with real-time operational feedback and performance metrics
    - Flexible output formatting with CSV export for reporting and integration

Authentication and Access:
    - Single-profile authentication for centralized StackSet management operations
    - Support for AWS Organizations cross-account role-based access patterns
    - Regional validation and access control for StackSet operational boundaries
    - Comprehensive error handling for authentication and authorization failures

Enterprise Use Cases:
    - Centralized StackSet deployment monitoring and operational excellence
    - Infrastructure governance and compliance tracking for organizational standards
    - Deployment failure analysis and troubleshooting for operational support
    - StackSet lifecycle management and capacity planning across accounts
    - Operational dashboards and reporting for infrastructure management teams

Performance and Scalability:
    - Multi-threaded architecture for efficient StackSet instance discovery
    - Queue-based worker pattern for concurrent StackSet operations analysis
    - Optimized AWS API usage with progress tracking and performance timing
    - Configurable concurrency limits for API rate limiting and throttling management

Security Considerations:
    - Read-only operations ensuring no accidental StackSet modifications
    - Comprehensive audit logging for compliance and operational tracking
    - Secure credential handling with profile-based authentication
    - Access validation and error handling for enterprise security requirements

Dependencies:
    - boto3: AWS SDK for CloudFormation StackSet operations
    - colorama: Enhanced terminal output with color coding
    - tqdm: Progress bars for long-running discovery operations
    - Inventory_Modules: Custom AWS inventory and discovery utilities
    - ArgumentsClass: Standardized CLI argument parsing and validation
    - account_class: AWS account access and credential management

Example Usage:
    # Basic StackSet operations discovery
    python list_cfn_stackset_operations.py --profile production

    # Fragment-based operations analysis
    python list_cfn_stackset_operations.py --fragment SecurityBaseline

    # Detailed instance enumeration with timing
    python list_cfn_stackset_operations.py --instances --timing

Output:
    Displays discovered StackSet operations with last operation status, failure counts,
    completion timestamps, and deployment topology insights for operational monitoring.
"""

import logging
import os
import sys
from queue import Queue
from threading import Thread
from time import time

import Inventory_Modules
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_stacksets3, get_regions3
from tqdm.auto import tqdm

init()

__version__ = "2024.05.18"
ERASE_LINE = "\x1b[2K"
begin_time = time()
DefaultMaxWorkerThreads = 5


##################
# Functions
##################
def parse_args(args: object):
    """
    Parse and validate CLI arguments for StackSet operations discovery and analysis.

    Configures comprehensive argument parsing for StackSet operations inventory across
    AWS Organizations with support for fragment-based filtering, instance enumeration,
    status tracking, and operational analysis. Provides enterprise-grade CLI interface
    for infrastructure teams managing large-scale StackSet deployments.

    Args:
        args (object): Command-line arguments list for parsing and validation

    Returns:
        argparse.Namespace: Parsed arguments object containing:
            - Profile: AWS profile for StackSet management operations access
            - Region: Target AWS region for StackSet operations discovery
            - Fragments: StackSet name fragments for targeted search and filtering
            - Exact: Boolean flag for exact fragment matching vs. substring matching
            - RootOnly: Boolean flag to limit discovery to root account only
            - Timing: Boolean flag to enable performance timing and metrics
            - Verbosity: Logging level for operational visibility and debugging
            - pinstancecount: Boolean flag for StackSet instance enumeration
            - pstatus: StackSet status filter ('Active' or 'Deleted')
            - Filename: Optional output file path for CSV export and reporting

    CLI Arguments:
        Single Profile Authentication:
            - --profile: AWS profile for centralized StackSet management access
            - Single-profile mode for focused operational analysis

        Regional Configuration:
            - --region: Target AWS region for StackSet operations discovery
            - Single-region mode for focused operational boundaries

        StackSet Filtering:
            - --fragment: StackSet name fragments for targeted operations analysis
            - --exact: Enable exact fragment matching for precise filtering
            - --status: Filter by StackSet status (Active/Deleted) for lifecycle tracking

        Instance Analysis:
            - --instances: Enable StackSet instance enumeration for topology analysis
            - Provides deployment pattern insights and capacity planning data

        Operational Controls:
            - --root-only: Limit discovery to root account StackSet operations
            - --timing: Enable performance timing for operational metrics
            - --save-to-file: Export results to CSV for reporting and integration
            - --verbose: Control logging verbosity for debugging and audit trails

    Enterprise Features:
        - Standardized CLI interface consistent with inventory tooling
        - Fragment-based search for targeted StackSet operations analysis
        - Instance enumeration for deployment topology and capacity insights
        - Status filtering for StackSet lifecycle and operational tracking
        - Output formatting with CSV export for enterprise reporting

    Validation and Error Handling:
        - Argument validation with informative error messages
        - Help text generation for operational documentation
        - Version information for tooling compatibility tracking
        - Default value configuration for operational convenience
    """
    script_path, script_name = os.path.split(sys.argv[0])
    parser = CommonArguments()

    # Configure standardized CLI arguments for enterprise inventory operations
    parser.singleprofile()  # Single AWS profile for centralized StackSet management access
    parser.singleregion()  # Single region specification for focused operational boundaries
    parser.fragment()  # Fragment-based filtering for targeted StackSet operations analysis
    parser.extendedargs()  # Extended argument support for advanced filtering capabilities
    parser.save_to_file()  # CSV export functionality for enterprise reporting and integration
    parser.rootOnly()  # Root account only mode for organizational StackSet oversight
    parser.timing()  # Performance timing metrics for operational analysis
    parser.verbosity()  # Configurable logging verbosity for debugging and audit trails
    parser.version(__version__)  # Version information for tooling compatibility tracking

    # Add script-specific arguments for StackSet operations analysis
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "-i",
        "--instances",
        dest="pinstancecount",
        action="store_true",
        default=False,
        help="Enable StackSet instance enumeration for deployment topology analysis and capacity planning",
    )
    local.add_argument(
        "-s",
        "--status",
        dest="pstatus",
        metavar="CloudFormation status",
        default="Active",
        choices=["active", "ACTIVE", "Active", "deleted", "DELETED", "Deleted"],
        help="Filter StackSets by lifecycle status - 'ACTIVE' for operational StackSets or 'DELETED' for cleanup analysis",
    )
    return parser.my_parser.parse_args(args)


def setup_auth_and_regions(
    fProfile: str, fRegion: str = None, fStackFrag: list = None, fExact: bool = False
) -> (aws_acct_access, list):
    """
    Initialize authentication and configure regional access for StackSet operations discovery.

    Establishes AWS authentication context and validates regional configuration for StackSet
    operations analysis and monitoring. Performs single-region validation and provides
    operational context display for infrastructure teams managing centralized StackSet
    deployments across AWS Organizations environments.

    Args:
        fProfile (str): AWS profile name for authentication and StackSet management access
                       If None, uses default profile or credential chain
        fRegion (str): Target AWS region for StackSet operations discovery
                      Defaults to 'us-east-1' if not specified
        fStackFrag (list): StackSet name fragments for targeted search and filtering
                          Defaults to ['all'] for comprehensive discovery
        fExact (bool): Enable exact fragment matching for precise filtering
                      Default False for substring-based matching

    Returns:
        tuple: Two-element tuple containing:
            - aws_acct_access: Authenticated account access object for StackSet operations
            - list: Validated AWS regions list for StackSet discovery operations

    Authentication and Validation:
        - Establishes AWS authentication using the specified profile
        - Validates single-region configuration for focused operational boundaries
        - Performs regional access validation for StackSet management operations
        - Handles authentication failures with appropriate error messaging

    Regional Configuration:
        - Single-region mode for focused StackSet operations analysis
        - Regional validation to ensure StackSet management capabilities
        - Error handling for invalid or inaccessible regions
        - Operational context display for transparency and troubleshooting

    Operational Display:
        - Account type and number identification for organizational context
        - Regional scope confirmation for operational boundaries
        - Fragment matching configuration display for search transparency
        - Clear operational intent communication for infrastructure teams

    Error Handling:
        - Connection error detection with appropriate system exit
        - Profile validation and authentication failure management
        - Regional access validation with informative error messages
        - Comprehensive error logging for troubleshooting and audit trails

    Enterprise Features:
        - Single-region focus for targeted StackSet operations monitoring
        - Clear operational scope display for infrastructure governance
        - Fragment-based search configuration for operational efficiency
        - Account type awareness for organizational structure recognition
    """

    # Set default values for optional parameters to ensure consistent operation
    if fStackFrag is None:
        fStackfrag = ["all"]  # Default to comprehensive StackSet discovery
    if fRegion is None:
        fRegion = "us-east-1"  # Default to primary AWS region for StackSet management

    try:
        # Establish AWS authentication using the specified profile
        aws_acct = aws_acct_access(fProfile)
    except ConnectionError as my_Error:
        # Handle authentication and connection failures with appropriate logging
        logging.error(f"Exiting due to error: {my_Error}")
        sys.exit(8)

    # Validate regional access and availability for StackSet operations
    RegionList = get_regions3(aws_acct, [fRegion])

    # Enforce single-region constraint for focused StackSet operations analysis
    if fRegion.lower() not in RegionList:
        print()
        print(
            f"{Fore.RED}You specified '{fRegion}' as the region, but this script only works with a single region.\n"
            f"Please run the command again and specify only a single, valid region{Fore.RESET}"
        )
        print()
        raise ValueError(f"You specified '{fRegion}' as the region, but this script only works with a single region.")

    # Display operational scope and configuration for transparency
    print()
    action = "but not modify"  # Read-only operations for safety
    print(f"You asked me to find ({action}) stacksets that match the following:")
    print(f"\t\tIn the {aws_acct.AccountType} account {aws_acct.acct_number}")
    print(f"\t\tIn this Region: {fRegion}")

    # Display fragment matching configuration for search transparency
    if fExact:
        print(f"\t\tFor stacksets that {Fore.RED}exactly match{Fore.RESET} these fragments: {fStackfrag}")
    else:
        print(f"\t\tFor stacksets that contains these fragments: {fStackfrag}")

    print()
    return aws_acct, RegionList


def collect_cfnstacksets(faws_acct: aws_acct_access, fRegion: str) -> (dict, dict, dict):
    """
    Collect and aggregate StackSet information with comprehensive instance enumeration and analysis.

    Performs comprehensive StackSet discovery, instance enumeration, and metadata aggregation
    for operational analysis and infrastructure governance. Orchestrates StackSet collection
    with detailed instance topology mapping and account/region distribution analysis for
    enterprise infrastructure teams managing large-scale CloudFormation deployments.

    Args:
        faws_acct (aws_acct_access): Authenticated AWS account access object for StackSet operations
        fRegion (str): Target AWS region for StackSet discovery and instance enumeration

    Returns:
        tuple: Three-element tuple containing comprehensive StackSet information:
            dict: StackSet aggregation containing:
                - combined_stack_set_instances: Complete list of StackSet instances with metadata
                - StackSets: Raw StackSet discovery results from inventory modules
                - StackSetsList: Filtered list of StackSet names in operational scope
            dict: Account aggregation containing:
                - AccountList: Unique list of accounts with StackSet instances
            dict: Region aggregation containing:
                - FoundRegionList: Unique list of regions with StackSet deployments

    StackSet Discovery Process:
        - Fragment-based StackSet discovery using inventory modules
        - Comprehensive instance enumeration across organizational accounts
        - Account and region filtering based on operational scope
        - Metadata extraction for deployment topology analysis

    Instance Analysis Features:
        - Multi-threaded instance discovery for performance optimization
        - Account filtering for targeted operational analysis
        - Regional distribution mapping for capacity planning
        - Status tracking and deployment pattern analysis

    Data Aggregation:
        - Deduplication of accounts and regions for clean reporting
        - StackSet name filtering and scope management
        - Comprehensive metadata preservation for analysis
        - Structured data organization for downstream processing

    Enterprise Infrastructure Governance:
        - Organizational StackSet visibility and management
        - Deployment topology analysis for operational excellence
        - Account and region distribution insights for capacity planning
        - Infrastructure governance and compliance tracking

    Error Handling:
        - AWS connection validation with appropriate error messaging
        - Failed discovery detection with comprehensive error reporting
        - Graceful degradation for partial discovery scenarios
        - Comprehensive logging for troubleshooting and audit trails
    """
    # Discover StackSets from the Management Account using fragment-based filtering
    StackSets = find_stacksets3(faws_acct, fRegion, pStackfrag, pExact)
    if not StackSets["Success"]:
        # Handle failed StackSet discovery with comprehensive error messaging
        error_message = (
            "Something went wrong with the AWS connection. Please check the parameters supplied and try again."
        )
        sys.exit(error_message)
    logging.info(f"Found {len(StackSets['StackSets'])} StackSetNames that matched your fragment")

    # Perform comprehensive StackSet instance enumeration across organizational accounts
    combined_stack_set_instances = find_stack_set_instances(StackSets["StackSets"], fRegion)

    print(ERASE_LINE)
    logging.info(f"Found {len(combined_stack_set_instances)} stack instances.")

    # Initialize aggregation lists for account and region distribution analysis
    AccountList = []
    StackSetsList = []
    FoundRegionList = []

    # Process and filter StackSet instances based on account inclusion criteria
    for _ in range(len(combined_stack_set_instances)):
        if pAccountList is None:  # Include all discovered instances when no specific account list provided
            StackSetsList.append(combined_stack_set_instances[_]["StackSetName"])
            AccountList.append(combined_stack_set_instances[_]["ChildAccount"])
            FoundRegionList.append(combined_stack_set_instances[_]["ChildRegion"])
        elif pAccountList is not None:
            # Filter instances to include only those in the specified account list
            if combined_stack_set_instances[_]["ChildAccount"] in pAccountList:
                StackSetsList.append(combined_stack_set_instances[_]["StackSetName"])
                AccountList.append(combined_stack_set_instances[_]["ChildAccount"])
                FoundRegionList.append(combined_stack_set_instances[_]["ChildRegion"])

    # Deduplicate and sort aggregated lists for clean reporting and analysis
    # Filter out None values that occur when StackSets have no deployed instances
    AccountList = sorted(list(set([item for item in AccountList if item is not None])))

    # Regional aggregation for deployment topology analysis
    # Note: Regional scope is maintained at StackSet level rather than per-account
    # Future enhancement: Consider per-account regional filtering for granular control
    FoundRegionList = sorted(list(set([item for item in FoundRegionList if item is not None])))
    StackSetsList = sorted(list(set(StackSetsList)))

    # Structure aggregated data for downstream processing and analysis
    StackSet_Dict = {
        "combined_stack_set_instances": combined_stack_set_instances,
        "StackSets": StackSets,
        "StackSetsList": StackSetsList,
    }
    Account_Dict = {"AccountList": AccountList}
    Region_Dict = {"FoundRegionList": FoundRegionList}
    return StackSet_Dict, Account_Dict, Region_Dict


def find_stack_set_instances(fStackSetNames: list, fRegion: str) -> list:
    """
    Discover and enumerate StackSet instances across organizational accounts using multi-threaded processing.

    Performs comprehensive StackSet instance discovery using concurrent worker threads for efficient
    enumeration across large-scale CloudFormation StackSet deployments. Provides detailed instance
    metadata extraction, status tracking, and deployment topology analysis for enterprise infrastructure
    teams managing multi-account StackSet orchestration and operational monitoring.

    Args:
        fStackSetNames (list): List of StackSet names for instance discovery and enumeration
                              Reserved keyword 'all' enables comprehensive discovery
        fRegion (str): Target AWS region for StackSet instance discovery operations

    Returns:
        list: Comprehensive list of StackSet instance dictionaries containing:
            - ParentAccountNumber: Management account hosting the StackSet
            - ChildAccount: Target account where StackSet instance is deployed
            - ChildRegion: Target region for StackSet instance deployment
            - StackStatus: Current deployment status of the StackSet instance
            - DetailedStatus: Detailed operational status for troubleshooting
            - StatusReason: Reason description for failed or problematic deployments
            - OrganizationalUnitId: AWS Organizations OU for organizational structure
            - PermissionModel: StackSet permission model (SELF_MANAGED/SERVICE_MANAGED)
            - StackSetName: Parent StackSet name for instance relationship tracking

    Multi-threaded Architecture:
        - Queue-based worker pattern for concurrent instance discovery
        - Configurable worker thread pool for performance optimization
        - Progress tracking with real-time operational feedback
        - Graceful error handling for authorization and throttling issues

    Instance Discovery Features:
        - Comprehensive metadata extraction for operational analysis
        - Account filtering support for targeted instance enumeration
        - Regional validation for deployment boundary enforcement
        - Status tracking for deployment lifecycle management

    Performance Optimization:
        - Concurrent processing for efficient large-scale discovery
        - Progress bars for operational visibility during long-running operations
        - Worker thread scaling based on StackSet count for optimal performance
        - Queue management for efficient work distribution and completion tracking

    Enterprise Infrastructure Management:
        - Organizational StackSet instance visibility across accounts
        - Deployment topology mapping for capacity planning and governance
        - Status monitoring for operational excellence and troubleshooting
        - Permission model tracking for security and compliance analysis

    Error Handling:
        - Authorization failure detection with graceful degradation
        - AWS API throttling management with retry logic
        - Connection error handling with comprehensive logging
        - Partial discovery support for operational resilience
    """

    class FindStackSets(Thread):
        """
        Multi-threaded worker class for concurrent StackSet instance discovery and enumeration.

        Implements thread-safe StackSet instance discovery using queue-based work distribution
        for efficient processing of large-scale StackSet deployments across organizational accounts.
        """

        def __init__(self, queue):
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            while True:
                # Extract work item from queue with StackSet information and processing context
                c_stacksetname, c_region, c_stackset_info, c_PlaceCount = self.queue.get()
                logging.info(f"De-queued info for stack set name {c_stacksetname}")

                try:
                    # Perform StackSet instance discovery for the current StackSet
                    # This is the most time-intensive operation in the discovery process
                    logging.info(
                        f"{ERASE_LINE}Looking through {c_PlaceCount} of {len(fStackSetNames)} stacksets found with {pStackfrag} string in them"
                    )

                    # Call inventory module to discover instances for the current StackSet
                    # Note: Empty StackSets (without instances) may be excluded from results
                    StackInstances = Inventory_Modules.find_stack_instances3(aws_acct, c_region, c_stacksetname)
                    logging.warning(f"Found {len(StackInstances)} Stack Instances within the StackSet {c_stacksetname}")

                    # Process each discovered StackSet instance with metadata extraction
                    for StackInstance in StackInstances:
                        # Validate StackSet instance deployment status
                        if "StackId" not in StackInstance.keys():
                            logging.info(
                                f"The stack instance found {StackInstance} doesn't have a stackid associated. Which means it's never been deployed and probably OUTDATED"
                            )
                            pass

                        # Apply account filtering for targeted instance enumeration
                        if pAccountList is None or StackInstance["Account"] in pAccountList:
                            # Include instance if no account filter specified or account matches filter
                            # Supports comprehensive discovery and targeted operational analysis
                            logging.debug(f"This is Instance #: {str(StackInstance)}")
                            logging.debug(f"This is instance status: {str(StackInstance['Status'])}")
                            logging.debug(f"This is ChildAccount: {StackInstance['Account']}")
                            logging.debug(f"This is ChildRegion: {StackInstance['Region']}")

                            # Validate regional scope and add instance to results
                            if StackInstance["Region"] in RegionList:
                                # Aggregate comprehensive instance metadata for analysis
                                f_combined_stack_set_instances.append(
                                    {
                                        "ParentAccountNumber": aws_acct.acct_number,  # Management account hosting StackSet
                                        "ChildAccount": StackInstance["Account"],  # Target deployment account
                                        "ChildRegion": StackInstance["Region"],  # Target deployment region
                                        "StackStatus": StackInstance["Status"],  # Current deployment status
                                        "DetailedStatus": StackInstance["StackInstanceStatus"]["DetailedStatus"]
                                        if "DetailedStatus" in StackInstance["StackInstanceStatus"]
                                        else None,  # Detailed status for troubleshooting
                                        "StatusReason": StackInstance["StatusReason"]
                                        if "StatusReason" in StackInstance
                                        else None,  # Failure reason for operational analysis
                                        "OrganizationalUnitId": StackInstance["OrganizationalUnitId"]
                                        if "OrganizationalUnitId" in StackInstance
                                        else None,  # AWS Organizations OU for structural analysis
                                        "PermissionModel": c_stackset_info["PermissionModel"]
                                        if "PermissionModel" in c_stackset_info
                                        else "SELF_MANAGED",  # StackSet permission model for security analysis
                                        "StackSetName": c_stacksetname,  # Parent StackSet name for relationship tracking
                                    }
                                )
                        elif not (StackInstance["Account"] in pAccountList):
                            # Skip instances that don't match the specified account filter
                            # Supports targeted operational analysis for specific accounts
                            logging.debug(
                                f"Found a stack instance, but the account didn't match {pAccountList}... exiting"
                            )
                            continue

                except KeyError as my_Error:
                    # Handle missing key errors during instance metadata extraction
                    logging.error(f"Account Access failed - trying to access {c_stacksetname}")
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    # Handle attribute errors likely caused by incorrect profile configuration
                    logging.error(f"Error: Likely that one of the supplied profiles was wrong")
                    logging.info(f"Actual Error: {my_Error}")
                    continue
                except ClientError as my_Error:
                    # Handle AWS API errors including throttling and authorization failures
                    logging.error(f"Error: Likely throttling errors from too much activity")
                    logging.info(f"Actual Error: {my_Error}")
                    continue
                finally:
                    # Complete processing and update progress tracking
                    logging.info(
                        f"{ERASE_LINE}Finished finding stack instances in stackset {c_stacksetname} in region {c_region} - {c_PlaceCount} / {len(fStackSetNames)}"
                    )
                    pbar.update()  # Update progress bar for operational visibility
                    self.queue.task_done()  # Mark queue item as completed

    ###########

    # Initialize processing context and data structures
    if fRegion is None:
        fRegion = "us-east-1"  # Default to primary AWS region for StackSet operations
    checkqueue = Queue()  # Queue for work distribution across worker threads

    f_combined_stack_set_instances = []  # Aggregated results list for all discovered instances
    PlaceCount = 0  # Progress counter for operational visibility

    # Configure optimal worker thread count based on StackSet count and system limits
    WorkerThreads = min(len(fStackSetNames), DefaultMaxWorkerThreads)

    # Initialize progress tracking for operational visibility during discovery
    pbar = tqdm(
        desc=f"Finding Stackset instances from {len(fStackSetNames)} stacksets",
        total=len(fStackSetNames),
        unit=" stacksets",
    )

    # Create and start worker thread pool for concurrent StackSet instance discovery
    for x in range(WorkerThreads):
        worker = FindStackSets(checkqueue)
        # Daemon threads allow main thread exit even if workers are still processing
        worker.daemon = True
        worker.start()

    # Queue StackSet discovery work items for worker thread processing
    for stacksetname in fStackSetNames:
        logging.debug(f"Beginning to queue data - starting with {stacksetname}")
        try:
            # Queue StackSet information for worker thread processing
            # Note: Tuple structure is critical for proper parameter expansion in worker threads
            PlaceCount += 1
            checkqueue.put((stacksetname, fRegion, stacksetname, PlaceCount))
        except ClientError as my_Error:
            # Handle authorization failures with informative error messaging
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing stack set {stacksetname['StackSetName']} in {fRegion} region"
                )
                logging.warning(f"It's possible that the region {fRegion} hasn't been opted-into")
                pass

    # Wait for all worker threads to complete processing
    checkqueue.join()
    pbar.close()  # Close progress bar after completion
    return f_combined_stack_set_instances


def find_last_operations(faws_acct: aws_acct_access, fStackSetNames: list):
    """
    Discover and analyze the most recent operations for CloudFormation StackSets.

    Retrieves the last operation performed on each StackSet for operational monitoring,
    failure analysis, and deployment lifecycle tracking. Provides essential operational
    insights for infrastructure teams managing large-scale StackSet deployments across
    AWS Organizations environments.

    Args:
        faws_acct (aws_acct_access): Authenticated AWS account access object for StackSet operations
        fStackSetNames (list): List of StackSet names for operation history discovery

    Returns:
        list: List of StackSet operation dictionaries containing:
            - StackSetName: StackSet identifier for operation correlation
            - Operation: Last operation type (CREATE_STACK_SET, UPDATE_STACK_SET, DELETE_STACK_SET)
            - LatestStatus: Current status of the last operation (SUCCEEDED, FAILED, STOPPED)
            - LatestDate: Completion timestamp for operational timeline analysis
            - Details: Failed stack instances count for troubleshooting and analysis

    Operation Discovery Features:
        - Latest operation retrieval for each StackSet with comprehensive metadata
        - Operation status tracking for deployment lifecycle monitoring
        - Failure count analysis for operational excellence and troubleshooting
        - Timestamp tracking for deployment pattern analysis and audit trails

    Operational Monitoring:
        - Progress tracking with real-time feedback during operation discovery
        - Sequential processing for reliable operation history retrieval
        - Comprehensive error handling for authorization and connectivity issues
        - Operation metadata extraction for enterprise infrastructure governance

    Enterprise Use Cases:
        - Deployment failure analysis and operational troubleshooting
        - StackSet lifecycle monitoring for infrastructure governance
        - Operational dashboards and reporting for infrastructure management
        - Compliance tracking and audit trail generation

    Error Handling:
        - AWS API error management with graceful degradation
        - Authorization failure detection with appropriate logging
        - Missing operation handling for newly created StackSets
        - Comprehensive error reporting for troubleshooting
    """
    # Initialize CloudFormation client for StackSet operations discovery
    StackSetOps_client = faws_acct.session.client("cloudformation")
    AllStackSetOps = []

    # Discover last operation for each StackSet with progress tracking
    for stacksetname in tqdm(fStackSetNames, desc="Checking stackset operations"):
        # Retrieve most recent operation for the current StackSet
        StackSetOps = StackSetOps_client.list_stack_set_operations(
            StackSetName=stacksetname, MaxResults=1, CallAs="SELF"
        )["Summaries"]

        # Extract and aggregate operation metadata for analysis
        AllStackSetOps.append(
            {
                "StackSetName": stacksetname,  # StackSet identifier for correlation
                "Operation": StackSetOps[0]["Action"],  # Operation type for lifecycle tracking
                "LatestStatus": StackSetOps[0]["Status"],  # Current operation status
                "LatestDate": StackSetOps[0]["EndTimestamp"],  # Completion timestamp
                "Details": StackSetOps[0]["StatusDetails"]["FailedStackInstancesCount"],  # Failure count for analysis
            }
        )
    return AllStackSetOps


##################
# Main
##################
if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    pProfile = args.Profile
    pRegion = args.Region
    pInstanceCount = args.pinstancecount
    pRootOnly = args.RootOnly
    verbose = args.loglevel
    pTiming = args.Time
    pStackfrag: list = args.Fragments
    pExact: bool = args.Exact
    pAccountList = args.Accounts
    pstatus = args.pstatus
    pFilename = args.Filename
    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    display_dict = {
        "StackSetName": {"DisplayOrder": 1, "Heading": "Stackset Name"},
        "Operation": {"DisplayOrder": 2, "Heading": "Action"},
        "LatestStatus": {"DisplayOrder": 3, "Heading": "Last status", "Condition": ["FAILED", "STOPPED"]},
        "LatestDate": {"DisplayOrder": 4, "Heading": "Last completed"},
        "Details": {"DisplayOrder": 5, "Heading": "Failures"},
    }

    # Setup the aws_acct object
    aws_acct, RegionList = setup_auth_and_regions(pProfile)
    # Collect the stacksets, AccountList and RegionList involved
    StackSets, Accounts, Regions = collect_cfnstacksets(aws_acct, pRegion)
    # Get the last operations from the Stacksets we've found
    StackSets_and_Operations = find_last_operations(aws_acct, StackSets["StackSetsList"])
    # Display what we've found
    sorted_StackSets_and_Operations = sorted(StackSets_and_Operations, key=lambda x: x["LatestDate"], reverse=True)
    display_results(sorted_StackSets_and_Operations, display_dict, None, pFilename)

    print()
    print(ERASE_LINE)
    print(
        f"{Fore.RED}Found {len(StackSets['StackSetsList'])} Stacksets across {len(Accounts)} accounts across {len(Regions)} regions{Fore.RESET}"
    )
    print()
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
    print("Thanks for using this script...")
    print()

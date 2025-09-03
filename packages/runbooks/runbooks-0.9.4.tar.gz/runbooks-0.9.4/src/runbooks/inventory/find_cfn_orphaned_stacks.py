#!/usr/bin/env python3

"""
AWS CloudFormation Orphaned Stack Detection and Analysis Script

This enterprise-grade script provides comprehensive detection and analysis of orphaned CloudFormation
stacks across multi-account AWS Organizations environments. Designed for infrastructure teams managing
CloudFormation StackSets at scale, offering automated orphaned stack identification, cross-account
stack reconciliation, and organizational governance support for infrastructure cleanup and compliance.

Key Features:
    - Multi-account, multi-region CloudFormation stack and StackSet reconciliation
    - Orphaned stack instance detection comparing StackSet definitions with deployed stacks
    - Fragment-based filtering for targeted orphaned stack analysis
    - Comprehensive cross-account stack inventory and comparison analysis
    - Enterprise governance support with account exclusion and targeted analysis
    - Multi-threaded processing for efficient large-scale stack discovery

Orphaned Stack Detection:
    - Cross-references StackSet instances in management account with actual stacks in member accounts
    - Identifies StackSet instances that exist in management account but not in target accounts
    - Discovers stacks in member accounts that are not managed by any StackSet
    - Provides detailed mismatch analysis for infrastructure cleanup and governance
    - Supports fragment-based filtering for targeted orphaned stack identification

Authentication & Access:
    - AWS Organizations support for centralized StackSet and stack management
    - Cross-account role assumption for organizational stack visibility
    - Regional validation and multi-region support for comprehensive coverage
    - Profile-based authentication with comprehensive credential management

Performance & Scalability:
    - Multi-threaded stack discovery for efficient large-scale processing
    - Progress tracking and performance metrics for operational visibility
    - Efficient credential management for multi-account stack enumeration
    - Memory-efficient processing for extensive StackSet and stack inventories

Enterprise Use Cases:
    - Infrastructure cleanup and orphaned resource identification
    - StackSet governance and stack instance lifecycle management
    - Organizational compliance monitoring and drift detection
    - Infrastructure migration and consolidation planning
    - Automated cleanup recommendation generation

Security & Compliance:
    - Account exclusion capabilities preventing analysis on sensitive accounts
    - Comprehensive audit logging for stack analysis and discovery operations
    - Regional access validation and opt-in status verification
    - Safe credential handling with automatic session management

Historical Context:
    This script was originally created to support the "move_stack_instances.py" script by providing
    recovery capabilities for stack instances that might be lost during StackSet migration operations.
    While the move script now has built-in recovery, this script remains valuable for identifying
    and analyzing orphaned stack instances that may occur during normal StackSet operations.

Dependencies:
    - boto3: AWS SDK for CloudFormation and StackSet API access
    - colorama: Terminal output formatting and colored display
    - Custom modules: Inventory_Modules, ArgumentsClass, account_class for enterprise operations

Output Format:
    - Comprehensive tabular analysis of orphaned stack instances
    - Separate reporting for parent StackSet instances and child stacks
    - Performance timing metrics and operational summaries
    - Optional file export for further analysis and reporting
"""

import logging
import sys
from os.path import split
from time import time

from account_class import aws_acct_access
from ArgumentsClass import CommonArguments

# import simplejson as json
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import (
    display_results,
    find_stack_instances3,
    find_stacks2,
    find_stacksets3,
    get_credentials_for_accounts_in_org,
    get_regions3,
    print_timings,
)

init()
__version__ = "2024.05.18"
ERASE_LINE = "\x1b[2K"
begin_time = time()


##################
# Functions
##################


def parse_args(fargs):
    """
    Parse and validate command-line arguments for CloudFormation orphaned stack detection operations.

    Configures comprehensive argument parsing for orphaned stack analysis across multi-account AWS
    Organizations environments. Supports enterprise-grade CloudFormation management with profile
    configuration, regional targeting, fragment-based filtering, and operational controls for
    large-scale stack reconciliation and orphaned resource identification.

    Args:
        fargs (list): Command-line argument list for orphaned stack detection configuration

    Returns:
        argparse.Namespace: Parsed argument namespace containing:
            - Profile: AWS profile for organizational CloudFormation access
            - Region: Home region for StackSet management and control operations
            - Fragments: Stack name fragments for targeted orphaned stack filtering
            - Exact: Boolean flag for exact fragment matching vs substring matching
            - Accounts: Specific account list for targeted orphaned stack analysis
            - SkipAccounts: Account exclusion list for selective stack enumeration
            - SkipProfiles: Profile exclusion list for selective discovery operations
            - AccessRoles: Custom IAM roles for cross-account StackSet access
            - Filename: Output file path for orphaned stack analysis results
            - Time: Performance timing flag for operational metrics and optimization
            - loglevel: Logging verbosity for operational visibility and troubleshooting
            - SearchRegionList: Target regions for comprehensive stack instance analysis

    CLI Argument Categories:
        - Single profile support for centralized StackSet management and analysis
        - Single home region for StackSet control plane operations
        - Fragment-based filtering for targeted orphaned stack identification
        - Extended arguments including account filtering and performance timing
        - Role-based access controls for cross-account StackSet operations
        - File export capabilities for analysis results and reporting
        - Multi-region search support for comprehensive stack instance coverage

    Enterprise Features:
        - Organizational profile management for centralized StackSet governance
        - Regional filtering for geo-distributed StackSet architectures
        - Account inclusion/exclusion for selective orphaned stack analysis
        - Performance monitoring with timing metrics for operational optimization
        - Comprehensive logging controls for audit and compliance requirements
        - Custom role support for enhanced security and access control

    Orphaned Stack Detection Features:
        - Home region specification for StackSet control plane access
        - Multi-region search capabilities for comprehensive stack instance analysis
        - Fragment-based filtering for targeted orphaned stack identification
        - Account-specific analysis for focused cleanup and governance operations

    Usage Examples:
        - Basic analysis: --profile mgmt-profile --region us-east-1
        - Fragment filtering: --fragment "MyApp" --exact for targeted analysis
        - Multi-region search: --SearchRegions us-east-1 us-west-2 eu-west-1
        - Account targeting: --accounts 123456789012 234567890123 for specific analysis
        - Performance timing: --timing for operational metrics and optimization analysis
    """
    script_path, script_name = split(sys.argv[0])  # Extract script name for argument grouping

    # Configure comprehensive argument parsing for orphaned stack detection
    parser = CommonArguments()
    parser.singleprofile()  # Single AWS profile for centralized StackSet management
    parser.singleregion()  # Single home region for StackSet control operations
    parser.fragment()  # Fragment-based filtering for targeted stack identification
    parser.extendedargs()  # Extended arguments including account filtering and timing
    parser.rolestouse()  # Custom IAM roles for cross-account StackSet access
    parser.save_to_file()  # File export capabilities for analysis results
    parser.verbosity()  # Logging verbosity controls for operational visibility
    parser.timing()  # Performance timing metrics for operational optimization
    parser.version(__version__)

    # Script-specific arguments for orphaned stack detection operations
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "-R",
        "--SearchRegions",
        help="Target regions for comprehensive stack instance analysis and orphaned stack detection. "
        "Supports multi-region search capabilities for thorough StackSet reconciliation across "
        "geo-distributed AWS infrastructure deployments.",
        default=["all"],  # Default to all regions for comprehensive analysis
        nargs="*",  # Multiple regions supported for targeted analysis
        metavar="region-name",
        dest="SearchRegionList",
    )

    return parser.my_parser.parse_args(fargs)


def setup_auth_and_regions(fProfile: str, f_AccountList: list, f_Region: str, f_args) -> (aws_acct_access, list, list):
    """
    Initialize AWS authentication and configure regional scope for orphaned stack detection operations.

    Establishes comprehensive AWS Organizations access and validates regional scope for CloudFormation
    orphaned stack analysis across multi-account environments. Performs input validation, credential
    initialization, account enumeration, and operational parameter display for enterprise-grade
    StackSet governance and infrastructure cleanup operations.

    Args:
        fProfile (str): AWS profile name for organizational CloudFormation access
                       None uses default credentials or profile configuration
        f_AccountList (list): Specific account list for targeted orphaned stack analysis
                            None includes all organizational accounts for comprehensive coverage
        f_Region (str): Home region for StackSet control plane operations and management
                       Must be a single, valid AWS region for StackSet operations
        f_args: Parsed command-line arguments containing:
            - SearchRegionList: Target regions for stack instance search operations
            - SkipAccounts: Account exclusion list for selective analysis
            - Fragments: Stack name fragments for targeted filtering
            - Exact: Boolean flag for exact fragment matching
            - Accounts: Account inclusion list for focused analysis

    Returns:
        tuple: Three-element tuple containing:
            - aws_acct_access: Initialized AWS account access object with organizational context
            - AccountList: List of account IDs for orphaned stack analysis scope
            - RegionList: List of regions for comprehensive stack instance search operations

    Authentication & Validation:
        - Profile validation ensuring single profile specification for centralized management
        - AWS Organizations connectivity validation with comprehensive error handling
        - Regional validation ensuring home region is available and properly configured
        - Account list filtering supporting both inclusion and exclusion patterns

    Organizational Context:
        - Account enumeration across AWS Organizations for comprehensive analysis scope
        - Management account identification and organizational hierarchy establishment
        - Child account filtering based on account inclusion/exclusion specifications
        - Account status validation ensuring active accounts for analysis operations

    Operational Display:
        - Comprehensive parameter summary for operational visibility and confirmation
        - Fragment filtering specifications with exact vs substring matching display
        - Account scope display showing targeted vs comprehensive analysis mode
        - Regional scope display for multi-region stack instance search operations

    Error Handling:
        - Profile validation with informative error messages and graceful exit
        - AWS connectivity error handling with detailed diagnostic information
        - Regional validation preventing invalid region specifications
        - Comprehensive input validation with clear error messaging

    Enterprise Features:
        - AWS Organizations support for centralized StackSet governance
        - Account filtering capabilities for selective orphaned stack analysis
        - Multi-region support for comprehensive stack instance coverage
        - Operational parameter display for audit trails and confirmation
    """
    # Perform comprehensive input validation for profile specification
    if isinstance(fProfile, str) or fProfile is None:
        pass  # Valid profile specification (string or None for default)
    else:  # Invalid profile type (list, integer, etc.) - should be caught at argparse level
        print(
            f"{Fore.RED}You specified an invalid profile name. This script only allows for one profile at a time. Please try again.{Fore.RESET}"
        )
        sys.exit(7)

    # Initialize AWS account access with comprehensive error handling
    try:
        aws_acct = aws_acct_access(fProfile)
    except ConnectionError as my_Error:
        logging.error(f"Exiting due to error: {my_Error}")
        sys.exit(8)

    # Configure regional scope for orphaned stack detection operations
    AllRegions = get_regions3(aws_acct)  # All available regions for validation
    RegionList = get_regions3(aws_acct, f_args.SearchRegionList)  # Target regions for stack instance search

    # Validate home region specification ensuring single region for StackSet control plane
    if f_Region.lower() not in AllRegions:
        print(
            f"{Fore.RED}You specified '{f_Region}' as the region, but this script only works with a single region.\n"
            f"Please run the command again and specify only a single, valid region{Fore.RESET}"
        )
        sys.exit(9)

    print()

    # Configure account scope for orphaned stack analysis with organizational context
    ChildAccounts = []  # List of account dictionaries: AccountId, AccountEmail, AccountStatus, MgmtAccount

    if f_AccountList is None:
        # Include all organizational accounts for comprehensive orphaned stack analysis
        ChildAccounts = aws_acct.ChildAccounts
    else:
        # Filter accounts based on user-specified inclusion list for targeted analysis
        for account in aws_acct.ChildAccounts:
            if account["AccountId"] in f_AccountList:
                ChildAccounts.append(
                    {
                        "AccountId": account["AccountId"],  # Account identifier for stack analysis
                        "AccountEmail": account["AccountEmail"],  # Account contact for audit context
                        "AccountStatus": account["AccountStatus"],  # Account operational status
                        "MgmtAccount": account["MgmtAccount"],  # Management account reference
                    }
                )

    # Extract account IDs for efficient processing and operational context
    AccountList = [account["AccountId"] for account in ChildAccounts]

    # Display comprehensive operational parameters for confirmation and audit trails
    print(f"You asked me to find orphaned stacksets that match the following:")
    print(f"\t\tIn the {aws_acct.AccountType} account {aws_acct.acct_number}")
    print(f"\t\tIn this home Region: {f_Region}")

    # Display search region configuration if specified
    print(
        f"\t\tFor stackset instances whose region matches this region fragment: {f_args.SearchRegionList}"
    ) if f_args.SearchRegionList is not None else ""

    # Display account exclusion list if specified
    print(
        f"While skipping these accounts:\n{Fore.RED}{f_args.SkipAccounts}{Fore.RESET}"
    ) if f_args.SkipAccounts is not None else ""

    # Display fragment filtering configuration with exact vs substring matching
    if f_args.Exact:
        print(f"\t\tFor stacksets that {Fore.RED}exactly match{Fore.RESET}: {f_args.Fragments}")
    else:
        print(
            f"\t\tFor stacksets that contain th{'is fragment' if len(f_args.Fragments) == 1 else 'ese fragments'}: {f_args.Fragments}"
        )

    # Display account scope configuration for targeted vs comprehensive analysis
    if f_args.Accounts is None:
        print(f"\t\tFor stack instances across all accounts")
    else:
        print(
            f"\t\tSpecifically to find th{'ese' if len(f_args.Accounts) > 1 else 'is'} account number{'s' if len(f_args.Accounts) > 1 else ''}: {f_args.Accounts}"
        )
    print()

    return aws_acct, AccountList, RegionList


def find_stacks_within_child_accounts(fall_credentials, fFragmentlist: list = None, threads: int = 25):
    """
    Discover and enumerate CloudFormation stacks across multiple organizational accounts using multi-threading.

    Performs comprehensive CloudFormation stack discovery using multi-threaded processing to efficiently
    inventory stacks across large-scale AWS Organizations environments. Designed for orphaned stack
    detection by providing detailed stack metadata extraction from member accounts for reconciliation
    with StackSet instances in the management account.

    Args:
        fall_credentials (list): List of credential dictionaries for cross-account stack discovery containing:
            - AccountId: AWS account number for CloudFormation stack access
            - Region: Target AWS region for stack enumeration
            - Success: Boolean indicating credential validity and access status
            - AccountNumber: Alternative account identifier format
        fFragmentlist (list): Stack name fragments for targeted search and filtering
                             None defaults to ["all"] for comprehensive stack discovery
        threads (int): Maximum number of worker threads for concurrent processing
                      Default 25, automatically limited by credential count for optimization

    Returns:
        list: Comprehensive list of stack dictionaries containing:
            - StackName: CloudFormation stack name identifier
            - StackId: Unique AWS CloudFormation stack identifier
            - StackStatus: Current operational status
            - AccountId: AWS account containing the stack
            - Region: AWS region where stack is deployed
            - Additional stack metadata for orphaned stack analysis

    Multi-threaded Architecture:
        - Queue-based worker pattern for concurrent stack discovery
        - Configurable worker thread pool with automatic scaling
        - Thread-safe stack aggregation for comprehensive result collection
        - Graceful error handling for authorization and access issues

    Stack Discovery Features:
        - Multi-account, multi-region CloudFormation stack enumeration
        - Fragment-based filtering for targeted stack identification
        - Comprehensive stack metadata extraction for governance analysis
        - Cross-account stack visibility for organizational inventory
        - Regional stack distribution analysis for operational planning

    Performance Optimization:
        - Concurrent processing for efficient large-scale stack discovery
        - Worker thread scaling based on credential count for optimal performance
        - Queue management for efficient work distribution and completion tracking
        - Memory-efficient processing for extensive stack inventories

    Enterprise Infrastructure Governance:
        - Organizational stack visibility across accounts and regions
        - Stack metadata aggregation for compliance and audit tracking
        - Fragment-based search capabilities for targeted stack management
        - Comprehensive error handling for operational resilience and troubleshooting

    Error Handling:
        - Authorization failure detection with graceful degradation
        - AWS API error management with comprehensive logging
        - Credential validation and failure tracking for multi-account operations
        - Regional access validation preventing unauthorized stack enumeration
    """
    from queue import Queue
    from threading import Thread

    class FindStacks(Thread):
        """
        Multi-threaded worker class for concurrent CloudFormation stack discovery.

        Implements thread-safe stack discovery using queue-based work distribution for
        efficient processing of CloudFormation stacks across organizational accounts
        and regions.
        """

        def __init__(self, fqueue: Queue):
            Thread.__init__(self)
            self.queue = fqueue

        def run(self):
            while True:
                # Extract work item from queue with account credentials and processing context
                c_credential, c_fragmentlist = self.queue.get()

                # Discover CloudFormation stacks with comprehensive error handling
                try:
                    if c_credential["Success"]:
                        # Execute stack discovery using validated credentials
                        account_and_region_stacks = find_stacks2(c_credential, c_credential["Region"], c_fragmentlist)
                        AllFoundStacks.extend(account_and_region_stacks)
                    else:
                        # Skip failed credentials with informative logging
                        logging.info(
                            f"Skipping {c_credential['AccountNumber']} in {c_credential['Region']} as we failed to successfully access"
                        )
                except Exception as my_Error:
                    # Handle comprehensive stack discovery errors with detailed logging
                    logging.error(
                        f"Error accessing account {c_credential['AccountId']} in region {c_credential['Region']} "
                        f"Skipping this account"
                    )
                    logging.info(f"Actual Error: {my_Error}")
                finally:
                    # Mark queue item as completed for work distribution tracking
                    self.queue.task_done()

    # Initialize multi-threaded processing infrastructure for stack discovery
    checkqueue = Queue()  # Queue for work distribution across worker threads

    # Configure fragment filtering with default comprehensive discovery
    if fFragmentlist is None:
        fFragmentlist = ["all"]  # Default to all stacks for comprehensive analysis

    # Note: Account and skip account filtering is handled by upstream credential management
    # This function receives pre-filtered credentials based on user specifications

    # Configure optimal worker thread count based on credential count and system limits
    WorkerThreads = min(len(fall_credentials), threads)

    # Initialize aggregated results collection for discovered stacks
    AllFoundStacks = []

    # Create and start worker thread pool for concurrent stack discovery
    for x in range(WorkerThreads):
        worker = FindStacks(checkqueue)
        # Daemon threads allow main thread exit even if workers are still processing
        worker.daemon = True
        worker.start()

    # Queue stack discovery work items for worker thread processing
    for credential in fall_credentials:
        logging.info(f"Queueing account {credential['AccountId']} and {credential['Region']}")
        try:
            # Queue account and region combination for worker thread processing
            # Note: Tuple structure is critical for proper parameter expansion in worker threads
            checkqueue.put((credential, fFragmentlist))
        except ClientError as my_Error:
            # Handle authorization failures with informative error messaging
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']}"
                )
                logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass

    # Wait for all worker threads to complete stack discovery processing
    checkqueue.join()
    return AllFoundStacks


def reconcile_between_parent_stacksets_and_children_stacks(f_parent_stack_instances: list, f_child_stacks: list):
    """
    Perform comprehensive reconciliation analysis between StackSet instances and deployed stacks.

    Executes detailed cross-referencing between CloudFormation StackSet instances managed in the
    management account and actual CloudFormation stacks deployed in member accounts to identify
    orphaned resources, missing deployments, and infrastructure governance issues requiring cleanup
    or remediation across organizational AWS environments.

    Args:
        f_parent_stack_instances (list): List of StackSet instance dictionaries from management account containing:
            - StackId: Unique CloudFormation stack identifier for matching
            - Account: Target account for StackSet instance deployment
            - Region: Target region for StackSet instance deployment
            - StackSetId: Parent StackSet identifier for organizational context
            - Status: Current StackSet instance operational status
            - StatusReason: Detailed status reason for troubleshooting
        f_child_stacks (list): List of actual stack dictionaries from member accounts containing:
            - StackId: Unique CloudFormation stack identifier for matching
            - StackName: CloudFormation stack name (StackSet- prefix indicates StackSet managed)
            - AccountNumber: Account containing the deployed stack
            - Region: Region where stack is deployed
            - StackStatus: Current stack operational status

    Processing Logic:
        1. Cross-reference StackSet instances with deployed stacks using StackId matching
        2. Mark matched instances to identify properly managed StackSet deployments
        3. Identify parent StackSet instances without corresponding child stacks (missing deployments)
        4. Identify child stacks without corresponding parent StackSet instances (orphaned stacks)
        5. Filter child stacks to include only StackSet-managed stacks (StackSet- prefix)
        6. Generate comprehensive reports for infrastructure cleanup and governance

    Orphaned Stack Detection:
        - Parent instances not in child stacks indicate failed or missing StackSet deployments
        - Child stacks not in parent instances indicate orphaned StackSet-managed resources
        - Cross-account stack reconciliation ensuring organizational infrastructure alignment
        - Performance timing for large-scale reconciliation operations

    Reporting & Display:
        - Separate tabular reports for parent and child orphaned resources
        - Sortable display with account, region, and resource identifiers
        - Optional file export for further analysis and remediation planning
        - Comprehensive operational metrics and reconciliation statistics

    Enterprise Governance:
        - Infrastructure cleanup recommendations based on orphaned resource identification
        - StackSet lifecycle management insights for operational optimization
        - Organizational compliance monitoring through resource reconciliation
        - Automated remediation planning through detailed orphaned resource analysis

    Performance Monitoring:
        - Comparison metrics tracking reconciliation operation efficiency
        - Timing analysis for large-scale infrastructure reconciliation operations
        - Memory-efficient processing for extensive StackSet and stack inventories
        - Operational visibility through detailed progress and result logging
    """
    # Initialize reconciliation tracking metrics for operational monitoring
    child_comparisons = 0  # Counter for child stack comparison operations
    parent_comparisons = 0  # Counter for parent StackSet instance comparisons
    i = 0  # Match counter for successful reconciliation tracking

    # Execute comprehensive cross-referencing between parent StackSet instances and child stacks
    for ParentInstance in f_parent_stack_instances:
        parent_comparisons += 1  # Track parent instance processing for metrics

        # Compare current parent instance against all child stacks for matching
        for Childinstance in f_child_stacks:
            child_comparisons += 1  # Track child stack comparison operations

            # Perform StackId-based matching to identify properly managed StackSet deployments
            if "StackId" in ParentInstance.keys() and Childinstance["StackId"] == ParentInstance["StackId"]:
                i += 1  # Increment successful match counter

                # Log successful matches with timing for performance analysis
                logging.debug(f"**** Match {i}!! **** - {time() - begin_time:.6f}")
                logging.debug(f"Childinstance: {Childinstance['StackId']}")
                logging.debug(f"ParentInstance:  {ParentInstance['StackId']}")

                # Mark both instances as matched for filtering operations
                Childinstance["Matches"] = ParentInstance["StackId"]  # Child stack matches parent
                ParentInstance["Matches"] = Childinstance["StackId"]  # Parent instance matches child
            else:
                continue  # No match found, proceed to next comparison

    # Display reconciliation performance metrics for operational visibility
    print_timings(
        pTiming,
        verbose,
        begin_time,
        f"We compared {len(AllChildStackInstances)} child stacks against {len(AllParentStackInstancesInStackSets)} parent stack instances",
    )

    # Identify StackSet instances in management account without corresponding deployed stacks
    Parent_Instances_Not_In_Children_Stacks = [
        x for x in AllParentStackInstancesInStackSets if "Matches" not in x.keys()
    ]

    # Identify StackSet-managed stacks in member accounts without corresponding parent instances
    # Filter for StackSet-managed stacks only (StackSet- prefix) to exclude regular account stacks
    Child_Instances_Not_In_Parent_Stacks = [
        x for x in AllChildStackInstances if "Matches" not in x.keys() and (x["StackName"].find("StackSet-") > -1)
    ]

    # Display comprehensive reconciliation results for operational analysis
    print()
    print(
        f"We found {len(Parent_Instances_Not_In_Children_Stacks)} parent stack instances that are not in the child stacks"
    )
    print(f"We found {len(Child_Instances_Not_In_Parent_Stacks)} child stacks that are not in the parent stacksets")
    print()

    # Generate detailed tabular reports for orphaned resource analysis (if verbose logging enabled)
    if verbose < 50:
        # Configure display formatting for parent StackSet instances without child stacks
        parent_display_dict = {
            "Account": {"DisplayOrder": 1, "Heading": "Acct Number"},  # Target account for deployment
            "Region": {"DisplayOrder": 2, "Heading": "Region"},  # Target region for deployment
            "StackSetId": {"DisplayOrder": 3, "Heading": "StackSet Id"},  # Parent StackSet identifier
            "Status": {"DisplayOrder": 4, "Heading": "Status"},  # StackSet instance status
            "StatusReason": {"DisplayOrder": 5, "Heading": "Possible Reason"},  # Detailed status reason
        }

        # Display and export parent instances without corresponding child stacks
        print(f"Stack Instances in the Root Account that don't appear in the Children")
        sorted_Parent_Instances_Not_In_Children_Stacks = sorted(
            Parent_Instances_Not_In_Children_Stacks, key=lambda k: (k["Account"], k["Region"], k["StackSetId"])
        )
        display_results(
            sorted_Parent_Instances_Not_In_Children_Stacks, parent_display_dict, None, f"{pFilename}-Parent"
        )

        # Configure display formatting for child stacks without parent StackSet instances
        child_display_dict = {
            "AccountNumber": {"DisplayOrder": 1, "Heading": "Acct Number"},  # Account containing orphaned stack
            "Region": {"DisplayOrder": 2, "Heading": "Region"},  # Region containing orphaned stack
            "StackName": {"DisplayOrder": 3, "Heading": "Stack Name"},  # Orphaned stack name
            "StackStatus": {"DisplayOrder": 4, "Heading": "Status"},  # Current stack status
        }

        # Display and export child stacks without corresponding parent StackSet instances
        print(f"Stacks in the Children accounts that don't appear in the Root Stacksets")
        sorted_Child_Instances_Not_In_Parent_Stacks = sorted(
            Child_Instances_Not_In_Parent_Stacks, key=lambda k: (k["AccountNumber"], k["Region"], k["StackName"])
        )
        display_results(sorted_Child_Instances_Not_In_Parent_Stacks, child_display_dict, None, f"{pFilename}-Child")


##################
# Main
##################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfile = args.Profile
    pRegion = args.Region
    pSearchRegionList = args.SearchRegionList
    pAccounts = args.Accounts
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pFilename = args.Filename
    pRootOnly = False  # It doesn't make any sense to think that this script would be used for only the root account
    pExact = args.Exact
    pRoles = args.AccessRoles
    verbose = args.loglevel
    pTiming = args.Time
    pFragments = args.Fragments
    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    ERASE_LINE = "\x1b[2K"
    begin_time = time()

    # Setup credentials and regions (filtered by what they wanted to check)
    aws_acct, AccountList, RegionList = setup_auth_and_regions(pProfile, pAccounts, pRegion, args)
    # Determine the accounts we're checking
    print_timings(pTiming, verbose, begin_time, "Just setup account and region list")
    AllCredentials = get_credentials_for_accounts_in_org(
        aws_acct, pSkipAccounts, pRootOnly, AccountList, pProfile, RegionList, pRoles, pTiming
    )
    print_timings(
        pTiming,
        verbose,
        begin_time,
        f"Finished getting {len(AllCredentials)} credentials for all accounts and regions in spec...",
    )

    # Connect to every account, and in every region specified, to find all stacks
    print(
        f"Now finding all stacks across {'all' if pAccounts is None else (len(pAccounts) * len(RegionList))} accounts and regions under the {aws_acct.AccountType} account {aws_acct.acct_number}"
    )
    AllChildStackInstances = find_stacks_within_child_accounts(AllCredentials, pFragments)
    print_timings(
        pTiming, verbose, begin_time, f"Just finished getting {len(AllChildStackInstances)} children stack instances"
    )
    # and then compare them with the stackset instances managed within the Root account, and find anything that doesn't match

    # This is the list of stacksets in the root account
    AllParentStackSets = find_stacksets3(aws_acct, pRegion, pFragments, pExact)
    print_timings(
        pTiming, verbose, begin_time, f"Just finished getting {len(AllParentStackSets['StackSets'])} parent stack sets"
    )
    print(f"Now getting all the stack instances for all {len(AllParentStackSets)} stacksets")
    # This will be the listing of the stack_instances in each of the stacksets in the root account
    AllParentStackInstancesInStackSets = []
    for stackset_name, stackset_attributes in AllParentStackSets["StackSets"].items():
        StackInstancesInStackSets = find_stack_instances3(
            aws_acct, pRegion, stackset_name, faccountlist=AccountList, fregionlist=RegionList
        )
        # TODO: Filter out skipped / closed accounts within the stacksets
        AllParentStackInstancesInStackSets.extend(StackInstancesInStackSets)
    print_timings(
        pTiming,
        verbose,
        begin_time,
        f"Just finished getting {len(AllParentStackInstancesInStackSets)} parent stack instances",
    )
    # Then compare the stack_instances in the root account with the stack_instances in the child accounts to see if anything is missing
    print(f"We found {len(AllChildStackInstances)} stack instances in the {len(AccountList)} child accounts")
    print(
        f"We found {len(AllParentStackInstancesInStackSets)} stack instances in the {len(AllParentStackSets['StackSets'])} stacksets in the root account"
    )
    print(f"Now cross-referencing these to find if there are any orphaned stacks...")
    # Find the stacks that are in the root account but not in the child accounts
    # And find any stack instances in the children accounts that are not in the root account
    # And display them to the screen...
    reconcile_between_parent_stacksets_and_children_stacks(AllParentStackInstancesInStackSets, AllChildStackInstances)

    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

    print()
    print("Thanks for using this script...")
    print()

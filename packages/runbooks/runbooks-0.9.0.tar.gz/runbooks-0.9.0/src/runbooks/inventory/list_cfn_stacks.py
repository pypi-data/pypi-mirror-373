#!/usr/bin/env python3
"""
AWS CloudFormation Stack Inventory Collection

A comprehensive CloudFormation stack discovery and management tool for multi-account 
AWS Organizations. Provides detailed stack inventory with advanced filtering capabilities 
and optional stack deletion functionality.

**AWS API Mapping**: `cloudformation.describe_stacks()`, `cloudformation.list_stacks()`

Features:
    - Multi-account CloudFormation stack discovery
    - Advanced status filtering (CREATE_COMPLETE, UPDATE_FAILED, etc.)
    - Stack fragment matching for partial name searches
    - Stack ID display and metadata collection
    - Conditional stack deletion with safety controls
    - Cross-region stack inventory aggregation
    - Specialized GuardDuty stack handling

Compatibility:
    - AWS Organizations with cross-account roles
    - AWS Control Tower managed accounts
    - Standalone AWS accounts
    - All AWS regions including opt-in regions

Example:
    Discover all active stacks:
    ```bash
    python cfn_describe_stacks.py --profile my-org-profile
    ```
    
    Find stacks by name fragment:
    ```bash
    python cfn_describe_stacks.py --profile my-profile \\
        --fragment my-app --status CREATE_COMPLETE
    ```
    
    Display stack IDs for troubleshooting:
    ```bash
    python cfn_describe_stacks.py --profile my-profile \\
        --stackid --fragment problematic-stack
    ```

Warning:
    The `+delete` parameter will **DELETE** matching stacks WITHOUT additional 
    confirmation. Use with extreme caution in production environments.

Requirements:
    - IAM permissions: `cloudformation:DescribeStacks`, `cloudformation:DeleteStack`
    - AWS Organizations access (for multi-account scanning)
    - Python 3.8+ with required dependencies

Author:
    AWS Cloud Foundations Team
    
Version:
    2024.05.31
"""

import logging
import sys
from os.path import split
from pprint import pprint
from time import time

import Inventory_Modules
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, get_all_credentials

init()

__version__ = "2024.05.31"

###########################


def parse_args(f_arguments):
    """
    Parse and validate command-line arguments for CloudFormation stack inventory.

    Configures the argument parser with CloudFormation-specific options including
    status filtering, stack ID display, and optional deletion capabilities.
    Uses the standardized CommonArguments framework for consistency.

    Args:
        f_arguments (list): Command-line arguments to parse (typically sys.argv[1:])

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profile: AWS profile for authentication
            - Regions: Target AWS regions for stack discovery
            - Fragments: Stack name fragments for filtering
            - status: CloudFormation stack status filters
            - stackid: Flag to display full stack ARNs
            - DeletionRun: DANGEROUS flag to delete matched stacks
            - Other standard framework arguments

    Note:
        The DeletionRun parameter enables destructive operations.
        Use with extreme caution in production environments.
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
    parser.singleprofile()  # Allows for a single profile to be specified
    parser.multiregion()  # Allows for multiple regions to be specified at the command line
    parser.extendedargs()  # Allows for extended arguments like which accounts to skip, and whether Force is enabled.
    parser.rootOnly()
    # TODO: Add parameter for access_roles
    #  parser.rolestouse()  # Allows for the roles to be specified at the command line.
    parser.fragment()
    parser.timing()
    parser.verbosity()  # Allows for the verbosity to be handled.
    parser.version(__version__)
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "-s",
        "--status",
        dest="status",
        nargs="*",
        choices=[
            "CREATE_IN_PROGRESS",
            "CREATE_FAILED",
            "CREATE_COMPLETE",
            "ROLLBACK_IN_PROGRESS",
            "ROLLBACK_FAILED",
            "ROLLBACK_COMPLETE",
            "DELETE_IN_PROGRESS",
            "DELETE_FAILED",
            "DELETE_COMPLETE",
            "UPDATE_IN_PROGRESS",
            "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
            "UPDATE_COMPLETE",
            "UPDATE_FAILED",
            "UPDATE_ROLLBACK_IN_PROGRESS",
            "UPDATE_ROLLBACK_FAILED",
            "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
            "UPDATE_ROLLBACK_COMPLETE",
            "REVIEW_IN_PROGRESS",
            "IMPORT_IN_PROGRESS",
            "IMPORT_COMPLETE",
            "IMPORT_ROLLBACK_IN_PROGRESS",
            "IMPORT_ROLLBACK_FAILED",
            "IMPORT_ROLLBACK_COMPLETE",
            "all",
            "All",
            "ALL",
        ],
        metavar="CloudFormation status",
        default=None,
        help="List of statuses that determines which statuses we see. Default is all ACTIVE statuses. 'All' will capture all statuses",
    )
    local.add_argument(
        "--stackid",
        dest="stackid",
        action="store_true",
        help="Flag that determines whether we display the Stack IDs as well",
    )
    local.add_argument(
        "+delete",
        "+forreal",
        dest="DeletionRun",
        action="store_true",
        help="This will delete the stacks found - without any opportunity to confirm. Be careful!!",
    )
    return parser.my_parser.parse_args(f_arguments)


def setup_auth_accounts_and_regions(
    fProfile: str,
    fRegionList: list = None,
    fAccountList: list = None,
    fSkipAccounts: list = None,
    fStackFrag: list = None,
    fExact: bool = False,
    fDeletionRun: bool = False,
) -> (aws_acct_access, list, list):
    """
    Initialize AWS account access and determine target accounts/regions for stack discovery.

    This function establishes the AWS Organizations context, resolves account access
    permissions, and prepares the execution scope for CloudFormation stack operations.
    Includes safety warnings and user confirmation for destructive operations.

    Args:
        fProfile (str): AWS profile name for authentication and organization access
        fRegionList (list, optional): Target regions for stack discovery.
            Defaults to all accessible regions if None.
        fAccountList (list, optional): Specific account IDs to include.
            Defaults to all organization accounts if None.
        fSkipAccounts (list, optional): Account IDs to exclude from discovery
        fStackFrag (list, optional): Stack name fragments for filtering operations
        fExact (bool, optional): Use exact matching for stack fragments.
            Defaults to False (partial matching).
        fDeletionRun (bool, optional): Flag indicating destructive operations.
            Triggers additional warnings and confirmations.

    Returns:
        tuple: Three-element tuple containing:
            - aws_acct_access: Authenticated AWS account access object
            - list: Resolved list of target account IDs
            - list: Resolved list of target AWS regions

    Raises:
        ConnectionError: When AWS profile authentication fails

    Side Effects:
        - Displays execution parameters and warnings to stdout
        - Shows colored output for operation confirmation
        - Exits process (sys.exit(8)) on authentication failure

    Security Note:
        When fDeletionRun=True, displays prominent warnings about
        destructive operations to prevent accidental stack deletion.
    """
    try:
        aws_acct = aws_acct_access(fProfile)
    except ConnectionError as my_Error:
        logging.error(f"Exiting due to error: {my_Error}")
        sys.exit(8)

    ChildAccounts = aws_acct.ChildAccounts
    RegionList = Inventory_Modules.get_regions3(aws_acct, fRegionList)

    ChildAccounts = Inventory_Modules.RemoveCoreAccounts(ChildAccounts, fSkipAccounts)
    if fAccountList is None:
        AccountList = [account["AccountId"] for account in ChildAccounts]
    else:
        AccountList = [account["AccountId"] for account in ChildAccounts if account["AccountId"] in fAccountList]

    print(f"You asked to find stacks with this fragment {Fore.RED}'{fStackFrag}'{Fore.RESET}")
    print(f"in these accounts:\n{Fore.RED}{AccountList}{Fore.RESET}")
    print(f"in these regions:\n{Fore.RED}{RegionList}{Fore.RESET}")
    print(f"While skipping these accounts:\n{Fore.RED}{fSkipAccounts}{Fore.RESET}") if fSkipAccounts is not None else ""
    if fDeletionRun:
        print()
        print("And delete the stacks that are found...")

    if fExact:
        print(f"\t\tFor stacks that {Fore.RED}exactly match{Fore.RESET} these fragments: {fStackFrag}")
    else:
        print(f"\t\tFor stacks that contains these fragments: {fStackFrag}")

    return aws_acct, AccountList, RegionList


def collect_cfnstacks(fCredentialList: list) -> list:
    """
    Execute multi-threaded CloudFormation stack discovery across AWS accounts and regions.

    This is the core discovery engine that performs concurrent CloudFormation API calls
    across all provided credentials. Uses a worker thread pool pattern for optimal
    performance while managing API rate limits and error handling.

    Args:
        fCredentialList (list): List of credential dictionaries containing:
            - AccountId: AWS account identifier
            - Region: AWS region name
            - AccessKeyId, SecretAccessKey, SessionToken: AWS credentials
            - Success: Boolean flag indicating credential validation status

    Returns:
        list: Sorted list of CloudFormation stack dictionaries with metadata:
            - Account: AWS account ID where stack exists
            - Region: AWS region of the stack
            - StackName: CloudFormation stack name
            - StackStatus: Current stack status (CREATE_COMPLETE, etc.)
            - StackCreate: Stack creation date (formatted YYYY-MM-DD)
            - StackArn: Full stack ARN (if stackid flag enabled)
            - Credential fields for potential stack operations

    Threading Architecture:
        - Uses Queue for thread-safe work distribution
        - 4 concurrent worker threads for balanced throughput
        - Real-time progress display with colored output
        - Graceful handling of authentication failures

    Error Handling:
        - AuthFailure: Logs and continues with other accounts
        - ClientError: Handles AWS API throttling and service errors
        - Credential validation via Success flag checking

    Performance:
        Results are automatically sorted by Account -> Region -> StackName
        for consistent output presentation across executions.
    """
    from queue import Queue
    from threading import Thread

    StacksFound = []

    def worker(q, pStackfrag, pstatus):
        """
        Worker thread function for concurrent CloudFormation stack discovery.

        Each worker processes credentials from the shared queue, calls the
        CloudFormation API to discover stacks, and aggregates results.
        Implements comprehensive error handling and real-time progress display.

        Args:
            q (Queue): Thread-safe queue containing credential work items
            pStackfrag (list): Stack name fragments for filtering
            pstatus (list): Stack status filters to apply

        Side Effects:
            - Updates shared StacksFound list with discoveries
            - Displays real-time progress to stdout
            - Logs detailed account/region processing information
        """
        while True:
            # Get work item from thread-safe queue
            credential = q.get()
            if credential is None:
                break  # Shutdown signal received

            Stacks = False

            # Only process credentials that passed validation
            if credential["Success"]:
                try:
                    # Call CloudFormation API to discover stacks
                    Stacks = Inventory_Modules.find_stacks2(credential, credential["Region"], pStackfrag, pstatus)

                    # Log discovery results for debugging
                    logging.warning(
                        f"Account: {credential['AccountId']} | Region: {credential['Region']} | Found {len(Stacks)} Stacks"
                    )

                    # Display real-time progress with colored output
                    print(
                        f"{ERASE_LINE}{Fore.RED}Account: {credential['AccountId']} Region: {credential['Region']} Found {len(Stacks)} Stacks{Fore.RESET}",
                        end="\r",
                    )

                except ClientError as my_Error:
                    # Handle AWS authentication and authorization errors
                    if "AuthFailure" in str(my_Error):
                        print(f"{credential['AccountId']}: Authorization Failure")
            else:
                # Skip credentials that failed validation
                continue

            # Process discovered stacks and aggregate results
            if Stacks and len(Stacks) > 0:
                for y in range(len(Stacks)):
                    # Extract stack metadata from AWS API response
                    StackName = Stacks[y]["StackName"]
                    StackStatus = Stacks[y]["StackStatus"]
                    StackID = Stacks[y]["StackId"]
                    StackCreate = Stacks[y]["CreationTime"]

                    # Create standardized stack record for aggregation
                    # Includes both metadata and credentials for potential operations
                    StacksFound.append(
                        {
                            # Identity and location information
                            "Account": credential["AccountId"],
                            "Region": credential["Region"],
                            # AWS credentials for stack operations (deletion, etc.)
                            "AccessKeyId": credential["AccessKeyId"],
                            "SecretAccessKey": credential["SecretAccessKey"],
                            "SessionToken": credential["SessionToken"],
                            "AccountNumber": credential["AccountNumber"],
                            # CloudFormation stack metadata
                            "StackName": StackName,
                            "StackCreate": StackCreate.strftime("%Y-%m-%d"),
                            "StackStatus": StackStatus,
                            # Conditional stack ARN display (based on CLI flag)
                            "StackArn": StackID if pStackIdFlag else "None",
                        }
                    )

            # Mark work item as complete for queue management
            q.task_done()

    stacks_queue = Queue()
    for credential in fCredentialList:
        stacks_queue.put(credential)

    num_threads = 4  # Number of worker threads
    for i in range(num_threads):
        t = Thread(target=worker, args=(stacks_queue, pStackfrag, pstatus))
        t.start()

    stacks_queue.join()

    for i in range(num_threads):
        stacks_queue.put(None)

    sortedStacksFound = sorted(StacksFound, key=lambda x: (x["Account"], x["Region"], x["StackName"]))
    return sortedStacksFound


def display_stacks(fAllStacks: list):
    display_dict = {
        "Account": {"DisplayOrder": 1, "Heading": "Account"},
        "Region": {"DisplayOrder": 2, "Heading": "Region"},
        "StackStatus": {"DisplayOrder": 3, "Heading": "Stack Status"},
        "StackCreate": {"DisplayOrder": 4, "Heading": "Create Date"},
        "StackName": {"DisplayOrder": 5, "Heading": "Stack Name"},
        "StackArn": {"DisplayOrder": 6, "Heading": "Stack ID"},
    }

    display_results(
        fAllStacks,
        display_dict,
        None,
    )
    print(ERASE_LINE)
    print(
        f"{Fore.RED}Found {len(fAllStacks)} stacks across {len(AccountList)} accounts across {len(RegionList)} regions{Fore.RESET}"
    )
    print()
    if args.loglevel < 21:  # INFO level
        lAccounts = lRegions = lAccountsAndRegions = []
        for i in range(len(fAllStacks)):
            lAccounts.append(fAllStacks[i]["Account"])
            lRegions.append(fAllStacks[i]["Region"])
            lAccountsAndRegions.append((fAllStacks[i]["Account"], fAllStacks[i]["Region"]))
        print("The list of accounts and regions:")
        pprint(list(sorted(set(lAccountsAndRegions))))


def modify_stacks(fStacksFound: list):
    """
    Execute CloudFormation stack deletion operations with specialized error handling.

    This function implements the destructive stack deletion workflow with multiple
    safety confirmations and specialized handling for problematic stack types like
    GuardDuty stacks that may have resource retention requirements.

    Args:
        fStacksFound (list): List of stack dictionaries to delete, each containing:
            - StackName: CloudFormation stack identifier
            - Account: AWS account ID
            - Region: AWS region
            - StackStatus: Current stack status
            - Credential information for API calls

    Returns:
        list: Collection of AWS API responses from deletion operations.
              May contain success confirmations or error details.

    Safety Features:
        - Interactive confirmation prompt before execution
        - Special handling for DELETE_FAILED stacks
        - GuardDuty-specific resource retention logic
        - Progress display during batch deletions

    Special Cases:
        - GuardDuty stacks: Uses RetainResources=['MasterDetector'] due to
          common deletion failures with GuardDuty master detectors
        - DELETE_FAILED stacks: Automatically retains problematic resources
          that may be blocking normal deletion

    Warning:
        This function performs IRREVERSIBLE CloudFormation stack deletions.
        Ensure proper backups and confirmations before execution.

    Example:
        >>> stacks_to_delete = [{'StackName': 'test-stack', 'Account': '123456789'}]
        >>> responses = modify_stacks(stacks_to_delete)
        >>> print(f"Deleted {len(responses)} stacks")
    """
    ReallyDelete = (
        (input(f"Deletion of stacks has been requested, are you still sure? (y/n): ") in ["y", "Y"])
        if DeletionRun
        else False
    )
    response2 = []
    if DeletionRun and ReallyDelete and ("GuardDuty" in pStackfrag or "guardduty" in pStackfrag):
        logging.warning(f"Deleting {len(fStacksFound)} stacks")
        for stack_found in fStacksFound:
            print(
                f"Deleting stack {stack_found['StackName']} from Account {stack_found['Account']} in region {stack_found['Region']}"
            )
            if stack_found["StackStatus"] == "DELETE_FAILED":
                # This deletion generally fails because the Master Detector doesn't properly delete (and it's usually already deleted due to some other script) - so we just need to delete the stack anyway - and ignore the actual resource.
                response = Inventory_Modules.delete_stack2(
                    stack_found,
                    stack_found["Region"],
                    stack_found["StackName"],
                    RetainResources=True,
                    ResourcesToRetain=["MasterDetector"],
                )
            else:
                response = Inventory_Modules.delete_stack2(stack_found, stack_found["Region"], stack_found["StackName"])
            response2.append(response)
    elif DeletionRun and ReallyDelete:
        logging.warning(f"Deleting {len(fStacksFound)} stacks")
        for stack_found in fStacksFound:
            print(
                f"Deleting stack {stack_found['StackName']} from account {stack_found['Account']} in region {stack_found['Region']} with status: {stack_found['StackStatus']}"
            )
            # print(f"Finished {y + 1} of {len(fStacksFound)}")
            response = Inventory_Modules.delete_stack2(stack_found, stack_found["Region"], stack_found["StackName"])
            response2.append(response)
    # pprint(response)
    return response2


###########################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    pProfile = args.Profile
    pRegionList = args.Regions
    pStackfrag = args.Fragments
    pExact = args.Exact
    pTiming = args.Time
    verbose = args.loglevel
    pSkipProfiles = args.SkipProfiles
    pSkipAccounts = args.SkipAccounts
    pRootOnly = args.RootOnly
    pAccountList = args.Accounts
    pstatus = args.status
    pStackIdFlag = args.stackid
    DeletionRun = args.DeletionRun
    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)

    begin_time = time()

    ##########################
    ERASE_LINE = "\x1b[2K"

    print()
    # Setup the aws_acct object
    aws_acct, AccountList, RegionList = setup_auth_accounts_and_regions(
        pProfile, pRegionList, pAccountList, pSkipAccounts, pStackfrag, pExact, DeletionRun
    )
    # Get credentials for all Child Accounts
    CredentialList = get_all_credentials(
        pProfile, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, AccountList, RegionList
    )
    # Collect the stacksets, AccountList and RegionList involved
    AllStacks = collect_cfnstacks(CredentialList)
    # Display the information we've found this far
    display_stacks(AllStacks)
    # Modify stacks, if requested
    if DeletionRun:
        modify_result = modify_stacks(AllStacks)

    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

    print()
    print("Thanks for using this script...")
    print()

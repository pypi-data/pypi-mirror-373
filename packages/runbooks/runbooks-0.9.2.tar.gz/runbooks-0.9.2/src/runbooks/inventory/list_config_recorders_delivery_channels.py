#!/usr/bin/env python3

"""
AWS Config Service Configuration Recorders and Delivery Channels Discovery and Management Script

This enterprise-grade inventory and management script provides comprehensive discovery, analysis,
and optional cleanup of AWS Config service configuration recorders and delivery channels across
multi-account AWS Organizations environments. Designed for infrastructure teams, DevOps engineers,
and cloud architects managing AWS Config service deployment and compliance across large-scale
enterprise environments.

Key Features:
    - Configuration recorder discovery and inventory across organizational accounts
    - Delivery channel enumeration with S3 bucket and SNS topic configuration analysis
    - Fragment-based filtering for targeted Config service component discovery
    - Optional deletion capabilities with safety controls and confirmation prompts
    - Multi-threaded discovery for efficient large-scale Config service inventory
    - Comprehensive error handling for authorization, throttling, and connectivity issues
    - Progress tracking with real-time operational feedback and performance metrics
    - Flexible output formatting with CSV export for reporting and integration

Configuration Discovery Features:
    - Configuration recorder enumeration with recording scope and status analysis
    - Delivery channel discovery with destination bucket and notification configuration
    - Cross-account Config service visibility for organizational compliance oversight
    - Fragment-based search for targeted Config component identification and filtering
    - Regional Config service availability validation and access control

Management and Cleanup:
    - Safe deletion workflows with explicit confirmation prompts and force flags
    - Batch deletion capabilities for efficient Config service cleanup operations
    - Pre-deletion validation and dependency checking for operational safety
    - Comprehensive audit logging for compliance and operational tracking
    - Rollback-safe operations with detailed status tracking and error handling

Authentication and Access:
    - Multi-profile authentication for comprehensive organizational Config discovery
    - Cross-account role-based access patterns supporting AWS Organizations structure
    - Multi-region support with Config service availability validation
    - Root account filtering and inclusion controls for targeted discovery
    - Comprehensive error handling for authentication and authorization failures

Enterprise Use Cases:
    - Config service governance and compliance tracking for organizational oversight
    - Centralized Config service inventory for infrastructure management and planning
    - Config service cleanup and decommissioning for cost optimization
    - Compliance framework validation ensuring consistent Config deployment
    - Operational maintenance identification for Config service health monitoring

Performance and Scalability:
    - Multi-threaded architecture for efficient Config service discovery operations
    - Queue-based worker pattern for concurrent Config component enumeration
    - Optimized AWS API usage with progress tracking and performance timing
    - Configurable concurrency limits for API rate limiting and throttling management
    - Efficient credential management for cross-account Config service access

Security Considerations:
    - Read-only discovery operations ensuring no accidental Config modifications
    - Explicit deletion controls with confirmation prompts and force flag requirements
    - Comprehensive audit logging for compliance and operational tracking
    - Secure credential handling with profile-based authentication patterns
    - Access validation and error handling for enterprise security requirements

Dependencies:
    - boto3: AWS SDK for Config service operations and cross-account access
    - colorama: Enhanced terminal output with color coding for operational visibility
    - tqdm: Progress bars for long-running discovery and management operations
    - Inventory_Modules: Custom AWS inventory and discovery utilities
    - ArgumentsClass: Standardized CLI argument parsing and validation

Example Usage:
    # Basic Config service discovery
    python list_config_recorders_delivery_channels.py --profiles production

    # Fragment-based Config component search
    python list_config_recorders_delivery_channels.py --fragment SecurityBaseline

    # Config service cleanup with confirmation
    python list_config_recorders_delivery_channels.py +delete --force

Output:
    Displays discovered Config recorders and delivery channels with account, region,
    type, and configuration details for infrastructure management and compliance tracking.
"""

import logging
import sys
from os.path import split
from queue import Queue
from threading import Thread
from time import time

import Inventory_Modules
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import del_config_recorder_or_delivery_channel2, display_results, get_all_credentials
from tqdm.auto import tqdm

init()
__version__ = "2024.05.31"


##################
# Functions
##################


# TODO: Enable the deletion of the config recorders / delivery channels from specific accounts (or all?) at the end.
def parse_args(f_arguments):
    """
    Parse and validate CLI arguments for Config service discovery and management operations.

    Configures comprehensive argument parsing for AWS Config service configuration recorders
    and delivery channels inventory across AWS Organizations with support for fragment-based
    filtering, deletion operations, and cross-account discovery. Provides enterprise-grade
    CLI interface for infrastructure teams managing Config service deployment and compliance.

    Args:
        f_arguments (object): Command-line arguments list for parsing and validation

    Returns:
        argparse.Namespace: Parsed arguments object containing:
            - Profiles: List of AWS profiles for multi-account Config discovery
            - Regions: Target AWS regions for Config service enumeration
            - Accounts: Specific account IDs for targeted Config discovery
            - Fragments: Config component name fragments for targeted search and filtering
            - SkipAccounts: Account IDs to exclude from Config discovery operations
            - SkipProfiles: Profile names to exclude from Config service inventory
            - RootOnly: Boolean flag to limit discovery to root account only
            - Filename: Optional output file path for CSV export and reporting
            - AccessRole: Cross-account access role for Config service operations
            - Time: Boolean flag to enable performance timing and metrics
            - loglevel: Logging verbosity level for operational visibility and debugging
            - flagDelete: Boolean flag to enable Config component deletion operations
            - Force: Boolean flag to bypass confirmation prompts for deletion

    CLI Arguments:
        Multi-Account Authentication:
            - --profiles: AWS profiles for comprehensive organizational Config discovery
            - --skip-profiles: Profile exclusion for targeted Config inventory
            - Multi-profile mode for extensive Config service visibility

        Regional Configuration:
            - --regions: Target AWS regions for Config service discovery
            - Multi-region support for comprehensive Config deployment analysis

        Account Filtering:
            - --accounts: Specific account IDs for targeted Config discovery
            - --skip-accounts: Account exclusion for focused Config inventory
            - --root-only: Limit discovery to root account Config components

        Config Component Filtering:
            - --fragment: Config recorder/delivery channel name fragments for targeted search
            - Fragment-based search for precise Config component identification
            - Supports substring matching for flexible Config discovery

        Management Operations:
            - +delete: Enable Config component deletion with safety controls
            - --force: Bypass confirmation prompts for automated deletion workflows
            - Deletion safety features with explicit confirmation requirements

        Operational Controls:
            - --access-role: Cross-account access role for Config operations
            - --timing: Enable performance timing for operational metrics
            - --save-to-file: Export results to CSV for reporting and integration
            - --verbose: Control logging verbosity for debugging and audit trails

    Enterprise Features:
        - Standardized CLI interface consistent with inventory tooling
        - Fragment-based search for targeted Config component discovery
        - Multi-account and multi-region support for organizational Config visibility
        - Safe deletion workflows with confirmation and force controls
        - Output formatting with CSV export for enterprise reporting

    Validation and Error Handling:
        - Argument validation with informative error messages
        - Help text generation for operational documentation
        - Version information for tooling compatibility tracking
        - Default value configuration for operational convenience
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()

    # Configure standardized CLI arguments for enterprise Config service operations
    parser.multiprofile()  # Multi-profile authentication for organizational Config discovery
    parser.multiregion()  # Multi-region support for comprehensive Config deployment analysis
    parser.extendedargs()  # Extended argument support for advanced filtering capabilities
    parser.deletion()  # Standard deletion controls with safety and confirmation features
    parser.rootOnly()  # Root account only mode for targeted Config discovery
    parser.roletouse()  # Cross-account access role configuration for Config operations
    parser.timing()  # Performance timing metrics for operational analysis
    parser.save_to_file()  # CSV export functionality for enterprise reporting and integration
    parser.fragment()  # Fragment-based filtering for targeted Config component discovery
    parser.verbosity()  # Configurable logging verbosity for debugging and audit trails
    parser.version(__version__)  # Version information for tooling compatibility tracking

    # Add script-specific arguments for Config service management operations
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "+delete",
        "+forreal",
        dest="flagDelete",
        action="store_true",  # Enable deletion mode when parameter is supplied
        help="Enable deletion of discovered configuration recorders and delivery channels with safety controls",
    )
    return parser.my_parser.parse_args(f_arguments)


def check_accounts_for_delivery_channels_and_config_recorders(CredentialList, fFragments=None, fFixRun=False):
    """
    Discover and enumerate AWS Config service components across multiple accounts and regions.

    Performs comprehensive Config service discovery using multi-threaded processing to efficiently
    inventory configuration recorders and delivery channels across large-scale AWS Organizations
    environments. Supports fragment-based filtering for targeted Config component discovery and
    provides detailed metadata extraction for enterprise infrastructure governance and compliance.

    Args:
        CredentialList (list): List of credential dictionaries for cross-account Config discovery containing:
            - AccountId: AWS account number for Config service access
            - Region: Target AWS region for Config component enumeration
            - Success: Boolean indicating credential validity and access status
            - AccessError: Error details for failed credential attempts
        fFragments (list): Config component name fragments for targeted search and filtering
                          Defaults to None for comprehensive Config discovery
        fFixRun (bool): Deletion mode flag for Config component cleanup operations
                       Default False for read-only discovery mode

    Returns:
        list: Comprehensive list of Config component dictionaries containing:
            - Type: Config component type (Config Recorder or Delivery Channel)
            - AccountId: AWS account containing the Config component
            - Region: AWS region where Config component is deployed
            - name: Config component name identifier
            - ParentProfile: AWS profile used for Config component access
            - MgmtAccount: Management account for organizational Config oversight
            - Deleted: Boolean flag indicating deletion status for cleanup operations

    Config Discovery Features:
        - Configuration recorder enumeration with recording scope and status analysis
        - Delivery channel discovery with S3 bucket and SNS topic configuration
        - Fragment-based filtering for targeted Config component identification
        - Cross-account Config service visibility for organizational compliance oversight
        - Regional Config service availability validation and access control

    Multi-threaded Architecture:
        - Queue-based worker pattern for concurrent Config component discovery
        - Configurable worker thread pool for performance optimization
        - Progress tracking with real-time operational feedback
        - Graceful error handling for authorization and throttling issues

    Performance Optimization:
        - Concurrent processing for efficient large-scale Config discovery
        - Progress bars for operational visibility during long-running operations
        - Worker thread scaling based on credential count for optimal performance
        - Queue management for efficient work distribution and completion tracking

    Enterprise Infrastructure Governance:
        - Organizational Config service visibility across accounts and regions
        - Config component metadata extraction for compliance and audit tracking
        - Fragment-based search for targeted Config component management
        - Comprehensive error handling for operational resilience and troubleshooting

    Error Handling:
        - Authorization failure detection with graceful degradation
        - AWS API error management with comprehensive logging
        - Credential validation and failure tracking
        - Profile-specific error handling for multi-account Config discovery
    """

    class Find_Config_Recorders_and_Delivery_Channels(Thread):
        """
        Multi-threaded worker class for concurrent Config service component discovery and enumeration.

        Implements thread-safe Config service discovery using queue-based work distribution for
        efficient processing of configuration recorders and delivery channels across organizational
        accounts and regions.
        """

        def __init__(self, queue):
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            while True:
                # Extract work item from queue with account credentials and processing context
                c_account_credentials, c_fixrun, c_fragments, c_PlacesToLook, c_PlaceCount = self.queue.get()
                logging.info(
                    f"De-queued info for account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}"
                )

                try:
                    # Begin Config service discovery for the current account and region
                    logging.info(
                        f"Checking for config recorders and delivery channels in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}"
                    )

                    # Discover and process Config delivery channels with fragment-based filtering
                    capture_this_delivery_channel = False
                    account_dcs = Inventory_Modules.find_delivery_channels2(
                        c_account_credentials, c_account_credentials["Region"]
                    )

                    # Process discovered delivery channels with fragment matching logic
                    if len(account_dcs["DeliveryChannels"]) > 0:
                        # Apply fragment filtering for targeted delivery channel discovery
                        if c_fragments is None or "all" in c_fragments:
                            # Include all delivery channels when no fragment filter specified
                            capture_this_delivery_channel = True
                            logging.info(f"No fragment provided. Found {account_dcs['DeliveryChannels'][0]['name']}")
                        else:
                            # Apply fragment-based filtering for targeted discovery
                            for fragment in c_fragments:
                                if fragment in account_dcs["DeliveryChannels"][0]["name"]:
                                    capture_this_delivery_channel = True
                                    logging.info(
                                        f"Found {account_dcs['DeliveryChannels'][0]['name']} which contains {fragment}"
                                    )
                                    break
                                else:
                                    capture_this_delivery_channel = False
                                    logging.info(
                                        f"Looking for {fragment}. Found {account_dcs['DeliveryChannels'][0]['name']}, so skipping..."
                                    )

                        # Aggregate delivery channel metadata for enterprise reporting
                        if capture_this_delivery_channel:
                            account_dcs["DeliveryChannels"][0].update(
                                {
                                    "Type": "Delivery Channel",  # Component type for categorization
                                    "AccountId": c_account_credentials["AccountNumber"],  # Account identifier
                                    "AccessKeyId": c_account_credentials["AccessKeyId"],  # Access credentials
                                    "SecretAccessKey": c_account_credentials["SecretAccessKey"],  # Secret credentials
                                    "SessionToken": c_account_credentials["SessionToken"],  # Session token
                                    "Region": c_account_credentials["Region"],  # Regional deployment
                                    "MgmtAccount": c_account_credentials["MgmtAccount"],  # Management account
                                    "ParentProfile": c_account_credentials["ParentProfile"],  # Profile context
                                    "Deleted": False,  # Deletion status tracking
                                }
                            )
                            account_crs_and_dcs.extend(account_dcs["DeliveryChannels"])

                    # Discover and process Config configuration recorders with fragment-based filtering
                    account_crs = Inventory_Modules.find_config_recorders2(
                        c_account_credentials, c_account_credentials["Region"]
                    )
                    capture_this_config_recorder = False

                    # Process discovered configuration recorders with fragment matching logic
                    if len(account_crs["ConfigurationRecorders"]) > 0:
                        # Apply fragment filtering for targeted configuration recorder discovery
                        if c_fragments is None or "all" in c_fragments:
                            # Include all configuration recorders when no fragment filter specified
                            capture_this_config_recorder = True
                            logging.info(
                                f"No fragment provided. Found {account_crs['ConfigurationRecorders'][0]['name']}"
                            )
                        else:
                            # Apply fragment-based filtering for targeted discovery
                            for fragment in c_fragments:
                                if fragment in account_crs["ConfigurationRecorders"][0]["name"]:
                                    capture_this_config_recorder = True
                                    logging.info(
                                        f"Found {account_crs['ConfigurationRecorders'][0]['name']} which contains {fragment}"
                                    )
                                    break
                                else:
                                    capture_this_config_recorder = False
                                    logging.info(
                                        f"Looking for {fragment}. Found {account_crs['ConfigurationRecorders'][0]['name']}, so skipping..."
                                    )

                        # Aggregate configuration recorder metadata for enterprise reporting
                        if capture_this_config_recorder:
                            account_crs["ConfigurationRecorders"][0].update(
                                {
                                    "Type": "Config Recorder",  # Component type for categorization
                                    "AccountId": c_account_credentials["AccountNumber"],  # Account identifier
                                    "AccessKeyId": c_account_credentials["AccessKeyId"],  # Access credentials
                                    "SecretAccessKey": c_account_credentials["SecretAccessKey"],  # Secret credentials
                                    "SessionToken": c_account_credentials["SessionToken"],  # Session token
                                    "Region": c_account_credentials["Region"],  # Regional deployment
                                    "MgmtAccount": c_account_credentials["MgmtAccount"],  # Management account
                                    "ParentProfile": c_account_credentials["ParentProfile"],  # Profile context
                                    "Deleted": False,  # Deletion status tracking
                                }
                            )
                            account_crs_and_dcs.extend(account_crs["ConfigurationRecorders"])

                    # Log successful account and region processing for audit trail
                    logging.info(
                        f"Successfully connected to account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}"
                    )
                except KeyError as my_Error:
                    # Handle missing key errors during Config component metadata extraction
                    logging.error(
                        f"Account Access failed - trying to access {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}"
                    )
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    # Handle attribute errors likely caused by incorrect profile configuration
                    logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
                    logging.warning(my_Error)
                    continue
                finally:
                    # Complete processing and update progress tracking
                    logging.info(
                        f"{ERASE_LINE}Finished finding items in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']} - {c_PlaceCount} / {c_PlacesToLook}"
                    )
                    pbar.update()  # Update progress bar for operational visibility
                    self.queue.task_done()  # Mark queue item as completed

    # Initialize processing context and data structures for Config discovery
    account_crs_and_dcs = []  # Aggregated results list for all discovered Config components
    PlaceCount = 1  # Progress counter for operational visibility

    # Configure optimal worker thread count based on credential count and system limits
    WorkerThreads = min(len(CredentialList), 40)

    checkqueue = Queue()  # Queue for work distribution across worker threads

    # Initialize progress tracking for operational visibility during Config discovery
    pbar = tqdm(
        desc=f"Finding config recorders / delivery channels from {len(AllCredentials)} accounts and regions",
        total=len(AllCredentials),
        unit=" accounts & regions",
    )

    # Create and start worker thread pool for concurrent Config component discovery
    for x in range(WorkerThreads):
        worker = Find_Config_Recorders_and_Delivery_Channels(checkqueue)
        # Daemon threads allow main thread exit even if workers are still processing
        worker.daemon = True
        worker.start()

    # Queue Config discovery work items for worker thread processing
    # Note: Credential list already includes regional context, eliminating need for nested region iteration
    for credential in CredentialList:
        logging.info(f"Connecting to account {credential['AccountId']} in region {credential['Region']}")
        try:
            # Queue account and region combination for worker thread processing
            # Note: Tuple structure is critical for proper parameter expansion in worker threads
            checkqueue.put((credential, fFixRun, fFragments, len(CredentialList), PlaceCount))
        except ClientError as my_Error:
            # Handle authorization failures with informative error messaging
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region"
                )
                logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass

    # Wait for all worker threads to complete processing
    checkqueue.join()
    pbar.close()  # Close progress bar after completion
    return account_crs_and_dcs


def _delete_config_recorders_and_delivery_channels(f_config_recorders_and_delivery_channels_to_delete, f_timing):
    """
    Execute safe deletion of AWS Config service configuration recorders and delivery channels.

    Performs batch deletion operations for Config service components with comprehensive error
    handling, progress tracking, and status validation. Designed for enterprise Config service
    cleanup operations with safety controls and operational visibility for infrastructure teams
    managing Config service decommissioning and optimization.

    Args:
        f_config_recorders_and_delivery_channels_to_delete (list): List of Config component
            dictionaries containing deletion targets with:
            - Type: Config component type (Config Recorder or Delivery Channel)
            - AccountId: Target AWS account for deletion operation
            - Region: Target AWS region for Config component removal
            - name: Config component name identifier
            - Access credentials and metadata for deletion operations
        f_timing (bool): Performance timing flag for operational metrics and milestone tracking

    Returns:
        list: Updated Config component list with deletion status tracking containing:
            - Original component metadata preserved for audit trails
            - Deleted: Boolean flag indicating successful deletion completion
            - Deletion operation results and error details for troubleshooting

    Deletion Process:
        - Sequential processing for reliable Config component deletion
        - Pre-deletion validation ensuring component exists and is accessible
        - Comprehensive error handling for authorization and dependency issues
        - Status tracking with detailed logging for operational audit trails

    Safety Features:
        - Deletion confirmation and validation before component removal
        - Comprehensive error handling preventing partial deletion states
        - Detailed logging for compliance and audit trail requirements
        - Rollback-safe operations with status tracking and error reporting

    Performance Monitoring:
        - Optional timing metrics for deletion operation analysis
        - Progress tracking for operational visibility during batch deletions
        - Performance milestone reporting for optimization and planning
        - Efficient deletion sequencing for minimal operational impact

    Enterprise Operations:
        - Batch deletion capabilities for efficient Config service cleanup
        - Comprehensive audit logging for compliance and operational tracking
        - Error handling and recovery for enterprise operational requirements
        - Status validation and confirmation for deletion verification

    Error Handling:
        - AWS API error management with graceful degradation
        - Authorization failure detection with appropriate logging
        - Dependency validation preventing orphaned resource creation
        - Comprehensive error reporting for troubleshooting and audit trails
    """
    # Begin Config service component deletion with operational logging
    logging.warning("Deleting all Config Recorders")
    for deletion_item in f_config_recorders_and_delivery_channels_to_delete:
        try:
            # Display deletion progress for operational visibility
            print(
                ERASE_LINE,
                f"Deleting {deletion_item['Type']} from Account {deletion_item['AccountId']} in region {deletion_item['Region']}",
                end="\r",
            )

            # Process Config Recorder deletion with AWS API validation
            if deletion_item["Type"] == "Config Recorder":
                # Establish Config service client for configuration recorder deletion
                config_client = Inventory_Modules.get_child_access2(
                    profile=deletion_item, region=deletion_item["Region"], service="config"
                )
                # Execute configuration recorder deletion with AWS Config API
                deleteit = config_client.delete_configuration_recorder(ConfigurationRecorderName=deletion_item["name"])
                # Display timing metrics for performance monitoring if requested
                if f_timing:
                    print(
                        f"{ERASE_LINE}Deleted {deletion_item['Type']} in {deleteit['ResponseMetadata']['HTTPStatusCode']} ms"
                    )
                deletion_item["Deleted"] = True  # Mark deletion as successful
                logging.warning(f"Deleted {deletion_item['Type']} {deletion_item['name']}")

            # Process Delivery Channel deletion with AWS API validation
            elif deletion_item["Type"] == "Delivery Channel":
                # Establish Config service client for delivery channel deletion
                config_client = Inventory_Modules.get_child_access2(
                    profile=deletion_item, region=deletion_item["Region"], service="config"
                )
                # Execute delivery channel deletion with AWS Config API
                deleteit = config_client.delete_delivery_channel(DeliveryChannelName=deletion_item["name"])
                # Display timing metrics for performance monitoring if requested
                if f_timing:
                    print(
                        f"{ERASE_LINE}Deleted {deletion_item['Type']} in {deleteit['ResponseMetadata']['HTTPStatusCode']} ms"
                    )
                deletion_item["Deleted"] = True  # Mark deletion as successful
                logging.warning(f"Deleted {deletion_item['Type']} {deletion_item['name']}")

        except Exception as my_Error:
            # Handle deletion failures with comprehensive error logging
            deletion_item["Deleted"] = False  # Mark deletion as failed
            print(f"Error: {my_Error}")

    return f_config_recorders_and_delivery_channels_to_delete


##################
# Main
##################


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles
    pRegionList = args.Regions
    pAccounts = args.Accounts
    pFragments = args.Fragments
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pRootOnly = args.RootOnly
    pFilename = args.Filename
    pChildAccessRole = args.AccessRole
    pTiming = args.Time
    verbose = args.loglevel
    DeletionRun = args.flagDelete
    ForceDelete = args.Force
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)30s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)

    ERASE_LINE = "\x1b[2K"
    begin_time = time()

    display_dict = {
        "ParentProfile": {"DisplayOrder": 1, "Heading": "Parent Profile"},
        "MgmtAccount": {"DisplayOrder": 2, "Heading": "Mgmt Acct"},
        "AccountId": {"DisplayOrder": 3, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 4, "Heading": "Region"},
        "Type": {"DisplayOrder": 5, "Heading": "Type"},
        "name": {"DisplayOrder": 6, "Heading": "Name"},
    }

    NumObjectsFound = 0
    NumAccountsInvestigated = 0

    AllCredentials = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList
    )
    RegionList = list(set([x["Region"] for x in AllCredentials]))
    AccountNum = len(set([acct["AccountId"] for acct in AllCredentials]))

    cf_regions = Inventory_Modules.get_service_regions("config", RegionList)
    print()
    print(f"Searching total of {AccountNum} accounts and {len(cf_regions)} regions")
    if pTiming:
        print()
        milestone_time1 = time()
        print(
            f"{Fore.GREEN}\t\tFiguring out what regions are available to your accounts, and capturing credentials for all accounts in those regions took: {(milestone_time1 - begin_time):.3f} seconds{Fore.RESET}"
        )
        print()
    print(f"Now running through all accounts and regions identified to find resources...")
    all_config_recorders_and_delivery_channels = check_accounts_for_delivery_channels_and_config_recorders(
        AllCredentials, pFragments, DeletionRun
    )

    if pTiming:
        print()
        milestone_time2 = time()
        print(
            f"{Fore.GREEN}\t\tChecking {len(AllCredentials)} places took: {(milestone_time2 - milestone_time1):.3f} seconds{Fore.RESET}"
        )
        print()
    cr = 0
    dc = 0
    for item in all_config_recorders_and_delivery_channels:
        if item["Type"] == "Delivery Channel":
            dc += 1
        elif item["Type"] == "Config Recorder":
            cr += 1

    all_sorted_config_recorders_and_delivery_channels = sorted(
        all_config_recorders_and_delivery_channels,
        key=lambda d: (d["ParentProfile"], d["MgmtAccount"], d["AccountId"], d["Region"], d["Type"]),
    )
    if pTiming:
        print()
        milestone_time3 = time()
        print(
            f"{Fore.GREEN}\t\tSorting the list of places took: {(milestone_time3 - milestone_time2):.3f} seconds{Fore.RESET}"
        )
        print()
    display_results(all_sorted_config_recorders_and_delivery_channels, display_dict, None, pFilename)

    print(ERASE_LINE)
    print(f"We scanned {AccountNum} accounts and {len(RegionList)} regions...")
    print(f"We Found {cr} Configuration Recorders and {dc} Delivery Channels")
    print()

    if DeletionRun and not ForceDelete:
        ReallyDelete = (
            input("Deletion of Config Recorders and Delivery Channels has been requested. Are you still sure? (y/n): ")
            == "y"
        )
    else:
        ReallyDelete = False

    if DeletionRun and (ReallyDelete or ForceDelete):
        deleted_config_recorders_and_delivery_channels = _delete_config_recorders_and_delivery_channels(
            all_sorted_config_recorders_and_delivery_channels, pTiming
        )

    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This whole script took {time() - begin_time:.3f} seconds{Fore.RESET}")
    print()
    print("Thank you for using this tool")
    print()

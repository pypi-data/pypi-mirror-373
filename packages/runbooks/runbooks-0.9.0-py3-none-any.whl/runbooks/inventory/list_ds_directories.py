#!/usr/bin/env python3

"""
AWS Directory Service (DS) Directory Discovery and Inventory Script

This enterprise-grade script provides comprehensive discovery and enumeration of AWS Directory
Service (DS) directories across multi-account AWS Organizations environments. Designed for
infrastructure teams managing Microsoft Active Directory and Simple AD deployments at scale,
offering detailed directory metadata extraction, status analysis, and regional distribution
visibility for enterprise identity and access management governance.

Key Features:
    - Multi-account, multi-region Directory Service directory discovery
    - Comprehensive directory metadata extraction including status, type, and ownership
    - Fragment-based filtering for targeted directory identification and management
    - Enterprise governance support with organizational context and compliance tracking
    - Regional directory distribution analysis for operational planning and optimization
    - Progress tracking and performance metrics for large-scale directory discovery operations

Authentication & Access:
    - AWS Organizations support for centralized directory service management
    - Cross-account role assumption for organizational directory visibility
    - Regional validation and opt-in status verification for directory service availability
    - Profile-based authentication with comprehensive credential management

Performance & Scalability:
    - Progress bars and operational feedback for large-scale directory discovery
    - Efficient credential management for multi-account directory enumeration
    - Regional optimization with targeted directory service API calls
    - Memory-efficient processing for extensive directory service inventories

Enterprise Use Cases:
    - Directory service governance and compliance reporting across organizational accounts
    - Identity infrastructure audit and directory service configuration validation
    - Directory service consolidation and migration planning with organizational visibility
    - Operational monitoring and directory service health assessment

Security & Compliance:
    - Read-only directory discovery operations for operational safety
    - Comprehensive audit logging for directory service access and discovery activities
    - Regional access validation preventing unauthorized directory service enumeration
    - Safe credential handling with automatic session management

Dependencies:
    - boto3: AWS SDK for Directory Service API access
    - colorama: Terminal output formatting and colored display
    - tqdm: Progress bars for operational visibility during discovery
    - Custom modules: Inventory_Modules, ArgumentsClass for enterprise argument parsing

Output Format:
    - Tabular directory service inventory with sortable columns
    - Management account context for organizational directory visibility
    - Regional distribution summary for operational planning
    - Directory status and configuration details for enterprise governance
"""

import logging
import sys
from time import time

from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_directories2, get_all_credentials
from tqdm.auto import tqdm

init()
__version__ = "2024.05.31"


def parse_args(f_arguments):
    """
    Parse and validate command-line arguments for Directory Service directory discovery operations.

    Configures comprehensive argument parsing for AWS Directory Service discovery across multi-account
    AWS Organizations environments. Supports enterprise-grade directory management with profile
    management, regional targeting, fragment-based filtering, and operational controls for large-scale
    directory service governance and compliance operations.

    Args:
        f_arguments (list): Command-line argument list for directory discovery configuration

    Returns:
        argparse.Namespace: Parsed argument namespace containing:
            - Profiles: List of AWS profiles for multi-account directory discovery
            - Regions: Target AWS regions for directory service enumeration
            - Fragments: Directory name fragments for targeted discovery and filtering
            - Exact: Boolean flag for exact fragment matching vs substring matching
            - Accounts: Specific account list for targeted directory discovery
            - SkipAccounts: Account exclusion list for selective directory enumeration
            - SkipProfiles: Profile exclusion list for selective discovery operations
            - Time: Performance timing flag for operational metrics and optimization
            - RootOnly: Flag restricting discovery to management account only
            - loglevel: Logging verbosity for operational visibility and troubleshooting

    CLI Argument Categories:
        - Multi-profile support for organizational directory service management
        - Multi-region targeting for comprehensive directory service coverage
        - Fragment-based filtering for targeted directory identification and management
        - Extended arguments including account filtering and performance timing
        - Root-only mode for management account directory service discovery
        - Verbosity controls for operational logging and troubleshooting

    Enterprise Features:
        - Organizational profile management for centralized directory service governance
        - Regional filtering for geo-distributed directory service architectures
        - Account inclusion/exclusion for selective directory service discovery
        - Performance monitoring with timing metrics for operational optimization
        - Comprehensive logging controls for audit and compliance requirements

    Usage Examples:
        - Multi-account discovery: --profiles profile1 profile2 --regions us-east-1 us-west-2
        - Fragment filtering: --fragment "corp" --exact for targeted directory discovery
        - Root account only: --rootonly for management account directory enumeration
        - Performance timing: --timing for operational metrics and optimization analysis
    """
    parser = CommonArguments()
    parser.multiprofile()  # Enable multi-profile support for organizational directory discovery
    parser.multiregion()  # Enable multi-region targeting for comprehensive directory coverage
    parser.fragment()  # Enable fragment-based filtering for targeted directory identification
    parser.extendedargs()  # Enable account filtering and performance timing capabilities
    parser.timing()  # Enable performance timing metrics for operational optimization
    parser.rootOnly()  # Enable management account only mode for centralized directory discovery
    parser.version(__version__)
    parser.verbosity()  # Enable logging verbosity controls for operational visibility
    return parser.my_parser.parse_args(f_arguments)


def find_all_directories(f_credentials, f_fragments, f_exact):
    """
    Discover and enumerate AWS Directory Service directories across multiple accounts and regions.

    Performs comprehensive Directory Service discovery using credential-based enumeration to inventory
    Microsoft Active Directory, Simple AD, and AD Connector directories across large-scale AWS
    Organizations environments. Supports fragment-based filtering for targeted directory identification
    and provides detailed directory metadata extraction for enterprise identity and access management
    governance.

    Args:
        f_credentials (list): List of credential dictionaries for cross-account directory discovery containing:
            - AccountId: AWS account number for Directory Service access
            - Region: Target AWS region for directory enumeration
            - Success: Boolean indicating credential validity and access status
            - MgmtAccount: Management account identifier for organizational context
            - AccessError: Error details for failed credential attempts
        f_fragments (list): Directory name fragments for targeted search and filtering
                           Supports partial name matching for flexible directory identification
        f_exact (bool): Exact matching flag for precise directory name filtering
                       True for exact match, False for substring matching

    Returns:
        list: Comprehensive list of directory dictionaries containing:
            - DirectoryName: Human-readable directory name identifier
            - DirectoryId: Unique AWS Directory Service identifier
            - HomeRegion: Primary region where directory service is hosted
            - Status: Current operational status (Active, Creating, Deleting, etc.)
            - Type: Directory type (SimpleAD, MicrosoftAD, ADConnector, etc.)
            - Owner: Directory ownership context (Self, Shared, etc.)
            - MgmtAccount: Management account for organizational directory oversight
            - Region: AWS region where directory is deployed
            - AccountId: AWS account containing the directory

    Directory Discovery Features:
        - Multi-account, multi-region Directory Service enumeration
        - Fragment-based filtering for targeted directory identification
        - Comprehensive directory metadata extraction for governance and compliance
        - Cross-account directory visibility for organizational identity management
        - Regional directory distribution analysis for operational planning

    Processing Architecture:
        - Sequential processing with progress tracking for operational visibility
        - Credential validation and error handling for authorization issues
        - Regional validation ensuring directory service availability
        - Memory-efficient processing for extensive directory service inventories

    Performance Considerations:
        - Progress bars for operational feedback during large-scale discovery
        - Efficient Directory Service API usage for optimal performance
        - Error handling and graceful degradation for authorization failures
        - TODO: Future enhancement for multi-threading support to improve performance

    Enterprise Identity Management:
        - Organizational directory service visibility across accounts and regions
        - Directory metadata aggregation for compliance and audit tracking
        - Fragment-based search capabilities for targeted directory management
        - Comprehensive error handling for operational resilience and troubleshooting

    Error Handling:
        - Authorization failure detection with graceful degradation
        - AWS API error management with comprehensive logging
        - Type error handling for malformed directory service responses
        - Credential validation and failure tracking for multi-account operations
    """
    AllDirectories = []  # Aggregated list for all discovered directories

    # TODO: Need to use multi-threading here for improved performance
    # Sequential processing with progress tracking for operational visibility
    for credential in tqdm(
        f_credentials, desc=f"Looking through {len(f_credentials)} accounts and regions", unit="credentials"
    ):
        logging.info(f"{ERASE_LINE}Looking in account: {credential['AccountId']} in region {credential['Region']}")

        # Skip failed credentials to avoid API errors
        if not credential["Success"]:
            continue

        try:
            # Discover directories using Directory Service API with fragment filtering
            directories = find_directories2(credential, credential["Region"], f_fragments, f_exact)
            logging.info(f"directories: {directories}")
            logging.info(
                f"{ERASE_LINE}Account: {credential['AccountId']} Region: {credential['Region']} Found {len(directories)} directories"
            )

            # Process and aggregate discovered directories with organizational context
            if directories:
                for directory in directories:
                    # Enhance directory metadata with organizational and regional context
                    # Available directory metadata includes:
                    # - DirectoryName: Human-readable directory identifier
                    # - DirectoryId: Unique AWS Directory Service identifier
                    # - HomeRegion: Primary directory service region
                    # - Status: Operational status (Active, Creating, etc.)
                    # - Type: Directory type (SimpleAD, MicrosoftAD, etc.)
                    # - Owner: Directory ownership context

                    directory.update(
                        {
                            "MgmtAccount": credential["MgmtAccount"],  # Management account context
                            "Region": credential["Region"],  # Regional deployment information
                            "AccountId": credential["AccountId"],  # Account ownership details
                        }
                    )
                    AllDirectories.append(directory)

        except TypeError as my_Error:
            # Handle type errors from malformed Directory Service API responses
            logging.info(f"Error: {my_Error}")
            continue
        except ClientError as my_Error:
            # Handle AWS API authorization failures with informative logging
            if "AuthFailure" in str(my_Error):
                logging.error(f"{ERASE_LINE} Account {credential['AccountId']} : Authorization Failure")

    return AllDirectories


##########################

if __name__ == "__main__":
    # Parse command-line arguments for Directory Service discovery configuration
    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles  # AWS profiles for multi-account directory discovery
    pRegionList = args.Regions  # Target regions for directory service enumeration
    pFragments = args.Fragments  # Directory name fragments for targeted filtering
    pExact = args.Exact  # Exact matching flag for precise directory identification
    pAccounts = args.Accounts  # Specific account list for targeted discovery
    pSkipAccounts = args.SkipAccounts  # Account exclusion list for selective enumeration
    pSkipProfiles = args.SkipProfiles  # Profile exclusion list for selective operations
    pTiming = args.Time  # Performance timing flag for operational metrics
    pRootOnly = args.RootOnly  # Management account only mode for centralized discovery
    verbose = args.loglevel  # Logging verbosity for operational visibility

    # Configure comprehensive logging for Directory Service discovery operations
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)  # Suppress AWS SDK logging
    logging.getLogger("botocore").setLevel(logging.CRITICAL)  # Suppress AWS core logging
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)  # Suppress S3 transfer logging
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)  # Suppress HTTP logging
    logging.getLogger("botocore").setLevel(logging.CRITICAL)  # Suppress boto core logging

    ERASE_LINE = "\x1b[2K"  # Terminal control for dynamic output updates
    logging.info(f"Profiles: {pProfiles}")
    begin_time = time()  # Performance timing baseline for operational metrics

    print()
    print(f"Checking for Directories... ")
    print()

    # Initialize credential management for multi-account Directory Service access
    AllCredentials = []
    if pSkipAccounts is None:
        pSkipAccounts = []  # Initialize empty skip list if not provided
    if pSkipProfiles is None:
        SkipProfiles = []  # Initialize empty profile skip list if not provided
    account_num = 0

    # Retrieve and validate credentials for multi-account Directory Service discovery
    AllCredentials = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList
    )

    # Display credential retrieval timing for performance optimization
    if pTiming:
        print(
            f"{Fore.GREEN}\tAfter getting credentials, this script took {time() - begin_time:.3f} seconds{Fore.RESET}"
        )
        print()

    # Extract unique regional and account context for discovery scope analysis
    RegionList = list(set([x["Region"] for x in AllCredentials]))
    AccountList = list(set([x["AccountId"] for x in AllCredentials]))

    # Display credential parsing timing for operational metrics
    if pTiming:
        print(
            f"{Fore.GREEN}\tAfter parsing out all Regions, Account and Profiles, this script took {time() - begin_time:.3f} seconds{Fore.RESET}"
        )
        print()

    print()

    credential_number = 0
    logging.info(f"Looking through {len(AccountList)} accounts and {len(RegionList)} regions")

    # Execute comprehensive Directory Service discovery across organizational accounts
    all_directories = find_all_directories(AllCredentials, pFragments, pExact)

    print()

    # Configure display formatting for comprehensive directory service inventory
    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Parent Acct"},  # Management account context
        "AccountId": {"DisplayOrder": 2, "Heading": "Account Number"},  # Account ownership
        "Region": {"DisplayOrder": 3, "Heading": "Region"},  # Regional deployment
        "DirectoryName": {"DisplayOrder": 4, "Heading": "Directory Name"},  # Human-readable identifier
        "DirectoryId": {"DisplayOrder": 5, "Heading": "Directory ID"},  # Unique service identifier
        "HomeRegion": {"DisplayOrder": 6, "Heading": "Home Region"},  # Primary service region
        "Status": {"DisplayOrder": 7, "Heading": "Status"},  # Operational status
        "Type": {"DisplayOrder": 8, "Heading": "Type"},  # Directory type classification
        "Owner": {"DisplayOrder": 9, "Heading": "Owner"},  # Ownership context
    }

    # Sort directory results for consistent organizational reporting
    sorted_Results = sorted(
        all_directories, key=lambda d: (d["MgmtAccount"], d["AccountId"], d["Region"], d["DirectoryName"])
    )

    # Display comprehensive directory service inventory with formatted output
    display_results(sorted_Results, display_dict, "None")

    # Provide operational summary with discovery metrics and performance timing
    print(ERASE_LINE)
    print(
        f"Found {len(all_directories)} directories across {len(AccountList)} accounts across {len(RegionList)} regions"
    )
    print()

    # Display total execution timing for performance analysis and optimization
    if pTiming:
        print(f"{Fore.GREEN}\tThis script took {time() - begin_time:.3f} seconds{Fore.RESET}")
        print()
    print("Thank you for using this script")
    print()

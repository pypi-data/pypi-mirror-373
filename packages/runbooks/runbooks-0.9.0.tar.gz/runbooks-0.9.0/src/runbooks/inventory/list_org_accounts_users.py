#!/usr/bin/env python3

"""
AWS Organizations User Inventory Discovery Script

This script provides comprehensive discovery and enumeration capabilities for user accounts
across AWS Organizations environments, supporting both traditional IAM users and modern
AWS Identity Center (formerly AWS SSO) user management. It's designed for enterprise
identity and access management teams who need complete visibility into user distribution,
access patterns, and identity governance across large-scale multi-account deployments.

Key Features:
- Multi-account user discovery using assume role capabilities across AWS Organizations
- Dual identity source support: IAM users and AWS Identity Center users
- Comprehensive user metadata extraction with last access tracking
- Cross-account user enumeration with organizational hierarchy mapping
- Identity Center directory deduplication for efficient discovery
- Enterprise reporting with CSV export and structured output
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- Identity governance and user access auditing across organizations
- User lifecycle management and access certification processes
- Security compliance reporting for identity and access management
- Identity consolidation analysis and migration planning
- Multi-account user access patterns and behavioral analysis
- Identity Center adoption tracking and governance oversight
- User account sprawl detection and cleanup initiatives

Identity Management Features:
- IAM user discovery with comprehensive metadata extraction including:
  - User creation dates and last password usage tracking
  - Access key status and last activity monitoring
  - Policy attachments and group membership analysis
- AWS Identity Center user enumeration with directory awareness including:
  - Identity Center user profiles and attributes
  - Directory instance discovery and deduplication
  - User provisioning status and access tracking
- Cross-account identity correlation for governance oversight

Security Considerations:
- Uses IAM assume role capabilities for cross-account user discovery
- Implements proper error handling for authorization failures
- Supports read-only operations with no user modification capabilities
- Respects identity service permissions and regional access constraints
- Provides comprehensive audit trail through detailed logging
- Sensitive user information handling with appropriate access controls

Identity Center Integration:
- Automatic discovery of Identity Center directory instances
- Directory deduplication to prevent duplicate user enumeration
- Support for multiple Identity Center instances across organization
- Integration with Identity Center user provisioning and lifecycle management
- Identity Center user attribute and profile extraction

Performance Considerations:
- Sequential processing for reliable user discovery operations
- Progress tracking for operational visibility during large-scale enumeration
- Efficient credential management for cross-account user access
- Memory-optimized data structures for large user inventories
- Directory deduplication to optimize Identity Center discovery performance

Threading Architecture:
- Currently uses sequential processing for reliable operations
- TODO: Multi-threading enhancement planned for improved performance
- Thread-safe error handling and progress tracking architecture
- Graceful degradation for account access failures

Dependencies:
- boto3/botocore for AWS IAM and Identity Center API interactions
- ArgumentsClass for standardized CLI argument parsing
- Inventory_Modules for common utility functions and credential management
- colorama for enhanced output formatting
- tqdm for progress tracking during user discovery

Compliance and Audit Features:
- Comprehensive user discovery for identity governance auditing
- User access pattern analysis for compliance validation
- Cross-account user visibility for organizational security oversight
- Identity lifecycle tracking for governance and compliance management
- User attribute and metadata extraction for compliance reporting

Future Enhancements:
- Multi-threading for improved performance across large organizations
- User access pattern analysis and behavioral analytics
- Integration with AWS CloudTrail for user activity correlation
- User optimization recommendations for identity governance

Author: AWS CloudOps Team
Version: 2024.05.09
"""

import logging
import sys
from os.path import split
from time import time

from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import (
    display_results,
    find_iam_users2,
    find_idc_directory_id2,
    find_idc_users2,
    get_all_credentials,
)
from tqdm.auto import tqdm

init()
__version__ = "2024.05.09"
ERASE_LINE = "\x1b[2K"
begin_time = time()


##################
# Functions
##################
def parse_args(arguments):
    """
    Parse command line arguments for AWS Organizations user discovery operations.

    Configures comprehensive argument parsing for multi-account, multi-region user inventory
    operations. Supports enterprise identity and access management with profile management,
    region targeting, organizational access controls, and identity source selection for both
    traditional IAM users and modern AWS Identity Center user management.

    Args:
        arguments (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: List of AWS profiles to process
            - Regions: Target regions for user discovery
            - SkipProfiles/SkipAccounts: Exclusion filters
            - RootOnly: Limit to organization root accounts
            - AccessRoles: Cross-account roles for Organizations access
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration
            - pIdentityCenter: Enable AWS Identity Center user discovery
            - pIAM: Enable IAM user discovery

    Configuration Options:
        - Multi-region scanning with region filters for targeted user analysis
        - Multi-profile support for federated access across identity infrastructure
        - Extended arguments for advanced filtering and account selection
        - Root-only mode for organization-level user inventory
        - Role-based access for cross-account user discovery
        - File output for integration with identity management tools
        - Timing metrics for performance optimization and monitoring
        - Verbose logging for debugging and identity governance audit

    Identity Source Selection:
        - IAM flag (--iam): Enable traditional IAM user discovery and enumeration
        - Identity Center flag (--idc): Enable AWS Identity Center user discovery
        - Default behavior: Both identity sources enabled when neither flag specified
        - Selective discovery for focused identity analysis and governance

    Enterprise Identity Management:
        - Multi-account user discovery across organizational boundaries
        - Identity source flexibility for migration and governance planning
        - Cross-account user enumeration with organizational hierarchy mapping
        - Identity governance and compliance reporting capabilities
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
    parser.my_parser.description = "Discover and enumerate both IAM users and AWS Identity Center users across AWS Organizations for enterprise identity governance and access management."
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rootOnly()
    parser.rolestouse()
    parser.save_to_file()
    parser.verbosity()
    parser.timing()
    parser.version(__version__)
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "--idc",
        dest="pIdentityCenter",
        action="store_true",  # Defaults to False
        help="Enable AWS Identity Center user discovery only - supports modern centralized identity management with directory integration",
    )
    local.add_argument(
        "--iam",
        dest="pIAM",
        action="store_true",  # Defaults to False
        help="Enable traditional IAM user discovery only - supports legacy identity management and direct account access patterns",
    )
    return parser.my_parser.parse_args(arguments)


def find_all_org_users(f_credentials, f_IDC: bool, f_IAM: bool) -> list:
    """
    Discover and enumerate user accounts across AWS Organizations supporting both IAM and Identity Center.

    Performs comprehensive user discovery using sequential processing to efficiently inventory
    users across enterprise AWS environments. Supports dual identity sources with directory
    deduplication and comprehensive metadata extraction for enterprise identity governance.

    Args:
        f_credentials (list): List of credential dictionaries for cross-account access containing:
            - AccountId: AWS account number
            - Success: Boolean indicating credential validity
            - ErrorMessage: Error details for failed credential attempts
            - RolesTried: List of roles attempted for access
        f_IDC (bool): Enable AWS Identity Center user discovery
        f_IAM (bool): Enable traditional IAM user discovery

    Returns:
        list: Comprehensive list of user dictionaries containing:
            - MgmtAccount: Management account identifier for organizational hierarchy
            - AccountId: AWS account containing the user
            - Region: AWS region where user is managed
            - UserName: User account name or identifier
            - PasswordLastUsed: Last password usage timestamp (IAM users)
            - Type: User source type (IAM or Identity Center)
            - Additional metadata based on user type and source

    Identity Discovery Features:
        - IAM user enumeration with comprehensive metadata extraction
        - Identity Center user discovery with directory awareness
        - Directory instance deduplication for efficient discovery
        - Cross-account user correlation for governance oversight
        - User access pattern tracking for compliance analysis

    Performance Considerations:
        - Sequential processing for reliable user discovery operations
        - Progress tracking for operational visibility during enumeration
        - Directory deduplication to optimize Identity Center discovery
        - Memory-optimized data structures for large user inventories
        - TODO: Multi-threading enhancement planned for improved performance

    Error Handling:
        - Authorization failure detection with appropriate logging
        - AWS API error management with graceful degradation
        - Credential validation and failure tracking
        - Comprehensive error reporting for troubleshooting

    Identity Center Integration:
        - Automatic discovery of Identity Center directory instances
        - Directory deduplication to prevent duplicate user enumeration
        - Support for multiple Identity Center instances across organization
        - Integration with Identity Center user provisioning and lifecycle

    Enterprise Identity Governance:
        - Cross-account user visibility for organizational security oversight
        - User lifecycle tracking for governance and compliance management
        - Identity source correlation for migration and governance planning
        - User attribute and metadata extraction for compliance reporting
    """
    User_List = []
    directories_seen = set()

    # TODO: Enhance with multi-threading for improved performance across large organizations
    for credential in tqdm(
        f_credentials, desc=f"Looking for users across {len(f_credentials)} Accounts", unit=" accounts"
    ):
        # Skip credentials that failed validation
        if not credential["Success"]:
            logging.info(f"{credential['ErrorMessage']} with roles: {credential['RolesTried']}")
            continue

        # Discover traditional IAM users if requested
        if f_IAM:
            try:
                # Call inventory module to discover IAM users in this account
                User_List.extend(find_iam_users2(credential))
                # Optional verbose logging for user discovery progress (currently commented)
                # logging.info(f"{ERASE_LINE}Account: {credential['AccountId']} Found {len(User_List)} users")
            except ClientError as my_Error:
                # Handle IAM API authorization failures gracefully
                if "AuthFailure" in str(my_Error):
                    logging.error(f"{ERASE_LINE}{credential}: Authorization Failure")

        # Discover AWS Identity Center users if requested
        if f_IDC:
            try:
                # Find out if this account hosts an Identity Center with a user directory
                directory_ids = find_idc_directory_id2(credential)
                for directory_instance_id in directory_ids:
                    # Directory deduplication: if we've already interrogated this directory, skip it
                    if directory_instance_id in directories_seen:
                        continue
                    else:
                        # Mark this directory as processed and discover users
                        directories_seen.update(directory_ids)
                        User_List.extend(find_idc_users2(credential, directory_instance_id))
                # Optional verbose logging for user discovery progress (currently commented)
                # logging.info(f"{ERASE_LINE}Account: {credential['AccountId']} Found {len(User_List)} users")
            except ClientError as my_Error:
                # Handle Identity Center API authorization failures gracefully
                if "AuthFailure" in str(my_Error):
                    logging.error(f"{ERASE_LINE}{credential}: Authorization Failure")
    return User_List


##################
# Main
##################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles
    pRegionList = args.Regions
    pAccounts = args.Accounts
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pAccessRoles = args.AccessRoles
    pFilename = args.Filename
    pIdentityCenter = args.pIdentityCenter
    pIAM = args.pIAM
    # Although I want to the flags to remain
    if not pIAM and not pIdentityCenter:
        pIdentityCenter = True
        pIAM = True
    pRootOnly = args.RootOnly
    pTiming = args.Time
    verbose = args.loglevel
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    CredentialList = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pAccessRoles
    )
    SuccessfulAccountAccesses = [x for x in CredentialList if x["Success"]]
    UserListing = find_all_org_users(CredentialList, pIdentityCenter, pIAM)
    sorted_UserListing = sorted(
        UserListing, key=lambda k: (k["MgmtAccount"], k["AccountId"], k["Region"], k["UserName"])
    )

    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
        "AccountId": {"DisplayOrder": 2, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 3, "Heading": "Region"},
        "UserName": {"DisplayOrder": 4, "Heading": "User Name"},
        "PasswordLastUsed": {"DisplayOrder": 5, "Heading": "Last Used"},
        "Type": {"DisplayOrder": 6, "Heading": "Source"},
    }
    display_results(sorted_UserListing, display_dict, "N/A", pFilename)
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
    print(ERASE_LINE)
    print(
        f"Found {len(UserListing)} users across {len(SuccessfulAccountAccesses)} account{'' if len(SuccessfulAccountAccesses) == 1 else 's'}"
    )
    print()
    print("Thank you for using this script")
    print()

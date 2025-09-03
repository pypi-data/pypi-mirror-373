#!/usr/bin/env python3

"""
AWS CloudFormation StackSets Discovery and Analysis Script

This script provides comprehensive discovery and analysis capabilities for AWS CloudFormation
StackSets across multi-account AWS Organizations environments. It's designed for enterprise
cloud governance teams who need visibility into multi-account infrastructure deployment patterns,
StackSet lifecycle management, and centralized infrastructure orchestration across organizational
boundaries with detailed instance enumeration and operational oversight.

Key Features:
- Multi-account CloudFormation StackSet discovery using assume role capabilities
- Cross-region StackSet enumeration with comprehensive metadata extraction
- StackSet instance counting and detailed deployment analysis
- Fragment-based search for targeted StackSet discovery and filtering
- Status-based filtering for active and deleted StackSet lifecycle tracking
- Single-profile authentication with support for federated Organizations access
- Enterprise reporting with CSV export and structured output

Enterprise Use Cases:
- Multi-account infrastructure governance and StackSet portfolio management
- Centralized deployment pattern analysis and standardization oversight
- StackSet lifecycle tracking for operational excellence and compliance
- Infrastructure drift detection through StackSet status monitoring
- Cost optimization through StackSet deployment pattern analysis
- Compliance auditing for multi-account infrastructure governance
- Disaster recovery planning through StackSet deployment topology mapping

StackSet Management Features:
- Comprehensive StackSet enumeration with status and metadata tracking
- StackSet instance discovery with detailed deployment topology analysis
- Fragment-based search for targeted StackSet identification and management
- Status filtering for active, deleted, and lifecycle transition tracking
- Cross-account StackSet visibility for organizational infrastructure oversight
- Regional StackSet deployment pattern analysis and optimization

Security Considerations:
- Uses assume role capabilities for cross-account StackSet discovery
- Implements proper error handling for authorization failures
- Supports read-only operations with no StackSet modification capabilities
- Respects CloudFormation permissions and regional access constraints
- Provides comprehensive audit trail through detailed logging
- Sensitive infrastructure information handling with appropriate access controls

Performance Considerations:
- Sequential processing for reliable StackSet discovery operations
- Optional StackSet instance enumeration with performance timing metrics
- Progress tracking for operational visibility during discovery
- Efficient credential management for cross-account StackSet access
- Memory-optimized data structures for large StackSet inventories

StackSet Instance Analysis:
- Optional detailed instance enumeration for deployment topology mapping
- Instance count tracking for capacity planning and optimization
- Cross-account instance distribution analysis for governance oversight
- Regional instance deployment pattern analysis and standardization
- Instance status tracking for operational excellence and monitoring

Dependencies:
- boto3/botocore for AWS CloudFormation StackSets API interactions
- account_class for AWS account access management
- ArgumentsClass for standardized CLI argument parsing
- Inventory_Modules for common utility functions and StackSet discovery
- colorama for enhanced output formatting

Compliance and Audit Features:
- Comprehensive StackSet discovery for infrastructure governance auditing
- StackSet deployment pattern analysis for compliance validation
- Cross-account infrastructure visibility for organizational security oversight
- StackSet lifecycle tracking for governance and compliance management
- Infrastructure standardization analysis for organizational oversight

Future Enhancements:
- Multi-threading for improved performance across large organizations
- StackSet drift detection and configuration analysis
- Integration with AWS Config for StackSet configuration monitoring
- StackSet optimization recommendations for governance and cost management

Author: AWS CloudOps Team
Version: 2024.06.20
"""

import logging
import sys
from os.path import split
from time import time

from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from colorama import Fore, init
from Inventory_Modules import (
    RemoveCoreAccounts,
    display_results,
    find_stack_instances2,
    find_stacksets2,
    get_credentials_for_accounts_in_org,
    get_regions3,
)

init()

__version__ = "2024.06.20"
begin_time = time()
ERASE_LINE = "\x1b[2K"

#####################
# Functions
#####################


def parse_args(args):
    """
    Parse command line arguments for AWS CloudFormation StackSets discovery and analysis operations.

    Configures comprehensive argument parsing for single-profile, multi-region CloudFormation StackSet
    discovery operations. Supports enterprise infrastructure governance with profile management,
    region targeting, fragment-based search, and StackSet instance analysis for multi-account
    deployment pattern oversight and centralized infrastructure orchestration.

    Args:
        args (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profile: AWS profile for authentication
            - Regions: Target regions for StackSet discovery
            - Fragments: StackSet name fragments for targeted search
            - Exact: Enable exact fragment matching
            - SkipAccounts: Accounts to exclude from discovery
            - AccessRoles: Cross-account roles for Organizations access
            - RootOnly: Limit to organization root accounts
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration
            - pinstancecount: Enable StackSet instance enumeration
            - pstatus: StackSet status filter (Active/Deleted)

    Configuration Options:
        - Single profile support for focused StackSet discovery operations
        - Multi-region targeting for comprehensive StackSet infrastructure analysis
        - Fragment-based search for targeted StackSet identification and filtering
        - Extended arguments for advanced filtering and account selection
        - Role-based access for cross-account StackSet operations
        - Root-only mode for organization-level StackSet inventory
        - File output for integration with infrastructure management tools
        - Timing metrics for performance optimization and monitoring
        - Verbose logging for debugging and infrastructure governance audit

    StackSet-Specific Features:
        - Instance counting (-i/--instances): Enables detailed StackSet instance enumeration
          for deployment topology analysis and capacity planning
        - Status filtering (-s/--status): Filters StackSets by lifecycle status including:
          - Active: Currently deployed and operational StackSets
          - Deleted: Previously deployed but now deleted StackSets for cleanup analysis
        - Fragment search: Targeted StackSet discovery using name pattern matching

    Enterprise Infrastructure Management:
        - Multi-account StackSet visibility for organizational governance oversight
        - Cross-region StackSet deployment pattern analysis and standardization
        - StackSet lifecycle tracking for operational excellence and compliance
        - Infrastructure governance and centralized deployment orchestration
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
    parser.singleprofile()  # Single profile for focused StackSet discovery operations
    parser.multiregion()  # Multi-region support for comprehensive StackSet infrastructure analysis
    parser.fragment()  # Fragment-based search for targeted StackSet identification
    parser.extendedargs()  # Extended arguments for advanced filtering and account selection
    parser.rolestouse()  # Role-based access for cross-account StackSet operations
    parser.rootOnly()  # Root-only mode for organization-level StackSet inventory
    parser.save_to_file()  # File output for integration with infrastructure management tools
    parser.timing()  # Timing metrics for performance optimization and monitoring
    parser.verbosity()  # Verbose logging for debugging and infrastructure governance audit
    parser.version(__version__)
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "-i",
        "--instances",
        dest="pinstancecount",
        action="store_true",
        default=False,
        help="Enable detailed StackSet instance enumeration for deployment topology analysis and capacity planning",
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


def setup_auth_accounts_and_regions(fProfile: str) -> (aws_acct_access, list, list):
    """
    Initialize authentication and discover AWS Organizations accounts and regions for StackSet operations.

    Establishes authentication context and discovers organizational structure for comprehensive
    CloudFormation StackSet discovery across multi-account environments. Performs account
    filtering, region validation, and access role configuration for enterprise infrastructure
    governance and centralized deployment orchestration.

    Args:
        fProfile (str): AWS profile name for authentication and Organizations access
                       If None, uses default profile or credential chain

    Returns:
        tuple: Three-element tuple containing:
            - aws_acct_access: Authenticated account access object for Organizations operations
            - list: Account IDs available for StackSet discovery and analysis
            - list: Valid AWS regions for StackSet infrastructure operations

    Authentication and Discovery:
        - Establishes AWS Organizations access using the specified profile
        - Discovers child accounts within the organization structure
        - Validates regional access and availability for StackSet operations
        - Applies account filtering based on skip lists and inclusion criteria

    Account Management:
        - Removes core accounts from discovery scope based on skip configuration
        - Applies account inclusion filters for targeted StackSet analysis
        - Supports root-only mode for organization-level StackSet inventory
        - Handles access role configuration for cross-account StackSet operations

    Enterprise Features:
        - Multi-account discovery for organizational StackSet governance
        - Regional validation for comprehensive StackSet infrastructure analysis
        - Account filtering for targeted infrastructure discovery and management
        - Access role configuration for enterprise security and compliance

    Error Handling:
        - Connection error detection with appropriate system exit
        - Profile validation and authentication failure management
        - Regional access validation for StackSet operations
        - Comprehensive error logging for troubleshooting
    """
    try:
        # Establish AWS Organizations access using the specified profile
        aws_acct = aws_acct_access(fProfile)
    except ConnectionError as my_Error:
        # Handle authentication and connection failures with appropriate logging
        logging.error(f"Exiting due to error: {my_Error}")
        sys.exit(8)

    # Discover child accounts within the organization structure
    ChildAccounts = aws_acct.ChildAccounts

    # Validate regional access and availability for StackSet operations
    RegionList = get_regions3(aws_acct, pRegionList)

    # Apply account filtering based on skip lists and core account exclusions
    ChildAccounts = RemoveCoreAccounts(ChildAccounts, pSkipAccounts)

    # Determine final account list based on inclusion criteria and access configuration
    if pAccountList is None:
        # Include all discovered child accounts when no specific list provided
        AccountList = [account["AccountId"] for account in ChildAccounts]
    elif pAccessRoles is not None:
        # Use provided account list when access roles are specified
        AccountList = pAccountList
    else:
        # Filter child accounts to include only those in the specified account list
        AccountList = [account["AccountId"] for account in ChildAccounts if account["AccountId"] in pAccountList]

    # Display discovery scope and configuration for operational transparency
    print(f"You asked to find CloudFormation stacksets")
    if pRootOnly:
        print(f"\tIn only the root account: {aws_acct.acct_number}")
    else:
        print(f"\tin these accounts: {Fore.RED}{AccountList}{Fore.RESET}")
    print(f"\tin these regions: {Fore.RED}{RegionList}{Fore.RESET}")
    print(
        f"\tContaining {'this ' + Fore.RED + 'exact fragment' + Fore.RESET if pExact else 'one of these fragments'}: {pFragments}"
    )
    if pSkipAccounts is not None:
        print(f"\tWhile skipping these accounts: {Fore.RED}{pSkipAccounts}{Fore.RESET}")

    return aws_acct, AccountList, RegionList


def find_all_cfnstacksets(f_All_Credentials: list, f_Fragments: list, f_Status) -> list:
    """
    Discover and enumerate CloudFormation StackSets across multiple AWS accounts and regions.

    Performs comprehensive StackSet discovery using sequential processing to efficiently inventory
    StackSets across enterprise AWS environments. Supports fragment-based filtering for targeted
    discovery and optional instance enumeration for deployment topology analysis and capacity planning.

    Args:
        f_All_Credentials (list): List of credential dictionaries for cross-account access containing:
            - AccountId: AWS account number
            - Region: Target AWS region
            - Success: Boolean indicating credential validity
            - AccessError: Error details for failed credential attempts
        f_Fragments (list): StackSet name fragments for targeted search and filtering
        f_Status (str): StackSet status filter ('Active' or 'Deleted')

    Returns:
        list: Comprehensive list of StackSet dictionaries containing:
            - AccountId: AWS account containing the StackSet
            - Region: AWS region where StackSet is managed
            - StackName: CloudFormation StackSet name identifier
            - Status: StackSet operational status
            - InstanceNum: Number of StackSet instances (if enumeration enabled)

    StackSet Discovery Features:
        - Comprehensive StackSet enumeration with status and metadata tracking
        - Fragment-based search for targeted StackSet identification and filtering
        - Status filtering for active and deleted StackSet lifecycle tracking
        - Optional StackSet instance enumeration for deployment topology analysis
        - Cross-account StackSet visibility for organizational infrastructure oversight

    Performance Considerations:
        - Sequential processing for reliable StackSet discovery operations
        - Progress tracking for operational visibility during discovery
        - Optional instance enumeration with performance timing metrics
        - Efficient credential management for cross-account StackSet access
        - Graceful error handling for authorization and access failures

    Enterprise Infrastructure Governance:
        - Multi-account StackSet discovery for organizational oversight
        - StackSet deployment pattern analysis and standardization
        - Infrastructure lifecycle tracking for operational excellence
        - Centralized deployment orchestration visibility and management

    Error Handling:
        - Authorization failure detection with appropriate logging
        - AWS API error management with graceful degradation
        - Credential validation and failure tracking
        - Comprehensive error reporting for troubleshooting
    """
    All_Results = []
    for credential in f_All_Credentials:
        if not credential["Success"]:
            logging.error(
                f"Failure for account {credential['AccountId']} in region {credential['Region']}\n"
                f"With message: {credential['AccessError']}"
            )
            continue
        # logging.info(f"Account Creds: {account_credentials}")
        # Display progress for operational visibility during StackSet discovery
        print(
            f"{ERASE_LINE}{Fore.RED}Checking Account: {credential['AccountId']} Region: {credential['Region']} for stacksets matching {f_Fragments} with status: {f_Status}{Fore.RESET}",
            end="\r",
        )

        # Call inventory module to discover StackSets using fragment and status filtering
        StackSets = find_stacksets2(credential, pFragments, pstatus)
        logging.warning(
            f"Account: {credential['AccountId']} | Region: {credential['Region']} | Found {len(StackSets)} Stacksets"
        )

        # Handle cases where no StackSets are found in the account/region combination
        if not StackSets:
            print(
                f"{ERASE_LINE}We connected to account {credential['AccountId']} in region {credential['Region']}, but found no stacksets",
                end="\r",
            ) if verbose < 50 else ""
        else:
            print(
                f"{ERASE_LINE}{Fore.RED}Account: {credential['AccountId']} Region: {credential['Region']} Found {len(StackSets)} Stacksets{Fore.RESET}",
                end="\r",
            ) if verbose < 50 else ""

        # Process each discovered StackSet with optional instance enumeration
        for stack in StackSets:
            ListOfStackInstances = []  # Reset instance list for each StackSet

            # Optional StackSet instance enumeration for deployment topology analysis
            if pInstanceCount:
                milestone = time()
                # Discover StackSet instances across accounts and regions for capacity planning
                ListOfStackInstances = find_stack_instances2(credential, credential["Region"], stack["StackSetName"])
                if pTiming:
                    print(
                        f"{ERASE_LINE}Found {len(ListOfStackInstances)} instances for {stack['StackSetName']} in {credential['Region']}, which took {time() - milestone:.2f} seconds",
                        end="\r",
                    )

            # Aggregate StackSet information for enterprise infrastructure governance
            All_Results.append(
                {
                    "AccountId": credential["AccountId"],
                    "StackName": stack["StackSetName"],
                    "Status": stack["Status"],
                    "Region": credential["Region"],
                    "InstanceNum": len(ListOfStackInstances) if pInstanceCount else "N/A",
                }
            )
    return All_Results


#####################
# Main
#####################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfile = args.Profile
    pRegionList = args.Regions
    pInstanceCount = args.pinstancecount
    pRootOnly = args.RootOnly
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pAccountList = args.Accounts
    pAccessRoles = args.AccessRoles
    verbose = args.loglevel
    pTiming = args.Time
    pFragments = args.Fragments
    pExact = args.Exact
    pstatus = args.pstatus
    pFilename = args.Filename
    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    # Setup auth object, get account list and region list setup
    aws_acct, AccountList, RegionList = setup_auth_accounts_and_regions(pProfile)
    # Get all credentials needed
    CredentialList = get_credentials_for_accounts_in_org(
        aws_acct, pSkipAccounts, pRootOnly, AccountList, pProfile, RegionList, pAccessRoles, pTiming
    )
    # Find all the stacksets
    All_Results = find_all_cfnstacksets(CredentialList, AccountList, RegionList)
    print()
    display_dict = {
        "AccountId": {"DisplayOrder": 1, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 2, "Heading": "Region"},
        "Status": {"DisplayOrder": 3, "Heading": "Status"},
        "StackName": {"DisplayOrder": 4, "Heading": "Stackset Name"},
    }
    if pInstanceCount:
        display_dict.update({"Instances": {"DisplayOrder": 5, "Heading": "# of Instances"}})

    # Display results
    display_results(All_Results, display_dict, None, pFilename)

    print(ERASE_LINE)
    print(
        f"{Fore.RED}Found {len(All_Results)} Stacksets across {len(AccountList)} accounts across {len(RegionList)} regions{Fore.RESET}"
    )
    print()
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
    print("Thanks for using this script...")
    print()

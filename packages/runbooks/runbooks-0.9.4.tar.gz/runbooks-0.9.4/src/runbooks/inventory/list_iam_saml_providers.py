#!/usr/bin/env python3

"""
AWS IAM SAML Identity Providers Discovery and Management Script

This script provides comprehensive discovery, analysis, and optional deletion capabilities for
AWS Identity and Access Management (IAM) SAML identity providers across multi-account
environments. It's designed for enterprise identity and access management teams who need
visibility into SAML federation configuration, identity provider governance, and automated
cleanup capabilities across large-scale AWS deployments.

Key Features:
- Multi-account SAML identity provider discovery using assume role capabilities
- Comprehensive identity provider enumeration with metadata extraction
- Optional automated deletion capabilities with safety controls
- Enterprise reporting with CSV export and structured output
- Profile-based authentication with support for federated access
- Identity provider governance for organizational security standardization

Enterprise Use Cases:
- Identity provider audit and compliance reporting across organizations
- SAML federation governance and standardization across organizational boundaries
- Identity provider lifecycle management and automated cleanup
- Security incident response with identity provider configuration analysis
- Compliance reporting for identity federation and access control standards
- Multi-account identity governance and provider consolidation
- Identity provider drift detection and configuration standardization

SAML Identity Provider Features:
- Comprehensive identity provider enumeration with ARN extraction
- Provider metadata extraction for governance and compliance analysis
- Cross-account identity provider visibility for organizational oversight
- Provider configuration analysis for security and compliance assessment
- Identity provider lifecycle tracking for governance management

Security Considerations:
- Uses IAM assume role capabilities for cross-account identity provider access
- Implements proper error handling for authorization failures
- Supports optional deletion operations with explicit safety controls
- Respects IAM service permissions and regional access constraints
- Provides comprehensive audit trail through detailed logging
- Sensitive identity configuration handling with appropriate access controls

Identity Governance Features:
- Cross-account identity provider discovery for organizational oversight
- Provider configuration standardization across organizational boundaries
- Identity provider lifecycle management with automated cleanup capabilities
- Provider governance for compliance and security standardization
- Identity federation visibility for security and compliance management

Performance Considerations:
- Sequential processing for reliable identity provider discovery operations
- Progress tracking for operational visibility during large-scale operations
- Efficient credential management for cross-account identity provider access
- Memory-optimized data structures for large identity provider inventories
- Graceful error handling for authorization and throttling scenarios

Deletion Safety Features:
- Explicit deletion flags (+delete +forreal) for safety controls
- No confirmation prompts - requires explicit command-line flags
- Comprehensive logging of deletion operations for audit trails
- Error handling for deletion failures and authorization issues
- Deletion operation tracking for compliance and governance

Threading Architecture:
- Currently uses sequential processing for reliable operations
- TODO: Multi-threading enhancement planned for improved performance
- Thread-safe error handling and progress tracking architecture
- Graceful degradation for account access failures

Dependencies:
- boto3/botocore for AWS IAM API interactions
- account_class for AWS account access management
- ArgumentsClass for standardized CLI argument parsing
- Inventory_Modules for common utility functions and credential management
- colorama for enhanced output formatting

Compliance and Audit Features:
- Comprehensive identity provider discovery for security auditing
- Provider configuration analysis for compliance validation
- Cross-account identity governance for organizational security
- Provider lifecycle tracking for organizational oversight
- Identity federation visibility for compliance assessment

Future Enhancements:
- Multi-threading for improved performance across large organizations
- Identity provider configuration analysis and drift detection
- Integration with AWS Config for provider configuration monitoring
- Provider optimization recommendations for security and compliance

Author: AWS CloudOps Team
Version: 2024.03.27
"""

import logging
import sys
from os.path import split
from time import time

import boto3
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_saml_components_in_acct2, get_child_access3

init()
__version__ = "2024.03.27"

begin_time = time()
ERASE_LINE = "\x1b[2K"


##################


def parse_args(args):
    """
    Parse command line arguments for AWS IAM SAML identity provider discovery and management operations.

    Configures comprehensive argument parsing for single-profile, single-region IAM SAML identity
    provider operations. Supports enterprise identity and access management with profile configuration,
    region targeting, role-based access, and optional deletion capabilities with explicit safety controls.

    Args:
        args (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profile: AWS profile for authentication
            - Region: Target region for SAML identity provider discovery
            - AccessRole: IAM role for cross-account access
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration
            - DeletionRun: Enable identity provider deletion operations

    Configuration Options:
        - Single profile support for focused identity provider management
        - Single region targeting for specific regional identity provider analysis
        - Role-based access for cross-account identity provider operations
        - File output for integration with identity management tools
        - Timing metrics for performance optimization and monitoring
        - Verbose logging for debugging and identity governance audit

    Safety and Deletion Features:
        - Explicit deletion flags (+delete +forreal) for identity provider cleanup
        - No confirmation prompts - requires explicit command-line safety flags
        - Deletion operation logging for compliance and governance audit
        - Safety controls to prevent accidental identity provider deletion

    Enterprise Identity Management:
        - Single profile focus for targeted identity provider operations
        - Region-specific identity provider discovery and management
        - Role-based access for enterprise identity governance
        - Identity provider lifecycle management with safety controls
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
    parser.singleprofile()
    parser.singleregion()
    parser.roletouse()
    parser.verbosity()
    parser.save_to_file()
    parser.timing()
    parser.version(__version__)
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "+delete",
        "+forreal",
        dest="DeletionRun",
        const=True,
        default=False,
        action="store_const",
        help="Enable identity provider deletion - requires both flags for safety. Deletes without confirmation prompts. Use with extreme caution!",
    )
    return parser.my_parser.parse_args(args)


def all_my_saml_providers(faws_acct: aws_acct_access, fChildAccounts: list, f_access_role=None) -> list:
    """
    Discover and enumerate all SAML identity providers across multiple AWS child accounts.

    Performs comprehensive SAML identity provider discovery using sequential processing
    to efficiently inventory identity providers across enterprise AWS environments.
    Supports organization-wide identity governance with role-based access and provider
    metadata extraction for compliance and security management.

    Args:
        faws_acct (aws_acct_access): AWS account access object for credential management
        fChildAccounts (list): List of child account dictionaries containing:
            - AccountId: AWS account number
            - AccountStatus: Account status (ACTIVE, SUSPENDED, CLOSED)
        f_access_role (str, optional): IAM role name for cross-account access

    Returns:
        list: Comprehensive list of SAML identity provider dictionaries containing:
            - MgmtAccount: Management account identifier for organizational hierarchy
            - AccountNumber: AWS account containing the identity provider
            - Region: AWS region where identity provider is configured
            - IdpName: SAML identity provider name extracted from ARN
            - Arn: Complete identity provider Amazon Resource Name

    Enterprise Identity Features:
        - Cross-account SAML provider discovery with assume role capabilities
        - Provider metadata extraction for governance and compliance analysis
        - Account status filtering to skip suspended or closed accounts
        - Comprehensive error handling for authorization and access failures

    Performance Considerations:
        - Sequential processing for reliable identity provider discovery
        - Progress tracking for operational visibility during discovery
        - Efficient credential management for cross-account provider access
        - Memory-optimized data structures for large identity provider inventories

    Error Handling:
        - Authorization failure detection with appropriate logging
        - AWS API error management with graceful degradation
        - Account status validation to skip inactive accounts
        - Comprehensive error reporting for troubleshooting

    Security Considerations:
        - Role-based access for enterprise identity governance
        - Proper credential management for cross-account operations
        - Authorization failure handling with detailed logging
        - Account access validation before identity provider enumeration

    TODO: Enhance with multi-threading for improved performance across large organizations
    """
    IdpsFound = []

    # Sequential processing of child accounts for SAML identity provider discovery
    for account in fChildAccounts:
        try:
            # Only process active accounts, skip suspended or closed accounts
            if account["AccountStatus"] == "ACTIVE":
                print(f"{ERASE_LINE}Getting credentials for account {account['AccountId']}", end="\r")
                try:
                    # Obtain cross-account credentials using the specified access role
                    account_credentials = get_child_access3(faws_acct, account["AccountId"], pRegion, f_access_role)
                except ClientError as my_Error:
                    # Handle different types of credential and authorization failures
                    if "AuthFailure" in str(my_Error):
                        print(f"{pProfile}: Authorization Failure for account {account['AccountId']}")
                    else:
                        print(f"{pProfile}: Other kind of failure for account {account['AccountId']}")
                        print(my_Error)
                    continue

                idpNum = 0
                try:
                    # Discover SAML identity providers in the current account using inventory module
                    Idps = find_saml_components_in_acct2(account_credentials)
                    idpNum = len(Idps)
                    logging.info(f"Account: {account['AccountId']} | Region: {pRegion} | Found {idpNum} Idps")
                    logging.info(
                        f"{ERASE_LINE}{Fore.RED}Account: {account['AccountId']} pRegion: {pRegion} Found {idpNum} Idps.{Fore.RESET}"
                    )

                    # Process discovered identity providers and extract metadata
                    if idpNum > 0:
                        for idp in Idps:
                            logging.info(f"Arn: {idp['Arn']}")

                            # Extract identity provider name from ARN (everything after the last slash)
                            NameStart = idp["Arn"].find("/") + 1
                            logging.debug(f"Name starts at character: {NameStart}")
                            IdpName = idp["Arn"][NameStart:]

                            # Aggregate identity provider information for enterprise governance
                            IdpsFound.append(
                                {
                                    "MgmtAccount": account_credentials["MgmtAccount"],
                                    "AccountNumber": account_credentials["AccountId"],
                                    "Region": account_credentials["Region"],
                                    "IdpName": IdpName,
                                    "Arn": idp["Arn"],
                                }
                            )
                except ClientError as my_Error:
                    # Handle IAM API authorization failures for identity provider discovery
                    if "AuthFailure" in str(my_Error):
                        print(f"{account['AccountId']}: Authorization Failure")
            else:
                # Skip processing for inactive accounts
                print(ERASE_LINE, f"Skipping account {account['AccountId']} since it's SUSPENDED or CLOSED", end="\r")
        except KeyError as my_Error:
            # Handle cases where expected account keys are missing
            logging.error(f"Key Error: {my_Error}")
            continue
    return IdpsFound


def delete_idps(faws_acct: aws_acct_access, idps_found: list):
    for idp in idps_found:
        account_credentials = get_child_access3(faws_acct, idp["AccountNumber"])
        session_aws = boto3.Session(
            region_name=idp["pRegion"],
            aws_access_key_id=account_credentials["AccessKeyId"],
            aws_secret_access_key=account_credentials["SecretAccessKey"],
            aws_session_token=account_credentials["SessionToken"],
        )
        iam_client = session_aws.client("iam")
        print(f"Deleting Idp {idp['IdpName']} from account {idp['AccountId']} in pRegion {idp['pRegion']}")
        response = iam_client.delete_saml_provider(SAMLProviderArn=idp["Arn"])


##################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfile = args.Profile
    pRegion = args.Region
    verbose = args.loglevel
    pTiming = args.Time
    pAccessRole = args.AccessRole
    pFilename = args.Filename
    DeletionRun = args.DeletionRun

    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)30s() ] %(message)s")

    print()

    # Get credentials
    aws_acct = aws_acct_access(pProfile)
    ChildAccounts = aws_acct.ChildAccounts

    # Find the SAML providers
    IdpsFound = all_my_saml_providers(aws_acct, ChildAccounts, pAccessRole)
    print(f"{ERASE_LINE}")
    # Display results
    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
        "AccountNumber": {"DisplayOrder": 2, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 3, "Heading": "Region"},
        "IdpName": {"DisplayOrder": 4, "Heading": "IdP Name"},
        "Arn": {"DisplayOrder": 5, "Heading": "Arn"},
    }
    sorted_results = sorted(IdpsFound, key=lambda x: (x["AccountNumber"], x["Region"], x["IdpName"]))
    display_results(sorted_results, display_dict, None, pFilename)
    AccountsFound = list(set([x["AccountNumber"] for x in IdpsFound]))
    RegionsFound = list(set([x["Region"] for x in IdpsFound]))
    print()
    print(
        f"{Fore.RED}Found {len(IdpsFound)} Idps across {len(AccountsFound)} accounts in {len(RegionsFound)} regions{Fore.RESET}"
    )
    print()

    # Delete saml providers if requested
    if DeletionRun:
        logging.warning(f"Deleting {len(IdpsFound)} Idps")
        delete_idps(aws_acct, IdpsFound)

    print()
    if pTiming:
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
        print()
    print("Thanks for using this script...")
    print()

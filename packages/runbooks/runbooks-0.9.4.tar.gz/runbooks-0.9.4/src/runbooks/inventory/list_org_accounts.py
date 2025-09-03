#!/usr/bin/env python3
"""
AWS Organizations Account Inventory

A comprehensive AWS Organizations account discovery tool that provides detailed visibility
into multi-account structures across all accessible Management Accounts. Supports account
status analysis, organizational hierarchy mapping, and cross-organization account lookup.

**AWS API Mapping**: `organizations.list_accounts()`, `organizations.describe_organization()`

Features:
    - Multi-organization account discovery
    - Management Account identification and validation
    - Account status tracking (ACTIVE, SUSPENDED, etc.)
    - Cross-organization account lookup by ID
    - Short-form and detailed organizational views
    - Root profile discovery and listing
    - Account hierarchy visualization

Compatibility:
    - AWS Organizations with cross-account roles
    - AWS Control Tower managed accounts
    - Multiple AWS Organizations access
    - AWS Account Factory provisioned accounts

Example:
    Discover all accounts across organizations:
    ```bash
    python org_list_accounts.py --profile my-org-profile
    ```

    Short form listing for quick overview:
    ```bash
    python org_list_accounts.py --profile my-profile --short
    ```

    Find which organization contains specific accounts:
    ```bash
    python org_list_accounts.py --acct 123456789012 987654321098
    ```

    List only root profiles:
    ```bash
    python org_list_accounts.py --rootonly
    ```

Use Cases:
    - AWS Organizations discovery and mapping
    - Account governance and compliance auditing
    - Cross-organization account tracking
    - Management Account validation
    - Account migration planning

Requirements:
    - IAM permissions: `organizations:ListAccounts`, `organizations:DescribeOrganization`
    - AWS Organizations access (Management Account or delegated admin)
    - Python 3.8+ with required dependencies

Author:
    AWS Cloud Foundations Team

Version:
    2024.05.08
"""

import logging
import sys
from os.path import split
from time import time

from ArgumentsClass import CommonArguments

# from botocore.exceptions import ClientError, NoCredentialsError, InvalidConfigError
from colorama import Fore, Style, init
from Inventory_Modules import display_results, get_org_accounts_from_profiles, get_profiles

init()
__version__ = "2024.05.08"
ERASE_LINE = "\x1b[2K"
begin_time = time()


# TODO: If they provide a profile that isn't a root profile, you should find out which org it belongs to, and then show the org for that.
#  This will be difficult, since we don't know which profile that belongs to. Hmmm...


##################
# Functions
##################
def parse_args(f_arguments):
    """
    Parse and validate command-line arguments for AWS Organizations account discovery.

    Configures the argument parser with Organizations-specific options including
    profile management, output formatting, and account lookup capabilities.
    Uses the standardized CommonArguments framework for consistency.

    Args:
        f_arguments (list): Command-line arguments to parse (typically sys.argv[1:])

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: AWS profiles for multi-organization access
            - RootOnly: Flag to display only Management Accounts
            - pShortform: Brief output format (profiles only, not child accounts)
            - accountList: Specific account IDs to lookup across organizations
            - SkipProfiles: Profiles to exclude from discovery
            - Filename: Output file prefix for CSV export
            - Time: Enable execution timing measurements
            - Other standard framework arguments

    Script-Specific Arguments:
        --short/-s/-q: Enables brief output showing only profile-level information
                      without detailed child account enumeration. Improves performance
                      for large organizations where only high-level view is needed.

        --acct/-A: Cross-organization account lookup feature. Accepts multiple
                  account IDs and determines which organization each belongs to.
                  Essential for account governance and migration planning.

    Use Cases:
        - Quick organization overview: --short for high-level visibility
        - Account location discovery: --acct 123456789012 to find parent org
        - Management account audit: --rootonly for governance review
        - Comprehensive inventory: default mode for complete account listing
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()

    # Enable multi-profile support for cross-organization discovery
    parser.multiprofile()

    # Add extended arguments (skip accounts, skip profiles, etc.)
    parser.extendedargs()

    # Enable root-only filtering for Management Account focus
    parser.rootOnly()

    # Add execution timing capabilities
    parser.timing()

    # Enable CSV file export functionality
    parser.save_to_file()

    # Configure logging verbosity levels
    parser.verbosity()

    # Set script version for --version flag
    parser.version(__version__)

    # Add script-specific argument group
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")

    # Short-form display option for performance and readability
    local.add_argument(
        "-s",
        "-q",
        "--short",
        help="Display only brief listing of the profile accounts, and not the Child Accounts under them",
        action="store_const",
        dest="pShortform",
        const=True,
        default=False,
    )

    # Cross-organization account lookup capability
    local.add_argument(
        "-A", "--acct", help="Find which Org this account is a part of", nargs="*", dest="accountList", default=None
    )

    return parser.my_parser.parse_args(f_arguments)


def all_my_orgs(
    f_Profiles: list,
    f_SkipProfiles: list,
    f_AccountList: list,
    f_Timing: bool,
    f_RootOnly: bool,
    f_SaveFilename: str,
    f_Shortform: bool,
    f_verbose,
):
    """
    Execute comprehensive AWS Organizations discovery across multiple management accounts.

    This is the core orchestration function that discovers and maps AWS Organizations
    hierarchies, identifies management accounts, enumerates child accounts, and provides
    detailed organizational visibility across multiple AWS Organizations.

    Args:
        f_Profiles (list): AWS profiles to analyze for organization membership
        f_SkipProfiles (list): Profiles to exclude from discovery process
        f_AccountList (list): Specific account IDs to lookup across organizations
        f_Timing (bool): Enable execution timing measurements and display
        f_RootOnly (bool): Limit output to Management Accounts only
        f_SaveFilename (str): Output file prefix for CSV export (None for console only)
        f_Shortform (bool): Brief output format excluding child account details
        f_verbose: Logging verbosity level for detailed operational logging

    Returns:
        dict: Comprehensive organizational data containing:
            - OrgsFound: List of Management Account IDs discovered
            - StandAloneAccounts: Non-organizational standalone accounts
            - ClosedAccounts: Suspended or closed account IDs
            - FailedProfiles: Profiles that failed authentication/access
            - AccountList: Complete account inventory with metadata

    Processing Workflow:
        1. Profile Resolution: Convert profile names to validated credential sets
        2. Organization Discovery: Query each profile for organizational context
        3. Account Enumeration: List all child accounts for Management Accounts
        4. Status Analysis: Identify suspended, closed, or problematic accounts
        5. Output Generation: Format results for console display or CSV export
        6. Cross-Reference Lookup: Match requested account IDs to organizations

    Output Formats:
        - Console Mode: Formatted tables with colored output for status highlighting
        - CSV Mode: Pipe-delimited files suitable for data analysis and reporting
        - Short Mode: Profile-level summary without child account enumeration
        - Lookup Mode: Targeted account-to-organization mapping

    Error Handling:
        - Profile failures are logged and tracked but don't stop processing
        - Authentication errors are captured with detailed error messages
        - Missing organizations are handled gracefully with fallback behavior
        - API rate limits and throttling are managed through sequential processing

    Performance Considerations:
        - Sequential profile processing (no threading due to AWS API complexity)
        - Cached organization data to avoid redundant API calls
        - Progress indicators for long-running discovery operations
        - Memory-efficient handling of large organizational hierarchies

    Security Features:
        - Read-only operations with minimal required permissions
        - No credential storage or caching beyond execution scope
        - Audit trail through comprehensive logging
        - Safe handling of cross-account access patterns
    """
    ProfileList = get_profiles(fSkipProfiles=f_SkipProfiles, fprofiles=f_Profiles)
    # print("Capturing info for supplied profiles")
    logging.info(f"These profiles were requested {f_Profiles}.")
    logging.warning(f"These profiles are being checked {ProfileList}.")
    print(f"Please bear with us as we run through {len(ProfileList)} profiles")
    AllProfileAccounts = get_org_accounts_from_profiles(ProfileList)
    AccountList = []
    FailedProfiles = []
    OrgsFound = []

    # Print out the results
    if f_Timing:
        print()
        print(f"It's taken {Fore.GREEN}{time() - begin_time:.2f}{Fore.RESET} seconds to find profile accounts...")
        print()
    fmt = "%-23s %-15s %-15s %-12s %-10s"
    print("<------------------------------------>")
    print(fmt % ("Profile Name", "Account Number", "Payer Org Acct", "Org ID", "Root Acct?"))
    print(fmt % ("------------", "--------------", "--------------", "------", "----------"))

    for item in AllProfileAccounts:
        if not item["Success"]:
            # If the profile failed, don't print anything and continue on.
            FailedProfiles.append(item["profile"])
            logging.error(f"{item['profile']} errored. Message: {item['ErrorMessage']}")
        else:
            if item["RootAcct"]:
                # If the account is a root account, capture it for display later
                OrgsFound.append(item["MgmtAccount"])
            # Print results for all profiles
            item["AccountId"] = item["aws_acct"].acct_number
            item["AccountStatus"] = item["aws_acct"].AccountStatus
            # item['AccountEmail'] = item['aws_acct'].
            try:
                if f_RootOnly and not item["RootAcct"]:
                    # If we're only looking for root accounts, and this isn't one, don't print anything and continue on.
                    continue
                else:
                    logging.info(f"{item['profile']} was successful.")
                    print(
                        f"{Fore.RED if item['RootAcct'] else ''}{item['profile']:23s} {item['aws_acct'].acct_number:15s} {item['MgmtAccount']:15s} {str(item['OrgId']):12s} {item['RootAcct']}{Fore.RESET}"
                    )
            except TypeError as my_Error:
                logging.error(f"Error - {my_Error} on {item}")
                pass

    """
	If I create a dictionary from the Root Accts and Root Profiles Lists - 
	I can use that to determine which profile belongs to the root user of my (child) account.
	But this dictionary is only guaranteed to be valid after ALL profiles have been checked, 
	so... it doesn't solve our issue - unless we don't write anything to the screen until *everything* is done, 
	and we keep all output in another dictionary - where we can populate the missing data at the end... 
	but that takes a long time, since nothing would be sent to the screen in the meantime.
	"""

    print(ERASE_LINE)
    print("-------------------")

    if f_Shortform:
        # The user specified "short-form" which means they don't want any information on child accounts.
        return_response = {
            "OrgsFound": OrgsFound,
            "FailedProfiles": FailedProfiles,
            "AllProfileAccounts": AllProfileAccounts,
        }
    else:
        NumOfOrgAccounts = 0
        ClosedAccounts = []
        FailedAccounts = 0
        account = dict()
        ProfileNameLength = len("Organization's Profile")

        for item in AllProfileAccounts:
            # AllProfileAccounts holds the list of account class objects of the accounts associated with the profiles it found.
            if item["Success"] and not item["RootAcct"]:
                account.update(item["aws_acct"].ChildAccounts[0])
                account.update({"Profile": item["profile"]})
                AccountList.append(account.copy())
            elif item["Success"] and item["RootAcct"]:
                for child_acct in item["aws_acct"].ChildAccounts:
                    account.update(child_acct)
                    account.update({"Profile": item["profile"]})
                    ProfileNameLength = max(len(item["profile"]), ProfileNameLength)
                    AccountList.append(account.copy())
                    if not child_acct["AccountStatus"] == "ACTIVE":
                        ClosedAccounts.append(child_acct["AccountId"])

                NumOfOrgAccounts += len(item["aws_acct"].ChildAccounts)
            elif not item["Success"]:
                FailedAccounts += 1
                continue

        # Display results on screen
        if f_SaveFilename is None:
            fmt = "%-23s %-15s"
            print()
            print(fmt % ("Organization's Profile", "Root Account"))
            print(fmt % ("----------------------", "------------"))
            for item in AllProfileAccounts:
                if item["Success"] and item["RootAcct"]:
                    print(
                        f"{item['profile']:{ProfileNameLength}s} {Style.BRIGHT}{item['MgmtAccount']:15s}{Style.RESET_ALL}"
                    )
                    print(
                        f"\t{'Child Account Number':{len('Child Account Number')}s} {'Child Account Status':{len('Child Account Status')}s} {'Child Email Address'}"
                    )
                    for child_acct in item["aws_acct"].ChildAccounts:
                        print(
                            f"\t{Fore.RED if not child_acct['AccountStatus'] == 'ACTIVE' else ''}{child_acct['AccountId']:{len('Child Account Number')}s} {child_acct['AccountStatus']:{len('Child Account Status')}s} {child_acct['AccountEmail']}{Fore.RESET}"
                        )

        elif f_SaveFilename is not None:
            # The user specified a file name, which means they want a (pipe-delimited) CSV file with the relevant output.
            display_dict = {
                "MgmtAccount": {"DisplayOrder": 1, "Heading": "Parent Acct"},
                "AccountId": {"DisplayOrder": 2, "Heading": "Account Number"},
                "AccountStatus": {"DisplayOrder": 3, "Heading": "Account Status", "Condition": ["SUSPENDED", "CLOSED"]},
                "AccountEmail": {"DisplayOrder": 4, "Heading": "Email"},
            }
            if pRootOnly:
                sorted_Results = sorted(AllProfileAccounts, key=lambda d: (d["MgmtAccount"], d["AccountId"]))
            else:
                sorted_Results = sorted(AccountList, key=lambda d: (d["MgmtAccount"], d["AccountId"]))
            display_results(sorted_Results, display_dict, "None", f_SaveFilename)

        StandAloneAccounts = [
            x["AccountId"]
            for x in AccountList
            if x["MgmtAccount"] == x["AccountId"] and x["AccountEmail"] == "Not an Org Management Account"
        ]
        FailedProfiles = [i["profile"] for i in AllProfileAccounts if not i["Success"]]
        OrgsFound = [i["MgmtAccount"] for i in AllProfileAccounts if i["RootAcct"]]
        StandAloneAccounts.sort()
        FailedProfiles.sort()
        OrgsFound.sort()
        ClosedAccounts.sort()

        print()
        print(f"Number of Organizations: {len(OrgsFound)}")
        print(f"Number of Organization Accounts: {NumOfOrgAccounts}")
        print(f"Number of Standalone Accounts: {len(StandAloneAccounts)}")
        print(f"Number of suspended or closed accounts: {len(ClosedAccounts)}")
        print(f"Number of profiles that failed: {len(FailedProfiles)}")
        if f_verbose < 50:
            print("----------------------")
            print(f"The following accounts are the Org Accounts: {OrgsFound}")
            print(f"The following accounts are Standalone: {StandAloneAccounts}") if len(
                StandAloneAccounts
            ) > 0 else None
            print(f"The following accounts are closed or suspended: {ClosedAccounts}") if len(
                ClosedAccounts
            ) > 0 else None
            print(f"The following profiles failed: {FailedProfiles}") if len(FailedProfiles) > 0 else None
            print("----------------------")
        print()
        return_response = {
            "OrgsFound": OrgsFound,
            "StandAloneAccounts": StandAloneAccounts,
            "ClosedAccounts": ClosedAccounts,
            "FailedProfiles": FailedProfiles,
            "AccountList": AccountList,
        }

    if f_AccountList is not None:
        print(f"Found the requested account number{'' if len(AccountList) == 1 else 's'}:")
        for acct in AccountList:
            if acct["AccountId"] in f_AccountList:
                print(
                    f"Profile: {acct['Profile']} | Org: {acct['MgmtAccount']} | Account: {acct['AccountId']} | Status: {acct['AccountStatus']} | Email: {acct['AccountEmail']}"
                )

    return return_response


##################
# Main
##################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    pProfiles = args.Profiles
    pRootOnly = args.RootOnly
    pTiming = args.Time
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    verbose = args.loglevel
    pSaveFilename = args.Filename
    pShortform = args.pShortform
    pAccountList = args.accountList
    logging.basicConfig(
        level=verbose, format="[%(filename)s:%(lineno)s - %(processName)s %(threadName)s %(funcName)20s() ] %(message)s"
    )
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    all_my_orgs(pProfiles, pSkipProfiles, pAccountList, pTiming, pRootOnly, pSaveFilename, pShortform, verbose)

    print()
    if pTiming:
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
        print()
    print("Thanks for using this script")
    print()

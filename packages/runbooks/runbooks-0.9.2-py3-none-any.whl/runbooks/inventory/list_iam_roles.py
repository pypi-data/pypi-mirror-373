#!/usr/bin/env python3
"""
AWS IAM Role Inventory and Management Tool

CRITICAL SECURITY WARNING: This script can DELETE IAM roles across multiple AWS accounts.
Exercise extreme caution when using deletion features in production environments.

Purpose:
    Discovers and inventories IAM roles across AWS Organizations with optional deletion
    capabilities. Provides comprehensive role analysis with fragment-based filtering
    and bulk management operations for enterprise IAM governance.

AWS API Operations:
    - iam.list_roles(): Primary API for role discovery
    - iam.list_attached_role_policies(): Policy attachment analysis
    - iam.detach_role_policy(): Policy detachment for deletion
    - iam.delete_role_policy(): Inline policy cleanup
    - iam.delete_role(): Role deletion operation

Destructive Operations:
    The +delete/+d flag enables IRREVERSIBLE role deletion across multiple accounts.
    Includes safety confirmations and force options for automation scenarios.

Security Features:
    - Multi-stage confirmation for destructive operations
    - Comprehensive policy detachment before role deletion
    - Force flag with delay for automation safety
    - Detailed audit logging of all operations

Usage:
    python list_iam_roles.py -p <profile> --fragment <role_name_fragment>
    python list_iam_roles.py -p <profile> --fragment <fragment> +delete

Author: AWS Cloud Foundations Team
Version: 2023.11.06
Maintained: IAM Security Team
"""

import logging
import sys
from time import sleep, time

import boto3
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_in, get_all_credentials

init()
__version__ = "2023.11.06"


###########################
def parse_args(args):
    """
    Parse and validate command-line arguments for IAM role inventory operations.

    Configures the argument parser with IAM-specific options including role fragment
    filtering, deletion capabilities, and safety controls. Uses the standardized
    CommonArguments framework for consistency across inventory scripts.

    Args:
        args (list): Command-line arguments to parse (typically sys.argv[1:])

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: AWS profiles for multi-account access
            - Regions: Target AWS regions (IAM is global but needed for sessions)
            - Fragments: Role name fragments for filtering
            - pDelete: DANGEROUS flag enabling role deletion
            - Force: Skip confirmation prompts for automation
            - Exact: Use exact matching instead of substring matching
            - Other standard framework arguments

    Security Note:
        The pDelete parameter enables destructive operations that can impact
        AWS account security posture. Use with extreme caution.
    """
    parser = CommonArguments()
    parser.my_parser.description = (
        "We're going to find all roles within any of the accounts we have access to, given the profile(s) provided."
    )
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.fragment()
    parser.deletion()
    parser.rootOnly()
    parser.verbosity()
    parser.timing()
    parser.save_to_file()
    parser.version(__version__)
    parser.my_parser.add_argument(
        "+d",
        "+delete",
        dest="pDelete",
        action="store_const",
        const=True,
        default=False,
        help="Whether you'd like to delete that specified role.",
    )
    return parser.my_parser.parse_args(args)


def my_delete_role(fRoleList):
    """
    Execute comprehensive IAM role deletion with proper cleanup sequence.

    CRITICAL SECURITY OPERATION: This function performs IRREVERSIBLE deletion
    of IAM roles including all attached policies. Must follow AWS IAM deletion
    sequence: detach managed policies -> delete inline policies -> delete role.

    Args:
        fRoleList (dict): Role deletion context containing:
            - AccessKeyId, SecretAccessKey, SessionToken: AWS credentials
            - Region: AWS region for session establishment
            - RoleName: IAM role name to delete
            - AccountId: Target AWS account (for logging)

    Returns:
        bool: True if deletion successful, False if any step failed

    Deletion Sequence:
        1. Establish authenticated IAM session using provided credentials
        2. List and detach all AWS managed and customer-managed policies
        3. List and delete all inline policies attached to the role
        4. Delete the IAM role itself (only works after all policies removed)

    Error Handling:
        - ClientError: AWS API errors (permissions, throttling, dependencies)
        - Logs all errors for audit trail and troubleshooting
        - Returns False on any failure to prevent inconsistent state

    Security Implications:
        - Role deletion affects all services and resources using the role
        - Cannot be undone - permanent loss of role and policy associations
        - May break applications, services, or automation depending on role

    AWS IAM Constraints:
        - Cannot delete role with attached policies (managed or inline)
        - Cannot delete role if it has active sessions or is being assumed
        - Some AWS service-linked roles cannot be deleted
    """
    # Establish authenticated IAM session using provided credentials
    iam_session = boto3.Session(
        aws_access_key_id=fRoleList["AccessKeyId"],
        aws_secret_access_key=fRoleList["SecretAccessKey"],
        aws_session_token=fRoleList["SessionToken"],
        region_name=fRoleList["Region"],
    )
    iam_client = iam_session.client("iam")

    try:
        # Step 1: Detach all managed policies (AWS managed and customer managed)
        # These are policies attached via PolicyArn (not inline)
        attached_role_policies = iam_client.list_attached_role_policies(RoleName=fRoleList["RoleName"])[
            "AttachedPolicies"
        ]

        for _ in range(len(attached_role_policies)):
            response = iam_client.detach_role_policy(
                RoleName=fRoleList["RoleName"], PolicyArn=attached_role_policies[_]["PolicyArn"]
            )
            logging.info(f"Detached policy {attached_role_policies[_]['PolicyArn']} from role {fRoleList['RoleName']}")

        # Step 2: Delete all inline policies (policies embedded directly in the role)
        # These are policy documents stored as part of the role definition
        inline_role_policies = iam_client.list_role_policies(RoleName=fRoleList["RoleName"])["PolicyNames"]

        for _ in range(len(inline_role_policies)):
            response = iam_client.delete_role_policy(
                RoleName=fRoleList["RoleName"],
                PolicyName=inline_role_policies[_],  # Fixed: was accessing dict incorrectly
            )
            logging.info(f"Deleted inline policy {inline_role_policies[_]} from role {fRoleList['RoleName']}")

        # Step 3: Delete the IAM role itself (only works after all policies removed)
        response = iam_client.delete_role(RoleName=fRoleList["RoleName"])
        logging.warning(
            f"DELETED IAM role {fRoleList['RoleName']} from account {fRoleList.get('AccountId', 'unknown')}"
        )

        return True

    except ClientError as my_Error:
        # Log detailed error for troubleshooting and audit purposes
        logging.error(f"Failed to delete IAM role {fRoleList['RoleName']}: {my_Error}")

        # Common failure scenarios:
        # - Role has active sessions or is being assumed
        # - Role has instance profiles attached
        # - Permissions insufficient for deletion operations
        # - Role is service-linked and managed by AWS service

        return False


def find_and_collect_roles_across_accounts(fAllCredentials: list, frole_fragments: list) -> list:
    """
    Execute sequential IAM role discovery across multiple AWS accounts and regions.

    WARNING: This function processes accounts sequentially and should be enhanced
    with multi-threading for better performance in large AWS Organizations.

    Performs comprehensive IAM role inventory across all provided accounts,
    with optional fragment-based filtering for targeted role discovery.
    Handles AWS IAM API pagination and provides real-time progress feedback.

    Args:
        fAllCredentials (list): List of credential dictionaries containing:
            - AccessKeyId, SecretAccessKey, SessionToken: AWS credentials
            - Region: AWS region (IAM is global, but needed for session)
            - AccountNumber: AWS account ID for role attribution
            - MgmtAccount: Management account identifier
            - Success: Boolean indicating credential validation status

        frole_fragments (list): Optional role name fragments for filtering.
            If None, returns all roles. If provided, filters by fragment matching.

    Returns:
        list: Comprehensive list of IAM role dictionaries containing:
            - RoleName: IAM role name
            - AccountId: Source AWS account ID
            - MgmtAcct: Management account identifier
            - Region: AWS region (for session context)
            - AccessKeyId, SecretAccessKey, SessionToken: Credentials for operations

    Performance Considerations:
        - Sequential processing may be slow for large Organizations
        - IAM list_roles() API supports pagination for accounts with many roles
        - Real-time progress display shows per-account role counts

    Error Handling:
        - Skips accounts where credential validation failed
        - AuthFailure: Logs and continues with remaining accounts
        - ClientError: Handles AWS API errors gracefully
        - Pagination: Properly handles truncated IAM responses

    Filtering Logic:
        - If frole_fragments is None: Returns all discovered roles
        - If frole_fragments provided: Uses find_in() with exact/partial matching
        - Exact matching controlled by global pExact flag

    TODO: Implement multi-threading pattern similar to other inventory scripts
          for improved performance across large AWS Organizations.
    """
    print()
    if pFragments is None:
        print(f"Listing out all roles across {len(fAllCredentials)} accounts")
        print()
    elif pExact:
        print(
            f"Looking for a role {Fore.RED}exactly{Fore.RESET} named one of these strings {frole_fragments} across {len(fAllCredentials)} accounts"
        )
        print()
    else:
        print(
            f"Looking for a role containing one of these strings {frole_fragments} across {len(fAllCredentials)} accounts"
        )
        print()

    # Initialize role collection list for aggregating results across all accounts
    Roles = []

    # Sequential processing of each account (TODO: convert to multi-threading)
    for account in fAllCredentials:
        # Skip accounts where credential validation failed during setup
        if account["Success"]:
            # Establish authenticated IAM session for this account
            # Note: IAM is a global service but session requires region parameter
            iam_session = boto3.Session(
                aws_access_key_id=account["AccessKeyId"],
                aws_secret_access_key=account["SecretAccessKey"],
                aws_session_token=account["SessionToken"],
                region_name=account["Region"],  # Required for session, though IAM is global
            )
            iam_client = iam_session.client("iam")
        else:
            # Skip this account due to credential validation failure
            continue

        try:
            # Call AWS IAM API to list roles in this account
            # Default limit is 100 roles per call, pagination handled below
            response = iam_client.list_roles()

            # Process first page of roles
            for i in range(len(response["Roles"])):
                # Create standardized role record with metadata and credentials
                # Credentials included to enable subsequent operations (deletion, etc.)
                Roles.append(
                    {
                        # AWS credentials for role operations
                        "AccessKeyId": account["AccessKeyId"],
                        "SecretAccessKey": account["SecretAccessKey"],
                        "SessionToken": account["SessionToken"],
                        # Organizational and account context
                        "MgmtAcct": account["MgmtAccount"],
                        "Region": account["Region"],
                        "AccountId": account["AccountNumber"],
                        # IAM role metadata from AWS API response
                        "RoleName": response["Roles"][i]["RoleName"],
                    }
                )

            # Track role count for progress display
            num_of_roles_in_account = len(response["Roles"])

            # Handle AWS IAM API pagination for accounts with >100 roles
            # Enterprise accounts often have hundreds of roles requiring pagination
            while response["IsTruncated"]:
                # Get next page using pagination marker
                response = iam_client.list_roles(Marker=response["Marker"])

                # Process additional roles from paginated response
                for i in range(len(response["Roles"])):
                    Roles.append(
                        {
                            "AccessKeyId": account["AccessKeyId"],
                            "SecretAccessKey": account["SecretAccessKey"],
                            "SessionToken": account["SessionToken"],
                            "MgmtAcct": account["MgmtAccount"],
                            "Region": account["Region"],
                            "AccountId": account["AccountNumber"],
                            "RoleName": response["Roles"][i]["RoleName"],
                        }
                    )

                # Update role count (note: this shows last page count, not total)
                num_of_roles_in_account += len(response["Roles"])

            # Display real-time progress with role count per account
            print(f"Found {num_of_roles_in_account} roles in account {account['AccountNumber']}", end="\r")

        except ClientError as my_Error:
            # Handle AWS IAM API errors with appropriate logging
            if "AuthFailure" in str(my_Error):
                print(f"\nAuthorization Failure for account {account['AccountId']}")
                # Common causes: insufficient IAM permissions, account access issues
            else:
                print(f"\nError: {my_Error}")
                # Other potential errors: throttling, service unavailability, etc.

    # Apply role name filtering based on provided fragments
    if pFragments is None:
        # No filtering requested - return all discovered roles
        found_roles = Roles
    else:
        # Filter roles using fragment matching (exact or partial based on pExact flag)
        # find_in() handles both exact string matching and substring matching
        found_roles = [x for x in Roles if find_in([x["RoleName"]], pFragments, pExact)]

    return found_roles


def delete_roles(roles_to_delete):
    """
    Execute batch IAM role deletion with comprehensive safety controls.

    CRITICAL SECURITY FUNCTION: This orchestrates IRREVERSIBLE deletion of IAM roles
    across multiple AWS accounts. Implements multiple safety layers including
    confirmation prompts, force flags, and detailed audit logging.

    Args:
        roles_to_delete (list): List of role dictionaries to delete, each containing:
            - RoleName: IAM role name for deletion
            - AccountId: Target AWS account ID
            - Credential information for authenticated API calls

    Safety Control Flow:
        1. Fragment Validation: Refuses deletion if no role fragments specified
        2. Interactive Confirmation: Prompts user for explicit confirmation
        3. Force Mode: Automated confirmation with safety delay
        4. Individual Deletion: Calls my_delete_role() for each role
        5. Result Tracking: Updates role records with deletion status

    Security Features:
        - Prevents accidental bulk deletion without fragment specification
        - Interactive confirmation shows exact count and scope
        - Force mode includes mandatory delay allowing Ctrl-C abort
        - Per-role deletion status tracking for audit purposes
        - Comprehensive logging of all deletion attempts

    Deletion Modes:
        - Interactive Mode: User must confirm each batch deletion
        - Force Mode: Automated with {time_to_sleep} second safety delay
        - Dry Run: No deletion if pDelete flag not set

    Side Effects:
        - Modifies roles_to_delete list by adding 'Action' field
        - Logs all deletion attempts at INFO level
        - Displays progress and confirmation prompts to stdout

    Error Handling:
        - Individual role deletion failures are logged but don't stop batch
        - Failed deletions marked with "delete failed" status
        - Successful deletions marked with "deleted" status

    Enterprise Considerations:
        - Supports bulk operations across hundreds of roles
        - Maintains audit trail for compliance requirements
        - Provides abort mechanisms for operational safety
    """
    confirm = False

    if pDelete:
        # Safety Check #1: Prevent bulk deletion without specific targeting
        if pFragments is None:
            print(
                f"You asked to delete roles, but didn't give a specific role to delete, so we're not going to delete anything."
            )

        # Safety Check #2: Interactive confirmation for targeted deletions
        elif len(roles_to_delete) > 0 and not pForce:
            print(
                f"Your specified role fragment matched at least 1 role.\n"
                f"Please confirm you want to really delete all {len(roles_to_delete)} roles found"
            )
            confirm = (
                input(
                    f"Really delete {len(roles_to_delete)} across {len(AllCredentials)} accounts. Are you still sure? (y/n): "
                ).lower()
                == "y"
            )

        # Safety Check #3: Force mode with mandatory safety delay
        elif pForce and len(roles_to_delete) > 0:
            print(
                f"You specified a fragment that matched multiple roles.\n"
                f"And you specified the 'FORCE' parameter - so we're not asking again, BUT we'll wait {time_to_sleep} seconds to give you the option to Ctrl-C here..."
            )
            # Mandatory delay provides abort opportunity even in automation
            sleep(time_to_sleep)

    # Execute batch deletion if safety controls are satisfied
    if (pDelete and confirm) or (pDelete and pForce):
        for i in range(len(roles_to_delete)):
            # Log each deletion attempt for audit purposes
            logging.info(
                f"Deleting role {roles_to_delete[i]['RoleName']} from account {roles_to_delete[i]['AccountId']}"
            )

            # Attempt individual role deletion
            result = my_delete_role(roles_to_delete[i])

            # Update role record with deletion status for reporting
            if result:
                roles_to_delete[i].update({"Action": "deleted"})
            else:
                roles_to_delete[i].update({"Action": "delete failed"})


###########################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles
    pRegionList = args.Regions
    # pRole = args.pRole
    pFragments = args.Fragments
    pAccounts = args.Accounts
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pDelete = args.pDelete
    pForce = args.Force
    pExact = args.Exact
    pRootOnly = args.RootOnly
    pFilename = args.Filename
    pTiming = args.Time
    verbose = args.loglevel
    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    ERASE_LINE = "\x1b[2K"
    time_to_sleep = 5
    begin_time = time()

    print()

    # Get credentials for all Child Accounts
    AllCredentials = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList
    )
    # Collect the stacksets, AccountList and RegionList involved
    all_found_roles = find_and_collect_roles_across_accounts(AllCredentials, pFragments)
    # Display the information we've found this far
    sorted_Results = sorted(all_found_roles, key=lambda d: (d["MgmtAcct"], d["AccountId"], d["RoleName"]))
    display_dict = {
        "AccountId": {"DisplayOrder": 2, "Heading": "Account Number"},
        "MgmtAcct": {"DisplayOrder": 1, "Heading": "Parent Acct"},
        "RoleName": {"DisplayOrder": 3, "Heading": "Role Name"},
        "Action": {"DisplayOrder": 4, "Heading": "Action Taken"},
    }

    display_results(sorted_Results, display_dict, "No Action", pFilename)

    # Modify stacks, if requested
    if pDelete:
        delete_roles(sorted_Results)

    print()
    if pFragments is None:
        print(f"Found {len(sorted_Results)} roles across {len(AllCredentials)} accounts")
    else:
        print(
            f"Found {len(sorted_Results)} instances where role containing {pFragments} was found across {len(AllCredentials)} accounts"
        )

    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
    print()
    print("Thanks for using this script...")
    print()

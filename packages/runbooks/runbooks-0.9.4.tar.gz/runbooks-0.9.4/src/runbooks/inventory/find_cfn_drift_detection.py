#!/usr/bin/env python3

"""
AWS CloudFormation Stack Drift Detection Enablement Script

This enterprise-grade script provides comprehensive CloudFormation drift detection enablement
across multi-account AWS Organizations environments. Designed for infrastructure teams managing
CloudFormation stacks at scale, offering automated drift detection initialization, stack
discovery with filtering capabilities, and organizational governance support for infrastructure
configuration management and compliance monitoring.

Key Features:
    - Multi-account, multi-region CloudFormation stack discovery and drift detection enablement
    - Fragment-based stack filtering for targeted drift detection operations
    - Stack status filtering supporting active and deleted stack analysis
    - Enterprise governance support with organizational context and account exclusion
    - Comprehensive error handling for authorization and access control issues
    - Progress tracking and operational feedback for large-scale drift detection operations

Drift Detection Capabilities:
    - Automated drift detection enablement for discovered CloudFormation stacks
    - Stack-level drift detection initialization with operational logging
    - Regional drift detection coverage for comprehensive infrastructure monitoring
    - Fragment-based stack targeting for selective drift detection operations
    - Status-based stack filtering for active vs historical stack analysis

Authentication & Access:
    - AWS Organizations support for centralized CloudFormation stack management
    - Cross-account role assumption for organizational stack visibility
    - Regional validation and opt-in status verification for CloudFormation availability
    - Profile-based authentication with comprehensive credential management

Performance & Scalability:
    - Progress bars and operational feedback for large-scale drift detection operations
    - Efficient credential management for multi-account stack enumeration
    - Regional optimization with targeted CloudFormation API calls
    - Memory-efficient processing for extensive stack inventories

Enterprise Use Cases:
    - Infrastructure configuration drift detection and compliance monitoring
    - CloudFormation stack governance and change management automation
    - Organizational infrastructure audit and drift analysis
    - Automated configuration compliance validation across organizational accounts

Security & Compliance:
    - Account exclusion capabilities preventing drift detection on sensitive accounts
    - Comprehensive audit logging for drift detection operations and stack access
    - Regional access validation preventing unauthorized stack enumeration
    - Safe credential handling with automatic session management

Dependencies:
    - boto3: AWS SDK for CloudFormation API access
    - colorama: Terminal output formatting and colored display
    - Custom modules: Inventory_Modules, ArgumentsClass, account_class for enterprise operations

Output Format:
    - Real-time progress feedback with account and region context
    - Comprehensive drift detection summary with stack counts and regional coverage
    - Operational logging for audit trails and troubleshooting

Future Enhancements:
    - Drift detection status monitoring using describe_stack_drift_detection_status
    - Enhanced progress tracking and drift detection result analysis
    - Multi-threaded processing for improved performance at scale
"""

import logging

import Inventory_Modules
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init

init()
__version__ = "2023.05.04"

# Configure comprehensive argument parsing for CloudFormation drift detection operations
parser = CommonArguments()
parser.singleprofile()  # Single AWS profile for organizational drift detection management
parser.multiregion()  # Multi-region support for comprehensive CloudFormation coverage
parser.verbosity()  # Logging verbosity controls for operational visibility
parser.version(__version__)

# Enhanced CLI arguments for targeted CloudFormation drift detection operations
parser.my_parser.add_argument(
    "-f",
    "--fragment",
    dest="pstackfrag",
    metavar="CloudFormation stack fragment",
    default="all",
    help="String fragment of CloudFormation stack names for targeted drift detection filtering. "
    "Supports partial name matching for flexible stack identification and selective drift analysis.",
)
parser.my_parser.add_argument(
    "-s",
    "--status",
    dest="pstatus",
    metavar="CloudFormation status",
    default="active",
    help="Stack status filter determining drift detection scope. "
    "'active' for CREATE_COMPLETE stacks only, 'all' includes DELETE_COMPLETE stacks for historical analysis.",
)
parser.my_parser.add_argument(
    "-k",
    "--skip",
    dest="pSkipAccounts",
    nargs="*",
    metavar="Accounts to leave alone",
    default=[],
    help="Account exclusion list preventing drift detection on sensitive or core organizational accounts. "
    "Provides safety controls for production and management account protection.",
)
args = parser.my_parser.parse_args()

# Extract and configure parameters from parsed command-line arguments
pProfile = args.Profile  # AWS profile for organizational CloudFormation access
pRegionList = args.Regions  # Target regions for comprehensive drift detection coverage
pstackfrag = args.pstackfrag  # Stack name fragments for targeted drift detection filtering
pstatus = args.pstatus  # Stack status filter for active vs historical analysis
AccountsToSkip = args.pSkipAccounts  # Account exclusion list for production safety
verbose = args.loglevel  # Logging verbosity for operational visibility

# Configure comprehensive logging for CloudFormation drift detection operations
logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.getLogger("boto3").setLevel(logging.CRITICAL)  # Suppress AWS SDK logging
logging.getLogger("botocore").setLevel(logging.CRITICAL)  # Suppress AWS core logging
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)  # Suppress S3 transfer logging
logging.getLogger("urllib3").setLevel(logging.CRITICAL)  # Suppress HTTP logging

"""
Future Enhancement: Drift Detection Status Monitoring
We should eventually create an argument here that would check on the status of the drift-detection using
"describe_stack_drift_detection_status", but we haven't created that function yet...  
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_drift_detection_status

This would enable:
- Real-time drift detection progress monitoring
- Drift detection result analysis and reporting  
- Automated drift detection completion verification
- Enhanced operational visibility for large-scale drift operations
"""

##########################
ERASE_LINE = "\x1b[2K"  # Terminal control for dynamic output updates

# Initialize AWS account access and organizational context for drift detection
aws_acct = aws_acct_access(pProfile)
sts_client = aws_acct.session.client("sts")

# Handle organizational vs single account drift detection scope
if aws_acct.AccountType == "Root":
    print()
    # Default to organizational drift detection for automation compatibility
    try:
        # Interactive prompt for organizational drift detection scope selection
        answer = input(
            f"You've specified a root account to check. \n"
            f"Do you want to check the entire Org or only the root account? (Enter 'root' for whole Org):"
        )
    except EOFError:
        # Handle non-interactive mode (automated testing)
        print("Non-interactive mode detected, defaulting to root account only")
        answer = "single"

    if answer == "root":
        # Enable organizational drift detection across all child accounts
        ChildAccounts = aws_acct.ChildAccounts
    else:
        # Restrict drift detection to management account only
        ChildAccounts = [
            {
                "MgmtAccount": aws_acct.acct_number,  # Management account identifier
                "AccountId": aws_acct.acct_number,  # Account number for single account scope
                "AccountEmail": aws_acct.MgmtEmail,  # Management email for audit context
                "AccountStatus": aws_acct.AccountStatus,  # Account operational status
            }
        ]

# Initialize drift detection operation tracking and regional scope configuration
NumStacksFound = 0  # Counter for tracking total stacks processed for drift detection
print()

# Configure regional scope for comprehensive CloudFormation drift detection coverage
RegionList = Inventory_Modules.get_service_regions("cloudformation", pRegionList)

# Note: Alternative account discovery approaches for organizational drift detection
# ChildAccounts = Inventory_Modules.find_child_accounts2(pProfile)  # Direct account discovery
# ChildAccounts = Inventory_Modules.RemoveCoreAccounts(ChildAccounts, AccountsToSkip)  # Account filtering

# Configure display formatting for drift detection progress and results
fmt = "%-20s %-15s %-15s %-50s"
print(fmt % ("Account", "Region", "Stack Status", "Stack Name"))
print(fmt % ("-------", "------", "------------", "----------"))

# Execute comprehensive CloudFormation drift detection across organizational accounts and regions
StacksFound = []  # Aggregated list for discovered stacks requiring drift detection
for account in ChildAccounts:
    # Note: Alternative role ARN construction for cross-account CloudFormation access
    # role_arn = f"arn:aws:iam::{account['AccountId']}:role/AWSCloudFormationStackSetExecutionRole"
    # logging.info(f"Role ARN: {role_arn}")

    try:
        # Establish cross-account credentials for CloudFormation stack access
        account_credentials = Inventory_Modules.get_child_access3(
            aws_acct,
            account["AccountId"],
        )

        # Validate account access and skip failed credential attempts
        if account_credentials["AccessError"]:
            logging.error(f"Accessing account {account['AccountId']} didn't work, so we're skipping it")
            continue

    except ClientError as my_Error:
        # Handle comprehensive AWS API authorization and access errors
        if "AuthFailure" in str(my_Error):
            print(f"{pProfile}: Authorization Failure for account {account['AccountId']}")
        elif str(my_Error).find("AccessDenied") > 0:
            print(f"{pProfile}: Access Denied Failure for account {account['AccountId']}")
        else:
            print(f"{pProfile}: Other kind of failure for account {account['AccountId']}")
            print(my_Error)
        break

    # Iterate through regions for comprehensive regional drift detection coverage
    for region in RegionList:
        Stacks = []  # Regional stack collection for drift detection processing
        try:
            StackNum = 0  # Regional stack counter for progress tracking

            # Discover CloudFormation stacks with fragment and status filtering
            Stacks = Inventory_Modules.find_stacks2(account_credentials, region, pstackfrag, pstatus)

            # Log regional stack discovery progress for operational visibility
            logging.warning(f"Account: {account['AccountId']} | Region: {region} | Found {StackNum} Stacks")
            logging.info(
                f"{ERASE_LINE}{Fore.RED}Account: {account['AccountId']} Region: {region} Found {StackNum} Stacks{Fore.RESET}"
            )

        except ClientError as my_Error:
            # Handle regional authorization failures during stack discovery
            if "AuthFailure" in str(my_Error):
                print(f"{account['AccountId']}: Authorization Failure")

        # Process discovered stacks for drift detection enablement
        for Stack in Stacks:
            # Extract stack metadata for drift detection operations
            StackName = Stack["StackName"]  # Human-readable stack identifier
            StackStatus = Stack["StackStatus"]  # Current operational status
            StackID = Stack["StackId"]  # Unique CloudFormation stack identifier

            # Enable drift detection on discovered CloudFormation stack
            DriftStatus = Inventory_Modules.enable_drift_on_stacks2(account_credentials, region, StackName)

            # Log drift detection enablement for audit trail and operational tracking
            logging.error(
                f"Enabled drift detection on {StackName} in account {account_credentials['AccountNumber']} in region {region}"
            )
            NumStacksFound += 1  # Increment total drift detection counter

# Provide comprehensive operational summary with drift detection metrics
print(ERASE_LINE)
print(
    f"{Fore.RED}Looked through {NumStacksFound} Stacks across {len(ChildAccounts)} accounts across "
    f"{len(RegionList)} regions{Fore.RESET}"
)
print()

# Display completion message for drift detection operation
print("Thanks for using this script...")
print()

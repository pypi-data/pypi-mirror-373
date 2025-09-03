#!/usr/bin/env python3

"""
AWS IAM Policies Discovery and Action Analysis Script

This script provides comprehensive discovery and analysis capabilities for AWS Identity
and Access Management (IAM) policies across multiple accounts and regions. It's designed
for enterprise security and compliance teams who need visibility into policy distribution,
permission analysis, and action-specific security assessment across large-scale AWS deployments.

Key Features:
- Multi-account IAM policy discovery using assume role capabilities
- Policy action analysis for permission tracking and security assessment
- Customer-managed policy filtering for organizational policy governance
- Fragment-based search for targeted policy discovery and analysis
- Enterprise reporting with CSV export and structured output
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- Security policy audit and compliance reporting across organizations
- Permission analysis for least privilege access implementation
- Policy governance and standardization across organizational boundaries
- Security incident response with policy and permission analysis
- Compliance reporting for access control and authorization standards
- Multi-account IAM governance and policy lifecycle management
- Risk assessment through policy action enumeration and analysis

IAM Policy Analysis Features:
- Comprehensive policy enumeration with metadata extraction
- Policy action discovery for permission tracking and analysis
- Customer-managed policy identification for organizational governance
- Cross-account policy consistency analysis and standardization
- Policy fragment search for targeted security assessment
- Permission correlation across organizational boundaries

Security Considerations:
- Uses IAM assume role capabilities for cross-account policy access
- Implements proper error handling for authorization failures
- Supports read-only operations with no policy modification capabilities
- Respects IAM service permissions and regional access constraints
- Provides comprehensive audit trail through detailed logging
- Sensitive permission information handling with appropriate access controls

Policy Governance Features:
- Customer-managed policy filtering for organizational policy oversight
- Policy action enumeration for security and compliance analysis
- Cross-account policy visibility for governance and standardization
- Fragment-based search for targeted policy discovery and assessment
- Policy lifecycle tracking for governance and compliance management

Performance Considerations:
- Multi-threaded processing for concurrent IAM API operations
- Progress tracking for operational visibility during large-scale operations
- Efficient credential management for cross-account policy access
- Memory-optimized data structures for large policy inventories
- Queue-based worker architecture for scalable policy discovery

Threading Architecture:
- Worker thread pool with configurable concurrency for policy action analysis
- Queue-based task distribution for efficient policy processing
- Thread-safe error handling and progress tracking
- Graceful degradation for account access failures

Dependencies:
- boto3/botocore for AWS IAM API interactions
- Inventory_Modules for common utility functions and credential management
- ArgumentsClass for standardized CLI argument parsing
- threading and queue for concurrent processing architecture
- colorama for enhanced output formatting

Compliance and Audit Features:
- Comprehensive policy discovery for security auditing
- Action-specific permission analysis for compliance validation
- Cross-account policy governance for organizational security
- Customer-managed policy tracking for organizational oversight
- Fragment-based search for targeted compliance assessment

Future Enhancements:
- Policy risk assessment with privilege escalation detection
- Automated policy compliance checking against security standards
- Integration with AWS Config for policy configuration drift detection
- Policy optimization recommendations for least privilege implementation

Author: AWS CloudOps Team
Version: 2023.12.12
"""

# import boto3
import logging
import sys
from queue import Queue
from threading import Thread
from time import time

from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_account_policies2, find_policy_action2, get_all_credentials

init()
__version__ = "2023.12.12"
ERASE_LINE = "\x1b[2K"
begin_time = time()


##################
def parse_args(args):
    """
    Parse command line arguments for AWS IAM policy discovery and action analysis operations.

    Configures comprehensive argument parsing for multi-account, multi-region IAM policy
    inventory operations. Supports enterprise security and compliance management with profile
    management, region targeting, organizational access controls, fragment-based search,
    and policy action analysis for permission tracking and security assessment.

    Args:
        args (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: List of AWS profiles to process
            - Regions: Target regions for IAM policy discovery
            - SkipProfiles/SkipAccounts: Exclusion filters
            - RootOnly: Limit to organization root accounts
            - Fragments: Policy name fragments for targeted search
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration
            - paction: Specific policy actions to analyze
            - pcmp: Filter for customer-managed policies only
            - Exact: Enable exact fragment matching

    Configuration Options:
        - Multi-region scanning with region filters for targeted policy analysis
        - Multi-profile support for federated access across security infrastructure
        - Extended arguments for advanced filtering and account selection
        - Root-only mode for organization-level policy inventory
        - Fragment search for finding specific policies by name patterns
        - File output for integration with security management tools
        - Timing metrics for performance optimization and monitoring
        - Verbose logging for debugging and security audit

    IAM-Specific Features:
        - Policy action analysis for permission tracking and security assessment
        - Customer-managed policy filtering for organizational governance
        - Fragment-based search for targeted security policy discovery
        - Support for compliance analysis and policy governance workflows

    Security Analysis Options:
        - Specific action enumeration for permission analysis
        - Customer-managed policy focus for organizational security oversight
        - Cross-account policy visibility for governance and standardization
        - Exact matching for precise policy identification and analysis
    """
    parser = CommonArguments()
    parser.my_parser.description = "Discover and analyze AWS IAM policies and actions across multiple accounts and regions for enterprise security governance and compliance management."
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rootOnly()
    parser.fragment()
    parser.timing()
    parser.save_to_file()
    parser.verbosity()
    parser.version(__version__)
    parser.my_parser.add_argument(
        "--action",
        dest="paction",
        nargs="*",
        metavar="AWS Action",
        default=None,
        help="Specific AWS actions to search for within policy documents - supports multiple actions for comprehensive permission analysis",
    )
    parser.my_parser.add_argument(
        "--cmp",
        "--customer_managed_policies",
        dest="pcmp",
        action="store_true",
        help="Filter results to show only customer-managed policies for organizational governance and policy oversight",
    )
    return parser.my_parser.parse_args(args)


def check_accounts_for_policies(CredentialList, fRegionList=None, fActions=None, fFragments=None):
    """
    Discover and analyze AWS IAM policies across multiple accounts with optional action analysis.

    Performs comprehensive IAM policy discovery using multi-threaded processing to efficiently
    inventory policies across enterprise AWS environments. Supports fragment-based filtering
    for targeted discovery and action analysis for permission tracking and security assessment.

    Args:
        CredentialList (list): List of credential dictionaries for cross-account access containing:
            - AccountId: AWS account number
            - Region: Target AWS region
            - Success: Boolean indicating credential validity
            - MgmtAccount: Management account identifier
            - ParentProfile: Source AWS profile
        fRegionList (list, optional): Target regions for policy discovery (defaults to us-east-1)
        fActions (list, optional): Specific AWS actions to search for within policy documents
        fFragments (list, optional): Policy name fragments for targeted search and filtering

    Returns:
        list: Comprehensive list of policy dictionaries containing:
            - MgmtAccount: Management account identifier for organizational hierarchy
            - AccountNumber: AWS account containing the policy
            - Region: AWS region where policy is managed
            - PolicyName: IAM policy name identifier
            - PolicyArn: Unique policy Amazon Resource Name
            - Action: Specific actions found (if action analysis enabled)
            - Document: Policy document content for analysis

    Threading Architecture:
        - Worker thread pool with configurable concurrency for policy action analysis
        - Queue-based task distribution for efficient policy processing
        - Thread-safe error handling and progress tracking
        - Graceful degradation for account access failures and authorization issues

    Enterprise Features:
        - Cross-account policy discovery with assume role capabilities
        - Fragment-based search for targeted policy identification
        - Action analysis for permission tracking and security assessment
        - Comprehensive error handling for authorization and throttling scenarios

    Security Analysis:
        - Policy action enumeration for permission analysis
        - Customer-managed policy filtering for organizational governance
        - Cross-account policy visibility for security governance
        - Fragment-based search for targeted compliance assessment

    Error Handling:
        - Authorization failure detection with appropriate logging
        - AWS API throttling management with graceful degradation
        - Thread-safe error reporting and progress updates
        - Graceful handling of missing policies and empty responses

    Performance Considerations:
        - Dynamic thread pool sizing based on policy count and credential set
        - Efficient memory management for large policy inventories
        - Progress tracking for operational visibility during discovery
        - Policy metadata extraction for enterprise security management
    """

    # Worker thread class for concurrent policy action analysis
    class FindActions(Thread):
        def __init__(self, queue):
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            while True:
                # Get the work from the queue and expand the tuple
                c_account_credentials, c_policy, c_action, c_PlacesToLook, c_PlaceCount = self.queue.get()
                logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
                try:
                    logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")

                    # Analyze specific policy for the requested action using inventory module
                    policy_actions = find_policy_action2(c_account_credentials, c_policy, c_action)
                    logging.info(
                        f"Successfully connected to account {c_account_credentials['AccountId']} for policy {c_policy['PolicyName']}"
                    )

                    # Aggregate discovered policy actions for enterprise security analysis
                    if len(policy_actions) > 0:
                        AllPolicies.extend(policy_actions)

                except KeyError as my_Error:
                    # Handle cases where expected keys are missing from IAM API responses
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    # Handle cases where profile configuration is incorrect
                    logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
                    logging.warning(my_Error)
                    continue
                finally:
                    # Provide progress tracking for operational visibility and ensure queue management
                    print(
                        f"{ERASE_LINE}Finished finding policy actions in account {c_account_credentials['AccountId']} - {c_PlaceCount} / {c_PlacesToLook}",
                        end="\r",
                    )
                    self.queue.task_done()

    if fRegionList is None:
        fRegionList = ["us-east-1"]
    if fFragments is None:
        fFragments = []
    checkqueue = Queue()

    AllPolicies = []
    AccountCount = 0
    Policies = []
    PolicyCount = 0

    print()
    for credential in CredentialList:
        try:
            logging.info(f"Connecting to account {credential['AccountId']}")
            Policies = find_account_policies2(credential, fRegionList[0], fFragments, pExact, pCMP)
            AccountCount += 1
            if fActions is None:
                PlacesToLook = len(Policies)
            else:
                PlacesToLook = len(Policies) * len(fActions)
            print(
                f"{ERASE_LINE}Found {PlacesToLook} matching policies in account {credential['AccountId']} ({AccountCount}/{len(CredentialList)})",
                end="\r",
            )
            # print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
            if fActions is None:
                AllPolicies.extend(Policies)
            else:
                for policy in Policies:
                    PolicyCount += 1
                    for action in fActions:
                        checkqueue.put((credential, policy, action, PlacesToLook, PolicyCount))
        except ClientError as my_Error:
            if "AuthFailure" in str(my_Error):
                logging.error(f"Authorization Failure accessing account {credential['AccountId']}")
                pass

    # WorkerThreads = min(len(Policies) * len(fAction), 250)
    WorkerThreads = min(round(len(AllPolicies) / len(CredentialList)), 200)

    for x in range(WorkerThreads):
        worker = FindActions(checkqueue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    checkqueue.join()
    return AllPolicies


##################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    pProfiles = args.Profiles
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pAccounts = args.Accounts
    pFragments = args.Fragments
    pRootOnly = args.RootOnly
    pActions = args.paction
    pCMP = args.pcmp
    pExact = args.Exact
    pTiming = args.Time
    pFilename = args.Filename
    verbose = args.loglevel
    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    logging.info(f"Profiles: {pProfiles}")

    print()
    print(f"Checking for matching Policies... ")
    print()

    PoliciesFound = []
    AllChildAccounts = []
    # TODO: Will have to be changed to support single region-only accounts, but that's a ways off yet.
    pRegionList = RegionList = ["us-east-1"]

    # Get credentials for all Child Accounts
    AllCredentials = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList
    )
    # Find all the policies
    PoliciesFound.extend(check_accounts_for_policies(AllCredentials, RegionList, pActions, pFragments))
    # Display the information we've found this far
    sorted_policies = sorted(
        PoliciesFound, key=lambda x: (x["MgmtAccount"], x["AccountNumber"], x["Region"], x["PolicyName"])
    )

    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
        "AccountNumber": {"DisplayOrder": 2, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 3, "Heading": "Region"},
        "PolicyName": {"DisplayOrder": 4, "Heading": "Policy Name"},
        "Action": {"DisplayOrder": 5, "Heading": "Action"},
    }

    display_results(sorted_policies, display_dict, pActions, pFilename)

    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
    print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else print()
    print()
    print(
        f"Found {len(PoliciesFound)} policies across {len(AllCredentials)} accounts across {len(RegionList)} regions\n"
        f"	that matched the fragment{'s' if len(pFragments) > 1 else ''} that you specified: {pFragments}"
    )
    print()
    print("Thank you for using this script")
    print()

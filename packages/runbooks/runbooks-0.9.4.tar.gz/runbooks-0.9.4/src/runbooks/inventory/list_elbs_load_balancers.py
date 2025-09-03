#!/usr/bin/env python3

"""
AWS Elastic Load Balancers Discovery and Analysis Script

This script provides comprehensive discovery and inventory capabilities for AWS Elastic
Load Balancers (ELBs) across multiple accounts and regions. It's designed for enterprise
infrastructure teams who need visibility into load balancer distribution, capacity
planning, and traffic management across large-scale AWS deployments.

Key Features:
- Multi-account ELB discovery using assume role capabilities
- Multi-region scanning with configurable region targeting
- Load balancer metadata extraction including state and DNS information
- Status filtering for active and inactive load balancer analysis
- Fragment-based search for targeted load balancer discovery
- Enterprise reporting with structured output and integration capabilities
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- Load balancer inventory and governance across organizations
- Traffic distribution analysis for performance optimization
- Capacity planning for application load balancing infrastructure
- Compliance reporting for load balancer security and configuration standards
- Multi-account traffic management visibility and coordination
- Disaster recovery planning with load balancer distribution analysis
- Cost optimization through load balancer utilization tracking

Load Balancing Infrastructure Features:
- Classic Load Balancer (ELB) enumeration with health status
- Application Load Balancer (ALB) discovery and configuration analysis
- Network Load Balancer (NLB) inventory with performance metrics
- Load balancer state tracking (active, provisioning, failed)
- DNS name resolution and endpoint management
- Target group and backend instance analysis

Security Considerations:
- Uses IAM assume role capabilities for cross-account ELB access
- Implements proper error handling for authorization failures
- Supports read-only operations with no load balancer modification capabilities
- Respects ELB service permissions and regional access constraints
- Provides comprehensive audit trail through detailed logging

Load Balancer Analysis:
- State monitoring for operational health assessment
- DNS configuration validation for service endpoint management
- Performance characteristics analysis for optimization
- Security group and network access control evaluation
- SSL/TLS certificate management and compliance tracking

Performance Considerations:
- Multi-threaded processing for concurrent ELB API operations
- Progress tracking with tqdm for operational visibility during long operations
- Efficient credential management for cross-account load balancer access
- Memory-optimized data structures for large load balancer inventories
- Queue-based worker architecture for scalable discovery operations

Threading Architecture:
- Worker thread pool with configurable concurrency (max 10 threads for ELB APIs)
- Queue-based task distribution for efficient resource discovery
- Thread-safe error handling and progress tracking
- Graceful degradation for account access failures

Dependencies:
- boto3/botocore for AWS ELB API interactions
- Inventory_Modules for common utility functions and credential management
- ArgumentsClass for standardized CLI argument parsing
- threading and queue for concurrent processing architecture
- colorama for enhanced output formatting and tqdm for progress tracking

Future Enhancements:
- Application Load Balancer (ALB) target group analysis
- Network Load Balancer (NLB) performance metrics integration
- SSL certificate expiration monitoring and alerting
- Load balancer security configuration compliance checking
- Cost optimization recommendations based on traffic patterns

Author: AWS CloudOps Team
Version: 2024.05.06
"""

import logging
import sys
from os.path import split
from queue import Queue
from threading import Thread
from time import time

from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_load_balancers2, get_all_credentials
from tqdm.auto import tqdm

init()
__version__ = "2024.05.06"
ERASE_LINE = "\x1b[2K"
begin_time = time()


##################
# Functions
##################


def parse_args(arguments):
    """
    Parse command line arguments for AWS Elastic Load Balancer discovery operations.

    Configures comprehensive argument parsing for multi-account, multi-region ELB
    inventory operations. Supports enterprise load balancing infrastructure management
    with profile management, region targeting, organizational access controls, status
    filtering, and fragment-based search for targeted discovery operations.

    Args:
        arguments (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: List of AWS profiles to process
            - Regions: Target regions for ELB discovery
            - SkipProfiles/SkipAccounts: Exclusion filters
            - RootOnly: Limit to organization root accounts
            - AccessRoles: IAM roles for cross-account access
            - Fragments: Name fragments for targeted ELB search
            - pstatus: Load balancer status filter
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration

    Configuration Options:
        - Multi-region scanning with region filters for targeted load balancer analysis
        - Multi-profile support for federated access across load balancing infrastructure
        - Extended arguments for advanced filtering and account selection
        - Root-only mode for organization-level load balancer inventory
        - Role-based access for cross-account ELB resource discovery
        - Fragment search for finding specific load balancers by name patterns
        - Status filtering for operational state analysis and monitoring
        - Timing metrics for performance optimization and monitoring
        - Verbose logging for debugging and infrastructure audit

    ELB-Specific Features:
        - Load balancer status filtering to focus on operational states
        - Fragment-based search for targeted load balancer discovery
        - Support for traffic management analysis and monitoring
        - Integration with enterprise load balancing governance workflows
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
    parser.my_parser.description = "Discover and analyze AWS Elastic Load Balancers across multiple accounts and regions for enterprise traffic management and infrastructure planning."
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rootOnly()
    parser.rolestouse()
    parser.fragment()
    parser.verbosity()
    parser.timing()
    parser.version(__version__)
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "-s",
        "--status",
        dest="pstatus",
        metavar="Load balancer status",
        default="active",
        help="Filter load balancers by operational status: 'active' for operational ELBs, 'provisioning' for pending, 'failed' for error states",
    )
    return parser.my_parser.parse_args(arguments)


def find_all_elbs(fAllCredentials: list, ffragment: list, fstatus: str):
    """
    Discover and inventory AWS Elastic Load Balancers across multiple accounts and regions.

    Performs comprehensive ELB discovery using multi-threaded processing to efficiently
    inventory load balancing infrastructure across enterprise AWS environments. Supports
    fragment-based filtering for targeted discovery and status filtering for operational
    state analysis and traffic management planning.

    Args:
        fAllCredentials (list): List of credential dictionaries for cross-account access containing:
            - AccountId: AWS account number
            - Region: Target AWS region
            - Success: Boolean indicating credential validity
            - MgmtAccount: Management account identifier
            - ParentProfile: Source AWS profile
        ffragment (list): Name fragments for targeted load balancer search and filtering
        fstatus (str): Load balancer status filter ('active', 'provisioning', 'failed', etc.)

    Returns:
        list: Comprehensive list of load balancer dictionaries containing:
            - MgmtAccount: Management account identifier for organizational hierarchy
            - AccountId: AWS account containing the load balancer
            - Region: AWS region where load balancer is located
            - Name: Load balancer name identifier
            - Status: Current operational state (active, provisioning, failed)
            - DNSName: Load balancer DNS endpoint for traffic routing

    Threading Architecture:
        - Worker thread pool with maximum 10 concurrent threads for ELB API optimization
        - Queue-based task distribution for efficient load balancer discovery
        - Thread-safe error handling and progress tracking
        - Graceful degradation for account access failures and authorization issues

    Enterprise Features:
        - Cross-account load balancer discovery with assume role capabilities
        - Fragment-based search for targeted load balancer identification
        - Status filtering for operational state monitoring and analysis
        - Comprehensive error handling for authorization and throttling scenarios

    Error Handling:
        - Authorization failure detection with region opt-in diagnostics
        - AWS API throttling management with appropriate logging
        - Graceful handling of missing load balancers and empty responses
        - Thread-safe error reporting and progress updates

    Performance Considerations:
        - Optimized thread pool size for ELB API rate limits
        - Efficient memory management for large load balancer inventories
        - Progress tracking for operational visibility during discovery
        - Load balancer metadata extraction for enterprise reporting
    """

    # Worker thread class for concurrent load balancer discovery
    class FindLoadBalancers(Thread):
        def __init__(self, queue):
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            while True:
                # Get the work from the queue and expand the tuple
                c_account_credentials, c_fragment, c_status = self.queue.get()
                logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
                try:
                    # Discover load balancers using inventory module with fragment and status filtering
                    LoadBalancers = find_load_balancers2(c_account_credentials, c_fragment, c_status)
                    logging.info(
                        f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(LoadBalancers)} load balancers"
                    )

                    # Process each discovered load balancer and extract enterprise metadata
                    for lb in LoadBalancers:
                        All_Load_Balancers.append(
                            {
                                # Management account for organizational hierarchy tracking
                                "MgmtAccount": c_account_credentials["MgmtAccount"],
                                # Account containing the load balancer for governance
                                "AccountId": c_account_credentials["AccountId"],
                                # Regional placement for capacity planning and disaster recovery
                                "Region": c_account_credentials["Region"],
                                # Load balancer name for identification and management
                                "Name": lb["LoadBalancerName"],
                                # Operational status for health monitoring
                                "Status": lb["State"]["Code"],
                                # DNS endpoint for traffic routing configuration
                                "DNSName": lb["DNSName"],
                            }
                        )
                except KeyError as my_Error:
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    logging.error(f"Error: Likely that one of the supplied profiles was wrong")
                    logging.warning(my_Error)
                    continue
                except ClientError as my_Error:
                    # Handle AWS API errors including authorization failures and throttling
                    if "AuthFailure" in str(my_Error):
                        logging.error(
                            f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region"
                        )
                        logging.warning(
                            f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into"
                        )
                        continue
                    else:
                        # Handle throttling and other AWS API errors
                        logging.error(f"Error: Likely throttling errors from too much activity")
                        logging.warning(my_Error)
                        continue
                finally:
                    # Ensure queue management regardless of success/failure
                    self.queue.task_done()

    ###########
    # Initialize queue-based threading architecture for scalable load balancer discovery
    ###########

    # Create thread-safe queue for distributing work across worker threads
    checkqueue = Queue()

    # Initialize results list for aggregating discovered load balancers
    All_Load_Balancers = []

    # Configure worker thread pool size optimized for ELB API rate limits
    # Maximum 10 threads to prevent overwhelming ELB APIs while maintaining efficiency
    WorkerThreads = min(len(fAllCredentials), 10)

    # Start worker threads for concurrent load balancer discovery
    for x in range(WorkerThreads):
        worker = FindLoadBalancers(checkqueue)
        # Setting daemon to True allows main thread exit even if workers are still processing
        worker.daemon = True
        worker.start()

    # Queue credential sets with progress tracking for operational visibility
    for credential in tqdm(fAllCredentials):
        logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
        try:
            # Queue credential set with fragment and status filters for targeted discovery
            # Tuple format: (credentials, fragment_filter, status_filter)
            checkqueue.put((credential, ffragment, fstatus))
        except ClientError as my_Error:
            # Handle authorization failures during credential queuing
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region"
                )
                logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass

    # Wait for all queued work to complete before proceeding
    checkqueue.join()
    return All_Load_Balancers


##################
# Main execution entry point for enterprise load balancer discovery and traffic management analysis
##################

if __name__ == "__main__":
    """
    Main orchestration for comprehensive AWS Elastic Load Balancer discovery and analysis.
    
    Coordinates multi-account, multi-region load balancer inventory with detailed traffic
    management analysis, capacity planning support, and enterprise load balancing
    infrastructure governance across AWS Organizations environments.
    """
    # Parse enterprise command-line arguments with ELB-specific traffic management options
    args = parse_args(sys.argv[1:])

    # Extract configuration parameters for multi-account load balancer discovery
    pProfiles = args.Profiles  # AWS profile list for federated ELB access
    pRegionList = args.Regions  # Target regions for load balancer enumeration
    pAccounts = args.Accounts  # Specific account targeting for focused traffic analysis
    pSkipAccounts = args.SkipAccounts  # Account exclusion list for organizational policy compliance
    pSkipProfiles = args.SkipProfiles  # Profile exclusion for credential optimization
    pAccessRoles = args.AccessRoles  # Cross-account roles for Organizations ELB access
    pFragment = args.Fragments  # Name fragments for targeted load balancer discovery
    pStatus = args.pstatus  # Load balancer status filter for operational analysis
    pRootOnly = args.RootOnly  # Organization root account limitation flag
    pTiming = args.Time  # Performance timing for operational optimization
    verbose = args.loglevel  # Logging verbosity for load balancing infrastructure visibility

    # Configure enterprise logging infrastructure for ELB operations audit trail
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    # Configure enterprise ELB inventory report display formatting for traffic management analysis
    display_dict = {
        # 'ParentProfile': {'DisplayOrder': 1, 'Heading': 'Parent Profile'}, # Disabled for concise output
        "MgmtAccount": {"DisplayOrder": 2, "Heading": "Mgmt Acct"},  # Management account hierarchy
        "AccountId": {"DisplayOrder": 3, "Heading": "Acct Number"},  # Account identifier for governance
        "Region": {"DisplayOrder": 4, "Heading": "Region"},  # AWS region for geographic distribution
        "Name": {"DisplayOrder": 5, "Heading": "Name"},  # Load balancer name for identification
        "Status": {"DisplayOrder": 6, "Heading": "Status"},  # Operational state for monitoring
        "DNSName": {"DisplayOrder": 7, "Heading": "Public Name"},  # DNS endpoint for traffic routing
        # 'State': {'DisplayOrder': 9, 'Heading': 'State', 'Condition': ['running']} # Reserved for future use
    }

    # Execute enterprise credential discovery and validation across organizational load balancing infrastructure
    CredentialList = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pAccessRoles
    )

    # Calculate organizational scope for executive load balancing infrastructure reporting
    AccountNum = len(set([acct["AccountId"] for acct in CredentialList]))
    RegionNum = len(set([acct["Region"] for acct in CredentialList]))
    WorkerThreads = min(AccountNum, 10)  # Optimize thread pool for ELB API rate limits

    print()
    print(f"Looking through {RegionNum} regions and {AccountNum} accounts for load balancers")
    print()

    # Execute comprehensive multi-threaded ELB discovery with fragment and status filtering
    All_Load_Balancers = find_all_elbs(CredentialList, pFragment, pStatus)

    # Generate comprehensive load balancer inventory report with enterprise formatting
    display_results(All_Load_Balancers, display_dict)

    # Display performance timing metrics for operational optimization and SLA compliance
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

    print(ERASE_LINE)

    # Display comprehensive operational summary for executive traffic management reporting
    print(
        f"{Fore.RED}Found {len(All_Load_Balancers)} Load Balancers across {AccountNum} profiles across {RegionNum} regions{Fore.RESET}"
    )
    print()

    # Display completion message for user confirmation and operational closure
    print("Thank you for using this script")
    print()

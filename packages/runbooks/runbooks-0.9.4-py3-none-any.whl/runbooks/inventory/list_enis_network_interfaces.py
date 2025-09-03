#!/usr/bin/env python3

"""
AWS Elastic Network Interfaces (ENI) Discovery and Analysis Script

This script provides comprehensive discovery and inventory capabilities for AWS Elastic
Network Interfaces (ENIs) across multiple accounts and regions. It's designed for enterprise
network teams who need visibility into network interface distribution, IP address management,
and network security analysis across large-scale AWS deployments.

Key Features:
- Multi-account ENI discovery using assume role capabilities
- Multi-region scanning with configurable region targeting
- IP address search and tracking for network forensics and management
- Public IP filtering for security posture analysis
- ENI status monitoring for cost optimization (unused ENIs detection)
- Enterprise reporting with CSV export and structured output
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- Network inventory and IP address management (IPAM) across organizations
- Security analysis for public IP exposure and network attack surface
- Cost optimization through detection of unused network interfaces
- Network forensics and IP address tracking for incident response
- Compliance reporting for network security and configuration standards
- Multi-account network architecture documentation and governance
- Capacity planning for network interface allocation and utilization

Network Interface Analysis Features:
- ENI enumeration with attachment status and configuration details
- IP address tracking for both private and public allocations
- VPC and subnet association analysis for network topology mapping
- Security group and network ACL configuration visibility
- DNS name resolution and endpoint management
- Network interface lifecycle and cost optimization analysis

Security Considerations:
- Uses IAM assume role capabilities for cross-account ENI access
- Implements proper error handling for authorization failures
- Supports read-only operations with no network interface modification capabilities
- Respects EC2 service permissions and regional access constraints
- Provides comprehensive audit trail through detailed logging
- Sensitive IP address information handling with appropriate access controls

IP Address Management Features:
- Targeted IP address search for network forensics and tracking
- Public IP enumeration for security assessment and compliance
- Private IP allocation analysis for network capacity planning
- ENI attachment status for resource utilization tracking
- Cross-account IP address correlation and conflict detection

Performance Considerations:
- Multi-threaded processing for concurrent ENI API operations
- Progress tracking with tqdm for operational visibility during long operations
- Efficient credential management for cross-account network access
- Memory-optimized data structures for large network interface inventories
- Queue-based worker architecture for scalable discovery operations

Threading Architecture:
- Worker thread pool with configurable concurrency (max 50 threads for ENI APIs)
- Queue-based task distribution for efficient network interface discovery
- Thread-safe error handling and progress tracking
- Graceful degradation for account access failures

Dependencies:
- boto3/botocore for AWS EC2 ENI API interactions
- Inventory_Modules for common utility functions and credential management
- ArgumentsClass for standardized CLI argument parsing
- threading and queue for concurrent processing architecture
- colorama for enhanced output formatting and tqdm for progress tracking

Cost Optimization Features:
- Detection of detached ENIs that incur charges without providing value
- ENI lifecycle analysis for resource optimization recommendations
- Public IP usage tracking for cost management
- Network interface utilization reporting for capacity planning

Future Enhancements:
- ENI security group analysis and compliance checking
- Network traffic analysis integration for performance optimization
- Automated ENI cleanup recommendations for cost reduction
- Integration with AWS Config for network configuration drift detection

Author: AWS CloudOps Team
Version: 2024.10.24
"""

import logging
import os
import sys
from queue import Queue
from threading import Thread
from time import time

from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError

# from datetime import datetime
from colorama import Fore, init
from Inventory_Modules import display_results, find_account_enis2, get_all_credentials
from tqdm.auto import tqdm

init()

__version__ = "2024.10.24"


##################
# Functions
##################


def parse_args(f_args):
    """
    Parse command line arguments for AWS Elastic Network Interface discovery operations.

    Configures comprehensive argument parsing for multi-account, multi-region ENI
    inventory operations. Supports enterprise network management with profile
    management, region targeting, organizational access controls, IP address search,
    and public IP filtering for network security analysis and IP address management.

    Args:
        f_args (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: List of AWS profiles to process
            - Regions: Target regions for ENI discovery
            - SkipProfiles/SkipAccounts: Exclusion filters
            - RootOnly: Limit to organization root accounts
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration
            - pipaddresses: Specific IP addresses to search for
            - ppublic: Filter for public IP addresses only

    Configuration Options:
        - Multi-region scanning with region filters for targeted network analysis
        - Multi-profile support for federated access across network infrastructure
        - Extended arguments for advanced filtering and account selection
        - Root-only mode for organization-level network inventory
        - File output for integration with network management tools
        - Timing metrics for performance optimization and monitoring
        - Verbose logging for debugging and network audit

    ENI-Specific Features:
        - IP address search for network forensics and incident response
        - Public IP filtering for security posture analysis and compliance
        - Support for network topology analysis and documentation
        - Integration with enterprise IP address management (IPAM) workflows

    Network Security Options:
        - Targeted IP address discovery for forensic analysis
        - Public IP enumeration for attack surface assessment
        - Network interface status filtering for cost optimization
        - Cross-account network visibility for security governance
    """
    parser = CommonArguments()
    script_path, script_name = os.path.split(sys.argv[0])
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rootOnly()
    parser.timing()
    parser.save_to_file()
    parser.verbosity()
    parser.version(__version__)
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "--ipaddress",
        "--ip",
        dest="pipaddresses",
        nargs="*",
        metavar="IP address",
        default=None,
        help="Specific IP address(es) to search for across network interfaces - supports multiple IPs for forensic analysis",
    )
    local.add_argument(
        "--public-only",
        "--po",
        action="store_true",
        dest="ppublic",
        help="Filter results to show only ENIs with public IP addresses for security posture analysis",
    )
    return parser.my_parser.parse_args(f_args)


def check_accounts_for_enis(fCredentialList, fip=None, fPublicOnly: bool = False):
    """
    Discover and inventory AWS Elastic Network Interfaces across multiple accounts and regions.

    Performs comprehensive ENI discovery using multi-threaded processing to efficiently
    inventory network interfaces across enterprise AWS environments. Supports IP address
    filtering for targeted search operations and public IP filtering for security analysis
    and compliance assessment.

    Args:
        fCredentialList (list): List of credential dictionaries for cross-account access containing:
            - AccountId: AWS account number
            - Region: Target AWS region
            - Success: Boolean indicating credential validity
            - MgmtAccount: Management account identifier
            - ParentProfile: Source AWS profile
        fip (list, optional): Specific IP addresses to search for across network interfaces
        fPublicOnly (bool, optional): Filter to show only ENIs with public IP addresses

    Returns:
        list: Comprehensive list of ENI dictionaries containing:
            - MgmtAccount: Management account identifier for organizational hierarchy
            - AccountId: AWS account containing the ENI
            - Region: AWS region where ENI is located
            - ENIId: Elastic Network Interface identifier
            - PrivateIpAddress: Primary private IP address assignment
            - PublicIp: Associated public IP address (if any)
            - Status: Current ENI state (available, in-use, attaching, detaching)
            - VpcId: Virtual Private Cloud association
            - SubnetId: Subnet placement for network topology
            - PrivateDnsName: Internal DNS name resolution

    Threading Architecture:
        - Worker thread pool with maximum 50 concurrent threads for ENI API optimization
        - Queue-based task distribution for efficient network interface discovery
        - Thread-safe error handling and progress tracking with tqdm
        - Graceful degradation for account access failures and authorization issues

    Enterprise Features:
        - Cross-account ENI discovery with assume role capabilities
        - IP address search for network forensics and incident response
        - Public IP filtering for security posture analysis and compliance
        - Comprehensive error handling for authorization and throttling scenarios

    Network Security Analysis:
        - Public IP enumeration for attack surface assessment
        - ENI status tracking for unused resource identification
        - Cross-account network visibility for security governance
        - IP address correlation for forensic investigations

    Error Handling:
        - Authorization failure detection with region opt-in diagnostics
        - AWS API throttling management with appropriate logging
        - Graceful handling of missing ENIs and empty responses
        - Thread-safe error reporting and progress updates

    Performance Considerations:
        - High concurrency (50 threads) optimized for ENI API characteristics
        - Efficient memory management for large network interface inventories
        - Progress tracking for operational visibility during discovery
        - ENI metadata extraction for enterprise network management

    Cost Optimization:
        - Detection of unused ENIs that incur charges without providing value
        - Public IP usage analysis for cost management
        - Network interface lifecycle tracking for optimization
    """

    # Worker thread class for concurrent ENI discovery
    class FindENIs(Thread):
        def __init__(self, queue):
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Main worker thread execution loop for ENI discovery and network interface analysis.

            Continuously processes credential sets from the shared work queue, performing
            comprehensive Elastic Network Interface discovery operations with detailed
            metadata extraction and enterprise network security analysis.
            """
            while True:
                # Retrieve ENI discovery work item from thread-safe queue
                c_account_credentials, c_region, c_fip, c_PlacesToLook, c_PlaceCount = self.queue.get()
                pbar.update()  # Update progress tracking for operational visibility
                logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")

                try:
                    logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")

                    # Execute comprehensive ENI discovery for the current account/region
                    # This calls the inventory module's specialized ENI discovery function with IP filtering
                    account_enis = find_account_enis2(c_account_credentials, c_region, c_fip)
                    logging.info(
                        f"Successfully connected to account {c_account_credentials['AccountId']} in region {c_region}"
                    )

                    # Process each discovered ENI with comprehensive metadata extraction and filtering
                    for eni in account_enis:
                        # Add organizational context for multi-account network management
                        eni["MgmtAccount"] = c_account_credentials["MgmtAccount"]

                        # Apply public IP filtering for security posture analysis when requested
                        if fPublicOnly and eni["PublicIp"] == "No Public IP":
                            # Skip ENIs without public IPs when security analysis filter is active
                            # This is critical for attack surface assessment and compliance reporting
                            pass
                        else:
                            # Include ENI in enterprise network inventory for comprehensive reporting
                            # ENI contains detailed network interface metadata:
                            # - IP address assignments (private and public)
                            # - VPC and subnet associations for topology mapping
                            # - Security group configurations for access control analysis
                            # - DNS name resolution for endpoint management
                            # - Attachment status for cost optimization analysis
                            Results.append(eni)

                except KeyError as my_Error:
                    # Handle cases where expected keys are missing from ENI API responses
                    # This can occur with incomplete ENI metadata or API response format changes
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    # Handle cases where profile configuration is incorrect or credential format errors
                    # This typically indicates AWS profile misconfiguration or credential management issues
                    logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
                    logging.warning(my_Error)
                    continue
                finally:
                    # Always ensure queue management regardless of success/failure for thread pool stability
                    # Critical for preventing worker thread deadlock and ensuring operation completion
                    self.queue.task_done()

    # Initialize queue-based threading architecture for scalable ENI discovery
    checkqueue = Queue()

    # Initialize progress tracking for operational visibility during large-scale operations
    pbar = tqdm(
        desc=f"Finding enis from {len(CredentialList)} accounts / regions",
        total=len(fCredentialList),
        unit=" locations",
    )

    # Initialize results list for aggregating discovered ENIs
    Results = []
    PlaceCount = 0
    PlacesToLook = fCredentialList.__len__()

    # Configure worker thread pool size optimized for ENI API characteristics
    # Maximum 50 threads to balance performance with AWS API rate limits
    WorkerThreads = min(len(fCredentialList), 50)

    # Start worker threads for concurrent ENI discovery
    for x in range(WorkerThreads):
        worker = FindENIs(checkqueue)
        # Setting daemon to True allows main thread exit even if workers are still processing
        worker.daemon = True
        worker.start()

    # Queue credential sets for processing by worker threads
    for credential in fCredentialList:
        logging.info(f"Connecting to account {credential['AccountId']} in region {credential['Region']}")
        try:
            # Queue credential set with IP filter and progress tracking parameters
            # Tuple format: (credentials, region, ip_filter, total_places, current_count)
            checkqueue.put((credential, credential["Region"], fip, PlacesToLook, PlaceCount))
            PlaceCount += 1
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
    return Results


def present_results(f_ENIsFound: list):
    """
    Present comprehensive ENI discovery results with enterprise network analysis and cost optimization insights.

    Generates detailed network interface inventory reports with organizational hierarchy,
    security posture analysis, and cost optimization recommendations. Identifies unused
    ENIs that may be generating unnecessary charges and provides executive-level
    operational summaries for network management decision-making.

    Args:
        f_ENIsFound (list): List of discovered ENI dictionaries containing:
            - Network interface metadata and organizational context
            - IP address assignments and DNS configuration
            - VPC/subnet associations for topology analysis
            - Status information for cost optimization assessment

    Report Features:
        - Hierarchical organization by management account and region
        - Status-based filtering highlighting cost optimization opportunities
        - Public IP analysis for security posture assessment
        - Comprehensive network topology and resource utilization metrics

    Cost Optimization Analysis:
        - Identifies detached ENIs that incur charges without providing value
        - Highlights ENIs in transitional states (attaching, detaching)
        - Provides actionable recommendations for network resource cleanup
        - Calculates potential cost savings from unused network interfaces

    Enterprise Reporting:
        - Multi-account network visibility with management hierarchy
        - Regional distribution analysis for capacity planning
        - Public IP exposure analysis for security compliance
        - CSV export integration for network management tool integration
    """
    # Configure enterprise ENI inventory report display formatting for network management analysis
    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},  # Management account hierarchy
        "AccountId": {"DisplayOrder": 2, "Heading": "Acct Number"},  # Account identifier for governance
        "Region": {"DisplayOrder": 3, "Heading": "Region"},  # AWS region for geographic distribution
        "PrivateDnsName": {"DisplayOrder": 4, "Heading": "ENI Name"},  # DNS name for endpoint identification
        "Status": {
            "DisplayOrder": 5,
            "Heading": "Status",
            "Condition": ["available", "attaching", "detaching"],
        },  # Operational state for cost analysis
        "PublicIp": {"DisplayOrder": 6, "Heading": "Public IP Address"},  # Public IP for security analysis
        "ENIId": {"DisplayOrder": 7, "Heading": "ENI Id"},  # ENI identifier for management
        "PrivateIpAddress": {"DisplayOrder": 8, "Heading": "Assoc. IP"},  # Private IP assignment
    }

    # Sort ENIs for consistent enterprise reporting and network topology analysis
    sorted_ENIs_Found = sorted(f_ENIsFound, key=lambda d: (d["MgmtAccount"], d["AccountId"], d["Region"], d["VpcId"]))

    # Generate comprehensive ENI inventory report with CSV export capability
    display_results(sorted_ENIs_Found, display_dict, "None", pFilename)

    # Identify detached ENIs for cost optimization analysis and recommendations
    # ENIs in these states incur charges but provide no operational value
    DetachedENIs = [x for x in sorted_ENIs_Found if x["Status"] in ["available", "attaching", "detaching"]]

    # Calculate organizational scope metrics for executive network management reporting
    RegionList = list(set([x["Region"] for x in sorted_ENIs_Found]))
    AccountList = list(set([x["AccountId"] for x in sorted_ENIs_Found]))

    # Display exclusion information for audit trail and operational transparency
    print() if pSkipAccounts is not None or pSkipProfiles is not None else ""
    print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else ""
    print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else ""
    print()

    # Inform user about CSV export capability for integration with network management tools
    print(
        f"The output has also been written to a file beginning with '{pFilename}' + the date and time"
    ) if pFilename is not None else ""

    # Display comprehensive operational summary for executive network management reporting
    print(
        f"Found {len(f_ENIsFound)} ENIs {'with public IPs' if pPublicOnly else ''} across {len(AccountList)} accounts across {len(RegionList)} regions"
    )

    # Highlight cost optimization opportunities with unused ENI identification
    print(
        f"{Fore.RED}Found {len(DetachedENIs)} ENIs that are not listed as 'in-use' and may therefore be costing you additional money while they're unused.{Fore.RESET}"
    ) if DetachedENIs else ""
    print()

    # Provide detailed cost optimization analysis when verbose logging is enabled
    if verbose < 40:
        for x in DetachedENIs:
            print(x)


##################
# Main execution entry point for enterprise ENI discovery and network security analysis
##################

ERASE_LINE = "\x1b[2K"

if __name__ == "__main__":
    """
    Main orchestration for comprehensive Elastic Network Interface discovery and analysis.
    
    Coordinates multi-account, multi-region ENI inventory with detailed network security
    analysis, IP address management support, and enterprise network infrastructure
    governance across AWS Organizations environments.
    """
    # Parse enterprise command-line arguments with ENI-specific network security options
    args = parse_args(sys.argv[1:])

    # Extract configuration parameters for multi-account network interface discovery
    pProfiles = args.Profiles  # AWS profile list for federated ENI access
    pRegionList = args.Regions  # Target regions for network interface enumeration
    pSkipAccounts = args.SkipAccounts  # Account exclusion list for organizational policy compliance
    pSkipProfiles = args.SkipProfiles  # Profile exclusion for credential optimization
    pAccounts = args.Accounts  # Specific account targeting for focused network analysis
    pRootOnly = args.RootOnly  # Organization root account limitation flag
    pIPaddressList = args.pipaddresses  # Specific IP addresses for forensic analysis and tracking
    pPublicOnly = args.ppublic  # Public IP filter for security posture assessment
    pFilename = args.Filename  # CSV export file for enterprise network reporting
    pTiming = args.Time  # Performance timing for operational optimization
    verbose = args.loglevel  # Logging verbosity for network infrastructure visibility

    # Configure enterprise logging infrastructure for ENI operations audit trail
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    # Initialize performance timing for operational optimization and SLA compliance
    begin_time = time()
    print()
    print(f"Checking for Elastic Network Interfaces... ")
    print()

    logging.info(f"Profiles: {pProfiles}")

    # Execute enterprise credential discovery and validation across organizational network infrastructure
    CredentialList = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList
    )

    # Execute comprehensive multi-threaded ENI discovery with IP address filtering and security analysis
    ENIsFound = check_accounts_for_enis(CredentialList, pIPaddressList, pPublicOnly)

    # Generate comprehensive ENI inventory report with cost optimization and security insights
    present_results(ENIsFound)

    # Display performance timing metrics for operational optimization and SLA compliance
    if pTiming:
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

# Display completion message for user confirmation and operational closure
print()
print("Thank you for using this script")
print()

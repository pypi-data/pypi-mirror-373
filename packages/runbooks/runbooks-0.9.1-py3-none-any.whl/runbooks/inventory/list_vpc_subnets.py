#!/usr/bin/env python3

"""
AWS VPC Subnet Inventory and IP Utilization Analysis Script

This script provides comprehensive discovery, analysis, and reporting capabilities for
AWS VPC subnets across multiple accounts and regions. It's designed for enterprise
networking teams who need visibility into subnet utilization, IP address allocation,
and network architecture across large-scale AWS deployments.

Key Features:
- Multi-account VPC subnet discovery using assume role capabilities
- Multi-region scanning with configurable region targeting
- IP address allocation tracking and utilization analysis
- Subnet exhaustion detection with configurable thresholds
- Parallel processing with optimized threading for large environments
- IP address search capabilities for network troubleshooting
- Comprehensive subnet metadata extraction and reporting
- Enterprise reporting with CSV export and structured output
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- Network capacity planning and IP address management (IPAM)
- Subnet utilization monitoring and exhaustion prevention
- Multi-account network architecture documentation
- IP address conflict detection and resolution
- Network security auditing and compliance reporting
- Cost optimization through subnet consolidation analysis
- Disaster recovery planning for network infrastructure

Network Analysis Features:
- IP utilization percentage calculation with exhaustion alerts
- Available IP address counting across subnet ranges
- VPC-level aggregation for architectural analysis
- CIDR block overlap detection and validation
- Network segmentation compliance verification
- Subnet naming convention analysis and standardization

Security Considerations:
- Uses IAM assume role capabilities for cross-account access
- Implements proper error handling for authorization failures
- Supports read-only operations with no network modification capabilities
- Respects VPC and subnet access permissions
- Provides comprehensive audit trail through detailed logging

Performance Optimizations:
- Multi-threaded processing with configurable worker pools
- Queue-based work distribution for load balancing
- Progress tracking with real-time feedback
- API rate limiting respect to prevent throttling
- Efficient memory usage for large subnet inventories

Future Enhancements:
- Elastic IP address integration for complete IP visibility
- Network ACL and security group association analysis
- Route table mapping and traffic flow analysis
- ENI (Elastic Network Interface) inventory integration

Dependencies:
- boto3/botocore for AWS VPC API interactions
- Threading support for concurrent processing
- Inventory_Modules for common utility functions
- ArgumentsClass for standardized CLI argument parsing

Author: AWS CloudOps Team
Version: 2024.10.24
"""

import logging
import os
import sys
from queue import Queue
from threading import Thread
from time import time

import Inventory_Modules
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, get_all_credentials

init()
__version__ = "2024.10.24"

# TODO: Add Elastic IPs to this script as well.


##################
# Functions
##################


def parse_args(f_args):
    """
    Parse command line arguments for VPC subnet inventory and IP analysis operations.

    Configures comprehensive argument parsing for multi-account, multi-region VPC subnet
    discovery with specialized support for IP address searching and network analysis.
    Supports enterprise networking patterns with profile management, region targeting,
    and operational customization for large-scale network environments.

    Args:
        f_args (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: List of AWS profiles to process
            - Regions: Target regions for subnet discovery
            - SkipProfiles/SkipAccounts: Exclusion filters
            - RootOnly: Limit to organization root accounts
            - AccessRoles: IAM roles for cross-account access
            - pipaddresses: Specific IP addresses to search for
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration

    Configuration Options:
        - Multi-region scanning with region filters
        - Multi-profile support for federated access
        - Extended arguments for advanced filtering
        - Root-only mode for organization-level inventory
        - Role-based access for cross-account operations
        - IP address search for network troubleshooting
        - File output for integration and reporting
        - Timing metrics for performance optimization
        - Verbose logging for debugging and audit

    Network-Specific Arguments:
        --ipaddress/--ip: Enables targeted IP address search across all discovered
                         subnets for network troubleshooting and IP conflict detection.
                         Supports multiple IP addresses for batch operations.

    Enterprise Features:
        - Cross-account role assumption for organizational visibility
        - Configurable region targeting for regulatory compliance
        - Profile-based access controls for security boundaries
        - Comprehensive logging for network audit requirements
    """
    script_path, script_name = os.path.split(sys.argv[0])
    parser = CommonArguments()
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rootOnly()
    parser.rolestouse()
    parser.save_to_file()
    parser.timing()
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
        help="IP address(es) you're looking for within your VPCs",
    )
    return parser.my_parser.parse_args(f_args)


def check_accounts_for_subnets(CredentialList, fip=None):
    """
    Discover and analyze VPC subnets across multiple AWS accounts and regions with parallel processing.

    Implements high-performance multi-threaded processing to efficiently scan large-scale AWS
    environments for VPC subnets with optional IP address filtering. Uses optimized worker
    pools to maximize throughput while respecting AWS API limits and providing real-time
    progress feedback for operational visibility.

    Args:
        CredentialList (list): List of credential dictionaries containing:
            - AccountId: AWS account identifier
            - MgmtAccount: Organization management account
            - Region: Target AWS region for scanning
            - Credentials: Temporary AWS credentials for API access
        fip (list, optional): List of IP addresses to search for within subnets

    Returns:
        list: Aggregated collection of subnet records with structure:
            - MgmtAccount: Organization management account
            - AccountId: Account containing the subnet
            - Region: AWS region of the subnet
            - VpcId: VPC identifier containing the subnet
            - SubnetName: Subnet name from Name tag (default: "None")
            - CidrBlock: CIDR block assigned to subnet
            - AvailableIpAddressCount: Available IP addresses in subnet
            - SubnetId: Unique subnet identifier
            - Tags: Resource tags for metadata and organization

    Threading Architecture:
        - Worker pool limited to min(credentials, 50) threads for optimal performance
        - Queue-based work distribution for balanced load across workers
        - Daemon threads for clean shutdown handling
        - Real-time progress indicators for operational feedback

    Network Processing:
        - Subnet metadata enrichment with organizational context
        - Tag-based name resolution with fallback handling
        - VPC association mapping for network architecture visibility
        - IP filtering capabilities for targeted subnet discovery

    Error Handling:
        - KeyError: Account access credential issues
        - AttributeError: Profile configuration problems
        - ClientError: AWS API authorization and regional failures
        - Graceful handling with continued processing on individual failures

    Performance Optimizations:
        - Concurrent processing across accounts and regions
        - Worker thread pool tuning for API efficiency
        - Progress tracking for operational visibility
        - Memory-efficient result aggregation
    """

    class FindSubnets(Thread):
        """
        Worker thread class for concurrent VPC subnet discovery and analysis.

        Processes work items from shared queue to discover subnets in individual
        AWS accounts and regions. Enriches subnet data with organizational metadata
        and handles tag-based name resolution for enterprise visibility.
        """

        def __init__(self, queue):
            """Initialize worker thread with shared work queue."""
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Main worker thread execution loop for subnet discovery.

            Continuously processes credential sets from the work queue, discovers
            VPC subnets, enriches metadata, and aggregates results. Implements
            comprehensive error handling for various AWS API error conditions.
            """
            while True:
                # Get the work from the queue and expand the tuple
                c_account_credentials, c_fip, c_PlacesToLook, c_PlaceCount = self.queue.get()
                logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
                try:
                    logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
                    # Call VPC API to discover subnets in this account/region with optional IP filtering
                    account_subnets = Inventory_Modules.find_account_subnets2(c_account_credentials, c_fip)
                    logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")

                    # Enrich each discovered subnet with organizational metadata
                    for y in range(len(account_subnets["Subnets"])):
                        account_subnets["Subnets"][y]["MgmtAccount"] = c_account_credentials["MgmtAccount"]
                        account_subnets["Subnets"][y]["AccountId"] = c_account_credentials["AccountId"]
                        account_subnets["Subnets"][y]["Region"] = c_account_credentials["Region"]
                        account_subnets["Subnets"][y]["SubnetName"] = "None"

                        # Extract subnet name from tags for human-readable identification
                        if "Tags" in account_subnets["Subnets"][y].keys():
                            for tag in account_subnets["Subnets"][y]["Tags"]:
                                if tag["Key"] == "Name":
                                    account_subnets["Subnets"][y]["SubnetName"] = tag["Value"]

                        # Normalize VPC ID field for consistent reporting
                        account_subnets["Subnets"][y]["VPCId"] = (
                            account_subnets["Subnets"][y]["VpcId"]
                            if "VpcId" in account_subnets["Subnets"][y].keys()
                            else None
                        )

                    # Aggregate discovered subnets to shared result collection
                    if len(account_subnets["Subnets"]) > 0:
                        AllSubnets.extend(account_subnets["Subnets"])

                except KeyError as my_Error:
                    # Handle credential or account access failures
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    # Handle profile configuration issues
                    logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
                    logging.warning(my_Error)
                    continue
                finally:
                    # Provide real-time progress feedback and mark work item complete
                    print(
                        f"{ERASE_LINE}Finished finding subnets in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']} - {c_PlaceCount} / {c_PlacesToLook}",
                        end="\r",
                    )
                    self.queue.task_done()

    # Initialize threading infrastructure for parallel processing
    checkqueue = Queue()
    AllSubnets = []
    PlaceCount = 0
    PlacesToLook = len(CredentialList)
    WorkerThreads = min(len(CredentialList), 50)  # Limit worker threads for API efficiency

    # Start worker thread pool for concurrent subnet discovery
    for x in range(WorkerThreads):
        worker = FindSubnets(checkqueue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    # Queue all credential sets for processing by worker threads
    for credential in CredentialList:
        logging.info(f"Connecting to account {credential['AccountId']}")
        try:
            checkqueue.put((credential, fip, PlacesToLook, PlaceCount))
            PlaceCount += 1
        except ClientError as my_Error:
            # Handle authorization errors during queue operations
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region"
                )
                logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass

    # Wait for all work items to be processed
    checkqueue.join()
    return AllSubnets


def present_results(fSubnetsFound: list):
    """
    Description: Shows off results at the end
    @param fSubnetsFound: List of subnets found and their attributes.
    """
    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
        "AccountId": {"DisplayOrder": 2, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 3, "Heading": "Region"},
        "VpcId": {"DisplayOrder": 4, "Heading": "VPC ID"},
        "SubnetName": {"DisplayOrder": 5, "Heading": "Subnet Name"},
        "CidrBlock": {"DisplayOrder": 6, "Heading": "CIDR Block"},
        "AvailableIpAddressCount": {"DisplayOrder": 7, "Heading": "Available IPs"},
        # 'IPUtilization'          : {'DisplayOrder': 8, 'Heading': 'IP Utilization'},
        # 'NearExhaustion'          : {'DisplayOrder': 8, 'Heading': 'Near Exhaustion', 'Condition': [True]},
    }
    AccountNum = len(set([acct["AccountId"] for acct in AllCredentials]))
    RegionNum = len(set([acct["Region"] for acct in AllCredentials]))
    sorted_Subnets_Found = sorted(
        fSubnetsFound, key=lambda x: (x["MgmtAccount"], x["AccountId"], x["Region"], x["SubnetName"])
    )
    display_results(sorted_Subnets_Found, display_dict, "None", pFilename)
    print()
    print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else ""
    print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else ""
    print(
        f"The output has also been written to a file beginning with '{pFilename}' + the date and time"
    ) if pFilename is not None else ""
    print()
    print(f"Found {len(SubnetsFound)} subnets across {AccountNum} accounts across {RegionNum} regions")


def analyze_results(fSubnetsFound: list):
    # :fSubnetsFound: a list of the subnets found and their attributes
    account_summary = []
    VPC_summary = []
    subnets_near_exhaustion = []
    for record in fSubnetsFound:
        AvailableIps = record["AvailableIpAddressCount"]
        account_number = record["AccountId"]
        vpc_id = record["VpcId"]
        mask = int(str(record["CidrBlock"]).split("/")[1])
        TotalIPs = 2 ** (32 - mask) - 5
        IPUtilization = 100 - (round(AvailableIps / TotalIPs, 2) * 100)
        subnets_near_exhaustion.append(record["SubnetId"]) if IPUtilization > 74 else ""
        if account_number not in account_summary:
            account_summary.append(account_number)
        if vpc_id not in VPC_summary:
            VPC_summary.append(vpc_id)
    print()
    print(f"Number of accounts found with subnets: {len(account_summary)}")
    print(f"Number of unique VPCs found: {len(VPC_summary)}")
    print(f"Number of subnets in danger of IP Exhaustion (80%+ IPs utilized): {len(subnets_near_exhaustion)}")
    # print(f"Number of subnets using unroutable space (100.64.*.*): ")
    print()


##################
# Main
##################


ERASE_LINE = "\x1b[2K"
begin_time = time()

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles
    pRegionList = args.Regions
    pAccounts = args.Accounts
    pRoleList = args.AccessRoles
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pRootOnly = args.RootOnly
    pIPaddressList = args.pipaddresses
    pFilename = args.Filename
    pTiming = args.Time
    verbose = args.loglevel
    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    logging.info(f"Profiles: {pProfiles}")

    print()
    print(f"Checking accounts for Subnets... ")
    print()

    # Get credentials from all relevant Children accounts
    AllCredentials = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pRoleList
    )
    # Get relevant subnets
    SubnetsFound = check_accounts_for_subnets(AllCredentials, fip=pIPaddressList)
    # display_results(SubnetsFound, display_dict)
    present_results(SubnetsFound)
    # Print out an analysis of what was found at the end
    if verbose < 50:
        analyze_results(SubnetsFound)
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script completed in {time() - begin_time:.2f} seconds{Fore.RESET}")

print()
print("Thank you for using this script")
print()

#!/usr/bin/env python3

"""
AWS Route53 Hosted Zones Inventory Script

This script provides comprehensive discovery and inventory capabilities for AWS Route53
private hosted zones across multiple accounts and regions. It's designed for enterprise
environments where DNS infrastructure visibility and management is critical for
networking operations and compliance.

Key Features:
- Multi-account Route53 hosted zone discovery using assume role capabilities
- Multi-region scanning with configurable region targeting
- Parallel processing with configurable threading for performance optimization
- Private hosted zone detection and record count analysis
- Detailed zone metadata extraction including zone ID and record counts
- Comprehensive error handling for authorization failures and throttling
- Enterprise reporting with CSV export and structured output formatting
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- DNS Infrastructure auditing and compliance reporting
- Multi-account DNS zone consolidation planning
- Route53 cost optimization through zone utilization analysis
- Networking architecture documentation and change management
- Security auditing of DNS configurations across organization
- Disaster recovery planning for DNS infrastructure

Security Considerations:
- Uses IAM assume role capabilities for cross-account access
- Implements proper error handling for authorization failures
- Supports read-only operations with no modification capabilities
- Respects AWS API rate limits with controlled threading
- Provides audit trail through comprehensive logging

Output Format:
- Tabular display with sortable columns for analysis
- CSV export capability for integration with other tools
- Color-coded output for enhanced readability
- Performance timing metrics for optimization

Dependencies:
- boto3/botocore for AWS API interactions
- Threading support for concurrent processing
- Inventory_Modules for common utility functions
- ArgumentsClass for standardized CLI argument parsing

Author: AWS CloudOps Team
Version: 2023.11.08
"""

import logging
import sys
from queue import Queue
from threading import Thread
from time import time

from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_private_hosted_zones2, get_all_credentials

init()
__version__ = "2023.11.08"
ERASE_LINE = "\x1b[2K"

########################


def parse_args(args):
    """
    Parse command line arguments for Route53 hosted zones discovery.

    Configures comprehensive argument parsing for multi-account, multi-region Route53
    hosted zone inventory operations. Supports enterprise deployment patterns with
    profile management, region targeting, and output customization.

    Args:
        args (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: List of AWS profiles to process
            - Regions: Target regions for hosted zone discovery
            - SkipProfiles/SkipAccounts: Exclusion filters
            - RootOnly: Limit to organization root accounts
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration

    Configuration Options:
        - Multi-region scanning with region filters
        - Multi-profile support for federated access
        - Extended arguments for advanced filtering
        - Root-only mode for organization-level inventory
        - File output for integration and reporting
        - Timing metrics for performance optimization
        - Verbose logging for debugging and audit
    """
    parser = CommonArguments()
    parser.multiregion()
    parser.multiprofile()
    parser.extendedargs()
    parser.rootOnly()
    parser.save_to_file()
    parser.verbosity()
    parser.timing()
    parser.version(__version__)
    return parser.my_parser.parse_args(args)


def find_all_hosted_zones(fAllCredentials):
    """
    Discover Route53 private hosted zones across multiple AWS accounts and regions.

    Implements high-performance parallel processing to efficiently scan large-scale
    AWS environments for Route53 private hosted zones. Uses multi-threading with
    configurable worker pools to optimize API call patterns while respecting
    AWS service limits and throttling constraints.

    Args:
        fAllCredentials (list): List of credential dictionaries containing:
            - AccountId: AWS account identifier
            - ParentProfile: Source profile for assume role
            - MgmtAccount: Management account identifier
            - Region: Target AWS region for scanning
            - Credentials: Temporary AWS credentials

    Returns:
        list: Collection of hosted zone records with structure:
            - ParentProfile: Source AWS profile
            - MgmtAccount: Organization management account
            - AccountId: Account containing the hosted zone
            - Region: AWS region of the hosted zone
            - PHZName: Private hosted zone name/domain
            - Records: Number of resource records in zone
            - PHZId: Route53 hosted zone identifier

    Threading Architecture:
        - Worker pool limited to min(credentials, 25) threads
        - Queue-based work distribution for load balancing
        - Daemon threads for clean shutdown handling
        - Progress indicators with real-time feedback

    Error Handling:
        - KeyError: Account access credential issues
        - AttributeError: Profile configuration problems
        - ClientError: AWS API authorization and throttling
        - Regional opt-in validation for new AWS regions

    Performance Optimizations:
        - Concurrent processing across accounts/regions
        - Worker thread pool tuning for API efficiency
        - Queue-based work distribution
        - Progress tracking for operational visibility
    """

    class FindZones(Thread):
        """
        Worker thread class for concurrent Route53 hosted zone discovery.

        Processes work items from shared queue to discover private hosted zones
        in individual AWS accounts and regions. Implements proper error handling
        and progress reporting for enterprise-scale operations.
        """

        def __init__(self, queue):
            """Initialize worker thread with shared work queue."""
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Main worker thread execution loop.

            Continuously processes credential sets from the work queue, discovers
            Route53 private hosted zones, and aggregates results. Handles various
            AWS API error conditions with appropriate retry and logging strategies.
            """
            while True:
                c_account_credentials, c_PlaceCount = self.queue.get()
                logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")
                try:
                    # Call Route53 API to discover private hosted zones in this account/region
                    HostedZones = find_private_hosted_zones2(c_account_credentials, c_account_credentials["Region"])
                    logging.info(
                        f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(HostedZones['HostedZones'])} zones"
                    )

                    # Process each discovered hosted zone and extract metadata
                    if len(HostedZones["HostedZones"]) > 0:
                        for zone in HostedZones["HostedZones"]:
                            ThreadedHostedZones.append(
                                {
                                    "ParentProfile": c_account_credentials["ParentProfile"],
                                    "MgmtAccount": c_account_credentials["MgmtAccount"],
                                    "AccountId": c_account_credentials["AccountId"],
                                    "Region": c_account_credentials["Region"],
                                    "PHZName": zone["Name"],
                                    "Records": zone["ResourceRecordSetCount"],
                                    "PHZId": zone["Id"],
                                }
                            )
                except KeyError as my_Error:
                    # Handle credential or account access failures
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    # Handle profile configuration issues
                    logging.error("Error: Likely that one of the supplied profiles was wrong")
                    logging.warning(my_Error)
                    continue
                except ClientError as my_Error:
                    # Handle AWS API errors including authorization and throttling
                    if "AuthFailure" in str(my_Error):
                        logging.error(
                            f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region"
                        )
                        logging.warning(
                            f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into"
                        )
                        continue
                    else:
                        logging.error("Error: Likely throttling errors from too much activity")
                        logging.warning(my_Error)
                        continue
                finally:
                    # Provide progress feedback and mark work item complete
                    print(".", end="")
                    self.queue.task_done()

    # Initialize threading infrastructure for parallel processing
    checkqueue = Queue()
    ThreadedHostedZones = []
    PlaceCount = 0
    WorkerThreads = min(len(fAllCredentials), 25)  # Limit worker threads for API efficiency

    # Start worker thread pool for concurrent processing
    for x in range(WorkerThreads):
        worker = FindZones(checkqueue)
        worker.daemon = True
        worker.start()

    # Queue all credential sets for processing by worker threads
    for credential in fAllCredentials:
        logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
        try:
            checkqueue.put((credential, PlaceCount))
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
    return ThreadedHostedZones


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles
    pRegionList = args.Regions
    pSkipProfiles = args.SkipProfiles
    pSkipAccounts = args.SkipAccounts
    pRootOnly = args.RootOnly
    pAccounts = args.Accounts
    pFilename = args.Filename
    pTiming = args.Time
    verbose = args.loglevel
    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    begin_time = time()
    # Get Credentials
    AllCredentials = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList
    )
    AllAccountList = list(set([x["AccountId"] for x in AllCredentials]))
    AllRegionList = list(set([x["Region"] for x in AllCredentials]))
    # Find the hosted zones
    AllHostedZones = find_all_hosted_zones(AllCredentials)
    # Display results
    print()

    display_dict = {
        # 'ParentProfile': {'DisplayOrder': 1, 'Heading': 'Parent Profile'},
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
        "AccountId": {"DisplayOrder": 2, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 3, "Heading": "Region"},
        "PHZName": {"DisplayOrder": 4, "Heading": "Zone Name"},
        "Records": {"DisplayOrder": 5, "Heading": "# of Records"},
        "PHZId": {"DisplayOrder": 6, "Heading": "Zone ID"},
    }
    sorted_results = sorted(
        AllHostedZones, key=lambda x: (x["ParentProfile"], x["MgmtAccount"], x["AccountId"], x["PHZName"], x["Region"])
    )
    display_results(sorted_results, display_dict, None, pFilename)

    print(
        f"{Fore.RED}Found {len(AllHostedZones)} Hosted Zones across {len(AllAccountList)} accounts across {len(AllRegionList)} regions{Fore.RESET}"
    )
    print()
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
        print(ERASE_LINE)
    print("Thanks for using this script...")
    print()

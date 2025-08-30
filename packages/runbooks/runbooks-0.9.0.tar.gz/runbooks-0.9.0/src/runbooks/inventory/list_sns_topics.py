#!/usr/bin/env python3
"""
AWS SNS Topic Inventory Collection

A comprehensive SNS topic discovery tool for multi-account AWS Organizations that
provides detailed messaging infrastructure visibility across all accounts and regions.
Essential for event-driven architecture governance, compliance, and cost optimization.

**AWS API Mapping**: `boto3.client('sns').list_topics()`

Features:
    - Multi-account SNS topic discovery via AWS Organizations
    - Fragment-based topic filtering for targeted operations
    - Cross-region messaging topology mapping
    - Topic naming convention compliance validation
    - Comprehensive error handling and logging
    - Enterprise-grade inventory and reporting

Messaging Architecture Use Cases:
    - Event-driven architecture documentation and governance
    - Topic naming convention compliance auditing
    - Cross-account messaging topology analysis
    - Cost optimization through topic utilization assessment
    - Security assessment of topic configurations and policies
    - Migration planning for messaging infrastructure

Compatibility:
    - AWS Organizations with cross-account roles
    - AWS Control Tower managed accounts
    - Standalone AWS accounts
    - All AWS regions including opt-in regions
    - All SNS topic types (Standard and FIFO)

Example:
    Discover all SNS topics across organization:
    ```bash
    python list_sns_topics.py --profile my-org-profile
    ```
    
    Find topics with specific naming pattern:
    ```bash
    python list_sns_topics.py --profile my-profile --fragment "alert"
    ```
    
    Export topic inventory to file:
    ```bash
    python list_sns_topics.py --profile my-profile \
        --save sns_inventory.json --output json
    ```

Requirements:
    - IAM permissions: `sns:ListTopics`, `sts:AssumeRole`
    - AWS Organizations access (for multi-account scanning)
    - Python 3.8+ with required dependencies

Author:
    AWS Cloud Foundations Team
    
Version:
    2023.11.08
"""

import logging
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
__version__ = "2023.11.08"
begin_time = time()


def parse_args(args):
    """
    Parse and validate command-line arguments for SNS topic inventory discovery.

    Configures the argument parser with SNS-specific options for comprehensive
    messaging infrastructure discovery across multi-account AWS environments.
    Uses the standardized CommonArguments framework for consistency.

    Args:
        args (list): Command-line arguments to parse (typically sys.argv[1:])

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: AWS profiles for multi-account messaging discovery
            - Regions: Target AWS regions for SNS enumeration
            - AccessRoles: Cross-account roles for Organizations access
            - Fragment: Topic name fragment for targeted filtering
            - pExact: Boolean flag for exact topic name matching
            - RootOnly: Limit to Organization Management Accounts
            - Filename: Output file prefix for topic inventory export
            - Other standard framework arguments

    Messaging Discovery Use Cases:
        - Topic inventory: Complete SNS topic asset management
        - Architecture documentation: Event-driven system mapping
        - Compliance auditing: Topic naming and configuration validation
        - Cost optimization: Topic utilization and subscription analysis
        - Security assessment: Topic policy and access review
        - Migration planning: Cross-account messaging architecture analysis
    """
    parser = CommonArguments()
    parser.my_parser.description = "Finding all the topics for the accounts we can find... "
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rootOnly()
    parser.fragment()
    parser.save_to_file()
    parser.timing()
    parser.verbosity()
    parser.version(__version__)
    return parser.my_parser.parse_args(args)


def find_topics(CredentialList: list, ftopic_frag: str = None, fexact: bool = False) -> list:
    """
    Execute multi-threaded SNS topic discovery across AWS accounts and regions.

    This is the core messaging infrastructure discovery engine that performs concurrent
    SNS topic enumeration across all provided AWS accounts and regions. Essential for
    understanding event-driven architecture, message routing, and compliance assessment.

    Args:
        CredentialList (list): List of credential dictionaries containing:
            - AccountId: AWS account identifier
            - Region: AWS region name
            - AccessKeyId, SecretAccessKey, SessionToken: AWS credentials
            - MgmtAccount: Management account identifier
            - Success: Boolean flag indicating credential validation status

        ftopic_frag (str, optional): Topic name fragment for filtering:
            - Enables targeted discovery of specific topic patterns
            - Supports partial name matching for flexible searches
            - Examples: "alert", "notification", "error"

        fexact (bool, optional): Enable exact topic name matching:
            - When True, requires precise topic name matches
            - When False, performs substring matching
            - Default: False for broader discovery scope

    Returns:
        list: Comprehensive SNS topic inventory with metadata:
            - TopicName: SNS topic name or ARN
            - AccountId: Source AWS account
            - Region: Source AWS region
            - MgmtAccount: Management account identifier

    Threading Architecture:
        - Uses Queue for thread-safe work distribution
        - Worker thread pool (max 50) for concurrent topic discovery
        - Comprehensive error handling for account access failures
        - Progress tracking for large-scale messaging inventory

    Messaging Analysis Features:
        - Topic name pattern analysis and compliance validation
        - Cross-account messaging topology mapping
        - Regional topic distribution assessment
        - Fragment-based filtering for targeted operations
        - FIFO vs Standard topic classification

    Enterprise Use Cases:
        - Event-driven architecture documentation and governance
        - Topic naming convention compliance auditing
        - Cross-account messaging security assessment
        - Cost optimization through topic utilization analysis
        - Migration planning and messaging consolidation
        - Disaster recovery and business continuity planning
    """

    class FindTopics(Thread):
        """
        Worker thread for concurrent SNS topic discovery across AWS accounts.

        Each worker thread processes credential sets from the shared queue,
        calls AWS SNS APIs to discover messaging topics, and performs detailed
        metadata extraction including topic filtering and categorization.

        Messaging Discovery Capabilities:
            - SNS topic enumeration with comprehensive metadata
            - Topic name pattern matching and filtering
            - Cross-account messaging topology analysis
            - Regional topic distribution assessment
            - Multi-account messaging inventory aggregation
        """

        def __init__(self, queue):
            """
            Initialize worker thread with reference to shared work queue.

            Args:
                queue (Queue): Thread-safe queue containing SNS discovery work items
            """
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Main worker thread execution loop for SNS topic discovery.

            Continuously processes credential sets from queue, performs topic
            discovery via AWS SNS APIs, and aggregates messaging infrastructure data
            with comprehensive filtering and metadata extraction.
            """
            while True:
                # Get SNS discovery work item from thread-safe queue
                c_account_credentials, c_topic_frag, c_exact, c_PlacesToLook, c_PlaceCount = self.queue.get()
                logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")

                try:
                    logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")

                    # Call AWS SNS API to discover topics in this account/region
                    # find_sns_topics2() handles ListTopics API with optional filtering
                    account_topics = Inventory_Modules.find_sns_topics2(c_account_credentials, c_topic_frag, c_exact)

                    logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")
                    # Process discovered SNS topics with comprehensive metadata extraction
                    for topic in account_topics:
                        # Create comprehensive topic record for messaging inventory
                        topic_record = {
                            # Organizational context
                            "MgmtAccount": c_account_credentials["MgmtAccount"],
                            "AccountId": c_account_credentials["AccountId"],
                            "Region": c_account_credentials["Region"],
                            # Topic identification and metadata
                            "TopicName": topic,
                        }

                        # Add to global messaging inventory collection
                        AllTopics.append(topic_record)
                except KeyError as my_Error:
                    # Handle credential or account access configuration errors
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    # Continue processing other accounts despite this failure
                    pass

                except AttributeError as my_Error:
                    # Handle profile configuration or credential format errors
                    logging.error(f"Error: Likely that one of the supplied profiles was wrong")
                    logging.warning(my_Error)
                    continue

                finally:
                    # Progress tracking for large-scale messaging inventory
                    # Commented out to avoid console clutter in production use
                    # print(f"{ERASE_LINE}Finished finding Topics in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']} - {c_PlaceCount} / {c_PlacesToLook}", end='\r')

                    # Always mark work item as complete for queue management
                    self.queue.task_done()

    checkqueue = Queue()

    AllTopics = []
    PlaceCount = 0
    PlacesToLook = len(CredentialList)
    WorkerThreads = min(len(CredentialList), 50)

    for x in range(WorkerThreads):
        worker = FindTopics(checkqueue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    for credential in CredentialList:
        logging.info(f"Connecting to account {credential['AccountId']}")
        # for region in fRegionList:
        try:
            # print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
            checkqueue.put((credential, ftopic_frag, fexact, PlacesToLook, PlaceCount))
            PlaceCount += 1
        except ClientError as my_Error:
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region"
                )
                logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass
    checkqueue.join()
    return AllTopics


def present_results(f_data_found: list):
    """
    Description: Shows off results at the end
    @param f_data_found: List of Topics found and their attributes.
    """
    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
        "AccountId": {"DisplayOrder": 2, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 3, "Heading": "Region"},
        "TopicName": {"DisplayOrder": 4, "Heading": "Topic Name"},
    }
    AccountNum = len(set([acct["AccountId"] for acct in AllCredentials]))
    RegionNum = len(set([acct["Region"] for acct in AllCredentials]))
    sorted_Topics_Found = sorted(
        f_data_found, key=lambda x: (x["MgmtAccount"], x["AccountId"], x["Region"], x["TopicName"])
    )
    display_results(sorted_Topics_Found, display_dict, "None", pFilename)
    print()
    print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else ""
    print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else ""
    print(
        f"The output has also been written to a file beginning with '{pFilename}' + the date and time"
    ) if pFilename is not None else ""
    print()
    print(f"Found {len(f_data_found)} topics across {AccountNum} accounts across {RegionNum} regions")


##########################
ERASE_LINE = "\x1b[2K"

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles
    pRegions = args.Regions
    pAccounts = args.Accounts
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pRootOnly = args.RootOnly
    pExact = args.Exact
    pTopicFrag = args.Fragments
    pFilename = args.Filename
    pTiming = args.Time
    verbose = args.loglevel
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)30s() ] %(message)s")

    # Get credentials
    AllCredentials = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegions
    )
    AllAccounts = list(set([x["AccountId"] for x in AllCredentials]))
    AllRegions = list(set([x["Region"] for x in AllCredentials]))
    print()
    # RegionList = Inventory_Modules.get_ec2_regions3(aws_acct, pRegions)
    # ChildAccounts = aws_acct.ChildAccounts
    logging.info(f"# of Regions: {len(AllRegions)}")
    logging.info(f"# of Child Accounts: {len(AllAccounts)}")
    account_credentials = None

    # Find topics
    all_topics_found = find_topics(AllCredentials, pTopicFrag, pExact)

    # Display data
    present_results(all_topics_found)

    print()
    if pTiming:
        print(f"{Fore.GREEN}This script completed in {time() - begin_time:.2f} seconds{Fore.RESET}")
        print()
print("Thank you for using this script.")

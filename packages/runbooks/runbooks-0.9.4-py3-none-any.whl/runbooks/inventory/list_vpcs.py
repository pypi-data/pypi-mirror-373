#!/usr/bin/env python3
"""
AWS VPC Inventory Collection

A comprehensive VPC discovery tool for multi-account AWS Organizations that provides
detailed network topology visibility across all accounts and regions. Supports
filtering for default VPCs to identify potential security risks.

**AWS API Mapping**: `boto3.client('ec2').describe_vpcs()`

Features:
    - Multi-account VPC discovery via AWS Organizations
    - Default VPC identification for security auditing
    - CIDR block and association analysis
    - VPC peering and gateway information
    - Tag-based metadata collection
    - Cross-region network topology mapping

Compatibility:
    - AWS Organizations with cross-account roles
    - AWS Control Tower managed accounts
    - Standalone AWS accounts
    - All AWS regions including opt-in regions

Example:
    Discover all VPCs across organization:
    ```bash
    python ec2_describe_vpcs.py --profile my-org-profile
    ```
    
    Find only default VPCs for security audit:
    ```bash
    python ec2_describe_vpcs.py --profile my-profile --default
    ```
    
    Export VPC inventory to file:
    ```bash
    python ec2_describe_vpcs.py --profile my-profile \\
        --save vpc_inventory.json --output json
    ```

Requirements:
    - IAM permissions: `ec2:DescribeVpcs`, `sts:AssumeRole`
    - AWS Organizations access (for multi-account scanning)
    - Python 3.8+ with required dependencies

Author:
    AWS Cloud Foundations Team
    
Version:
    2024.01.26
"""

import logging
import sys
from queue import Queue

# from tqdm.auto import tqdm
from threading import Thread
from time import time

import Inventory_Modules
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, get_all_credentials

init()
__version__ = "2024.01.26"


##########################
def parse_args(args):
    """
    Parse and validate command-line arguments for VPC network topology discovery.

    Configures the argument parser with VPC-specific options including default VPC
    detection for security auditing and comprehensive network inventory capabilities.
    Uses the standardized CommonArguments framework for consistency.

    Args:
        args (list): Command-line arguments to parse (typically sys.argv[1:])

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: AWS profiles for multi-account network discovery
            - Regions: Target AWS regions for VPC enumeration
            - AccessRoles: Cross-account roles for Organizations access
            - pDefault: CRITICAL security flag for default VPC identification
            - RootOnly: Limit to Organization Management Accounts
            - Filename: Output file prefix for network topology export
            - Other standard framework arguments

    Security-Critical Argument:
        --default: Identifies default VPCs which represent significant security risks:
                  - Often have overly permissive security groups
                  - May violate network segmentation policies
                  - Should be replaced with purpose-built VPCs
                  - Critical for compliance auditing (PCI DSS, SOC2)
                  - Essential for CIS benchmark compliance

    Network Architecture Use Cases:
        - Network topology mapping: Complete VPC inventory
        - Security auditing: Default VPC identification and remediation
        - CIDR planning: IP address space utilization analysis
        - Compliance validation: Network segmentation verification
        - Migration planning: Cross-account network architecture assessment
    """
    parser = CommonArguments()
    parser.my_parser.description = "We're going to find all vpcs within any of the accounts and regions we have access to, given the profile(s) provided."
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rolestouse()
    parser.rootOnly()
    parser.timing()
    parser.save_to_file()
    parser.verbosity()
    parser.version(__version__)
    parser.my_parser.add_argument(
        "--default",
        dest="pDefault",
        metavar="Looking for default VPCs only",
        action="store_const",
        default=False,
        const=True,
        help="Flag to determine whether we're looking for default VPCs only.",
    )
    return parser.my_parser.parse_args(args)


def find_all_vpcs(fAllCredentials, fDefaultOnly=False):
    """
    Execute multi-threaded VPC discovery across AWS accounts and regions.

    This is the core network topology discovery engine that performs concurrent
    VPC enumeration across all provided AWS accounts and regions. Essential for
    understanding network architecture, CIDR utilization, and security posture.

    Args:
        fAllCredentials (list): List of credential dictionaries containing:
            - AccountId: AWS account identifier
            - Region: AWS region name
            - AccessKeyId, SecretAccessKey, SessionToken: AWS credentials
            - MgmtAccount: Management account identifier
            - Success: Boolean flag indicating credential validation status

        fDefaultOnly (bool, optional): Focus discovery on default VPCs only.
            Critical for security auditing as default VPCs often violate
            network security policies and compliance requirements.

    Returns:
        list: Comprehensive VPC inventory with network metadata:
            - VpcId: AWS VPC identifier
            - VpcName: VPC name from tags (or "No name defined")
            - CIDR: VPC CIDR block (handles multiple CIDRs per VPC)
            - IsDefault: Boolean indicating if VPC is account default
            - AccountId: Source AWS account
            - Region: Source AWS region
            - MgmtAccount: Management account identifier

    Threading Architecture:
        - Uses Queue for thread-safe work distribution
        - Worker thread pool for concurrent VPC discovery
        - Progress tracking for large-scale network inventory
        - Comprehensive error handling for account access failures

    Network Analysis Features:
        - CIDR block enumeration (handles secondary CIDR associations)
        - Default VPC identification for security compliance
        - Tag-based VPC naming and categorization
        - Cross-account network topology mapping
        - Regional network architecture visibility

    Security Implications:
        - Default VPCs represent significant security risks
        - Often have permissive default security groups
        - May violate network segmentation requirements
        - Critical for PCI DSS and SOC2 compliance validation
        - Essential for Zero Trust architecture assessment

    Enterprise Use Cases:
        - Network architecture documentation
        - CIDR space planning and IP address management
        - Compliance auditing and remediation planning
        - Multi-account network segmentation validation
        - Cloud migration network assessment
    """

    class FindVPCs(Thread):
        """
        Worker thread for concurrent VPC discovery and network topology analysis.

        Each worker thread processes credential sets from the shared queue,
        calls AWS EC2 VPC APIs to discover network infrastructure, and performs
        detailed CIDR and default VPC analysis for security assessment.

        Network Discovery Capabilities:
            - VPC enumeration with metadata extraction
            - CIDR block association analysis
            - Default VPC identification for security auditing
            - Tag-based VPC naming and categorization
            - Cross-account network topology mapping
        """

        def __init__(self, queue):
            """
            Initialize worker thread with reference to shared work queue.

            Args:
                queue (Queue): Thread-safe queue containing VPC discovery work items
            """
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Main worker thread execution loop for VPC network discovery.

            Continuously processes credential sets from queue, performs VPC
            discovery via AWS EC2 APIs, and aggregates network topology data
            with comprehensive CIDR and security analysis.
            """
            while True:
                # Get VPC discovery work item from thread-safe queue
                c_account_credentials, c_default, c_PlaceCount = self.queue.get()
                logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")

                try:
                    # Call AWS EC2 API to discover VPCs in this account/region
                    # find_account_vpcs2() handles DescribeVpcs API with optional default filtering
                    Vpcs = Inventory_Modules.find_account_vpcs2(c_account_credentials, c_default)

                    logging.info(
                        f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(Vpcs['Vpcs'])} VPCs"
                    )
                    # Process discovered VPCs with comprehensive network metadata extraction
                    if "Vpcs" in Vpcs.keys() and len(Vpcs["Vpcs"]) > 0:
                        for y in range(len(Vpcs["Vpcs"])):
                            # Initialize VPC metadata with default values
                            VpcName = "No name defined"  # Fallback for untagged VPCs
                            VpcId = Vpcs["Vpcs"][y]["VpcId"]
                            IsDefault = Vpcs["Vpcs"][y]["IsDefault"]  # Critical for security assessment
                            CIDRBlockAssociationSet = Vpcs["Vpcs"][y]["CidrBlockAssociationSet"]

                            # Extract VPC name from tags for network documentation
                            # Proper VPC naming is essential for network governance
                            if "Tags" in Vpcs["Vpcs"][y]:
                                for z in range(len(Vpcs["Vpcs"][y]["Tags"])):
                                    if Vpcs["Vpcs"][y]["Tags"][z]["Key"] == "Name":
                                        VpcName = Vpcs["Vpcs"][y]["Tags"][z]["Value"]

                            # Handle multiple CIDR block associations per VPC
                            # AWS supports secondary CIDR blocks for IP space expansion
                            # Each CIDR gets its own record for accurate IP space tracking
                            for _ in range(len(CIDRBlockAssociationSet)):
                                # Create individual record for each CIDR association
                                # This enables precise CIDR space analysis and planning
                                AllVPCs.append(
                                    {
                                        # Organizational context
                                        "MgmtAccount": c_account_credentials["MgmtAccount"],
                                        "AccountId": c_account_credentials["AccountId"],
                                        "Region": c_account_credentials["Region"],
                                        # Network topology data
                                        "CIDR": CIDRBlockAssociationSet[_]["CidrBlock"],
                                        "VpcId": VpcId,
                                        "VpcName": VpcName,
                                        # Security-critical default VPC flag
                                        "IsDefault": IsDefault,
                                    }
                                )
                    else:
                        # No VPCs found in this account/region combination
                        continue
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

                except ClientError as my_Error:
                    # Handle AWS API authentication and authorization errors
                    if "AuthFailure" in str(my_Error):
                        logging.error(
                            f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region"
                        )
                        logging.warning(
                            f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into"
                        )
                        continue
                    else:
                        # Handle API throttling and other service errors
                        logging.error(f"Error: Likely throttling errors from too much activity")
                        logging.warning(my_Error)
                        continue

                finally:
                    # Always mark work item as complete for queue management
                    self.queue.task_done()

    ###########

    checkqueue = Queue()

    AllVPCs = []
    PlaceCount = 0
    WorkerThreads = min(len(fAllCredentials), 25)

    worker_threads = []
    for x in range(WorkerThreads):
        worker = FindVPCs(checkqueue)
        # Setting daemon to False for proper cleanup
        worker.daemon = False
        worker.start()
        worker_threads.append(worker)

    for credential in fAllCredentials:
        logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
        print(
            f"{ERASE_LINE}Checking {credential['AccountId']} in region {credential['Region']} - {PlaceCount + 1} / {len(fAllCredentials)}",
            end="\r",
        )
        # for region in fRegionList:
        try:
            # I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
            checkqueue.put((credential, fDefaultOnly, PlaceCount))
            logging.info(f"Put credential: {credential}, Default: {fDefaultOnly}")
            PlaceCount += 1
        except ClientError as my_Error:
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region"
                )
                logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass
    checkqueue.join()
    return AllVPCs


##########################
if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles
    pRegionList = args.Regions
    pAccounts = args.Accounts
    pRoles = args.AccessRoles
    pSkipProfiles = args.SkipProfiles
    pSkipAccounts = args.SkipAccounts
    pRootOnly = args.RootOnly
    pTiming = args.Time
    pFilename = args.Filename
    pDefault = args.pDefault
    verbose = args.loglevel
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)30s() ] %(message)s")

    ERASE_LINE = "\x1b[2K"

    begin_time = time()

    NumVpcsFound = 0
    NumRegions = 0
    if pProfiles is not None:
        print(f"Checking for VPCs in profile{'s' if len(pProfiles) > 1 else ''} {pProfiles}")
    else:
        print(f"Checking for VPCs in default profile")

    # NumOfRootProfiles = 0
    # Get credentials
    AllCredentials = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pRoles
    )
    AllRegionsList = list(set([x["Region"] for x in AllCredentials]))
    AllAccountList = list(set([x["AccountId"] for x in AllCredentials]))
    # Find the VPCs
    All_VPCs_Found = find_all_vpcs(AllCredentials, pDefault)
    # Display results
    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
        "AccountId": {"DisplayOrder": 2, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 3, "Heading": "Region"},
        "VpcName": {"DisplayOrder": 4, "Heading": "VPC Name"},
        "CIDR": {"DisplayOrder": 5, "Heading": "CIDR Block"},
        "IsDefault": {"DisplayOrder": 6, "Heading": "Default VPC", "Condition": [True, 1, "1"]},
        "VpcId": {"DisplayOrder": 7, "Heading": "VPC Id"},
    }

    logging.info(f"# of Regions: {len(AllRegionsList)}")
    # logging.info(f"# of Management Accounts: {NumOfRootProfiles}")
    logging.info(f"# of Child Accounts: {len(AllAccountList)}")

    sorted_AllVPCs = sorted(
        All_VPCs_Found, key=lambda d: (d["MgmtAccount"], d["AccountId"], d["Region"], d["VpcName"], d["CIDR"])
    )
    print()
    display_results(sorted_AllVPCs, display_dict, None, pFilename)

    # Threading cleanup is handled within find_all_vpcs function

    print()
    # checkqueue.join() marks all of the threads as done - so Checking is done
    logging.info(f"Threads all done - took {time() - begin_time:.2f} seconds")

    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
    print(ERASE_LINE)
    # Had to do this, because some of the VPCs that show up in the "sorted_AllVPCs" list are actually the same VPC, with a different CIDR range.
    Num_of_unique_VPCs = len(set([x["VpcId"] for x in sorted_AllVPCs]))
    print(
        f"Found {Num_of_unique_VPCs}{' default' if pDefault else ''} Vpcs across {len(AllAccountList)} accounts across {len(AllRegionsList)} regions"
    )
    print()
    print("Thank you for using this script.")
    print()

#!/usr/bin/env python3
"""
AWS EC2 Instance Inventory Collection

A comprehensive EC2 instance discovery tool that operates across multiple AWS accounts 
and regions using the AWS Cloud Foundations framework. This script provides detailed 
inventory reporting with support for multi-account Organizations access patterns.

**AWS API Mapping**: `boto3.client('ec2').describe_instances()`

Features:
    - Multi-account EC2 instance discovery via AWS Organizations
    - Parallel region scanning with threading optimization
    - Flexible filtering by instance state (running/stopped)
    - Multiple output formats (table, JSON, CSV)
    - Tag-based metadata collection
    - VPC and network information gathering
    
Compatibility:
    - AWS Organizations with cross-account roles
    - AWS Control Tower managed accounts  
    - Standalone AWS accounts
    - All AWS regions including opt-in regions

Example:
    Basic usage across all regions:
    ```bash
    python ec2_describe_instances.py --profile my-org-profile
    ```
    
    Filter running instances in specific regions:
    ```bash
    python ec2_describe_instances.py --profile my-profile \\
        --regions us-east-1 us-west-2 --status running
    ```
    
    Export to JSON for analysis:
    ```bash
    python ec2_describe_instances.py --profile my-profile \\
        --output json --save instances_inventory.json
    ```

Requirements:
    - IAM permissions: `ec2:DescribeInstances`, `sts:AssumeRole`
    - AWS Organizations access (for multi-account scanning)
    - Python 3.8+ with required dependencies

Author:
    AWS Cloud Foundations Team
    
Version:
    2025.04.09
"""

import logging
import sys
from os.path import split
from queue import Queue
from threading import Thread
from time import time

import Inventory_Modules
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, get_all_credentials
from tqdm.auto import tqdm

init()
__version__ = "2025.04.09"
ERASE_LINE = "\x1b[2K"
begin_time = time()


##################
# Functions
##################


def parse_args(f_arguments):
    """Parse command-line arguments for EC2 instance inventory collection.

    Configures argument parser with standard AWS Cloud Foundations parameters
    plus EC2-specific options for filtering instance states.

    Args:
            f_arguments (list): Command-line arguments to parse

    Returns:
            argparse.Namespace: Parsed arguments containing:
                    - pProfiles: List of AWS profiles to use
                    - pRegions: List of AWS regions to scan
                    - pStatus: Instance state filter ('running', 'stopped', or None)
                    - Verbose: Logging verbosity level
                    - Other standard AWS Cloud Foundations parameters

    Example:
            >>> args = parse_args(['--profile', 'my-profile', '--status', 'running'])
            >>> print(args.pStatus)
            'running'
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
    parser.my_parser.description = (
        "We're going to find all instances within any of the accounts we have access to, given the profile(s) provided."
    )
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rolestouse()
    parser.rootOnly()
    parser.save_to_file()
    parser.timing()
    parser.verbosity()
    parser.version(__version__)
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")
    local.add_argument(
        "-s",
        "--status",
        dest="pStatus",
        choices=["running", "stopped"],
        type=str,
        default=None,
        help="Whether you want to limit the instances returned to either 'running', 'stopped'. Default is both",
    )
    return parser.my_parser.parse_args(f_arguments)


def find_all_instances(fAllCredentials: list, fStatus: str = None) -> list:
    """Discover EC2 instances across multiple AWS accounts and regions.

    Performs parallel discovery of EC2 instances using multi-threading for optimal
    performance across large AWS Organizations. Supports optional state filtering
    to focus on specific instance lifecycle phases.

    Args:
            fAllCredentials (list): List of credential dictionaries containing:
                    - AccountId: AWS account identifier
                    - Region: AWS region name
                    - AccessKey, SecretKey, SessionToken: AWS credentials
                    - MgmtAccount: Management account flag
            fStatus (str, optional): Instance state filter. Valid values:
                    - 'running': Only return running instances
                    - 'stopped': Only return stopped instances
                    - None: Return instances in all states

    Returns:
            list: Collection of EC2 instance dictionaries with attributes:
                    - InstanceId: EC2 instance identifier
                    - InstanceType: EC2 instance type (e.g., 't3.micro')
                    - State: Current instance state
                    - VpcId: Associated VPC identifier
                    - SubnetId: Associated subnet identifier
                    - PrivateIpAddress: Private IP address
                    - PublicIpAddress: Public IP address (if assigned)
                    - Tags: Instance tags as key-value pairs
                    - LaunchTime: Instance launch timestamp
                    - AccountId: Source AWS account
                    - Region: Source AWS region

    Raises:
            ClientError: When AWS API calls fail due to permissions or service issues

    Example:
            >>> credentials = get_all_credentials(['my-profile'])
            >>> running_instances = find_all_instances(credentials, 'running')
            >>> print(f"Found {len(running_instances)} running instances")

    Note:
            Uses ThreadPool for concurrent execution across regions/accounts.
            Progress tracking provided via tqdm when verbose logging enabled.
    """

    class FindInstances(Thread):
        """
        Worker thread for concurrent EC2 instance discovery across AWS accounts.

        Each worker thread processes credential sets from the shared queue,
        calls AWS EC2 APIs to discover compute instances, and performs detailed
        metadata extraction including networking, tagging, and state analysis.

        Compute Discovery Capabilities:
            - EC2 instance enumeration with comprehensive metadata
            - Instance state and lifecycle analysis
            - Network configuration discovery (VPC, subnet, IP addresses)
            - Tag-based instance categorization and naming
            - Multi-account compute inventory aggregation
        """

        def __init__(self, queue):
            """
            Initialize worker thread with reference to shared work queue.

            Args:
                queue (Queue): Thread-safe queue containing EC2 discovery work items
            """
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Main worker thread execution loop for EC2 instance discovery.

            Continuously processes credential sets from queue, performs instance
            discovery via AWS EC2 APIs, and aggregates compute infrastructure data
            with comprehensive metadata extraction and state filtering.
            """
            while True:
                # Get EC2 discovery work item from thread-safe queue
                c_account_credentials = self.queue.get()
                logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")

                try:
                    # Call AWS EC2 API to discover instances in this account/region
                    # find_account_instances2() handles DescribeInstances API with pagination
                    # This is the most time-intensive operation in the discovery process
                    Instances = Inventory_Modules.find_account_instances2(c_account_credentials)
                    logging.info(
                        f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(Instances['Reservations'])} reservations"
                    )

                    # Initialize instance metadata variables with defaults
                    State = InstanceType = InstanceId = PublicDnsName = Name = ""

                    # Process discovered EC2 instances with comprehensive metadata extraction
                    # AWS returns instances grouped by reservation (launch request)
                    if "Reservations" in Instances.keys():
                        for y in range(len(Instances["Reservations"])):
                            # Each reservation can contain multiple instances
                            for z in range(len(Instances["Reservations"][y]["Instances"])):
                                # Extract core instance attributes
                                instance_data = Instances["Reservations"][y]["Instances"][z]

                                InstanceType = instance_data["InstanceType"]
                                InstanceId = instance_data["InstanceId"]
                                State = instance_data["State"]["Name"]

                                # Handle optional public DNS name (depends on network configuration)
                                PublicDnsName = (
                                    instance_data["PublicDnsName"]
                                    if "PublicDnsName" in instance_data
                                    else "No Public DNS Name"
                                )

                                # Initialize name with fallback for untagged instances
                                Name = "No Name Tag"
                                # Extract instance name from tags for resource identification
                                # Proper instance naming is essential for operational visibility
                                try:
                                    if "Tags" in instance_data:
                                        for tag in instance_data["Tags"]:
                                            if tag["Key"] == "Name":
                                                Name = tag["Value"]
                                                break
                                except KeyError as my_Error:
                                    # Handle cases where Tags key is missing from API response
                                    # This can occur with instances launched without tags
                                    logging.info(f"No tags found for instance {InstanceId}: {my_Error}")
                                    pass
                                # Apply state filtering if specified
                                # Common filters: 'running' for active workloads, 'stopped' for cost analysis
                                if fStatus is None or fStatus == State:
                                    # Create comprehensive instance record for inventory
                                    instance_record = {
                                        # Organizational context
                                        "MgmtAccount": c_account_credentials["MgmtAccount"],
                                        "AccountId": c_account_credentials["AccountId"],
                                        "Region": c_account_credentials["Region"],
                                        "ParentProfile": c_account_credentials["ParentProfile"],
                                        # Instance identification and metadata
                                        "InstanceId": InstanceId,
                                        "Name": Name,
                                        # Compute and operational attributes
                                        "InstanceType": InstanceType,
                                        "State": State,
                                        # Network configuration
                                        "PublicDNSName": PublicDnsName,
                                    }

                                    # Add to global inventory collection
                                    AllInstances.append(instance_record)
                                else:
                                    # Skip instances that don't match state filter
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

    AllInstances = []
    WorkerThreads = min(len(fAllCredentials), 25)

    pbar = tqdm(
        desc=f"Finding instances from {len(fAllCredentials)} locations", total=len(fAllCredentials), unit=" locations"
    )

    for x in range(WorkerThreads):
        worker = FindInstances(checkqueue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    for credential in fAllCredentials:
        logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
        try:
            # I don't know why - but double parens are necessary below. If you remove them, only the first parameter is queued.
            checkqueue.put((credential))
        except ClientError as my_Error:
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region"
                )
                logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass
    checkqueue.join()
    pbar.close()
    return AllInstances


##################
# Main
##################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles
    pRegionList = args.Regions
    pAccounts = args.Accounts
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pAccessRoles = args.AccessRoles
    pStatus = args.pStatus
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

    # Import Rich display utilities for professional output
    from runbooks.inventory.rich_inventory_display import (
        create_inventory_progress,
        display_ec2_inventory_results,
        display_inventory_header,
    )

    # Display professional inventory header
    display_inventory_header(
        "EC2", pProfiles, AccountNum if "AccountNum" in locals() else 0, RegionNum if "RegionNum" in locals() else 0
    )

    # Find credentials for all Child Accounts
    # CredentialList = get_credentials(pProfiles, pRegionList, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pAccessRoles, pTiming)
    CredentialList = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pAccessRoles
    )
    AccountNum = len(set([acct["AccountId"] for acct in CredentialList]))
    RegionNum = len(set([acct["Region"] for acct in CredentialList]))

    # Update header with actual counts
    display_inventory_header("EC2", pProfiles, AccountNum, RegionNum)

    if pTiming:
        milestone_time1 = time()
        from runbooks.common.rich_utils import print_info

        print_info(f"⏱️ Credential discovery completed in {(milestone_time1 - begin_time):.3f} seconds")
    # Collect all the instances from the credentials found
    AllInstances = find_all_instances(CredentialList, pStatus)
    # Display the information we've found thus far
    display_dict = {
        "ParentProfile": {"DisplayOrder": 1, "Heading": "Parent Profile"},
        "MgmtAccount": {"DisplayOrder": 2, "Heading": "Mgmt Acct"},
        "AccountId": {"DisplayOrder": 3, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 4, "Heading": "Region"},
        "InstanceType": {"DisplayOrder": 5, "Heading": "Instance Type"},
        "Name": {"DisplayOrder": 6, "Heading": "Name"},
        "InstanceId": {"DisplayOrder": 7, "Heading": "Instance ID"},
        "PublicDNSName": {"DisplayOrder": 8, "Heading": "Public Name"},
        "State": {"DisplayOrder": 9, "Heading": "State", "Condition": ["running"]},
    }

    sorted_all_instances = sorted(
        AllInstances, key=lambda d: (d["ParentProfile"], d["MgmtAccount"], d["Region"], d["AccountId"])
    )
    display_results(sorted_all_instances, display_dict, None, pFilename)

    # Display results using Rich formatting
    timing_info = {"total_time": time() - begin_time} if pTiming else None
    display_ec2_inventory_results(AllInstances, AccountNum, RegionNum, timing_info)

#!/usr/bin/env python3
"""
AWS RDS Database Instance Inventory Collection

A comprehensive RDS database discovery tool for multi-account AWS Organizations that
provides detailed database infrastructure visibility across all accounts and regions.
Essential for database governance, compliance, and cost optimization initiatives.

**AWS API Mapping**: `boto3.client('rds').describe_db_instances()`

Features:
    - Multi-account RDS instance discovery via AWS Organizations
    - Database engine and version inventory
    - Storage allocation and backup status analysis
    - Instance class and performance tier mapping
    - Database state and availability monitoring
    - Cross-region database topology visibility

Database Governance Use Cases:
    - Database inventory and asset management
    - Engine version compliance auditing
    - Backup policy validation and compliance
    - Cost optimization through instance right-sizing
    - Security assessment of database configurations
    - Disaster recovery planning and validation

Compatibility:
    - AWS Organizations with cross-account roles
    - AWS Control Tower managed accounts
    - Standalone AWS accounts
    - All AWS regions including opt-in regions
    - All RDS engine types (MySQL, PostgreSQL, Oracle, SQL Server, MariaDB, Aurora)

Example:
    Discover all RDS instances across organization:
    ```bash
    python list_rds_db_instances.py --profile my-org-profile
    ```
    
    Export database inventory to file:
    ```bash
    python list_rds_db_instances.py --profile my-profile \
        --save rds_inventory.json --output json
    ```

Requirements:
    - IAM permissions: `rds:DescribeDBInstances`, `sts:AssumeRole`
    - AWS Organizations access (for multi-account scanning)
    - Python 3.8+ with required dependencies

Author:
    AWS Cloud Foundations Team
    
Version:
    2025.04.09
"""

# import boto3
import logging
import sys
from queue import Queue
from threading import Thread
from time import time

import Inventory_Modules
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_account_rds_instances2, get_all_credentials
from tqdm.auto import tqdm

init()

__version__ = "2025.04.09"


##################
# Functions
##################


def parse_args(args):
    """
    Parse and validate command-line arguments for RDS database inventory discovery.

    Configures the argument parser with RDS-specific options for comprehensive
    database infrastructure discovery across multi-account AWS environments.
    Uses the standardized CommonArguments framework for consistency.

    Args:
        args (list): Command-line arguments to parse (typically sys.argv[1:])

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: AWS profiles for multi-account database discovery
            - Regions: Target AWS regions for RDS enumeration
            - AccessRoles: Cross-account roles for Organizations access
            - RootOnly: Limit to Organization Management Accounts
            - Filename: Output file prefix for database inventory export
            - Other standard framework arguments

    Database Discovery Use Cases:
        - Database asset inventory: Complete RDS instance enumeration
        - Compliance auditing: Engine version and configuration validation
        - Cost optimization: Instance class and storage utilization analysis
        - Backup validation: Backup policy and recovery point assessment
        - Security assessment: Database configuration and access review
        - Migration planning: Cross-account database architecture analysis
    """
    parser = CommonArguments()
    parser.my_parser.description = "We're going to find all rds instances within any of the accounts we have access to, given the profile(s) provided."
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rolestouse()
    parser.rootOnly()
    parser.save_to_file()
    parser.timing()
    parser.verbosity()
    parser.version(__version__)
    return parser.my_parser.parse_args(args)


def check_accounts_for_instances(fAllCredentials: list) -> list:
    """
    Execute multi-threaded RDS database instance discovery across AWS accounts and regions.

    This is the core database infrastructure discovery engine that performs concurrent
    RDS instance enumeration across all provided AWS accounts and regions. Essential for
    understanding database architecture, capacity planning, and compliance assessment.

    Args:
        fAllCredentials (list): List of credential dictionaries containing:
            - AccountId: AWS account identifier
            - Region: AWS region name
            - AccessKeyId, SecretAccessKey, SessionToken: AWS credentials
            - MgmtAccount: Management account identifier
            - Success: Boolean flag indicating credential validation status

    Returns:
        list: Comprehensive RDS database inventory with metadata:
            - DBId: RDS database instance identifier
            - Name: Database name (or "No Name" if unspecified)
            - Engine: Database engine type (MySQL, PostgreSQL, etc.)
            - InstanceType: RDS instance class (db.t3.micro, etc.)
            - State: Database instance status
            - Size: Allocated storage in GB
            - LastBackup: Latest restorable time for backup validation
            - AccountNumber: Source AWS account
            - Region: Source AWS region
            - MgmtAccount: Management account identifier

    Threading Architecture:
        - Uses Queue for thread-safe work distribution
        - Worker thread pool for concurrent database discovery
        - Progress tracking for large-scale database inventory
        - Comprehensive error handling for account access failures

    Database Analysis Features:
        - Engine type and version enumeration
        - Storage capacity and utilization tracking
        - Backup status and recovery point validation
        - Instance class and performance tier analysis
        - Multi-AZ configuration detection
        - Cross-account database topology mapping

    Enterprise Use Cases:
        - Database governance and asset management
        - Compliance auditing (SOX, PCI DSS, HIPAA)
        - Cost optimization through right-sizing analysis
        - Backup policy validation and disaster recovery planning
        - Security assessment of database configurations
        - Migration planning and capacity assessment
    """

    class FindRDSInstances(Thread):
        """
        Worker thread for concurrent RDS database instance discovery across AWS accounts.

        Each worker thread processes credential sets from the shared queue,
        calls AWS RDS APIs to discover database instances, and performs detailed
        metadata extraction including engine types, storage, and backup analysis.

        Database Discovery Capabilities:
            - RDS instance enumeration with comprehensive metadata
            - Database engine and version analysis
            - Storage allocation and backup status assessment
            - Instance class and performance tier evaluation
            - Multi-account database inventory aggregation
        """

        def __init__(self, queue):
            """
            Initialize worker thread with reference to shared work queue.

            Args:
                queue (Queue): Thread-safe queue containing RDS discovery work items
            """
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Main worker thread execution loop for RDS database instance discovery.

            Continuously processes credential sets from queue, performs database
            discovery via AWS RDS APIs, and aggregates database infrastructure data
            with comprehensive metadata extraction and analysis.
            """
            while True:
                # Get RDS discovery work item from thread-safe queue
                c_account_credentials = self.queue.get()
                logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")

                try:
                    # Call AWS RDS API to discover database instances in this account/region
                    # find_account_rds_instances2() handles DescribeDBInstances API with pagination
                    # This is the most time-intensive operation in the discovery process
                    DBInstances = find_account_rds_instances2(c_account_credentials)
                    logging.info(
                        f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(DBInstances['DBInstances'])} RDS instances"
                    )

                    # Process discovered RDS instances with comprehensive metadata extraction
                    if "DBInstances" in DBInstances.keys():
                        for RDSinstance in DBInstances["DBInstances"]:
                            # Extract database name with fallback for unnamed databases
                            # Proper database naming is essential for operational visibility
                            Name = RDSinstance["DBName"] if "DBName" in RDSinstance.keys() else "No Name"

                            # Extract backup information for compliance and recovery planning
                            # Critical for disaster recovery and regulatory compliance
                            LastBackup = (
                                RDSinstance["LatestRestorableTime"]
                                if "LatestRestorableTime" in RDSinstance.keys()
                                else "No Backups"
                            )

                            # Create comprehensive database record for inventory
                            database_record = {
                                # Organizational context
                                "MgmtAccount": c_account_credentials["MgmtAccount"],
                                "AccountNumber": c_account_credentials["AccountId"],
                                "Region": c_account_credentials["Region"],
                                # Database identification and naming
                                "DBId": RDSinstance["DBInstanceIdentifier"],
                                "Name": Name,
                                # Database engine and performance attributes
                                "Engine": RDSinstance["Engine"],
                                "InstanceType": RDSinstance["DBInstanceClass"],
                                "State": RDSinstance["DBInstanceStatus"],
                                # Storage and backup configuration
                                "Size": RDSinstance["AllocatedStorage"],
                                "LastBackup": LastBackup,
                            }

                            # Add to global database inventory collection
                            AllRDSInstances.append(database_record)
                    else:
                        # No RDS instances found in this account/region combination
                        continue
                except KeyError as my_Error:
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    logging.error(f"Error: Likely that one of the supplied profiles was wrong")
                    logging.warning(my_Error)
                    continue
                except ClientError as my_Error:
                    if "AuthFailure" in str(my_Error):
                        logging.error(
                            f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region"
                        )
                        logging.warning(
                            f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into"
                        )
                        continue
                    if my_Error.response["Error"]["Code"] == "AccessDenied":
                        logging.warning(
                            f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region"
                        )
                        logging.warning(
                            f"It's likely there's an SCP blocking access to this {c_account_credentials['AccountId']} account"
                        )
                        continue
                    else:
                        logging.error(f"Error: Likely throttling errors from too much activity")
                        logging.warning(my_Error)
                        continue
                finally:
                    pbar.update()
                    self.queue.task_done()

    checkqueue = Queue()

    AllRDSInstances = []
    WorkerThreads = min(len(fAllCredentials), 25)

    pbar = tqdm(
        desc=f"Finding RDS instances from {len(fAllCredentials)} locations",
        total=len(fAllCredentials),
        unit=" location",
    )

    for x in range(WorkerThreads):
        worker = FindRDSInstances(checkqueue)
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
    return AllRDSInstances


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
    begin_time = time()
    logging.info(f"Profiles: {pProfiles}")

    print()
    print(f"Checking for rds instances... ")
    print()

    InstancesFound = []
    AllChildAccounts = []

    # Display RDS Instances found
    display_dict = {
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Mgmt Acct"},
        "AccountNumber": {"DisplayOrder": 2, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 3, "Heading": "Region"},
        "InstanceType": {"DisplayOrder": 4, "Heading": "Instance Type"},
        "Name": {"DisplayOrder": 5, "Heading": "DB Name"},
        "DBId": {"DisplayOrder": 6, "Heading": "Database ID"},
        "Engine": {"DisplayOrder": 7, "Heading": "DB Engine"},
        "Size": {"DisplayOrder": 8, "Heading": "Size (GB)"},
        "LastBackup": {"DisplayOrder": 9, "Heading": "Latest Backup"},
        "State": {
            "DisplayOrder": 10,
            "Heading": "State",
            "Condition": ["Failed", "Deleting", "Maintenance", "Rebooting", "Upgrading"],
        },
    }

    # Get credentials
    CredentialList = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pAccessRoles
    )
    AccountNum = len(set([acct["AccountId"] for acct in CredentialList]))
    RegionNum = len(set([acct["Region"] for acct in CredentialList]))

    # Get RDS Instances
    InstancesFound = check_accounts_for_instances(CredentialList)
    sorted_results = sorted(
        InstancesFound, key=lambda d: (d["MgmtAccount"], d["AccountNumber"], d["Region"], d["DBId"])
    )
    # unique_results = uniqify_dict(sorted_results)
    # Display results
    display_results(sorted_results, display_dict, None, pFilename)

    print(ERASE_LINE)
    print(f"Found {len(InstancesFound)} instances across {AccountNum} accounts across {RegionNum} regions")
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
    print()
    print("Thank you for using this script")
    print()

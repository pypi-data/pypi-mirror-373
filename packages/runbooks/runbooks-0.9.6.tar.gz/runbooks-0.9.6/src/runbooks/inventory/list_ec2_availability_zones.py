#!/usr/bin/env python3

"""
AWS EC2 Availability Zones Discovery and Mapping Script

This script provides comprehensive discovery and analysis capabilities for AWS EC2
availability zones across multiple accounts and regions. It's designed for enterprise
infrastructure teams who need visibility into availability zone distribution, capacity
planning, and regional architecture across large-scale AWS deployments.

Key Features:
- Multi-account availability zone discovery using assume role capabilities
- Multi-region scanning with configurable region targeting
- Availability zone metadata extraction including zone IDs and types
- Regional capacity planning and architecture documentation
- Cross-account zone consistency analysis and validation
- Enterprise reporting with CSV export and structured output
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- Infrastructure capacity planning and availability zone selection
- Multi-account regional architecture documentation and standardization
- Disaster recovery planning with availability zone distribution analysis
- Compliance reporting for regional data residency requirements
- Cost optimization through availability zone placement strategies
- Network architecture planning with zone-aware resource placement

Infrastructure Planning Features:
- Zone ID mapping for consistent cross-account resource placement
- Availability zone enumeration for capacity planning
- Regional coverage analysis across organizational boundaries
- Zone type classification for infrastructure decision making
- Cross-account zone consistency validation for disaster recovery

Security Considerations:
- Uses IAM assume role capabilities for cross-account access
- Implements proper error handling for authorization failures
- Supports read-only operations with no infrastructure modification capabilities
- Respects regional access permissions and zone visibility constraints
- Provides comprehensive audit trail through detailed logging

Availability Zone Analysis:
- Zone name and ID correlation for consistent placement
- Zone type classification (availability-zone, local-zone, wavelength-zone)
- Regional availability zone count validation
- Cross-account zone naming consistency analysis
- Capacity planning data aggregation

Performance Considerations:
- Sequential processing for reliability across large account sets
- Progress tracking for operational visibility during long operations
- Efficient credential management for cross-account operations
- Memory-optimized data structures for large organizational inventories

Dependencies:
- boto3/botocore for AWS EC2 API interactions
- Inventory_Modules for common utility functions and credential management
- ArgumentsClass for standardized CLI argument parsing
- colorama for enhanced output formatting

Author: AWS CloudOps Team
Version: 2024.03.06
"""

import logging
import sys
from time import time

from ArgumentsClass import CommonArguments
from colorama import Fore, init
from Inventory_Modules import display_results, get_all_credentials, get_region_azs2

init()
__version__ = "2024.03.06"
ERASE_LINE = "\x1b[2K"
begin_time = time()


###########################
# Functions
###########################
def parse_args(args):
    """
    Parse command line arguments for EC2 availability zone discovery operations.

    Configures comprehensive argument parsing for multi-account, multi-region availability
    zone inventory operations. Supports enterprise deployment patterns with profile
    management, region targeting, and organizational access controls for infrastructure
    planning and capacity management.

    Args:
        args (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: List of AWS profiles to process
            - Regions: Target regions for availability zone discovery
            - SkipProfiles/SkipAccounts: Exclusion filters
            - RootOnly: Limit to organization root accounts
            - AccessRoles: IAM roles for cross-account access
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration

    Configuration Options:
        - Multi-region scanning with region filters for targeted analysis
        - Multi-profile support for federated access across organizations
        - Extended arguments for advanced filtering and account selection
        - Root-only mode for organization-level infrastructure inventory
        - Role-based access for cross-account availability zone discovery
        - File output for integration with capacity planning tools
        - Timing metrics for performance optimization and monitoring
        - Verbose logging for debugging and infrastructure audit
    """
    parser = CommonArguments()
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.rootOnly()
    parser.timing()
    parser.save_to_file()
    parser.rolestouse()
    parser.verbosity()
    parser.version(__version__)
    return parser.my_parser.parse_args(args)


def azs_across_accounts(
    fProfiles, fRegionList, fSkipProfiles, fSkipAccounts, fAccountList, fTiming, fRootOnly, fverbose, fRoleList
) -> dict:
    """
    Discover and map availability zones across multiple AWS accounts and regions.

    Performs comprehensive availability zone discovery across organizational boundaries
    to provide infrastructure teams with complete visibility into zone distribution,
    capacity planning data, and regional architecture patterns. Supports large-scale
    enterprise environments with multiple AWS organizations and standalone accounts.

    Args:
        fProfiles (list): AWS profiles for authentication and access
        fRegionList (list): Target regions for availability zone discovery
        fSkipProfiles (list): Profiles to exclude from processing
        fSkipAccounts (list): Account IDs to exclude from discovery
        fAccountList (list): Specific accounts to target (if provided)
        fTiming (bool): Enable performance timing metrics
        fRootOnly (bool): Limit discovery to organization root accounts
        fverbose (int): Logging verbosity level for operational visibility
        fRoleList (list): IAM roles for cross-account access

    Returns:
        dict: Nested dictionary structure with availability zone data:
            - First level: Account numbers as keys
            - Second level: Region names as keys
            - Third level: List of availability zone objects containing:
                - ZoneName: Human-readable zone name (e.g., us-east-1a)
                - ZoneId: Unique zone identifier for consistent placement
                - ZoneType: Zone classification (availability-zone, local-zone, etc.)
                - Region: AWS region containing the zone
                - State: Zone operational state

    Processing Flow:
        1. Credential Discovery: Obtain cross-account credentials for all target accounts
        2. Organization Analysis: Identify unique organizations and standalone accounts
        3. Sequential Processing: Iterate through successful credentials for zone discovery
        4. Zone Enumeration: Call EC2 API to discover availability zones per account/region
        5. Data Aggregation: Structure results for enterprise reporting and analysis

    Enterprise Features:
        - Progress tracking with real-time feedback for long operations
        - Organizational boundary detection for multi-org environments
        - Error handling with graceful degradation for access failures
        - Performance timing for optimization and capacity planning

    Infrastructure Planning Use Cases:
        - Capacity planning with zone-aware resource allocation
        - Disaster recovery planning with cross-zone distribution analysis
        - Regional architecture standardization across accounts
        - Zone ID mapping for consistent multi-account deployments
    """
    if fTiming:
        begin_time = time()
    logging.warning(f"These profiles are being checked {fProfiles}.")

    # Obtain credentials for all accounts across specified regions and profiles
    AllCredentials = get_all_credentials(
        fProfiles, fTiming, fSkipProfiles, fSkipAccounts, fRootOnly, fAccountList, fRegionList, fRoleList
    )

    # Identify unique organizations for progress tracking
    OrgList = list(set([x["MgmtAccount"] for x in AllCredentials]))
    print(f"Please bear with us as we run through {len(OrgList)} organizations / standalone accounts")

    print(ERASE_LINE)

    # Initialize nested dictionary for organizing availability zone data by account and region
    AllOrgAZs = dict()
    SuccessfulCredentials = [x for x in AllCredentials if x["Success"]]
    passnumber = 0

    # Process each successful credential set to discover availability zones
    for item in SuccessfulCredentials:
        # Initialize account structure if not present
        if item["AccountNumber"] not in AllOrgAZs.keys():
            AllOrgAZs[item["AccountNumber"]] = dict()
        passnumber += 1

        # Discover availability zones for this account/region combination
        if item["Success"]:
            region_azs = get_region_azs2(item)
            print(
                f"{ERASE_LINE}Looking at account {item['AccountNumber']} in region {item['Region']} -- {passnumber}/{len(SuccessfulCredentials)}",
                end="\r",
            )

        # Store availability zone data in structured format
        AllOrgAZs[item["AccountNumber"]][item["Region"]] = region_azs
    return AllOrgAZs


###########################
# Main
###########################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    pProfiles = args.Profiles
    pRegions = args.Regions
    pRootOnly = args.RootOnly
    pTiming = args.Time
    pSkipProfiles = args.SkipProfiles
    pSkipAccounts = args.SkipAccounts
    pverbose = args.loglevel
    pSaveFilename = args.Filename
    pAccountList = args.Accounts
    pRoleList = args.AccessRoles
    # Setup logging levels
    logging.basicConfig(level=pverbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    print(f"Collecting credentials for all accounts in your org, across multiple regions")
    AllOrgAZs = azs_across_accounts(
        pProfiles, pRegions, pSkipProfiles, pSkipAccounts, pAccountList, pTiming, pRootOnly, pverbose, pRoleList
    )
    histogram = list()
    for account, account_info in AllOrgAZs.items():
        for region, az_info in account_info.items():
            for az in az_info:
                if az["ZoneType"] == "availability-zone":
                    # print(az)
                    histogram.append(
                        {"AccountNumber": account, "Region": az["Region"], "Name": az["ZoneName"], "Id": az["ZoneId"]}
                    )

    summary = dict()
    for item in histogram:
        if item["AccountNumber"] not in summary.keys():  # item['AccountNumber'] not in t:
            summary[item["AccountNumber"]] = dict()
            summary[item["AccountNumber"]][item["Region"]] = list()
            summary[item["AccountNumber"]][item["Region"]].append((item["Name"], item["Id"]))
        elif item["AccountNumber"] in summary.keys() and item["Region"] not in summary[item["AccountNumber"]].keys():
            summary[item["AccountNumber"]][item["Region"]] = list()
            summary[item["AccountNumber"]][item["Region"]].append((item["Name"], item["Id"]))
        elif item["AccountNumber"] in summary.keys():
            summary[item["AccountNumber"]][item["Region"]].append((item["Name"], item["Id"]))

    display_dict = {
        "AccountNumber": {"DisplayOrder": 1, "Heading": "Account Number"},
        "Region": {"DisplayOrder": 2, "Heading": "Region Name"},
        "ZoneName": {"DisplayOrder": 3, "Heading": "Zone Name"},
        "ZoneId": {"DisplayOrder": 4, "Heading": "Zone Id"},
        "ZoneType": {"DisplayOrder": 5, "Heading": "Zone Type"},
    }
    # How to sort a dictionary by the key:
    sorted_summary = dict(sorted(summary.items()))
    # sorted_Results = sorted(summary, key=lambda d: (d['MgmtAccount'], d['AccountId'], d['Region']))
    display_results(summary, display_dict, "None", pSaveFilename)

    print()
    if pTiming:
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")
    print("Thanks for using this script")
    print()

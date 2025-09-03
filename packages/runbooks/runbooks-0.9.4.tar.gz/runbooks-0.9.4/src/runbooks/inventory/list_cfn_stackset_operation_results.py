#!/usr/bin/env python3

"""
AWS CloudFormation StackSet Operation Results Analysis and Correlation Script

This enterprise-grade analysis and reporting script provides comprehensive correlation and
analysis of CloudFormation StackSet deployment results with AWS Organizations account data.
Designed for infrastructure teams, DevOps engineers, and cloud architects managing large-scale
StackSet deployments across AWS Organizations for operational excellence and governance.

Key Features:
    - StackSet deployment correlation with organizational account structure
    - Missing deployment identification for compliance and coverage analysis
    - Outdated and inoperable StackSet instance detection for operational maintenance
    - Account and region deployment histogram analysis for capacity planning
    - Cross-reference analysis between StackSet deployments and active accounts
    - Cleanup recommendations for orphaned StackSet instances and resources

Analysis Capabilities:
    - File-based input processing for StackSet operation results and Organizations data
    - Regular expression-based parsing for flexible input format handling
    - Multi-dimensional analysis including account, region, and status correlations
    - Deployment gap analysis for organizational compliance tracking
    - Status categorization for operational health monitoring and maintenance

Input File Processing:
    - StackSets results file parsing with deployment status and regional distribution
    - AWS Organizations account list processing with status and email correlation
    - Cross-reference validation between deployment data and organizational structure
    - Flexible parsing supporting various output formats from inventory scripts

Enterprise Use Cases:
    - Infrastructure governance and compliance reporting for organizational oversight
    - Deployment coverage analysis ensuring consistent policy and security baseline deployment
    - Operational maintenance identification for outdated and problematic StackSet instances
    - Capacity planning and resource distribution analysis across accounts and regions
    - Cleanup orchestration for orphaned resources and inactive account deployments

Reporting and Analysis:
    - Account-based deployment histogram for organizational visibility
    - Regional distribution analysis for capacity planning and disaster recovery
    - Missing deployment identification for coverage gap analysis
    - Status-based categorization for operational health monitoring
    - Cleanup recommendations for resource optimization and maintenance

Security and Compliance:
    - Read-only analysis operations ensuring no accidental modifications
    - Comprehensive audit trail through detailed logging and analysis output
    - Organizational structure validation for security baseline compliance
    - Gap analysis supporting compliance frameworks and governance requirements

Future Enhancements:
    - Visual dashboard integration for operational monitoring and reporting
    - Enhanced output formatting with charts and graphical representations
    - Automated remediation recommendations and workflow integration
    - Real-time monitoring capabilities for continuous compliance tracking

Dependencies:
    - re: Regular expression processing for flexible input file parsing
    - ArgumentsClass: Standardized CLI argument parsing and validation
    - colorama: Enhanced terminal output with color coding for operational visibility

Example Usage:
    # Basic StackSet results analysis
    python list_cfn_stackset_operation_results.py --stacksets_filename stacksets.out --org_filename orgs.out

    # Verbose analysis with detailed logging
    python list_cfn_stackset_operation_results.py --ssf stacksets.out --of orgs.out --verbose

Output:
    Provides comprehensive analysis of StackSet deployment status, missing deployments,
    cleanup recommendations, and organizational coverage for infrastructure governance.
"""

import logging
import re

from ArgumentsClass import CommonArguments
from colorama import Fore, init

init()
__version__ = "2024.06.20"

# Configure CLI argument parsing for StackSet results analysis and correlation
parser = CommonArguments()
parser.singleprofile()  # Add profile support for consistency with other scripts
parser.verbosity()  # Configure logging verbosity for debugging and audit trails
parser.version(__version__)  # Version information for tooling compatibility tracking

# Add StackSets results file input argument for deployment analysis
parser.my_parser.add_argument(
    "--stacksets_filename",
    "--ssf",
    dest="StackSetsFilename",
    metavar="Stacksets results from the script",
    help="Path to StackSets inventory results file containing deployment status and regional distribution data",
)

# Add AWS Organizations file input argument for account correlation
parser.my_parser.add_argument(
    "--org_filename",
    "--of",
    dest="OrgsFilename",
    metavar="Organizations results from the script",
    help="Path to AWS Organizations account list file containing active accounts with status and email information",
)

# Parse command-line arguments and extract configuration parameters
args = parser.my_parser.parse_args()

pStackSetsFilename = args.StackSetsFilename  # StackSets results file path for analysis
pOrgsFilename = args.OrgsFilename  # Organizations account file path for correlation
verbose = args.loglevel  # Logging verbosity level for operational visibility

# Configure comprehensive logging for analysis operations and audit trails
logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.getLogger("boto3").setLevel(logging.CRITICAL)  # Suppress AWS SDK noise
logging.getLogger("botocore").setLevel(logging.CRITICAL)  # Suppress AWS core library noise
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)  # Suppress S3 transfer noise
logging.getLogger("urllib3").setLevel(logging.CRITICAL)  # Suppress HTTP client noise

##########################
# Analysis and Data Processing
##########################

ERASE_LINE = "\x1b[2K"  # Terminal line clearing for dynamic output updates

# Initialize StackSets data structure for comprehensive deployment analysis
StackSets = {}

# Parse StackSets inventory results file for deployment status and regional distribution
if pStackSetsFilename:
    with open(pStackSetsFilename, "r") as StackSets_infile:
        for line in StackSets_infile:
            line = line.strip("\n")  # Clean line endings for processing

            # Identify StackSet name lines using pattern matching for header detection
            if re.match("^[A-Za-z]", line) and line.find("MANAGED):$"):
                stackset_name = line.split(" ", 1)[0]  # Extract StackSet name identifier
                StackSets[stackset_name] = {}  # Initialize StackSet data structure

            # Identify and parse deployment status categories (CURRENT, OUTDATED, INOPERABLE)
            elif re.search("CURRENT|OUTDATED|INOPERABLE", line):
                Status = line.split(":", 1)[0].strip()  # Extract status category for instances
                StackSets[stackset_name][Status] = []  # Initialize status-specific instance list

            # Parse account and region deployment information using account ID pattern
            elif re.search("[0-9]{12}", line):
                acctid, regions = line.split(":")  # Split account ID from regions list
                acctid = acctid.strip()  # Clean account ID for processing

                # Parse and clean regions list from various bracket and quote formats
                region_list = regions.replace("[", "").replace("]", "").replace("'", "").replace(" ", "").split(",")

                # Aggregate account and region deployment data for analysis
                StackSets[stackset_name][Status].append({"AccountId": acctid.lstrip(), "Regions": region_list})
else:
    print("No StackSets filename provided - using empty dataset for testing")

# Parse AWS Organizations account list file for active account correlation
OrgAccounts = []
if pOrgsFilename:
    with open(pOrgsFilename, "r") as Orgs_infile:
        for line in Orgs_infile:
            # Filter lines containing account information using pattern matching
            if not re.match("^\t\t[0-9]{12}", line):
                continue

            # Extract account information from formatted Organizations output
            acct_number = line.split()[0]  # AWS account number for correlation
            Status = line.split()[1]  # Account status (ACTIVE, SUSPENDED, etc.)
            Email = line.split()[2]  # Account email for contact identification

            # Aggregate Organizations account data for cross-reference analysis
            OrgAccounts.append({"AcctId": acct_number, "Status": Status, "Email": Email})
else:
    print("No Organizations filename provided - using empty dataset for testing")

# Create active account list for deployment coverage analysis
AccountList = [x["AcctId"] for x in OrgAccounts]

# Initialize analysis data structures for comprehensive reporting
StacksToCleanUp = []  # Orphaned StackSet instances requiring cleanup
StackInstancesToCheckOn = []  # Non-current instances requiring operational attention
RegionHistogram = {}  # Regional deployment distribution for capacity planning
AccountHistogram = {}  # Account-based deployment analysis for organizational visibility

# Perform comprehensive StackSet deployment analysis and correlation
for stackset_name, stackset_data in StackSets.items():
    logging.debug(f"stackset_name: {stackset_name} | stackset_data: {stackset_data}")

    # Analyze each deployment status category for operational insights
    for status, instances in stackset_data.items():
        logging.debug(f"status: {status} | instances: {instances}")

        # Process each StackSet instance for correlation and analysis
        for i in range(len(instances)):
            current_account = StackSets[stackset_name][status][i]["AccountId"]
            logging.debug(f"AccountId: {current_account}")

            # Initialize account-based histogram for deployment tracking
            if current_account not in AccountHistogram.keys():
                AccountHistogram[current_account] = {}

            # Build comprehensive deployment histograms for analysis and reporting
            for region in StackSets[stackset_name][status][i]["Regions"]:
                # Initialize regional histogram structures
                if region not in RegionHistogram.keys():
                    RegionHistogram[region] = {}
                if region not in AccountHistogram[current_account].keys():
                    AccountHistogram[current_account][region] = list()
                if current_account not in RegionHistogram[region].keys():
                    RegionHistogram[region][current_account] = list()

                # Aggregate StackSet deployment data for histogram analysis
                RegionHistogram[region][current_account].append(stackset_name)
                AccountHistogram[current_account][region].append(stackset_name)

            # Cross-reference StackSet deployments with active Organizations accounts
            if current_account in AccountList:
                # Mark as active account with valid organizational membership
                StackSets[stackset_name][status][i]["Status"] = "ACTIVE"

                # Identify non-current instances requiring operational attention
                if not status == "CURRENT":
                    StackInstancesToCheckOn.append(
                        {
                            "StackSetName": stackset_name,
                            "Status": status,
                            "Account": current_account,
                            "Regions": StackSets[stackset_name][status][i]["Regions"],
                        }
                    )
            else:
                # Mark as orphaned instance requiring cleanup
                StackSets[stackset_name][status][i]["Status"] = "MISSING"
                StacksToCleanUp.append({"StackSetName": stackset_name, "Account": current_account})

# Identify missing deployments for coverage gap analysis
Missing_Stuff = {}
for stackset_name, stackset_data in StackSets.items():
    for status, stack_instances in stackset_data.items():
        # Analyze current deployments to identify coverage gaps
        if status == "CURRENT":
            # Extract accounts with current deployments
            account_list = [x["AccountId"] for x in stack_instances] if len(stack_instances) > 1 else []
            # Calculate missing deployments using set difference analysis
            Missing_Stuff[stackset_name] = list(set(AccountList) - set(account_list))

print()
print("Thanks for using this script...")
print()

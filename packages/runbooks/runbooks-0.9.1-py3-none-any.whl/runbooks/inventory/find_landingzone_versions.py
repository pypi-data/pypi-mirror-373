#!/usr/bin/env python3
"""
AWS Landing Zone Version Discovery and Analysis Script

Comprehensive enterprise-grade tool for discovering, enumerating, and analyzing AWS Landing Zone
(ALZ) deployments across multiple AWS profiles and organizational environments. Designed for
enterprise infrastructure governance, compliance monitoring, and Landing Zone lifecycle management
with multi-profile authentication and automated version tracking capabilities.

Key Features:
- Multi-profile AWS Landing Zone discovery and version identification
- Automated Management Account detection through CloudFormation stack analysis
- Landing Zone solution version extraction from CloudFormation outputs
- Comprehensive tabular reporting with profile, account, region, and version details
- Enterprise authentication with multi-profile credential management
- Extensive error handling for credential and configuration issues

Enterprise Capabilities:
- Organizational Landing Zone inventory and lifecycle tracking
- Multi-environment Landing Zone version compliance monitoring
- Automated Management Account identification for governance operations
- Cross-profile Landing Zone deployment visibility and analysis
- Enterprise credential management with comprehensive error handling
- Scalable processing for large-scale multi-account environments

Operational Use Cases:
- Landing Zone version audit and compliance tracking across organizations
- Management Account discovery for organizational governance operations
- Infrastructure inventory for Landing Zone upgrade planning and coordination
- Enterprise compliance monitoring through systematic Landing Zone analysis
- Multi-environment Landing Zone deployment tracking and management

Output Format:
- Tabular display with Profile, Account, Region, Stack Name, and Version information
- Comprehensive operational metrics including profile count and Landing Zone discovery statistics
- Color-coded terminal output for enhanced operational visibility
- Structured data presentation for integration with enterprise reporting systems

Authentication & Security:
- Multi-profile AWS credential management with comprehensive validation
- Cross-account access through profile-based authentication
- Extensive error handling for credential retrieval and configuration issues
- Regional validation and access control for secure Landing Zone operations

Performance & Scale:
- Efficient multi-profile processing for large-scale organizational environments
- Memory-efficient CloudFormation stack analysis and version extraction
- Progress indicators for enhanced user experience during discovery operations
- Optimized API usage patterns for improved performance and reduced throttling

Landing Zone Detection Logic:
- CloudFormation stack analysis for Landing Zone identification (SO0044 solution)
- Stack description parsing for AWS Landing Zone solution identification
- Output key extraction for precise Landing Zone version determination
- Multi-stack analysis ensuring comprehensive Landing Zone discovery

Error Handling & Resilience:
- Comprehensive credential error handling with specific error type identification
- AWS API authorization failure detection with detailed troubleshooting guidance
- Configuration validation with profile-specific error messaging
- Graceful degradation for inaccessible profiles maintaining operation continuity

Dependencies:
- boto3: AWS SDK for CloudFormation and credential management
- Custom modules: Inventory_Modules, ArgumentsClass
- colorama: Enhanced terminal output and progress indicators

Authors: AWS CloudOps Team
Version: 2023.05.31
License: MIT
"""

import logging

import boto3
import Inventory_Modules
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError, CredentialRetrievalError, InvalidConfigError
from colorama import init

# Initialize colorama for cross-platform colored terminal output
init()

__version__ = "2023.05.31"

# Configure comprehensive CLI argument parsing for Landing Zone discovery operations
parser = CommonArguments()
parser.multiprofile()  # Multi-profile authentication for organizational Landing Zone discovery
parser.verbosity()  # Configurable logging levels for operational visibility
parser.version(__version__)  # Script version tracking for compatibility management
args = parser.my_parser.parse_args()

# Extract CLI arguments for Landing Zone discovery and operational configuration
pProfiles = args.Profiles  # AWS profiles for multi-account Landing Zone analysis
verbose = args.loglevel  # Logging verbosity for operational monitoring and troubleshooting

# Configure comprehensive logging for Landing Zone discovery operations
logging.basicConfig(
    level=args.loglevel, format="[%(filename)s:%(lineno)s:%(levelname)s - %(funcName)30s() ] %(message)s"
)

##########################
# Terminal control and operational configuration constants
ERASE_LINE = "\x1b[2K"  # ANSI escape sequence for clearing terminal line during progress display
SkipProfiles = ["default"]  # Profile exclusion list for organizational Landing Zone discovery

# Configure AWS profile discovery strategy based on user input
if pProfiles is None:
    # Default to single profile when no specific profiles are specified
    print(f"You've provided no profile, so we'll use the default")
    AllProfiles = ["default"]
elif "all" in pProfiles or "ALL" in pProfiles or "All" in pProfiles:
    # Comprehensive multi-profile Landing Zone discovery across all available profiles
    logging.info(
        f"You specified 'all' as the profile, so we're going to check ALL of the profiles to find all of the management accounts, and list out all of their ALZ versions."
    )
    print(
        "You've specified multiple profiles, so we've got to find them, determine which profiles represent Management Accounts, \n"
        "and then parse through those. This will take a few moments."
    )
    # Discover all available profiles excluding specified skip profiles
    AllProfiles = Inventory_Modules.get_profiles(fSkipProfiles=SkipProfiles, fprofiles=pProfiles)
else:
    # Targeted profile-specific Landing Zone discovery based on user selection
    AllProfiles = Inventory_Modules.get_profiles(fSkipProfiles=SkipProfiles, fprofiles=pProfiles)

# Execute comprehensive Landing Zone discovery across all configured profiles
ALZProfiles = []  # Initialize Landing Zone profile collection for discovered Management Accounts

for profile in AllProfiles:
    # Display real-time progress during profile analysis with terminal line clearing
    print(f"{ERASE_LINE}Checking profile: {profile}", end="\r")

    try:
        # Analyze current profile to determine if it represents an AWS Landing Zone Management Account
        ALZMgmntAcct = Inventory_Modules.find_if_alz(profile)

        if ALZMgmntAcct["ALZ"]:
            # Extract account metadata for confirmed Landing Zone Management Accounts
            accountnum = Inventory_Modules.find_account_number(profile)
            ALZProfiles.append({"Profile": profile, "Acctnum": accountnum, "Region": ALZMgmntAcct["Region"]})

    except ClientError as my_Error:
        # Handle AWS API client errors with specific error type identification
        if str(my_Error).find("UnrecognizedClientException") > 0:
            logging.error("%s: Security Issue", profile)
        elif str(my_Error).find("InvalidClientTokenId") > 0:
            logging.error("%s: Security Token is bad - probably a bad entry in config", profile)
            pass

    except CredentialRetrievalError as my_Error:
        # Handle credential retrieval errors for custom authentication processes
        if str(my_Error).find("CredentialRetrievalError") > 0:
            logging.error("%s: Some custom process isn't working", profile)
            pass

    except InvalidConfigError as my_Error:
        # Handle configuration validation errors for profile-specific credential issues
        if str(my_Error).find("InvalidConfigError") > 0:
            logging.error(
                "%s: profile is invalid. Probably due to a config profile based on a credential that doesn't work",
                profile,
            )
            pass

# Clear progress display and initialize tabular output formatting for Landing Zone inventory
print(ERASE_LINE)
fmt = "%-20s %-13s %-15s %-35s %-21s"  # Column formatting for structured Landing Zone data display
print(fmt % ("Profile", "Account", "Region", "ALZ Stack Name", "ALZ Version"))
print(fmt % ("-------", "-------", "------", "--------------", "-----------"))

# Execute comprehensive Landing Zone version analysis for each discovered Management Account
for item in ALZProfiles:
    # Establish authenticated AWS session for CloudFormation stack analysis
    aws_session = boto3.Session(profile_name=item["Profile"], region_name=item["Region"])
    aws_client = aws_session.client("cloudformation")

    # Retrieve comprehensive CloudFormation stack inventory for Landing Zone identification
    stack_list = aws_client.describe_stacks()["Stacks"]

    # Analyze each CloudFormation stack for AWS Landing Zone solution identification
    for i in range(len(stack_list)):
        logging.warning(f"Checking stack {stack_list[i]['StackName']} to see if it is the ALZ initiation stack")

        # Identify Landing Zone stacks through solution ID (SO0044) in stack description
        if "Description" in stack_list[i].keys() and stack_list[i]["Description"].find("SO0044") > 0:
            # Extract Landing Zone version from CloudFormation stack outputs
            for j in range(len(stack_list[i]["Outputs"])):
                if stack_list[i]["Outputs"][j]["OutputKey"] == "LandingZoneSolutionVersion":
                    # Extract and display Landing Zone version information with formatted output
                    ALZVersion = stack_list[i]["Outputs"][j]["OutputValue"]
                    print(
                        fmt % (item["Profile"], item["Acctnum"], item["Region"], stack_list[i]["StackName"], ALZVersion)
                    )

# Display comprehensive operational summary with discovery metrics
print(ERASE_LINE)
print(f"Checked {len(AllProfiles)} accounts/ Orgs. Found {len(ALZProfiles)} ALZs")
print()
print("Thank you for using this script.")
print()

#!/usr/bin/env python3

"""
AWS Systems Manager (SSM) Parameter Store Inventory and Management Script

This script provides comprehensive discovery, analysis, and optional cleanup capabilities
for AWS Systems Manager Parameter Store parameters across multiple accounts and regions.
It's designed for enterprise environments where parameter sprawl and legacy parameter
cleanup is critical for operational efficiency and cost optimization.

Key Features:
- Multi-account SSM Parameter Store discovery using assume role capabilities
- Multi-region scanning with configurable region targeting
- AWS Landing Zone (ALZ) parameter detection and cleanup validation
- Age-based parameter filtering with configurable retention periods
- Pattern-based parameter identification using regex matching
- Comprehensive parameter metadata extraction and analysis
- Enterprise reporting with CSV export and structured output
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- Parameter Store auditing and compliance reporting
- Legacy AWS Landing Zone parameter cleanup and migration
- Parameter sprawl analysis and cost optimization
- Multi-account parameter standardization and governance
- Operational efficiency through automated parameter lifecycle management
- Security auditing of stored parameters and access patterns

ALZ-Specific Features:
- Automatic detection of AWS Landing Zone generated parameters
- Pattern matching for ALZ UUID-based parameter naming conventions
- Age-based filtering to identify stale ALZ parameters from failed deployments
- Bulk deletion capabilities for ALZ cleanup operations (when enabled)
- Rollback protection through configurable retention windows

Security Considerations:
- Uses IAM assume role capabilities for cross-account access
- Implements proper error handling for authorization failures
- Supports read-only operations with optional deletion capabilities
- Provides comprehensive audit trail through detailed logging
- Respects parameter access permissions and encryption settings

Parameter Patterns:
- ALZ Pattern: /UUID-based-path/numeric-suffix (e.g., /2ac07efd-153d-4069-b7ad-0d18cc398b11/105)
- Standard AWS parameter conventions and custom organizational patterns
- Configurable regex matching for flexible parameter identification

Dependencies:
- boto3/botocore for AWS SSM API interactions
- tqdm for progress tracking during large-scale operations
- Inventory_Modules for common utility functions
- ArgumentsClass for standardized CLI argument parsing

Author: AWS CloudOps Team
Version: 2024.05.07
"""

import logging
import re
import sys
from datetime import datetime, timedelta, timezone
from os.path import split
from time import time

from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_ssm_parameters2, get_all_credentials
from tqdm.auto import tqdm

init()
__version__ = "2024.05.07"
begin_time = time()
ERASE_LINE = "\x1b[2K"


##################
# Functions
##################


def parse_args(arguments):
    """
    Parse command line arguments for SSM Parameter Store inventory and management operations.

    Configures comprehensive argument parsing for multi-account, multi-region SSM Parameter
    Store discovery with specialized support for AWS Landing Zone parameter cleanup and
    age-based filtering. Supports enterprise deployment patterns with profile management,
    region targeting, and operational safety controls.

    Args:
        arguments (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: List of AWS profiles to process
            - Regions: Target regions for parameter discovery
            - SkipProfiles/SkipAccounts: Exclusion filters
            - RootOnly: Limit to organization root accounts
            - ALZParam: Enable AWS Landing Zone parameter detection
            - DaysBack: Retention period for age-based filtering (default: 90 days)
            - DeletionRun: Enable parameter deletion operations (currently disabled)
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration

    Configuration Options:
        - Multi-region scanning with region filters
        - Multi-profile support for federated access
        - Extended arguments for advanced filtering
        - Root-only mode for organization-level inventory
        - ALZ-specific parameter pattern detection
        - Configurable retention windows for cleanup operations
        - File output for integration and reporting
        - Timing metrics for performance optimization
        - Verbose logging for debugging and audit

    ALZ-Specific Arguments:
        --ALZ: Enables detection of AWS Landing Zone generated parameters using UUID-based
               pattern matching for identification of stale parameters from failed deployments
        -b/--daysback: Configures retention window for parameter age filtering, defaults to
                       90 days to provide reasonable safety margin for cleanup operations
        +delete: Reserved for future parameter deletion capabilities, currently disabled for
                 safety pending enhanced multi-account/region grouping implementation

    Safety Features:
        - Deletion operations are currently disabled to prevent accidental data loss
        - Age-based filtering provides rollback protection for recent parameters
        - Comprehensive logging ensures full audit trail for compliance
        - Profile-based access controls respect organizational security boundaries
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
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
        "--ALZ",
        help="Identify left-over parameters created by the ALZ solution",
        action="store_const",
        dest="ALZParam",
        const=True,
        default=False,
    )
    local.add_argument(
        "-b", "--daysback", help="Only keep the last x days of Parameters (default 90)", dest="DaysBack", default=90
    )
    local.add_argument(
        "+delete",
        help="Deletion is not working currently (as of 6/22/23)",
        # help="Delete left-over parameters created by the ALZ solution. DOES NOT DELETE ANY OTHER PARAMETERS!!",
        action="store_const",
        dest="DeletionRun",
        const=True,
        default=False,
    )
    return parser.my_parser.parse_args(arguments)


def find_ssm_parameters(f_credentialList):
    """
    Discover and collect SSM Parameter Store parameters across multiple AWS accounts and regions.

    Implements sequential processing across account/region combinations to gather comprehensive
    parameter inventory while providing progress feedback through visual indicators. Handles
    large parameter stores with thousands of parameters while maintaining operational stability
    through proper error handling and logging.

    Args:
        f_credentialList (list): List of credential dictionaries containing:
            - AccountId/AccountNumber: AWS account identifier
            - Profile: AWS profile for authentication
            - Region: Target AWS region for scanning
            - Credentials: Temporary AWS credentials for API access

    Returns:
        list: Aggregated collection of parameter records with structure:
            - AccountNumber: AWS account containing the parameter
            - Region: AWS region where parameter is stored
            - Name: Parameter name/path in SSM Parameter Store
            - LastModifiedDate: Timestamp of last parameter modification
            - credentials: AWS credentials for potential deletion operations

    Processing Architecture:
        - Sequential processing for stability with large parameter stores
        - Progress tracking through tqdm for operational visibility
        - Comprehensive error handling for authorization failures
        - Extensible design for future multi-threading optimization

    Performance Considerations:
        - Parameter stores can contain 10,000+ parameters per account/region
        - Sequential processing trades speed for reliability and simplicity
        - Future enhancement opportunity for multi-threaded implementation
        - Progress indicators provide operational feedback during long operations

    Error Handling:
        - ClientError: AWS API authorization and throttling issues
        - Graceful handling of access denied scenarios
        - Detailed logging for troubleshooting authentication problems
        - Continues processing remaining accounts on individual failures

    Enterprise Scale Considerations:
        - Designed for large multi-account organizations
        - Handles parameter stores with thousands of parameters
        - Provides operational visibility through progress tracking
        - Logs authorization issues for security team follow-up
    """
    parameter_list = []
    # Import Rich display utilities for professional output
    from runbooks.common.rich_utils import console, print_info, print_success
    from runbooks.inventory.rich_inventory_display import create_inventory_progress, display_inventory_header

    # Calculate operation scope
    account_count = len(set([cred["AccountId"] for cred in f_credentialList]))
    region_count = len(set([cred["Region"] for cred in f_credentialList]))

    # Display professional header
    display_inventory_header("SSM Parameters", "multi-profile", account_count, region_count)

    # Create Rich progress bar
    progress = create_inventory_progress(len(f_credentialList), "🔑 Discovering SSM Parameters")
    task = progress.add_task("Processing credentials", total=len(f_credentialList))
    progress.start()

    for credential in f_credentialList:
        try:
            # Call SSM API to discover all parameters in this account/region combination
            # Note: Parameter stores can contain 10,000+ parameters - this operation may take time
            # Future enhancement: Consider multi-threading for improved performance
            parameter_list.extend(find_ssm_parameters2(credential))
        # Optional verbose logging for parameter discovery progress (currently commented)
        # if verbose < 50 or len(parameter_list) == 0:
        # 	print(f"Found a running total of {len(parameter_list)} parameters in account {Fore.RED}{credential['AccountNumber']}{Fore.RESET} in region {Fore.RED}{credential['Region']}{Fore.RESET}")
        except ClientError as my_Error:
            # Handle AWS API authorization failures gracefully
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Profile {credential['Profile']}: Authorization Failure for account {credential['AccountNumber']}"
                )
        finally:
            # Update progress
            progress.update(task, advance=1)

    progress.stop()

    # Display completion summary
    print_success(f"✅ SSM Parameter discovery completed! Found {len(parameter_list)} parameters total")

    return parameter_list


##################
# Main execution entry point for SSM Parameter Store enterprise inventory and management
##################
if __name__ == "__main__":
    """
    Main orchestration for comprehensive SSM Parameter Store discovery and analysis.
    
    Coordinates multi-account, multi-region parameter inventory operations with specialized
    support for AWS Landing Zone cleanup and enterprise parameter governance workflows.
    """
    # Parse enterprise command-line arguments with specialized SSM and ALZ options
    args = parse_args(sys.argv[1:])

    # Extract configuration parameters for multi-account parameter discovery
    pProfiles = args.Profiles  # AWS profile list for federated access management
    pRegionList = args.Regions  # Target regions for parameter store scanning
    pSkipAccounts = args.SkipAccounts  # Account exclusion list for organizational policy
    pSkipProfiles = args.SkipProfiles  # Profile exclusion for credential optimization
    pAccounts = args.Accounts  # Specific account targeting for focused operations
    pRootOnly = args.RootOnly  # Organization root account limitation flag
    ALZParam = args.ALZParam  # AWS Landing Zone parameter detection enablement
    pTiming = args.Time  # Performance timing for operational optimization
    pFilename = args.Filename  # CSV export file for enterprise reporting
    DeletionRun = args.DeletionRun  # Parameter deletion capability (currently disabled)
    dtDaysBack = timedelta(days=int(args.DaysBack))  # Retention window for age-based filtering
    verbose = args.loglevel  # Logging verbosity for operational visibility

    # Configure enterprise logging infrastructure for parameter store operations
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

    # Suppress verbose AWS SDK logging for cleaner parameter inventory output
    logging.getLogger("boto3").setLevel(logging.CRITICAL)  # Suppress boto3 internal logging
    logging.getLogger("botocore").setLevel(logging.CRITICAL)  # Suppress botocore HTTP logging
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)  # Suppress S3 transfer logging
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)  # Suppress HTTP connection logging

    ##########################
    # Define AWS Landing Zone (ALZ) parameter pattern for UUID-based identification
    # Pattern matches: /UUID/numeric-suffix (e.g., /2ac07efd-153d-4069-b7ad-0d18cc398b11/105)
    ALZRegex = r"/\w{8,8}-\w{4,4}-\w{4,4}-\w{4,4}-\w{12,12}/\w{3,3}"
    # Import Rich utilities at module level
    from runbooks.common.rich_utils import console, print_header

    # Display module header
    print_header("SSM Parameter Store Discovery", "0.7.8")

    # Execute enterprise credential discovery across organizational hierarchy
    CredentialList = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList
    )

    # Extract unique lists for summary reporting and operational metrics
    RegionList = list(set([x["Region"] for x in CredentialList]))  # Distinct regions for coverage analysis
    AccountList = list(set([x["AccountId"] for x in CredentialList]))  # Distinct accounts for scope reporting

    # Initialize deletion candidate list for ALZ parameter cleanup operations
    ParamsToDelete = []

    # Execute comprehensive SSM Parameter Store discovery across all accounts/regions
    AllParameters = find_ssm_parameters(CredentialList)

    # Configure enterprise SSM parameter inventory report display formatting
    display_dict = {
        "AccountNumber": {"DisplayOrder": 1, "Heading": "Acct Number"},  # Account identifier for organizational context
        "Region": {"DisplayOrder": 2, "Heading": "Region"},  # AWS region for geographic parameter distribution
        "Name": {"DisplayOrder": 3, "Heading": "Parameter Name"},  # SSM parameter path for identification
        "LastModifiedDate": {
            "DisplayOrder": 4,
            "Heading": "Last Modified",
        },  # Modification timestamp for lifecycle analysis
    }

    # Sort parameter inventory for structured enterprise reporting and operational analysis
    sorted_Parameters = sorted(AllParameters, key=lambda x: (x["AccountNumber"], x["Region"], x["Name"]))

    # Generate comprehensive SSM parameter inventory report with CSV export capability
    display_results(sorted_Parameters, display_dict, "Default", pFilename)

    # Execute AWS Landing Zone (ALZ) parameter pattern analysis and cleanup candidate identification
    if ALZParam:
        ALZParams = 0  # Counter for ALZ parameters matching cleanup criteria
        today = datetime.now(tz=timezone.utc)  # Current UTC timestamp for age calculation

        # Iterate through all discovered parameters for ALZ pattern matching and age analysis
        for y in range(len(AllParameters)):
            # ALZ parameters follow UUID-based path pattern: /UUID/numeric-suffix
            # Example: "/2ac07efd-153d-4069-b7ad-0d18cc398b11/105" from failed ALZ deployments
            # Regex pattern: "/\w{8,8}-\w{4,4}-\w{4,4}-\w{4,4}-\w{12,12}/\w{3,3}"
            ParameterDate = AllParameters[y]["LastModifiedDate"]
            mydelta = today - ParameterDate  # Calculate parameter age as timedelta object
            # Compile ALZ regex pattern for efficient UUID-based parameter identification
            p = re.compile(ALZRegex)

            # Log parameter analysis for detailed operational visibility and debugging
            logging.info(f"Parameter{y}: {AllParameters[y]['Name']} with date {AllParameters[y]['LastModifiedDate']}")

            # Identify ALZ parameters that match UUID pattern and exceed retention window
            if p.match(AllParameters[y]["Name"]) and mydelta > dtDaysBack:
                logging.error(
                    f"Parameter {AllParameters[y]['Name']} with date of {AllParameters[y]['LastModifiedDate']} matched"
                )
                ALZParams += 1  # Increment counter for cleanup candidate identification

                # Add parameter to deletion candidate list with credentials for future cleanup operations
                ParamsToDelete.append(
                    {"Credentials": AllParameters[y]["credentials"], "Name": AllParameters[y]["Name"]}
                )

    # Handle parameter deletion operations (currently disabled for safety)
    if DeletionRun:
        print(
            f"Currently the deletion function for errored ALZ parameters isn't working. Please contact the author if this functionality is still needed for you... "
        )

        """
        Technical Note: Parameter Deletion Architecture Challenge
        
        The SSM parameter deletion functionality is currently disabled due to architectural limitations
        with the current multi-account/multi-region discovery implementation:
        
        - SSM delete_parameters API requires account/region-specific batching (max 10 parameters per call)
        - Original single-account/single-region implementation supported efficient batched deletion
        - Current multi-account/multi-region capability requires parameter grouping by account/region
        - Implementation complexity vs. usage demand assessment resulted in temporary disabling
        
        Future Enhancement Requirements:
        - Group deletion candidates by account/region combination for proper API batching  
        - Implement account/region-specific credential context for deletion operations
        - Add batch size optimization (10 parameters per delete_parameters API call)
        - Include rollback protection and deletion confirmation workflows
        - Add comprehensive deletion audit logging for compliance tracking
        
        Contact maintainer if this functionality is required for your operational needs.
        """

    print()
    print(ERASE_LINE)  # Clear any progress indicators for clean summary display

    # Display comprehensive SSM parameter inventory summary for operational reporting
    print(f"Found {len(AllParameters)} total parameters")

    # Report ALZ cleanup analysis results when ALZ detection is enabled
    print(
        f"And {ALZParams} of them were from buggy ALZ runs more than {dtDaysBack.days} days back"
    ) if ALZParam else None

    # Display performance timing metrics for operational optimization
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

    print()

    # Display operational exclusion summary for transparency and audit trail
    print(f"These accounts were skipped - as requested: {pSkipAccounts}") if pSkipAccounts is not None else None
    print(f"These profiles were skipped - as requested: {pSkipProfiles}") if pSkipProfiles is not None else None

    print()

    # Display comprehensive operational summary for executive reporting
    print(
        f"Found {len(AllParameters)} SSM parameters across {len(AccountList)} account{'' if len(AccountList) == 1 else 's'} across {len(RegionList)} region{'' if len(RegionList) == 1 else 's'}"
    )

    print()

    # Display completion message and output file information
    print("Thank you for using this script")
    print(
        f"Your output was saved to {Fore.GREEN}'{pFilename}-{datetime.now().strftime('%y-%m-%d--%H:%M:%S')}'{Fore.RESET}"
    ) if pFilename is not None else None

    print()

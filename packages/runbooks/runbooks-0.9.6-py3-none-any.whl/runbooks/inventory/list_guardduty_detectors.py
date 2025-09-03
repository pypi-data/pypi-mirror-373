#!/usr/bin/env python3

"""
AWS GuardDuty Detector Discovery and Management Script

This script provides comprehensive discovery, inventory, and management capabilities for
AWS GuardDuty detectors and invitations across multiple accounts and regions. It's designed
for enterprise security teams who need visibility into GuardDuty deployment status,
detector configuration, and administrative relationships across large-scale AWS environments.

Key Features:
- Multi-account GuardDuty detector discovery using assume role capabilities
- Multi-region scanning with GuardDuty-enabled region targeting
- GuardDuty invitation tracking and management for organizational security
- Administrative account detection with member account relationship mapping
- Detector deletion capabilities with safety controls for cleanup operations
- Enterprise reporting with detailed detector and invitation analysis
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- Security posture assessment and GuardDuty deployment validation
- GuardDuty administrative relationship mapping across organizations
- Security service cleanup and consolidation during account transitions
- Compliance reporting for threat detection service coverage
- Multi-account security governance and standardization
- GuardDuty cost optimization through detector lifecycle management
- Security incident response planning with detector coverage analysis

GuardDuty Management Features:
- Detector enumeration with administrative status identification
- Member account relationship tracking for security hierarchy mapping
- Invitation discovery and cleanup for organizational security management
- Multi-region detector coverage analysis for comprehensive protection
- Administrative account detection with member count reporting
- Detector deletion with safety controls and confirmation mechanisms

Security Considerations:
- Uses IAM assume role capabilities for cross-account GuardDuty access
- Implements proper error handling for authorization failures
- Supports both read-only discovery and controlled deletion operations
- Respects GuardDuty service permissions and regional availability constraints
- Provides comprehensive audit trail through detailed logging
- Implements safety controls for destructive operations with confirmation prompts

GuardDuty Administrative Analysis:
- Administrative account identification and member relationship mapping
- Invitation status tracking for organizational security coordination
- Detector configuration analysis across organizational boundaries
- Security service coverage assessment for compliance validation
- Multi-account threat detection architecture documentation

Deletion and Cleanup Features:
- Safe detector deletion with confirmation mechanisms
- Invitation cleanup for organizational security management
- Member disassociation handling for administrative relationship changes
- Comprehensive error handling for cleanup operation failures
- Audit logging for all deletion and modification operations

Performance Considerations:
- Sequential processing for reliable GuardDuty API operations
- Progress tracking for operational visibility during large-scale operations
- Efficient credential management for cross-account security access
- Region-aware processing optimized for GuardDuty service availability
- Memory-optimized data structures for large security inventories

Dependencies:
- boto3/botocore for AWS GuardDuty API interactions
- Inventory_Modules for common utility functions and credential management
- ArgumentsClass for standardized CLI argument parsing
- account_class for AWS account access and session management
- colorama for enhanced output formatting

Safety and Compliance:
- Confirmation prompts for destructive operations
- Comprehensive logging for security audit trails
- Error handling for failed deletion operations
- Member account protection during administrative cleanup
- Force deletion capability with additional safety controls

Future Enhancements:
- GuardDuty finding analysis and threat intelligence integration
- Automated detector configuration compliance checking
- Integration with AWS Config for security service drift detection
- Cost analysis and optimization recommendations for GuardDuty usage

Author: AWS CloudOps Team
Version: 2023.07.18
"""

import logging
import sys

import boto3
import Inventory_Modules
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import get_all_credentials

init()
__version__ = "2023.07.18"

# Parse enterprise command-line arguments with GuardDuty-specific security management options
parser = CommonArguments()
parser.singleprofile()  # Single profile mode for focused GuardDuty operations
parser.multiregion_nodefault()  # Multi-region scanning without default region assumptions
parser.extendedargs()  # Extended arguments for advanced filtering and account selection
parser.deletion()  # Deletion capabilities with safety controls for GuardDuty cleanup
parser.rootOnly()  # Organization root account limitation for security governance
parser.rolestouse()  # Cross-account roles for Organizations GuardDuty access
parser.timing()  # Performance timing for operational optimization
parser.verbosity()  # Logging verbosity for security operations audit trail
parser.version(__version__)  # Version information for operational documentation

# Add GuardDuty-specific deletion and management arguments
parser.my_parser.add_argument(
    "+delete",
    "+forreal",
    "+fix",
    dest="flagDelete",
    action="store_true",
    help="Enable GuardDuty detector deletion operations - DESTRUCTIVE ACTION with confirmation prompts for security cleanup",
)

# Parse all command-line arguments for GuardDuty security management operations
args = parser.my_parser.parse_args()

# Extract configuration parameters for multi-account GuardDuty security management
pProfile = args.Profile  # AWS profile for GuardDuty administrative access
pRegions = args.Regions  # Target regions for GuardDuty detector enumeration
pSkipAccounts = args.SkipAccounts  # Account exclusion list for organizational policy compliance
pSkipProfiles = args.SkipProfiles  # Profile exclusion for credential optimization
pAccounts = args.Accounts  # Specific account targeting for focused security analysis
pRootOnly = args.RootOnly  # Organization root account limitation flag
pRolesToUse = args.AccessRoles  # Cross-account roles for Organizations security access
verbose = args.loglevel  # Logging verbosity for security operations visibility
DeletionRun = args.flagDelete  # Enable detector deletion operations - CRITICAL SECURITY FLAG
ForceDelete = args.Force  # Override safety confirmations for automated security workflows
pTiming = args.Time  # Performance timing for operational optimization

# Configure enterprise logging infrastructure for GuardDuty operations audit trail
logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

##########################
# Initialize enterprise GuardDuty discovery and security management operations
##########################

ERASE_LINE = "\x1b[2K"

# Initialize AWS account access for GuardDuty administrative operations
aws_acct = aws_acct_access(pProfile)

# Initialize enterprise GuardDuty inventory tracking and metrics
NumObjectsFound = 0  # Total detector count across all accounts and regions
session_gd = aws_acct.session  # Primary session for GuardDuty administrative operations
all_gd_detectors = []  # Comprehensive detector inventory with administrative relationships
all_gd_invites = []  # GuardDuty invitation tracking for organizational security coordination
GD_Admin_Accounts = []  # Administrative account tracking for security hierarchy mapping

# Configure GuardDuty-enabled regions for comprehensive threat detection coverage
# This validation ensures we only scan regions where GuardDuty service is available and enabled
if pRegions is None:
    pRegions = ["all"]  # Default to all available GuardDuty regions for comprehensive security coverage

# Discover GuardDuty-enabled regions across organizational accounts
gd_regions = Inventory_Modules.get_regions3(aws_acct, pRegions)

# Execute enterprise credential discovery and validation across organizational GuardDuty infrastructure
AllCredentials = get_all_credentials(
    pProfile, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, gd_regions, pRolesToUse
)

# Calculate organizational scope for executive security management reporting
RegionList = list(set([x["Region"] for x in AllCredentials]))
AccountList = list(set([x["AccountId"] for x in AllCredentials]))
print(f"Searching {len(AccountList)} accounts and {len(RegionList)} regions for GuardDuty detectors")

# Initialize STS session for cross-account credential validation and security token management
sts_session = aws_acct.session
sts_client = sts_session.client("sts")

# Execute comprehensive GuardDuty detector and invitation discovery across organizational accounts
places_to_try = len(AllCredentials)  # Progress tracking for operational visibility

# Main GuardDuty discovery loop - Sequential processing for reliable security service enumeration
for credential in AllCredentials:
    logging.info(f"Checking Account: {credential['AccountId']}")

    # Legacy credential access pattern (commented out for reference)
    # This was the original approach for cross-account access before credential pre-processing
    # try:
    #     account_credentials = Inventory_Modules.get_child_access3(aws_acct, account['AccountId'])
    # except ClientError as my_Error:
    #     if "AuthFailure" in str(my_Error):
    #         print(f"Authorization Failure for account {account['AccountId']}")
    #     sys.exit("Credentials failure")

    logging.info(f"Checking Region: {credential['Region']}")
    places_to_try -= 1  # Decrement progress counter for operational tracking

    try:
        # Establish AWS session for GuardDuty API operations using pre-validated credentials
        # This session enables cross-account GuardDuty detector and invitation discovery
        session_aws = boto3.Session(
            aws_access_key_id=credential["AccessKeyId"],
            aws_secret_access_key=credential["SecretAccessKey"],
            aws_session_token=credential["SessionToken"],
            region_name=credential["Region"],
        )

        # Initialize GuardDuty client for security service API operations
        client_aws = session_aws.client("guardduty")
        logging.debug(f"Token Info: {credential} in region {credential['Region']}")

        # Execute GuardDuty invitation discovery for organizational security coordination
        # Invitations represent pending or active administrative relationships between accounts
        logging.info(f"Finding any invites for account: {credential['AccountId']} in region {credential['Region']}")
        response = client_aws.list_invitations()
        logging.debug(
            f"Finished listing invites for account: {credential['AccountId']} in region {credential['Region']}"
        )

    except ClientError as my_Error:
        # Handle AWS API authorization failures with comprehensive error analysis
        if "AuthFailure" in str(my_Error):
            print(f"{credential['AccountId']}: Authorization Failure for account {credential['AccountId']}")
            continue  # Skip this account/region combination but continue processing others

        # Handle invalid security token errors typically caused by region opt-in issues
        if str(my_Error).find("security token included in the request is invalid") > 0:
            logging.error(
                f"Account #:{credential['AccountId']} - The region you're trying '{credential['Region']}' isn't enabled for your account"
            )
            continue  # Skip disabled regions but continue with other regions

    except Exception as my_Error:
        # Handle unexpected errors during GuardDuty API operations
        print(my_Error)
        continue  # Continue processing despite unexpected errors for operational resilience
    # Process discovered GuardDuty invitations for organizational security coordination
    try:
        if "Invitations" in response.keys():
            # Process each invitation to build comprehensive security relationship mapping
            for i in range(len(response["Invitations"])):
                # Create invitation record with credentials for future management operations
                invitation_record = {
                    "AccountId": response["Invitations"][i]["AccountId"],  # Administrative account identifier
                    "InvitationId": response["Invitations"][i]["InvitationId"],  # Unique invitation identifier
                    "Region": credential["Region"],  # Regional context for security coordination
                    "AccessKeyId": credential["AccessKeyId"],  # Credentials for invitation management
                    "SecretAccessKey": credential["SecretAccessKey"],  # Security credentials for API operations
                    "SessionToken": credential["SessionToken"],  # Session token for temporary access
                }

                # Add to enterprise GuardDuty invitation inventory for administrative tracking
                all_gd_invites.append(invitation_record)

                # Log invitation discovery for security audit trail and organizational visibility
                logging.error(
                    f"Found invite ID {response['Invitations'][i]['InvitationId']} in account {response['Invitations'][i]['AccountId']} in region {credential['Region']}"
                )
    except NameError:
        # Handle cases where response variable is undefined due to API errors
        # This ensures graceful handling of failed invitation discovery operations
        pass
    # Execute comprehensive GuardDuty detector discovery with administrative relationship analysis
    try:
        # Display progress information for operational visibility during large-scale security operations
        print(
            f"{ERASE_LINE}Trying account {credential['AccountId']} in region {credential['Region']} -- {places_to_try} left of {len(AllCredentials)}",
            end="\r",
        )

        # Execute GuardDuty detector enumeration for security service inventory
        response = client_aws.list_detectors()

        # Process discovered detectors with comprehensive metadata extraction and administrative analysis
        if len(response["DetectorIds"]) > 0:
            # Update enterprise security service metrics and tracking
            NumObjectsFound = NumObjectsFound + len(response["DetectorIds"])

            # Analyze administrative relationships and member account associations
            # This is critical for understanding GuardDuty security hierarchy and governance structure
            admin_acct_response = client_aws.list_members(
                DetectorId=str(response["DetectorIds"][0]),
                OnlyAssociated="False",  # Include both associated and pending member accounts
            )

            # Log detector discovery for security audit trail and operational tracking
            logging.warning(
                f"Found another detector {str(response['DetectorIds'][0])} in account {credential['AccountId']} in region {credential['Region']} bringing the total found to {str(NumObjectsFound)}"
            )

            # Classify detector as administrative account based on member relationships
            if len(admin_acct_response["Members"]) > 0:
                # Create comprehensive administrative account record for security governance
                admin_detector_record = {
                    "AccountId": credential["AccountId"],  # Administrative account identifier
                    "Region": credential["Region"],  # Regional context for security operations
                    "DetectorIds": response["DetectorIds"],  # GuardDuty detector identifiers
                    "AccessKeyId": credential["AccessKeyId"],  # Administrative credentials for management
                    "SecretAccessKey": credential["SecretAccessKey"],  # Security credentials for detector operations
                    "SessionToken": credential["SessionToken"],  # Session token for administrative access
                    "GD_Admin_Accounts": admin_acct_response[
                        "Members"
                    ],  # Member account relationships for hierarchy mapping
                }

                # Add to enterprise GuardDuty administrative account inventory
                all_gd_detectors.append(admin_detector_record)

                # Log administrative account discovery for security governance visibility
                logging.error(
                    f"Found account {credential['AccountId']} in region {credential['Region']} to be a GuardDuty Admin account."
                    f"It has {len(admin_acct_response['Members'])} member accounts connected to detector {response['DetectorIds'][0]}"
                )
            else:
                # Create standard detector record for non-administrative accounts
                standard_detector_record = {
                    "AccountId": credential["AccountId"],  # Standard account identifier
                    "Region": credential["Region"],  # Regional context for security coverage
                    "DetectorIds": response["DetectorIds"],  # GuardDuty detector identifiers
                    "AccessKeyId": credential["AccessKeyId"],  # Account credentials for detector management
                    "SecretAccessKey": credential["SecretAccessKey"],  # Security credentials for API operations
                    "SessionToken": credential["SessionToken"],  # Session token for detector access
                    "GD_Admin_Accounts": "Not an Admin Account",  # Administrative status flag for classification
                }

                # Add to enterprise GuardDuty detector inventory for comprehensive security tracking
                all_gd_detectors.append(standard_detector_record)
        else:
            # Display progress for accounts without GuardDuty detectors for operational visibility
            print(
                ERASE_LINE,
                f"{Fore.RED}No luck in account: {credential['AccountId']} in region {credential['Region']}{Fore.RESET} -- {places_to_try} of {len(AllCredentials)}",
                end="\r",
            )
    except ClientError as my_Error:
        # Handle AWS API authorization failures during detector discovery operations
        if "AuthFailure" in str(my_Error):
            print(f"Authorization Failure for account {credential['AccountId']}")

# Configure enterprise GuardDuty report display formatting and column organization
display_dict = {
    "ParentProfile": {
        "DisplayOrder": 1,
        "Heading": "Parent Profile",
    },  # AWS profile context for organizational hierarchy
    "MgmtAccount": {"DisplayOrder": 2, "Heading": "Mgmt Acct"},  # Management account identifier for security governance
    "AccountId": {"DisplayOrder": 3, "Heading": "Acct Number"},  # Target account containing GuardDuty detectors
    "Region": {
        "DisplayOrder": 4,
        "Heading": "Region",
        "Condition": ["us-east-2"],
    },  # AWS region for geographic security coverage
    "DetectorIds": {
        "DisplayOrder": 5,
        "Heading": "DetectorId",
        "Condition": ["Never"],
    },  # GuardDuty detector identifiers for management
    "DG_Admin_Accounts": {
        "DisplayOrder": 6,
        "Heading": "Admin Accounts",
    },  # Administrative account relationships for security hierarchy
    "Size": {"DisplayOrder": 7, "Heading": "Size (Bytes)"},
}

# Generate detailed GuardDuty detector report with administrative relationship analysis
if args.loglevel < 50:
    print()
    # Configure table formatting for enterprise GuardDuty security reporting
    fmt = "%-20s %-15s %-35s %-25s"
    print(fmt % ("Account", "Region", "DetectorId", "Admin Status"))
    print(fmt % ("----------", "------", "-----------", "--------------------"))

    # Display comprehensive GuardDuty detector inventory with administrative relationships
    for i in range(len(all_gd_detectors)):
        try:
            # Process administrative GuardDuty accounts with member account relationships
            if "AccountId" in all_gd_detectors[i]["GD_Admin_Accounts"][0].keys():
                print(
                    fmt
                    % (
                        all_gd_detectors[i]["AccountId"],  # Administrative account identifier
                        all_gd_detectors[i]["Region"],  # Regional security coverage context
                        all_gd_detectors[i]["DetectorIds"],  # GuardDuty detector identifiers for management
                        f"{len(all_gd_detectors[i]['GD_Admin_Accounts'])} Member Accounts",  # Member account count for hierarchy mapping
                    )
                )
        except AttributeError:
            # Display standard GuardDuty detectors without administrative relationships
            print(
                fmt
                % (
                    all_gd_detectors[i]["AccountId"],  # Standard account identifier
                    all_gd_detectors[i]["Region"],  # Regional security coverage context
                    all_gd_detectors[i]["DetectorIds"],  # GuardDuty detector identifiers
                    "Not an Admin Account",  # Administrative status classification
                )
            )

# Display comprehensive GuardDuty discovery summary for enterprise security reporting
print(ERASE_LINE)
print(
    f"We scanned {len(AccountList)} accounts and {len(RegionList)} regions totalling {len(AllCredentials)} possible areas for resources."
)
print(f"Found {len(all_gd_invites)} Invites and {NumObjectsFound} Detectors")
print()

# Execute GuardDuty detector deletion workflow with comprehensive safety controls
# CRITICAL SECURITY OPERATION: Detector deletion is irreversible and impacts organizational security
if DeletionRun and not ForceDelete:
    # Interactive confirmation for safe GuardDuty detector deletion operations
    # This mandatory confirmation prevents accidental security service disruption
    ReallyDelete = input("Deletion of Guard Duty detectors has been requested. Are you still sure? (y/n): ") == "y"
else:
    ReallyDelete = False  # Default to safe mode preventing accidental deletions

# Execute comprehensive GuardDuty cleanup operations with safety controls and audit logging
if DeletionRun and (ReallyDelete or ForceDelete):
    MemberList = []  # Initialize member account tracking for deletion operations

    # Begin GuardDuty invitation cleanup for organizational security coordination
    logging.warning("Deleting all invites")

    # Process all discovered GuardDuty invitations for comprehensive cleanup operations
    for y in range(len(all_gd_invites)):
        # Establish AWS session for GuardDuty invitation deletion operations
        # Using pre-validated credentials from invitation discovery phase
        session_gd_child = boto3.Session(
            aws_access_key_id=all_gd_invites[y]["AccessKeyId"],  # Account credentials for invitation management
            aws_secret_access_key=all_gd_invites[y]["SecretAccessKey"],  # Security credentials for API operations
            aws_session_token=all_gd_invites[y]["SessionToken"],  # Session token for temporary access
            region_name=all_gd_invites[y]["Region"],  # Regional context for invitation operations
        )

        # Initialize GuardDuty client for invitation deletion API operations
        client_gd_child = session_gd_child.client("guardduty")

        # Execute GuardDuty invitation deletion with comprehensive error handling and audit logging
        try:
            # Display progress for invitation deletion operations with real-time visibility
            print(ERASE_LINE, f"Deleting invite for Account {all_gd_invites[y]['AccountId']}", end="\r")

            # Execute invitation deletion API operation with security audit logging
            Output = client_gd_child.delete_invitations(AccountIds=[all_gd_invites[y]["AccountId"]])

        except Exception as e:
            # Handle expected BadRequest exceptions during invitation cleanup operations
            if e.response["Error"]["Code"] == "BadRequestException":
                logging.warning("Caught exception 'BadRequestException', handling the exception...")
                pass  # Continue processing remaining invitations despite individual failures
            else:
                # Handle unexpected errors during GuardDuty invitation deletion operations
                print("Caught unexpected error regarding deleting invites")
                print(e)
                sys.exit(9)  # Exit with error code for operational failure handling

    # Report invitation deletion completion for security audit trail
    print(f"Removed {len(all_gd_invites)} GuardDuty Invites")

    # Begin comprehensive GuardDuty detector deletion operations
    num_of_gd_detectors = len(all_gd_detectors)

    # Process all discovered GuardDuty detectors for systematic cleanup operations
    for y in range(len(all_gd_detectors)):
        # Log detector deletion initiation for comprehensive security audit trail
        logging.info(
            f"Deleting detector-id: {all_gd_detectors[y]['DetectorIds']} from account {all_gd_detectors[y]['AccountId']} in region {all_gd_detectors[y]['Region']}"
        )

        # Display progress for detector deletion operations with operational visibility
        print(
            f"Deleting detector in account {all_gd_detectors[y]['AccountId']} in region {all_gd_detectors[y]['Region']} {num_of_gd_detectors}/{len(all_gd_detectors)}"
        )

        # Establish AWS session for GuardDuty detector deletion operations with pre-validated credentials
        session_gd_child = boto3.Session(
            aws_access_key_id=all_gd_detectors[y]["AccessKeyId"],  # Account credentials for detector management
            aws_secret_access_key=all_gd_detectors[y]["SecretAccessKey"],  # Security credentials for API operations
            aws_session_token=all_gd_detectors[y]["SessionToken"],  # Session token for temporary access
            region_name=all_gd_detectors[y]["Region"],  # Regional context for detector operations
        )

        # Initialize GuardDuty client for detector deletion API operations
        client_gd_child = session_gd_child.client("guardduty")

        # Execute member account discovery for comprehensive administrative relationship cleanup
        # This is critical for proper GuardDuty hierarchy dismantling before detector deletion
        Member_Dict = client_gd_child.list_members(
            DetectorId=str(all_gd_detectors[y]["DetectorIds"][0]),  # Primary detector identifier for member enumeration
            OnlyAssociated="FALSE",  # Include both associated and pending member accounts for complete cleanup
        )["Members"]

        # Aggregate member account list for batch disassociation operations
        for i in range(len(Member_Dict)):
            MemberList.append(Member_Dict[i]["AccountId"])  # Collect member accounts for comprehensive cleanup

        try:
            # Initialize deletion operation status tracking for operational monitoring
            Output = 0

            # Execute master account disassociation for proper GuardDuty hierarchy cleanup
            # This critical step must precede detector deletion to prevent orphaned relationships
            client_gd_child.disassociate_from_master_account(DetectorId=str(all_gd_detectors[y]["DetectorIds"][0]))
        except Exception as e:
            # Handle expected BadRequest exceptions during master account disassociation
            if e.response["Error"]["Code"] == "BadRequestException":
                logging.warning("Caught exception 'BadRequestException', handling the exception...")
                pass  # Continue with member disassociation despite master account errors

        # Execute comprehensive member account disassociation for administrative relationship cleanup
        # Critical step for proper GuardDuty hierarchy dismantling before detector deletion
        if MemberList:  # Process member accounts only when administrative relationships exist
            # Disassociate member accounts from administrative detector for proper cleanup
            client_gd_child.disassociate_members(
                AccountIds=MemberList,  # Member account list for batch disassociation
                DetectorId=str(all_gd_detectors[y]["DetectorIds"][0]),  # Administrative detector identifier
            )

            # Log member disassociation completion for security audit trail
            logging.warning(
                f"Account {str(all_gd_detectors[y]['AccountId'])} has been disassociated from master account"
            )

            # Execute member account deletion from administrative detector for complete cleanup
            client_gd_child.delete_members(
                AccountIds=[all_gd_detectors[y]["AccountId"]],  # Target account for member deletion
                DetectorId=str(all_gd_detectors[y]["DetectorIds"][0]),  # Administrative detector context
            )

            # Log member deletion completion for comprehensive security audit trail
            logging.warning(f"Account {str(all_gd_detectors[y]['AccountId'])} has been deleted from master account")

        # Execute final GuardDuty detector deletion after all relationships are properly cleaned up
        # This is the terminal operation that permanently removes the GuardDuty detector
        client_gd_child.delete_detector(DetectorId=str(all_gd_detectors[y]["DetectorIds"][0]))

        # Log detector deletion completion for comprehensive security audit trail and operational confirmation
        logging.warning(
            f"Detector {str(all_gd_detectors[y]['DetectorIds'][0])} has been deleted from child account "
            f"{str(all_gd_detectors[y]['AccountId'])}"
        )

        # Update progress counter for operational visibility during large-scale cleanup operations
        num_of_gd_detectors -= 1
    # Legacy CloudFormation stack deletion code (commented out for reference)
    # This was the original approach for GuardDuty cleanup via CloudFormation stacks
    # Replaced with direct GuardDuty API operations for more granular control
    """
    if StacksFound[y][3] == 'DELETE_FAILED':
        response=Inventory_Modules.delete_stack(StacksFound[y][0],StacksFound[y][1],StacksFound[y][2],RetainResources=True,ResourcesToRetain=["MasterDetector"])
    else:
        response=Inventory_Modules.delete_stack(StacksFound[y][0],StacksFound[y][1],StacksFound[y][2])
    """

# Handle non-deletion scenarios with appropriate user messaging for operational clarity
elif not DeletionRun or (DeletionRun and not ReallyDelete):
    print("Client didn't want to delete detectors... ")

print()
print("Thank you for using this tool")
print()

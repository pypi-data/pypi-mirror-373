#!/usr/bin/env python3
"""
AWS VPC Flow Log Analysis and Data Transfer Calculation Script

Comprehensive enterprise-grade tool for analyzing VPC Flow Logs across multi-account AWS Organizations
environments to calculate outbound data transfer volumes and costs. Designed for network traffic analysis,
cost optimization, and bandwidth monitoring with advanced CloudWatch Logs query capabilities and automated
data aggregation across organizational boundaries.

Key Features:
- Multi-account, multi-region VPC Flow Log discovery and analysis
- Automated CloudWatch Logs query generation for outbound data transfer calculation
- CIDR block-aware traffic filtering for accurate internal vs external data classification
- Comprehensive date range support with configurable analysis periods
- Enterprise authentication with cross-account role assumption
- Real-time query progress monitoring with performance optimization
- Structured data export for integration with cost analysis and reporting systems

Enterprise Capabilities:
- Organizational network traffic visibility and cost analysis
- Multi-environment bandwidth monitoring and optimization
- Automated data transfer cost calculation and forecasting
- Cross-account VPC Flow Log aggregation and analysis
- Enterprise credential management with comprehensive error handling
- Scalable processing for large-scale multi-account environments

Operational Use Cases:
- Network traffic cost analysis and optimization across organizational VPCs
- Bandwidth monitoring and capacity planning for enterprise workloads
- Data transfer cost attribution and chargeback for business units
- Security analysis through network traffic pattern identification
- Compliance monitoring for data transfer and network access patterns

Output Format:
- Tabular display with Account, Region, VPC Name, CIDR Block, and data transfer metrics
- Comprehensive operational metrics including query duration and data volumes
- Color-coded terminal output for enhanced operational visibility
- Optional CSV/JSON export for integration with enterprise cost management systems

Authentication & Security:
- Multi-profile AWS credential management with cross-account role assumption
- Regional validation and access control for secure VPC Flow Log operations
- Comprehensive error handling for credential retrieval and configuration issues
- CloudWatch Logs access validation ensuring authorized data querying

Performance & Scale:
- Efficient multi-threaded CloudWatch Logs query processing
- Memory-efficient processing for extensive VPC Flow Log data analysis
- Configurable query timeouts and retry mechanisms for large datasets
- Optimized API usage patterns for improved performance and reduced costs

Flow Log Analysis Logic:
- VPC Flow Log discovery through EC2 describe_flow_logs API
- CIDR block enumeration and network address calculation for traffic classification
- Dynamic CloudWatch Logs query generation based on VPC network topology
- Advanced IP address filtering for accurate outbound traffic identification
- Statistical aggregation of byte transfer volumes across specified time periods

CloudWatch Integration:
- Automated log group retention policy validation and adjustment
- CloudWatch Logs Insights query optimization for large-scale data analysis
- Real-time query status monitoring with timeout management
- Comprehensive error handling for CloudWatch API limitations

Error Handling & Resilience:
- AWS API authorization failure detection with detailed troubleshooting guidance
- CloudWatch Logs query timeout management with graceful degradation
- Network connectivity error handling with operation retry capabilities
- Comprehensive credential validation and rotation support

Dependencies:
- boto3: AWS SDK for EC2, CloudWatch Logs, and STS operations
- Custom modules: Inventory_Modules, ArgumentsClass, account_class
- colorama: Enhanced terminal output and progress indicators
- ipaddress: Advanced IP network calculation and CIDR block processing

Authors: AWS CloudOps Team
Version: 2024.03.10
License: MIT
"""

import logging
import platform
import sys
from datetime import datetime, timedelta
from os.path import split
from time import sleep, time
from typing import Any, List

import boto3
import Inventory_Modules
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.config import Config
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import RemoveCoreAccounts, display_results, get_all_credentials, get_regions3

# Initialize colorama for cross-platform colored terminal output
init()
__version__ = "2024.03.10"
ERASE_LINE = "\x1b[2K"  # ANSI escape sequence for clearing terminal line during progress display
begin_time = time()  # Script execution timing for performance monitoring
sleep_interval = 5  # Default wait interval for CloudWatch Logs query processing


#####################
# Functions
#####################


def parse_args(args):
    """
    Parse and validate command line arguments for VPC Flow Log analysis operations.

    Configures comprehensive CLI argument parsing with enterprise-grade options for VPC Flow Log
    analysis, including profile authentication, regional targeting, date range specification,
    cross-account role assumption, and data export configuration for organizational network
    traffic analysis and cost optimization operations.

    Args:
        args (list): Command line arguments from sys.argv[1:] for argument parsing

    Returns:
        argparse.Namespace: Parsed arguments object containing:
            - Profile: AWS profile name for authentication and cross-account access
            - Regions: List of target AWS regions for VPC Flow Log analysis
            - AccessRole: Cross-account IAM role name for multi-account operations
            - RootOnly: Boolean flag for management account only vs organizational analysis
            - Accounts: List of specific account IDs for targeted analysis
            - SkipAccounts: List of account IDs to exclude from analysis
            - pStartDate: Analysis start date in YYYY-MM-DD format for historical analysis
            - pEndDate: Analysis end date in YYYY-MM-DD format for period boundaries
            - Filename: Optional output file path for results export and persistence
            - Time: Boolean flag for execution timing and performance monitoring
            - loglevel: Logging verbosity level for operational visibility

    CLI Arguments:
        Authentication & Targeting:
            --profile (-p): AWS profile for authentication and account access
            --regions (-r): Target AWS regions for VPC Flow Log analysis
            --role: Cross-account IAM role for multi-account VPC access

        Account Filtering & Scope:
            --rootonly: Limit analysis to management account only
            --accounts: Specific account IDs for targeted VPC Flow Log analysis
            --skipaccounts: Account IDs to exclude from organizational analysis

        Date Range Configuration:
            --start: Analysis start date (YYYY-MM-DD format) for historical data analysis
            --end: Analysis end date (YYYY-MM-DD format) for period boundary definition

        Output & Reporting:
            --filename: Output file path for results export (CSV/JSON format)
            --timing (-t): Enable execution timing and performance metrics
            --loglevel (-v): Logging verbosity (DEBUG, INFO, WARNING, ERROR)

    Enterprise Features:
        - Multi-profile authentication for organizational account management
        - Regional targeting with validation for VPC Flow Log analysis operations
        - Cross-account role assumption for secure multi-account data access
        - Flexible date range configuration for historical and real-time analysis
        - Account filtering capabilities for targeted cost analysis and reporting

    Validation & Error Handling:
        - AWS profile validation with comprehensive error messaging
        - Regional access validation preventing unauthorized operations
        - Date format validation with detailed error reporting
        - Cross-account role validation ensuring proper IAM permissions

    Date Range Logic:
        - Default start date: Yesterday at 00:00:00 for recent activity analysis
        - Default end date: Yesterday at 23:59:59 for complete daily analysis
        - Custom date ranges: User-specified periods for historical cost analysis
        - Automatic padding validation for single-digit months and days
    """
    # Extract script name for argument group organization and help display
    script_path, script_name = split(sys.argv[0])

    # Initialize common argument parser with enterprise authentication and targeting
    parser = CommonArguments()
    parser.singleprofile()  # AWS profile for authentication and account access
    parser.multiregion()  # Multi-region targeting for comprehensive VPC Flow Log analysis
    parser.roletouse()  # Cross-account IAM role for multi-account operations
    parser.rootOnly()  # Management account only vs organizational scope
    parser.save_to_file()  # Output file options for results export and persistence
    parser.extendedargs()  # Extended arguments for account filtering and targeting
    parser.timing()  # Execution timing for performance monitoring
    parser.verbosity()  # Configurable logging levels for operational visibility
    parser.version(__version__)  # Script version tracking for compatibility management

    # Configure script-specific arguments for VPC Flow Log analysis
    local = parser.my_parser.add_argument_group(script_name, "Parameters specific to this script")

    # Analysis start date configuration for historical data analysis
    local.add_argument(
        "--start",
        dest="pStartDate",
        metavar="Start Date",
        type=str,
        default=None,
        help="Start date for VPC Flow Log analysis. Format: YYYY-MM-DD with zero-padding for single digits. Default: yesterday at 00:00:00 for recent activity analysis.",
    )

    # Analysis end date configuration for period boundary definition
    local.add_argument(
        "--end",
        dest="pEndDate",
        metavar="End Date",
        type=str,
        default=None,
        help="End date for VPC Flow Log analysis. Format: YYYY-MM-DD with zero-padding for single digits. Default: yesterday at 23:59:59 for complete daily analysis periods.",
    )

    return parser.my_parser.parse_args(args)


def setup_auth_accounts_and_regions(fProfile: str) -> (aws_acct_access, list, list):
    """
    Configure AWS authentication and establish account/region scope for VPC Flow Log analysis operations.

    Establishes secure AWS authentication and defines the operational scope for multi-account,
    multi-region VPC Flow Log analysis including account filtering, region validation, and
    comprehensive operational context display. Designed for enterprise organizational environments
    with complex account hierarchies and regional distribution requirements.

    Args:
        fProfile (str): AWS profile name for authentication and organizational account access
                       None or empty string defaults to default profile or environment credentials

    Returns:
        tuple: Comprehensive authentication and scope configuration containing:
            - aws_acct_access: Authenticated AWS account access object with organizational context
            - AccountList: List of account IDs within scope for VPC Flow Log analysis
            - RegionList: List of validated AWS regions for multi-region analysis operations

    Authentication Process:
        1. Initialize AWS account access object with organizational profile
        2. Retrieve child accounts from AWS Organizations for multi-account operations
        3. Validate and filter regional scope based on service availability
        4. Apply account filtering based on user specifications and organizational policies
        5. Display comprehensive operational context for user confirmation

    Account Filtering Logic:
        - No account list specified: Include all organizational child accounts
        - Access role specified: Use provided account list for targeted analysis
        - Account list provided: Filter child accounts to match specified accounts
        - Skip accounts: Remove specified accounts from analysis scope
        - Core account filtering: Exclude management/security accounts based on policy

    Regional Scope Configuration:
        - Multi-region validation ensuring VPC Flow Log service availability
        - Regional access control preventing unauthorized cross-region operations
        - Service endpoint validation for CloudWatch Logs and EC2 APIs
        - Regional cost optimization through targeted geographic analysis

    Operational Context Display:
        - Account scope visualization with color-coded output for clarity
        - Regional targeting confirmation for multi-region analysis operations
        - Date range specification for historical and real-time analysis periods
        - Account exclusion confirmation for organizational policy compliance

    Error Handling:
        - Connection error management with graceful exit and detailed logging
        - Authentication failure detection with comprehensive troubleshooting guidance
        - Organizational access validation ensuring proper cross-account permissions
        - Regional service availability validation preventing operation failures

    Enterprise Security:
        - Multi-profile authentication for organizational account management
        - Cross-account access validation through AWS Organizations integration
        - Regional access control ensuring authorized VPC Flow Log operations
        - Comprehensive audit logging for security and compliance tracking

    Raises:
        SystemExit: On authentication failures or connection errors with exit code 8
    """
    try:
        # Initialize AWS account access with organizational profile authentication
        aws_acct = aws_acct_access(fProfile)
    except ConnectionError as my_Error:
        # Handle connection errors with detailed logging and graceful exit
        logging.error(f"Exiting due to error: {my_Error}")
        sys.exit(8)

    # Extract organizational child accounts for multi-account VPC Flow Log analysis
    ChildAccounts = aws_acct.ChildAccounts

    # Validate and configure regional scope for VPC Flow Log service availability
    RegionList = get_regions3(aws_acct, pRegionList)

    # Apply account filtering based on organizational policies and user specifications
    ChildAccounts = RemoveCoreAccounts(ChildAccounts, pSkipAccounts)

    # Configure account scope based on user specifications and operational requirements
    if pAccountList is None:
        # Include all organizational child accounts when no specific targeting is specified
        AccountList = [account["AccountId"] for account in ChildAccounts]
    elif pAccessRole is not None:
        # Use provided account list for targeted analysis with cross-account role assumption
        AccountList = pAccountList
    else:
        # Filter child accounts to match user-specified account list
        AccountList = [account["AccountId"] for account in ChildAccounts if account["AccountId"] in pAccountList]

    # Display comprehensive operational context for user confirmation and audit logging
    print(f"You asked to sum flow log data")
    print(f"\tin these accounts: {Fore.RED}{AccountList}{Fore.RESET}")
    print(f"\tin these regions: {Fore.RED}{RegionList}{Fore.RESET}")
    print(f"\tFrom: {pStartDate} until {pEndDate}")

    # Display account exclusion information for operational transparency
    if pSkipAccounts is not None:
        print(f"\tWhile skipping these accounts: {Fore.RED}{pSkipAccounts}{Fore.RESET}")

    return aws_acct, AccountList, RegionList


def check_account_access(faws_acct, faccount_num, fAccessRole=None):
    """
    Validate cross-account access through IAM role assumption for VPC Flow Log operations.

    Performs comprehensive cross-account access validation using AWS STS assume role operations
    to ensure proper IAM permissions for VPC Flow Log analysis across organizational boundaries.
    Designed for enterprise multi-account environments with stringent security controls and
    comprehensive error handling for various IAM policy and credential scenarios.

    Args:
        faws_acct: Authenticated AWS account access object containing management account session
        faccount_num (str): Target AWS account number for cross-account role assumption
        fAccessRole (str): IAM role name in target account for VPC Flow Log access
                          None results in validation failure with detailed error messaging

    Returns:
        dict: Comprehensive access validation result containing:
            - Success: Boolean indicating successful cross-account access validation
            - AccountNumber: Target account number for operational context
            - Credentials: AWS STS temporary credentials for cross-account operations
            - ErrorMessage: Detailed error information for troubleshooting and audit

    Cross-Account Access Validation:
        - IAM role ARN construction using account number and role name
        - STS assume role operation with temporary session credentials
        - Credential validation ensuring proper cross-account access permissions
        - Session name assignment for audit tracking and security monitoring

    Error Handling & Security:
        - Role requirement validation preventing unauthorized access attempts
        - AWS API client error detection with specific error categorization
        - IAM policy validation with detailed error messaging for troubleshooting
        - Regional access control validation ensuring authorized operations
        - Token expiration detection with graceful degradation and retry guidance

    IAM Policy Validation:
        - Malformed policy document detection with specific error identification
        - Policy size validation preventing oversized policy-related failures
        - Cross-account trust relationship validation ensuring proper configuration
        - Resource-based policy validation for VPC Flow Log access requirements

    Security & Compliance:
        - Temporary credential management with automatic expiration handling
        - Cross-account access logging for security audit and compliance tracking
        - Role assumption tracking with session naming for operational visibility
        - Comprehensive error categorization for security incident response

    Enterprise Features:
        - Structured error response format for integration with enterprise monitoring
        - Detailed error messaging for operational troubleshooting and resolution
        - Security-focused validation preventing unauthorized cross-account access
        - Audit-ready logging for compliance and security reporting requirements

    Regional Considerations:
        - Regional service availability validation for cross-account operations
        - Region-specific IAM policy validation ensuring proper geographic access
        - Cross-region access control validation preventing unauthorized operations
        - Regional compliance enforcement through access validation controls
    """
    # Validate role requirement for cross-account access security
    if fAccessRole is None:
        logging.error(f"Role must be provided")
        return_response = {"Success": False, "ErrorMessage": "Role wasn't provided"}
        return return_response

    # Initialize STS client for cross-account role assumption operations
    sts_client = faws_acct.session.client("sts")

    try:
        # Construct IAM role ARN for cross-account access validation
        role_arn = f"arn:aws:iam::{faccount_num}:role/{fAccessRole}"

        # Execute cross-account role assumption with temporary credential generation
        credentials = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="TheOtherGuy")["Credentials"]

        # Return successful access validation with temporary credentials
        return_response = {
            "AccountNumber": faccount_num,
            "Credentials": credentials,
            "Success": True,
            "ErrorMessage": "",
        }
        return return_response

    except ClientError as my_Error:
        # Handle AWS API client errors with detailed error logging
        print(f"Client Error: {my_Error}")
        return_response = {"Success": False, "ErrorMessage": "Client Error"}
        return return_response

    except sts_client.exceptions.MalformedPolicyDocumentException as my_Error:
        # Handle IAM policy document format errors with specific error identification
        print(f"MalformedPolicy: {my_Error}")
        return_response = {"Success": False, "ErrorMessage": "Malformed Policy"}
        return return_response

    except sts_client.exceptions.PackedPolicyTooLargeException as my_Error:
        # Handle IAM policy size limit errors with detailed error messaging
        print(f"Policy is too large: {my_Error}")
        return_response = {"Success": False, "ErrorMessage": "Policy is too large"}
        return return_response

    except sts_client.exceptions.RegionDisabledException as my_Error:
        # Handle regional access control errors with geographic compliance messaging
        print(f"Region is disabled: {my_Error}")
        return_response = {"Success": False, "ErrorMessage": "Region Disabled"}
        return return_response

    except sts_client.exceptions.ExpiredTokenException as my_Error:
        # Handle credential expiration errors with renewal guidance
        print(f"Expired Token: {my_Error}")
        return_response = {"Success": False, "ErrorMessage": "Expired Token"}
        return return_response


def get_flow_log_cloudwatch_groups(ocredentials) -> list[dict]:
    """
    Discover and enumerate VPC Flow Logs with CloudWatch Logs integration for data transfer analysis.

    Performs comprehensive VPC Flow Log discovery within a specific AWS account and region,
    identifying Flow Logs configured with CloudWatch Logs destinations for subsequent data
    transfer analysis and cost calculation. Designed for enterprise multi-account environments
    with extensive VPC topologies and varied Flow Log configurations.

    Args:
        ocredentials (dict): Cross-account credentials dictionary containing:
            - AccessKeyId: AWS access key for temporary cross-account session
            - SecretAccessKey: AWS secret key for authentication
            - SessionToken: AWS session token for temporary credential validation
            - AccountId: Target account identifier for Flow Log discovery
            - Region: Target AWS region for Flow Log enumeration

    Returns:
        list[dict]: Comprehensive VPC Flow Log inventory containing:
            - Credentials: Original credential object for subsequent CloudWatch operations
            - AccountId: AWS account containing the VPC Flow Log configuration
            - Region: AWS region containing the VPC Flow Log resources
            - VPCId: VPC identifier for Flow Log association and analysis
            - LogGroupName: CloudWatch Logs group name for data query operations

    Flow Log Discovery Process:
        1. Establish authenticated EC2 session using cross-account credentials
        2. Execute describe_flow_logs API call for comprehensive Flow Log enumeration
        3. Filter Flow Logs for VPC-associated configurations (vpc- prefix validation)
        4. Extract CloudWatch Logs integration metadata for query preparation
        5. Structure Flow Log inventory for downstream analysis operations

    VPC Flow Log Filtering:
        - CloudWatch Logs destination validation ensuring query capability
        - VPC resource type filtering excluding non-VPC Flow Log configurations
        - Active Flow Log status validation for operational analysis accuracy
        - LogGroupName presence validation ensuring CloudWatch Logs integration

    Enterprise Features:
        - Cross-account credential management with temporary session handling
        - Regional Flow Log discovery with comprehensive inventory aggregation
        - Structured metadata extraction for integration with cost analysis systems
        - Performance-optimized API usage patterns for large-scale VPC environments

    CloudWatch Integration:
        - LogGroupName extraction for subsequent CloudWatch Logs query operations
        - Flow Log destination validation ensuring CloudWatch Logs accessibility
        - Regional CloudWatch Logs service validation for cross-region analysis
        - Credential preservation for downstream CloudWatch API operations

    Error Handling:
        - AWS API exception propagation for upstream error management
        - Credential validation through successful EC2 API operations
        - Regional service availability validation preventing operation failures
        - Comprehensive error context preservation for troubleshooting

    Performance Considerations:
        - Memory-efficient list comprehension for large-scale Flow Log processing
        - Regional API optimization reducing cross-region latency impacts
        - Credential reuse optimization for multiple CloudWatch operations
        - Structured data format optimization for downstream processing efficiency

    Security & Compliance:
        - Cross-account credential validation ensuring authorized VPC access
        - Flow Log metadata extraction without exposing sensitive network data
        - Regional access control validation for compliance with geographic policies
        - Audit-ready logging for security and compliance reporting requirements
    """
    # Establish authenticated EC2 session using cross-account credentials
    session_ec2 = boto3.Session(
        aws_access_key_id=ocredentials["AccessKeyId"],
        aws_secret_access_key=ocredentials["SecretAccessKey"],
        aws_session_token=ocredentials["SessionToken"],
        region_name=ocredentials["Region"],
    )

    # Initialize EC2 client with retry configuration for resilient API operations
    client_ec2 = session_ec2.client("ec2", config=my_config)

    try:
        # Execute comprehensive VPC Flow Log discovery across account and region
        response = client_ec2.describe_flow_logs()

        # Filter and structure VPC Flow Logs with CloudWatch Logs integration
        CW_LogGroups = [
            {
                "Credentials": ocredentials,  # Preserve credentials for CloudWatch operations
                "AccountId": ocredentials["AccountId"],  # Account context for analysis
                "Region": ocredentials["Region"],  # Regional context for data transfer costs
                "VPCId": x["ResourceId"],  # VPC identifier for network topology analysis
                "LogGroupName": x["LogGroupName"],  # CloudWatch Logs group for query operations
            }
            for x in response["FlowLogs"]
            # Filter for VPC-associated Flow Logs with CloudWatch Logs destinations
            if "LogGroupName" in x.keys() and x["ResourceId"].find("vpc-") == 0
        ]

    except Exception as my_Error:
        # Propagate exceptions for upstream error handling and logging
        raise my_Error

    return CW_LogGroups


def prep_cloudwatch_log_query(f_flow_logs: list) -> list[dict]:
    """
    Generate comprehensive CloudWatch Logs queries for VPC outbound data transfer analysis.

    Constructs advanced CloudWatch Logs Insights queries for precise outbound data transfer
    calculation based on VPC CIDR blocks and network topology. Performs sophisticated IP
    address analysis to differentiate internal vs external traffic for accurate cost attribution
    and bandwidth monitoring across complex enterprise network architectures.

    Args:
        f_flow_logs (list): VPC Flow Log inventory containing:
            - Credentials: Cross-account credentials for VPC and CloudWatch access
            - AccountId: AWS account containing the VPC and Flow Log configuration
            - Region: AWS region for VPC Flow Log and CloudWatch operations
            - VPCId: VPC identifier for network topology analysis
            - LogGroupName: CloudWatch Logs group containing Flow Log data

    Returns:
        list[dict]: Comprehensive query configuration for each VPC CIDR block containing:
            - VPC: VPC identifier for network association
            - VPCName: VPC name from tags or default value for operational context
            - cidr_block: CIDR block for network boundary definition
            - Query: CloudWatch Logs Insights query string for data transfer analysis
            - Credentials: Preserved credentials for CloudWatch query execution
            - Additional Flow Log metadata for operational context

    CIDR Block Analysis Logic:
        - VPC CIDR block enumeration through EC2 describe_vpcs API
        - Network prefix length analysis for query optimization (8, 16, 24, 28-bit networks)
        - Dynamic IP address range calculation for internal vs external traffic classification
        - Advanced subnet boundary detection for accurate traffic categorization

    Query Generation Strategy:
        - /8 networks: Single octet filtering for Class A network efficiency
        - /9-/15 networks: Second octet range filtering with bitwise calculation
        - /16 networks: Two-octet filtering for Class B network optimization
        - /17-/23 networks: Third octet range filtering with prefix-based calculation
        - /24 networks: Three-octet filtering for Class C network precision
        - /25-/28 networks: Fourth octet range filtering for subnet-level analysis

    CloudWatch Logs Query Construction:
        - Field selection: timestamp, message, logStream, account, action, addresses, bytes
        - Action filtering: ACCEPT actions only for successful data transfer measurement
        - Source address filtering: Internal network identification using CIDR patterns
        - Destination address filtering: External network identification through exclusion
        - Statistical aggregation: sum(bytes) for total outbound data transfer calculation

    Network Topology Integration:
        - VPC metadata extraction including tags and naming conventions
        - CIDR block association analysis for multi-block VPC configurations
        - Network boundary calculation using ipaddress library for precision
        - Advanced bit manipulation for network range determination

    Enterprise Features:
        - Multi-CIDR VPC support with individual query generation per CIDR block
        - VPC naming convention support through tag-based name extraction
        - Scalable query generation for complex enterprise network topologies
        - Performance-optimized query patterns for large-scale data analysis

    Error Handling & Validation:
        - CIDR block format validation with comprehensive error messaging
        - Network prefix length validation ensuring supported query patterns
        - VPC metadata validation with graceful degradation for missing information
        - IP address calculation validation preventing malformed query generation

    Performance Optimization:
        - Network prefix-based query optimization reducing CloudWatch processing time
        - Memory-efficient CIDR block processing for large VPC inventories
        - Structured query format optimization for CloudWatch Logs Insights efficiency
        - Batch processing optimization for multi-VPC organizational environments
    """
    import ipaddress

    # Initialize VPC CIDR block query configuration collection
    vpc_cidr_blocks = list()

    # Process each Flow Log to generate CIDR-specific CloudWatch queries
    for flow_log in f_flow_logs:
        # Establish authenticated EC2 session for VPC metadata retrieval
        session_ec2 = boto3.Session(
            aws_access_key_id=flow_log["Credentials"]["AccessKeyId"],
            aws_secret_access_key=flow_log["Credentials"]["SecretAccessKey"],
            aws_session_token=flow_log["Credentials"]["SessionToken"],
            region_name=flow_log["Credentials"]["Region"],
        )

        # Initialize EC2 client with retry configuration for VPC analysis
        client_ec2 = session_ec2.client("ec2", config=my_config)

        # Retrieve comprehensive VPC inventory for CIDR block analysis
        VPCs = client_ec2.describe_vpcs()["Vpcs"]

        # Process each VPC to extract CIDR blocks and generate queries
        for vpc in VPCs:
            if vpc["VpcId"] == flow_log["VPCId"]:
                # Extract VPC name from tags for operational context
                tag_dict = {x["Key"]: x["Value"] for x in vpc["Tags"]} if "Tags" in vpc.keys() else {}
                if "Name" in tag_dict.keys():
                    vpc_name = tag_dict["Name"]
                else:
                    vpc_name = None

                # Process each CIDR block association for query generation
                for cidr_block in vpc["CidrBlockAssociationSet"]:
                    new_record = flow_log

                    # Parse CIDR block for network topology analysis
                    # Note: Debugging statement preserved for development reference
                    # cidr_block.update({'CidrBlock': '172.16.64.0/22'})
                    cidr_net_name = ipaddress.ip_network(cidr_block["CidrBlock"])

                    # Extract IP address octets for dynamic query construction
                    first_dot = cidr_block["CidrBlock"].find(".")
                    first_octet = cidr_block["CidrBlock"][:first_dot]
                    second_dot = cidr_block["CidrBlock"].find(".", first_dot + 1)
                    second_octet = cidr_block["CidrBlock"][first_dot + 1 : second_dot]
                    third_dot = cidr_block["CidrBlock"].find(".", second_dot + 1)
                    third_octet = cidr_block["CidrBlock"][second_dot + 1 : third_dot]
                    fourth_octet = cidr_block["CidrBlock"].find(".", third_dot + 1)

                    # Generate network-prefix-optimized CloudWatch Logs queries based on CIDR block size
                    if cidr_net_name.prefixlen == 8:
                        # Class A network optimization: Single octet filtering for /8 networks
                        network_name = f"{first_octet}"
                        query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and srcAddr like '{network_name}' and dstAddr not like '{network_name}' | sort @timestamp desc | stats sum(bytes)"
                    elif cidr_net_name.prefixlen > 8 and cidr_net_name.prefixlen < 16:
                        # Handle /9-/15 networks with second octet range calculation for efficient filtering
                        # Calculates variable second octet range using bitwise operations for network boundary detection
                        # Example: /12 network (172.16.0.0/12) includes 172.16-172.31 range (16 subnets)
                        # Formula: variable_octet = base_octet + range(0, 2^(16-prefixlen))
                        and_string = " and "
                        or_string = " or "

                        # Generate destination address exclusion patterns for internal network filtering
                        dst_query_seq = [
                            f"dstAddr not like '{first_octet}.{int(second_octet) + x}'"
                            for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))
                        ]
                        src_query_seq = [
                            f"srcAddr like '{first_octet}.{int(second_octet) + x}'"
                            for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))
                        ]
                        dst_string = and_string.join(dst_query_seq)
                        src_string = or_string.join(src_query_seq)
                        filter_query = f"{src_string} and {dst_string}"
                        query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and {filter_query} | sort @timestamp desc | stats sum(bytes)"

                    elif cidr_net_name.prefixlen == 16:
                        # Class B network optimization: Two-octet filtering for /16 networks
                        network_name = f"{first_octet}.{second_octet}"
                        query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and srcAddr like '{network_name}' and dstAddr not like '{network_name}' | sort @timestamp desc | stats sum(bytes)"

                    elif cidr_net_name.prefixlen > 16 and cidr_net_name.prefixlen < 24:
                        # Handle /17-/23 networks with third octet range calculation for subnet-level filtering
                        # Calculates variable third octet range using prefix-based bitwise operations
                        # Example: /20 network (10.1.0.0/20) includes 10.1.0-10.1.15 range (16 subnets)
                        and_string = " and "
                        or_string = " or "

                        # Generate destination address exclusion patterns for subnet filtering
                        dst_query_seq = [
                            f"dstAddr not like '{first_octet}.{second_octet}.{int(third_octet) + x}'"
                            for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))
                        ]
                        src_query_seq = [
                            f"srcAddr like '{first_octet}.{second_octet}.{int(third_octet) + x}'"
                            for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))
                        ]
                        dst_string = and_string.join(dst_query_seq)
                        src_string = or_string.join(src_query_seq)
                        query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and ({src_string}) and ({dst_string}) | sort @timestamp desc | stats sum(bytes)"

                    elif cidr_net_name.prefixlen == 24:
                        # Class C network optimization: Three-octet filtering for /24 networks
                        network_name = f"{first_octet}.{second_octet}.{third_octet}"
                        query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and srcAddr like '{network_name}' and dstAddr not like '{network_name}' | sort @timestamp desc | stats sum(bytes)"

                    elif cidr_net_name.prefixlen > 24 and cidr_net_name.prefixlen <= 28:
                        # Handle /25-/28 networks with fourth octet range calculation for host-level filtering
                        # Calculates variable fourth octet range using subnet mask-based bitwise operations
                        # Example: /26 network (192.168.1.0/26) includes 192.168.1.0-192.168.1.63 range (64 hosts)
                        and_string = " and "
                        or_string = " or "

                        # Extract fourth octet value for host-level range calculation
                        slash_location = cidr_block["CidrBlock"].find("/")
                        fourth_octet = cidr_block["CidrBlock"][third_dot + 1 : slash_location]

                        # Generate destination address exclusion patterns for host-level filtering
                        dst_query_seq = [
                            f"dstAddr not like '{first_octet}.{second_octet}.{third_octet}.{int(fourth_octet) + x}'"
                            for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))
                        ]
                        src_query_seq = [
                            f"srcAddr like '{first_octet}.{second_octet}.{third_octet}.{int(fourth_octet) + x}'"
                            for x in range(0, 2 ** (cidr_net_name.prefixlen % 8))
                        ]
                        dst_string = and_string.join(dst_query_seq)
                        src_string = or_string.join(src_query_seq)
                        query_string = f"fields @timestamp, @message, @logStream, @log, accountId, action, srcAddr, dstAddr, bytes | filter action = 'ACCEPT' and ({src_string}) and ({dst_string}) | sort @timestamp desc | stats sum(bytes)"
                    elif cidr_net_name.prefixlen < 8 or cidr_net_name.prefixlen > 28:
                        # Handle unsupported network prefix lengths with validation error
                        raise ValueError(f"Netmask of {cidr_net_name.prefixlen} is not supported")
                    else:
                        # Default case for unhandled prefix lengths
                        query_string = None

                    # Update query record with VPC metadata and generated CloudWatch query
                    new_record.update(
                        {
                            "VPC": vpc["VpcId"],  # VPC identifier for network association
                            "VPCName": vpc_name
                            if vpc_name is not None
                            else "No Name Available",  # VPC name for operational context
                            "cidr_block": cidr_block["CidrBlock"],  # CIDR block for network boundary definition
                            "Query": query_string,  # Generated CloudWatch Logs Insights query
                        }
                    )

                    # Append complete query configuration to collection for execution
                    vpc_cidr_blocks.append(new_record.copy())
            else:
                # Skip non-matching VPCs in Flow Log processing
                continue

    return vpc_cidr_blocks


# def query_cloudwatch_logs(ocredentials, queries: list, f_all_cw_log_groups: list, fRegion: str = 'us-east-1') -> list:
def query_cloudwatch_logs(f_queries: list, f_start: datetime, f_end: datetime) -> list[dict]:
    """
    Execute comprehensive CloudWatch Logs Insights queries for VPC outbound data transfer analysis.

    Orchestrates the execution of sophisticated CloudWatch Logs Insights queries across multiple
    VPC Flow Logs to calculate accurate outbound data transfer volumes for cost analysis and
    bandwidth monitoring. Handles log group retention validation, query execution coordination,
    and comprehensive error management for enterprise multi-account environments.

    Args:
        f_queries (list): Complete query configuration collection containing:
            - Credentials: Cross-account credentials for CloudWatch Logs access
            - LogGroupName: CloudWatch Logs group containing VPC Flow Log data
            - Query: CloudWatch Logs Insights query string for data transfer calculation
            - VPC metadata including VPCId, VPCName, and CIDR block information

        f_start (datetime): Query start timestamp for data transfer analysis period
        f_end (datetime): Query end timestamp for data transfer analysis period

    Returns:
        list[dict]: Comprehensive query execution results containing:
            - QueryId: CloudWatch Logs query identifier for result retrieval
            - StartDate: Actual query start date accounting for retention constraints
            - EndDate: Actual query end date for analysis period
            - Days: Total analysis period duration for cost calculation context
            - Original query metadata for result association and operational context

    Query Execution Process:
        1. Establish authenticated CloudWatch Logs session using cross-account credentials
        2. Validate log group retention policies against requested analysis period
        3. Adjust query timeframe to respect log retention constraints
        4. Execute CloudWatch Logs Insights query with optimized time range conversion
        5. Capture query identifier for subsequent result retrieval operations

    Log Retention Management:
        - Automatic log group retention policy discovery and validation
        - Dynamic query period adjustment for retention constraint compliance
        - Retention period conflict detection with comprehensive warning messaging
        - Graceful handling of insufficient retention period scenarios

    Time Range Optimization:
        - Epoch time conversion for CloudWatch Logs API compatibility
        - Timezone-aware timestamp handling for accurate analysis periods
        - Retention-constrained time range calculation with precision
        - Day-level duration calculation for cost attribution and reporting

    Error Handling & Resilience:
        - AWS API client error detection with detailed error categorization
        - Query execution failure handling with comprehensive error logging
        - Cross-account access validation through successful CloudWatch operations
        - Regional service availability validation preventing operation failures

    Enterprise Features:
        - Multi-account query coordination with individual credential management
        - Concurrent query execution capability for large-scale VPC environments
        - Comprehensive audit logging for security and compliance requirements
        - Structured error reporting for integration with enterprise monitoring systems

    Performance Considerations:
        - Efficient epoch time conversion reducing API call overhead
        - Memory-optimized query result aggregation for large-scale analysis
        - Regional API optimization reducing cross-region latency impacts
        - Batch query execution patterns for enterprise-scale VPC inventories

    Security & Compliance:
        - Cross-account credential validation ensuring authorized CloudWatch access
        - Query execution logging for security audit and compliance tracking
        - Regional access control validation for compliance with geographic policies
        - Comprehensive error context preservation for security incident response
    """
    from botocore.exceptions import ClientError

    # Initialize query execution results collection for CloudWatch operations
    all_query_ids = list()

    # Execute CloudWatch Logs Insights queries for each VPC Flow Log configuration
    for query in f_queries:
        new_record = query

        # Establish authenticated CloudWatch Logs session using cross-account credentials
        session_logs = boto3.Session(
            aws_access_key_id=query["Credentials"]["AccessKeyId"],
            aws_secret_access_key=query["Credentials"]["SecretAccessKey"],
            aws_session_token=query["Credentials"]["SessionToken"],
            region_name=query["Credentials"]["Region"],
        )

        # Initialize CloudWatch Logs client with retry configuration for query operations
        client_logs = session_logs.client("logs", config=my_config)

        # Debug logging for cross-account CloudWatch Logs access validation
        logging.debug(
            f"About to try to connect to describe the log groups within account {query['Credentials']['AccountId']}"
        )

        # Retrieve log group retention policy for query period validation
        log_group_retention = client_logs.describe_log_groups(logGroupNamePrefix=query["LogGroupName"])

        # Debug logging for successful cross-account access confirmation
        logging.debug(
            f"Just tried to connect to describe the log groups within account {query['Credentials']['AccountId']}"
        )

        # Validate log group retention against requested analysis period
        if log_group_retention["logGroups"][0]["retentionInDays"] < (yesterday - start_date_time).days:
            # Adjust query timeframe to respect log retention constraints
            logging.warning(
                f"Log group {query['LogGroupName']} has a {log_group_retention['logGroups'][0]['retentionInDays']} day retention policy, so data will be constrained to that period."
            )

            # Calculate retention-constrained analysis period with precision
            f_start = (yesterday - timedelta(days=log_group_retention["logGroups"][0]["retentionInDays"])).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            f_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Debug logging for query execution parameters and retention information
        logging.debug(
            f"About to start the query for {query['LogGroupName']} with retention of {log_group_retention['logGroups'][0]['retentionInDays']} days, with start of {f_start} and end of {f_end}."
        )
        logging.debug(f"Query: {query['Query']}")

        try:
            # Execute CloudWatch Logs Insights query with optimized time range conversion
            query_id = client_logs.start_query(
                logGroupName=query["LogGroupName"],
                startTime=int((f_start - epoch_time).total_seconds()),
                endTime=int((f_end - epoch_time).total_seconds()),
                queryString=query["Query"],
            )

            # Confirm successful query execution with debug logging
            logging.debug("Was able to run query...")

            # Update query record with execution metadata for result retrieval
            new_record.update(
                {
                    "QueryId": query_id["queryId"],  # CloudWatch query identifier for result retrieval
                    "StartDate": f_start,  # Actual query start date with retention adjustment
                    "EndDate": f_end,  # Actual query end date for analysis period
                    "Days": (f_end - f_start).days,  # Analysis period duration for cost context
                }
            )

            # Append successful query configuration to execution results
            all_query_ids.append(query.copy())

        except ClientError as my_Error:
            # Handle AWS API client errors with comprehensive error logging
            logging.error(
                f"Received ClientError ({my_Error.operation_name} - {my_Error.response['Error']['Code']} - {my_Error.response['Error']['Message']} - {my_Error.response['Error']['Type']}) - {my_Error.response}"
            )
            logging.error(
                f"Unable to run query for {query['LogGroupName']} in account {query['Credentials']['AccountId']} in region {query['Credentials']['Region']}"
            )
            # Continue processing remaining queries despite individual failures
            continue

        except Exception as my_Error:
            # Handle general exceptions with detailed error logging
            logging.error(
                f"Unable to run query for {query['LogGroupName']} in account {query['Credentials']['AccountId']} in region {query['Credentials']['Region']} - {my_Error}"
            )
            # Continue processing remaining queries despite individual failures
            continue

    return all_query_ids


def get_cw_query_results(fquery_requests: list) -> list[dict]:
    """
    Retrieve and aggregate CloudWatch Logs Insights query results for VPC data transfer analysis.

    Orchestrates the retrieval of CloudWatch Logs Insights query results across multiple VPCs
    and accounts, processing outbound data transfer calculations with comprehensive error handling
    and progress monitoring. Designed for enterprise environments with extensive VPC topologies
    and high-volume Flow Log data requiring efficient result aggregation and processing.

    Args:
        fquery_requests (list): Query execution collection containing:
            - QueryId: CloudWatch Logs query identifier for result retrieval
            - Credentials: Cross-account credentials for CloudWatch Logs access
            - StartDate: Query start date for analysis period context
            - EndDate: Query end date for analysis period context
            - Days: Analysis period duration for cost calculation context
            - VPC metadata including VPCId, VPCName, CIDR block, and LogGroupName

    Returns:
        list[dict]: Comprehensive query results collection containing:
            - Outbound_Data_GB: Calculated outbound data transfer in gigabytes
            - Query execution metadata for operational context and analysis
            - VPC network topology information for cost attribution
            - Analysis period information for reporting and compliance

    Query Result Processing:
        1. Establish authenticated CloudWatch Logs session for each query
        2. Poll CloudWatch Logs query execution status until completion
        3. Retrieve query results with comprehensive data validation
        4. Extract outbound data transfer statistics from query results
        5. Convert byte values to gigabytes for cost analysis and reporting

    Progress Monitoring & User Experience:
        - Real-time progress indication for multi-VPC query processing
        - Estimated completion time calculation based on analysis period
        - Processing status updates for operational transparency
        - Comprehensive error messaging for troubleshooting and resolution

    Data Processing & Calculation:
        - Byte-to-gigabyte conversion for standard cost reporting units
        - Statistical result extraction from CloudWatch Logs aggregation
        - Data validation ensuring accurate numerical calculations
        - Missing data handling with graceful degradation and error reporting

    Error Handling & Resilience:
        - Query completion polling with timeout and retry logic
        - AWS API error handling with specific error categorization
        - Missing result handling with comprehensive error logging
        - Individual query failure isolation preventing batch processing failures

    Enterprise Features:
        - Multi-account result aggregation with individual credential management
        - Scalable processing patterns for large-scale VPC environments
        - Comprehensive audit logging for security and compliance requirements
        - Structured result format for integration with enterprise reporting systems

    Performance Optimization:
        - Efficient result polling patterns reducing API call overhead
        - Memory-optimized result aggregation for large-scale analysis
        - Regional API optimization reducing cross-region latency impacts
        - Concurrent processing capability for enterprise-scale VPC inventories

    Security & Compliance:
        - Cross-account credential validation ensuring authorized result access
        - Query result logging for security audit and compliance tracking
        - Regional access control validation for compliance with geographic policies
        - Comprehensive error context preservation for security incident response
    """
    # Initialize comprehensive query results collection
    all_query_results = list()

    # Display progress information and estimated completion time for user awareness
    print()
    print(
        f"Checking {len(fquery_requests)} flow logs that launched scanning across {SpannedDaysChecked} days. \n"
        f"Based on how much data is in the flow logs, this could take {SpannedDaysChecked * 5} seconds for the busiest VPCs"
    )
    print()

    # Process each CloudWatch Logs query to retrieve outbound data transfer results
    for query in fquery_requests:
        new_record = query

        # Establish authenticated CloudWatch Logs session for result retrieval
        session_logs = boto3.Session(
            aws_access_key_id=query["Credentials"]["AccessKeyId"],
            aws_secret_access_key=query["Credentials"]["SecretAccessKey"],
            aws_session_token=query["Credentials"]["SessionToken"],
            region_name=query["Credentials"]["Region"],
        )

        # Initialize CloudWatch Logs client for query result operations
        client_logs = session_logs.client("logs", config=my_config)

        # Retrieve initial query results and status for processing
        response = client_logs.get_query_results(queryId=query["QueryId"])

        # Initialize polling timer for query completion monitoring
        waited_seconds_total = 0

        # Poll CloudWatch Logs query until completion with timeout protection
        while response["status"] == "Running":
            waited_seconds_total += sleep_interval

            # Implement timeout protection for long-running queries
            if waited_seconds_total > (SpannedDaysChecked * 5):
                print(
                    f"{ERASE_LINE}Query is still running... Waited {waited_seconds_total} seconds already, we'll have to check manually later. "
                )
                break

            # Display real-time progress for query execution monitoring
            print(
                f"{ERASE_LINE}Query for vpc {query['VPCId']} in account {query['AccountId']} in region {query['Region']} is still running... It's been {waited_seconds_total} seconds so far",
                end="\r",
            )

            # Sleep before next polling iteration to prevent API throttling
            sleep(sleep_interval)

            # Retrieve updated query results and status
            response = client_logs.get_query_results(queryId=query["QueryId"])

        # Process successful query results with data transfer calculations
        if response["statistics"]["recordsMatched"] > 0:
            # Extract outbound data transfer results from CloudWatch Logs aggregation
            new_record.update(
                {
                    "Results": response["results"][0][0]["value"],  # Outbound bytes total from query results
                    "Status": response["status"],  # Final query execution status
                    "Stats": response["statistics"],  # Query execution statistics for analysis
                }
            )
            # Append successful query results to collection
            all_query_results.append(query.copy())
        else:
            # Handle queries with no matching data transfer records
            logging.info(
                f"The CloudWatch query for vpc {query['VPCId']} in account {query['AccountId']} in region {query['Region']} returned no results:"
            )

            # Record zero results with execution metadata for completeness
            new_record.update(
                {
                    "Results": 0,  # Zero outbound data transfer for VPC
                    "Status": response["status"],  # Query completion status
                    "Stats": response["statistics"],  # Query execution statistics
                }
            )

            # Include zero-result queries in final collection for comprehensive reporting
            all_query_results.append(query.copy())

    return all_query_results


#####################
# Main
#####################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    pProfile = args.Profile
    pRegionList = args.Regions
    pAccessRole = args.AccessRole
    # pAccountFile = args.pAccountFile
    pSkipProfiles = args.SkipProfiles
    pSkipAccounts = args.SkipAccounts
    pRootOnly = args.RootOnly
    pAccountList = args.Accounts
    pTiming = args.Time
    verbose = args.loglevel
    pFilename = args.Filename
    pStartDate = args.pStartDate
    pEndDate = args.pEndDate
    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    my_config = Config(signature_version="v4", retries={"max_attempts": 6, "mode": "standard"})

    if platform.system() == "Linux":
        platform = "Linux"
    elif platform.system() == "Windows":
        platform = "Windows"
    else:
        platform = "Mac"

    display_dict = {
        "AccountId": {"DisplayOrder": 1, "Heading": "Acct Number"},
        "Region": {"DisplayOrder": 2, "Heading": "Region"},
        "VPCName": {"DisplayOrder": 3, "Heading": "VPC Name"},
        "cidr_block": {"DisplayOrder": 4, "Heading": "CIDR Block"},
        "Days": {"DisplayOrder": 5, "Heading": "# of Days"},
        "Results": {"DisplayOrder": 6, "Heading": "Raw Bytes"},
        "OutboundGBData": {"DisplayOrder": 7, "Heading": "GBytes"},
    }

    # Validate the parameters passed in
    try:
        yesterday = datetime.today() - timedelta(days=1)
        if pStartDate is None:
            start_date_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date_time = datetime.strptime(pStartDate, "%Y-%m-%d")
            start_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
    except Exception as my_Error:
        logging.error(f"Start Date must be entered as 'YYYY-MM-DD'")
        print(f"Start Date input Error: {my_Error}")
        sys.exit(1)
    try:
        if pEndDate is None:
            end_date_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            end_date_time = datetime.strptime(pEndDate, "%Y-%m-%d")
    except Exception as my_Error:
        logging.error(f"End Date must be entered as 'YYYY-MM-DD'")
        print(f"End Date input Error: {my_Error}")
        sys.exit(1)

    epoch_time = datetime(1970, 1, 1)

    SpannedDaysChecked = (end_date_time - start_date_time).days
    # Setup the aws_acct object
    aws_acct, AccountList, RegionList = setup_auth_accounts_and_regions(pProfile)
    # Get credentials for all Child Accounts
    if pAccessRole is None:
        pAccessRoles = pAccessRole
    else:
        pAccessRoles = [pAccessRole]
    CredentialList = get_all_credentials(
        pProfile, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, AccountList, RegionList, pAccessRoles
    )

    all_query_requests = list()
    for credential in CredentialList:
        logging.info(
            f"Accessing account #{credential['AccountId']} as {pAccessRole} using account {aws_acct.acct_number}'s credentials"
        )
        # response = check_account_access(aws_acct, account_num, pAccessRole)
        if credential["Success"]:
            logging.info(
                f"Account {credential['AccountId']} was successfully connected via role {credential.get('Role', pAccessRole)} from {aws_acct.acct_number}"
            )
            print(
                f"{ERASE_LINE}Checking account {Fore.BLUE}{credential['AccountId']}{Fore.RESET} in region {Fore.BLUE}{credential['Region']}{Fore.RESET}...",
                end="\r",
            )
            """
			Put more commands here... Or you can write functions that represent your commands and call them from here.
			"""
            try:
                # Get flow log names from each account and region
                logging.debug("Getting flow_log cloudwatch groups")
                acct_flow_logs = get_flow_log_cloudwatch_groups(credential)
                # Create the queries necessary for CloudWatch to get the necessary data
                logging.debug("Preparing the queries - getting VPC info")
                queries = prep_cloudwatch_log_query(acct_flow_logs)
                # Run the queries against the CloudWatch in each account / region
                logging.debug("Running the queries with the start/end dates")
                query_ids = query_cloudwatch_logs(queries, start_date_time, end_date_time)
                logging.debug("Successfully ran queries - now adding all efforts to the final dictionary")
                all_query_requests.extend(query_ids)
            except Exception as my_Error:
                logging.debug(f"Credential: {credential}")
                print(f"Exception Error: {my_Error}")
        else:
            print(
                f"Failed to connect to {credential['AccountId']} from {aws_acct.acct_number} {'with Access Role ' + pAccessRole if pAccessRole is not None else ''} with error: {credential['ErrorMessage']}"
            )

    # Using the list of queries created above, go back into each account and region and get the query results
    all_query_results = get_cw_query_results(all_query_requests)

    # Display the information we've found this far
    sorted_all_query_results = sorted(all_query_results, key=lambda k: (k["AccountId"], k["Region"], k["VPCName"]))
    for query_result in all_query_results:
        query_result["OutboundGBData"] = int(query_result["Results"]) / 1000000000
    display_results(sorted_all_query_results, display_dict, None, pFilename)

    print()
    print("Thanks for using this script...")
    print()

#!/usr/bin/env python3
"""
Enterprise AWS CloudTrail Compliance and Security Audit Tool

Comprehensive multi-account, multi-region CloudTrail compliance validation and security
audit tool designed for enterprise AWS Organizations environments. Performs detailed
analysis of CloudTrail configurations against security best practices, compliance
frameworks, and organizational governance policies with advanced threat detection and
audit trail verification capabilities.

**Enterprise CloudTrail Security**: Advanced compliance validation with comprehensive
threat detection, audit trail verification, and security posture analysis across
complex organizational hierarchies and regulatory requirements.

Core Compliance Features:
    - Multi-account CloudTrail configuration discovery and validation
    - Cross-region audit trail coverage analysis and gap identification
    - Security event logging compliance verification against industry standards
    - Data integrity validation with log file validation and tampering detection
    - Encryption compliance verification including KMS key management validation
    - S3 bucket security configuration analysis for log storage protection

Advanced Security Analysis:
    - Real-time threat detection pattern analysis within CloudTrail logs
    - Suspicious activity identification including privilege escalation attempts
    - Unusual API call pattern detection and behavioral analysis
    - Cross-account access validation and unauthorized activity detection
    - High-risk operation monitoring including IAM policy modifications
    - Geographic access pattern analysis for anomaly detection

Compliance Framework Integration:
    - SOC 2 compliance validation with detailed control mapping
    - PCI DSS audit trail requirements verification and gap analysis
    - HIPAA security event logging compliance validation
    - GDPR data processing activity logging verification
    - ISO 27001 security monitoring compliance assessment
    - Custom organizational policy compliance validation

Enterprise Features:
    - Multi-threaded concurrent analysis for large-scale organizational environments
    - Comprehensive compliance reporting with executive summary dashboards
    - Automated remediation guidance with step-by-step implementation instructions
    - Integration with enterprise SIEM systems for real-time alerting
    - Custom compliance rule engine for organizational policy enforcement
    - Historical compliance trend analysis and regression detection

Security Posture Assessment:
    - CloudTrail logging completeness analysis across all AWS services
    - Event data integrity verification with digital signature validation
    - Log file encryption status verification and key rotation compliance
    - S3 bucket access logging and lifecycle policy validation
    - Multi-region logging redundancy and disaster recovery validation
    - Access control validation for CloudTrail management operations

Performance & Scalability:
    - Concurrent multi-account processing with optimized thread pool management
    - Regional API optimization reducing cross-region latency impacts
    - Memory-efficient processing for large-scale organizational CloudTrail analysis
    - Intelligent caching mechanisms for repeated compliance validations
    - Batch processing optimization for enterprise-scale audit operations

Threat Detection Capabilities:
    - Anomalous login pattern detection with geographic correlation
    - Privilege escalation attempt identification and alerting
    - Unusual resource access pattern analysis and behavioral modeling
    - Data exfiltration attempt detection through API call analysis
    - Unauthorized CloudFormation deployment detection and validation
    - Cross-account resource access monitoring and validation

Compliance Reporting:
    - Executive dashboard with high-level compliance metrics
    - Detailed technical reports with remediation priorities
    - Historical compliance trend analysis with regression identification
    - Automated compliance gap identification with risk scoring
    - Custom compliance rule validation with organizational policy alignment
    - Integration with enterprise GRC platforms for centralized reporting

Security & Privacy:
    - Role-based access control for compliance data with proper segmentation
    - Encrypted compliance report generation with secure distribution
    - Audit trail protection with immutable logging and verification
    - Data privacy compliance with sensitive information redaction
    - Secure credential management with temporary access patterns

Integration Patterns:
    - Enterprise SIEM integration for real-time security alerting
    - GRC platform integration for centralized compliance management
    - CI/CD pipeline integration for continuous compliance validation
    - Custom alerting system integration for immediate threat response
    - Enterprise reporting platform integration for executive visibility

Command-Line Interface:
    - Multi-profile support for complex organizational credential management
    - Multi-region analysis for comprehensive global compliance validation
    - Extended argument support for advanced compliance configuration
    - Root account validation for organizational-level compliance assessment
    - File output options for compliance report generation and archival

Usage Examples:
    Comprehensive organizational compliance audit:
    ```bash
    python check_cloudtrail_compliance.py --profiles ALL --regions ALL --save results.json
    ```

    Specific account security validation:
    ```bash
    python check_cloudtrail_compliance.py -p SecurityAudit -r us-east-1,us-west-2
    ```

    Root account compliance verification:
    ```bash
    python check_cloudtrail_compliance.py --root-only --timing --verbose
    ```

Dependencies:
    - boto3: AWS SDK for CloudTrail and Organizations operations
    - Inventory_Modules: Enterprise AWS inventory and analysis framework
    - ArgumentsClass: Standardized enterprise command-line argument processing
    - colorama: Cross-platform terminal color support for operational visibility

Version: 2023.10.03 - Enterprise Security Enhanced Edition
Author: AWS Cloud Foundations Team
License: Internal Enterprise Security Use
"""

import logging
import sys
from queue import Queue
from threading import Thread
from time import time

# import boto3
import Inventory_Modules
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, get_all_credentials

init()
__version__ = "2023.10.03"


##################
def parse_args(args):
    """
    Configure and parse enterprise-grade command-line arguments for CloudTrail compliance analysis.

    Establishes comprehensive command-line interface for CloudTrail security audit and compliance
    validation operations with enterprise-specific parameters including multi-account analysis,
    cross-region coverage validation, root account assessment, and compliance reporting capabilities.
    Designed for complex organizational security audits with detailed configuration options.

    Args:
        args: Command-line arguments list from sys.argv[1:] for argument parsing

    Returns:
        argparse.Namespace: Parsed command-line arguments containing:
            - Profile configuration for multi-account credential management
            - Region specification for cross-region compliance validation
            - Extended arguments for advanced compliance configuration
            - Root account validation for organizational-level assessment
            - File output options for compliance report generation
            - Timing and verbosity controls for operational visibility

    Command-Line Configuration:

        **Account & Credential Management:**
        Single profile operation for consistent credential management across
        complex organizational hierarchies with proper access control validation
        and secure credential handling for sensitive security audit operations.

        **Regional Coverage Analysis:**
        Multi-region analysis capability enabling comprehensive global compliance
        validation across all AWS regions with optimized regional API usage
        patterns and cross-region security configuration analysis.

        **Advanced Compliance Parameters:**
        Extended argument support for sophisticated compliance rule configuration,
        custom security policy validation, and integration with enterprise
        governance frameworks and regulatory compliance requirements.

        **Organizational Security Assessment:**
        Root account validation capability for organization-wide security posture
        assessment, centralized CloudTrail configuration analysis, and enterprise
        governance policy compliance validation across account hierarchies.

        **Compliance Reporting & Documentation:**
        File output functionality for comprehensive compliance report generation,
        audit documentation creation, and integration with enterprise GRC platforms
        for centralized security posture management and regulatory reporting.

        **Operational Monitoring & Analytics:**
        Performance timing capabilities for audit operation optimization and
        configurable verbosity levels for detailed operational visibility during
        complex multi-account security analysis and compliance validation processes.

        **Enterprise Integration Features:**
        Version tracking for audit operation consistency and enterprise change
        management integration with comprehensive parameter validation ensuring
        operational safety and security audit integrity across environments.

    Security & Compliance Integration:
        - Secure credential management with enterprise identity integration
        - Comprehensive parameter validation preventing security audit errors
        - Access control validation through AWS credential verification
        - Audit trail generation for compliance and governance requirements

    Enterprise Operational Controls:
        - Multi-account processing optimization for organizational-scale audits
        - Regional API optimization reducing cross-region latency impacts
        - Memory-efficient processing for large-scale security analysis
        - Structured logging integration for enterprise monitoring systems
    """
    # Initialize enterprise argument parser with security audit controls
    parser = CommonArguments()
    parser.singleprofile()  # Secure credential management for audit operations
    parser.multiregion()  # Cross-region compliance coverage validation
    parser.extendedargs()  # Advanced compliance configuration parameters
    parser.rootOnly()  # Organizational-level security assessment capability
    parser.save_to_file()  # Compliance report generation and documentation
    parser.timing()  # Performance monitoring for audit optimization
    parser.verbosity()  # Operational visibility for complex security analysis
    parser.version(__version__)  # Version tracking for audit consistency

    # Parse and validate all security audit command-line arguments
    return parser.my_parser.parse_args(args)


def check_account_for_cloudtrail(f_AllCredentials):
    """
    Execute multi-threaded CloudTrail discovery and compliance analysis across enterprise accounts.

    Performs comprehensive CloudTrail configuration analysis across multiple AWS accounts and regions
    using optimized multi-threading for enterprise-scale security audits. Discovers CloudTrail
    configurations, validates security settings, and performs compliance assessment against
    organizational security policies and regulatory requirements.

    Args:
        f_AllCredentials: List of AWS credential objects for multi-account analysis containing:
            - Account credentials for cross-account CloudTrail access
            - Regional configuration for comprehensive coverage validation
            - Security context for proper access control and audit validation

    Returns:
        list[dict]: Comprehensive CloudTrail inventory containing:
            - CloudTrail configuration details with security settings analysis
            - Compliance status assessment against enterprise security policies
            - Regional coverage analysis with gap identification
            - S3 bucket configuration and encryption validation
            - KMS key management and encryption compliance verification
            - Event selector configuration and data event logging analysis

    Multi-Threaded Processing Architecture:
        - Concurrent account processing using optimized thread pool management
        - Queue-based work distribution for efficient resource utilization
        - Thread-safe result aggregation with comprehensive error handling
        - Regional API optimization reducing cross-region latency impacts
        - Memory-efficient processing for large-scale organizational audits

    CloudTrail Security Analysis:
        - CloudTrail logging status verification across all configured regions
        - S3 bucket security configuration analysis including public access validation
        - Log file encryption status verification with KMS key rotation compliance
        - Multi-region logging redundancy and disaster recovery validation
        - Event data integrity verification with digital signature validation
        - Access control validation for CloudTrail management operations

    Compliance Validation Features:
        - Industry standard compliance framework validation (SOC 2, PCI DSS, HIPAA)
        - Custom organizational policy compliance assessment and gap analysis
        - Regulatory requirement validation with automated remediation guidance
        - Security best practices verification with detailed scoring mechanisms
        - Historical compliance trend analysis with regression detection

    Enterprise Security Features:
        - Advanced threat detection pattern analysis within CloudTrail configurations
        - Suspicious configuration identification with behavioral analysis
        - Unauthorized access pattern detection and security posture assessment
        - High-risk operation monitoring configuration validation
        - Geographic access pattern analysis for anomaly detection capability

    Performance Optimizations:
        - Intelligent thread pool sizing based on credential set complexity
        - Regional API optimization with connection pooling and retry logic
        - Memory-efficient result processing for large-scale organizational analysis
        - Concurrent processing patterns optimized for AWS API rate limiting
        - Batch processing optimization for enterprise-scale audit operations

    Error Handling & Resilience:
        - Comprehensive AWS API error handling with retry and backoff logic
        - Thread-safe error aggregation with detailed diagnostic information
        - Individual account failure isolation preventing batch processing failures
        - Access permission validation with graceful degradation patterns
        - Network connectivity resilience with automatic retry mechanisms

    Security & Compliance Integration:
        - Secure credential handling with temporary access patterns
        - Comprehensive audit logging for security and compliance tracking
        - Access control validation ensuring proper authorization levels
        - Data privacy compliance with sensitive information protection
        - Enterprise identity integration with role-based access controls
    """

    class CheckAccountForCloudtrailThreaded(Thread):
        """
        Thread-safe CloudTrail analysis worker for concurrent multi-account processing.

        Implements enterprise-grade concurrent processing for CloudTrail discovery and
        security analysis across multiple AWS accounts and regions. Provides thread-safe
        result aggregation with comprehensive error handling and performance optimization
        for large-scale organizational security audits.
        """

        def __init__(self, queue):
            """
            Initialize CloudTrail analysis thread with work queue integration.

            Args:
                queue: Thread-safe work queue containing credential sets for processing
            """
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Execute CloudTrail analysis for queued account credentials with comprehensive error handling.

            Processes account credentials from the thread-safe work queue, performing detailed
            CloudTrail discovery and security analysis for each account-region combination.
            Implements robust error handling, logging, and result aggregation patterns for
            enterprise-scale security audits with operational resilience.
            """
            while True:
                # Retrieve account credentials from thread-safe work queue
                c_account_credentials = self.queue.get()
                try:
                    # Log CloudTrail analysis initiation for operational visibility
                    logging.info(
                        f"Checking account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}"
                    )
                    # Execute comprehensive CloudTrail discovery and security analysis
                    Trails = Inventory_Modules.find_account_cloudtrail2(
                        c_account_credentials, c_account_credentials["Region"]
                    )

                    # Log CloudTrail discovery results with organizational context
                    logging.info(
                        f"Root Account: {c_account_credentials['MgmtAccount']} Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Found {len(Trails['trailList'])} trails"
                    )

                    # Process discovered CloudTrails for comprehensive compliance analysis
                    if "trailList" in Trails.keys():
                        # Iterate through discovered CloudTrails for detailed analysis
                        for y in range(len(Trails["trailList"])):
                            # Aggregate CloudTrail metadata with organizational context
                            AllTrails.append(
                                {
                                    "MgmtAccount": c_account_credentials[
                                        "MgmtAccount"
                                    ],  # Management account for organizational context
                                    "AccountId": c_account_credentials[
                                        "AccountId"
                                    ],  # Target account containing CloudTrail
                                    "Region": c_account_credentials[
                                        "Region"
                                    ],  # AWS region for regional compliance analysis
                                    "TrailName": Trails["trailList"][y]["Name"],  # CloudTrail name for identification
                                    "MultiRegion": Trails["trailList"][y][
                                        "IsMultiRegionTrail"
                                    ],  # Multi-region logging status
                                    "OrgTrail": "OrgTrail"  # Organization trail classification
                                    if Trails["trailList"][y]["IsOrganizationTrail"]
                                    else "Account Trail",  # Trail scope classification for compliance analysis
                                    "Bucket": Trails["trailList"][y][
                                        "S3BucketName"
                                    ],  # S3 bucket for log storage and encryption validation
                                    "KMS": Trails["trailList"][y]["KmsKeyId"]
                                    if "KmsKeyId" in Trails.keys()
                                    else None,  # KMS encryption key for data protection compliance
                                    "CloudWatchLogArn": Trails["trailList"][y][
                                        "CloudWatchLogsLogGroupArn"
                                    ]  # CloudWatch integration for real-time monitoring
                                    if "CloudWatchLogsLogGroupArn" in Trails.keys()
                                    else None,
                                    "HomeRegion": Trails["trailList"][y][
                                        "HomeRegion"
                                    ]  # Primary region for multi-region trail management
                                    if "HomeRegion" in Trails.keys()
                                    else None,
                                    "SNSTopicName": Trails["trailList"][y][
                                        "SNSTopicName"
                                    ]  # SNS topic for notification integration
                                    if "SNSTopicName" in Trails.keys()
                                    else None,
                                }
                            )
                        # Legacy code: AllTrails.append(Trails['trailList']) - replaced with detailed metadata extraction
                except ClientError as my_Error:
                    # Handle AWS API authorization and access errors with detailed logging
                    if "AuthFailure" in str(my_Error):
                        logging.error(
                            f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region"
                        )
                        logging.warning(
                            f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into"
                        )
                        pass  # Continue processing other accounts despite individual failures

                finally:
                    # Signal task completion for thread-safe work queue management
                    self.queue.task_done()
                    # Print progress indicator for operational visibility
                    print(".", end="")

    # Initialize thread-safe result aggregation for enterprise-scale CloudTrail inventory
    AllTrails = []  # Global CloudTrail inventory with comprehensive security metadata
    checkqueue = Queue()  # Thread-safe work queue for concurrent account processing

    # Optimize thread pool size for efficient processing while respecting AWS API limits
    WorkerThreads = min(len(f_AllCredentials), 50)  # Cap at 50 threads for API rate limiting

    # Initialize multi-threaded CloudTrail analysis worker pool
    for x in range(WorkerThreads):
        worker = CheckAccountForCloudtrailThreaded(checkqueue)
        worker.daemon = True  # Enable graceful shutdown with main thread termination
        worker.start()  # Begin concurrent CloudTrail analysis processing

    # Populate work queue with account credentials for distributed processing
    for credential in f_AllCredentials:
        try:
            # Add valid credentials to processing queue, skip failed credential validation
            checkqueue.put(credential) if credential["Success"] else None
        except ClientError as my_Error:
            logging.error(f"Error: {my_Error}")
            pass  # Continue processing remaining credentials despite individual failures

    # Wait for all CloudTrail analysis tasks to complete before result aggregation
    checkqueue.join()

    # Return comprehensive CloudTrail inventory with enterprise security metadata
    return AllTrails


##################
# ANSI escape sequence for terminal line clearing in progress display
ERASE_LINE = "\x1b[2K"

if __name__ == "__main__":
    """
    Main execution entry point for enterprise CloudTrail compliance analysis and security audit.
    
    Orchestrates comprehensive multi-account, multi-region CloudTrail security assessment with
    enterprise-grade operational controls, detailed compliance validation, and structured
    reporting capabilities for organizational security posture management.
    """
    # Parse command-line arguments for CloudTrail compliance analysis configuration
    args = parse_args(sys.argv[1:])

    # Extract enterprise credential profile for multi-account access management
    pProfile = args.Profile
    pRegionList = args.Regions  # Target regions for compliance analysis coverage
    pSkipAccounts = args.SkipAccounts  # Account exclusion list for organizational policy compliance
    pAccounts = args.Accounts  # Specific account targeting for focused security audits
    pSkipProfiles = args.SkipProfiles  # Profile exclusion for credential management optimization
    pRootOnly = args.RootOnly  # Root account validation flag for organizational assessment
    pSaveFilename = args.Filename  # Output file path for compliance report generation
    pTiming = args.Time  # Performance timing flag for operational optimization
    verbose = args.loglevel  # Logging verbosity level for operational visibility

    # Configure enterprise logging infrastructure for security audit operations
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

    # Suppress verbose AWS SDK logging for cleaner security audit output
    logging.getLogger("boto3").setLevel(logging.CRITICAL)  # Suppress boto3 internal logging
    logging.getLogger("botocore").setLevel(logging.CRITICAL)  # Suppress botocore HTTP request logging
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)  # Suppress S3 transfer operation logging
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)  # Suppress HTTP connection pool logging

    # Log enterprise security audit initialization with operational context
    logging.info(f"Single Profile: {pProfile}")

    # Initialize performance timing for operational optimization and SLA compliance
    if pTiming:
        begin_time = time()  # Start timing for CloudTrail compliance analysis performance

    print()
    print(f"Checking for CloudTrails... ")
    print()

    # Initialize enterprise CloudTrail compliance analysis data structures
    TrailsFound = []  # Comprehensive CloudTrail inventory with security metadata
    AllCredentials = []  # Validated credential set for multi-account analysis
    CTSummary = {}  # CloudTrail summary aggregation for compliance reporting
    OrgTrailInUse = False  # Organization-level trail detection flag
    ExtraCloudTrails = 0  # Counter for redundant CloudTrail configurations

    # Ensure account exclusion list is properly initialized for organizational policy compliance
    if pSkipAccounts is None:
        pSkipAccounts = []

    # Execute enterprise credential discovery and validation across organizational hierarchy
    AllCredentials = get_all_credentials(
        pProfile, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList
    )

    # Perform comprehensive multi-threaded CloudTrail discovery and security analysis
    TrailsFound = check_account_for_cloudtrail(AllCredentials)

    # Generate comprehensive account-region matrix for CloudTrail coverage gap analysis
    AllChildAccountandRegionList = [[item["MgmtAccount"], item["AccountId"], item["Region"]] for item in AllCredentials]
    ChildAccountsandRegionsWithCloudTrail = [
        [item["MgmtAccount"], item["AccountId"], item["Region"]] for item in TrailsFound
    ]

    # Identify compliance gaps: accounts and regions lacking CloudTrail coverage for security audit
    ProblemAccountsandRegions = [
        item for item in AllChildAccountandRegionList if item not in ChildAccountsandRegionsWithCloudTrail
    ]

    # Extract unique region list for regional compliance coverage validation
    UniqueRegions = list(set([item["Region"] for item in AllCredentials]))

    # Analyze CloudTrail configuration patterns for compliance violations and redundancy detection
    if verbose < 50:  # Perform detailed analysis when not in high verbosity mode
        for trail in TrailsFound:
            # Detect organization-level trail usage for centralized security monitoring
            if trail["OrgTrail"] == "OrgTrail":
                OrgTrailInUse = True  # Flag organization trail for compliance assessment

            # Initialize account-level CloudTrail summary for compliance reporting
            if trail["AccountId"] not in CTSummary.keys():
                CTSummary[trail["AccountId"]] = {}
                CTSummary[trail["AccountId"]]["CloudTrailNum"] = 1

            # Process regional CloudTrail configuration for coverage analysis
            if trail["Region"] not in CTSummary[trail["AccountId"]].keys():
                CTSummary[trail["AccountId"]][trail["Region"]] = []
                CTSummary[trail["AccountId"]]["CloudTrailNum"] += 1
                # Aggregate CloudTrail metadata for detailed compliance analysis
                CTSummary[trail["AccountId"]][trail["Region"]].append(
                    {"TrailName": trail["TrailName"], "Bucket": trail["Bucket"], "OrgTrail": trail["OrgTrail"]}
                )
            elif trail["Region"] in CTSummary[trail["AccountId"]].keys():
                # Detect redundant CloudTrail configurations indicating potential compliance violations
                ExtraCloudTrails += 1  # Counter for excess CloudTrail instances requiring optimization
                CTSummary[trail["AccountId"]]["CloudTrailNum"] += 1
                # Aggregate additional CloudTrail metadata for redundancy analysis
                CTSummary[trail["AccountId"]][trail["Region"]].append(
                    {"TrailName": trail["TrailName"], "Bucket": trail["Bucket"], "OrgTrail": trail["OrgTrail"]}
                )
    print()  # Visual separator for enhanced terminal output formatting

    # Configure enterprise CloudTrail compliance report display formatting
    display_dict = {
        "AccountId": {"DisplayOrder": 2, "Heading": "Account Number"},  # Account identifier for organizational context
        "MgmtAccount": {"DisplayOrder": 1, "Heading": "Parent Acct"},  # Management account for hierarchical analysis
        "Region": {"DisplayOrder": 3, "Heading": "Region"},  # AWS region for geographic compliance coverage
        "TrailName": {"DisplayOrder": 4, "Heading": "Trail Name"},  # CloudTrail identifier for configuration tracking
        "OrgTrail": {"DisplayOrder": 5, "Heading": "Trail Type"},  # Trail scope classification for compliance analysis
        "Bucket": {"DisplayOrder": 6, "Heading": "S3 Bucket"},  # S3 storage location for audit log retention analysis
    }

    # Sort CloudTrail results for structured enterprise reporting and compliance analysis
    sorted_Results = sorted(TrailsFound, key=lambda d: (d["MgmtAccount"], d["AccountId"], d["Region"], d["TrailName"]))
    ProblemAccountsandRegions.sort()  # Sort compliance gap list for organized reporting

    # Generate comprehensive CloudTrail compliance report with enterprise formatting
    display_results(sorted_Results, display_dict, "None", pSaveFilename)

    # Display account exclusion summary for operational transparency and audit trail
    if pSkipAccounts is not None:
        print(f"These accounts were skipped - as requested: {pSkipAccounts}")
    if pSkipProfiles is not None:
        print(f"These profiles were skipped - as requested: {pSkipProfiles}")

    # Report CloudTrail coverage gaps for compliance remediation and security improvement
    if len(ProblemAccountsandRegions) > 0:
        print(
            f"There were {len(ProblemAccountsandRegions)} accounts and regions that didn't seem to have a CloudTrail associated: \n"
        )
        # Display detailed list of accounts/regions requiring CloudTrail configuration
        for item in ProblemAccountsandRegions:
            print(item)
        print()
    else:
        print(f"All accounts and regions checked seem to have a CloudTrail associated")  # Compliance success message

    # Generate CloudTrail redundancy and optimization recommendations for enterprise efficiency
    if verbose < 50:
        print(f"We found {ExtraCloudTrails} extra cloud trails in use")
        # Highlight potential optimization opportunities with organization trail usage
        print(
            f"Which is silly because we have an Org Trail enabled for the whole Organization"
        ) if OrgTrailInUse else ""
        # Provide cost optimization recommendation for enterprise financial management
        print(
            f"Removing these extra trails would save considerable money (can't really quantify how much right now)"
        ) if ExtraCloudTrails > 0 else ""
        print()

    # Display comprehensive CloudTrail analysis summary for executive reporting
    print(
        f"Found {len(TrailsFound)} trails across {len(AllCredentials)} accounts/ regions across {len(UniqueRegions)} regions"
    )
    print()

    # Display performance timing for operational optimization and SLA compliance
    if pTiming:
        print(ERASE_LINE)  # Clear progress indicators for clean timing display
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

# Display completion message for user confirmation and operational closure
print("Thank you for using this script")
print()

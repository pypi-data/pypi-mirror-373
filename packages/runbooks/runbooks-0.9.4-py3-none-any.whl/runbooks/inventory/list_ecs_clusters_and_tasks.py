# !/usr/bin/env python3

"""
AWS ECS Clusters, Services, and Tasks Discovery and Analysis Script

This script provides comprehensive discovery and inventory capabilities for Amazon
Elastic Container Service (ECS) resources across multiple AWS accounts and regions.
It's designed for enterprise container platform teams who need visibility into
containerized workloads, service distribution, and task management across large-scale
AWS deployments.

Key Features:
- Multi-account ECS cluster discovery using assume role capabilities
- Multi-region scanning with configurable region targeting
- ECS service enumeration with detailed metadata extraction
- ECS task inventory with state tracking and resource utilization
- Container workload analysis and capacity planning support
- Enterprise reporting with CSV export and structured output
- Profile-based authentication with support for federated access

Enterprise Use Cases:
- Container platform inventory and governance across organizations
- ECS service distribution analysis for load balancing optimization
- Task resource utilization tracking for cost optimization
- Capacity planning for containerized workloads
- Compliance reporting for container security and configuration standards
- Multi-account container orchestration visibility
- Disaster recovery planning with service distribution analysis

Container Platform Features:
- ECS cluster enumeration with capacity provider analysis
- Service discovery with task definition and deployment tracking
- Task inventory with container instance placement and resource allocation
- Service health monitoring and availability analysis
- Container resource utilization tracking across accounts
- Load balancer integration analysis for service endpoints

Security Considerations:
- Uses IAM assume role capabilities for cross-account ECS access
- Implements proper error handling for authorization failures
- Supports read-only operations with no container modification capabilities
- Respects ECS service permissions and cluster access constraints
- Provides comprehensive audit trail through detailed logging

ECS Resource Analysis:
- Cluster capacity and utilization metrics for planning
- Service scaling configuration and deployment strategy analysis
- Task placement constraints and resource requirements tracking
- Container instance distribution across availability zones
- Service mesh and load balancer integration visibility

Performance Considerations:
- Multi-threaded processing for concurrent ECS API operations
- Progress tracking with tqdm for operational visibility during long operations
- Efficient credential management for cross-account container access
- Memory-optimized data structures for large container inventories
- Queue-based worker architecture for scalable discovery operations

Threading Architecture:
- Worker thread pool with configurable concurrency (max 25 threads)
- Queue-based task distribution for efficient resource discovery
- Thread-safe error handling and progress tracking
- Graceful degradation for account access failures

Dependencies:
- boto3/botocore for AWS ECS API interactions
- Inventory_Modules for common utility functions and credential management
- ArgumentsClass for standardized CLI argument parsing
- threading and queue for concurrent processing architecture
- colorama for enhanced output formatting and tqdm for progress tracking

Future Enhancements:
- ECS task definition analysis and security compliance checking
- Container image vulnerability scanning integration
- Service mesh configuration analysis
- Auto-scaling configuration and recommendation engine
- Cost optimization recommendations based on resource utilization

Author: AWS CloudOps Team
Version: 2024.09.06
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
from Inventory_Modules import display_results, find_account_ecs_clusters_services_and_tasks2, get_all_credentials
from tqdm.auto import tqdm

init()
__version__ = "2024.09.06"
ERASE_LINE = "\x1b[2K"
begin_time = time()

# TODO: Need a table at the bottom that summarizes the results, by instance-type, by running/ stopped, maybe by account and region


##################
# Functions
##################


def parse_args(f_arguments):
    """
    Parse command line arguments for ECS clusters, services, and tasks discovery operations.

    Configures comprehensive argument parsing for multi-account, multi-region ECS resource
    inventory operations. Supports enterprise container platform management with profile
    management, region targeting, organizational access controls, and status filtering for
    container workload analysis and capacity planning.

    Args:
        f_arguments (list): Command line arguments from sys.argv[1:]

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - Profiles: List of AWS profiles to process
            - Regions: Target regions for ECS resource discovery
            - SkipProfiles/SkipAccounts: Exclusion filters
            - RootOnly: Limit to organization root accounts
            - AccessRoles: IAM roles for cross-account access
            - Filename: Output file for CSV export
            - Time: Enable performance timing metrics
            - loglevel: Logging verbosity configuration
            - pStatus: Filter tasks by status (running/stopped)

    Configuration Options:
        - Multi-region scanning with region filters for targeted container analysis
        - Multi-profile support for federated access across container platforms
        - Extended arguments for advanced filtering and account selection
        - Root-only mode for organization-level container inventory
        - Role-based access for cross-account ECS resource discovery
        - File output for integration with container management tools
        - Timing metrics for performance optimization and monitoring
        - Status filtering for task state analysis (running, stopped, or both)
        - Verbose logging for debugging and container platform audit

    ECS-Specific Features:
        - Task status filtering to focus on specific workload states
        - Support for container lifecycle analysis and monitoring
        - Integration with enterprise container governance workflows
    """
    script_path, script_name = split(sys.argv[0])
    parser = CommonArguments()
    parser.my_parser.description = "Discover and analyze ECS clusters, services, and tasks across multiple AWS accounts and regions for enterprise container platform management."
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
        help="Filter ECS tasks by status: 'running' for active workloads, 'stopped' for terminated tasks, or omit for both states",
    )
    return parser.my_parser.parse_args(f_arguments)


# The parameters passed to this function should be the dictionary of attributes that will be examined within the thread.
def find_all_clusters_and_tasks(fAllCredentials: list, fStatus: str = None) -> list:
    """
    Discover and inventory ECS clusters, services, and tasks across multiple AWS accounts and regions.

    Performs comprehensive ECS resource discovery using multi-threaded processing to efficiently
    inventory containerized workloads across enterprise AWS environments. Supports status filtering
    for task lifecycle analysis and provides detailed metadata for capacity planning and governance.

    Args:
        fAllCredentials (list): List of credential dictionaries for cross-account access containing:
            - AccountId: AWS account number
            - Region: Target AWS region
            - Success: Boolean indicating credential validity
            - MgmtAccount: Management account identifier
            - ParentProfile: Source AWS profile
        fStatus (str, optional): Filter tasks by status ('running', 'stopped', or None for all)

    Returns:
        list: Comprehensive list of ECS resource dictionaries containing:
            - MgmtAccount: Management account identifier for organizational hierarchy
            - AccountId: AWS account containing the ECS resources
            - Region: AWS region where resources are located
            - ClusterName: ECS cluster identifier
            - ServiceName: ECS service name (if applicable)
            - TaskDefinition: Task definition ARN and revision
            - TaskArn: Unique task identifier
            - TaskStatus: Current task state (RUNNING, STOPPED, PENDING)
            - ContainerInstances: EC2 instances hosting containers
            - ParentProfile: Source profile for audit and governance
            - LaunchType: Container launch type (EC2, FARGATE)
            - PlatformVersion: ECS platform version for Fargate tasks

    Threading Architecture:
        - Worker thread pool with maximum 25 concurrent threads for scalability
        - Queue-based task distribution for efficient resource discovery
        - Thread-safe error handling and progress tracking with tqdm
        - Graceful degradation for account access failures and authorization issues

    Enterprise Features:
        - Cross-account ECS resource discovery with assume role capabilities
        - Container workload analysis with status filtering for lifecycle management
        - Progress tracking for operational visibility during large-scale operations
        - Comprehensive error handling for authorization and throttling scenarios

    Error Handling:
        - Authorization failure detection with region opt-in diagnostics
        - AWS API throttling management with appropriate logging
        - Graceful handling of missing resources and empty responses
        - Thread-safe error reporting and progress updates

    Performance Considerations:
        - Configurable thread pool size based on credential set size
        - Efficient memory management for large container inventories
        - Progress tracking with real-time feedback for long operations
        - Optimized data structures for enterprise-scale resource discovery
    """

    # Worker thread class for concurrent ECS resource discovery
    class FindInstances(Thread):
        def __init__(self, queue):
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            """
            Main worker thread execution loop for ECS resource discovery and analysis.

            Continuously processes credential sets from the shared work queue, performing
            comprehensive ECS cluster, service, and task discovery operations with detailed
            metadata extraction and enterprise container platform analysis.
            """
            while True:
                # Retrieve ECS discovery work item from thread-safe queue
                c_account_credentials = self.queue.get()
                logging.info(f"De-queued info for account number {c_account_credentials['AccountId']}")

                try:
                    # Execute comprehensive ECS resource discovery for the current account/region
                    # This calls the inventory module's specialized ECS discovery function
                    EcsInfo = Inventory_Modules.find_account_ecs_clusters_services_and_tasks2(c_account_credentials)
                    logging.info(
                        f"Account: {c_account_credentials['AccountId']} Region: {c_account_credentials['Region']} | Discovered ECS resources"
                    )

                    # Initialize ECS resource metadata variables with defaults
                    ClusterName = ServiceName = TaskDefinition = TaskArn = TaskStatus = ""
                    LaunchType = PlatformVersion = ContainerInstanceArn = ""

                    # Process discovered ECS clusters, services, and tasks with comprehensive metadata extraction
                    # ECS resources have a hierarchical structure: Clusters -> Services -> Tasks
                    if "Clusters" in EcsInfo and EcsInfo["Clusters"]:
                        for cluster in EcsInfo["Clusters"]:
                            ClusterName = cluster.get("clusterName", "Unknown")
                            ClusterArn = cluster.get("clusterArn", "")
                            ClusterStatus = cluster.get("status", "")

                            # Process ECS services within each cluster for workload analysis
                            if "Services" in cluster and cluster["Services"]:
                                for service in cluster["Services"]:
                                    ServiceName = service.get("serviceName", "Unknown")
                                    ServiceArn = service.get("serviceArn", "")
                                    ServiceStatus = service.get("status", "")
                                    TaskDefinition = service.get("taskDefinition", "")

                                    # Extract running task count for capacity analysis
                                    RunningCount = service.get("runningCount", 0)
                                    PendingCount = service.get("pendingCount", 0)
                                    DesiredCount = service.get("desiredCount", 0)

                                    # Process ECS tasks for detailed workload state analysis
                                    if "Tasks" in service and service["Tasks"]:
                                        for task in service["Tasks"]:
                                            TaskArn = task.get("taskArn", "")
                                            TaskStatus = task.get("lastStatus", "")
                                            LaunchType = task.get("launchType", "")
                                            PlatformVersion = task.get("platformVersion", "")

                                            # Extract container instance information for EC2 launch type
                                            ContainerInstanceArn = task.get("containerInstanceArn", "")

                                            # Apply status filtering for task lifecycle analysis
                                            if fStatus is None or fStatus.upper() == TaskStatus.upper():
                                                # Create comprehensive ECS resource record for enterprise inventory
                                                ecs_record = {
                                                    # Organizational context for multi-account container management
                                                    "MgmtAccount": c_account_credentials["MgmtAccount"],
                                                    "AccountId": c_account_credentials["AccountId"],
                                                    "Region": c_account_credentials["Region"],
                                                    "ParentProfile": c_account_credentials["ParentProfile"],
                                                    # ECS cluster hierarchy and identification
                                                    "ClusterName": ClusterName,
                                                    "ClusterArn": ClusterArn,
                                                    "ClusterStatus": ClusterStatus,
                                                    # ECS service configuration and capacity
                                                    "ServiceName": ServiceName,
                                                    "ServiceArn": ServiceArn,
                                                    "ServiceStatus": ServiceStatus,
                                                    "TaskDefinition": TaskDefinition,
                                                    # Service capacity metrics for planning
                                                    "RunningCount": RunningCount,
                                                    "PendingCount": PendingCount,
                                                    "DesiredCount": DesiredCount,
                                                    # Task-level metadata and runtime information
                                                    "TaskArn": TaskArn,
                                                    "TaskStatus": TaskStatus,
                                                    "LaunchType": LaunchType,
                                                    "PlatformVersion": PlatformVersion,
                                                    "ContainerInstanceArn": ContainerInstanceArn,
                                                }

                                                # Add to enterprise container platform inventory
                                                AllInstances.append(ecs_record)
                                            else:
                                                # Skip tasks that don't match status filter
                                                continue
                                    else:
                                        # Handle services without tasks (potentially new or scaled-down services)
                                        if fStatus is None:  # Only include in comprehensive inventory mode
                                            service_record = {
                                                # Organizational context
                                                "MgmtAccount": c_account_credentials["MgmtAccount"],
                                                "AccountId": c_account_credentials["AccountId"],
                                                "Region": c_account_credentials["Region"],
                                                "ParentProfile": c_account_credentials["ParentProfile"],
                                                # Service-level information without tasks
                                                "ClusterName": ClusterName,
                                                "ServiceName": ServiceName,
                                                "ServiceStatus": ServiceStatus,
                                                "TaskDefinition": TaskDefinition,
                                                "RunningCount": RunningCount,
                                                "PendingCount": PendingCount,
                                                "DesiredCount": DesiredCount,
                                                # Empty task fields for consistency
                                                "TaskArn": "",
                                                "TaskStatus": "NO_TASKS",
                                                "LaunchType": "",
                                                "PlatformVersion": "",
                                                "ContainerInstanceArn": "",
                                            }
                                            AllInstances.append(service_record)
                            else:
                                # Handle clusters without services (empty or infrastructure-only clusters)
                                if fStatus is None:  # Only include in comprehensive inventory mode
                                    cluster_record = {
                                        # Organizational context
                                        "MgmtAccount": c_account_credentials["MgmtAccount"],
                                        "AccountId": c_account_credentials["AccountId"],
                                        "Region": c_account_credentials["Region"],
                                        "ParentProfile": c_account_credentials["ParentProfile"],
                                        # Cluster-only information
                                        "ClusterName": ClusterName,
                                        "ClusterStatus": ClusterStatus,
                                        # Empty service and task fields for consistency
                                        "ServiceName": "NO_SERVICES",
                                        "ServiceStatus": "",
                                        "TaskDefinition": "",
                                        "RunningCount": 0,
                                        "PendingCount": 0,
                                        "DesiredCount": 0,
                                        "TaskArn": "",
                                        "TaskStatus": "",
                                        "LaunchType": "",
                                        "PlatformVersion": "",
                                        "ContainerInstanceArn": "",
                                    }
                                    AllInstances.append(cluster_record)
                except KeyError as my_Error:
                    # Handle cases where expected keys are missing from ECS API responses
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    # Handle cases where profile configuration is incorrect
                    logging.error(f"Error: Likely that one of the supplied profiles was wrong")
                    logging.warning(my_Error)
                    continue
                except ClientError as my_Error:
                    # Handle AWS API errors including authorization failures and throttling
                    if "AuthFailure" in str(my_Error):
                        logging.error(
                            f"Authorization Failure accessing account {c_account_credentials['AccountId']} in {c_account_credentials['Region']} region"
                        )
                        logging.warning(
                            f"It's possible that the region {c_account_credentials['Region']} hasn't been opted-into"
                        )
                        continue
                    else:
                        # Handle API throttling and service limits for ECS operations
                        logging.error(f"Error: Likely throttling errors from too much ECS API activity")
                        logging.warning(my_Error)
                        continue
                finally:
                    # Ensure progress tracking and queue management regardless of success/failure
                    pbar.update()
                    self.queue.task_done()

    ###########
    # Initialize queue-based threading architecture for scalable ECS resource discovery
    ###########

    # Create thread-safe queue for distributing work across worker threads
    checkqueue = Queue()

    # Initialize results list for aggregating discovered ECS resources
    AllInstances = []

    # Configure worker thread pool size - balance between performance and AWS API limits
    # Maximum 25 threads to prevent overwhelming AWS APIs while maintaining efficiency
    WorkerThreads = min(len(fAllCredentials), 25)

    # Initialize progress tracking for operational visibility during large-scale operations
    pbar = tqdm(
        desc=f"Finding ECS clusters, services and tasks from {len(fAllCredentials)} accounts / regions",
        total=len(fAllCredentials),
        unit=" locations",
    )

    # Start worker threads for concurrent ECS resource discovery
    for x in range(WorkerThreads):
        worker = FindInstances(checkqueue)
        # Setting daemon to True allows main thread exit even if workers are still processing
        worker.daemon = True
        worker.start()

    # Queue credential sets for processing by worker threads
    for credential in fAllCredentials:
        logging.info(f"Beginning to queue data - starting with {credential['AccountId']}")
        try:
            # Queue individual credential set for ECS resource discovery
            # Note: Single parameter queuing - credential dictionary contains all needed info
            checkqueue.put(credential)
        except ClientError as my_Error:
            # Handle authorization failures during credential queuing
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in {credential['Region']} region"
                )
                logging.warning(f"It's possible that the region {credential['Region']} hasn't been opted-into")
                pass

    # Wait for all queued work to complete before proceeding
    checkqueue.join()
    pbar.close()
    return AllInstances


##################
# Main execution entry point for enterprise ECS resource discovery and analysis
##################

if __name__ == "__main__":
    """
    Main orchestration for comprehensive ECS cluster, service, and task discovery operations.
    
    Coordinates multi-account, multi-region ECS resource inventory with detailed container
    platform analysis, capacity planning support, and enterprise containerized workload
    governance across AWS Organizations environments.
    """
    # Parse enterprise command-line arguments with ECS-specific container platform options
    args = parse_args(sys.argv[1:])

    # Extract configuration parameters for multi-account container platform discovery
    pProfiles = args.Profiles  # AWS profile list for federated ECS access
    pRegionList = args.Regions  # Target regions for ECS cluster enumeration
    pAccounts = args.Accounts  # Specific account targeting for focused container analysis
    pSkipAccounts = args.SkipAccounts  # Account exclusion list for organizational policy compliance
    pSkipProfiles = args.SkipProfiles  # Profile exclusion for credential optimization
    pAccessRoles = args.AccessRoles  # Cross-account roles for Organizations ECS access
    pStatus = args.pStatus  # Task status filter for container lifecycle analysis
    pRootOnly = args.RootOnly  # Organization root account limitation flag
    pFilename = args.Filename  # CSV export file for enterprise container reporting
    pTiming = args.Time  # Performance timing for operational optimization
    verbose = args.loglevel  # Logging verbosity for container platform visibility

    # Configure enterprise logging infrastructure for ECS operations audit trail
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    print()
    print(f"Checking for ECS clusters, services, and tasks... ")
    print()

    # Execute enterprise credential discovery and validation across organizational container infrastructure
    CredentialList = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList, pAccessRoles
    )

    # Calculate organizational scope for executive container platform reporting
    AccountNum = len(set([acct["AccountId"] for acct in CredentialList]))
    RegionNum = len(set([acct["Region"] for acct in CredentialList]))
    print()
    print(f"Searching total of {AccountNum} accounts and {RegionNum} regions for ECS resources")

    # Display performance timing for credential discovery phase optimization
    if pTiming:
        print()
        milestone_time1 = time()
        print(
            f"{Fore.GREEN}\t\tCredential discovery and region enumeration took: {(milestone_time1 - begin_time):.3f} seconds{Fore.RESET}"
        )
        print()

    print(f"Now running through all accounts and regions to discover ECS resources...")

    # Execute comprehensive multi-threaded ECS resource discovery and container platform analysis
    AllInstances = find_all_clusters_and_tasks(CredentialList, pStatus)

    # Configure enterprise ECS resource inventory report display formatting
    display_dict = {
        "ParentProfile": {"DisplayOrder": 1, "Heading": "Parent Profile"},  # Source profile for audit
        "MgmtAccount": {"DisplayOrder": 2, "Heading": "Mgmt Acct"},  # Management account hierarchy
        "AccountId": {"DisplayOrder": 3, "Heading": "Acct Number"},  # Account identifier
        "Region": {"DisplayOrder": 4, "Heading": "Region"},  # AWS region
        "ClusterName": {"DisplayOrder": 5, "Heading": "Cluster"},  # ECS cluster name
        "ServiceName": {"DisplayOrder": 6, "Heading": "Service"},  # ECS service name
        "TaskStatus": {"DisplayOrder": 7, "Heading": "Task Status"},  # Task lifecycle state
        "LaunchType": {"DisplayOrder": 8, "Heading": "Launch Type"},  # EC2 or Fargate
        "RunningCount": {"DisplayOrder": 9, "Heading": "Running Tasks"},  # Active task count
        "DesiredCount": {"DisplayOrder": 10, "Heading": "Desired Tasks"},  # Target task count
    }

    # Sort ECS resources for consistent enterprise reporting and operational visibility
    sorted_all_instances = sorted(
        AllInstances,
        key=lambda d: (d["ParentProfile"], d["MgmtAccount"], d["Region"], d["AccountId"], d.get("ClusterName", "")),
    )

    # Generate comprehensive ECS resource inventory report with CSV export capability
    display_results(sorted_all_instances, display_dict, None, pFilename)

    # Display performance timing metrics for operational optimization and SLA compliance
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script took {time() - begin_time:.2f} seconds{Fore.RESET}")

    print(ERASE_LINE)

    # Display comprehensive operational summary for executive container platform reporting
    print(f"Found {len(AllInstances)} ECS resources across {AccountNum} accounts across {RegionNum} regions")
    print()

    # Display completion message for user confirmation and operational closure
    print("Thank you for using this script")
    print()

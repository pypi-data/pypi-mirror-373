"""
AWS management and governance resource collector.

This module provides specialized collection of management and governance resources including
AWS Organizations, CloudFormation stacks/stacksets, Service Catalog, and related components.
Integrates the functionality from the organizations module.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import boto3
import yaml
from botocore.exceptions import ClientError
from loguru import logger

from runbooks.inventory.collectors.base import BaseResourceCollector, CollectionContext
from runbooks.inventory.models.resource import AWSResource, ResourceCost, ResourceState
from runbooks.inventory.utils.aws_helpers import aws_api_retry


class ManagementResourceCollector(BaseResourceCollector):
    """
    Collector for AWS management and governance resources.

    Handles discovery and inventory of:
    - AWS Organizations (OUs, accounts, policies)
    - CloudFormation stacks and stacksets
    - Service Catalog portfolios and products
    - Config rules and conformance packs
    - Systems Manager documents and parameters
    - CloudWatch dashboards and alarms
    """

    service_category = "management"
    supported_resources = {
        "organizations:account",
        "organizations:organizational_unit",
        "organizations:policy",
        "cloudformation:stack",
        "cloudformation:stackset",
        "servicecatalog:portfolio",
        "servicecatalog:product",
        "config:rule",
        "config:conformance_pack",
        "ssm:document",
        "ssm:parameter",
        "cloudwatch:dashboard",
        "cloudwatch:alarm",
    }
    requires_org_access = True  # Organizations requires management account access

    def collect_resources(
        self, context: CollectionContext, resource_filters: Optional[Dict[str, Any]] = None
    ) -> List[AWSResource]:
        """
        Collect management and governance resources.

        Args:
            context: Collection context with account and region info
            resource_filters: Optional filters for resource selection

        Returns:
            List of discovered AWS management resources
        """
        resources = []
        resource_types = context.resource_types or self.supported_resources

        # Create AWS clients
        clients = self._create_clients(context)

        for resource_type in resource_types:
            if resource_type not in self.supported_resources:
                continue

            try:
                if resource_type.startswith("organizations:"):
                    resources.extend(self._collect_organizations_resources(clients, context, resource_type))
                elif resource_type.startswith("cloudformation:"):
                    resources.extend(self._collect_cloudformation_resources(clients, context, resource_type))
                elif resource_type.startswith("servicecatalog:"):
                    resources.extend(self._collect_servicecatalog_resources(clients, context, resource_type))
                elif resource_type.startswith("config:"):
                    resources.extend(self._collect_config_resources(clients, context, resource_type))
                elif resource_type.startswith("ssm:"):
                    resources.extend(self._collect_ssm_resources(clients, context, resource_type))
                elif resource_type.startswith("cloudwatch:"):
                    resources.extend(self._collect_cloudwatch_resources(clients, context, resource_type))

            except Exception as e:
                logger.error(f"Error collecting {resource_type} resources: {e}")

        logger.info(f"Collected {len(resources)} management resources for account {context.account.account_id}")
        return resources

    def _create_clients(self, context: CollectionContext) -> Dict[str, Any]:
        """Create AWS service clients for management services."""
        session = self._get_session(context.account)
        return {
            "organizations": session.client("organizations", region_name="us-east-1"),  # Global service
            "cloudformation": session.client("cloudformation", region_name=context.region),
            "servicecatalog": session.client("servicecatalog", region_name=context.region),
            "config": session.client("config", region_name=context.region),
            "ssm": session.client("ssm", region_name=context.region),
            "cloudwatch": session.client("cloudwatch", region_name=context.region),
        }

    def _collect_organizations_resources(
        self, clients: Dict[str, Any], context: CollectionContext, resource_type: str
    ) -> List[AWSResource]:
        """Collect AWS Organizations resources."""
        resources = []
        org_client = clients["organizations"]

        try:
            if resource_type == "organizations:account":
                resources.extend(self._collect_organization_accounts(org_client, context))
            elif resource_type == "organizations:organizational_unit":
                resources.extend(self._collect_organizational_units(org_client, context))
            elif resource_type == "organizations:policy":
                resources.extend(self._collect_organization_policies(org_client, context))

        except ClientError as e:
            if e.response["Error"]["Code"] == "AWSOrganizationsNotInUseException":
                logger.warning("AWS Organizations is not enabled in this account")
            else:
                logger.error(f"Error collecting organizations resources: {e}")

        return resources

    @aws_api_retry
    def _collect_organization_accounts(self, org_client, context: CollectionContext) -> List[AWSResource]:
        """Collect organization accounts."""
        resources = []

        try:
            paginator = org_client.get_paginator("list_accounts")
            for page in paginator.paginate():
                for account in page.get("Accounts", []):
                    resource = AWSResource(
                        resource_id=account["Id"],
                        resource_type="organizations:account",
                        resource_name=account.get("Name", account["Id"]),
                        region="global",  # Organizations is global
                        account_id=context.account.account_id,
                        state=ResourceState.AVAILABLE if account["Status"] == "ACTIVE" else ResourceState.UNKNOWN,
                        properties={
                            "email": account.get("Email"),
                            "status": account.get("Status"),
                            "joined_method": account.get("JoinedMethod"),
                            "joined_timestamp": account.get("JoinedTimestamp"),
                        },
                        tags=self._get_account_tags(org_client, account["Id"]),
                        created_date=account.get("JoinedTimestamp"),
                        last_modified=datetime.utcnow(),
                    )
                    resources.append(resource)

        except Exception as e:
            logger.error(f"Error collecting organization accounts: {e}")

        return resources

    @aws_api_retry
    def _collect_organizational_units(self, org_client, context: CollectionContext) -> List[AWSResource]:
        """Collect organizational units."""
        resources = []

        try:
            # Get organization root
            roots = org_client.list_roots()["Roots"]
            if not roots:
                return resources

            root_id = roots[0]["Id"]

            # Recursively collect OUs
            def collect_ous(parent_id: str, level: int = 0):
                response = org_client.list_organizational_units_for_parent(ParentId=parent_id)

                for ou in response.get("OrganizationalUnits", []):
                    resource = AWSResource(
                        resource_id=ou["Id"],
                        resource_type="organizations:organizational_unit",
                        resource_name=ou["Name"],
                        region="global",
                        account_id=context.account.account_id,
                        state=ResourceState.AVAILABLE,
                        properties={
                            "arn": ou.get("Arn"),
                            "parent_id": parent_id,
                            "level": level,
                        },
                        tags=self._get_ou_tags(org_client, ou["Id"]),
                        created_date=datetime.utcnow(),
                        last_modified=datetime.utcnow(),
                    )
                    resources.append(resource)

                    # Recursively collect child OUs
                    collect_ous(ou["Id"], level + 1)

            collect_ous(root_id)

        except Exception as e:
            logger.error(f"Error collecting organizational units: {e}")

        return resources

    @aws_api_retry
    def _collect_organization_policies(self, org_client, context: CollectionContext) -> List[AWSResource]:
        """Collect organization policies."""
        resources = []

        try:
            # Get all policy types
            policy_types = ["SERVICE_CONTROL_POLICY", "TAG_POLICY", "BACKUP_POLICY", "AISERVICES_OPT_OUT_POLICY"]

            for policy_type in policy_types:
                try:
                    paginator = org_client.get_paginator("list_policies")
                    for page in paginator.paginate(Filter=policy_type):
                        for policy in page.get("Policies", []):
                            resource = AWSResource(
                                resource_id=policy["Id"],
                                resource_type="organizations:policy",
                                resource_name=policy["Name"],
                                region="global",
                                account_id=context.account.account_id,
                                state=ResourceState.AVAILABLE,
                                properties={
                                    "arn": policy.get("Arn"),
                                    "type": policy.get("Type"),
                                    "description": policy.get("Description"),
                                    "aws_managed": policy.get("AwsManaged", False),
                                },
                                tags=self._get_policy_tags(org_client, policy["Id"]),
                                created_date=datetime.utcnow(),
                                last_modified=datetime.utcnow(),
                            )
                            resources.append(resource)

                except Exception as e:
                    logger.warning(f"Error collecting {policy_type} policies: {e}")

        except Exception as e:
            logger.error(f"Error collecting organization policies: {e}")

        return resources

    def _get_account_tags(self, org_client, account_id: str) -> Dict[str, str]:
        """Get tags for an organization account."""
        try:
            response = org_client.list_tags_for_resource(ResourceId=account_id)
            return {tag["Key"]: tag["Value"] for tag in response.get("Tags", [])}
        except Exception:
            return {}

    def _get_ou_tags(self, org_client, ou_id: str) -> Dict[str, str]:
        """Get tags for an organizational unit."""
        try:
            response = org_client.list_tags_for_resource(ResourceId=ou_id)
            return {tag["Key"]: tag["Value"] for tag in response.get("Tags", [])}
        except Exception:
            return {}

    def _get_policy_tags(self, org_client, policy_id: str) -> Dict[str, str]:
        """Get tags for an organization policy."""
        try:
            response = org_client.list_tags_for_resource(ResourceId=policy_id)
            return {tag["Key"]: tag["Value"] for tag in response.get("Tags", [])}
        except Exception:
            return {}

    def _collect_cloudformation_resources(
        self, clients: Dict[str, Any], context: CollectionContext, resource_type: str
    ) -> List[AWSResource]:
        """Collect CloudFormation resources."""
        resources = []
        cfn_client = clients["cloudformation"]

        try:
            if resource_type == "cloudformation:stack":
                resources.extend(self._collect_cfn_stacks(cfn_client, context))
            elif resource_type == "cloudformation:stackset":
                resources.extend(self._collect_cfn_stacksets(cfn_client, context))

        except Exception as e:
            logger.error(f"Error collecting CloudFormation resources: {e}")

        return resources

    @aws_api_retry
    def _collect_cfn_stacks(self, cfn_client, context: CollectionContext) -> List[AWSResource]:
        """Collect CloudFormation stacks."""
        resources = []

        try:
            paginator = cfn_client.get_paginator("list_stacks")
            for page in paginator.paginate():
                for stack in page.get("StackSummaries", []):
                    if stack["StackStatus"] != "DELETE_COMPLETE":
                        resource = AWSResource(
                            resource_id=stack["StackId"],
                            resource_type="cloudformation:stack",
                            resource_name=stack["StackName"],
                            region=context.region,
                            account_id=context.account.account_id,
                            state=self._get_cfn_stack_state(stack["StackStatus"]),
                            properties={
                                "stack_status": stack["StackStatus"],
                                "creation_time": stack.get("CreationTime"),
                                "last_updated_time": stack.get("LastUpdatedTime"),
                                "deletion_time": stack.get("DeletionTime"),
                                "stack_status_reason": stack.get("StackStatusReason"),
                                "template_description": stack.get("TemplateDescription"),
                                "drift_status": stack.get("DriftInformation", {}).get("StackDriftStatus"),
                            },
                            tags=self._get_cfn_stack_tags(cfn_client, stack["StackName"]),
                            created_date=stack.get("CreationTime"),
                            last_modified=stack.get("LastUpdatedTime"),
                        )
                        resources.append(resource)

        except Exception as e:
            logger.error(f"Error collecting CloudFormation stacks: {e}")

        return resources

    @aws_api_retry
    def _collect_cfn_stacksets(self, cfn_client, context: CollectionContext) -> List[AWSResource]:
        """Collect CloudFormation stacksets."""
        resources = []

        try:
            paginator = cfn_client.get_paginator("list_stack_sets")
            for page in paginator.paginate():
                for stackset in page.get("Summaries", []):
                    resource = AWSResource(
                        resource_id=stackset["StackSetId"],
                        resource_type="cloudformation:stackset",
                        resource_name=stackset["StackSetName"],
                        region=context.region,
                        account_id=context.account.account_id,
                        state=self._get_cfn_stackset_state(stackset["Status"]),
                        properties={
                            "status": stackset["Status"],
                            "description": stackset.get("Description"),
                            "drift_status": stackset.get("DriftStatus"),
                            "last_drift_check_timestamp": stackset.get("LastDriftCheckTimestamp"),
                            "auto_deployment": stackset.get("AutoDeployment"),
                            "permission_model": stackset.get("PermissionModel"),
                        },
                        tags=self._get_cfn_stackset_tags(cfn_client, stackset["StackSetName"]),
                        created_date=datetime.utcnow(),
                        last_modified=datetime.utcnow(),
                    )
                    resources.append(resource)

        except Exception as e:
            logger.error(f"Error collecting CloudFormation stacksets: {e}")

        return resources

    def _get_cfn_stack_state(self, status: str) -> ResourceState:
        """Map CloudFormation stack status to ResourceState."""
        if status.endswith("_COMPLETE"):
            return ResourceState.AVAILABLE
        elif status.endswith("_IN_PROGRESS"):
            return ResourceState.PENDING
        elif status.endswith("_FAILED"):
            return ResourceState.ERROR
        else:
            return ResourceState.UNKNOWN

    def _get_cfn_stackset_state(self, status: str) -> ResourceState:
        """Map CloudFormation stackset status to ResourceState."""
        if status == "ACTIVE":
            return ResourceState.AVAILABLE
        else:
            return ResourceState.UNKNOWN

    def _get_cfn_stack_tags(self, cfn_client, stack_name: str) -> Dict[str, str]:
        """Get tags for a CloudFormation stack."""
        try:
            response = cfn_client.describe_stacks(StackName=stack_name)
            stacks = response.get("Stacks", [])
            if stacks:
                return {tag["Key"]: tag["Value"] for tag in stacks[0].get("Tags", [])}
        except Exception:
            pass
        return {}

    def _get_cfn_stackset_tags(self, cfn_client, stackset_name: str) -> Dict[str, str]:
        """Get tags for a CloudFormation stackset."""
        try:
            response = cfn_client.describe_stack_set(StackSetName=stackset_name)
            stackset = response.get("StackSet", {})
            return {tag["Key"]: tag["Value"] for tag in stackset.get("Tags", [])}
        except Exception:
            pass
        return {}

    def _collect_servicecatalog_resources(
        self, clients: Dict[str, Any], context: CollectionContext, resource_type: str
    ) -> List[AWSResource]:
        """Collect Service Catalog resources."""
        # Placeholder for Service Catalog collection
        return []

    def _collect_config_resources(
        self, clients: Dict[str, Any], context: CollectionContext, resource_type: str
    ) -> List[AWSResource]:
        """Collect AWS Config resources."""
        # Placeholder for Config collection
        return []

    def _collect_ssm_resources(
        self, clients: Dict[str, Any], context: CollectionContext, resource_type: str
    ) -> List[AWSResource]:
        """Collect Systems Manager resources."""
        # Placeholder for SSM collection
        return []

    def _collect_cloudwatch_resources(
        self, clients: Dict[str, Any], context: CollectionContext, resource_type: str
    ) -> List[AWSResource]:
        """Collect CloudWatch resources."""
        # Placeholder for CloudWatch collection
        return []


class OrganizationsManager:
    """
    Organizational Unit (OU) management for AWS Organizations.

    This class provides capabilities for setting up and managing
    AWS Organizations structure following Cloud Foundations best practices.
    Integrated from the previous organizations module.
    """

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        """Initialize OU manager."""
        self.profile = profile
        self.region = region or "us-east-1"  # Organizations is global but requires a region
        self._org_client = None
        self._session = None

    @property
    def session(self):
        """Get AWS session."""
        if self._session is None:
            if self.profile:
                self._session = boto3.Session(profile_name=self.profile)
            else:
                self._session = boto3.Session()
        return self._session

    @property
    def org_client(self):
        """Get AWS Organizations client."""
        if self._org_client is None:
            self._org_client = self.session.client("organizations", region_name=self.region)
        return self._org_client

    def get_template_structure(self, template: str) -> Dict[str, Any]:
        """
        Get predefined OU structure template.

        Args:
            template: Template name ('standard', 'security', 'custom')

        Returns:
            OU structure definition
        """
        templates = {
            "standard": {
                "name": "Standard OU Structure",
                "description": "Standard Cloud Foundations OU structure",
                "organizational_units": [
                    {
                        "name": "Core",
                        "description": "Core organizational units for foundational services",
                        "children": [
                            {
                                "name": "Log Archive",
                                "description": "Centralized logging account",
                                "policies": ["LogArchivePolicy"],
                            },
                            {
                                "name": "Audit",
                                "description": "Security and compliance auditing",
                                "policies": ["AuditPolicy"],
                            },
                            {
                                "name": "Shared Services",
                                "description": "Shared infrastructure services",
                                "policies": ["SharedServicesPolicy"],
                            },
                        ],
                    },
                    {
                        "name": "Production",
                        "description": "Production workload accounts",
                        "children": [
                            {
                                "name": "Prod-WebApps",
                                "description": "Production web applications",
                                "policies": ["ProductionPolicy"],
                            },
                            {
                                "name": "Prod-Data",
                                "description": "Production data services",
                                "policies": ["ProductionPolicy", "DataPolicy"],
                            },
                        ],
                    },
                    {
                        "name": "Non-Production",
                        "description": "Development and testing accounts",
                        "children": [
                            {
                                "name": "Development",
                                "description": "Development environments",
                                "policies": ["DevelopmentPolicy"],
                            },
                            {
                                "name": "Testing",
                                "description": "Testing and staging environments",
                                "policies": ["TestingPolicy"],
                            },
                        ],
                    },
                ],
            },
            "security": {
                "name": "Security-Focused OU Structure",
                "description": "Enhanced security OU structure with additional controls",
                "organizational_units": [
                    {
                        "name": "Security",
                        "description": "Security and compliance organizational unit",
                        "children": [
                            {
                                "name": "Security-Prod",
                                "description": "Production security tools",
                                "policies": ["SecurityProdPolicy"],
                            },
                            {
                                "name": "Security-NonProd",
                                "description": "Non-production security tools",
                                "policies": ["SecurityNonProdPolicy"],
                            },
                            {
                                "name": "Log Archive",
                                "description": "Centralized security logging",
                                "policies": ["LogArchivePolicy", "SecurityLogPolicy"],
                            },
                            {
                                "name": "Audit",
                                "description": "Security auditing and compliance",
                                "policies": ["AuditPolicy", "CompliancePolicy"],
                            },
                        ],
                    },
                    {
                        "name": "Workloads",
                        "description": "Application workload accounts",
                        "children": [
                            {
                                "name": "Prod-HighSecurity",
                                "description": "High security production workloads",
                                "policies": ["HighSecurityPolicy", "ProductionPolicy"],
                            },
                            {
                                "name": "Prod-Standard",
                                "description": "Standard production workloads",
                                "policies": ["StandardSecurityPolicy", "ProductionPolicy"],
                            },
                            {
                                "name": "NonProd",
                                "description": "Non-production workloads",
                                "policies": ["NonProdPolicy"],
                            },
                        ],
                    },
                ],
            },
        }

        if template not in templates:
            raise ValueError(f"Unknown template: {template}. Available: {list(templates.keys())}")

        logger.info(f"Using OU structure template: {template}")
        return templates[template]

    def load_structure_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load OU structure from YAML file.

        Args:
            file_path: Path to YAML structure file

        Returns:
            OU structure definition
        """
        config_path = Path(file_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Structure file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                structure = yaml.safe_load(f)

            logger.info(f"Loaded OU structure from: {config_path}")
            return structure

        except Exception as e:
            logger.error(f"Failed to load structure file: {e}")
            raise

    def create_ou_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create OU structure in AWS Organizations.

        Args:
            structure: OU structure definition

        Returns:
            Creation results with OU IDs and status
        """
        logger.info(f"Creating OU structure: {structure.get('name', 'Unnamed')}")

        try:
            # Get organization root
            root_id = self._get_organization_root()

            # Create OUs
            results = {"structure_name": structure.get("name"), "root_id": root_id, "created_ous": [], "errors": []}

            organizational_units = structure.get("organizational_units", [])

            for ou_def in organizational_units:
                try:
                    ou_result = self._create_ou_recursive(ou_def, root_id)
                    results["created_ous"].append(ou_result)
                    logger.info(f"Created OU: {ou_def['name']}")

                except Exception as e:
                    error_msg = f"Failed to create OU {ou_def['name']}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            logger.info(f"OU structure creation completed. Created {len(results['created_ous'])} OUs")
            return results

        except Exception as e:
            logger.error(f"OU structure creation failed: {e}")
            raise

    def _get_organization_root(self) -> str:
        """Get the organization root ID."""
        try:
            response = self.org_client.list_roots()

            if not response.get("Roots"):
                raise Exception("No organization roots found")

            root_id = response["Roots"][0]["Id"]
            logger.debug(f"Found organization root: {root_id}")
            return root_id

        except Exception as e:
            logger.error(f"Failed to get organization root: {e}")
            raise

    def _create_ou_recursive(self, ou_def: Dict[str, Any], parent_id: str) -> Dict[str, Any]:
        """
        Recursively create OU and its children.

        Args:
            ou_def: OU definition
            parent_id: Parent OU ID

        Returns:
            Creation result with OU details
        """
        ou_name = ou_def["name"]
        ou_description = ou_def.get("description", "")

        logger.info(f"Creating OU: {ou_name} under parent: {parent_id}")

        # Check if OU already exists
        existing_ou = self._find_existing_ou(ou_name, parent_id)
        if existing_ou:
            logger.info(f"OU {ou_name} already exists: {existing_ou['Id']}")
            ou_id = existing_ou["Id"]
        else:
            # Create the OU
            response = self.org_client.create_organizational_unit(ParentId=parent_id, Name=ou_name)
            ou_id = response["OrganizationalUnit"]["Id"]
            logger.info(f"Created OU {ou_name}: {ou_id}")

        result = {"name": ou_name, "id": ou_id, "parent_id": parent_id, "description": ou_description, "children": []}

        # Create child OUs
        children = ou_def.get("children", [])
        for child_def in children:
            try:
                child_result = self._create_ou_recursive(child_def, ou_id)
                result["children"].append(child_result)
            except Exception as e:
                logger.error(f"Failed to create child OU {child_def.get('name', 'Unknown')}: {e}")

        return result

    def _find_existing_ou(self, ou_name: str, parent_id: str) -> Optional[Dict[str, Any]]:
        """Find existing OU by name under a parent."""
        try:
            response = self.org_client.list_organizational_units_for_parent(ParentId=parent_id)

            for ou in response.get("OrganizationalUnits", []):
                if ou["Name"] == ou_name:
                    return ou

            return None

        except Exception as e:
            logger.warning(f"Error checking for existing OU {ou_name}: {e}")
            return None

    def list_organizational_units(self) -> List[Dict[str, Any]]:
        """List all organizational units in the organization."""
        try:
            root_id = self._get_organization_root()
            all_ous = []

            def collect_ous(parent_id: str, level: int = 0):
                response = self.org_client.list_organizational_units_for_parent(ParentId=parent_id)

                for ou in response.get("OrganizationalUnits", []):
                    ou["Level"] = level
                    ou["ParentId"] = parent_id
                    all_ous.append(ou)

                    # Recursively collect child OUs
                    collect_ous(ou["Id"], level + 1)

            collect_ous(root_id)

            logger.info(f"Found {len(all_ous)} organizational units")
            return all_ous

        except Exception as e:
            logger.error(f"Failed to list organizational units: {e}")
            raise

    def delete_ou(self, ou_id: str) -> bool:
        """
        Delete an organizational unit.

        Args:
            ou_id: OU ID to delete

        Returns:
            True if successful
        """
        try:
            # Check if OU has any accounts
            accounts_response = self.org_client.list_accounts_for_parent(ParentId=ou_id)

            if accounts_response.get("Accounts"):
                raise Exception(f"Cannot delete OU {ou_id}: it contains accounts")

            # Check if OU has child OUs
            ous_response = self.org_client.list_organizational_units_for_parent(ParentId=ou_id)

            if ous_response.get("OrganizationalUnits"):
                raise Exception(f"Cannot delete OU {ou_id}: it contains child OUs")

            # Delete the OU
            self.org_client.delete_organizational_unit(OrganizationalUnitId=ou_id)

            logger.info(f"Deleted OU: {ou_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete OU {ou_id}: {e}")
            raise

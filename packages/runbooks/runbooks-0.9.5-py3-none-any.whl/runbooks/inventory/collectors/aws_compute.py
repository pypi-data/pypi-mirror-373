"""
AWS compute resource collector.

This module provides specialized collection of compute resources including
EC2 instances, Lambda functions, ECS clusters/services, and related components.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from runbooks.inventory.collectors.base import BaseResourceCollector, CollectionContext
from runbooks.inventory.models.resource import AWSResource, ResourceCost, ResourceState
from runbooks.inventory.utils.aws_helpers import aws_api_retry


class ComputeResourceCollector(BaseResourceCollector):
    """
    Collector for AWS compute resources.

    Handles discovery and inventory of:
    - EC2 instances, images, snapshots, volumes
    - Lambda functions and layers
    - ECS clusters, services, and tasks
    - Auto Scaling groups
    - Elastic Beanstalk applications
    """

    service_category = "compute"
    supported_resources = {
        "ec2:instance",
        "ec2:image",
        "ec2:snapshot",
        "ec2:volume",
        "lambda:function",
        "lambda:layer",
        "ecs:cluster",
        "ecs:service",
        "ecs:task",
        "autoscaling:group",
        "elasticbeanstalk:application",
    }
    requires_org_access = False

    def collect_resources(
        self, context: CollectionContext, resource_filters: Optional[Dict[str, Any]] = None
    ) -> List[AWSResource]:
        """
        Collect compute resources from AWS account/region.

        Args:
            context: Collection context with account, region, and options
            resource_filters: Optional filters to apply during collection

        Returns:
            List of discovered compute resources
        """
        resources = []
        resource_filters = resource_filters or {}

        logger.info(
            f"Starting compute resource collection in {context.region} for account {context.account.account_id}"
        )

        # Collect each supported resource type
        for resource_type in context.resource_types.intersection(self.supported_resources):
            try:
                if resource_type.startswith("ec2:"):
                    resources.extend(self._collect_ec2_resources(context, resource_type, resource_filters))
                elif resource_type.startswith("lambda:"):
                    resources.extend(self._collect_lambda_resources(context, resource_type, resource_filters))
                elif resource_type.startswith("ecs:"):
                    resources.extend(self._collect_ecs_resources(context, resource_type, resource_filters))
                elif resource_type.startswith("autoscaling:"):
                    resources.extend(self._collect_autoscaling_resources(context, resource_type, resource_filters))
                elif resource_type.startswith("elasticbeanstalk:"):
                    resources.extend(self._collect_beanstalk_resources(context, resource_type, resource_filters))

            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                logger.error(f"Failed to collect {resource_type} in {context.region}: {error_code} - {e}")
                if error_code in ["UnauthorizedOperation", "AccessDenied"]:
                    logger.warning(f"Insufficient permissions for {resource_type}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error collecting {resource_type}: {e}")
                continue

        logger.info(f"Collected {len(resources)} compute resources from {context.region}")
        return resources

    @aws_api_retry(max_retries=3)
    def _collect_ec2_resources(
        self, context: CollectionContext, resource_type: str, filters: Dict[str, Any]
    ) -> List[AWSResource]:
        """Collect EC2 resources (instances, volumes, snapshots, images)."""
        resources = []
        ec2_client = self.get_client("ec2", context.region)

        if resource_type == "ec2:instance":
            resources.extend(self._collect_ec2_instances(ec2_client, context, filters))
        elif resource_type == "ec2:volume":
            resources.extend(self._collect_ebs_volumes(ec2_client, context, filters))
        elif resource_type == "ec2:snapshot":
            resources.extend(self._collect_ebs_snapshots(ec2_client, context, filters))
        elif resource_type == "ec2:image":
            resources.extend(self._collect_ec2_images(ec2_client, context, filters))

        return resources

    def _collect_ec2_instances(
        self, ec2_client: boto3.client, context: CollectionContext, filters: Dict[str, Any]
    ) -> List[AWSResource]:
        """Collect EC2 instances."""
        resources = []

        try:
            paginator = ec2_client.get_paginator("describe_instances")

            for page in paginator.paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        resource = self._create_ec2_instance_resource(instance, context)
                        if resource:
                            resources.append(resource)

            logger.debug(f"Collected {len(resources)} EC2 instances")

        except ClientError as e:
            logger.error(f"Failed to collect EC2 instances: {e}")
            raise

        return resources

    def _create_ec2_instance_resource(
        self, instance_data: Dict[str, Any], context: CollectionContext
    ) -> Optional[AWSResource]:
        """Create AWSResource from EC2 instance data."""
        try:
            instance_id = instance_data["InstanceId"]
            instance_type = instance_data["InstanceType"]
            state = instance_data["State"]["Name"]

            # Map EC2 state to ResourceState
            state_mapping = {
                "pending": ResourceState.PENDING,
                "running": ResourceState.RUNNING,
                "shutting-down": ResourceState.PENDING,
                "terminated": ResourceState.TERMINATED,
                "stopping": ResourceState.PENDING,
                "stopped": ResourceState.STOPPED,
            }

            resource_state = state_mapping.get(state, ResourceState.UNKNOWN)

            # Extract tags
            tags = {}
            for tag in instance_data.get("Tags", []):
                tags[tag["Key"]] = tag["Value"]

            # Get instance name
            instance_name = tags.get("Name", instance_id)

            # Extract security groups
            security_groups = [sg["GroupId"] for sg in instance_data.get("SecurityGroups", [])]

            # Determine public access
            public_access = bool(instance_data.get("PublicIpAddress"))

            # Create resource configuration
            configuration = {
                "instance_type": instance_type,
                "image_id": instance_data.get("ImageId"),
                "launch_time": instance_data.get("LaunchTime"),
                "platform": instance_data.get("Platform"),
                "subnet_id": instance_data.get("SubnetId"),
                "vpc_id": instance_data.get("VpcId"),
                "private_ip": instance_data.get("PrivateIpAddress"),
                "public_ip": instance_data.get("PublicIpAddress"),
                "monitoring": instance_data.get("Monitoring", {}).get("State"),
                "ebs_optimized": instance_data.get("EbsOptimized", False),
            }

            # Create cost estimate (rough approximation)
            cost_info = None
            if context.include_costs:
                # Simple cost estimation based on instance type
                # In production, use AWS Cost Explorer API
                cost_info = self._estimate_ec2_cost(instance_type, resource_state)

            # Create resource metadata
            metadata = self._create_resource_metadata(context, instance_data)

            return AWSResource(
                resource_id=instance_id,
                resource_type="ec2:instance",
                resource_arn=f"arn:aws:ec2:{context.region}:{context.account.account_id}:instance/{instance_id}",
                resource_name=instance_name,
                state=resource_state,
                creation_date=instance_data.get("LaunchTime"),
                account_id=context.account.account_id,
                region=context.region,
                availability_zone=instance_data.get("Placement", {}).get("AvailabilityZone"),
                configuration=configuration,
                tags=tags,
                security_groups=security_groups,
                public_access=public_access,
                cost_info=cost_info,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Error creating EC2 instance resource: {e}")
            return None

    def _collect_ebs_volumes(
        self, ec2_client: boto3.client, context: CollectionContext, filters: Dict[str, Any]
    ) -> List[AWSResource]:
        """Collect EBS volumes."""
        resources = []

        try:
            paginator = ec2_client.get_paginator("describe_volumes")

            for page in paginator.paginate():
                for volume in page["Volumes"]:
                    resource = self._create_ebs_volume_resource(volume, context)
                    if resource:
                        resources.append(resource)

            logger.debug(f"Collected {len(resources)} EBS volumes")

        except ClientError as e:
            logger.error(f"Failed to collect EBS volumes: {e}")
            raise

        return resources

    def _create_ebs_volume_resource(
        self, volume_data: Dict[str, Any], context: CollectionContext
    ) -> Optional[AWSResource]:
        """Create AWSResource from EBS volume data."""
        try:
            volume_id = volume_data["VolumeId"]
            state = volume_data["State"]

            # Map EBS state to ResourceState
            state_mapping = {
                "creating": ResourceState.CREATING,
                "available": ResourceState.AVAILABLE,
                "in-use": ResourceState.IN_USE,
                "deleting": ResourceState.DELETING,
                "deleted": ResourceState.TERMINATED,
                "error": ResourceState.UNKNOWN,
            }

            resource_state = state_mapping.get(state, ResourceState.UNKNOWN)

            # Extract tags
            tags = {}
            for tag in volume_data.get("Tags", []):
                tags[tag["Key"]] = tag["Value"]

            volume_name = tags.get("Name", volume_id)

            # Configuration details
            configuration = {
                "volume_type": volume_data.get("VolumeType"),
                "size": volume_data.get("Size"),
                "iops": volume_data.get("Iops"),
                "encrypted": volume_data.get("Encrypted", False),
                "kms_key_id": volume_data.get("KmsKeyId"),
                "throughput": volume_data.get("Throughput"),
            }

            # Check attachments
            attachments = volume_data.get("Attachments", [])
            attached_to = [att["InstanceId"] for att in attachments if att.get("State") == "attached"]

            # Cost estimation
            cost_info = None
            if context.include_costs:
                cost_info = self._estimate_ebs_cost(volume_data)

            metadata = self._create_resource_metadata(context, volume_data)

            return AWSResource(
                resource_id=volume_id,
                resource_type="ec2:volume",
                resource_arn=f"arn:aws:ec2:{context.region}:{context.account.account_id}:volume/{volume_id}",
                resource_name=volume_name,
                state=resource_state,
                creation_date=volume_data.get("CreateTime"),
                account_id=context.account.account_id,
                region=context.region,
                availability_zone=volume_data.get("AvailabilityZone"),
                configuration=configuration,
                tags=tags,
                encryption_status="encrypted" if volume_data.get("Encrypted") else "not-encrypted",
                cost_info=cost_info,
                metadata=metadata,
                dependencies=[
                    f"arn:aws:ec2:{context.region}:{context.account.account_id}:instance/{instance_id}"
                    for instance_id in attached_to
                ],
            )

        except Exception as e:
            logger.error(f"Error creating EBS volume resource: {e}")
            return None

    @aws_api_retry(max_retries=3)
    def _collect_lambda_resources(
        self, context: CollectionContext, resource_type: str, filters: Dict[str, Any]
    ) -> List[AWSResource]:
        """Collect Lambda resources (functions, layers)."""
        resources = []
        lambda_client = self.get_client("lambda", context.region)

        if resource_type == "lambda:function":
            resources.extend(self._collect_lambda_functions(lambda_client, context, filters))
        elif resource_type == "lambda:layer":
            resources.extend(self._collect_lambda_layers(lambda_client, context, filters))

        return resources

    def _collect_lambda_functions(
        self, lambda_client: boto3.client, context: CollectionContext, filters: Dict[str, Any]
    ) -> List[AWSResource]:
        """Collect Lambda functions."""
        resources = []

        try:
            paginator = lambda_client.get_paginator("list_functions")

            for page in paginator.paginate():
                for function in page["Functions"]:
                    resource = self._create_lambda_function_resource(function, context)
                    if resource:
                        resources.append(resource)

            logger.debug(f"Collected {len(resources)} Lambda functions")

        except ClientError as e:
            logger.error(f"Failed to collect Lambda functions: {e}")
            raise

        return resources

    def _create_lambda_function_resource(
        self, function_data: Dict[str, Any], context: CollectionContext
    ) -> Optional[AWSResource]:
        """Create AWSResource from Lambda function data."""
        try:
            function_name = function_data["FunctionName"]
            function_arn = function_data["FunctionArn"]

            # Lambda functions are always "available" when listed
            resource_state = ResourceState.AVAILABLE

            # Configuration details
            configuration = {
                "runtime": function_data.get("Runtime"),
                "handler": function_data.get("Handler"),
                "code_size": function_data.get("CodeSize"),
                "memory_size": function_data.get("MemorySize"),
                "timeout": function_data.get("Timeout"),
                "environment": function_data.get("Environment", {}).get("Variables", {}),
                "role": function_data.get("Role"),
                "vpc_config": function_data.get("VpcConfig"),
                "last_modified": function_data.get("LastModified"),
            }

            # Cost estimation for Lambda
            cost_info = None
            if context.include_costs:
                cost_info = self._estimate_lambda_cost(function_data)

            metadata = self._create_resource_metadata(context, function_data)

            return AWSResource(
                resource_id=function_name,
                resource_type="lambda:function",
                resource_arn=function_arn,
                resource_name=function_name,
                state=resource_state,
                creation_date=datetime.fromisoformat(function_data.get("LastModified", "").replace("Z", "+00:00")),
                account_id=context.account.account_id,
                region=context.region,
                configuration=configuration,
                tags={},  # Lambda tags require separate API call
                cost_info=cost_info,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Error creating Lambda function resource: {e}")
            return None

    def _collect_ecs_resources(
        self, context: CollectionContext, resource_type: str, filters: Dict[str, Any]
    ) -> List[AWSResource]:
        """Collect ECS resources (clusters, services, tasks)."""
        # Implementation for ECS resources
        return []

    def _collect_autoscaling_resources(
        self, context: CollectionContext, resource_type: str, filters: Dict[str, Any]
    ) -> List[AWSResource]:
        """Collect Auto Scaling resources."""
        # Implementation for Auto Scaling groups
        return []

    def _collect_beanstalk_resources(
        self, context: CollectionContext, resource_type: str, filters: Dict[str, Any]
    ) -> List[AWSResource]:
        """Collect Elastic Beanstalk resources."""
        # Implementation for Beanstalk applications
        return []

    def get_resource_costs(self, resources: List[AWSResource], context: CollectionContext) -> Dict[str, float]:
        """Get cost information for compute resources."""
        costs = {}

        if not context.include_costs:
            return costs

        # Group resources by type for batch cost calculation
        ec2_instances = [r for r in resources if r.resource_type == "ec2:instance"]
        ebs_volumes = [r for r in resources if r.resource_type == "ec2:volume"]
        lambda_functions = [r for r in resources if r.resource_type == "lambda:function"]

        # Calculate costs for each resource type
        # In production, integrate with AWS Cost Explorer API
        for instance in ec2_instances:
            if instance.cost_info:
                costs[instance.resource_arn] = instance.cost_info.monthly_cost or 0.0

        for volume in ebs_volumes:
            if volume.cost_info:
                costs[volume.resource_arn] = volume.cost_info.monthly_cost or 0.0

        for function in lambda_functions:
            if function.cost_info:
                costs[function.resource_arn] = function.cost_info.monthly_cost or 0.0

        return costs

    def _estimate_ec2_cost(self, instance_type: str, state: ResourceState) -> Optional[ResourceCost]:
        """Estimate monthly cost for EC2 instance."""
        if state not in [ResourceState.RUNNING, ResourceState.PENDING]:
            return None

        # Simplified cost estimation (replace with actual pricing API)
        base_costs = {
            "t2.micro": 8.5,
            "t2.small": 17.0,
            "t2.medium": 34.0,
            "t3.micro": 7.5,
            "t3.small": 15.0,
            "t3.medium": 30.0,
            "m5.large": 70.0,
            "m5.xlarge": 140.0,
            "c5.large": 62.0,
            "r5.large": 91.0,
        }

        monthly_cost = base_costs.get(instance_type, 50.0)  # Default estimate

        return ResourceCost(monthly_cost=monthly_cost, currency="USD", cost_breakdown={"compute": monthly_cost})

    def _estimate_ebs_cost(self, volume_data: Dict[str, Any]) -> Optional[ResourceCost]:
        """Estimate monthly cost for EBS volume."""
        volume_type = volume_data.get("VolumeType", "gp2")
        size_gb = volume_data.get("Size", 0)

        # Simplified EBS pricing per GB per month
        prices_per_gb = {"gp2": 0.10, "gp3": 0.08, "io1": 0.125, "io2": 0.125, "st1": 0.045, "sc1": 0.025}

        price_per_gb = prices_per_gb.get(volume_type, 0.10)
        monthly_cost = size_gb * price_per_gb

        cost_breakdown = {"storage": monthly_cost}

        # Add IOPS cost for provisioned IOPS volumes
        if volume_type in ["io1", "io2"] and volume_data.get("Iops"):
            iops_cost = volume_data["Iops"] * 0.065  # $0.065 per IOPS per month
            cost_breakdown["iops"] = iops_cost
            monthly_cost += iops_cost

        return ResourceCost(monthly_cost=monthly_cost, currency="USD", cost_breakdown=cost_breakdown)

    def _estimate_lambda_cost(self, function_data: Dict[str, Any]) -> Optional[ResourceCost]:
        """Estimate monthly cost for Lambda function."""
        memory_mb = function_data.get("MemorySize", 128)

        # Lambda pricing is based on requests and GB-seconds
        # This is a very rough estimate - actual costs depend on usage
        estimated_monthly_requests = 10000  # Assumption
        estimated_avg_duration_ms = 1000  # Assumption

        # Calculate GB-seconds
        gb_seconds = (memory_mb / 1024) * (estimated_avg_duration_ms / 1000) * estimated_monthly_requests

        # Lambda pricing (simplified)
        request_cost = estimated_monthly_requests * 0.0000002  # $0.20 per 1M requests
        compute_cost = gb_seconds * 0.0000166667  # $0.0000166667 per GB-second

        monthly_cost = request_cost + compute_cost

        return ResourceCost(
            monthly_cost=monthly_cost,
            currency="USD",
            cost_breakdown={"requests": request_cost, "compute": compute_cost},
        )

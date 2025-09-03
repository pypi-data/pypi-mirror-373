"""
Tagging Operations Module.

Provides comprehensive cross-service AWS resource tagging capabilities including
bulk tagging operations, tag compliance enforcement, and tag management workflows.

Migrated and enhanced from:
- aws/tagging_lambda_handler.py
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import ClientError
from loguru import logger

from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus


class TaggingOperations(BaseOperation):
    """
    Cross-service AWS resource tagging operations.

    Handles tagging operations across multiple AWS services with support for
    bulk operations, compliance enforcement, and tag lifecycle management.
    """

    service_name = "resourcegroupstaggingapi"
    supported_operations = {
        "tag_resources",
        "untag_resources",
        "get_resources_by_tags",
        "apply_tag_template",
        "enforce_tag_compliance",
        "generate_tag_report",
        "copy_tags",
        "standardize_tags",
    }
    requires_confirmation = False  # Tagging is generally safe

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None, dry_run: bool = False):
        """Initialize tagging operations."""
        super().__init__(profile, region, dry_run)
        self.default_tags = self._load_default_tags()

    def _load_default_tags(self) -> Dict[str, str]:
        """Load default tag templates."""
        # In production, this could load from a configuration file
        return {
            "Environment": "Production",
            "Project": "CloudOps",
            "ManagedBy": "CloudOps-Runbooks",
            "CreatedDate": datetime.utcnow().strftime("%Y-%m-%d"),
            "CostCenter": "IT-Operations",
        }

    def execute_operation(self, context: OperationContext, operation_type: str, **kwargs) -> List[OperationResult]:
        """
        Execute tagging operation.

        Args:
            context: Operation context
            operation_type: Type of operation to execute
            **kwargs: Operation-specific arguments

        Returns:
            List of operation results
        """
        self.validate_context(context)

        if operation_type == "tag_resources":
            return self.tag_resources(context, **kwargs)
        elif operation_type == "untag_resources":
            return self.untag_resources(context, **kwargs)
        elif operation_type == "get_resources_by_tags":
            return self.get_resources_by_tags(context, **kwargs)
        elif operation_type == "apply_tag_template":
            return self.apply_tag_template(context, **kwargs)
        elif operation_type == "enforce_tag_compliance":
            return self.enforce_tag_compliance(context, **kwargs)
        elif operation_type == "generate_tag_report":
            return self.generate_tag_report(context, **kwargs)
        elif operation_type == "copy_tags":
            return self.copy_tags(context, **kwargs)
        elif operation_type == "standardize_tags":
            return self.standardize_tags(context, **kwargs)
        else:
            raise ValueError(f"Unsupported operation: {operation_type}")

    def tag_resources(
        self,
        context: OperationContext,
        resource_arns: List[str],
        tags: Dict[str, str],
        merge_with_defaults: bool = True,
    ) -> List[OperationResult]:
        """
        Add tags to AWS resources.

        Args:
            context: Operation context
            resource_arns: List of resource ARNs to tag
            tags: Tags to apply to resources
            merge_with_defaults: Whether to merge with default tags

        Returns:
            List of operation results
        """
        tagging_client = self.get_client("resourcegroupstaggingapi", context.region)

        # Merge with default tags if requested
        final_tags = {}
        if merge_with_defaults:
            final_tags.update(self.default_tags)
        final_tags.update(tags)

        results = []

        for resource_arn in resource_arns:
            result = self.create_operation_result(context, "tag_resources", "aws:resource", resource_arn)

            try:
                if context.dry_run:
                    logger.info(f"[DRY-RUN] Would tag resource {resource_arn} with {len(final_tags)} tags")
                    result.mark_completed(OperationStatus.DRY_RUN)
                else:
                    response = self.execute_aws_call(
                        tagging_client, "tag_resources", ResourceARNList=[resource_arn], Tags=final_tags
                    )

                    if response.get("FailedResourcesMap"):
                        failed_arns = list(response["FailedResourcesMap"].keys())
                        if resource_arn in failed_arns:
                            error_info = response["FailedResourcesMap"][resource_arn]
                            error_msg = f"Failed to tag resource: {error_info.get('ErrorMessage', 'Unknown error')}"
                            result.mark_completed(OperationStatus.FAILED, error_msg)
                        else:
                            result.mark_completed(OperationStatus.SUCCESS)
                            logger.info(f"Successfully tagged resource {resource_arn}")
                    else:
                        result.mark_completed(OperationStatus.SUCCESS)
                        logger.info(f"Successfully tagged resource {resource_arn}")

                    result.response_data = response

            except ClientError as e:
                error_msg = f"Failed to tag resource {resource_arn}: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        return results

    def untag_resources(
        self, context: OperationContext, resource_arns: List[str], tag_keys: List[str]
    ) -> List[OperationResult]:
        """
        Remove tags from AWS resources.

        Args:
            context: Operation context
            resource_arns: List of resource ARNs to untag
            tag_keys: Tag keys to remove

        Returns:
            List of operation results
        """
        tagging_client = self.get_client("resourcegroupstaggingapi", context.region)
        results = []

        for resource_arn in resource_arns:
            result = self.create_operation_result(context, "untag_resources", "aws:resource", resource_arn)

            try:
                if context.dry_run:
                    logger.info(f"[DRY-RUN] Would remove {len(tag_keys)} tags from resource {resource_arn}")
                    result.mark_completed(OperationStatus.DRY_RUN)
                else:
                    response = self.execute_aws_call(
                        tagging_client, "untag_resources", ResourceARNList=[resource_arn], TagKeys=tag_keys
                    )

                    if response.get("FailedResourcesMap"):
                        failed_arns = list(response["FailedResourcesMap"].keys())
                        if resource_arn in failed_arns:
                            error_info = response["FailedResourcesMap"][resource_arn]
                            error_msg = f"Failed to untag resource: {error_info.get('ErrorMessage', 'Unknown error')}"
                            result.mark_completed(OperationStatus.FAILED, error_msg)
                        else:
                            result.mark_completed(OperationStatus.SUCCESS)
                            logger.info(f"Successfully untagged resource {resource_arn}")
                    else:
                        result.mark_completed(OperationStatus.SUCCESS)
                        logger.info(f"Successfully untagged resource {resource_arn}")

                    result.response_data = response

            except ClientError as e:
                error_msg = f"Failed to untag resource {resource_arn}: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        return results

    def get_resources_by_tags(
        self,
        context: OperationContext,
        tag_filters: Optional[List[Dict[str, Union[str, List[str]]]]] = None,
        resource_type_filters: Optional[List[str]] = None,
        include_compliance_details: bool = False,
    ) -> List[OperationResult]:
        """
        Find AWS resources by tags.

        Args:
            context: Operation context
            tag_filters: Tag filters to apply
            resource_type_filters: Resource type filters
            include_compliance_details: Include compliance information

        Returns:
            List of operation results with resource information
        """
        tagging_client = self.get_client("resourcegroupstaggingapi", context.region)

        result = self.create_operation_result(context, "get_resources_by_tags", "aws:search", "tag_search")

        try:
            get_params = {}

            if tag_filters:
                get_params["TagFilters"] = tag_filters
            if resource_type_filters:
                get_params["ResourceTypeFilters"] = resource_type_filters
            if include_compliance_details:
                get_params["IncludeComplianceDetails"] = True

            resources = []
            paginator = tagging_client.get_paginator("get_resources")

            for page in paginator.paginate(**get_params):
                resources.extend(page.get("ResourceTagMappingList", []))

            result.response_data = {
                "resources": resources,
                "resource_count": len(resources),
                "search_filters": {
                    "tag_filters": tag_filters,
                    "resource_type_filters": resource_type_filters,
                },
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Found {len(resources)} resources matching tag criteria")

        except ClientError as e:
            error_msg = f"Failed to search resources by tags: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def apply_tag_template(
        self,
        context: OperationContext,
        resource_arns: List[str],
        template_name: str,
        template_values: Optional[Dict[str, str]] = None,
    ) -> List[OperationResult]:
        """
        Apply a predefined tag template to resources.

        Args:
            context: Operation context
            resource_arns: Resources to tag
            template_name: Name of tag template to apply
            template_values: Values to substitute in template

        Returns:
            List of operation results
        """
        # Define tag templates
        templates = {
            "production": {
                "Environment": "Production",
                "Backup": "Required",
                "Monitoring": "Enabled",
                "CostCenter": "Production-Workloads",
                "Owner": "DevOps-Team",
            },
            "development": {
                "Environment": "Development",
                "Backup": "Optional",
                "Monitoring": "Basic",
                "CostCenter": "Development",
                "Owner": "Development-Team",
            },
            "security": {
                "SecurityLevel": "High",
                "DataClassification": "Confidential",
                "ComplianceRequired": "true",
                "EncryptionRequired": "true",
                "AccessLogging": "Enabled",
            },
            "cost-optimization": {
                "CostOptimization": "Enabled",
                "AutoShutdown": "Enabled",
                "RightSizing": "Required",
                "ResourceReview": "Monthly",
            },
        }

        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(templates.keys())}")

        template_tags = templates[template_name].copy()

        # Apply template value substitutions
        if template_values:
            for key, value in template_tags.items():
                for placeholder, replacement in template_values.items():
                    template_tags[key] = value.replace(f"{{{placeholder}}}", replacement)

        # Add template metadata
        template_tags["TagTemplate"] = template_name
        template_tags["TaggedDate"] = datetime.utcnow().strftime("%Y-%m-%d")

        return self.tag_resources(context, resource_arns, template_tags, merge_with_defaults=True)

    def enforce_tag_compliance(
        self,
        context: OperationContext,
        required_tags: List[str],
        resource_type_filters: Optional[List[str]] = None,
        auto_remediate: bool = False,
    ) -> List[OperationResult]:
        """
        Enforce tag compliance across resources.

        Args:
            context: Operation context
            required_tags: List of required tag keys
            resource_type_filters: Resource types to check
            auto_remediate: Automatically add missing tags

        Returns:
            List of operation results with compliance information
        """
        result = self.create_operation_result(context, "enforce_tag_compliance", "aws:compliance", "tag_compliance")

        try:
            # Get all resources in scope
            search_results = self.get_resources_by_tags(
                context, resource_type_filters=resource_type_filters, include_compliance_details=True
            )

            if not search_results or search_results[0].status != OperationStatus.SUCCESS:
                result.mark_completed(OperationStatus.FAILED, "Failed to retrieve resources for compliance check")
                return [result]

            resources = search_results[0].response_data["resources"]
            non_compliant_resources = []

            for resource in resources:
                resource_arn = resource["ResourceARN"]
                existing_tags = {tag["Key"]: tag["Value"] for tag in resource.get("Tags", [])}
                missing_tags = [tag for tag in required_tags if tag not in existing_tags]

                if missing_tags:
                    non_compliant_resources.append(
                        {
                            "resource_arn": resource_arn,
                            "missing_tags": missing_tags,
                            "existing_tags": existing_tags,
                        }
                    )

            compliance_rate = (
                (len(resources) - len(non_compliant_resources)) / len(resources) * 100 if resources else 100
            )

            compliance_report = {
                "total_resources": len(resources),
                "compliant_resources": len(resources) - len(non_compliant_resources),
                "non_compliant_resources": len(non_compliant_resources),
                "compliance_rate": compliance_rate,
                "required_tags": required_tags,
                "non_compliant_details": non_compliant_resources,
            }

            # Auto-remediation if enabled
            if auto_remediate and non_compliant_resources:
                logger.info(f"Auto-remediating {len(non_compliant_resources)} non-compliant resources")

                for resource_info in non_compliant_resources:
                    # Apply default values for missing tags
                    remediation_tags = {}
                    for tag_key in resource_info["missing_tags"]:
                        remediation_tags[tag_key] = "AUTO-REMEDIATED"

                    self.tag_resources(
                        context, [resource_info["resource_arn"]], remediation_tags, merge_with_defaults=False
                    )

            result.response_data = compliance_report
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Tag compliance check completed: {compliance_rate:.1f}% compliant")

        except Exception as e:
            error_msg = f"Failed to enforce tag compliance: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def generate_tag_report(
        self,
        context: OperationContext,
        resource_type_filters: Optional[List[str]] = None,
        include_cost_allocation: bool = False,
    ) -> List[OperationResult]:
        """
        Generate comprehensive tag usage report.

        Args:
            context: Operation context
            resource_type_filters: Resource types to include in report
            include_cost_allocation: Include cost allocation tag analysis

        Returns:
            List of operation results with tag report
        """
        result = self.create_operation_result(context, "generate_tag_report", "aws:report", "tag_report")

        try:
            # Get all resources
            search_results = self.get_resources_by_tags(context, resource_type_filters=resource_type_filters)

            if not search_results or search_results[0].status != OperationStatus.SUCCESS:
                result.mark_completed(OperationStatus.FAILED, "Failed to retrieve resources for report")
                return [result]

            resources = search_results[0].response_data["resources"]

            # Analyze tag usage
            tag_usage = {}
            resource_types = {}
            untagged_resources = []

            for resource in resources:
                resource_type = resource["ResourceARN"].split(":")[2]  # Extract service from ARN
                resource_types[resource_type] = resource_types.get(resource_type, 0) + 1

                tags = resource.get("Tags", [])
                if not tags:
                    untagged_resources.append(resource["ResourceARN"])
                    continue

                for tag in tags:
                    key = tag["Key"]
                    value = tag["Value"]

                    if key not in tag_usage:
                        tag_usage[key] = {"count": 0, "values": {}}

                    tag_usage[key]["count"] += 1
                    tag_usage[key]["values"][value] = tag_usage[key]["values"].get(value, 0) + 1

            # Generate report
            report = {
                "summary": {
                    "total_resources": len(resources),
                    "tagged_resources": len(resources) - len(untagged_resources),
                    "untagged_resources": len(untagged_resources),
                    "tagging_coverage": (len(resources) - len(untagged_resources)) / len(resources) * 100
                    if resources
                    else 0,
                    "unique_tag_keys": len(tag_usage),
                },
                "resource_types": resource_types,
                "tag_usage": tag_usage,
                "untagged_resources": untagged_resources,
                "recommendations": self._generate_tag_recommendations(tag_usage, len(resources)),
            }

            result.response_data = report
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Generated tag report: {len(resources)} resources analyzed")

        except Exception as e:
            error_msg = f"Failed to generate tag report: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def _generate_tag_recommendations(self, tag_usage: Dict[str, Any], total_resources: int) -> List[str]:
        """Generate tag usage recommendations."""
        recommendations = []

        # Find inconsistent tag naming
        similar_tags = {}
        for tag_key in tag_usage.keys():
            normalized_key = tag_key.lower().replace("-", "").replace("_", "").replace(" ", "")
            if normalized_key not in similar_tags:
                similar_tags[normalized_key] = []
            similar_tags[normalized_key].append(tag_key)

        for normalized_key, tag_keys in similar_tags.items():
            if len(tag_keys) > 1:
                recommendations.append(f"Consider standardizing similar tag keys: {', '.join(tag_keys)}")

        # Find rarely used tags
        rare_tags = [
            tag_key
            for tag_key, usage in tag_usage.items()
            if usage["count"] < total_resources * 0.05  # Used on less than 5% of resources
        ]

        if rare_tags:
            recommendations.append(f"Consider removing rarely used tags: {', '.join(rare_tags[:5])}")

        # Suggest common tags
        common_tag_suggestions = ["Environment", "Owner", "Project", "CostCenter", "CreatedBy"]
        missing_common_tags = [tag for tag in common_tag_suggestions if tag not in tag_usage]

        if missing_common_tags:
            recommendations.append(f"Consider adding common tags: {', '.join(missing_common_tags)}")

        return recommendations

    def copy_tags(
        self,
        context: OperationContext,
        source_resource_arn: str,
        target_resource_arns: List[str],
        tag_keys: Optional[List[str]] = None,
    ) -> List[OperationResult]:
        """
        Copy tags from one resource to others.

        Args:
            context: Operation context
            source_resource_arn: Source resource to copy tags from
            target_resource_arns: Target resources to copy tags to
            tag_keys: Specific tag keys to copy (all if None)

        Returns:
            List of operation results
        """
        # First get tags from source resource
        search_results = self.get_resources_by_tags(context)

        if not search_results or search_results[0].status != OperationStatus.SUCCESS:
            result = self.create_operation_result(context, "copy_tags", "aws:operation", "copy_tags_failed")
            result.mark_completed(OperationStatus.FAILED, "Failed to retrieve source resource tags")
            return [result]

        # Find source resource in results
        source_tags = {}
        for resource in search_results[0].response_data["resources"]:
            if resource["ResourceARN"] == source_resource_arn:
                source_tags = {tag["Key"]: tag["Value"] for tag in resource.get("Tags", [])}
                break

        if not source_tags:
            result = self.create_operation_result(context, "copy_tags", "aws:operation", "copy_tags_failed")
            result.mark_completed(
                OperationStatus.FAILED, f"Source resource {source_resource_arn} not found or has no tags"
            )
            return [result]

        # Filter tags if specific keys requested
        if tag_keys:
            source_tags = {k: v for k, v in source_tags.items() if k in tag_keys}

        # Apply tags to target resources
        return self.tag_resources(context, target_resource_arns, source_tags, merge_with_defaults=False)

    def standardize_tags(
        self, context: OperationContext, resource_arns: List[str], standardization_rules: Dict[str, str]
    ) -> List[OperationResult]:
        """
        Standardize tag keys and values according to rules.

        Args:
            context: Operation context
            resource_arns: Resources to standardize
            standardization_rules: Mapping of old tag keys to new tag keys

        Returns:
            List of operation results
        """
        results = []

        for resource_arn in resource_arns:
            result = self.create_operation_result(context, "standardize_tags", "aws:resource", resource_arn)

            try:
                # Get current tags for resource
                search_results = self.get_resources_by_tags(context)

                if not search_results or search_results[0].status != OperationStatus.SUCCESS:
                    result.mark_completed(OperationStatus.FAILED, "Failed to retrieve resource tags")
                    results.append(result)
                    continue

                # Find resource in results
                current_tags = {}
                for resource in search_results[0].response_data["resources"]:
                    if resource["ResourceARN"] == resource_arn:
                        current_tags = {tag["Key"]: tag["Value"] for tag in resource.get("Tags", [])}
                        break

                # Apply standardization rules
                new_tags = {}
                tags_to_remove = []

                for old_key, value in current_tags.items():
                    if old_key in standardization_rules:
                        new_key = standardization_rules[old_key]
                        new_tags[new_key] = value
                        tags_to_remove.append(old_key)
                    else:
                        new_tags[old_key] = value

                if context.dry_run:
                    logger.info(f"[DRY-RUN] Would standardize {len(tags_to_remove)} tags on {resource_arn}")
                    result.mark_completed(OperationStatus.DRY_RUN)
                else:
                    # Remove old tags if they're being renamed
                    if tags_to_remove:
                        self.untag_resources(context, [resource_arn], tags_to_remove)

                    # Apply new standardized tags
                    tag_results = self.tag_resources(context, [resource_arn], new_tags, merge_with_defaults=False)

                    if tag_results and tag_results[0].status == OperationStatus.SUCCESS:
                        result.mark_completed(OperationStatus.SUCCESS)
                        logger.info(f"Successfully standardized tags on {resource_arn}")
                    else:
                        result.mark_completed(OperationStatus.FAILED, "Failed to apply standardized tags")

            except Exception as e:
                error_msg = f"Failed to standardize tags on {resource_arn}: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        return results

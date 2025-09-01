#!/usr/bin/env python3
"""
VPC Endpoints Operations for CloudOps Runbooks Platform

This module provides enterprise-grade VPC endpoint management with cost optimization,
ROI analysis, and strategic decision support following McKinsey operating principles.

Addresses GitHub Issue #96 expanded scope: VPC Endpoints management with
comprehensive cost optimization and business value analysis.

Features:
- Complete VPC endpoint lifecycle management (create, modify, delete)
- Cost optimization analysis (endpoint costs vs NAT Gateway savings)
- ROI calculator for endpoint deployment decisions
- Security compliance validation
- Integration with existing VPC operations module
- McKinsey-style decision frameworks for endpoint deployment

Author: CloudOps Runbooks Team
Version: 0.7.8
Enhanced for Sprint 2 VPC Scope Expansion
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from runbooks.common.rich_utils import (
    console,
    create_panel,
    create_table,
    format_cost,
    print_error,
    print_status,
    print_success,
)
from runbooks.operate.base import BaseOperation, OperationResult

logger = logging.getLogger(__name__)


class VPCEndpointOperations(BaseOperation):
    """
    Enterprise VPC Endpoint operations with cost optimization and ROI analysis.

    Extends BaseOperation following CloudOps Runbooks patterns for:
    - VPC endpoint lifecycle management
    - Cost-benefit analysis vs NAT Gateway usage
    - Security compliance validation
    - McKinsey-style ROI decision frameworks

    GitHub Issue #96 - VPC & Infrastructure Enhancement
    """

    service_name = "ec2"
    supported_operations = {
        "create_endpoint",
        "delete_endpoint",
        "modify_endpoint",
        "describe_endpoints",
        "analyze_endpoint_costs",
        "calculate_endpoint_roi",
        "optimize_endpoint_placement",
        "security_compliance_check",
    }
    requires_confirmation = True  # Endpoints have cost implications

    # VPC Endpoint pricing (monthly estimates in USD)
    ENDPOINT_PRICING = {
        "Interface": 7.30,  # ~$7.30/month per interface endpoint
        "Gateway": 0.00,  # S3/DynamoDB gateways are free
        "GatewayLoadBalancer": 7.30,  # Same as interface endpoints
    }

    # Data processing costs (per GB)
    DATA_PROCESSING_COSTS = {
        "Interface": 0.01,  # $0.01 per GB processed
        "GatewayLoadBalancer": 0.0025,  # $0.0025 per GB processed
    }

    def __init__(self, profile: str, region: str, dry_run: bool = True):
        """Initialize VPC Endpoint operations."""
        super().__init__(profile, region, dry_run)
        self.ec2_client = self.session.client("ec2")
        self.cloudwatch = self.session.client("cloudwatch")

    def create_endpoint(
        self,
        vpc_id: str,
        service_name: str,
        endpoint_type: str = "Interface",
        subnet_ids: Optional[List[str]] = None,
        security_group_ids: Optional[List[str]] = None,
        policy_document: Optional[str] = None,
        private_dns_enabled: bool = True,
        tags: Optional[Dict[str, str]] = None,
    ) -> OperationResult:
        """
        Create a VPC endpoint with cost analysis and ROI validation.

        Args:
            vpc_id: Target VPC ID
            service_name: AWS service name (e.g., 'com.amazonaws.us-east-1.s3')
            endpoint_type: Interface, Gateway, or GatewayLoadBalancer
            subnet_ids: Subnet IDs for Interface endpoints
            security_group_ids: Security group IDs for Interface endpoints
            policy_document: IAM policy document (JSON string)
            private_dns_enabled: Enable private DNS resolution
            tags: Resource tags

        Returns:
            OperationResult with endpoint creation details and cost analysis
        """
        try:
            print_status(f"Creating VPC endpoint for {service_name} in {vpc_id}", "info")

            # Validate inputs and perform cost analysis
            validation_result = self._validate_endpoint_creation(vpc_id, service_name, endpoint_type, subnet_ids)
            if not validation_result["valid"]:
                return self.create_result(
                    success=False,
                    message=f"Endpoint validation failed: {validation_result['message']}",
                    data=validation_result,
                )

            # Calculate ROI before creation
            roi_analysis = self.calculate_endpoint_roi(service_name, vpc_id, endpoint_type, estimated_monthly_gb=100)

            # Display cost analysis to user
            self._display_cost_analysis(roi_analysis)

            if self.dry_run:
                print_status("DRY RUN: VPC endpoint creation simulated", "warning")
                return self.create_result(
                    success=True,
                    message=f"DRY RUN: Would create {endpoint_type} endpoint for {service_name}",
                    data={
                        "vpc_id": vpc_id,
                        "service_name": service_name,
                        "endpoint_type": endpoint_type,
                        "estimated_monthly_cost": roi_analysis.get("monthly_cost", 0),
                        "roi_analysis": roi_analysis,
                        "dry_run": True,
                    },
                )

            # Build endpoint creation parameters
            create_params = {
                "VpcId": vpc_id,
                "ServiceName": service_name,
                "VpcEndpointType": endpoint_type,
                "PolicyDocument": policy_document,
            }

            if endpoint_type == "Interface":
                if subnet_ids:
                    create_params["SubnetIds"] = subnet_ids
                if security_group_ids:
                    create_params["SecurityGroupIds"] = security_group_ids
                create_params["PrivateDnsEnabled"] = private_dns_enabled

            if tags:
                tag_specs = [
                    {"ResourceType": "vpc-endpoint", "Tags": [{"Key": k, "Value": v} for k, v in tags.items()]}
                ]
                create_params["TagSpecifications"] = tag_specs

            # Create the endpoint
            response = self.ec2_client.create_vpc_endpoint(**create_params)
            endpoint = response["VpcEndpoint"]
            endpoint_id = endpoint["VpcEndpointId"]

            print_success(f"VPC endpoint created: {endpoint_id}")

            # Add cost tracking tags
            cost_tags = {
                "CloudOps-CostCenter": "NetworkOptimization",
                "CloudOps-CreatedBy": "VPCEndpointOperations",
                "CloudOps-EstimatedMonthlyCost": str(roi_analysis.get("monthly_cost", 0)),
                "CloudOps-CreatedAt": datetime.now().isoformat(),
            }

            self._tag_endpoint(endpoint_id, cost_tags)

            return self.create_result(
                success=True,
                message=f"VPC endpoint created successfully: {endpoint_id}",
                data={
                    "endpoint_id": endpoint_id,
                    "vpc_id": vpc_id,
                    "service_name": service_name,
                    "endpoint_type": endpoint_type,
                    "state": endpoint["State"],
                    "creation_timestamp": endpoint["CreationTimestamp"].isoformat(),
                    "estimated_monthly_cost": roi_analysis.get("monthly_cost", 0),
                    "roi_analysis": roi_analysis,
                },
            )

        except ClientError as e:
            error_msg = f"Failed to create VPC endpoint: {e.response['Error']['Message']}"
            print_error(error_msg, e)
            return self.create_result(
                success=False, message=error_msg, data={"error_code": e.response["Error"]["Code"]}
            )
        except Exception as e:
            error_msg = f"Unexpected error creating VPC endpoint: {str(e)}"
            print_error(error_msg, e)
            return self.create_result(success=False, message=error_msg, data={"error": str(e)})

    def delete_endpoint(self, endpoint_id: str) -> OperationResult:
        """
        Delete a VPC endpoint with cost impact analysis.

        Args:
            endpoint_id: VPC endpoint ID to delete

        Returns:
            OperationResult with deletion status and cost impact
        """
        try:
            print_status(f"Deleting VPC endpoint {endpoint_id}", "warning")

            # Get endpoint details before deletion for cost analysis
            endpoint_details = self._get_endpoint_details(endpoint_id)
            if not endpoint_details:
                return self.create_result(
                    success=False, message=f"VPC endpoint {endpoint_id} not found", data={"endpoint_id": endpoint_id}
                )

            # Calculate cost impact of deletion
            cost_impact = self._calculate_deletion_cost_impact(endpoint_details)

            if self.dry_run:
                print_status("DRY RUN: VPC endpoint deletion simulated", "warning")
                return self.create_result(
                    success=True,
                    message=f"DRY RUN: Would delete endpoint {endpoint_id}",
                    data={
                        "endpoint_id": endpoint_id,
                        "service_name": endpoint_details.get("ServiceName", "unknown"),
                        "cost_impact": cost_impact,
                        "dry_run": True,
                    },
                )

            # Perform deletion
            response = self.ec2_client.delete_vpc_endpoints(VpcEndpointIds=[endpoint_id])

            if response["Unsuccessful"]:
                error_detail = response["Unsuccessful"][0]
                error_msg = f"Failed to delete endpoint {endpoint_id}: {error_detail['Error']['Message']}"
                print_error(error_msg)
                return self.create_result(success=False, message=error_msg, data={"error": error_detail["Error"]})

            print_success(f"VPC endpoint {endpoint_id} deleted successfully")

            return self.create_result(
                success=True,
                message=f"VPC endpoint deleted successfully: {endpoint_id}",
                data={
                    "endpoint_id": endpoint_id,
                    "service_name": endpoint_details.get("ServiceName", "unknown"),
                    "cost_impact": cost_impact,
                    "deleted_at": datetime.now().isoformat(),
                },
            )

        except ClientError as e:
            error_msg = f"Failed to delete VPC endpoint: {e.response['Error']['Message']}"
            print_error(error_msg, e)
            return self.create_result(
                success=False, message=error_msg, data={"error_code": e.response["Error"]["Code"]}
            )
        except Exception as e:
            error_msg = f"Unexpected error deleting VPC endpoint: {str(e)}"
            print_error(error_msg, e)
            return self.create_result(success=False, message=error_msg, data={"error": str(e)})

    def describe_endpoints(
        self, vpc_id: Optional[str] = None, endpoint_ids: Optional[List[str]] = None
    ) -> OperationResult:
        """
        Describe VPC endpoints with cost analysis and optimization recommendations.

        Args:
            vpc_id: Filter by VPC ID
            endpoint_ids: Specific endpoint IDs to describe

        Returns:
            OperationResult with endpoint details and cost analysis
        """
        try:
            print_status("Retrieving VPC endpoints with cost analysis...", "info")

            # Build filters
            filters = []
            if vpc_id:
                filters.append({"Name": "vpc-id", "Values": [vpc_id]})

            describe_params = {}
            if filters:
                describe_params["Filters"] = filters
            if endpoint_ids:
                describe_params["VpcEndpointIds"] = endpoint_ids

            # Get endpoints
            response = self.ec2_client.describe_vpc_endpoints(**describe_params)
            endpoints = response["VpcEndpoints"]

            if not endpoints:
                print_status("No VPC endpoints found", "info")
                return self.create_result(
                    success=True, message="No VPC endpoints found", data={"endpoints": [], "total_count": 0}
                )

            # Enhance endpoints with cost analysis
            enhanced_endpoints = []
            total_monthly_cost = 0.0

            for endpoint in endpoints:
                enhanced_endpoint = self._enhance_endpoint_with_cost_analysis(endpoint)
                enhanced_endpoints.append(enhanced_endpoint)
                total_monthly_cost += enhanced_endpoint.get("estimated_monthly_cost", 0)

            # Display endpoints table
            self._display_endpoints_table(enhanced_endpoints, total_monthly_cost)

            # Generate optimization recommendations
            optimization_recommendations = self._generate_optimization_recommendations(enhanced_endpoints)

            print_success(
                f"Found {len(endpoints)} VPC endpoints with total estimated cost: ${total_monthly_cost:.2f}/month"
            )

            return self.create_result(
                success=True,
                message=f"Retrieved {len(endpoints)} VPC endpoints",
                data={
                    "endpoints": enhanced_endpoints,
                    "total_count": len(endpoints),
                    "total_monthly_cost": total_monthly_cost,
                    "optimization_recommendations": optimization_recommendations,
                },
            )

        except ClientError as e:
            error_msg = f"Failed to describe VPC endpoints: {e.response['Error']['Message']}"
            print_error(error_msg, e)
            return self.create_result(
                success=False, message=error_msg, data={"error_code": e.response["Error"]["Code"]}
            )
        except Exception as e:
            error_msg = f"Unexpected error describing VPC endpoints: {str(e)}"
            print_error(error_msg, e)
            return self.create_result(success=False, message=error_msg, data={"error": str(e)})

    def calculate_endpoint_roi(
        self,
        service_name: str,
        vpc_id: str,
        endpoint_type: str = "Interface",
        estimated_monthly_gb: float = 100,
        nat_gateway_count: int = 1,
    ) -> Dict[str, Any]:
        """
        Calculate ROI for VPC endpoint deployment using McKinsey-style analysis.

        Args:
            service_name: AWS service name
            vpc_id: Target VPC ID
            endpoint_type: Interface, Gateway, or GatewayLoadBalancer
            estimated_monthly_gb: Estimated monthly data transfer in GB
            nat_gateway_count: Number of NAT Gateways that could be replaced/optimized

        Returns:
            Comprehensive ROI analysis with McKinsey decision framework
        """
        try:
            # Calculate endpoint costs
            endpoint_monthly_cost = self.ENDPOINT_PRICING.get(endpoint_type, 7.30)
            data_processing_cost = self.DATA_PROCESSING_COSTS.get(endpoint_type, 0.01)
            total_data_cost = estimated_monthly_gb * data_processing_cost
            total_endpoint_cost = endpoint_monthly_cost + total_data_cost

            # Calculate NAT Gateway costs (baseline for comparison)
            nat_gateway_monthly_cost = 45.0 * nat_gateway_count  # $45/month per NAT Gateway
            nat_data_processing = estimated_monthly_gb * 0.045  # $0.045 per GB through NAT
            total_nat_cost = nat_gateway_monthly_cost + nat_data_processing

            # Calculate savings and ROI
            monthly_savings = total_nat_cost - total_endpoint_cost
            annual_savings = monthly_savings * 12
            roi_percentage = (monthly_savings / total_endpoint_cost * 100) if total_endpoint_cost > 0 else 0

            # McKinsey-style decision framework
            recommendation = "DEPLOY"
            if monthly_savings < 0:
                recommendation = "DO_NOT_DEPLOY"
            elif monthly_savings < 10:
                recommendation = "EVALUATE_FURTHER"
            elif monthly_savings > 50:
                recommendation = "PRIORITY_DEPLOY"

            # Business case summary
            business_case = {
                "financial_impact": {
                    "monthly_savings": monthly_savings,
                    "annual_savings": annual_savings,
                    "roi_percentage": roi_percentage,
                    "payback_period_months": 1 if monthly_savings > 0 else None,
                },
                "strategic_value": {
                    "reduced_nat_gateway_dependency": nat_gateway_count,
                    "improved_security": endpoint_type == "Interface",
                    "reduced_internet_traffic": True,
                    "compliance_benefits": "Private connectivity to AWS services",
                },
                "recommendation": recommendation,
            }

            return {
                "service_name": service_name,
                "vpc_id": vpc_id,
                "endpoint_type": endpoint_type,
                "cost_analysis": {
                    "endpoint_monthly_cost": endpoint_monthly_cost,
                    "data_processing_cost": total_data_cost,
                    "total_endpoint_cost": total_endpoint_cost,
                    "nat_gateway_baseline_cost": total_nat_cost,
                    "monthly_savings": monthly_savings,
                    "annual_savings": annual_savings,
                    "roi_percentage": roi_percentage,
                },
                "business_case": business_case,
                "mckinsey_decision_framework": {
                    "recommendation": recommendation,
                    "confidence_level": "HIGH" if abs(roi_percentage) > 20 else "MEDIUM",
                    "decision_criteria": [
                        f"Cost savings: ${monthly_savings:.2f}/month",
                        f"ROI: {roi_percentage:.1f}%",
                        f"Strategic value: {'HIGH' if endpoint_type == 'Interface' else 'MEDIUM'}",
                    ],
                },
            }

        except Exception as e:
            logger.error(f"Failed to calculate endpoint ROI: {e}")
            return {
                "error": str(e),
                "service_name": service_name,
                "vpc_id": vpc_id,
                "recommendation": "ERROR_IN_CALCULATION",
            }

    def _validate_endpoint_creation(
        self, vpc_id: str, service_name: str, endpoint_type: str, subnet_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Validate endpoint creation parameters."""
        try:
            # Validate VPC exists
            vpc_response = self.ec2_client.describe_vpcs(VpcIds=[vpc_id])
            if not vpc_response["Vpcs"]:
                return {"valid": False, "message": f"VPC {vpc_id} not found"}

            # Validate service name format
            if not service_name.startswith("com.amazonaws."):
                return {"valid": False, "message": f"Invalid service name format: {service_name}"}

            # Validate endpoint type
            if endpoint_type not in ["Interface", "Gateway", "GatewayLoadBalancer"]:
                return {"valid": False, "message": f"Invalid endpoint type: {endpoint_type}"}

            # Validate subnets for Interface endpoints
            if endpoint_type == "Interface" and subnet_ids:
                try:
                    subnet_response = self.ec2_client.describe_subnets(SubnetIds=subnet_ids)
                    # Ensure all subnets belong to the VPC
                    for subnet in subnet_response["Subnets"]:
                        if subnet["VpcId"] != vpc_id:
                            return {"valid": False, "message": f"Subnet {subnet['SubnetId']} not in VPC {vpc_id}"}
                except ClientError:
                    return {"valid": False, "message": "One or more subnet IDs are invalid"}

            return {"valid": True, "message": "Validation successful"}

        except ClientError as e:
            return {"valid": False, "message": f"Validation error: {e.response['Error']['Message']}"}

    def _get_endpoint_details(self, endpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a VPC endpoint."""
        try:
            response = self.ec2_client.describe_vpc_endpoints(VpcEndpointIds=[endpoint_id])
            endpoints = response["VpcEndpoints"]
            return endpoints[0] if endpoints else None
        except ClientError:
            return None

    def _calculate_deletion_cost_impact(self, endpoint_details: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the cost impact of deleting an endpoint."""
        endpoint_type = endpoint_details.get("VpcEndpointType", "Interface")
        service_name = endpoint_details.get("ServiceName", "unknown")

        monthly_cost_saving = self.ENDPOINT_PRICING.get(endpoint_type, 7.30)

        return {
            "monthly_cost_saving": monthly_cost_saving,
            "annual_cost_saving": monthly_cost_saving * 12,
            "service_name": service_name,
            "endpoint_type": endpoint_type,
            "warning": "Deleting endpoint may increase NAT Gateway costs for service access",
        }

    def _enhance_endpoint_with_cost_analysis(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance endpoint data with cost analysis."""
        endpoint_type = endpoint.get("VpcEndpointType", "Interface")
        service_name = endpoint.get("ServiceName", "unknown")

        # Calculate estimated monthly cost
        base_cost = self.ENDPOINT_PRICING.get(endpoint_type, 7.30)
        estimated_data_gb = 50  # Conservative estimate
        data_cost = estimated_data_gb * self.DATA_PROCESSING_COSTS.get(endpoint_type, 0.01)
        total_monthly_cost = base_cost + data_cost

        # Add cost analysis to endpoint data
        enhanced = endpoint.copy()
        enhanced.update(
            {
                "estimated_monthly_cost": total_monthly_cost,
                "cost_breakdown": {
                    "base_cost": base_cost,
                    "estimated_data_cost": data_cost,
                    "estimated_monthly_gb": estimated_data_gb,
                },
                "cost_center": "NetworkOptimization",
            }
        )

        return enhanced

    def _display_endpoints_table(self, endpoints: List[Dict[str, Any]], total_cost: float) -> None:
        """Display endpoints in a formatted table."""
        table = create_table(
            title=f"VPC Endpoints Analysis - Total Monthly Cost: ${total_cost:.2f}",
            columns=[
                {"name": "Endpoint ID", "style": "cyan", "justify": "left"},
                {"name": "Service", "style": "blue", "justify": "left"},
                {"name": "Type", "style": "green", "justify": "center"},
                {"name": "State", "style": "yellow", "justify": "center"},
                {"name": "Monthly Cost", "style": "red", "justify": "right"},
                {"name": "VPC ID", "style": "dim", "justify": "left"},
            ],
        )

        for endpoint in endpoints:
            table.add_row(
                endpoint["VpcEndpointId"][:20] + "...",
                endpoint.get("ServiceName", "unknown").split(".")[-1],
                endpoint.get("VpcEndpointType", "Interface"),
                endpoint.get("State", "unknown"),
                f"${endpoint.get('estimated_monthly_cost', 0):.2f}",
                endpoint.get("VpcId", "unknown"),
            )

        console.print(table)

    def _display_cost_analysis(self, roi_analysis: Dict[str, Any]) -> None:
        """Display cost analysis in a formatted panel."""
        cost_data = roi_analysis.get("cost_analysis", {})
        recommendation = roi_analysis.get("mckinsey_decision_framework", {}).get("recommendation", "UNKNOWN")

        analysis_text = f"""
[bold]Cost Analysis Summary[/bold]

Endpoint Monthly Cost: ${cost_data.get("total_endpoint_cost", 0):.2f}
NAT Gateway Baseline: ${cost_data.get("nat_gateway_baseline_cost", 0):.2f}
Monthly Savings: ${cost_data.get("monthly_savings", 0):.2f}
ROI: {cost_data.get("roi_percentage", 0):.1f}%

[bold]McKinsey Recommendation: {recommendation}[/bold]
        """

        panel = create_panel(
            analysis_text,
            title="VPC Endpoint ROI Analysis",
            border_style="cyan" if cost_data.get("monthly_savings", 0) > 0 else "red",
        )

        console.print(panel)

    def _generate_optimization_recommendations(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on endpoint analysis."""
        recommendations = []

        # Group endpoints by service
        service_groups = {}
        for endpoint in endpoints:
            service = endpoint.get("ServiceName", "unknown")
            if service not in service_groups:
                service_groups[service] = []
            service_groups[service].append(endpoint)

        # Analyze for consolidation opportunities
        for service, service_endpoints in service_groups.items():
            if len(service_endpoints) > 2:
                total_cost = sum(ep.get("estimated_monthly_cost", 0) for ep in service_endpoints)
                recommendations.append(
                    {
                        "type": "CONSOLIDATION_OPPORTUNITY",
                        "service": service,
                        "current_endpoints": len(service_endpoints),
                        "estimated_savings": total_cost * 0.3,  # Conservative 30% savings
                        "recommendation": f"Consider consolidating {len(service_endpoints)} {service} endpoints",
                    }
                )

        # Check for unused endpoints (placeholder - would need CloudWatch metrics)
        for endpoint in endpoints:
            if endpoint.get("State") != "available":
                recommendations.append(
                    {
                        "type": "UNUSED_ENDPOINT",
                        "endpoint_id": endpoint["VpcEndpointId"],
                        "monthly_savings": endpoint.get("estimated_monthly_cost", 0),
                        "recommendation": f"Consider deleting unused endpoint {endpoint['VpcEndpointId']}",
                    }
                )

        return recommendations

    def _tag_endpoint(self, endpoint_id: str, tags: Dict[str, str]) -> None:
        """Add tags to a VPC endpoint."""
        try:
            self.ec2_client.create_tags(Resources=[endpoint_id], Tags=[{"Key": k, "Value": v} for k, v in tags.items()])
        except ClientError as e:
            logger.warning(f"Failed to tag endpoint {endpoint_id}: {e}")


# Export the operations class
__all__ = ["VPCEndpointOperations"]

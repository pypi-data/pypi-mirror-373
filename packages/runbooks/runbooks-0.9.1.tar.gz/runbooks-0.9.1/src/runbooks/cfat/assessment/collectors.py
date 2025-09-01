"""
AWS Resource Collectors for Cloud Foundations Assessment.

This module provides specialized collectors for gathering AWS resource
information across different services for compliance assessment.

Each collector is responsible for:
- Authenticating with specific AWS services
- Gathering relevant resource configurations
- Normalizing data for assessment validation
- Handling AWS API rate limiting and pagination
- Error handling and retry logic

The collectors follow a common interface pattern and can be used
independently or orchestrated by the assessment engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from loguru import logger

from runbooks.base import CloudFoundationsBase


class BaseCollector(CloudFoundationsBase, ABC):
    """Base class for AWS resource collectors."""

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Collect resources from AWS service."""
        pass

    @abstractmethod
    def get_service_name(self) -> str:
        """Get the AWS service name for this collector."""
        pass


class IAMCollector(BaseCollector):
    """Identity and Access Management resource collector."""

    def get_service_name(self) -> str:
        """Get service name."""
        return "iam"

    def collect(self) -> Dict[str, Any]:
        """
        Collect IAM resources for assessment.

        Returns:
            Dictionary containing IAM resource data
        """
        logger.info("Collecting IAM resources...")

        # Placeholder implementation
        # TODO: Implement actual IAM resource collection
        return {
            "users": [],
            "roles": [],
            "policies": [],
            "groups": [],
            "root_account_mfa": False,
            "password_policy": {},
        }


class VPCCollector(BaseCollector):
    """Virtual Private Cloud resource collector with NAT Gateway cost optimization integration."""

    def get_service_name(self) -> str:
        """Get service name."""
        return "ec2"  # VPC is part of EC2 service

    def collect(self) -> Dict[str, Any]:
        """
        Collect VPC resources for assessment with NAT Gateway cost analysis.

        Returns:
            Dictionary containing VPC resource data including cost optimization insights
        """
        logger.info("Collecting VPC resources with cost optimization analysis...")

        try:
            ec2_client = self.session.client("ec2", region_name=self.region)

            # Collect VPCs
            vpcs_response = ec2_client.describe_vpcs()
            vpcs = vpcs_response.get("Vpcs", [])

            # Collect Subnets
            subnets_response = ec2_client.describe_subnets()
            subnets = subnets_response.get("Subnets", [])

            # Collect NAT Gateways with cost analysis (GitHub Issue #96)
            nat_gateways_response = ec2_client.describe_nat_gateways()
            nat_gateways = nat_gateways_response.get("NatGateways", [])

            # Calculate NAT Gateway costs ($45/month per gateway)
            active_nat_gateways = [ng for ng in nat_gateways if ng.get("State") == "available"]
            nat_cost_analysis = {
                "total_nat_gateways": len(active_nat_gateways),
                "estimated_monthly_cost": len(active_nat_gateways) * 45.0,
                "optimization_opportunities": self._analyze_nat_optimization(active_nat_gateways, subnets),
                "cost_alerts": [],
            }

            if len(active_nat_gateways) > 3:
                nat_cost_analysis["cost_alerts"].append(
                    f"HIGH COST: {len(active_nat_gateways)} NAT Gateways detected. "
                    f"Monthly cost: ${nat_cost_analysis['estimated_monthly_cost']:,.2f}"
                )

            # Collect Security Groups
            sg_response = ec2_client.describe_security_groups()
            security_groups = sg_response.get("SecurityGroups", [])

            # Collect Network ACLs
            nacls_response = ec2_client.describe_network_acls()
            nacls = nacls_response.get("NetworkAcls", [])

            # Collect Internet Gateways
            igw_response = ec2_client.describe_internet_gateways()
            internet_gateways = igw_response.get("InternetGateways", [])

            # Collect VPC Flow Logs
            flow_logs_response = ec2_client.describe_flow_logs()
            flow_logs = flow_logs_response.get("FlowLogs", [])

            # Collect Route Tables for routing analysis
            route_tables_response = ec2_client.describe_route_tables()
            route_tables = route_tables_response.get("RouteTables", [])

            logger.info(
                f"Collected {len(vpcs)} VPCs, {len(nat_gateways)} NAT Gateways, "
                f"estimated monthly NAT cost: ${nat_cost_analysis['estimated_monthly_cost']:,.2f}"
            )

            return {
                "vpcs": vpcs,
                "subnets": subnets,
                "nat_gateways": nat_gateways,
                "nat_cost_analysis": nat_cost_analysis,  # New: Cost optimization data
                "security_groups": security_groups,
                "nacls": nacls,
                "flow_logs": flow_logs,
                "internet_gateways": internet_gateways,
                "route_tables": route_tables,
                "assessment_metadata": {
                    "collector_version": "v0.7.8-vpc-enhanced",
                    "github_issue": "#96",
                    "cost_optimization_enabled": True,
                },
            }

        except Exception as e:
            logger.error(f"Failed to collect VPC resources: {e}")
            return {
                "vpcs": [],
                "subnets": [],
                "nat_gateways": [],
                "nat_cost_analysis": {"error": str(e)},
                "security_groups": [],
                "nacls": [],
                "flow_logs": [],
                "internet_gateways": [],
                "route_tables": [],
                "assessment_metadata": {"collector_version": "v0.7.8-vpc-enhanced", "error": str(e)},
            }

    def _analyze_nat_optimization(self, nat_gateways: List[Dict], subnets: List[Dict]) -> int:
        """
        Analyze NAT Gateway placement for cost optimization opportunities.

        Args:
            nat_gateways: List of NAT Gateway configurations
            subnets: List of subnet configurations

        Returns:
            Number of optimization opportunities found
        """
        opportunities = 0

        # Group NAT Gateways by Availability Zone
        az_nat_count = {}
        for nat in nat_gateways:
            if nat.get("State") == "available":
                subnet_id = nat.get("SubnetId")
                # Find AZ for this subnet
                subnet_az = None
                for subnet in subnets:
                    if subnet.get("SubnetId") == subnet_id:
                        subnet_az = subnet.get("AvailabilityZone")
                        break

                if subnet_az:
                    az_nat_count[subnet_az] = az_nat_count.get(subnet_az, 0) + 1

        # Check for potential consolidation opportunities
        for az, count in az_nat_count.items():
            if count > 1:
                opportunities += count - 1  # Could potentially consolidate to 1 per AZ

        return opportunities

    def run(self) -> "CloudFoundationsResult":
        """
        Run VPC resource collection and return standardized result.

        Returns:
            CloudFoundationsResult with VPC assessment data including NAT Gateway cost analysis
        """
        try:
            # Collect VPC resources with cost optimization analysis
            vpc_data = self.collect()

            # Determine success based on data collection
            success = bool(vpc_data) and not vpc_data.get("assessment_metadata", {}).get("error")

            # Create message with cost insights
            nat_cost_analysis = vpc_data.get("nat_cost_analysis", {})
            total_cost = nat_cost_analysis.get("estimated_monthly_cost", 0)
            total_nats = nat_cost_analysis.get("total_nat_gateways", 0)

            if success:
                message = (
                    f"VPC assessment completed: {len(vpc_data.get('vpcs', []))} VPCs, "
                    f"{total_nats} NAT Gateways, estimated monthly NAT cost: ${total_cost:,.2f}"
                )

                # Add cost alerts to message if present
                cost_alerts = nat_cost_analysis.get("cost_alerts", [])
                if cost_alerts:
                    message += f". {len(cost_alerts)} cost optimization opportunities identified"
            else:
                error = vpc_data.get("assessment_metadata", {}).get("error", "Unknown error")
                message = f"VPC assessment failed: {error}"

            return self.create_result(
                success=success,
                message=message,
                data=vpc_data,
                errors=[vpc_data.get("assessment_metadata", {}).get("error")] if not success else [],
            )

        except Exception as e:
            logger.error(f"VPC collector run failed: {e}")
            return self.create_result(
                success=False, message=f"VPC assessment failed: {str(e)}", data={}, errors=[str(e)]
            )


class CloudTrailCollector(BaseCollector):
    """CloudTrail logging service collector."""

    def get_service_name(self) -> str:
        """Get service name."""
        return "cloudtrail"

    def collect(self) -> Dict[str, Any]:
        """
        Collect CloudTrail resources for assessment.

        Returns:
            Dictionary containing CloudTrail configuration data
        """
        logger.info("Collecting CloudTrail resources...")

        # Placeholder implementation
        # TODO: Implement actual CloudTrail resource collection
        return {
            "trails": [],
            "event_selectors": [],
            "insight_selectors": [],
            "status": {},
        }


class ConfigCollector(BaseCollector):
    """AWS Config service collector."""

    def get_service_name(self) -> str:
        """Get service name."""
        return "config"

    def collect(self) -> Dict[str, Any]:
        """
        Collect AWS Config resources for assessment.

        Returns:
            Dictionary containing Config service data
        """
        logger.info("Collecting AWS Config resources...")

        # Placeholder implementation
        # TODO: Implement actual Config resource collection
        return {
            "configuration_recorders": [],
            "delivery_channels": [],
            "rules": [],
            "remediation_configurations": [],
        }


class OrganizationsCollector(BaseCollector):
    """AWS Organizations service collector."""

    def get_service_name(self) -> str:
        """Get service name."""
        return "organizations"

    def collect(self) -> Dict[str, Any]:
        """
        Collect Organizations resources for assessment.

        Returns:
            Dictionary containing Organizations data
        """
        logger.info("Collecting Organizations resources...")

        # Placeholder implementation
        # TODO: Implement actual Organizations resource collection
        return {
            "organization": {},
            "accounts": [],
            "organizational_units": [],
            "policies": [],
            "service_control_policies": [],
        }


class EC2Collector(BaseCollector):
    """EC2 compute service collector."""

    def get_service_name(self) -> str:
        """Get service name."""
        return "ec2"

    def collect(self) -> Dict[str, Any]:
        """
        Collect EC2 resources for assessment.

        Returns:
            Dictionary containing EC2 resource data
        """
        logger.info("Collecting EC2 resources...")

        # Placeholder implementation
        # TODO: Implement actual EC2 resource collection
        return {
            "instances": [],
            "images": [],
            "key_pairs": [],
            "security_groups": [],
            "volumes": [],
            "snapshots": [],
        }

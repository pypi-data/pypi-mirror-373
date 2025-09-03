"""
Networking Cost Engine - Core cost analysis and calculation logic
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import boto3
import numpy as np
from botocore.exceptions import ClientError

from .config import VPCNetworkingConfig, load_config

logger = logging.getLogger(__name__)


class NetworkingCostEngine:
    """
    Core engine for networking cost calculations and analysis
    """

    def __init__(self, session: Optional[boto3.Session] = None, config: Optional[VPCNetworkingConfig] = None):
        """
        Initialize the cost engine

        Args:
            session: Boto3 session for AWS API calls
            config: VPC networking configuration (uses default if None)
        """
        self.session = session or boto3.Session()
        self.config = config or load_config()
        self.cost_model = self.config.cost_model
        self._cost_explorer_client = None
        self._cloudwatch_client = None

    @property
    def cost_explorer(self):
        """Lazy load Cost Explorer client"""
        if not self._cost_explorer_client:
            self._cost_explorer_client = self.session.client("ce", region_name="us-east-1")
        return self._cost_explorer_client

    @property
    def cloudwatch(self):
        """Lazy load CloudWatch client"""
        if not self._cloudwatch_client:
            self._cloudwatch_client = self.session.client("cloudwatch")
        return self._cloudwatch_client

    def calculate_nat_gateway_cost(
        self, nat_gateway_id: str, days: int = 30, include_data_processing: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate NAT Gateway costs

        Args:
            nat_gateway_id: NAT Gateway ID
            days: Number of days to analyze
            include_data_processing: Include data processing charges

        Returns:
            Dictionary with cost breakdown
        """
        cost_breakdown = {
            "nat_gateway_id": nat_gateway_id,
            "period_days": days,
            "base_cost": 0.0,
            "data_processing_cost": 0.0,
            "total_cost": 0.0,
            "daily_average": 0.0,
            "monthly_projection": 0.0,
        }

        # Base cost calculation
        cost_breakdown["base_cost"] = self.cost_model.nat_gateway_hourly * 24 * days

        if include_data_processing:
            try:
                # Get data processing metrics from CloudWatch
                end_time = datetime.now()
                start_time = end_time - timedelta(days=days)

                response = self.cloudwatch.get_metric_statistics(
                    Namespace="AWS/NATGateway",
                    MetricName="BytesOutToDestination",
                    Dimensions=[{"Name": "NatGatewayId", "Value": nat_gateway_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400 * days,
                    Statistics=["Sum"],
                )

                if response["Datapoints"]:
                    total_bytes = sum([p["Sum"] for p in response["Datapoints"]])
                    total_gb = total_bytes / (1024**3)
                    cost_breakdown["data_processing_cost"] = total_gb * self.cost_model.nat_gateway_data_processing
            except Exception as e:
                logger.warning(f"Failed to get data processing metrics: {e}")

        # Calculate totals
        cost_breakdown["total_cost"] = cost_breakdown["base_cost"] + cost_breakdown["data_processing_cost"]
        cost_breakdown["daily_average"] = cost_breakdown["total_cost"] / days
        cost_breakdown["monthly_projection"] = cost_breakdown["daily_average"] * 30

        return cost_breakdown

    def calculate_vpc_endpoint_cost(
        self, endpoint_type: str, availability_zones: int = 1, data_processed_gb: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate VPC Endpoint costs

        Args:
            endpoint_type: 'Interface' or 'Gateway'
            availability_zones: Number of AZs for interface endpoints
            data_processed_gb: Data processed in GB

        Returns:
            Dictionary with cost breakdown
        """
        cost_breakdown = {
            "endpoint_type": endpoint_type,
            "availability_zones": availability_zones,
            "data_processed_gb": data_processed_gb,
            "base_cost": 0.0,
            "data_processing_cost": 0.0,
            "total_monthly_cost": 0.0,
        }

        if endpoint_type == "Interface":
            # Interface endpoints cost per AZ
            cost_breakdown["base_cost"] = self.cost_model.vpc_endpoint_interface_monthly * availability_zones
            cost_breakdown["data_processing_cost"] = data_processed_gb * self.cost_model.vpc_endpoint_data_processing
        else:
            # Gateway endpoints are free
            cost_breakdown["base_cost"] = 0.0
            cost_breakdown["data_processing_cost"] = 0.0

        cost_breakdown["total_monthly_cost"] = cost_breakdown["base_cost"] + cost_breakdown["data_processing_cost"]

        return cost_breakdown

    def calculate_transit_gateway_cost(
        self, attachments: int, data_processed_gb: float = 0, days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate Transit Gateway costs

        Args:
            attachments: Number of attachments
            data_processed_gb: Data processed in GB
            days: Number of days

        Returns:
            Dictionary with cost breakdown
        """
        cost_breakdown = {
            "attachments": attachments,
            "data_processed_gb": data_processed_gb,
            "base_cost": 0.0,
            "attachment_cost": 0.0,
            "data_processing_cost": 0.0,
            "total_cost": 0.0,
            "monthly_projection": 0.0,
        }

        # Base Transit Gateway cost
        cost_breakdown["base_cost"] = self.cost_model.transit_gateway_hourly * 24 * days

        # Attachment costs
        cost_breakdown["attachment_cost"] = self.cost_model.transit_gateway_attachment * 24 * days * attachments

        # Data processing costs
        cost_breakdown["data_processing_cost"] = data_processed_gb * self.cost_model.transit_gateway_data_processing

        # Calculate totals
        cost_breakdown["total_cost"] = (
            cost_breakdown["base_cost"] + cost_breakdown["attachment_cost"] + cost_breakdown["data_processing_cost"]
        )

        cost_breakdown["monthly_projection"] = cost_breakdown["total_cost"] / days * 30

        return cost_breakdown

    def calculate_elastic_ip_cost(self, idle_hours: int = 0, remaps: int = 0) -> Dict[str, Any]:
        """
        Calculate Elastic IP costs

        Args:
            idle_hours: Hours the EIP was idle
            remaps: Number of remaps

        Returns:
            Dictionary with cost breakdown
        """
        cost_breakdown = {
            "idle_hours": idle_hours,
            "remaps": remaps,
            "idle_cost": idle_hours * self.cost_model.elastic_ip_idle_hourly,
            "remap_cost": remaps * self.cost_model.elastic_ip_remap,
            "total_cost": 0.0,
            "monthly_projection": 0.0,
        }

        cost_breakdown["total_cost"] = cost_breakdown["idle_cost"] + cost_breakdown["remap_cost"]

        # Project to monthly (assuming same pattern)
        if idle_hours > 0:
            days_analyzed = idle_hours / 24
            cost_breakdown["monthly_projection"] = cost_breakdown["total_cost"] / days_analyzed * 30
        else:
            cost_breakdown["monthly_projection"] = cost_breakdown["total_cost"]

        return cost_breakdown

    def calculate_data_transfer_cost(
        self, inter_az_gb: float = 0, inter_region_gb: float = 0, internet_out_gb: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate data transfer costs

        Args:
            inter_az_gb: Inter-AZ transfer in GB
            inter_region_gb: Inter-region transfer in GB
            internet_out_gb: Internet outbound transfer in GB

        Returns:
            Dictionary with cost breakdown
        """
        cost_breakdown = {
            "inter_az_gb": inter_az_gb,
            "inter_region_gb": inter_region_gb,
            "internet_out_gb": internet_out_gb,
            "inter_az_cost": inter_az_gb * self.cost_model.data_transfer_inter_az,
            "inter_region_cost": inter_region_gb * self.cost_model.data_transfer_inter_region,
            "internet_out_cost": internet_out_gb * self.cost_model.data_transfer_internet_out,
            "total_cost": 0.0,
        }

        cost_breakdown["total_cost"] = (
            cost_breakdown["inter_az_cost"] + cost_breakdown["inter_region_cost"] + cost_breakdown["internet_out_cost"]
        )

        return cost_breakdown

    def get_actual_costs_from_cost_explorer(
        self, service: str, start_date: str, end_date: str, granularity: str = "MONTHLY"
    ) -> Dict[str, Any]:
        """
        Get actual costs from AWS Cost Explorer

        Args:
            service: AWS service name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            granularity: DAILY, MONTHLY, or HOURLY

        Returns:
            Dictionary with actual cost data
        """
        try:
            response = self.cost_explorer.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity=granularity,
                Metrics=["BlendedCost", "UnblendedCost"],
                Filter={"Dimensions": {"Key": "SERVICE", "Values": [service]}},
            )

            cost_data = {
                "service": service,
                "period": f"{start_date} to {end_date}",
                "granularity": granularity,
                "total_cost": 0.0,
                "results_by_time": [],
            }

            for result in response["ResultsByTime"]:
                period_cost = float(result["Total"]["BlendedCost"]["Amount"])
                cost_data["total_cost"] += period_cost
                cost_data["results_by_time"].append(
                    {
                        "start": result["TimePeriod"]["Start"],
                        "end": result["TimePeriod"]["End"],
                        "cost": period_cost,
                        "unit": result["Total"]["BlendedCost"]["Unit"],
                    }
                )

            return cost_data

        except Exception as e:
            logger.error(f"Failed to get costs from Cost Explorer: {e}")
            return {"service": service, "error": str(e), "total_cost": 0.0}

    def estimate_optimization_savings(
        self, current_costs: Dict[str, float], optimization_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Estimate savings from optimization scenarios

        Args:
            current_costs: Current cost breakdown by service
            optimization_scenarios: List of optimization scenarios

        Returns:
            Dictionary with savings estimates
        """
        total_current = sum(current_costs.values())

        savings_analysis = {
            "current_monthly_cost": total_current,
            "scenarios": [],
            "recommended_scenario": None,
            "maximum_savings": 0.0,
        }

        for scenario in optimization_scenarios:
            scenario_savings = 0.0
            optimized_costs = current_costs.copy()

            # Apply optimization percentages
            for service, reduction_pct in scenario.get("reductions", {}).items():
                if service in optimized_costs:
                    savings = optimized_costs[service] * (reduction_pct / 100)
                    scenario_savings += savings
                    optimized_costs[service] -= savings

            scenario_result = {
                "name": scenario.get("name", "Unnamed"),
                "description": scenario.get("description", ""),
                "monthly_savings": scenario_savings,
                "annual_savings": scenario_savings * 12,
                "new_monthly_cost": total_current - scenario_savings,
                "savings_percentage": (scenario_savings / total_current) * 100 if total_current > 0 else 0,
                "risk_level": scenario.get("risk_level", "medium"),
                "implementation_effort": scenario.get("effort", "medium"),
            }

            savings_analysis["scenarios"].append(scenario_result)

            if scenario_savings > savings_analysis["maximum_savings"]:
                savings_analysis["maximum_savings"] = scenario_savings
                savings_analysis["recommended_scenario"] = scenario_result

        return savings_analysis

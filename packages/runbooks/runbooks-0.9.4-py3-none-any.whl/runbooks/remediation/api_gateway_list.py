"""
API Gateway Inventory - List and analyze API Gateway configurations.
"""

import logging
import re

import click
from botocore.exceptions import ClientError

from .commons import (
    get_api_gateway_calls,
    get_api_gateways,
    get_client,
    get_lambda_invocations,
    get_log_group_from_lambda,
    get_method_details,
    get_resources,
    get_stages,
    write_to_csv,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option("--output-file", default="api_gateway_inventory.csv", help="Output CSV file path")
def list_api_gateways(output_file):
    """List all API Gateways and their configuration details."""
    logger.info("Collecting API Gateway inventory")

    try:
        # Create API Gateway and Lambda clients
        client_apigateway = get_client("apigateway")
        client_lambda = get_client("lambda")

        # Get all REST APIs
        rest_apis = get_api_gateways(client_apigateway)

        if not rest_apis:
            logger.info("No API Gateways found")
            return

        logger.info(f"Found {len(rest_apis)} API Gateways to analyze")

        data = []
        for rest_api in rest_apis:
            rest_api_id = rest_api["id"]
        # logger.info(f"API Gateway: {rest_api['name']} ({rest_api_id})")

        stages = get_stages(client_apigateway, rest_api_id)

        for stage in stages:
            stage_name = stage["stageName"]
            # logger.info(f"  Stage: {stage_name}")
            # Retrieve stage-level logging configuration
            log_group_arn = None
            if stage.get("accessLogSettings"):
                log_group_arn = stage["accessLogSettings"].get("destinationArn")

            resources = get_resources(client_apigateway, rest_api_id)

            for resource in resources:
                resource_id = resource["id"]

                integration_type = None
                uri = None
                integration_line = "    - No Integration Found"
                function_name = None
                log_group = None
                for http_method in [
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "OPTIONS",  # Add more as needed
                    "HEAD",
                    "PATCH",
                    "ANY",
                ]:
                    try:
                        response = client_apigateway.get_integration(
                            restApiId=rest_api_id, resourceId=resource_id, httpMethod=http_method
                        )

                        integration_type = response["type"]  # Possible values: HTTP, AWS, MOCK, AWS_PROXY

                        if integration_type == "AWS":
                            # Lambda integration
                            uri = response["uri"]
                            if uri.startswith("arn:aws:apigateway:"):
                                match = re.search(r"function:(\w+-\w+)", uri)
                                function_name = match.group(1) if match else None
                                integration_line = f"    - Lambda Integration: {function_name}"

                        elif integration_type == "HTTP" or integration_type == "AWS_PROXY":
                            # HTTP Endpoint or HTTP Proxy (could be S3, etc.)
                            uri = response["uri"]
                            match = re.search(r"function:(.+?)/", uri)
                            function_name = match.group(1) if match else None
                            integration_line = f"    - HTTP/Proxy Integration: {uri}"

                        elif integration_type == "MOCK":
                            integration_line = f"    - Mock Integration"

                    except client_apigateway.exceptions.NotFoundException:
                        pass

                    response = get_method_details(client_apigateway, rest_api_id, resource_id, http_method)

                    # Check caching status
                    if response and "methodResponses" in response and "200" in response["methodResponses"]:
                        caching_enabled = response["methodResponses"]["200"].get("cachingEnabled", False)
                        logger.info(f"API Gateway: {rest_api['name']} ({rest_api_id})")
                        logger.info(f"  Stage: {stage_name}")
                        logger.info(
                            f"    {http_method} Method (Resource: {resource['path']}) - Cache Enabled: {caching_enabled}"
                        )
                        logger.info(f"{integration_line}")
                        log_group_name = None
                        if log_group_arn:
                            log_group_name = log_group_arn.split(":")[-1]  # Extract from ARN
                            logger.info(f"    Access Log Group: {log_group_name}")

                        if function_name:
                            log_group = get_log_group_from_lambda(client_lambda, function_name)
                            if log_group:
                                logger.info(f"      Log Group: {log_group}")
                            else:
                                logger.info(f"      Log Group could not be determined from configuration.")

                        data.append(
                            {
                                "API Gateway": rest_api["name"],
                                "Rest API ID": rest_api_id,  # Added rest api id to the output
                                "Resource": resource["path"],  # Added resource path to the output
                                "Stage": stage_name,
                                "Method": http_method,
                                "Access Log Group": log_group_name,
                                "Cache Enabled": caching_enabled,
                                "Integration Type": integration_type,
                                "Integration details": integration_line.strip(),  # Added integration details to the output
                                "URI": uri,
                                "Function Name": function_name,
                                "Log Group of Function": log_group,
                                "API gateway (includes all http methods) calls in last 360 days": get_api_gateway_calls(
                                    rest_api["name"], 360
                                ),
                                "Lambda function invocations in last 360 days": get_lambda_invocations(
                                    function_name, 360
                                )
                                if function_name
                                else None,
                            }
                        )

        # Export results to CSV
        write_to_csv(data, output_file)
        logger.info(f"API Gateway inventory exported to: {output_file}")
        logger.info(f"Processed {len(data)} API Gateway configurations")

    except ClientError as e:
        logger.error(f"Failed to collect API Gateway inventory: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

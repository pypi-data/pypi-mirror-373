"""
Multi-Service Phrase Scanner - Search for sensitive data across AWS services.
"""

import json
import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client, write_to_csv

logger = logging.getLogger(__name__)


def scan_lambda_functions(phrase, case_sensitive=False):
    """Search Lambda function environment variables for the phrase."""
    try:
        lambda_client = get_client("lambda")
        paginator = lambda_client.get_paginator("list_functions")

        results = []
        function_count = 0

        for page in paginator.paginate():
            for function in page["Functions"]:
                function_count += 1
                function_name = function["FunctionName"]

                if "Environment" in function:
                    env_vars = function["Environment"].get("Variables", {})
                    for key, value in env_vars.items():
                        search_value = value if case_sensitive else value.lower()
                        search_phrase = phrase if case_sensitive else phrase.lower()

                        if search_phrase in search_value:
                            results.append(
                                {
                                    "service": "Lambda",
                                    "resource_type": "Function",
                                    "resource_name": function_name,
                                    "resource_arn": function["FunctionArn"],
                                    "location": f"Environment Variable: {key}",
                                    "match_context": f"{key}={value[:100]}..."
                                    if len(value) > 100
                                    else f"{key}={value}",
                                }
                            )

        logger.info(f"  Scanned {function_count} Lambda functions")
        return results

    except ClientError as e:
        logger.error(f"Failed to scan Lambda functions: {e}")
        return []


def scan_ecs_tasks(phrase, case_sensitive=False):
    """Search ECS task definitions for the phrase."""
    try:
        ecs_client = get_client("ecs")
        paginator = ecs_client.get_paginator("list_task_definitions")

        results = []
        task_def_count = 0

        for page in paginator.paginate():
            for task_def_arn in page["taskDefinitionArns"]:
                task_def_count += 1

                try:
                    task_def = ecs_client.describe_task_definition(taskDefinition=task_def_arn)["taskDefinition"]

                    for container_def in task_def["containerDefinitions"]:
                        container_name = container_def["name"]

                        if "environment" in container_def:
                            for env_var in container_def["environment"]:
                                var_name = env_var.get("name", "")
                                var_value = env_var.get("value", "")

                                search_value = var_value if case_sensitive else var_value.lower()
                                search_phrase = phrase if case_sensitive else phrase.lower()

                                if search_phrase in search_value:
                                    results.append(
                                        {
                                            "service": "ECS",
                                            "resource_type": "Task Definition",
                                            "resource_name": task_def_arn.split("/")[-1],
                                            "resource_arn": task_def_arn,
                                            "location": f"Container: {container_name}, Env Var: {var_name}",
                                            "match_context": f"{var_name}={var_value[:100]}..."
                                            if len(var_value) > 100
                                            else f"{var_name}={var_value}",
                                        }
                                    )

                except ClientError as e:
                    logger.debug(f"Could not describe task definition {task_def_arn}: {e}")
                    continue

        logger.info(f"  Scanned {task_def_count} ECS task definitions")
        return results

    except ClientError as e:
        logger.error(f"Failed to scan ECS task definitions: {e}")
        return []


def scan_ssm_parameters(phrase, case_sensitive=False):
    """Search SSM Parameter Store for the phrase."""
    try:
        ssm_client = get_client("ssm")
        paginator = ssm_client.get_paginator("describe_parameters")

        results = []
        param_count = 0
        access_denied_count = 0

        for page in paginator.paginate():
            for param in page["Parameters"]:
                param_count += 1
                param_name = param["Name"]

                try:
                    parameter = ssm_client.get_parameter(Name=param_name, WithDecryption=True)
                    param_value = parameter["Parameter"]["Value"]

                    search_value = param_value if case_sensitive else param_value.lower()
                    search_phrase = phrase if case_sensitive else phrase.lower()

                    if search_phrase in search_value:
                        results.append(
                            {
                                "service": "SSM Parameter Store",
                                "resource_type": "Parameter",
                                "resource_name": param_name,
                                "resource_arn": param.get("ARN", "N/A"),
                                "location": "Parameter Value",
                                "match_context": param_value[:100] + "..." if len(param_value) > 100 else param_value,
                            }
                        )

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code", "Unknown")
                    if error_code in ["ParameterNotFound", "AccessDenied"]:
                        access_denied_count += 1
                        logger.debug(f"Cannot access parameter {param_name}: {error_code}")
                    else:
                        logger.warning(f"Error accessing parameter {param_name}: {e}")

        logger.info(f"  Scanned {param_count} SSM parameters ({access_denied_count} access denied)")
        return results

    except ClientError as e:
        logger.error(f"Failed to scan SSM parameters: {e}")
        return []


def scan_secrets_manager(phrase, case_sensitive=False):
    """Search AWS Secrets Manager for the phrase."""
    try:
        secrets_client = get_client("secretsmanager")
        paginator = secrets_client.get_paginator("list_secrets")

        results = []
        secret_count = 0
        access_denied_count = 0

        for page in paginator.paginate():
            for secret in page["SecretList"]:
                secret_count += 1
                secret_name = secret["Name"]
                secret_arn = secret["ARN"]

                try:
                    secret_value = secrets_client.get_secret_value(SecretId=secret_arn)
                    secret_string = secret_value.get("SecretString", "")

                    if isinstance(secret_string, str):
                        # Try to parse as JSON first
                        try:
                            secret_data = json.loads(secret_string)
                            if isinstance(secret_data, dict):
                                # Search in JSON keys and values
                                for key, value in secret_data.items():
                                    search_value = str(value) if case_sensitive else str(value).lower()
                                    search_phrase = phrase if case_sensitive else phrase.lower()

                                    if search_phrase in search_value:
                                        results.append(
                                            {
                                                "service": "Secrets Manager",
                                                "resource_type": "Secret",
                                                "resource_name": secret_name,
                                                "resource_arn": secret_arn,
                                                "location": f"JSON Key: {key}",
                                                "match_context": f"{key}={str(value)[:100]}..."
                                                if len(str(value)) > 100
                                                else f"{key}={value}",
                                            }
                                        )
                            else:
                                # Not a JSON object, search the string directly
                                search_value = secret_string if case_sensitive else secret_string.lower()
                                search_phrase = phrase if case_sensitive else phrase.lower()

                                if search_phrase in search_value:
                                    results.append(
                                        {
                                            "service": "Secrets Manager",
                                            "resource_type": "Secret",
                                            "resource_name": secret_name,
                                            "resource_arn": secret_arn,
                                            "location": "Secret Value",
                                            "match_context": secret_string[:100] + "..."
                                            if len(secret_string) > 100
                                            else secret_string,
                                        }
                                    )
                        except json.JSONDecodeError:
                            # Not valid JSON, search as plain string
                            search_value = secret_string if case_sensitive else secret_string.lower()
                            search_phrase = phrase if case_sensitive else phrase.lower()

                            if search_phrase in search_value:
                                results.append(
                                    {
                                        "service": "Secrets Manager",
                                        "resource_type": "Secret",
                                        "resource_name": secret_name,
                                        "resource_arn": secret_arn,
                                        "location": "Secret Value",
                                        "match_context": secret_string[:100] + "..."
                                        if len(secret_string) > 100
                                        else secret_string,
                                    }
                                )

                except ClientError as e:
                    error_code = e.response.get("Error", {}).get("Code", "Unknown")
                    if error_code in ["ResourceNotFoundException", "AccessDeniedException"]:
                        access_denied_count += 1
                        logger.debug(f"Cannot access secret {secret_name}: {error_code}")
                    else:
                        logger.warning(f"Error accessing secret {secret_name}: {e}")

        logger.info(f"  Scanned {secret_count} secrets ({access_denied_count} access denied)")
        return results

    except ClientError as e:
        logger.error(f"Failed to scan Secrets Manager: {e}")
        return []


def scan_route53_records(phrase, case_sensitive=False):
    """Search Route 53 DNS records for the phrase."""
    try:
        route53_client = get_client("route53")

        results = []
        zone_count = 0
        record_count = 0

        # List all hosted zones
        hosted_zones = route53_client.list_hosted_zones()["HostedZones"]

        for zone in hosted_zones:
            zone_count += 1
            zone_id = zone["Id"]
            zone_name = zone["Name"]

            # List records in the hosted zone
            paginator = route53_client.get_paginator("list_resource_record_sets")
            for page in paginator.paginate(HostedZoneId=zone_id):
                for record in page["ResourceRecordSets"]:
                    record_count += 1
                    record_name = record["Name"]
                    record_type = record["Type"]

                    search_name = record_name if case_sensitive else record_name.lower()
                    search_phrase = phrase if case_sensitive else phrase.lower()

                    # Check if the phrase is in the record name
                    if search_phrase in search_name:
                        results.append(
                            {
                                "service": "Route 53",
                                "resource_type": "DNS Record",
                                "resource_name": record_name,
                                "resource_arn": f"arn:aws:route53:::hostedzone/{zone_id.split('/')[-1]}",
                                "location": f"Record Name in Zone: {zone_name}",
                                "match_context": f"Type: {record_type}, Name: {record_name}",
                            }
                        )

                    # Check record values for A and CNAME records
                    if record_type in ["A", "CNAME"] and "ResourceRecords" in record:
                        for value_record in record["ResourceRecords"]:
                            record_value = value_record["Value"]
                            search_value = record_value if case_sensitive else record_value.lower()

                            if search_phrase in search_value:
                                results.append(
                                    {
                                        "service": "Route 53",
                                        "resource_type": "DNS Record",
                                        "resource_name": record_name,
                                        "resource_arn": f"arn:aws:route53:::hostedzone/{zone_id.split('/')[-1]}",
                                        "location": f"Record Value in Zone: {zone_name}",
                                        "match_context": f"Type: {record_type}, Value: {record_value}",
                                    }
                                )

        logger.info(f"  Scanned {zone_count} hosted zones, {record_count} DNS records")
        return results

    except ClientError as e:
        logger.error(f"Failed to scan Route 53 records: {e}")
        return []


@click.command()
@click.option("--phrase", required=True, help="Phrase to search for in AWS resources")
@click.option("--case-sensitive", is_flag=True, help="Perform case-sensitive search")
@click.option("--services", default="lambda,ecs,ssm,secrets,route53", help="Comma-separated list of services to scan")
@click.option("--output-file", default="phrase_search_results.csv", help="Output CSV file path")
def search_aws_resources(phrase, case_sensitive, services, output_file):
    """Search for a phrase across multiple AWS services (Lambda, ECS, SSM, Secrets Manager, Route 53)."""
    logger.info(f"Multi-service phrase search in {display_aws_account_info()}")
    logger.info(f"Searching for: '{phrase}' (case-sensitive: {case_sensitive})")

    # Parse service list
    service_list = [s.strip().lower() for s in services.split(",")]
    service_scanners = {
        "lambda": scan_lambda_functions,
        "ecs": scan_ecs_tasks,
        "ssm": scan_ssm_parameters,
        "secrets": scan_secrets_manager,
        "route53": scan_route53_records,
    }

    # Validate services
    invalid_services = [s for s in service_list if s not in service_scanners]
    if invalid_services:
        logger.error(f"Invalid services: {invalid_services}")
        logger.info(f"Valid services: {list(service_scanners.keys())}")
        return

    logger.info(f"Scanning services: {', '.join(service_list)}")

    try:
        all_results = []

        # Scan each requested service
        for service in service_list:
            logger.info(f"🔍 Scanning {service.upper()}...")
            scanner = service_scanners[service]

            try:
                results = scanner(phrase, case_sensitive)
                all_results.extend(results)

                if results:
                    logger.info(f"  ✓ Found {len(results)} matches in {service}")
                else:
                    logger.info(f"  ○ No matches found in {service}")

            except Exception as e:
                logger.error(f"  ✗ Error scanning {service}: {e}")

        # Process and export results
        if all_results:
            logger.info(f"\n🎯 SEARCH RESULTS: Found {len(all_results)} total matches")

            # Group by service for summary
            service_counts = {}
            for result in all_results:
                service = result["service"]
                service_counts[service] = service_counts.get(service, 0) + 1

            logger.info("Matches per service:")
            for service, count in sorted(service_counts.items()):
                logger.info(f"  {service}: {count} matches")

            # Export to CSV
            csv_data = []
            for result in all_results:
                csv_data.append(
                    {
                        "Service": result["service"],
                        "ResourceType": result["resource_type"],
                        "ResourceName": result["resource_name"],
                        "ResourceARN": result["resource_arn"],
                        "Location": result["location"],
                        "MatchContext": result["match_context"],
                    }
                )

            write_to_csv(csv_data, output_file)
            logger.info(f"Search results exported to: {output_file}")

            # Show sample results
            logger.info("\nSample matches (first 5):")
            for i, result in enumerate(all_results[:5]):
                logger.info(f"  {i + 1}. {result['service']}: {result['resource_name']}")
                logger.info(f"     Location: {result['location']}")

        else:
            logger.info(f"❌ No matches found for phrase: '{phrase}'")

        # Summary
        logger.info("\n=== SEARCH SUMMARY ===")
        logger.info(f"Services scanned: {len(service_list)}")
        logger.info(f"Total matches found: {len(all_results)}")
        logger.info(f"Search phrase: '{phrase}' (case-sensitive: {case_sensitive})")

    except Exception as e:
        logger.error(f"Failed to search AWS resources: {e}")
        raise


if __name__ == "__main__":
    search_aws_resources()

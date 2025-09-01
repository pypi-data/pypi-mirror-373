"""
Lambda Function Inventory - Analyze and optimize Lambda function configurations.
"""

import copy
import json
import logging
import re

import click
from botocore.exceptions import ClientError

from .commons import (
    display_aws_account_info,
    get_client,
    get_lambda_invocations,
    get_lambda_total_duration,
    write_to_csv,
)

logger = logging.getLogger(__name__)

# Lambda pricing (adjust for your region)
PRICE_PER_GB_SECOND = 0.00001667  # US East (N. Virginia) - update for your region


def update_iam_role_with_inline_policies(role_name, new_policy_document):
    """Update IAM role inline policies with improved error handling."""
    try:
        client_iam = get_client("iam")

        for policy_name, policy in new_policy_document.items():
            policy_string = json.dumps(policy)

            try:
                client_iam.put_role_policy(RoleName=role_name, PolicyName=policy_name, PolicyDocument=policy_string)
                logger.info(f"✓ Updated policy '{policy_name}' for role '{role_name}'")

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")
                logger.error(f"✗ Failed to update policy '{policy_name}' for role '{role_name}': {error_code}")

    except Exception as e:
        logger.error(f"Failed to update IAM role policies: {e}")
        raise


def update_policy_document(policy_document):
    new_policy_document = copy.deepcopy(policy_document)
    changes = {}

    for policy_name, policy in new_policy_document.items():
        for statement in iterate_policy_statement(policy):
            # Check if 'Action' is '*'
            if statement["Action"] == "*" and statement["Resource"] != "*" and isinstance(statement["Resource"], str):
                match = re.search(r"arn:aws:(\w+):", statement["Resource"])
                if match and set(statement["Action"]) != {f"{match.group(1)}:*"}:
                    statement["Action"] = f"{match.group(1)}:*"
                    changes.setdefault(policy_name, []).append(statement["Action"])
            elif isinstance(statement["Resource"], list) and statement["Action"] == "*":
                statement["Action"] = []
                for resource in statement["Resource"]:
                    match = re.search(r"arn:aws:(\w+):", resource)
                    if match and set(statement["Action"]) != {f"{match.group(1)}:*"}:
                        statement["Action"].append(f"{match.group(1)}:*")
                        changes.setdefault(policy_name, []).append(statement["Action"])

            # Check if 'Resource' is '*'
            if statement["Resource"] == "*" and statement["Action"] != "*" and isinstance(statement["Action"], str):
                match = re.search(r"(\w+):", statement["Action"])
                if match and set(statement["Resource"]) != {f"arn:aws:{match.group(1)}:*:*:*"}:
                    statement["Resource"] = f"arn:aws:{match.group(1)}:*:*:*"
                    changes.setdefault(policy_name, []).append(statement["Resource"])
            elif isinstance(statement["Action"], list) and statement["Resource"] == "*":
                statement["Resource"] = []
                for action in statement["Action"]:
                    match = re.search(r"(\w+):", action)
                    if match and set(statement["Resource"]) != {f"arn:aws:{match.group(1)}:*:*:*"}:
                        statement["Resource"].append(f"arn:aws:{match.group(1)}:*:*:*")
                        changes.setdefault(policy_name, []).append(statement["Resource"])

    return changes, new_policy_document


def iterate_policy_statement(policy):
    if isinstance(policy["Statement"], list):
        for statement in policy["Statement"]:
            yield statement
    elif isinstance(policy["Statement"], dict):
        yield policy["Statement"]


def list_all_lambda_functions(client_lambda):
    """Generator that yields all Lambda functions with pagination."""
    try:
        paginator = client_lambda.get_paginator("list_functions")

        for page in paginator.paginate():
            for function in page["Functions"]:
                yield function

    except ClientError as e:
        logger.error(f"Failed to list Lambda functions: {e}")
        raise


@click.command()
@click.option(
    "--dry-run", is_flag=True, default=True, help="Preview mode - show analysis without making policy changes"
)
@click.option("--output-file", default="lambda_functions.csv", help="Output CSV file path")
@click.option("--days", default=360, help="Number of days to analyze for invocations")
def list_lambda_functions(dry_run: bool = True, output_file: str = "lambda_functions.csv", days: int = 360):
    """Analyze Lambda functions, costs, and IAM policies with optimization suggestions."""
    logger.info(f"Analyzing Lambda functions in {display_aws_account_info()}")

    try:
        # Initialize AWS clients
        client_lambda = get_client("lambda")
        client_cloudwatch = get_client("cloudwatch")
        client_iam = get_client("iam")

        # Get all Lambda functions
        all_functions = list(list_all_lambda_functions(client_lambda))

        if not all_functions:
            logger.info("No Lambda functions found")
            return

        logger.info(f"Found {len(all_functions)} Lambda functions to analyze")

        data = []
        policy_updates_count = 0

        # Analyze each function
        for i, function in enumerate(all_functions, 1):
            function_name = function["FunctionName"]
            logger.info(f"Analyzing function {i}/{len(all_functions)}: {function_name}")

            try:
                # Get function metrics
                invocations = get_lambda_invocations(function_name, days)
                total_duration = get_lambda_total_duration(client_cloudwatch, function_name)
                memory_size_gb = function["MemorySize"] / 1024  # Convert to GB
                role_arn = function["Role"]
                role_name = role_arn.split("/")[-1]

                warnings = []

                # Get IAM role policies
                try:
                    attached_response = client_iam.list_attached_role_policies(RoleName=role_name)
                    attached_policies = attached_response.get("AttachedPolicies", [])
                except ClientError as e:
                    if e.response.get("Error", {}).get("Code") == "NoSuchEntity":
                        message = f"Role {role_name} does not exist for function {function_name}"
                        logger.warning(message)
                        warnings.append(message)
                        attached_policies = []
                    else:
                        raise

                try:
                    inline_response = client_iam.list_role_policies(RoleName=role_name)
                    inline_policies = inline_response.get("PolicyNames", [])
                except ClientError as e:
                    if e.response.get("Error", {}).get("Code") == "NoSuchEntity":
                        inline_policies = []
                    else:
                        raise

                # Get inline policy documents
                inline_policy_documents = {}
                for policy_name in inline_policies:
                    try:
                        policy_response = client_iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                        inline_policy_documents[policy_name] = policy_response["PolicyDocument"]
                    except ClientError as e:
                        logger.warning(f"Could not get policy '{policy_name}' for role '{role_name}': {e}")

                # Analyze and potentially update policies
                changes, new_policy_document = update_policy_document(inline_policy_documents)

                if changes:
                    logger.info(f"  → Policy optimization recommendations found for {role_name}")
                    if not dry_run:
                        logger.info(f"  → Updating policies for role: {role_name}")
                        update_iam_role_with_inline_policies(role_name, new_policy_document)
                        policy_updates_count += 1
                    else:
                        logger.info(f"  → DRY-RUN: Would update policies for role: {role_name}")

                # Calculate cost estimate
                gb_seconds = (total_duration / 1000) * memory_size_gb
                cost_estimate = gb_seconds * PRICE_PER_GB_SECOND

                # Collect function data
                function_data = {
                    "FunctionName": function_name,
                    "Runtime": function.get("Runtime", ""),
                    "MemorySize": function.get("MemorySize", 0),
                    "Timeout": function.get("Timeout", 0),
                    "LastModified": function.get("LastModified", ""),
                    "Description": function.get("Description", ""),
                    "Version": function.get("Version", ""),
                    f"Total Invocations in {days} days": invocations,
                    "Total Duration 30 days (seconds)": total_duration / 1000,
                    "Estimated Cost (30 days)": round(cost_estimate, 4),
                    "IAM Role": role_name,
                    "Attached Policies Count": len(attached_policies),
                    "Inline Policies Count": len(inline_policies),
                    "Policy Optimization": "Changes available" if changes else "No changes needed",
                    "Warnings": "; ".join(warnings) if warnings else "None",
                }

                data.append(function_data)

            except Exception as e:
                logger.error(f"  ✗ Failed to analyze function {function_name}: {e}")
                # Add minimal data for failed analysis
                data.append({"FunctionName": function_name, "Error": str(e), "Status": "Analysis Failed"})

        # Export results
        write_to_csv(data, output_file)
        logger.info(f"Lambda analysis exported to: {output_file}")

        # Summary
        logger.info("\n=== ANALYSIS SUMMARY ===")
        logger.info(f"Functions analyzed: {len(all_functions)}")
        logger.info(
            f"Functions with policy optimizations: {sum(1 for d in data if d.get('Policy Optimization') == 'Changes available')}"
        )

        if dry_run and policy_updates_count == 0:
            policy_candidates = sum(1 for d in data if d.get("Policy Optimization") == "Changes available")
            if policy_candidates > 0:
                logger.info(f"To apply {policy_candidates} policy optimizations, run with --no-dry-run")
        elif not dry_run:
            logger.info(f"Applied policy updates to {policy_updates_count} roles")

    except Exception as e:
        logger.error(f"Failed to analyze Lambda functions: {e}")
        raise

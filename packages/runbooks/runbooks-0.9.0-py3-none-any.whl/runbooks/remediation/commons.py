import configparser
import csv
import json
import logging
import os
import time
import webbrowser
from datetime import datetime, timedelta
from functools import lru_cache as LRU_cache

import boto3
import botocore.exceptions
import botocore.session
from botocore.exceptions import ClientError

from runbooks.common.rich_utils import console, print_error, print_info, print_warning

logger = logging.getLogger(__name__)


def get_all_available_aws_credentials(start_url: str = None, role_name="power-user") -> dict:
    if not start_url:
        raise ValueError("Start URL for AWS SSO is required")

    credentials = {}

    # Create an SSO OIDC client
    sso_oidc = boto3.client("sso-oidc", region_name="ap-southeast-2")

    try:
        # Register client
        client_creds = sso_oidc.register_client(
            clientName="MyApp",
            clientType="public",
        )

        # Get device authorization
        device_auth = sso_oidc.start_device_authorization(
            clientId=client_creds["clientId"], clientSecret=client_creds["clientSecret"], startUrl=start_url
        )

        console.print(
            f"[cyan]Please go to {device_auth['verificationUriComplete']} and enter the code: [bold]{device_auth['userCode']}[/bold][/cyan]"
        )
        webbrowser.open(device_auth["verificationUriComplete"])

        # Wait for user to authorize
        token = None
        max_retries = 60  # Maximum number of retries (5 minutes with 5-second intervals)
        retry_count = 0

        while not token and retry_count < max_retries:
            try:
                token = sso_oidc.create_token(
                    clientId=client_creds["clientId"],
                    clientSecret=client_creds["clientSecret"],
                    grantType="urn:ietf:params:oauth:grant-type:device_code",
                    deviceCode=device_auth["deviceCode"],
                )
            except sso_oidc.exceptions.AuthorizationPendingException:
                print_info("Waiting for authorization... Please complete the process in your browser.")
                time.sleep(5)  # Wait for 5 seconds before trying again
                retry_count += 1
            except Exception as e:
                print_error(f"An error occurred: {e}")
                break

        if not token:
            print_error("Authorization timed out or failed. Please try again.")
            return credentials

        # Create SSO client
        sso = boto3.client("sso", region_name="ap-southeast-2")

        # List accounts (with pagination)
        all_accounts = []
        paginator = sso.get_paginator("list_accounts")
        for page in paginator.paginate(accessToken=token["accessToken"]):
            all_accounts.extend(page["accountList"])

        for account in all_accounts:
            # Get role names for each account
            roles = []
            role_paginator = sso.get_paginator("list_account_roles")
            for role_page in role_paginator.paginate(accessToken=token["accessToken"], accountId=account["accountId"]):
                roles.extend(role_page["roleList"])

            for role in roles:
                # Get temporary credentials for each role
                if role["roleName"] == role_name:
                    creds = sso.get_role_credentials(
                        accessToken=token["accessToken"], accountId=account["accountId"], roleName=role["roleName"]
                    )

                    credentials[f"{account['accountId']}_{role['roleName']}"] = {
                        "aws_access_key_id": creds["roleCredentials"]["accessKeyId"],
                        "aws_secret_access_key": creds["roleCredentials"]["secretAccessKey"],
                        "aws_session_token": creds["roleCredentials"]["sessionToken"],
                    }

    except ClientError as e:
        logger.error(f"An error occurred: {e}")

    return credentials


def read_all_aws_credentials(file_path: str = "credentials") -> dict:
    config = configparser.ConfigParser()
    config.read(file_path)  # replace with your file path if not in the same directory

    credentials = {}
    for profile_name in config.sections():
        aws_access_key_id = config.get(profile_name, "aws_access_key_id")
        aws_secret_access_key = config.get(profile_name, "aws_secret_access_key")
        aws_session_token = config.get(profile_name, "aws_session_token")

        credentials[profile_name] = {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "aws_session_token": aws_session_token,
        }

    return credentials


def get_api_gateways(client):
    response = client.get_rest_apis()
    return response["items"]


def get_stages(client, rest_api_id):
    response = client.get_stages(restApiId=rest_api_id)
    return response["item"]


@LRU_cache(maxsize=32)
def get_resources(client, rest_api_id):
    response = client.get_resources(restApiId=rest_api_id)
    return response["items"]


def get_method_details(client, rest_api_id, resource_id, http_method):
    try:
        response = client.get_method(restApiId=rest_api_id, resourceId=resource_id, httpMethod=http_method)
        return response
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NotFoundException":
            # logging.info(f"Method {http_method} not found for resource {resource_id} in API {rest_api_id}")
            return None
        else:
            raise


def get_client(client_name: str):
    return boto3.client(
        client_name,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
        region_name=os.environ.get("AWS_REGION"),  # or your preferred region
    )


def get_resource(client_name: str):
    return boto3.resource(
        client_name,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
        region_name=os.environ.get("AWS_REGION"),  # or your preferred region
    )


def get_log_groups(client, log_group_name_prefix):
    response = client.describe_log_groups(logGroupNamePrefix=log_group_name_prefix)
    return response["logGroups"]


def write_to_csv(data, filename):
    """Write data to a CSV file.

    Args:
    data (list of dict): The data to write. Each dict is a row in the CSV.
    filename (str): The name of the CSV file.
    """
    with open(filename, "w", newline="") as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)


@LRU_cache(maxsize=32)
def get_log_group_from_lambda(client_lambda, function_name):
    try:
        response = client_lambda.get_function_configuration(FunctionName=function_name)

        if "LoggingConfig" in response:
            return response["LoggingConfig"]["LogGroup"]

        else:
            return None  # Lambda logging might not be configured

    except client_lambda.exceptions.ResourceNotFoundException:
        message = f"Lambda function '{function_name}' not found."
        logger.info(message)
        return message


@LRU_cache(maxsize=32)
def get_lambda_config(client_lambda, function_name):
    try:
        response = client_lambda.get_function_configuration(FunctionName=function_name)

        return response

    except client_lambda.exceptions.ResourceNotFoundException:
        message = f"Lambda function '{function_name}' not found."
        logger.info(message)
        return message


@LRU_cache(maxsize=32)
def get_lambda_invocations(function_name, days=30):
    client_cloudwatch = get_client("cloudwatch")
    # Define the time period
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    # Get the metric statistics
    response = client_cloudwatch.get_metric_statistics(
        Namespace="AWS/Lambda",
        MetricName="Invocations",
        Dimensions=[
            {"Name": "FunctionName", "Value": function_name},
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600 * 24,  # One day periods
        Statistics=[
            "Sum",  # Get the total (sum) of the invocations
        ],
    )

    # Calculate the total invocations over the time period
    total_invocations = sum(datapoint["Sum"] for datapoint in response["Datapoints"])

    return total_invocations


@LRU_cache(maxsize=32)
def get_api_gateway_calls(api_name, days=30):
    # Create a CloudWatch client
    client = get_client("cloudwatch")

    # Define the time period
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    # Get the metric statistics
    response = client.get_metric_statistics(
        Namespace="AWS/ApiGateway",
        MetricName="Count",
        Dimensions=[
            {"Name": "ApiName", "Value": api_name},
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600 * 24,  # One day periods
        Statistics=[
            "Sum",  # Get the total (sum) of the API calls
        ],
    )

    # Calculate the total API calls over the time period
    total_calls = sum(datapoint["Sum"] for datapoint in response["Datapoints"])

    return total_calls


def get_lambda_total_duration(client_cloudwatch, function_name, days=30):
    # Define the time period
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    # Get the metric statistics for Duration
    response_duration = client_cloudwatch.get_metric_statistics(
        Namespace="AWS/Lambda",
        MetricName="Duration",
        Dimensions=[
            {"Name": "FunctionName", "Value": function_name},
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,  # One hour periods
        Statistics=[
            "Sum",  # Get the total duration
        ],
    )

    # Calculate the total duration over the time period
    total_duration = (
        sum(datapoint["Sum"] for datapoint in response_duration["Datapoints"]) if response_duration["Datapoints"] else 0
    )

    return total_duration


def get_price(service_code, region_name, instance_type):
    """Get the on-demand price for an instance type in a region"""
    response = get_product_pricing(instance_type, region_name, service_code)

    for product in response["PriceList"]:
        product_obj = json.loads(product)
        product_terms = product_obj["terms"]

        for term in product_terms["OnDemand"]:
            price_dimensions = product_terms["OnDemand"][term]["priceDimensions"]

            for dimension in price_dimensions:
                price_info = price_dimensions[dimension]
                price = float(price_info["pricePerUnit"]["USD"])
                currency = list(price_info["pricePerUnit"].keys())[0]  # Get the currency
                if not price:
                    continue
                return price, currency

    return None


@LRU_cache(maxsize=32)
def get_product_pricing(instance_type, region_name, service_code):
    # Pricing API available only in selected regions
    pricing = botocore.session.get_session().create_client("pricing", region_name="us-east-1")
    response = pricing.get_products(
        ServiceCode=service_code,
        Filters=[
            {"Type": "TERM_MATCH", "Field": "location", "Value": region_name},
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {"Type": "TERM_MATCH", "Field": "termType", "Value": "OnDemand"},
        ],
        MaxResults=100,
    )
    return response


def get_role_permissions(role_name):
    # Create a client for IAM
    iam_client = get_client("iam")

    # Get the policies attached to the role
    response = iam_client.list_attached_role_policies(RoleName=role_name)

    # The policies are in the 'AttachedPolicies' field of the response
    attached_policies = response["AttachedPolicies"]

    response = iam_client.list_role_policies(RoleName=role_name)

    inline_policies = response["PolicyNames"]

    inline_policy_documents = {}
    for policy_name in inline_policies:
        policy_document = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)["PolicyDocument"]
        inline_policy_documents[policy_name] = policy_document

    return attached_policies, inline_policy_documents


def get_vpc_flow_logs():
    # Create a client for EC2
    ec2_client = get_client("ec2")

    # Get a list of flow logs
    response = ec2_client.describe_flow_logs()

    # The flow logs are in the 'FlowLogs' field of the response
    flow_logs = response["FlowLogs"]

    # Create a dictionary to store the flow logs for each VPC
    vpc_flow_logs = {}

    # Iterate over the flow logs
    for flow_log in flow_logs:
        # Get the ID of the VPC that the flow log is attached to
        vpc_id = flow_log["ResourceId"]

        # If the VPC ID is not already in the dictionary, add it
        if vpc_id not in vpc_flow_logs:
            vpc_flow_logs[vpc_id] = []

        # Add the flow log to the list for this VPC
        vpc_flow_logs[vpc_id].append(flow_log)

    return vpc_flow_logs


def get_ec2_instances_by_security_groups(security_group_ids):
    ec2 = get_resource("ec2")  # Use resource instead of client

    # Filter instances based on security groups
    instances = ec2.instances.filter(Filters=[{"Name": "instance.group-id", "Values": security_group_ids}])

    instance_info = []
    for instance in instances:
        instance_info.append({"InstanceId": instance.id, "State": instance.state["Name"], "Tags": instance.tags})

    return instance_info


@LRU_cache(maxsize=32)
def get_bucket_policy(bucket_name) -> tuple:
    s3 = get_client("s3")
    try:
        result = s3.get_bucket_policy(Bucket=bucket_name)
        policy = json.loads(result["Policy"])
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucketPolicy":
            policy = "No policy"
        else:
            policy = e.response["Error"]["Message"]

    try:
        public_access_block = s3.get_public_access_block(Bucket=bucket_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
            public_access_block = "No public access block configuration"
        else:
            public_access_block = e.response["Error"]["Message"]
    else:
        if isinstance(public_access_block, dict):
            public_access_block = public_access_block.get("PublicAccessBlockConfiguration", {})

    return policy, public_access_block


def display_aws_account_info():
    sts = get_client("sts")

    # Get caller identity
    identity = sts.get_caller_identity()

    # Get account id
    account_id = identity["Account"]

    # Get IAM user or role name
    user_or_role_name = identity["Arn"].split("/")[-2]

    return {"AWS Account ID": account_id, "AWS User or Role Name": user_or_role_name}


def list_tables():
    """Lists all DynamoDB tables in the account."""
    dynamodb = get_client("dynamodb")
    paginator = dynamodb.get_paginator("list_tables")
    for page in paginator.paginate():
        yield from page["TableNames"]

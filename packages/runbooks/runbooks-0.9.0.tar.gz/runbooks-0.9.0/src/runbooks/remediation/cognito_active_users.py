"""
Cognito User Analysis - List active users in Cognito User Pools.
"""

import logging

import click
from botocore.exceptions import ClientError

from .commons import get_client, write_to_csv

logger = logging.getLogger(__name__)


@click.command()
@click.option("--user-pool-id", prompt="User Pool ID", help="The ID of the Cognito User Pool")
@click.option("--output-file", default="cognito_active_users.csv", help="Output CSV file path")
def get_active_users_in_cognito_pool(user_pool_id, output_file):
    """Get active users in a Cognito User Pool and export to CSV."""
    logger.info(f"Getting active users from Cognito User Pool: {user_pool_id}")

    try:
        client_cognito = get_client("cognito-idp")

        # Get active users (enabled status)
        response = client_cognito.list_users(UserPoolId=user_pool_id, Filter='status="Enabled"')

        users = response.get("Users", [])

        if not users:
            logger.info("No active users found in the user pool")
            return

        logger.info(f"Found {len(users)} active users")

        # Process user data
        user_data = []
        for user in users:
            user_info = {
                "username": user.get("Username", ""),
                "status": user.get("UserStatus", ""),
                "created_at": user["UserCreateDate"].isoformat() if "UserCreateDate" in user else "",
                "last_modified_at": user["UserLastModifiedDate"].isoformat() if "UserLastModifiedDate" in user else "",
                "enabled": user.get("Enabled", False),
                "email_verified": False,
                "phone_verified": False,
            }

            # Extract email and phone verification status from attributes
            for attr in user.get("Attributes", []):
                if attr.get("Name") == "email_verified":
                    user_info["email_verified"] = attr.get("Value") == "true"
                elif attr.get("Name") == "phone_number_verified":
                    user_info["phone_verified"] = attr.get("Value") == "true"

            user_data.append(user_info)
            logger.debug(f"Processed user: {user_info['username']}")

        # Export to CSV
        write_to_csv(user_data, output_file)
        logger.info(f"User data exported to: {output_file}")

        # Summary
        enabled_count = sum(1 for u in user_data if u["enabled"])
        email_verified_count = sum(1 for u in user_data if u["email_verified"])

        logger.info(f"Summary: {enabled_count} enabled users, {email_verified_count} with verified emails")

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "ResourceNotFoundException":
            logger.error(f"User pool not found: {user_pool_id}")
        else:
            logger.error(f"Failed to get Cognito users: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

"""
🚨 HIGH-RISK: Cognito Password Reset - Handle user authentication with extreme care.
"""

import logging

import click
from botocore.exceptions import ClientError

from .commons import display_aws_account_info, get_client

logger = logging.getLogger(__name__)


@click.command()
@click.option("--user-pool-id", help="Cognito User Pool ID (interactive mode if not provided)")
@click.option("--username", help="Username to reset (interactive mode if not provided)")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompts (dangerous!)")
def reset_password(user_pool_id, username, confirm):
    """🚨 HIGH-RISK: Reset user password in Cognito User Pool with safety checks."""

    # HIGH-RISK OPERATION WARNING
    if not confirm:
        logger.warning("🚨 HIGH-RISK OPERATION: User password reset")
        logger.warning("This operation will reset user authentication credentials")
        if not click.confirm("Do you want to continue?"):
            logger.info("Operation cancelled by user")
            return

    logger.info(f"🔐 Cognito password reset in {display_aws_account_info()}")

    try:
        client = get_client("cognito-idp")

        # Get User Pool ID if not provided
        if not user_pool_id:
            logger.info("Listing available User Pools...")
            response = client.list_user_pools(MaxResults=60)
            user_pools = response.get("UserPools", [])

            if not user_pools:
                logger.error("No User Pools found")
                return

            logger.info("\n📋 Available User Pools:")
            for i, pool in enumerate(user_pools, 1):
                logger.info(f"  {i}. {pool['Name']} (ID: {pool['Id']})")

            user_pool_id = click.prompt("\nPlease enter the User Pool ID", type=str)

        # Validate User Pool exists
        try:
            client.describe_user_pool(UserPoolId=user_pool_id)
            logger.info(f"✓ User Pool {user_pool_id} found")
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ResourceNotFoundException":
                logger.error(f"❌ User Pool not found: {user_pool_id}")
                return
            raise

        # Get username if not provided
        if not username:
            logger.info("Listing users in the pool...")
            try:
                response = client.list_users(UserPoolId=user_pool_id, Limit=50)
                users = response.get("Users", [])

                if not users:
                    logger.error("No users found in the User Pool")
                    return

                logger.info("\n👥 Available Users:")
                for i, user in enumerate(users, 1):
                    status = user.get("UserStatus", "Unknown")
                    enabled = user.get("Enabled", False)
                    logger.info(f"  {i}. {user['Username']} (Status: {status}, Enabled: {enabled})")

                username = click.prompt("\nPlease enter the username", type=str)

            except ClientError as e:
                logger.error(f"Failed to list users: {e}")
                return

        # Validate user exists and get details
        try:
            user_info = client.admin_get_user(UserPoolId=user_pool_id, Username=username)
            user_status = user_info.get("UserStatus", "Unknown")
            user_enabled = user_info.get("Enabled", False)

            logger.info(f"\n📝 User Details:")
            logger.info(f"  Username: {username}")
            logger.info(f"  Status: {user_status}")
            logger.info(f"  Enabled: {user_enabled}")

        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "UserNotFoundException":
                logger.error(f"❌ User not found: {username}")
                return
            raise

        # Get new password and settings
        password = click.prompt("Please enter the new password", type=str, hide_input=True, confirmation_prompt=True)
        permanent = click.prompt("Set the password as permanent? (default: temporary)", type=bool, default=False)

        # FINAL CONFIRMATION for high-risk operation
        if not confirm:
            logger.warning(f"\n🚨 FINAL CONFIRMATION:")
            logger.warning(f"  User Pool: {user_pool_id}")
            logger.warning(f"  Username: {username}")
            logger.warning(f"  Permanent: {permanent}")
            if not click.confirm("Proceed with password reset?"):
                logger.info("Operation cancelled")
                return

        # Perform password reset
        logger.info(f"🔄 Resetting password for user: {username}")
        try:
            response = client.admin_set_user_password(
                UserPoolId=user_pool_id, Username=username, Password=password, Permanent=permanent
            )
            logger.info(f"✅ Password reset successful for user: {username}")

            # Log the operation for audit trail
            logger.info(f"🔍 Audit: Password reset completed")
            logger.info(f"  User Pool: {user_pool_id}")
            logger.info(f"  Username: {username}")
            logger.info(f"  Permanent: {permanent}")

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "UserNotFoundException":
                logger.error(f"❌ User not found: {username}")
            elif error_code == "InvalidPasswordException":
                logger.error("❌ Invalid password - check User Pool password policy")
            elif error_code == "NotAuthorizedException":
                logger.error("❌ Not authorized - check IAM permissions")
            else:
                logger.error(f"❌ Failed to reset password: {e}")
            return

        # Optional: Add user to ReadHistorical group (if needed)
        group_name = "ReadHistorical"
        if click.confirm(f"Add user to group '{group_name}'?", default=False):
            try:
                # Check if user is already in the group
                response = client.admin_list_groups_for_user(UserPoolId=user_pool_id, Username=username)
                existing_groups = [group["GroupName"] for group in response.get("Groups", [])]

                if group_name in existing_groups:
                    logger.info(f"ℹ User already in group: {group_name}")
                else:
                    client.admin_add_user_to_group(UserPoolId=user_pool_id, Username=username, GroupName=group_name)
                    logger.info(f"✅ User added to group: {group_name}")

            except ClientError as e:
                logger.error(f"❌ Failed to add user to group: {e}")

    except ClientError as e:
        logger.error(f"❌ Cognito operation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise

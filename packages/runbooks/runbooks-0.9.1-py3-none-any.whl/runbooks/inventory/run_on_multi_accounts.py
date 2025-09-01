#!/usr/bin/env python3

import logging
import sys

import Inventory_Modules
from account_class import aws_acct_access
from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from rich.console import Console
from rich.panel import Panel

# Initialize Rich console
console = Console()

init()
__version__ = "2023.05.04"

parser = CommonArguments()
parser.singleprofile()
parser.verbosity()  # Allows for the verbosity to be handled.
parser.version(__version__)
parser.my_parser.add_argument(
    "-f",
    "--file",
    dest="pAccountFile",
    metavar="Account File",
    required=True,
    default=None,
    help="List of account numbers, one per line.",
)
parser.my_parser.add_argument(
    "--Role",
    dest="pAccessRole",
    metavar="Access Role",
    default="Admin",
    help="Role used to gain access to the list of accounts.",
)
args = parser.my_parser.parse_args()

pProfile = args.Profile
pAccountFile = args.pAccountFile
pAccessRole = args.pAccessRole
verbose = args.loglevel
logging.basicConfig(level=args.loglevel, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

aws_acct = aws_acct_access(pProfile)

#####################


def check_account_access(faws_acct, faccount_num, fAccessRole=None):
    if fAccessRole is None:
        logging.error(f"Role must be provided")
        return_response = {"Success": False, "ErrorMessage": "Role wasn't provided"}
        return return_response
    sts_client = faws_acct.session.client("sts")
    try:
        role_arn = f"arn:aws:iam::{faccount_num}:role/{fAccessRole}"
        credentials = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="TheOtherGuy")["Credentials"]
        return_response = {"Credentials": credentials, "Success": True, "ErrorMessage": ""}
        return return_response
    except ClientError as my_Error:
        console.print(f"[red]❌ Client Error: {my_Error}[/red]")
        return_response = {"Success": False, "ErrorMessage": "Client Error"}
        return return_response
    except sts_client.exceptions.MalformedPolicyDocumentException as my_Error:
        console.print(f"[red]❌ MalformedPolicy: {my_Error}[/red]")
        return_response = {"Success": False, "ErrorMessage": "Malformed Policy"}
        return return_response
    except sts_client.exceptions.PackedPolicyTooLargeException as my_Error:
        console.print(f"[red]❌ Policy is too large: {my_Error}[/red]")
        return_response = {"Success": False, "ErrorMessage": "Policy is too large"}
        return return_response
    except sts_client.exceptions.RegionDisabledException as my_Error:
        console.print(f"[red]❌ Region is disabled: {my_Error}[/red]")
        return_response = {"Success": False, "ErrorMessage": "Region Disabled"}
        return return_response
    except sts_client.exceptions.ExpiredTokenException as my_Error:
        console.print(f"[red]❌ Expired Token: {my_Error}[/red]")
        return_response = {"Success": False, "ErrorMessage": "Expired Token"}
        return return_response


def participant_user(faws_acct, create=None, username=None):
    from randominfo import random_password

    if create is None:
        create = True
    if username is None:
        username = "reinvent_admin"
    password = random_password()
    client_iam = faws_acct.session.client("iam")
    return_response = {
        "Success": False,
        "ErrorMessage": None,
        "AccountId": None,
        "User": None,
        "Password": None,
        "AccessKeyId": None,
        "SecretAccessKey": None,
    }
    if create:
        try:
            user_response = client_iam.create_user(UserName=username)["User"]
            return_response = {"Success": True, "AccountId": faws_acct.acct_number, "User": username, "Password": None}

        except client_iam.exceptions.EntityAlreadyExistsException as my_Error:
            logging.error(f"User {username} already exists... moving on")
        try:
            # user_response = client_iam.create_user(UserName=username)['User']
            password_response = client_iam.create_login_profile(
                UserName=username, Password=password, PasswordResetRequired=False
            )
            return_response = {
                "Success": True,
                "AccountId": faws_acct.acct_number,
                "User": username,
                "Password": password,
            }
        except client_iam.exceptions.EntityAlreadyExistsException as my_Error:
            logging.error("User login profile already exists, so we'll update it instead")
            try:
                password_response = client_iam.update_login_profile(
                    UserName=username, Password=password, PasswordResetRequired=False
                )
                return_response = {
                    "Success": True,
                    "AccountId": faws_acct.acct_number,
                    "User": username,
                    "Password": password,
                }
            except ClientError as my_Error:
                ErrorMessage = f"Client Error: {my_Error}"
                logging.error(f"ErrorMessage: {ErrorMessage}")
                return_response = {"Success": False, "ErrorMessage": ErrorMessage}
        except ClientError as my_Error:
            ErrorMessage = f"Client Error: {my_Error}"
            logging.error(f"ErrorMessage: {ErrorMessage}")
            return_response = {"Success": False, "ErrorMessage": ErrorMessage}
        try:
            access_keys = client_iam.create_access_key(UserName=username)["AccessKey"]
            return_response["AccessKeyId"] = access_keys["AccessKeyId"]
            return_response["SecretAccessKey"] = access_keys["SecretAccessKey"]
        except (
            ClientError,
            client_iam.exceptions.NoSuchEntityException,
            client_iam.exceptions.LimitExceededException,
            client_iam.exceptions.ServiceFailureException,
        ) as my_Error:
            ErrorMessage = f"Client Error: {my_Error}"
            logging.error(f"ErrorMessage: {ErrorMessage}")
            return_response["Success"] = False
            return_response["ErrorMessage"] = ErrorMessage
        try:
            attached_policy = client_iam.attach_user_policy(
                UserName=username, PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess"
            )
            return_response["Success"] = True
        except (
            client_iam.exceptions.EntityTemporarilyUnmodifiableException,
            client_iam.exceptions.NoSuchEntityException,
            client_iam.exceptions.PasswordPolicyViolationException,
            client_iam.exceptions.PasswordPolicyViolationException,
            client_iam.exceptions.LimitExceededException,
            client_iam.exceptions.ServiceFailureException,
        ) as my_Error:
            ErrorMessage = f"Specific Error: {my_Error}"
            logging.error(f"ErrorMessage: {ErrorMessage}")
            return_response["Success"] = False
            return_response["ErrorMessage"] = ErrorMessage
    return return_response


#####################


if pAccountFile is None:
    logging.critical(f"file of accounts was not provided. This is required. Exiting.")
    sys.exit(1)

Accounts = []
with open(pAccountFile, "r") as infile:
    for line in infile:
        Accounts.append(line.rstrip("\r\n,"))
infile.close()

for account_num in Accounts:
    logging.info(
        f"Accessing account #{account_num} as {pAccessRole} using account's {aws_acct.acct_number}'s credentials"
    )
    response = check_account_access(aws_acct, account_num, pAccessRole)
    if response["Success"]:
        console.print(
            f"[green]✅ Account {account_num} was successfully connected via role {pAccessRole} from {aws_acct.acct_number}[/green]"
        )
        """
		Put more commands here... Or you can write functions that represent your commands and call them from here.
		"""
        credentials = Inventory_Modules.get_child_access3(aws_acct, account_num, "us-east-1", ["reinvent-Admin"])
        tgt_aws_access = aws_acct_access(ocredentials=credentials)
        username = "Paul"
        user_response = participant_user(tgt_aws_access, username=username)
    else:
        console.print(
            Panel(
                f"Access Role {pAccessRole} failed to connect to {account_num} from {aws_acct.acct_number}",
                title=f"[red]❌ Connection Error: {response['ErrorMessage']}[/red]",
                border_style="red",
            )
        )

    # Display access keys with Rich formatting
    credentials_info = [
        f"[cyan]Account:[/cyan] {tgt_aws_access.acct_number}",
        f"[cyan]User:[/cyan] {user_response['User']} (created/confirmed in account {user_response['AccountId']})",
        f"[cyan]Password:[/cyan] {user_response['Password']}",
        f"[cyan]Access Key ID:[/cyan] {user_response['AccessKeyId']}",
        f"[cyan]Secret Access Key:[/cyan] {user_response['SecretAccessKey']}",
    ]

    console.print(Panel("\n".join(credentials_info), title="[blue]🔑 Account Credentials[/blue]", border_style="blue"))

console.print("")
console.print("[green]✅ Thanks for using this script...[/green]")
console.print("")

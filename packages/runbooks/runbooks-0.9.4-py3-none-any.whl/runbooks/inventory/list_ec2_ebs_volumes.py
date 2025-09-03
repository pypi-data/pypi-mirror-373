#!/usr/bin/env python3
import logging
import sys
from queue import Queue
from threading import Thread
from time import time

from ArgumentsClass import CommonArguments
from botocore.exceptions import ClientError
from colorama import Fore, init
from Inventory_Modules import display_results, find_account_volumes2, get_all_credentials
from tqdm.auto import tqdm

init()
__version__ = "2024.05.31"

# ANSI escape code for clearing current line (progress bar cleanup)
ERASE_LINE = "\x1b[2K"


##################
def parse_args(f_arguments):
    """
    Description: Parses the arguments passed into the script
    @param f_arguments: args represents the list of arguments passed in
    @return: returns an object namespace that contains the individualized parameters passed in
    """

    parser = CommonArguments()
    parser.multiprofile()
    parser.multiregion()
    parser.extendedargs()
    parser.fragment()
    parser.rootOnly()
    parser.save_to_file()
    parser.timing()
    parser.verbosity()
    parser.version(__version__)
    return parser.my_parser.parse_args(f_arguments)


def present_results(fVolumesFound: list):
    """
    Display comprehensive results of EBS volume discovery with analysis.

    This function processes the discovered volumes, removes duplicates,
    sorts them logically, and presents them in a formatted output with
    summary statistics and operational insights.

    Args:
        fVolumesFound (list): List of discovered EBS volumes with metadata
    """

    display_dict = {
        "VolumeId": {"DisplayOrder": 1, "Heading": "Volume ID"},
        "Size": {"DisplayOrder": 2, "Heading": "Size (GB)"},
        "VolumeType": {"DisplayOrder": 3, "Heading": "Volume Type"},
        "VolumeName": {"DisplayOrder": 4, "Heading": "Volume Name"},
        "InstanceId": {"DisplayOrder": 5, "Heading": "Instance ID"},
        "Encrypted": {"DisplayOrder": 6, "Heading": "Encrypted"},
        "State": {"DisplayOrder": 7, "Heading": "State"},
        "AccountId": {"DisplayOrder": 8, "Heading": "Account"},
        "Region": {"DisplayOrder": 9, "Heading": "Region"},
    }

    # Phase 1: Data deduplication and preparation
    de_dupe_VolumesFound = []
    AccountsFound = set()
    RegionsFound = set()

    # Remove duplicate volumes based on VolumeId and collect unique accounts/regions
    seen = set()
    for volume in fVolumesFound:
        key = volume["VolumeId"]
        if key not in seen:
            seen.add(key)
            de_dupe_VolumesFound.append(volume)
            AccountsFound.add(volume.get("AccountId"))
            RegionsFound.add(volume.get("Region"))

    sorted_Volumes_Found = sorted(
        de_dupe_VolumesFound, key=lambda x: (x["MgmtAccount"], x["AccountId"], x["Region"], x["VolumeName"], x["Size"])
    )
    display_results(sorted_Volumes_Found, display_dict, "None", None)

    print()
    print(
        f"Found {len(de_dupe_VolumesFound)} volumes across {len(AccountsFound)} account{'' if len(AccountsFound) == 1 else 's'} "
        f"across {len(RegionsFound)} region{'' if len(RegionsFound) == 1 else 's'}"
    )

    # Calculate and display orphaned volumes
    orphaned_volumes = [vol for vol in de_dupe_VolumesFound if vol.get("State") == "available"]
    if orphaned_volumes:
        print(f"{Fore.YELLOW}Warning: {len(orphaned_volumes)} orphaned (unattached) volumes found{Fore.RESET}")
        total_orphaned_size = sum(vol.get("Size", 0) for vol in orphaned_volumes)
        print(f"Total orphaned storage: {total_orphaned_size} GB")

    print()


def check_accounts_for_ebs_volumes(f_CredentialList, f_fragment_list=None):
    """
    Note that this function takes a list of Credentials and checks for EBS Volumes in every account it has creds for
    @param f_CredentialList: List of credentials for all accounts to check
    @param f_fragment_list: List of name tag fragments to limit the searching to
    @return:
    """

    class FindVolumes(Thread):
        def __init__(self, queue):
            Thread.__init__(self)
            self.queue = queue

        def run(self):
            while True:
                # Get the work from the queue and expand the tuple
                # c_account_credentials, c_region, c_text_to_find, c_PlacesToLook, c_PlaceCount = self.queue.get()
                c_account_credentials, c_region, c_fragment = self.queue.get()
                logging.info(f"De-queued info for account {c_account_credentials['AccountId']}")
                try:
                    logging.info(f"Attempting to connect to {c_account_credentials['AccountId']}")
                    # account_volumes = find_account_volumes2(c_account_credentials, c_text_to_find)
                    account_volumes = find_account_volumes2(c_account_credentials)
                    logging.info(f"Successfully connected to account {c_account_credentials['AccountId']}")
                    for _ in range(len(account_volumes)):
                        account_volumes[_]["MgmtAccount"] = c_account_credentials["MgmtAccount"]
                    AllVolumes.extend(account_volumes)
                except KeyError as my_Error:
                    logging.error(f"Account Access failed - trying to access {c_account_credentials['AccountId']}")
                    logging.info(f"Actual Error: {my_Error}")
                    pass
                except AttributeError as my_Error:
                    logging.error(f"Error: Likely that one of the supplied profiles {pProfiles} was wrong")
                    logging.warning(my_Error)
                    continue
                finally:
                    logging.info(
                        f"{ERASE_LINE}Finished finding EBS volumes in account {c_account_credentials['AccountId']} in region {c_account_credentials['Region']}"
                    )
                    pbar.update()
                    self.queue.task_done()

    if f_fragment_list is None:
        f_fragment_list = []
    AllVolumes = []
    WorkerThreads = min(len(f_CredentialList), 50)

    checkqueue = Queue()

    pbar = tqdm(
        desc=f"Finding ebs volumes from {len(f_CredentialList)} accounts and regions",
        total=len(f_CredentialList),
        unit=" accounts & regions",
    )

    for x in range(WorkerThreads):
        worker = FindVolumes(checkqueue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()

    for credential in f_CredentialList:
        logging.info(f"Connecting to account {credential['AccountId']}")
        try:
            # print(f"{ERASE_LINE}Queuing account {credential['AccountId']} in region {region}", end='\r')
            checkqueue.put((credential, credential["Region"], f_fragment_list))
        except ClientError as my_Error:
            if "AuthFailure" in str(my_Error):
                logging.error(
                    f"Authorization Failure accessing account {credential['AccountId']} in '{credential['Region']}' region"
                )
                logging.warning(f"It's possible that the region '{credential['Region']}' hasn't been opted-into")
                pass
    checkqueue.join()
    pbar.close()
    return AllVolumes


##################


def main():
    """
    Main execution function for EBS volume inventory discovery.
    Orchestrates argument parsing, credential discovery, volume enumeration, and result presentation.
    """
    import sys

    args = parse_args(sys.argv[1:])
    pProfiles = args.Profiles
    pRegionList = args.Regions
    pAccounts = args.Accounts
    pFragments = args.Fragments
    pSkipAccounts = args.SkipAccounts
    pSkipProfiles = args.SkipProfiles
    pRootOnly = args.RootOnly
    pFilename = args.Filename
    pTiming = args.Time
    verbose = args.loglevel

    # Setup logging levels
    logging.basicConfig(level=verbose, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
    logging.getLogger("boto3").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.getLogger("s3transfer").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    # ANSI escape code for clearing current line (progress bar cleanup)
    ERASE_LINE = "\x1b[2K"

    # Start execution timing
    begin_time = time()

    # Display startup information
    print()
    print(f"Checking for EBS Volumes... ")
    logging.info(f"Profiles: {pProfiles}")
    print()

    # Phase 1: Gather credentials for all target accounts and regions
    CredentialList = get_all_credentials(
        pProfiles, pTiming, pSkipProfiles, pSkipAccounts, pRootOnly, pAccounts, pRegionList
    )

    # Phase 2: Execute multi-threaded EBS volume discovery
    VolumesFound = check_accounts_for_ebs_volumes(CredentialList, pFragments)

    # Phase 3: Present results with analysis and recommendations
    present_results(VolumesFound)

    # Display execution timing if requested
    if pTiming:
        print(ERASE_LINE)
        print(f"{Fore.GREEN}This script completed in {time() - begin_time:.2f} seconds{Fore.RESET}")


if __name__ == "__main__":
    main()

    # Display completion message
    print()
    print("Thank you for using this script")
    print()

from datetime import datetime, timedelta, timezone

from runbooks.utils.logger import configure_logger

from ..utils import common
from ..utils import level_const as level

logger = configure_logger(__name__)  ## ✅ Configure Logger

## Define the standard threshold for root account access
ROOT_ACCESS_DAYS_STANDARD = 7


## @depreciated def get_root_access_days(date):
def get_root_access_days(date: str) -> timedelta:
    """
    Calculates the timedelta between a given ISO datetime string and now, with robust error handling.

    Args:
        date (str): The ISO format string to parse.

    Returns:
        timedelta: The time difference between the given date and now,
                   or timedelta.max for invalid or missing dates.
    """
    if not date or date in ("N/A", "no_information"):
        return timedelta.max

    try:
        parsed_date = datetime.fromisoformat(date)
    except ValueError:
        try:
            ## Strips the last 6 characters in the timezone offset (e.g., +00:00).
            parsed_date = datetime.fromisoformat(date[:-6])
        except ValueError:
            logger.warning(f"Invalid date format encountered: {date}")
            return timedelta.max

    return datetime.now(timezone.utc) - parsed_date


def format_last_access_message(last_used_timedelta):
    """
    Formats a user-friendly message for last access time.

    Args:
        last_used_timedelta (timedelta): Time since last access.

    Returns:
        str: A descriptive message.
    """
    if last_used_timedelta == timedelta.max:
        return "No history"
    if last_used_timedelta.days == 0:
        return "Today"
    return f"{last_used_timedelta.days} days ago"


def check_root_usage(session, translator, credential_report) -> common.CheckResult:
    """
    Performs a security check on root account usage.

    Args:
        session: AWS session object (reserved for future extensions).
        translator: Translator for multi-language support.
        credential_report: Credential report from AWS.

    Returns:
        common.CheckResult: The result of the root usage security check.
    """
    logger.info(translator.translate("checking"))

    result = common.CheckResult()
    result.title = translator.translate("title")
    result.result_cols = ["Credential Type", "Last Access Date"]

    ## Handle missing credential report
    if not credential_report:
        result.level = level.error
        result.msg = translator.translate("credential_report_error")
        result.result_rows.append(["ERR", "No Credential Report Available"])
        return result

    try:
        ## Retrieve root credential details
        root_credential_report = common.get_root_credential_report(credential_report)

        ## Calculate days since last usage for each credential type
        password_last_used = get_root_access_days(
            root_credential_report[common.CREDENTIAL_REPORT_COLS.PASSWORD_LAST_USED.value]
        )
        access_key1_last_used = get_root_access_days(
            root_credential_report[common.CREDENTIAL_REPORT_COLS.ACCESS_KEY_1_LAST_USED_DATE.value]
        )
        access_key2_last_used = get_root_access_days(
            root_credential_report[common.CREDENTIAL_REPORT_COLS.ACCESS_KEY_2_LAST_USED_DATE.value]
        )

        ## Determine the most recent access across all credentials
        last_access_days = min(password_last_used, access_key1_last_used, access_key2_last_used)

        if last_access_days > timedelta(ROOT_ACCESS_DAYS_STANDARD):
            result.level = level.success
            result.msg = translator.translate("success").format(ROOT_ACCESS_DAYS_STANDARD)
        elif last_access_days.days == 0:
            result.level = level.danger
            result.msg = translator.translate("access_today")
        else:
            result.level = level.danger
            result.msg = translator.translate("danger").format(last_access_days.days)

        ## Add detailed result rows for each credential type
        result.result_rows.extend(
            [
                ["PASSWORD", format_last_access_message(password_last_used)],
                ["ACCESS KEY1", format_last_access_message(access_key1_last_used)],
                ["ACCESS KEY2", format_last_access_message(access_key2_last_used)],
            ]
        )

    except Exception as e:
        logger.error(f"Error processing root usage check: {str(e)}", exc_info=True)
        result.level = level.error
        result.msg = translator.translate("processing_error")
        result.result_rows.append(["ERR", "Processing Error"])
        result.error_message = str(e)

    return result

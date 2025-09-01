import time
from datetime import date, timedelta, datetime
from liveramp_automation.utils.log import Logger

ATTEMPT_NUMBER = 10
DEFAULT_WAIT_TIME_IN_TWO_SECONDS = 2
WAIT_FIXED_IN_MS = 1 * 1000
TWO_SECONDS_IN_MS = 2 * 1000
TEN_SECONDS_IN_MS = 10 * 1000
ONE_MINUTE_IN_MS = 60 * 1000



"""
The MACROS() API prepared some expected time format.
You could involve the time format like: yesterday.format(**MACROS) at any code snippet.
"""
MACROS = {
    "yesterday": (date.today() - timedelta(days=1)).strftime("%Y%m%d"),
    "today": date.today().strftime("%Y%m%d"),
    "dayOfYear": (date.today().timetuple()).tm_yday,
    "now": datetime.now().strftime("%Y%m%d%H%M%S"),  # preferred format
    "now_readable": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "now_ingestion": datetime.now().strftime("%Y%m%d-%H%M%S"),  # data ingestion must be in yyyymmdd-hhmmss format
    "three_days_ago": (date.today() - timedelta(days=3)).strftime("%Y%m%d"),
    "two_hours_from_now": (datetime.now() + timedelta(hours=2)).strftime("%Y%m%d-%H%M%S"),
    "24hours_before_now": (datetime.now() - timedelta(hours=24)).strftime("%Y%m%d%H%M%S"),
    "one_year_later": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
    "one_year_later_eng": '{dt:%b} {dt.day} {dt.year}'.format(dt=datetime.now() + timedelta(days=365))
}


def fixed_wait(seconds: int = DEFAULT_WAIT_TIME_IN_TWO_SECONDS) -> None:
    """Pause the program's execution for a specified number of seconds.

    :param seconds: The number of seconds to wait (default is 3 seconds).
    :return: None
    """
    time.sleep(seconds)
    Logger.debug("Pause the program's execution for {} seconds.".format(seconds))

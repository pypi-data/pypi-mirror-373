import datetime
from typing import Dict, Optional

DAYS_FIELD_NAME = "days"
SECONDS_FIELD_NAME = "seconds"
MICROSECONDS_FIELD_NAME = "microseconds"


def format_duration(delta: datetime.timedelta) -> Optional[str]:
    """
    Formats a timedelta into a simple string representation.

    Returns a string representation if the timedelta can be expressed as whole days, hours, or minutes,
    otherwise returns None.

    :param delta: The timedelta to format
    :return: String representation (e.g., "3d", "25h", "1d", "30m") or None if not a simple format
    """
    total_seconds = delta.total_seconds()
    assert total_seconds >= 0

    if total_seconds % 86400 == 0:
        days = total_seconds // 86400
        return f"{int(days)}d"

    elif total_seconds % 3600 == 0:
        hours = total_seconds // 3600
        return f"{int(hours)}h"

    elif total_seconds % 60 == 0:
        minutes = total_seconds // 60
        return f"{int(minutes)}m"

    return None


def timedelta_to_dict(time_delta: datetime.timedelta) -> Dict[str, int]:
    """
    Serialize a timedelta into a dictionary that can be used to generate a YAML file.
    """
    return {
        DAYS_FIELD_NAME: time_delta.days,
        SECONDS_FIELD_NAME: time_delta.seconds,
        MICROSECONDS_FIELD_NAME: time_delta.microseconds,
    }


def dict_to_timedelta(time_dict: Dict[str, int]) -> datetime.timedelta:
    """
    Deserialize a dictionary back into a timedelta object.

    It's expected that the dictionary contains only days, seconds, and microseconds.
    """
    return datetime.timedelta(
        days=time_dict.get(DAYS_FIELD_NAME, 0),
        seconds=time_dict.get(SECONDS_FIELD_NAME, 0),
        microseconds=time_dict.get(MICROSECONDS_FIELD_NAME, 0),
    )

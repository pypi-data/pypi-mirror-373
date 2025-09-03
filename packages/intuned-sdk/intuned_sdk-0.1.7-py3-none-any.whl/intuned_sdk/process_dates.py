from datetime import datetime
from typing import Optional

from dateutil import parser


def process_date(date_string: str) -> Optional[datetime]:
    """
    Process various date string formats into datetime objects using dateutil.
    Returns only the date part (year, month, day) without time components.

    Args:
        date_string: A string containing a date in various possible formats

    Returns:
        datetime object with only date components if parsing successful, None if parsing fails

    Examples:
        >>> process_date("22/11/2024 21:19:05")
        datetime(2024, 11, 22, 0, 0)
        >>> process_date("5 Dec 2024 8:00 AM PST")
        datetime(2024, 12, 5, 0, 0)
    """
    try:
        # Handle the case where there's a hyphen used as separator
        date_string = date_string.replace(" - ", " ")

        # Parse the date string with dayfirst=False to handle MM/DD/YYYY format
        parsed_date = parser.parse(date_string, dayfirst=False)
        return parsed_date.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        )
    except (ValueError, TypeError):
        return None


def is_date_in_last_x_days(date: datetime, days: int) -> bool:
    """
    Check if a date is within the last x days.
    """
    return (datetime.now() - date).days <= days

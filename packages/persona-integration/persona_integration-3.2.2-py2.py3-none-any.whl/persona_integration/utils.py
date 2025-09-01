"""
persona_integration utilities.
"""
from datetime import datetime


def parse_basic_iso_date_to_full_date(date):
    """
    Parse a date string into a timezone aware datetime object.

    This method assumes that the date string parameter follows the full ISO 8601 format.

    Below is an example string in this format.

    '2024-08-06T20:04:19.177Z'

    Note that The "Z" at the end of the date string stands for "Zulu time," which is a military and aviation term
    for Coordinated Universal Time (UTC). It indicates that the time is given in the UTC time zone, with no offset
    for local time zones.

    The datetime module supports a more limited set of the ISO 8601 standard. For example, the datetime module does not
    have native support for the "Z" suffix when parsing strings to datetime objects, so the datetime object resulting
    from parsing such a string is naive.

    For this reason, we replace the "Z" suffix with "+00:00", which represents UTC in the standard ISO format.

    Arguments:
        * date (str): the datetime string

    Returns:
        * date (datetime): the datetime object representing the date
    """
    iso_date = date.replace('Z', '+00:00')

    aware_datetime = datetime.fromisoformat(iso_date)

    return aware_datetime

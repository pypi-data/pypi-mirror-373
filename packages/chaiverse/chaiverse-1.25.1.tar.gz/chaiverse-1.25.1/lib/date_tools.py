from datetime import datetime, timezone
import dateparser
import pytz
from typing import Annotated, Optional

from pydantic import PlainSerializer
from typing_extensions import Literal

from chaiverse.schemas.date_range_schema import DateRange

US_PACIFIC = pytz.timezone('US/Pacific')
UTC = pytz.timezone('UTC')


# Pydantic v2 broke serialization with timezones, so we need a custom type
# to maintain the previous behaviour
DateTime = Annotated[
    datetime, PlainSerializer(lambda dt: dt.isoformat())
]


def utc_string(date_string: Optional[str]=None):
    return _create_date_string_in_timezone(UTC, date_string)


def convert_to_utc_iso_format(date_string: Optional[str], default_timezone=US_PACIFIC):
    date_string_in_utc = None
    if date_string is not None:
        date = datetime.fromisoformat(date_string)
        date = default_timezone.localize(date) if not date.tzinfo else date
        date_in_utc = date.astimezone(timezone.utc)
        date_string_in_utc = date_in_utc.isoformat()
    return date_string_in_utc


def convert_to_us_pacific_date(date: Optional[datetime], default_timezone=UTC):
    date_in_us_pacific = None
    if date is not None:
        date = default_timezone.localize(date) if not date.tzinfo else date
        date_in_us_pacific = date.astimezone(US_PACIFIC)
    return date_in_us_pacific


def _create_date_string_in_timezone(pytz_timezone, date_string: Optional[str]=None):
    if date_string:
        date = dateparser.parse(date_string)
        date = pytz_timezone.localize(date)
    else:
        date = datetime.now(pytz_timezone)
    return date.isoformat()

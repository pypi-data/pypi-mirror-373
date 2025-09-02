from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Union

from bigdata_client.models.advanced_search_query import (
    AbsoluteDateRangeQuery,
    RollingDateRangeQuery,
)
from bigdata_client.models.search import Expression


class RollingDateRange(Enum):
    """A date range that is relative to the current date."""

    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"  # goes back 7 days and starts from that week's Monday until that sunday
    LAST_SEVEN_DAYS = "last_seven_days"
    LAST_THIRTY_DAYS = "last_thirty_days"
    LAST_NINETY_DAYS = "last_ninety_days"
    YEAR_TO_DATE = "year_to_date"
    LAST_YEAR = "last_twelve_months"
    LAST_ONE_HOURS = "last_1_hours"
    LAST_THREE_HOURS = "last_3_hours"
    LAST_SIX_HOURS = "last_6_hours"
    LAST_NINE_HOURS = "last_9_hours"
    LAST_TWELVE_HOURS = "last_12_hours"
    LAST_TWENTY_FOUR_HOURS = "last_24_hours"
    LAST_FORTY_EIGHT_HOURS = "last_48_hours"

    def to_expression(self) -> Expression:
        query = RollingDateRangeQuery(self.value)
        return query.to_expression()

    def __and__(self, other):
        query = RollingDateRangeQuery(self.value)
        return query & other

    def __or__(self, other):
        query = RollingDateRangeQuery(self.value)
        return query | other

    def __invert__(self):
        query = RollingDateRangeQuery(self.value)
        return ~query

    def make_copy(self):
        """
        It doesn't make much sense, but just to comply with the interface in
        AdvancedSearchQuery.
        """
        return RollingDateRange(self.value)


class AbsoluteDateRange:
    """
    A date range with a start and end date

    The __init__ method accepts either datetime objects or strings in ISO format:

    >>> ran1 = AbsoluteDateRange(datetime(2021, 1, 1), datetime(2021, 1, 2))
    >>> ran2 = AbsoluteDateRange("2021-01-01T00:00:00", "2021-01-02T00:00:00")
    >>> ran1 == ran2
    True

    You can also use the to_string_tuple method to convert the datetimes to strings:

    >>> ran1
    AbsoluteDateRange('2021-01-01T00:00:00', '2021-01-02T00:00:00')
    >>> start, end = ran1.to_string_tuple()
    >>> start
    '2021-01-01T00:00:00'
    >>> end
    '2021-01-02T00:00:00'
    """

    def __init__(
        self, start: Union[datetime, str, None], end: Union[datetime, str, None]
    ):
        """Creates a new AbsoluteDateRange from two datetimes or strings."""
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        self.start_dt = to_naive_utc(start).replace(microsecond=0) if start else None
        self.end_dt = to_naive_utc(end).replace(microsecond=0) if end else None

    def to_string_tuple(self) -> tuple[Optional[str], Optional[str]]:
        """
        Converts datetimes to strings and returns the tuple

        >>> ran = AbsoluteDateRange(datetime(2021, 1, 1), datetime(2021, 1, 2))
        >>> ran.to_string_tuple()
        ('2021-01-01T00:00:00', '2021-01-02T00:00:00')

        >>> ran2 = AbsoluteDateRange(None, datetime(2021, 1, 2))
        >>> ran2.to_string_tuple()
        (None, '2021-01-02T00:00:00')

        >>> ran3 = AbsoluteDateRange(datetime(2021, 1, 1), None)
        >>> ran3.to_string_tuple()
        ('2021-01-01T00:00:00', None)

        >>> ran4 = AbsoluteDateRange(*ran.to_string_tuple())
        >>> ran == ran4
        True
        """
        start = self.start_dt.isoformat() if self.start_dt else None
        end = self.end_dt.isoformat() if self.end_dt else None
        return start, end

    def __eq__(self, other):
        if not isinstance(other, AbsoluteDateRange):
            return False
        return self.start_dt == other.start_dt and self.end_dt == other.end_dt

    def __repr__(self):
        return f"AbsoluteDateRange{self.to_string_tuple()}"

    @property
    def _proxy_query(self):
        start, end = self.to_string_tuple()
        if start is None or end is None:
            raise ValueError("Cannot create a query with None values")
        return AbsoluteDateRangeQuery(start, end)

    def to_expression(self):
        return self._proxy_query.to_expression()

    def to_dict(self):
        return self._proxy_query.to_dict()

    def __and__(self, other):
        return self._proxy_query & other

    def __or__(self, other):
        return self._proxy_query | other

    def __invert__(self):
        return ~self._proxy_query

    def make_copy(self):
        return AbsoluteDateRange(self.start_dt, self.end_dt)


def is_timezone_aware(dt):
    return dt.tzinfo is not None


def to_naive_utc(dt):
    """
    Transform the existing timezone to UTC and assume that the timezone is UTC if not specified.
    It returns a naive datetime (in UTC) without a timezone
    """
    if not is_timezone_aware(dt):
        dt = dt.replace(tzinfo=timezone.utc)

    utc_datetime = dt.astimezone(timezone.utc)
    return utc_datetime.replace(tzinfo=None)

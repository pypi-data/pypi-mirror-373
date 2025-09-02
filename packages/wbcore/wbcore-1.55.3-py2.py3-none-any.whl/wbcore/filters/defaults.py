from calendar import monthrange
from datetime import date, timedelta

from django.utils.timezone import localdate
from psycopg.types.range import DateRange
from rest_framework.exceptions import APIException

from wbcore.utils.date import get_end_date_from_date, get_start_date_from_date


def current_quarter_date_start(*args, **kwargs):
    return get_start_date_from_date(localdate())


def current_quarter_date_end(*args, **kwargs):
    return get_end_date_from_date(localdate())


def current_quarter_date_range(*args, **kwargs):
    return DateRange(current_quarter_date_start(*args, **kwargs), current_quarter_date_end(*args, **kwargs))


def current_month_date_start(*args, **kwargs):
    today = date.today()
    return date(today.year, today.month, 1)


def current_month_date_end(*args, **kwargs):
    today = date.today()
    return date(today.year, today.month, monthrange(today.year, today.month)[1])


def current_month_date_range(*args, **kwargs):
    return DateRange(current_month_date_start(*args, **kwargs), current_month_date_end(*args, **kwargs))


def current_year_date_range(*args, **kwargs):
    d = localdate()
    return DateRange(date(d.year, 1, 1), max((date(d.year + 1, 1, 1), d + timedelta(days=60))))


def year_to_date_range(*args, **kwargs):
    d = localdate()
    return DateRange(d.replace(day=1, month=1), d.today())


def n_year_data_range(n: int, *args, **kwargs):
    d = localdate()
    return DateRange(d - timedelta(days=n * 365), d)


def one_year_date_range(*args, **kwargs):
    return n_year_data_range(1)


def five_year_data_range(*args, **kwargs):
    return n_year_data_range(5)


def current_quarter_date_interval(*args, **kwargs):
    return (
        current_quarter_date_start(),
        current_quarter_date_end(*args, **kwargs),
    )


class RequiredFilterMissing(APIException):
    status_code = 400
    default_detail = "Required filters are not available in the query parameters."
    default_code = "required_filters_missing"

import datetime as dt
from typing import Union


def parse_execution_date(execution_date: Union[str, dt.date, dt.datetime]) -> dt.datetime:
    """Parse an airflow execution (iso format) date to a datetime object, accepts date and datetime as well, always returning a datetime."""
    if isinstance(execution_date, dt.datetime):
        return execution_date
    if isinstance(execution_date, dt.date):
        # Convert date to datetime at midnight
        return dt.datetime.combine(execution_date, dt.time())

    return dt.datetime.fromisoformat(execution_date)


def date_range(execution_date: Union[str, dt.datetime, dt.date], length: int) -> list[dt.datetime]:
    """Return a series of <length> datetimes, ending with execution_date."""
    start_date = parse_execution_date(execution_date)
    return [start_date - dt.timedelta(days=i) for i in reversed(range(length))]

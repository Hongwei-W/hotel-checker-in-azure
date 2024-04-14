import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

RATE_CODES = {"none": "Standard Rate", "aaa": "AAA/CAA Rate", "points": "Points"}

def marriott_date(dt):
    return dt.strftime('%m/%d/%Y')

def list_all_dates(start, end):
    dates = []
    cur = start
    while cur <= end:
        dates.append(cur)
        cur += timedelta(days=1)
    return dates

def month_end(dt):
    """get a datetime object of the last day of the month

    Args:
        dt (datetime): a datetime object

    Returns:
        datetime: a datetime object of the last day of the month
    """
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    return datetime(dt.year, dt.month, last_day)

def month_start(dt):
    """get a datetime object of the first day of the month

    Args:
        dt (datetime): a datetime object

    Returns:
        datetime: a datetime object of the first day of the month
    """
    return datetime(dt.year, dt.month, 1)

def next_month(dt):
    return dt + relativedelta(months=1)

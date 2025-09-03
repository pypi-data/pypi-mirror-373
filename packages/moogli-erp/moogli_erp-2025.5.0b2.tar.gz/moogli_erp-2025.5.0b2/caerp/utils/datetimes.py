import calendar
import datetime
import logging

from dateutil.relativedelta import relativedelta
from typing import Union


logger = logging.getLogger(__name__)


def parse_date(value, default=None, format_="%Y-%m-%d"):
    """
    Get a date object from a string

    :param str value: The string to parse
    :param str default: The default value to return
    :param str format_: The format of the str date
    :returns: a datetime.date object
    """
    try:
        result = datetime.datetime.strptime(value, format_).date()
    except ValueError as err:
        logger.debug("{} is not a date".format(value))
        if default is not None:
            result = default
        else:
            raise err
    return result


def parse_datetime(
    str_datetime: str, default=None, format_: str = "%Y-%m-%d %H:%M:%S"
) -> datetime.datetime:
    """
    Transform a date string to a date object

    :param str str_date: The date string
    :param tuple formats: List of date format to try when parsing
    :return: A datetime object
    :rtype: datetime.date
    """
    try:
        result = datetime.datetime.strptime(str_datetime, format_)
    except ValueError as err:
        logger.debug("{} is not a date".format(str_datetime))
        if default is not None:
            result = default
        else:
            raise err

    return result


def get_current_year():
    return datetime.date.today().year


def utcnow(delay=0):
    """
    Add Timezone info to the 'now' datetime object
    Usefull for delaying celery calls

    """
    n = datetime.datetime.utcnow()
    if delay:
        n += datetime.timedelta(seconds=delay)
    return n


def date_to_datetime(date: datetime.date) -> datetime.datetime:
    """Generate a datetime (0h00) from a date"""
    base_time = datetime.datetime.min.time()
    return datetime.datetime.combine(date, base_time)


def date_to_timestamp(date: datetime.date) -> float:
    """Convert a date to a timestamp"""
    return datetime.datetime.timestamp(date_to_datetime(date))


def datetime_to_timestamp(datetime: datetime.datetime) -> float:
    """Convert a datetime to a timestamp"""
    return datetime.datetime.timestamp(datetime)


def get_strftime_from_date(date_obj, template_str):
    """
    Return the result of date.strftime(template_str) handling exceptions
    """
    try:
        resp = date_obj.strftime(template_str)
    except ValueError:
        resp = ""
    return resp


def format_long_date(date: datetime.date, include_dayname: bool = True) -> str:
    """
    Convert a date to a localized string

    >>> import datetime
    >>> d = datetime.date.today()
    >>> format_long_date(d, include_name=True)
    Jeudi 22 juin 2023
    """
    template = "%d %B %Y"
    if include_dayname:
        template = f"%A {template}"
    return get_strftime_from_date(date, template)


def format_long_datetime(
    datetime_object: datetime.date, include_dayname: bool = True
) -> str:
    """
    Convert a datetime to a localized string

    >>> import datetime
    >>> d = datetime.datetime.now()
    >>> format_long_datetime(d, include_dayname=True)
    Jeudi 22 juin 2023 à 10h22
    """
    template = "%d %B %Y à %H:%M"
    if include_dayname:
        template = f"%A {template}"
    return get_strftime_from_date(datetime_object, template)


def str_to_date(
    str_date, formats=("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%Y-%m-%d", "%Y%m%d")
):
    """
    Transform a date string to a date object

    :param str str_date: The date string
    :param tuple formats: List of date format to try when parsing
    :return: A datetime object
    :rtype: datetime.datetime
    """
    res = None
    if str_date is not None:
        for format_ in formats:
            try:
                res = datetime.datetime.strptime(str_date, format_)
            except ValueError:
                pass
            else:
                break
    return res


def format_short_date(date):
    """
    return a short printable version of the date obj
    """
    if isinstance(date, datetime.date):
        resp = get_strftime_from_date(date, "%d/%m/%Y")
    elif not date:
        resp = ""
    else:
        date_obj = datetime.datetime.fromtimestamp(float(date))
        resp = get_strftime_from_date(date_obj, "%d/%m/%Y %H:%M")
    return resp


def format_datetime(datetime_object, timeonly=False, with_linebreak=False):
    """
    format a datetime object
    """
    res = get_strftime_from_date(datetime_object, "%H:%M")
    if not timeonly:
        day = get_strftime_from_date(datetime_object, "%d/%m/%Y")
        linebreak = "<br />" if with_linebreak else " "
        res = "%s%sà %s" % (day, linebreak, res)
    return res


def format_date(date, short=True):
    """
    return a pretty print version of the date object
    """
    if short:
        return format_short_date(date)
    else:
        return format_long_date(date)


def format_duration(duration, short=True):
    """
    return a pretty print version of a duration.

    :param (int,int) duration: hours,minutes tuple to convert.
    :param bool short: if True, hide minutes part when it equals zero.
    """
    hours, minutes = duration
    if minutes == 0 and short:
        return "{}h".format(hours)
    else:
        return "{}h{:02d}".format(hours, minutes)


class DateTools:
    def today(self):
        return datetime.date.today()

    def year_start(self, year: int = None) -> datetime.date:
        if year is None:
            year = datetime.date.today().year
        return datetime.date(year, 1, 1)

    def year_end(self, year: int = None) -> datetime.date:
        if year is None:
            year = datetime.date.today().year
        return datetime.date(year, 12, 31)

    def month_start(self, year: int = None, month: int = None) -> datetime.date:
        if year is None:
            year = datetime.date.today().year
        if month is None:
            month = datetime.date.today().month
        return datetime.date(year, month, 1)

    def month_end(self, year: int = None, month: int = None) -> datetime.date:
        if year is None:
            year = datetime.date.today().year
        if month is None:
            month = datetime.date.today().month
        return datetime.date(year, month, calendar.monthrange(year, month)[1])

    def previous_year_start(self, year: int = None) -> datetime.date:
        if year is None:
            year = datetime.date.today().year
        return datetime.date(year - 1, 1, 1)

    def previous_year_end(self, year: int = None) -> datetime.date:
        if year is None:
            year = datetime.date.today().year
        return datetime.date(year - 1, 12, 31)

    def previous_month_start(
        self, year: int = None, month: int = None
    ) -> datetime.date:
        if year is None:
            year = datetime.date.today().year
        if month is None:
            month = datetime.date.today().month
        month_start = self.month_start(year, month)
        return month_start - relativedelta(months=1)

    def previous_month_end(self, year: int = None, month: int = None) -> datetime.date:
        if year is None:
            year = datetime.date.today().year
        if month is None:
            month = datetime.date.today().month
        month_end = self.month_start(year, month)
        return month_end - datetime.timedelta(days=1)

    def format_date(
        self,
        date: Union[datetime.datetime, datetime.date, str, int, None],
        long_format: bool = False,
        force_no_time: bool = False,
    ) -> str:
        """
        Returns formatted string date from various date entry

        :param [datetime.datetime, datetime.date, str, int] date: The date we want to format, can be :
        - datetime.datetime object
        - datetime.date object
        - timestamp as int
        - string formated as 'YYYY-MM-DD', 'YYYYMMDD', or 'DD/MM/YYYY'
        :param bool long_format: '1 janvier 2023' if True, else '01/01/2023'
        :param bool force_no_time: no time in returned string if True, even with datetime or timestamp
        """
        str_date = ""
        date_template = "%d %B %Y" if long_format else "%d/%m/%Y"
        time_template = "" if force_no_time else " %H:%M"
        if isinstance(date, datetime.datetime):
            # From datetime object
            str_date = date.strftime(f"{date_template}{time_template}")
        elif isinstance(date, datetime.date):
            # From date object
            str_date = date.strftime(date_template)
        elif isinstance(date, int):
            # From timestamp
            date_obj = datetime.datetime.fromtimestamp(date)
            str_date = date_obj.strftime(f"{date_template}{time_template}")
        elif isinstance(date, str):
            # From string
            try:
                date_obj = datetime.datetime.fromisoformat(date)
            except ValueError:
                try:
                    date_obj = datetime.datetime.strptime(date, "%Y%m%d")
                except ValueError:
                    try:
                        date_obj = datetime.datetime.strptime(date, "%d/%m/%Y")
                    except ValueError:
                        raise ValueError("Unrecognized date string format")
            if ":" in date:
                str_date = date_obj.strftime(f"{date_template}{time_template}")
            else:
                str_date = date_obj.strftime(date_template)
        return str_date

    def age(self, birth_date: datetime.date, date_ref: datetime.date = None) -> int:
        if birth_date is None:
            return None
        if date_ref is None:
            date_ref = self.today()
        return (
            date_ref.year
            - birth_date.year
            - int((date_ref.month, date_ref.day) < (birth_date.month, birth_date.day))
        )

    def get_period_months(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> list:
        months = []
        if start_date is not None:
            months.append((start_date.year, start_date.month))
            if end_date is not None:
                date = start_date
                while (date.year < end_date.year) or (
                    date.year == end_date.year and date.month < end_date.month
                ):
                    date = date + relativedelta(months=1)
                    months.append((date.year, date.month))
        elif end_date is not None:
            months.append((end_date.year, end_date.month))
        return months

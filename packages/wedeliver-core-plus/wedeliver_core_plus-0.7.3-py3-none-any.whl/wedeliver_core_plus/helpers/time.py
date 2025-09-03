import pytz
from dateutil import parser
from flask import request
from datetime import datetime, timedelta, date, time

from flask_babel import format_datetime
from marshmallow import fields

DATABASE_DATE_FORMAT = "%Y-%m-%d"
DATABASE_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATABASE_TIME_FORMAT = "%H:%M:%S"

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT
DATETIME_FORMAT_SCHEMA = "%Y-%m-%d %H:%M"
DATETIME_FORMAT_BABEL_SCHEMA = "dd-MM-yyyy hh:mm a"


class LocalizedDateTime(fields.DateTime):
    def __init__(self, datetime_format=None, **kwargs):
        super().__init__(**kwargs)
        self.datetime_format = datetime_format or DATETIME_FORMAT_BABEL_SCHEMA

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return format_datetime(value, format=self.datetime_format)


def get_time_zone():
    time_zone = "UTC"
    if request:
        if request.headers.get("country_code"):
            time_zone = dict(sa="Asia/Riyadh", ps="Asia/Hebron").get(
                request.headers.get("country_code"), "UTC"
            )
    return time_zone


def from_utc_to_datetime_zone(date_time, time_zone=None):
    if isinstance(date_time, str):
        date_time = date_time.replace("T", " ").replace("Z", "")
    # Get the default Time Zone if not sent in parameters
    # Time Zone in KSA for example should be: UTC
    if not date_time:
        return date_time

    if len(str(date_time)) < 12:
        return date_time
    if time_zone is None:
        time_zone = get_time_zone()
    # Check if there is a set timezone, if not, return the datetime as it is
    if not time_zone:
        # app.logger.error(format_exception(traceback.format_exc()))
        return date_time

    # Check the time_zone if it is correct. If it is not defined, return the same date_time without conversion
    try:
        time_zone = pytz.timezone(time_zone)
    except Exception:
        # app.logger.error(format_exception(traceback.format_exc()))
        return date_time
    # Convert the date time to datetime object if it is sent as string
    if isinstance(date_time, str) or isinstance(date_time, timedelta):
        date_time = datetime.strptime(str(date_time)[:19], DATABASE_DATE_TIME_FORMAT[:17])
    date_time = pytz.utc.localize(date_time)

    # This method is not working, makes some extra minutes, do not use it!!!!
    # date_time = date_time.replace(tzinfo=pytz.utc)
    # If after checking the date time is not an object valid for conversion, return the object as it is
    if not isinstance(date_time, datetime):
        # app.logger.error(format_exception(traceback.format_exc()))
        return date_time

    # Convert the date_time to the target timezone
    # If the conversion failed, we should return the object as it is
    try:
        date_time = (date_time.astimezone(time_zone)).strftime(DATABASE_DATE_TIME_FORMAT)
    except Exception:
        pass
        # app.logger.error(format_exception(traceback.format_exc()))

    return date_time


def from_datetime_zone_to_utc(date_time, time_zone=None, only_date=False, to_string=True):
    if isinstance(date_time, str):
        date_time = date_time.replace("T", " ").replace("Z", "")
        if len(str(date_time)) < 12:
            return date_time
    # Get the default Time Zone if not sent in parameters
    # Time Zone in KSA for example should be: UTC

    if time_zone is None:
        time_zone = get_time_zone()
    # Check if there is a set timezone, if not, return the datetime as it is
    if not time_zone:
        # app.logger.error(format_exception(traceback.format_exc()))
        return date_time

    # Check the time_zone if it is correct. If it is not defined,
    # return the same date_time without conversion
    try:
        time_zone = pytz.timezone(time_zone)
    except Exception:
        # app.logger.error(format_exception(traceback.format_exc()))
        return date_time
    # Convert the date time to datetime object if it is sent as string
    if isinstance(date_time, str) or isinstance(date_time, timedelta):
        date_time = datetime.strptime(str(date_time)[:19], DATABASE_DATE_TIME_FORMAT[:17])

        date_time = time_zone.localize(date_time)
    # This method is not working, makes somoe extra minutes, do not use it!!!!
    # date_time = date_time.replace(tzinfo=time_zone)

    # If after checking the date time is not an object valid for conversion, return the object as it is
    if not isinstance(date_time, datetime):
        # app.logger.error(format_exception(traceback.format_exc()))
        return date_time

    # Convert the date_time to the target timezone
    # If the conversion failed, we should return the object as it is
    try:
        date_time = (date_time.astimezone(pytz.timezone(pytz.utc.zone)))
        if only_date:
            date_time = datetime(date_time.year, date_time.month, date_time.day)

        if to_string:
            date_time = date_time.strftime(
                DATABASE_DATE_TIME_FORMAT
            )
    except Exception:
        pass
        # app.logger.error(format_exception(traceback.format_exc()))
    return date_time


def from_string_to_datetime(value, value_format=DATABASE_DATE_TIME_FORMAT):
    return datetime.strptime(value, value_format) if value else None


def from_string_to_date(value, value_format=DATABASE_DATE_FORMAT):
    return from_string_to_datetime(value, value_format).date() if value else None


def from_datetime_to_string(value):
    return str(value) if value else None


def from_bulk_datetime_to_string(value_list, keys):
    for item in value_list:
        for key in keys:
            item[key] = from_datetime_to_string(value=item[key])
    return value_list


def from_bulk_string_to_datetime(value_list, keys, value_format=DATABASE_DATE_TIME_FORMAT):
    for item in value_list:
        for key in keys:
            item[key] = from_string_to_datetime(value=item[key], value_format=value_format) if item.get(key) else None
    return value_list


def from_bulk_string_to_date(value_list, keys, value_format=DATABASE_DATE_FORMAT):
    for item in value_list:
        for key in keys:
            item[key] = from_string_to_date(value=item[key], value_format=value_format)
    return value_list


def get_datetime(datetime_str=None):
    if not datetime_str or datetime_str == "0000-00-00 00:00:00.000000":
        return datetime.now()

    if isinstance(datetime_str, (datetime, timedelta)):
        return datetime_str

    elif isinstance(datetime_str, (list, tuple)):
        return datetime(datetime_str)

    elif isinstance(datetime_str, date):
        return datetime.combine(datetime_str, time())

    if is_invalid_date_string(datetime_str):
        return None

    try:
        return datetime.strptime(datetime_str, DATETIME_FORMAT)
    except ValueError:
        return parser.parse(datetime_str)


def is_invalid_date_string(date_string):
    # dateutil parser does not agree with dates like "0001-01-01" or "0000-00-00"
    return (not date_string) or (date_string or "").startswith(
        ("0001-01-01", "0000-00-00")
    )


def format_date_time(value):
    from datetime import datetime, date

    if value is None:
        return None
    if not isinstance(value, datetime):
        return None
    if not isinstance(value, date):
        return None

    return value.strftime("%Y-%m-%d %H:%M:%S")
import datetime
import logging
from typing import Any, Optional

from regscale.core.utils.date import datetime_str, date_str

logger = logging.getLogger(__name__)


def safe_float(value: Any, default: float = 0.0, field_name: str = "value") -> float:
    """
    Safely convert any value to a float.

    :param Any value: The value to convert
    :param float default: The default value to return if conversion fails
    :param str field_name: The name of the field being parsed (for logging purposes)
    :return: The parsed float value or the default value
    :rtype: float
    """
    if value is None:
        return default

    try:
        return float(value)
    except (ValueError, TypeError):
        logger.debug(f"Invalid float {field_name}: {value}. Defaulting to {default}")
        return default


def safe_int(value: Any, default: int = 0, field_name: str = "value") -> int:
    """
    Safely convert any value to an integer.

    :param Any value: The value to convert
    :param int default: The default value to return if conversion fails
    :param str field_name: The name of the field being parsed (for logging purposes)
    :return: The parsed integer value or the default value
    :rtype: int
    """
    if value is None:
        return default

    try:
        return int(value)
    except (ValueError, TypeError):
        logger.debug(f"Invalid integer {field_name}: {value}. Defaulting to {default}")
        return default


def safe_datetime_str(
    value: Any, default: datetime.datetime = datetime.datetime.now(), date_format: Optional[str] = None
) -> str:
    """
    Safely convert any value to a datetime.

    :param Any value: The value to convert
    :param datetime default: The default value to return if conversion fails
    :param Optional[str] date_format: The date format to use for the datetime string, defaults to None
    :return: The parsed datetime value or the default value
    :rtype: str
    """
    value = datetime_str(value, date_format)
    if not value:
        value = datetime_str(default, date_format)
    return value


def safe_date_str(value: Any, default: datetime.date = datetime.date.today()) -> str:
    """
    Safely convert any value to a date string.

    :param Any value: The value to convert
    :param date default: The default value to return if conversion fails
    :return: The parsed date string value or the default value

    :rtype: str
    """
    value = date_str(value)
    if not value:
        value = date_str(default)
    return value

import re
import codecs
import decimal
import datetime
from pprint import pformat
from typing import Optional, Union, List, Callable
import ast

# Convert SQL data to JS format for display


def none(data: Optional[str]) -> str:
    """Converts various 'null' representations to an empty string."""
    return "" if data in (None, "None", "null", "@NULL", "@null") else data


def phone(data: Optional[str]) -> str:
    """Formats a 10-digit phone number as (XXX) XXX-XXXX or returns an empty string if invalid."""
    if data in (None, "None", ""):
        return ""
    digits = re.sub(r"[^0-9]", "", data)
    match = re.search(r"\d{10}$", digits)
    if match:
        num = match.group()
        return f"({num[:3]}) {num[3:6]}-{num[6:]}"
    return ""


def day_of_week(data: Union[int, str, List], abbrev: bool = False) -> str:
    """Converts a day number (1-7) to a day name, abbreviated if specified. Supports lists."""
    days_full = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }
    days_abbrev = {
        1: "Mon",
        2: "Tue",
        3: "Wed",
        4: "Thu",
        5: "Fri",
        6: "Sat",
        7: "Sun",
    }
    days = days_abbrev if abbrev else days_full

    if isinstance(data, list):
        return ",".join(day_of_week(day, abbrev) for day in data if day in days)

    try:
        return days[int(data)]
    except (ValueError, KeyError, TypeError):
        return ""


def date_conv(
    data: Union[datetime.datetime, datetime.date, str], fmt: str = "%Y-%m-%d"
) -> str:
    """Formats a date object as a string according to the specified format."""
    return (
        data.strftime(fmt)
        if isinstance(data, (datetime.datetime, datetime.date))
        else str(data)
    )


def time_conv(
    data: Union[datetime.datetime, datetime.time, str], fmt: str = "%X"
) -> str:
    """Formats a time object as a string according to the specified format."""
    return (
        data.strftime(fmt)
        if isinstance(data, (datetime.datetime, datetime.time))
        else str(data)
    )


def timestamp(data: Union[datetime.datetime, str], fmt: str = "%c") -> str:
    """Formats a datetime object as a string according to the specified format."""
    return data.strftime(fmt) if isinstance(data, datetime.datetime) else str(data)


def email(data: Optional[str]) -> str:
    """Returns a lowercase email address or an empty string if invalid."""
    return "" if data in (None, "None") else data.lower()


def pointer(data: Union[str, int]) -> Union[int, str]:
    """Converts a string to an integer, or returns an empty string if conversion fails."""
    try:
        return int(data)
    except (ValueError, TypeError):
        return ""


def rot13(data: str) -> str:
    """Encodes a string using ROT13."""
    return codecs.decode(data, "rot13")


def boolean(data: Union[str, bool]) -> bool:
    """Converts various representations to a boolean."""
    if isinstance(data, str) and data.lower() in ["false", "", "f", "off", "no"]:
        return False
    return bool(data)


def money(data: Union[str, float, int, decimal.Decimal]) -> str:
    """Formats a numeric value as currency."""
    if data in [None, ""]:
        return ""
    try:
        amount = decimal.Decimal(str(data))
        return f"${amount:,.2f}"
    except (decimal.InvalidOperation, ValueError):
        return ""


def round_to(
    precision: int, data: Optional[Union[str, float, decimal.Decimal]] = None
) -> Union[Callable[[Union[str, float, decimal.Decimal]], str], str]:
    """Rounds a number to the specified precision."""

    def function(value):
        try:
            amount = decimal.Decimal(str(value))
            rounded = round(amount, precision)
            return f"{rounded:.{precision}f}"
        except (decimal.InvalidOperation, ValueError):
            return "0"

    return function if data is None else function(data)


def ein(data: str) -> str:
    """Formats a 9-digit EIN as XX-XXXXXXX or returns an empty string if invalid."""
    if data in (None, "None", ""):
        return ""
    cleaned_data = re.sub(r"[^0-9]", "", data)
    match = re.fullmatch(r"\d{9}", cleaned_data)
    return f"{cleaned_data[:2]}-{cleaned_data[2:]}" if match else ""


def to_list(data: Union[str, List]) -> Optional[List]:
    """Converts a single element or JSON-like list string to a list."""
    if data in (None, "None"):
        return None
    if isinstance(data, list):
        return data
    if isinstance(data, str):
        data = data.strip()
        if data.startswith("[") and data.endswith("]"):
            try:
                return ast.literal_eval(data)
            except (SyntaxError, ValueError):
                return None
        else:
            return [data]
    return [data]


def title(data: Optional[str]) -> str:
    """Converts a string to title case."""
    return "" if data in (None, "None") else str(data).title()


def lower(data: Optional[str]) -> str:
    """Converts a string to lowercase."""
    return "" if data in (None, "None") else str(data).lower()


def upper(data: Optional[str]) -> str:
    """Converts a string to uppercase."""
    return "" if data in (None, "None") else str(data).upper()


def padding(length: int, char: str) -> Callable[[str], str]:
    """Returns a function that pads a string to the specified length with the given character."""

    def inner(data: str) -> str:
        return str(data).rjust(length, char) if data not in (None, "None", "") else ""

    return inner


def pprint(data: str) -> str:
    """Pretty-prints a JSON-like string representation of data."""
    try:
        parsed_data = ast.literal_eval(data)
        return pformat(parsed_data)
    except (SyntaxError, ValueError):
        return data


def string(data: Optional[str]) -> str:
    """Converts a None value to an empty string; otherwise returns the string itself."""
    return "" if data is None else str(data)

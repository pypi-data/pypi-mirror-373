import re
import ast
import codecs
import decimal
from decimal import Decimal, ROUND_HALF_UP
from email.utils import parseaddr
from datetime import datetime
from typing import Optional, Union, Callable

# Convert JS data to SQL format for storage


def none(data: str) -> Optional[str]:
    """
    Converts various 'null' representations to None.

    - Now handles 'null', 'None', '@NULL', or empty string as None.
    - Returns the original string otherwise.
    """
    if data.strip().lower() in ("null", "none", "@null", ""):
        return None
    return data


def phone(data: str) -> Optional[str]:
    """
    Attempts to normalize a phone number.

    - Strips all non-digit characters.
    - Accepts 10-digit or 11-digit phone numbers.
      (If 11 digits and starts with '1', we accept the trailing 10 digits).
    - Returns None if the result is not 10 digits after normalization.
    """
    if not data or data.strip().lower() in ("none", "@null"):
        return None
    cleaned_data = re.sub(r"[^0-9]", "", data)
    if len(cleaned_data) == 11 and cleaned_data.startswith("1"):
        cleaned_data = cleaned_data[1:]  # drop leading '1'
    return cleaned_data if len(cleaned_data) == 10 else None


def day_of_week(data: str) -> Optional[int]:
    """
    Converts day of the week to an integer representation (1=Mon,...,7=Sun).

    - Handles both long and short forms: "monday"/"mon", "tuesday"/"tue", etc.
    - Returns None for unrecognized input.
    """
    if not data:
        return None
    days = {
        "monday": 1,
        "mon": 1,
        "tuesday": 2,
        "tue": 2,
        "wednesday": 3,
        "wed": 3,
        "thursday": 4,
        "thu": 4,
        "friday": 5,
        "fri": 5,
        "saturday": 6,
        "sat": 6,
        "sunday": 7,
        "sun": 7,
    }
    return days.get(data.strip().lower())


def date_conv(data: str, fmt: str = "%Y-%m-%d") -> Optional[datetime.date]:
    """
    Parses a date string into a date object using the specified format.

    - Returns None if parsing fails or if 'None' or '@null'.
    """
    data_clean = none(data)  # re-use the none() converter
    if data_clean is None:
        return None
    try:
        return datetime.strptime(data_clean, fmt).date()
    except ValueError:
        return None


def time_conv(data: str, fmt: str = "%H:%M:%S") -> Optional[datetime.time]:
    """
    Parses a time string into a time object using the specified format.

    - Defaults to HH:MM:SS if no format is provided.
    - Returns None if parsing fails or if 'None' or '@null'.
    """
    data_clean = none(data)
    if data_clean is None:
        return None
    try:
        return datetime.strptime(data_clean, fmt).time()
    except ValueError:
        return None


def timestamp(data: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parses a timestamp string into a datetime object using the specified format.

    - Returns None if parsing fails or if 'None' or '@null'.
    - Defaults to "%Y-%m-%d %H:%M:%S".
    """
    data_clean = none(data)
    if data_clean is None:
        return None
    try:
        return datetime.strptime(data_clean, fmt)
    except ValueError:
        return None


def email(data: str) -> Optional[str]:
    """
    Validates and returns a cleaned email address if properly formatted.

    - Uses parseaddr and requires an '@' and at least one '.' after '@'.
    - Returns None if invalid or if 'None'/'@null'.
    - This is still quite basic compared to more advanced email validation needs.
    """
    data_clean = none(data)
    if data_clean is None:
        return None

    data_clean = data_clean.strip().lower()
    # parseaddr only reliably splits out the email part
    addr = parseaddr(data_clean)[1]
    if "@" not in addr:
        return None
    # At least one '.' after the '@'
    domain_part = addr.split("@", 1)[-1]
    if "." not in domain_part:
        return None
    return addr


def integer(data: str) -> Optional[int]:
    """
    Converts a string to an integer, removing non-numeric (and '.') characters.

    - Returns None if conversion fails or if 'None'/'@null'.
    - Accepts optional leading sign and decimal point, but truncates toward int.
    """
    data_clean = none(data)
    if data_clean is None:
        return None

    # Keep digits, sign, and decimal
    cleaned = re.sub(r"[^0-9\.\-+]", "", data_clean)
    if cleaned.count(".") > 1:
        # Too many decimal points => treat as invalid
        return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def boolean(data: Union[str, bool]) -> bool:
    """
    Converts various string representations to a boolean.

    - 'false', '', 'f', 'off', '0', and 'no' => False
    - Everything else => True
    - If data is already bool, it is returned as is.
    """
    if isinstance(data, bool):
        return data
    data_str = str(data).strip().lower()
    if data_str in ["false", "", "f", "off", "0", "no", "@null", "none"]:
        return False
    return True


def rot13(data: str) -> Optional[str]:
    """
    Encodes a string using ROT13.

    - Returns None if input is None or 'None' or '@null'.
    """
    data_clean = none(data)
    if data_clean is None:
        return None
    return codecs.encode(data_clean, "rot13")


def pointer(data: str) -> Optional[int]:
    """
    Converts a pointer-like string to an integer, or returns None for special tokens.

    - If data is '@new', '@null', 'None', or empty => returns None.
    - Otherwise tries to parse as int; returns None if it fails.
    """
    data_clean = none(data)
    if data_clean is None or data_clean.lower() == "@new":
        return None

    # Attempt to parse as integer
    cleaned = re.sub(r"[^0-9\+\-]", "", data_clean)
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def money(data: str) -> Optional[Decimal]:
    """
    Converts a monetary string to a Decimal, removing non-numeric characters.

    - Returns None if 'None' or '@null' or if parse fails.
    - Example input: "$12,345.67" => Decimal("12345.67")
    """
    data_clean = none(data)
    if data_clean is None:
        return None

    cleaned = re.sub(r"[^0-9\.\-]", "", data_clean)
    if cleaned.count(".") > 1:
        return None
    try:
        return Decimal(cleaned)
    except (ValueError, TypeError, decimal.InvalidOperation):
        return None


def round_to(
    precision: int, data: Optional[Union[str, float, Decimal]] = None
) -> Union[Decimal, Callable[[Union[str, float, Decimal]], Optional[Decimal]]]:
    """
    Rounds a number to a specified precision.

    - If called with data, returns a single rounded Decimal or None.
    - If called without data, returns a function that can be used as a converter.
    """

    def _round_inner(val: Union[str, float, Decimal, None]) -> Optional[Decimal]:
        val_str = none(str(val)) if val is not None else None
        if val_str is None:
            return None
        # Remove non-numeric (except decimal, sign)
        cleaned = re.sub(r"[^0-9\.\-+]", "", val_str)
        try:
            as_dec = Decimal(cleaned)
        except (ValueError, TypeError, decimal.InvalidOperation):
            return None
        return as_dec.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)

    return _round_inner(data) if data is not None else _round_inner


def decimal_val(data: str) -> Optional[Decimal]:
    """
    Converts a numeric string to a Decimal, removing non-numeric characters.

    - Returns None if 'None'/'@null' or parse fails.
    - Accepts a single decimal point; returns None if multiple decimals.
    """
    data_clean = none(data)
    if data_clean is None:
        return None
    cleaned = re.sub(r"[^0-9\.\-]", "", data_clean)
    # if multiple decimal points => invalid
    if cleaned.count(".") > 1:
        return None
    try:
        return Decimal(cleaned)
    except (ValueError, TypeError, decimal.InvalidOperation):
        return None


def ein(data: str) -> Optional[str]:
    """
    Validates and returns a 9-digit EIN, or None if invalid.

    - Strips non-digit chars; must be exactly 9 digits.
    """
    data_clean = none(data)
    if data_clean is None:
        return None
    cleaned_data = re.sub(r"[^0-9]", "", data_clean)
    if len(cleaned_data) == 9:
        return cleaned_data
    return None


def to_list(data: Union[str, list, None]) -> Optional[list]:
    """
    Converts a string or single element into a list representation.

    - Returns None for 'None'/'@null' or empty string.
    - If data is already a list, returns it.
    - If data looks like a Python list string, attempts to eval it safely.
    - Otherwise returns a 1-element list with that data.
    """
    if not data or str(data).lower().strip() in ("none", "@null", ""):
        return None
    if isinstance(data, list):
        return data
    data_str = str(data).strip()
    if data_str.startswith("[") and data_str.endswith("]"):
        try:
            return ast.literal_eval(data_str)
        except (ValueError, SyntaxError):
            return [data_str]  # fallback: treat as a single string
    return [data_str]


def title(data: str) -> str:
    """
    Converts a string to title case.

    - Returns empty string if 'None'/'@null' or empty input.
    """
    data_clean = none(data)
    if data_clean is None:
        return ""
    return data_clean.title()


def lower(data: str) -> str:
    """
    Converts a string to lowercase.

    - Returns empty string if 'None'/'@null' or empty input.
    """
    data_clean = none(data)
    if data_clean is None:
        return ""
    return data_clean.lower()


def upper(data: str) -> str:
    """
    Converts a string to uppercase.

    - Returns empty string if 'None'/'@null' or empty input.
    """
    data_clean = none(data)
    if data_clean is None:
        return ""
    return data_clean.upper()


def padding(length: int, char: str = " ") -> Callable[[str], Optional[str]]:
    """
    Pads a string to the specified length with a given character on the left.

    - If data is None/'None'/'@null' or empty, returns None.
    """

    def inner(data: str) -> Optional[str]:
        data_clean = none(data)
        if data_clean is None:
            return None
        return data_clean.rjust(length, char)

    return inner


def string(data: str) -> Optional[str]:
    """
    Converts an empty string to None, otherwise returns the string.

    - Also treats 'None', '@null' as None.
    """
    data_clean = none(data)
    # If none() returned None, it’s None. Else, check if empty.
    if data_clean is None:
        return None
    return data_clean if data_clean else None

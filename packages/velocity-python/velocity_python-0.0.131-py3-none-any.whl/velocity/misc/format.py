import decimal
import json
from typing import Union
from types import FunctionType, MethodType
from datetime import datetime, date, time, timedelta


def gallons(data: Union[None, str, float, decimal.Decimal]) -> str:
    """Converts a value to a string formatted in gallons with two decimal places."""
    if data is None:
        return ""
    try:
        data = decimal.Decimal(data)
        return f"{data:.2f}"
    except (decimal.InvalidOperation, ValueError, TypeError):
        return ""  # Return an empty string for invalid input


def gallons2liters(data: Union[None, str, float, decimal.Decimal]) -> str:
    """Converts gallons to liters and formats with two decimal places."""
    if data is None:
        return ""
    try:
        data = decimal.Decimal(data) * decimal.Decimal("3.78541")
        return f"{data:.2f}"
    except (decimal.InvalidOperation, ValueError, TypeError):
        return ""


def currency(data: Union[None, str, float, decimal.Decimal]) -> str:
    """Formats a value as currency with two decimal places."""
    if data is None:
        return ""
    try:
        data = decimal.Decimal(data)
        return f"{data:.2f}"
    except (decimal.InvalidOperation, ValueError, TypeError):
        return ""


def human_delta(tdelta: timedelta) -> str:
    """Formats a timedelta object into a human-readable format."""
    d = {"days": tdelta.days, "hrs": 0, "min": 0, "sec": 0}
    d["hrs"], rem = divmod(tdelta.seconds, 3600)
    d["min"], d["sec"] = divmod(rem, 60)

    if d["min"] == 0:
        fmt = "{sec} sec"
    elif d["hrs"] == 0:
        fmt = "{min} min {sec} sec"
    elif d["days"] == 0:
        fmt = "{hrs} hr(s) {min} min {sec} sec"
    else:
        fmt = "{days} day(s) {hrs} hr(s) {min} min {sec} sec"

    return fmt.format(**d)


def to_json(o, datefmt: str = "%Y-%m-%d", timefmt: str = "%H:%M:%S") -> str:
    """Serializes an object to JSON, handling special types and reporting any unserializable values."""

    class JsonEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                if hasattr(obj, "to_json"):
                    return obj.to_json()
                if isinstance(obj, decimal.Decimal):
                    return float(obj)
                if isinstance(obj, datetime):
                    return obj.strftime(f"{datefmt} {timefmt}")
                if isinstance(obj, date):
                    return obj.strftime(datefmt)
                if isinstance(obj, time):
                    return obj.strftime(timefmt)
                if isinstance(obj, timedelta):
                    return str(obj)  # Or use human_delta(obj) if preferred
                if isinstance(obj, (FunctionType, MethodType)):
                    return f"WARNING: unserializable: method {getattr(obj, '__name__', 'anonymous')}"
                return f"WARNING: unserializable: {type(obj).__name__}" + (
                    f" ({getattr(obj, '__name__', '')})"
                    if hasattr(obj, "__name__")
                    else ""
                )
            except Exception as e:
                return f"WARNING: failed to serialize {type(obj).__name__}: {e}"

    return json.dumps(o, cls=JsonEncoder, indent=2)

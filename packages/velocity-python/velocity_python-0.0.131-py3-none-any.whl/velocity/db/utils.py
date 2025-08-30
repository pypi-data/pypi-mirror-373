"""
Database utility functions for common operations.

This module provides utility functions to handle common database operations
safely, including sorting with None values and other edge cases.
"""

from typing import Any, Callable, List


def safe_sort_key_none_last(field_name: str) -> Callable[[dict], tuple]:
    """
    Create a sort key function that places None values at the end.

    Args:
        field_name: Name of the field to sort by

    Returns:
        A function suitable for use as a sort key that handles None values

    Example:
        rows = [{"date": "2024-01"}, {"date": None}, {"date": "2023-12"}]
        sorted_rows = sorted(rows, key=safe_sort_key_none_last("date"))
        # Result: [{"date": "2023-12"}, {"date": "2024-01"}, {"date": None}]
    """

    def sort_key(row: dict) -> tuple:
        value = row.get(field_name)
        if value is None:
            return (1, "")  # None values sort last
        return (0, value)

    return sort_key


def safe_sort_key_none_first(field_name: str) -> Callable[[dict], tuple]:
    """
    Create a sort key function that places None values at the beginning.

    Args:
        field_name: Name of the field to sort by

    Returns:
        A function suitable for use as a sort key that handles None values

    Example:
        rows = [{"date": "2024-01"}, {"date": None}, {"date": "2023-12"}]
        sorted_rows = sorted(rows, key=safe_sort_key_none_first("date"))
        # Result: [{"date": None}, {"date": "2023-12"}, {"date": "2024-01"}]
    """

    def sort_key(row: dict) -> tuple:
        value = row.get(field_name)
        if value is None:
            return (0, "")  # None values sort first
        return (1, value)

    return sort_key


def safe_sort_key_with_default(
    field_name: str, default_value: Any = ""
) -> Callable[[dict], Any]:
    """
    Create a sort key function that replaces None values with a default.

    Args:
        field_name: Name of the field to sort by
        default_value: Value to use for None entries

    Returns:
        A function suitable for use as a sort key that handles None values

    Example:
        rows = [{"date": "2024-01"}, {"date": None}, {"date": "2023-12"}]
        sorted_rows = sorted(rows, key=safe_sort_key_with_default("date", "1900-01"))
        # Result: [{"date": None}, {"date": "2023-12"}, {"date": "2024-01"}]
    """

    def sort_key(row: dict) -> Any:
        value = row.get(field_name)
        return default_value if value is None else value

    return sort_key


def safe_sort_rows(
    rows: List[dict],
    field_name: str,
    none_handling: str = "last",
    default_value: Any = "",
    reverse: bool = False,
) -> List[dict]:
    """
    Safely sort a list of dictionaries by a field that may contain None values.

    Args:
        rows: List of dictionaries to sort
        field_name: Name of the field to sort by
        none_handling: How to handle None values - "first", "last", or "default"
        default_value: Default value to use when none_handling is "default"
        reverse: Whether to reverse the sort order

    Returns:
        New list of dictionaries sorted by the specified field

    Raises:
        ValueError: If none_handling is not a valid option

    Example:
        rows = [
            {"name": "Alice", "date": "2024-01"},
            {"name": "Bob", "date": None},
            {"name": "Charlie", "date": "2023-12"}
        ]

        # None values last
        sorted_rows = safe_sort_rows(rows, "date")

        # None values first
        sorted_rows = safe_sort_rows(rows, "date", none_handling="first")

        # Replace None with default
        sorted_rows = safe_sort_rows(rows, "date", none_handling="default",
                                   default_value="1900-01")
    """
    if none_handling == "last":
        key_func = safe_sort_key_none_last(field_name)
    elif none_handling == "first":
        key_func = safe_sort_key_none_first(field_name)
    elif none_handling == "default":
        key_func = safe_sort_key_with_default(field_name, default_value)
    else:
        raise ValueError(
            f"Invalid none_handling option: {none_handling}. "
            "Must be 'first', 'last', or 'default'"
        )

    return sorted(rows, key=key_func, reverse=reverse)


def group_by_fields(rows: List[dict], *field_names: str) -> dict:
    """
    Group rows by one or more field values.

    Args:
        rows: List of dictionaries to group
        *field_names: Names of fields to group by

    Returns:
        Dictionary where keys are tuples of field values and values are lists of rows

    Example:
        rows = [
            {"email": "alice@example.com", "type": "premium", "amount": 100},
            {"email": "alice@example.com", "type": "basic", "amount": 50},
            {"email": "bob@example.com", "type": "premium", "amount": 100},
        ]

        # Group by email only
        groups = group_by_fields(rows, "email")
        # Result: {
        #     ("alice@example.com",): [row1, row2],
        #     ("bob@example.com",): [row3]
        # }

        # Group by email and type
        groups = group_by_fields(rows, "email", "type")
        # Result: {
        #     ("alice@example.com", "premium"): [row1],
        #     ("alice@example.com", "basic"): [row2],
        #     ("bob@example.com", "premium"): [row3]
        # }
    """
    groups = {}
    for row in rows:
        key = tuple(row.get(field) for field in field_names)
        if key not in groups:
            groups[key] = []
        groups[key].append(row)

    return groups


def safe_sort_grouped_rows(
    grouped_rows: dict,
    field_name: str,
    none_handling: str = "last",
    default_value: Any = "",
    reverse: bool = False,
) -> dict:
    """
    Safely sort rows within each group of a grouped result.

    Args:
        grouped_rows: Dictionary of grouped rows (from group_by_fields)
        field_name: Name of the field to sort by within each group
        none_handling: How to handle None values - "first", "last", or "default"
        default_value: Default value to use when none_handling is "default"
        reverse: Whether to reverse the sort order

    Returns:
        Dictionary with the same keys but sorted lists as values

    Example:
        # After grouping payment profiles by email and card number
        groups = group_by_fields(payment_profiles, "email_address", "card_number")

        # Sort each group by expiration date, with None values last
        sorted_groups = safe_sort_grouped_rows(groups, "expiration_date")

        # Now process each sorted group
        for group_key, sorted_group in sorted_groups.items():
            for idx, row in enumerate(sorted_group):
                # Process each row safely
                pass
    """
    result = {}
    for key, rows in grouped_rows.items():
        result[key] = safe_sort_rows(
            rows, field_name, none_handling, default_value, reverse
        )

    return result

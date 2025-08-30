#!/usr/bin/env python3
"""
Test for payment profile sorting with None expiration dates.

This addresses the production error:
TypeError: '<' not supported between instances of 'NoneType' and 'NoneType'

The error occurs when sorting payment profiles by expiration_date when some values are None.
"""

import unittest
from datetime import datetime


class TestPaymentProfileSorting(unittest.TestCase):
    """Test sorting payment profiles with various expiration date scenarios."""

    def setUp(self):
        """Set up test data with various expiration date scenarios."""
        self.payment_profiles = [
            {
                "sys_id": 1,
                "email_address": "test1@example.com",
                "card_number": "1234",
                "expiration_date": "2024-12",
                "status": "active",
            },
            {
                "sys_id": 2,
                "email_address": "test1@example.com",
                "card_number": "1234",
                "expiration_date": "2024-06",
                "status": "active",
            },
            {
                "sys_id": 3,
                "email_address": "test1@example.com",
                "card_number": "1234",
                "expiration_date": None,
                "status": "active",
            },
            {
                "sys_id": 4,
                "email_address": "test1@example.com",
                "card_number": "1234",
                "expiration_date": "2025-01",
                "status": "active",
            },
            {
                "sys_id": 5,
                "email_address": "test1@example.com",
                "card_number": "1234",
                "expiration_date": None,
                "status": "active",
            },
        ]

    def test_original_error_reproduction(self):
        """Reproduce the original error to confirm it happens."""
        with self.assertRaises(TypeError) as context:
            # This should fail with the original error
            sorted(self.payment_profiles, key=lambda x: x["expiration_date"])

        self.assertIn(
            "'<' not supported between instances of 'NoneType'", str(context.exception)
        )

    def test_safe_sorting_with_none_last(self):
        """Test sorting with None values placed at the end."""

        def safe_sort_key_none_last(row):
            """Sort key that places None values at the end."""
            exp_date = row["expiration_date"]
            if exp_date is None:
                return (1, "")  # (1, "") sorts after (0, any_date)
            return (0, exp_date)

        sorted_profiles = sorted(self.payment_profiles, key=safe_sort_key_none_last)

        # Check that non-None dates come first and are in order
        non_none_dates = [
            p["expiration_date"]
            for p in sorted_profiles
            if p["expiration_date"] is not None
        ]
        self.assertEqual(non_none_dates, ["2024-06", "2024-12", "2025-01"])

        # Check that None values come last
        none_dates = [
            p["expiration_date"]
            for p in sorted_profiles
            if p["expiration_date"] is None
        ]
        self.assertEqual(len(none_dates), 2)

        # Verify the full sort order
        expected_order = ["2024-06", "2024-12", "2025-01", None, None]
        actual_order = [p["expiration_date"] for p in sorted_profiles]
        self.assertEqual(actual_order, expected_order)

    def test_safe_sorting_with_none_first(self):
        """Test sorting with None values placed at the beginning."""

        def safe_sort_key_none_first(row):
            """Sort key that places None values at the beginning."""
            exp_date = row["expiration_date"]
            if exp_date is None:
                return (0, "")  # (0, "") sorts before (1, any_date)
            return (1, exp_date)

        sorted_profiles = sorted(self.payment_profiles, key=safe_sort_key_none_first)

        # Check that None values come first
        none_count = sum(1 for p in sorted_profiles[:2] if p["expiration_date"] is None)
        self.assertEqual(none_count, 2)

        # Check that non-None dates come after and are in order
        non_none_dates = [
            p["expiration_date"]
            for p in sorted_profiles
            if p["expiration_date"] is not None
        ]
        self.assertEqual(non_none_dates, ["2024-06", "2024-12", "2025-01"])

    def test_safe_sorting_with_default_date(self):
        """Test sorting with None values replaced by a default date."""

        def safe_sort_key_with_default(row):
            """Sort key that replaces None with a default date."""
            exp_date = row["expiration_date"]
            if exp_date is None:
                return "1900-01"  # Very old date so None values sort first
            return exp_date

        sorted_profiles = sorted(self.payment_profiles, key=safe_sort_key_with_default)

        # Check that None values (now "1900-01") come first
        none_count = sum(1 for p in sorted_profiles[:2] if p["expiration_date"] is None)
        self.assertEqual(none_count, 2)

        # Check the overall order
        actual_order = [p["expiration_date"] for p in sorted_profiles]
        expected_order = [None, None, "2024-06", "2024-12", "2025-01"]
        self.assertEqual(actual_order, expected_order)

    def test_grouped_sorting_scenario(self):
        """Test the specific scenario from the billing handler."""
        # Group profiles by email and card number (as in the original code)
        groups = {}
        for row in self.payment_profiles:
            key = (row["email_address"], row["card_number"])
            if key not in groups:
                groups[key] = []
            groups[key].append(row)

        # Process each group with safe sorting
        for group in groups.values():
            # This should not raise an error
            def safe_sort_key(row):
                exp_date = row["expiration_date"]
                return (exp_date is None, exp_date or "")

            sorted_group = sorted(group, key=safe_sort_key)

            # Verify we can enumerate through the sorted group
            for idx, row in enumerate(sorted_group):
                self.assertIsInstance(idx, int)
                self.assertIn("sys_id", row)
                self.assertIn("expiration_date", row)


def safe_expiration_date_sort_key(row):
    """
    Safe sorting key for payment profiles by expiration date.

    Handles None values by placing them at the end of the sort order.

    Args:
        row: Dictionary representing a payment profile with 'expiration_date' key

    Returns:
        Tuple that can be safely sorted, with None values last
    """
    exp_date = row["expiration_date"]
    if exp_date is None:
        return (1, "")  # (1, "") sorts after (0, any_date)
    return (0, exp_date)


if __name__ == "__main__":
    unittest.main()

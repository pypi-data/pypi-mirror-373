#!/usr/bin/env python3
"""
Tests for database utility functions.
"""

import unittest
from src.velocity.db.utils import (
    safe_sort_key_none_last,
    safe_sort_key_none_first,
    safe_sort_key_with_default,
    safe_sort_rows,
    group_by_fields,
    safe_sort_grouped_rows,
)


class TestDatabaseUtils(unittest.TestCase):
    """Test database utility functions."""

    def setUp(self):
        """Set up test data."""
        self.sample_data = [
            {"id": 1, "name": "Alice", "date": "2024-03", "amount": 100},
            {"id": 2, "name": "Bob", "date": None, "amount": 200},
            {"id": 3, "name": "Charlie", "date": "2024-01", "amount": None},
            {"id": 4, "name": "David", "date": "2024-02", "amount": 150},
            {"id": 5, "name": "Eve", "date": None, "amount": 300},
        ]

    def test_safe_sort_key_none_last(self):
        """Test sorting with None values at the end."""
        sort_key = safe_sort_key_none_last("date")
        sorted_data = sorted(self.sample_data, key=sort_key)

        dates = [row["date"] for row in sorted_data]
        expected = ["2024-01", "2024-02", "2024-03", None, None]
        self.assertEqual(dates, expected)

    def test_safe_sort_key_none_first(self):
        """Test sorting with None values at the beginning."""
        sort_key = safe_sort_key_none_first("date")
        sorted_data = sorted(self.sample_data, key=sort_key)

        dates = [row["date"] for row in sorted_data]
        expected = [None, None, "2024-01", "2024-02", "2024-03"]
        self.assertEqual(dates, expected)

    def test_safe_sort_key_with_default(self):
        """Test sorting with None values replaced by default."""
        sort_key = safe_sort_key_with_default("date", "1900-01")
        sorted_data = sorted(self.sample_data, key=sort_key)

        dates = [row["date"] for row in sorted_data]
        expected = [None, None, "2024-01", "2024-02", "2024-03"]
        self.assertEqual(dates, expected)

    def test_safe_sort_rows_none_last(self):
        """Test safe_sort_rows with none_handling='last'."""
        sorted_data = safe_sort_rows(self.sample_data, "date", none_handling="last")

        dates = [row["date"] for row in sorted_data]
        expected = ["2024-01", "2024-02", "2024-03", None, None]
        self.assertEqual(dates, expected)

    def test_safe_sort_rows_none_first(self):
        """Test safe_sort_rows with none_handling='first'."""
        sorted_data = safe_sort_rows(self.sample_data, "date", none_handling="first")

        dates = [row["date"] for row in sorted_data]
        expected = [None, None, "2024-01", "2024-02", "2024-03"]
        self.assertEqual(dates, expected)

    def test_safe_sort_rows_with_default(self):
        """Test safe_sort_rows with none_handling='default'."""
        sorted_data = safe_sort_rows(
            self.sample_data, "date", none_handling="default", default_value="1900-01"
        )

        dates = [row["date"] for row in sorted_data]
        expected = [None, None, "2024-01", "2024-02", "2024-03"]
        self.assertEqual(dates, expected)

    def test_safe_sort_rows_reverse(self):
        """Test safe_sort_rows with reverse=True."""
        sorted_data = safe_sort_rows(self.sample_data, "date", reverse=True)

        dates = [row["date"] for row in sorted_data]
        expected = [None, None, "2024-03", "2024-02", "2024-01"]
        self.assertEqual(dates, expected)

    def test_safe_sort_rows_invalid_none_handling(self):
        """Test safe_sort_rows with invalid none_handling option."""
        with self.assertRaises(ValueError) as context:
            safe_sort_rows(self.sample_data, "date", none_handling="invalid")

        self.assertIn("Invalid none_handling option", str(context.exception))

    def test_group_by_fields_single_field(self):
        """Test grouping by a single field."""
        # Add data with same names for grouping
        test_data = [
            {"name": "Alice", "type": "A", "value": 1},
            {"name": "Bob", "type": "B", "value": 2},
            {"name": "Alice", "type": "C", "value": 3},
            {"name": "Bob", "type": "A", "value": 4},
        ]

        groups = group_by_fields(test_data, "name")

        self.assertEqual(len(groups), 2)
        self.assertIn(("Alice",), groups)
        self.assertIn(("Bob",), groups)
        self.assertEqual(len(groups[("Alice",)]), 2)
        self.assertEqual(len(groups[("Bob",)]), 2)

    def test_group_by_fields_multiple_fields(self):
        """Test grouping by multiple fields."""
        test_data = [
            {"name": "Alice", "type": "A", "value": 1},
            {"name": "Bob", "type": "B", "value": 2},
            {"name": "Alice", "type": "A", "value": 3},
            {"name": "Alice", "type": "B", "value": 4},
        ]

        groups = group_by_fields(test_data, "name", "type")

        self.assertEqual(len(groups), 3)
        self.assertIn(("Alice", "A"), groups)
        self.assertIn(("Bob", "B"), groups)
        self.assertIn(("Alice", "B"), groups)
        self.assertEqual(len(groups[("Alice", "A")]), 2)
        self.assertEqual(len(groups[("Bob", "B")]), 1)
        self.assertEqual(len(groups[("Alice", "B")]), 1)

    def test_safe_sort_grouped_rows(self):
        """Test sorting rows within groups."""
        # Create grouped data
        test_data = [
            {"group": "A", "date": "2024-03", "value": 1},
            {"group": "A", "date": None, "value": 2},
            {"group": "A", "date": "2024-01", "value": 3},
            {"group": "B", "date": "2024-02", "value": 4},
            {"group": "B", "date": None, "value": 5},
        ]

        groups = group_by_fields(test_data, "group")
        sorted_groups = safe_sort_grouped_rows(groups, "date")

        # Check group A is sorted correctly
        group_a_dates = [row["date"] for row in sorted_groups[("A",)]]
        expected_a = ["2024-01", "2024-03", None]
        self.assertEqual(group_a_dates, expected_a)

        # Check group B is sorted correctly
        group_b_dates = [row["date"] for row in sorted_groups[("B",)]]
        expected_b = ["2024-02", None]
        self.assertEqual(group_b_dates, expected_b)

    def test_payment_profile_scenario(self):
        """Test the specific payment profile scenario that was failing."""
        payment_profiles = [
            {
                "sys_id": 1,
                "email_address": "test@example.com",
                "card_number": "1234",
                "expiration_date": "2024-12",
                "status": "active",
            },
            {
                "sys_id": 2,
                "email_address": "test@example.com",
                "card_number": "1234",
                "expiration_date": "2024-06",
                "status": "active",
            },
            {
                "sys_id": 3,
                "email_address": "test@example.com",
                "card_number": "1234",
                "expiration_date": None,
                "status": "active",
            },
            {
                "sys_id": 4,
                "email_address": "other@example.com",
                "card_number": "5678",
                "expiration_date": "2025-01",
                "status": "active",
            },
            {
                "sys_id": 5,
                "email_address": "other@example.com",
                "card_number": "5678",
                "expiration_date": None,
                "status": "active",
            },
        ]

        # Group by email and card number
        groups = group_by_fields(payment_profiles, "email_address", "card_number")

        # Sort each group by expiration date
        sorted_groups = safe_sort_grouped_rows(groups, "expiration_date")

        # Verify we can safely enumerate through each group
        for group_key, group in sorted_groups.items():
            for idx, row in enumerate(group):
                # This should not raise any errors
                self.assertIsInstance(idx, int)
                self.assertIn("sys_id", row)
                self.assertIn("expiration_date", row)

        # Check specific group sorting
        test_group = sorted_groups[("test@example.com", "1234")]
        exp_dates = [row["expiration_date"] for row in test_group]
        expected = ["2024-06", "2024-12", None]
        self.assertEqual(exp_dates, expected)


if __name__ == "__main__":
    unittest.main()

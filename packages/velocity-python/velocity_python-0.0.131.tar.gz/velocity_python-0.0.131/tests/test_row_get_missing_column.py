#!/usr/bin/env python3
"""
Test to verify that Row.get() handles missing columns gracefully.
"""

import unittest
from unittest.mock import Mock, patch
from velocity.db.core.row import Row
from velocity.db.exceptions import DbColumnMissingError


class TestRowGetMissingColumn(unittest.TestCase):

    def setUp(self):
        """Set up a mock row for testing."""
        # Create a mock table
        self.mock_table = Mock()

        # Create a row instance
        self.row = Row(self.mock_table, {"id": 1})

    def test_get_existing_column(self):
        """Test that get() works normally for existing columns."""
        # Mock the table.get_value to return a normal value
        self.mock_table.get_value.return_value = "test_value"

        result = self.row.get("existing_column")
        self.assertEqual(result, "test_value")

    def test_get_missing_column_with_db_column_missing_error(self):
        """Test that get() returns default when DbColumnMissingError is raised."""
        # Mock the table.get_value to raise DbColumnMissingError
        self.mock_table.get_value.side_effect = DbColumnMissingError(
            'Column "nonexistent" does not exist'
        )

        result = self.row.get("nonexistent", "default_value")
        self.assertEqual(result, "default_value")

    def test_get_missing_column_with_generic_error(self):
        """Test that get() returns default when a generic column error is raised."""
        # Mock the table.get_value to raise a generic exception with column error message
        generic_error = Exception('column "descriptor" does not exist')
        self.mock_table.get_value.side_effect = generic_error

        result = self.row.get("descriptor", "default_value")
        self.assertEqual(result, "default_value")

    def test_get_missing_column_no_default(self):
        """Test that get() returns None when no default is provided."""
        # Mock the table.get_value to raise DbColumnMissingError
        self.mock_table.get_value.side_effect = DbColumnMissingError(
            'Column "nonexistent" does not exist'
        )

        result = self.row.get("nonexistent")
        self.assertIsNone(result)

    def test_get_other_exception_reraises(self):
        """Test that get() re-raises non-column-related exceptions."""
        # Mock the table.get_value to raise a different type of exception
        other_error = Exception("Some other database error")
        self.mock_table.get_value.side_effect = other_error

        with self.assertRaises(Exception) as context:
            self.row.get("some_column")

        self.assertEqual(str(context.exception), "Some other database error")


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import Mock, MagicMock
from velocity.db.core.table import Table
from velocity.db.core.result import Result


class TestCursorRowCountFix(unittest.TestCase):
    """
    Test cases to verify that table methods handle None cursors gracefully
    when accessing result.cursor.rowcount.

    This addresses the AttributeError: 'NoneType' object has no attribute 'rowcount'
    issue that can occur when the cursor is None due to connection errors or
    other exceptional conditions.
    """

    def setUp(self):
        """Set up mock objects for testing."""
        self.mock_tx = Mock()
        self.mock_sql = Mock()
        self.table = Table(self.mock_tx, "test_table")
        self.table.sql = self.mock_sql

    def test_insert_with_none_cursor(self):
        """Test that insert() returns 0 when result.cursor is None."""
        # Mock the SQL generation
        self.mock_sql.insert.return_value = ("INSERT SQL", ["values"])

        # Create a mock result with cursor = None
        mock_result = Mock(spec=Result)
        mock_result.cursor = None

        # Mock the execute method to return our mock result
        self.mock_tx.execute.return_value = mock_result

        # Mock the cursor method
        mock_cursor = Mock()
        self.table.cursor = Mock(return_value=mock_cursor)

        # Call insert and verify it returns 0 instead of raising AttributeError
        result = self.table.insert({"test_field": "test_value"})
        self.assertEqual(result, 0)

    def test_update_with_none_cursor(self):
        """Test that update() returns 0 when result.cursor is None."""
        # Mock the SQL generation
        self.mock_sql.update.return_value = ("UPDATE SQL", ["values"])

        # Create a mock result with cursor = None
        mock_result = Mock(spec=Result)
        mock_result.cursor = None

        # Mock the execute method to return our mock result
        self.mock_tx.execute.return_value = mock_result

        # Mock the cursor method
        mock_cursor = Mock()
        self.table.cursor = Mock(return_value=mock_cursor)

        # Call update and verify it returns 0 instead of raising AttributeError
        result = self.table.update({"test_field": "new_value"}, where={"id": 1})
        self.assertEqual(result, 0)

    def test_merge_with_none_cursor(self):
        """Test that merge() returns 0 when result.cursor is None."""
        # Mock the SQL generation
        self.mock_sql.merge.return_value = ("MERGE SQL", ["values"])

        # Create a mock result with cursor = None
        mock_result = Mock(spec=Result)
        mock_result.cursor = None

        # Mock the execute method to return our mock result
        self.mock_tx.execute.return_value = mock_result

        # Mock the cursor method
        mock_cursor = Mock()
        self.table.cursor = Mock(return_value=mock_cursor)

        # Call merge and verify it returns 0 instead of raising AttributeError
        result = self.table.merge({"test_field": "test_value"})
        self.assertEqual(result, 0)

    def test_delete_with_none_cursor(self):
        """Test that delete() returns 0 when result.cursor is None."""
        # Mock the SQL generation
        self.mock_sql.delete.return_value = ("DELETE SQL", ["values"])

        # Create a mock result with cursor = None
        mock_result = Mock(spec=Result)
        mock_result.cursor = None

        # Mock the execute method to return our mock result
        self.mock_tx.execute.return_value = mock_result

        # Call delete and verify it returns 0 instead of raising AttributeError
        result = self.table.delete(where={"id": 1})
        self.assertEqual(result, 0)

    def test_insert_with_valid_cursor(self):
        """Test that insert() returns rowcount when result.cursor is valid."""
        # Mock the SQL generation
        self.mock_sql.insert.return_value = ("INSERT SQL", ["values"])

        # Create a mock cursor with rowcount
        mock_cursor = Mock()
        mock_cursor.rowcount = 1

        # Create a mock result with valid cursor
        mock_result = Mock(spec=Result)
        mock_result.cursor = mock_cursor

        # Mock the execute method to return our mock result
        self.mock_tx.execute.return_value = mock_result

        # Mock the cursor method
        table_cursor = Mock()
        self.table.cursor = Mock(return_value=table_cursor)

        # Call insert and verify it returns the actual rowcount
        result = self.table.insert({"test_field": "test_value"})
        self.assertEqual(result, 1)

    def test_update_with_valid_cursor(self):
        """Test that update() returns rowcount when result.cursor is valid."""
        # Mock the SQL generation
        self.mock_sql.update.return_value = ("UPDATE SQL", ["values"])

        # Create a mock cursor with rowcount
        mock_cursor = Mock()
        mock_cursor.rowcount = 2

        # Create a mock result with valid cursor
        mock_result = Mock(spec=Result)
        mock_result.cursor = mock_cursor

        # Mock the execute method to return our mock result
        self.mock_tx.execute.return_value = mock_result

        # Mock the cursor method
        table_cursor = Mock()
        self.table.cursor = Mock(return_value=table_cursor)

        # Call update and verify it returns the actual rowcount
        result = self.table.update({"test_field": "new_value"}, where={"id": 1})
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import Mock, MagicMock
from velocity.db.core.result import Result


class TestResultSQLAwareFetch(unittest.TestCase):
    """
    Test cases to verify that Result doesn't attempt to fetch from
    INSERT/UPDATE/DELETE operations, preventing cursor errors.
    """

    def test_insert_sql_no_fetch_attempt(self):
        """Test that INSERT SQL doesn't attempt to fetch rows."""
        mock_cursor = Mock()

        # Create Result with INSERT SQL
        result = Result(
            cursor=mock_cursor, sql="INSERT INTO test (name) VALUES ('test')"
        )

        # Verify fetchone was never called on INSERT
        mock_cursor.fetchone.assert_not_called()

        # Verify result is marked as exhausted (no rows expected)
        self.assertTrue(result._exhausted)
        self.assertTrue(result._first_row_fetched)

        # Verify cursor is still valid (not set to None)
        self.assertIsNotNone(result.cursor)

    def test_update_sql_no_fetch_attempt(self):
        """Test that UPDATE SQL doesn't attempt to fetch rows."""
        mock_cursor = Mock()

        # Create Result with UPDATE SQL
        result = Result(cursor=mock_cursor, sql="UPDATE test SET name='new' WHERE id=1")

        # Verify fetchone was never called on UPDATE
        mock_cursor.fetchone.assert_not_called()

        # Verify result is marked as exhausted (no rows expected)
        self.assertTrue(result._exhausted)
        self.assertIsNotNone(result.cursor)

    def test_delete_sql_no_fetch_attempt(self):
        """Test that DELETE SQL doesn't attempt to fetch rows."""
        mock_cursor = Mock()

        # Create Result with DELETE SQL
        result = Result(cursor=mock_cursor, sql="DELETE FROM test WHERE id=1")

        # Verify fetchone was never called on DELETE
        mock_cursor.fetchone.assert_not_called()

        # Verify result is marked as exhausted (no rows expected)
        self.assertTrue(result._exhausted)
        self.assertIsNotNone(result.cursor)

    def test_select_sql_does_fetch(self):
        """Test that SELECT SQL still attempts to fetch rows."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None  # No rows returned

        # Create Result with SELECT SQL
        result = Result(cursor=mock_cursor, sql="SELECT * FROM test")

        # Verify fetchone WAS called on SELECT
        mock_cursor.fetchone.assert_called_once()

        # Verify result is marked as exhausted (no rows returned)
        self.assertTrue(result._exhausted)
        self.assertIsNotNone(result.cursor)

    def test_select_sql_with_rows(self):
        """Test that SELECT SQL with rows works correctly."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ("test_value",)
        mock_cursor.description = [("column1",)]

        # Create Result with SELECT SQL
        result = Result(cursor=mock_cursor, sql="SELECT column1 FROM test")

        # Verify fetchone WAS called on SELECT
        mock_cursor.fetchone.assert_called_once()

        # Verify result has cached first row and is not exhausted
        self.assertIsNotNone(result._cached_first_row)
        self.assertFalse(result._exhausted)
        self.assertIsNotNone(result.cursor)

    def test_case_insensitive_sql_detection(self):
        """Test that SQL detection works with various cases."""
        test_cases = [
            "insert into test values (1)",  # lowercase
            "INSERT INTO test VALUES (1)",  # uppercase
            "   INSERT INTO test VALUES (1)",  # leading whitespace
            "Insert Into test Values (1)",  # mixed case
            "UPDATE test SET name='x'",  # update
            "delete from test",  # delete
            "TRUNCATE TABLE test",  # truncate
        ]

        for sql in test_cases:
            with self.subTest(sql=sql):
                mock_cursor = Mock()
                result = Result(cursor=mock_cursor, sql=sql)

                # Verify fetchone was never called
                mock_cursor.fetchone.assert_not_called()

                # Verify result is marked as exhausted
                self.assertTrue(result._exhausted)
                self.assertIsNotNone(result.cursor)


if __name__ == "__main__":
    unittest.main()

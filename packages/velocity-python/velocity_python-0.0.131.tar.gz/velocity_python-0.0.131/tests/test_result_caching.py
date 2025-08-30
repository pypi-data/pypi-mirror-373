#!/usr/bin/env python3
"""
Test cases for Result class caching functionality.

Tests the new caching behavior in Result class that pre-fetches the first row
to enable immediate boolean evaluation and accurate state tracking.
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from velocity.db.core.result import Result


class MockCursor:
    """Mock cursor for testing"""

    def __init__(self, rows=None, description=None, raise_on_fetch=False):
        self.rows = rows or []
        self.description = description or [("id",), ("name",)]
        self.position = 0
        self.raise_on_fetch = raise_on_fetch
        self.closed = False

    def fetchone(self):
        if self.closed:
            raise Exception("Cursor is closed")
        if self.raise_on_fetch:
            raise Exception("Simulated cursor error")
        if self.position < len(self.rows):
            row = self.rows[self.position]
            self.position += 1
            return row
        return None

    def fetchall(self):
        if self.closed:
            raise Exception("Cursor is closed")
        remaining = self.rows[self.position :]
        self.position = len(self.rows)
        return remaining

    def close(self):
        self.closed = True


class TestResultCaching(unittest.TestCase):

    def test_empty_result(self):
        """Test with no rows"""
        cursor = MockCursor(rows=[])
        result = Result(cursor)

        self.assertFalse(bool(result))
        self.assertTrue(result.is_empty())
        self.assertFalse(result.has_results())
        self.assertIsNone(result.one())

    def test_single_row(self):
        """Test with one row"""
        cursor = MockCursor(rows=[(1, "Alice")])
        result = Result(cursor)

        self.assertTrue(bool(result))
        self.assertFalse(result.is_empty())
        self.assertTrue(result.has_results())

        row = result.one()
        self.assertEqual(row["id"], 1)
        self.assertEqual(row["name"], "Alice")

    def test_multiple_rows_boolean_state(self):
        """Test that boolean state changes as rows are consumed"""
        cursor = MockCursor(rows=[(1, "Alice"), (2, "Bob"), (3, "Charlie")])
        result = Result(cursor)

        # Initially should be True (has results)
        self.assertTrue(bool(result))
        self.assertTrue(result.has_results())
        self.assertFalse(result.is_empty())

        # Consume first row
        row1 = next(result)
        self.assertEqual(row1["id"], 1)

        # Should still be True (more rows available)
        self.assertTrue(bool(result))
        self.assertTrue(result.has_results())

        # Consume second row
        row2 = next(result)
        self.assertEqual(row2["id"], 2)

        # Should still be True (one more row available)
        self.assertTrue(bool(result))
        self.assertTrue(result.has_results())

        # Consume third row
        row3 = next(result)
        self.assertEqual(row3["id"], 3)

        # Now should be False (no more rows)
        self.assertFalse(bool(result))
        self.assertFalse(result.has_results())
        self.assertTrue(result.is_empty())

        # Trying to get another row should raise StopIteration
        with self.assertRaises(StopIteration):
            next(result)

    def test_scalar_functionality(self):
        """Test scalar functionality"""
        cursor = MockCursor(rows=[(42, "Answer")])
        result = Result(cursor)

        self.assertTrue(bool(result))
        scalar_value = result.scalar()
        self.assertEqual(scalar_value, 42)

        # After scalar(), should be exhausted
        self.assertFalse(bool(result))

    def test_boolean_check_then_iterate(self):
        """Test checking boolean state then iterating"""
        cursor = MockCursor(rows=[(1, "Alice"), (2, "Bob")])
        result = Result(cursor)

        # Check if we have results
        if result:
            rows = list(result)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["id"], 1)
            self.assertEqual(rows[1]["id"], 2)
        else:
            self.fail("Result should have data")

        # After consuming all, should be False
        self.assertFalse(bool(result))

    def test_one_method_exhausts_result(self):
        """Test that one() method marks result as exhausted"""
        cursor = MockCursor(rows=[(1, "Alice"), (2, "Bob")])
        result = Result(cursor)

        self.assertTrue(bool(result))

        row = result.one()
        self.assertEqual(row["id"], 1)

        # After one(), should be exhausted even though there were more rows
        self.assertFalse(bool(result))

    def test_caching_preserves_first_row(self):
        """Test that first row caching doesn't interfere with normal iteration"""
        cursor = MockCursor(rows=[(1, "Alice"), (2, "Bob"), (3, "Charlie")])
        result = Result(cursor)

        # Check boolean state (which triggers first row caching)
        self.assertTrue(bool(result))

        # Iterate through all rows - should get all three
        rows = list(result)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["id"], 1)
        self.assertEqual(rows[1]["id"], 2)
        self.assertEqual(rows[2]["id"], 3)

    def test_multiple_boolean_checks(self):
        """Test multiple boolean checks return consistent results"""
        cursor = MockCursor(rows=[(1, "Alice"), (2, "Bob")])
        result = Result(cursor)

        # Multiple boolean checks should be consistent
        self.assertTrue(bool(result))
        self.assertTrue(result.has_results())
        self.assertFalse(result.is_empty())
        self.assertTrue(bool(result))  # Should still be True

        # Consume one row
        next(result)

        # Should still be True (one more row)
        self.assertTrue(bool(result))
        self.assertTrue(result.has_results())

        # Consume last row
        next(result)

        # Now should be False
        self.assertFalse(bool(result))
        self.assertFalse(result.has_results())
        self.assertTrue(result.is_empty())

    def test_cursor_error_handling(self):
        """Test handling of cursor errors"""
        cursor = MockCursor(rows=[(1, "Alice")], raise_on_fetch=True)
        result = Result(cursor)

        # Should handle cursor error gracefully and return False
        self.assertFalse(bool(result))
        self.assertTrue(result.is_empty())
        self.assertFalse(result.has_results())

    def test_closed_cursor_handling(self):
        """Test handling of operations on closed cursor"""
        cursor = MockCursor(rows=[(1, "Alice"), (2, "Bob")])
        result = Result(cursor)

        # Should work initially
        self.assertTrue(bool(result))

        # Close the result explicitly
        result.close()

        # After closing, result should be exhausted
        self.assertFalse(bool(result))
        self.assertTrue(result.is_empty())
        self.assertFalse(result.has_results())

    def test_scalar_with_cursor_error(self):
        """Test scalar method with cursor errors"""
        cursor = MockCursor(rows=[(42, "Answer")])
        result = Result(cursor)

        # Scalar should work with cached first row
        scalar_value = result.scalar()
        self.assertEqual(scalar_value, 42)

        # Now test with a new result that has cursor error on fresh fetch
        cursor2 = MockCursor(rows=[], raise_on_fetch=True)
        result2 = Result(cursor2)

        # Should return default value gracefully
        scalar_value2 = result2.scalar("default")
        self.assertEqual(scalar_value2, "default")

    def test_columns_property_robustness(self):
        """Test columns property handles missing attributes gracefully"""

        # Create a mock column that behaves like real DB cursor columns
        class MockColumn:
            def __init__(self, name):
                self.name = name

        cursor = MockCursor(rows=[(1, "test")])
        cursor.description = [MockColumn("test_col")]

        result = Result(cursor)
        columns = result.columns

        # Should have at least the column name
        self.assertIn("test_col", columns)
        self.assertIn("type_name", columns["test_col"])
        self.assertEqual(columns["test_col"]["type_name"], "unknown")

    def test_multiple_close_calls(self):
        """Test that multiple close calls don't cause issues"""
        cursor = MockCursor(rows=[(1, "Alice")])
        result = Result(cursor)

        # Get the initial state (cached first row)
        initial_state = bool(result)
        self.assertTrue(initial_state)

        # Multiple close calls should be safe
        result.close()
        result.close()
        result.close()

        # Result should be marked as exhausted after close
        self.assertFalse(bool(result))


if __name__ == "__main__":
    unittest.main()

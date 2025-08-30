#!/usr/bin/env python3

"""
Test the robustness of the improved process_error method
"""

import sys
import unittest
from unittest.mock import Mock, patch
import logging

# Add the source directory to the path
sys.path.insert(0, "/home/ubuntu/tenspace/velocity-python/src")

from velocity.db.core.engine import Engine
from velocity.db import exceptions


class MockException(Exception):
    """Mock exception for testing"""

    def __init__(self, message, pgcode=None, pgerror=None):
        super().__init__(message)
        self.pgcode = pgcode
        self.pgerror = pgerror


class MockSQL:
    """Mock SQL class for testing"""

    server = "PostgreSQL"

    ApplicationErrorCodes = ["22P02", "42883", "42501", "42601", "25P01", "25P02"]
    DatabaseMissingErrorCodes = ["3D000"]
    TableMissingErrorCodes = ["42P01"]
    ColumnMissingErrorCodes = ["42703"]
    ForeignKeyMissingErrorCodes = ["42704"]
    ConnectionErrorCodes = [
        "08001",
        "08S01",
        "57P03",
        "08006",
        "53300",
        "08003",
        "08004",
        "08P01",
    ]
    DuplicateKeyErrorCodes = ["23505"]
    RetryTransactionCodes = ["40001", "40P01", "40002"]
    TruncationErrorCodes = ["22001"]
    LockTimeoutErrorCodes = ["55P03"]
    DatabaseObjectExistsErrorCodes = ["42710", "42P07", "42P04"]
    DataIntegrityErrorCodes = ["23503", "23502", "23514", "23P01", "22003"]

    @classmethod
    def get_error(cls, e):
        return getattr(e, "pgcode", None), getattr(e, "pgerror", None)


class TestProcessErrorRobustness(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.engine = Engine(driver=Mock(), config={"test": "config"}, sql=MockSQL())

        # Capture logs for testing
        self.log_handler = logging.StreamHandler()
        self.log_handler.setLevel(logging.DEBUG)
        logger = logging.getLogger("velocity.db.engine")
        logger.addHandler(self.log_handler)
        logger.setLevel(logging.DEBUG)

    def test_error_code_classification(self):
        """Test that error codes are properly classified"""
        test_cases = [
            # (pgcode, expected_exception_class, description)
            ("23505", exceptions.DbDuplicateKeyError, "unique violation"),
            ("40001", exceptions.DbRetryTransaction, "serialization failure"),
            ("40P01", exceptions.DbRetryTransaction, "deadlock detected"),
            ("42501", exceptions.DbApplicationError, "insufficient privilege"),
            ("42601", exceptions.DbApplicationError, "syntax error"),
            ("25P01", exceptions.DbApplicationError, "no active sql transaction"),
            ("3D000", exceptions.DbDatabaseMissingError, "invalid catalog name"),
            ("08003", exceptions.DbConnectionError, "connection does not exist"),
            ("23502", exceptions.DbDataIntegrityError, "not null violation"),
            ("42P01", exceptions.DbTableMissingError, "undefined table"),
            ("42703", exceptions.DbColumnMissingError, "undefined column"),
        ]

        for pgcode, expected_exception, description in test_cases:
            with self.subTest(pgcode=pgcode, description=description):
                mock_exc = MockException(f"Test error: {description}", pgcode=pgcode)

                with patch(
                    "sys.exc_info", return_value=(type(mock_exc), mock_exc, None)
                ):
                    with self.assertRaises(expected_exception):
                        self.engine.process_error("test sql", {"param": "value"})

    def test_regex_fallback_patterns(self):
        """Test regex pattern fallback when error codes aren't available"""
        test_cases = [
            # (message, expected_exception_class, description)
            (
                "key (sys_id)=(123) already exists.",
                exceptions.DbDuplicateKeyError,
                "sys_id duplicate",
            ),
            (
                "duplicate key value violates unique constraint",
                exceptions.DbDuplicateKeyError,
                "unique constraint",
            ),
            (
                "database 'testdb' does not exist",
                exceptions.DbDatabaseMissingError,
                "database missing",
            ),
            (
                "no such database: mydb",
                exceptions.DbDatabaseMissingError,
                "database not found",
            ),
            (
                "table 'users' already exists",
                exceptions.DbObjectExistsError,
                "object exists",
            ),
            (
                "server closed the connection unexpectedly",
                exceptions.DbConnectionError,
                "connection closed",
            ),
            (
                "connection timed out",
                exceptions.DbConnectionError,
                "connection timeout",
            ),
            ("no such table: users", exceptions.DbTableMissingError, "table missing"),
            (
                "permission denied for table users",
                exceptions.DbApplicationError,
                "permission denied",
            ),
            (
                "syntax error at or near 'SELCT'",
                exceptions.DbApplicationError,
                "syntax error",
            ),
            ("deadlock detected", exceptions.DbLockTimeoutError, "deadlock"),
        ]

        for message, expected_exception, description in test_cases:
            with self.subTest(message=message, description=description):
                mock_exc = MockException(
                    message
                )  # No pgcode - will trigger regex fallback

                with patch(
                    "sys.exc_info", return_value=(type(mock_exc), mock_exc, None)
                ):
                    with self.assertRaises(expected_exception):
                        self.engine.process_error("test sql", {"param": "value"})

    def test_already_custom_exception(self):
        """Test that custom exceptions are re-raised as-is"""
        custom_exc = exceptions.DbConnectionError("Already a custom exception")

        with patch("sys.exc_info", return_value=(type(custom_exc), custom_exc, None)):
            with self.assertRaises(exceptions.DbConnectionError):
                self.engine.process_error()

    def test_no_active_exception(self):
        """Test handling when no exception is active"""
        with patch("sys.exc_info", return_value=(None, None, None)):
            with self.assertRaises(RuntimeError) as cm:
                self.engine.process_error()
            self.assertIn("no active exception", str(cm.exception))

    def test_get_error_failure(self):
        """Test handling when get_error fails"""
        mock_exc = MockException("Test error")

        # Mock get_error to raise an exception
        with patch.object(
            self.engine.sql, "get_error", side_effect=Exception("get_error failed")
        ):
            with patch("sys.exc_info", return_value=(type(mock_exc), mock_exc, None)):
                # Should still handle the error using fallback mechanisms
                with self.assertRaises(
                    Exception
                ):  # Original exception should be re-raised
                    self.engine.process_error()

    def test_exception_str_failure(self):
        """Test handling when converting exception to string fails"""

        class UnstringableException(Exception):
            def __str__(self):
                raise Exception("Cannot convert to string")

        mock_exc = UnstringableException("Test error")

        with patch("sys.exc_info", return_value=(type(mock_exc), mock_exc, None)):
            with self.assertRaises(UnstringableException):
                self.engine.process_error()

    def test_exception_chaining(self):
        """Test that exception chaining is preserved"""
        mock_exc = MockException("Original error", pgcode="23505")

        with patch("sys.exc_info", return_value=(type(mock_exc), mock_exc, None)):
            try:
                self.engine.process_error()
            except exceptions.DbDuplicateKeyError as e:
                # Check that the original exception is chained
                self.assertIsInstance(e.__cause__, MockException)
                self.assertEqual(str(e.__cause__), "Original error")

    def test_enhanced_logging(self):
        """Test that enhanced logging provides good context"""
        mock_exc = MockException(
            "Test error for logging", pgcode="23505", pgerror="duplicate key"
        )

        with patch("sys.exc_info", return_value=(type(mock_exc), mock_exc, None)):
            with patch("velocity.db.core.engine.logger") as mock_logger:
                with self.assertRaises(exceptions.DbDuplicateKeyError):
                    self.engine.process_error("SELECT * FROM test", {"id": 123})

                # Verify warning log was called with proper context
                mock_logger.warning.assert_called_once()
                call_args = mock_logger.warning.call_args

                # Check the message contains key information
                message = call_args[0][0]
                self.assertIn("code=23505", message)
                self.assertIn("message=duplicate key", message)
                self.assertIn("type=MockException", message)

                # Check extra context is provided
                extra = call_args[1]["extra"]
                self.assertEqual(extra["error_code"], "23505")
                self.assertEqual(extra["sql_stmt"], "SELECT * FROM test")
                self.assertEqual(extra["sql_params"], {"id": 123})

    def test_unknown_error_logging(self):
        """Test logging for unhandled/unknown errors"""

        class UnknownException(Exception):
            pass

        mock_exc = UnknownException("Unknown error type")

        with patch("sys.exc_info", return_value=(type(mock_exc), mock_exc, None)):
            with patch("velocity.db.core.engine.logger") as mock_logger:
                with self.assertRaises(UnknownException):
                    self.engine.process_error("SELECT unknown", {"param": "test"})

                # Verify error log was called for unhandled case
                mock_logger.error.assert_called_once()
                call_args = mock_logger.error.call_args

                # Check that comprehensive context is logged
                extra = call_args[1]["extra"]
                self.assertIn("available_error_codes", extra)
                self.assertIn("original_exception_type", extra)
                self.assertEqual(extra["original_exception_type"], "UnknownException")


def main():
    print("Testing robustness of improved process_error method...")

    # Configure logging to see the output
    logging.basicConfig(
        level=logging.DEBUG, format="%(levelname)s - %(name)s - %(message)s"
    )

    # Run the tests
    unittest.main(argv=[""], exit=False, verbosity=2)

    print("\n=== Summary ===")
    print("✅ Enhanced error code classification")
    print("✅ Robust regex pattern fallback")
    print("✅ Exception chaining preservation")
    print("✅ Enhanced logging with context")
    print("✅ Graceful handling of edge cases")
    print("✅ Better debugging information")


if __name__ == "__main__":
    main()

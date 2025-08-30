"""
Database exceptions for the velocity library.
"""


class DbException(Exception):
    """Base class for all database exceptions."""

    pass


class DbApplicationError(DbException):
    """Application-level database error."""

    pass


class DbForeignKeyMissingError(DbException):
    """Foreign key constraint violation."""

    pass


class DbDatabaseMissingError(DbException):
    """Database does not exist."""

    pass


class DbTableMissingError(DbException):
    """Table does not exist."""

    pass


class DbColumnMissingError(DbException):
    """Column does not exist."""

    pass


class DbTruncationError(DbException):
    """Data truncation error."""

    pass


class DbConnectionError(DbException):
    """Database connection error."""

    pass


class DbDuplicateKeyError(DbException):
    """Duplicate key constraint violation."""

    pass


class DbObjectExistsError(DbException):
    """Database object already exists."""

    pass


class DbLockTimeoutError(DbException):
    """Lock timeout error."""

    pass


class DbRetryTransaction(DbException):
    """Transaction should be retried."""

    pass


class DbDataIntegrityError(DbException):
    """Data integrity constraint violation."""

    pass


class DbQueryError(DbException):
    """Database query error."""

    pass


class DbTransactionError(DbException):
    """Database transaction error."""

    pass


class DuplicateRowsFoundError(Exception):
    """Multiple rows found when expecting single result."""

    pass


# Add aliases for backward compatibility with engine.py
class DatabaseError(DbException):
    """Generic database error - alias for DbException."""

    pass


__all__ = [
    # Base exceptions
    "DbException",
    "DatabaseError",
    # Specific exceptions
    "DbApplicationError",
    "DbForeignKeyMissingError",
    "DbDatabaseMissingError",
    "DbTableMissingError",
    "DbColumnMissingError",
    "DbTruncationError",
    "DbConnectionError",
    "DbDuplicateKeyError",
    "DbObjectExistsError",
    "DbLockTimeoutError",
    "DbRetryTransaction",
    "DbDataIntegrityError",
    "DbQueryError",
    "DbTransactionError",
    "DuplicateRowsFoundError",
]

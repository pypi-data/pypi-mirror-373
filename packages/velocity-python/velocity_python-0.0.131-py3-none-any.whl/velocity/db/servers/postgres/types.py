import decimal
import datetime


class TYPES:
    """
    A simple mapping of Python types <-> SQL types (for PostgreSQL).
    """

    TEXT = "TEXT"
    INTEGER = "INTEGER"
    NUMERIC = "NUMERIC"
    DATETIME_TZ = "TIMESTAMP WITH TIME ZONE"
    TIMESTAMP_TZ = "TIMESTAMP WITH TIME ZONE"
    DATETIME = "TIMESTAMP WITHOUT TIME ZONE"
    TIMESTAMP = "TIMESTAMP WITHOUT TIME ZONE"
    DATE = "DATE"
    TIME_TZ = "TIME WITH TIME ZONE"
    TIME = "TIME WITHOUT TIME ZONE"
    BIGINT = "BIGINT"
    SMALLINT = "SMALLINT"
    BOOLEAN = "BOOLEAN"
    BINARY = "BYTEA"
    INTERVAL = "INTERVAL"

    @classmethod
    def get_type(cls, v):
        """
        Returns a suitable SQL type string for a Python value/object.
        """
        if isinstance(v, str) and v.startswith("@@"):
            # e.g. @@CURRENT_TIMESTAMP => special usage
            return v[2:] or cls.TEXT
        if isinstance(v, str) or v is str:
            return cls.TEXT
        if isinstance(v, bool) or v is bool:
            return cls.BOOLEAN
        if isinstance(v, int) or v is int:
            return cls.BIGINT
        if isinstance(v, float) or v is float:
            return f"{cls.NUMERIC}(19, 6)"
        if isinstance(v, decimal.Decimal) or v is decimal.Decimal:
            return f"{cls.NUMERIC}(19, 6)"
        if isinstance(v, datetime.datetime) or v is datetime.datetime:
            return cls.DATETIME
        if isinstance(v, datetime.date) or v is datetime.date:
            return cls.DATE
        if isinstance(v, datetime.time) or v is datetime.time:
            return cls.TIME
        if isinstance(v, datetime.timedelta) or v is datetime.timedelta:
            return cls.INTERVAL
        if isinstance(v, bytes) or v is bytes:
            return cls.BINARY
        return cls.TEXT

    @classmethod
    def get_conv(cls, v):
        """
        Returns a base SQL type for expression usage (e.g. CAST).
        """
        if isinstance(v, str) and v.startswith("@@"):
            return v[2:] or cls.TEXT
        if isinstance(v, str) or v is str:
            return cls.TEXT
        if isinstance(v, bool) or v is bool:
            return cls.BOOLEAN
        if isinstance(v, int) or v is int:
            return cls.BIGINT
        if isinstance(v, float) or v is float:
            return cls.NUMERIC
        if isinstance(v, decimal.Decimal) or v is decimal.Decimal:
            return cls.NUMERIC
        if isinstance(v, datetime.datetime) or v is datetime.datetime:
            return cls.DATETIME
        if isinstance(v, datetime.date) or v is datetime.date:
            return cls.DATE
        if isinstance(v, datetime.time) or v is datetime.time:
            return cls.TIME
        if isinstance(v, datetime.timedelta) or v is datetime.timedelta:
            return cls.INTERVAL
        if isinstance(v, bytes) or v is bytes:
            return cls.BINARY
        return cls.TEXT

    @classmethod
    def py_type(cls, v):
        """
        Returns the Python type that corresponds to an SQL type string.
        """
        v = str(v).upper()
        if v == cls.INTEGER or v == cls.SMALLINT or v == cls.BIGINT:
            return int
        if v == cls.NUMERIC:
            return decimal.Decimal
        if v == cls.TEXT:
            return str
        if v == cls.BOOLEAN:
            return bool
        if v == cls.DATE:
            return datetime.date
        if v == cls.TIME or v == cls.TIME_TZ:
            return datetime.time
        if v == cls.DATETIME or v == cls.TIMESTAMP:
            return datetime.datetime
        if v == cls.INTERVAL:
            return datetime.timedelta
        if v == cls.DATETIME_TZ or v == cls.TIMESTAMP_TZ:
            return datetime.datetime
        raise Exception(f"Unmapped type {v}")

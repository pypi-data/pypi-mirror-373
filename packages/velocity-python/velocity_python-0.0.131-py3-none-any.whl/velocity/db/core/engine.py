import inspect
import re
from functools import wraps
from velocity.db import exceptions
from velocity.db.core.transaction import Transaction

import logging

logger = logging.getLogger("velocity.db.engine")
logger.setLevel(logging.INFO)  # Or DEBUG for more verbosity


class Engine:
    """
    Encapsulates driver config, connection logic, error handling, and transaction decoration.
    """

    MAX_RETRIES = 100

    def __init__(self, driver, config, sql, connect_timeout=5):
        self.__config = config
        self.__sql = sql
        self.__driver = driver
        self.__connect_timeout = connect_timeout

    def __str__(self):
        return f"[{self.sql.server}] engine({self.config})"

    def connect(self):
        """
        Connects to the database and returns the connection object.
        If the database is missing, tries to create it, then reconnect.
        """
        try:
            conn = self.__connect()
        except exceptions.DbDatabaseMissingError:
            self.create_database()
            conn = self.__connect()
        if self.sql.server == "SQLite3":
            conn.isolation_level = None
        return conn

    def __connect(self):
        """
        Internal connection logic, raising suitable exceptions on error.
        Enforces a connect timeout and handles different config types.
        """
        server = self.sql.server.lower()
        timeout_key = "timeout" if "sqlite" in server else "connect_timeout"
        timeout_val = self.__connect_timeout

        try:
            if isinstance(self.config, dict):
                config = self.config.copy()
                if timeout_key not in config:
                    config[timeout_key] = timeout_val
                return self.driver.connect(**config)

            elif isinstance(self.config, str):
                conn_str = self.config
                if timeout_key not in conn_str:
                    conn_str += f" {timeout_key}={timeout_val}"
                return self.driver.connect(conn_str)

            elif isinstance(self.config, (tuple, list)):
                config_args = list(self.config)
                if config_args and isinstance(config_args[-1], dict):
                    if timeout_key not in config_args[-1]:
                        config_args[-1][timeout_key] = timeout_val
                else:
                    config_args.append({timeout_key: timeout_val})
                return self.driver.connect(*config_args)

            else:
                raise TypeError(
                    f"Unhandled configuration parameter type: {type(self.config)}"
                )

        except Exception as e:
            raise self.process_error(e)

    def transaction(self, func_or_cls=None):
        """
        Decorator that provides a Transaction. If `tx` is passed in, uses it; otherwise, creates a new one.
        May also be used to decorate a class, in which case all methods are wrapped in a transaction if they accept `tx`.
        With no arguments, returns a new Transaction directly.
        """
        # print("Transaction", func_or_cls.__name__, type(func_or_cls))

        if func_or_cls is None:
            return Transaction(self)

        if isinstance(func_or_cls, classmethod):
            return classmethod(self.transaction(func_or_cls.__func__))

        if inspect.isfunction(func_or_cls) or inspect.ismethod(func_or_cls):
            names = list(inspect.signature(func_or_cls).parameters.keys())
            # print(func_or_cls.__name__, names)
            if "_tx" in names:
                raise NameError(
                    f"In function {func_or_cls.__name__}, '_tx' is not allowed as a parameter."
                )

            @wraps(func_or_cls)
            def new_function(*args, **kwds):
                tx = None
                names = list(inspect.signature(func_or_cls).parameters.keys())

                # print("inside", func_or_cls.__name__)
                # print(names)
                # print(args, kwds)

                if "tx" not in names:
                    # The function doesn't even declare a `tx` parameter, so run normally.
                    return func_or_cls(*args, **kwds)

                if "tx" in kwds:
                    if isinstance(kwds["tx"], Transaction):
                        tx = kwds["tx"]
                    else:
                        raise TypeError(
                            f"In function {func_or_cls.__name__}, keyword argument `tx` must be a Transaction object."
                        )
                else:
                    # Might be in positional args
                    pos = names.index("tx")
                    if len(args) > pos:
                        if isinstance(args[pos], Transaction):
                            tx = args[pos]

                if tx:
                    return self.exec_function(func_or_cls, tx, *args, **kwds)

                with Transaction(self) as local_tx:
                    pos = names.index("tx")
                    new_args = args[:pos] + (local_tx,) + args[pos:]
                    return self.exec_function(func_or_cls, local_tx, *new_args, **kwds)

            return new_function

        if inspect.isclass(func_or_cls):

            NewCls = type(func_or_cls.__name__, (func_or_cls,), {})

            for attr_name in dir(func_or_cls):
                # Optionally skip special methods
                if attr_name.startswith("__") and attr_name.endswith("__"):
                    continue

                attr = getattr(func_or_cls, attr_name)

                if callable(attr):
                    setattr(NewCls, attr_name, self.transaction(attr))

            return NewCls

        return Transaction(self)

    def exec_function(self, function, _tx, *args, **kwds):
        """
        Executes the given function inside the transaction `_tx`.
        Retries if it raises DbRetryTransaction or DbLockTimeoutError, up to MAX_RETRIES times.
        """
        depth = getattr(_tx, "_exec_function_depth", 0)
        setattr(_tx, "_exec_function_depth", depth + 1)

        try:
            if depth > 0:
                # Not top-level. Just call the function.
                return function(*args, **kwds)
            else:
                retry_count = 0
                lock_timeout_count = 0
                while True:
                    try:
                        return function(*args, **kwds)
                    except exceptions.DbRetryTransaction:
                        retry_count += 1
                        if retry_count > self.MAX_RETRIES:
                            raise
                        _tx.rollback()
                    except exceptions.DbLockTimeoutError:
                        lock_timeout_count += 1
                        if lock_timeout_count > self.MAX_RETRIES:
                            raise
                        _tx.rollback()
                        continue
                    except Exception:
                        raise
        finally:
            setattr(_tx, "_exec_function_depth", depth)
            # or if depth was 0, you might delete the attribute:
            # if depth == 0:
            #     delattr(_tx, "_exec_function_depth")

    @property
    def driver(self):
        return self.__driver

    @property
    def config(self):
        return self.__config

    @property
    def sql(self):
        return self.__sql

    @property
    def version(self):
        """
        Returns the DB server version.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.version()
            return tx.execute(sql, vals).scalar()

    @property
    def timestamp(self):
        """
        Returns the current timestamp from the DB server.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.timestamp()
            return tx.execute(sql, vals).scalar()

    @property
    def user(self):
        """
        Returns the current user as known by the DB server.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.user()
            return tx.execute(sql, vals).scalar()

    @property
    def databases(self):
        """
        Returns a list of available databases.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.databases()
            result = tx.execute(sql, vals)
            return [x[0] for x in result.as_tuple()]

    @property
    def current_database(self):
        """
        Returns the name of the current database.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.current_database()
            return tx.execute(sql, vals).scalar()

    def create_database(self, name=None):
        """
        Creates a database if it doesn't exist, or does nothing if it does.
        """
        old = None
        if name is None:
            old = self.config["database"]
            self.set_config({"database": "postgres"})
            name = old
        with Transaction(self) as tx:
            sql, vals = self.sql.create_database(name)
            tx.execute(sql, vals, single=True)
        if old:
            self.set_config({"database": old})
        return self

    def switch_to_database(self, database):
        """
        Switch the config to use a different database name, closing any existing connection.
        """
        conf = self.config
        if "database" in conf:
            conf["database"] = database
        if "dbname" in conf:
            conf["dbname"] = database
        return self

    def set_config(self, config):
        """
        Updates the internal config dictionary.
        """
        self.config.update(config)

    @property
    def schemas(self):
        """
        Returns a list of schemas in the current database.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.schemas()
            result = tx.execute(sql, vals)
            return [x[0] for x in result.as_tuple()]

    @property
    def current_schema(self):
        """
        Returns the current schema in use.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.current_schema()
            return tx.execute(sql, vals).scalar()

    @property
    def tables(self):
        """
        Returns a list of 'schema.table' for all tables in the current DB.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.tables()
            result = tx.execute(sql, vals)
            return [f"{x[0]}.{x[1]}" for x in result.as_tuple()]

    @property
    def views(self):
        """
        Returns a list of 'schema.view' for all views in the current DB.
        """
        with Transaction(self) as tx:
            sql, vals = self.sql.views()
            result = tx.execute(sql, vals)
            return [f"{x[0]}.{x[1]}" for x in result.as_tuple()]

    def process_error(self, exception, sql=None, parameters=None):
        """
        Central method to parse driver exceptions and re-raise them as our custom exceptions.
        """
        logger = logging.getLogger(__name__)

        # If it's already a velocity exception, just re-raise it
        if isinstance(exception, exceptions.DbException):
            raise exception

        # Get error code and message from the SQL driver
        try:
            error_code, error_message = self.sql.get_error(exception)
        except Exception:
            error_code, error_message = None, str(exception)

        msg = str(exception).strip().lower()

        # Create enhanced error message with SQL query
        enhanced_message = str(exception)
        if sql:
            enhanced_message += (
                f"\n\nSQL Query:\n{self._format_sql_with_params(sql, parameters)}"
            )

        # Format SQL for logging
        formatted_sql_info = ""
        if sql:
            formatted_sql_info = f" sql={self._format_sql_with_params(sql, parameters)}"

        logger.warning(
            "Database error caught. Attempting to transform: code=%s message=%s%s",
            error_code,
            error_message,
            formatted_sql_info,
        )

        # Direct error code mapping
        if error_code in self.sql.ApplicationErrorCodes:
            raise exceptions.DbApplicationError(enhanced_message) from exception
        if error_code in self.sql.ColumnMissingErrorCodes:
            raise exceptions.DbColumnMissingError(enhanced_message) from exception
        if error_code in self.sql.TableMissingErrorCodes:
            raise exceptions.DbTableMissingError(enhanced_message) from exception
        if error_code in self.sql.DatabaseMissingErrorCodes:
            raise exceptions.DbDatabaseMissingError(enhanced_message) from exception
        if error_code in self.sql.ForeignKeyMissingErrorCodes:
            raise exceptions.DbForeignKeyMissingError(enhanced_message) from exception
        if error_code in self.sql.TruncationErrorCodes:
            raise exceptions.DbTruncationError(enhanced_message) from exception
        if error_code in self.sql.DataIntegrityErrorCodes:
            raise exceptions.DbDataIntegrityError(enhanced_message) from exception
        if error_code in self.sql.ConnectionErrorCodes:
            raise exceptions.DbConnectionError(enhanced_message) from exception
        if error_code in self.sql.DuplicateKeyErrorCodes:
            raise exceptions.DbDuplicateKeyError(enhanced_message) from exception
        if error_code in self.sql.DatabaseObjectExistsErrorCodes:
            raise exceptions.DbObjectExistsError(enhanced_message) from exception
        if error_code in self.sql.LockTimeoutErrorCodes:
            raise exceptions.DbLockTimeoutError(enhanced_message) from exception
        if error_code in self.sql.RetryTransactionCodes:
            raise exceptions.DbRetryTransaction(enhanced_message) from exception

        # Regex-based fallback patterns
        if re.search(r"key \(sys_id\)=\(\d+\) already exists.", msg, re.M):
            raise exceptions.DbDuplicateKeyError(enhanced_message) from exception
        if re.findall(r"database.*does not exist", msg, re.M):
            raise exceptions.DbDatabaseMissingError(enhanced_message) from exception
        if re.findall(r"no such database", msg, re.M):
            raise exceptions.DbDatabaseMissingError(enhanced_message) from exception
        if re.findall(r"already exists", msg, re.M):
            raise exceptions.DbObjectExistsError(enhanced_message) from exception
        if re.findall(r"server closed the connection unexpectedly", msg, re.M):
            raise exceptions.DbConnectionError(enhanced_message) from exception
        if re.findall(r"no connection to the server", msg, re.M):
            raise exceptions.DbConnectionError(enhanced_message) from exception
        if re.findall(r"connection timed out", msg, re.M):
            raise exceptions.DbConnectionError(enhanced_message) from exception
        if re.findall(r"could not connect to server", msg, re.M):
            raise exceptions.DbConnectionError(enhanced_message) from exception
        if re.findall(r"cannot connect to server", msg, re.M):
            raise exceptions.DbConnectionError(enhanced_message) from exception
        if re.findall(r"connection already closed", msg, re.M):
            raise exceptions.DbConnectionError(enhanced_message) from exception
        if re.findall(r"cursor already closed", msg, re.M):
            raise exceptions.DbConnectionError(enhanced_message) from exception
        if "no such table:" in msg:
            raise exceptions.DbTableMissingError(enhanced_message) from exception

        logger.error(
            "Unhandled/Unknown Error in engine.process_error",
            exc_info=True,
            extra={
                "error_code": error_code,
                "error_msg": error_message,
                "sql_stmt": sql,
                "sql_params": parameters,
            },
        )

        # If we can't classify it, re-raise with enhanced message
        raise type(exception)(enhanced_message) from exception

    def _format_sql_with_params(self, sql, parameters):
        """
        Format SQL query with parameters merged for easy copy-paste debugging.
        """
        if not sql:
            return "No SQL provided"

        if not parameters:
            return sql

        try:
            # Handle different parameter formats
            if isinstance(parameters, (list, tuple)):
                # Convert parameters to strings and handle None values
                formatted_params = []
                for param in parameters:
                    if param is None:
                        formatted_params.append("NULL")
                    elif isinstance(param, str):
                        # Escape single quotes and wrap in quotes
                        escaped = param.replace("'", "''")
                        formatted_params.append(f"'{escaped}'")
                    elif isinstance(param, bool):
                        formatted_params.append("TRUE" if param else "FALSE")
                    else:
                        formatted_params.append(str(param))

                # Replace %s placeholders with actual values
                formatted_sql = sql
                for param in formatted_params:
                    formatted_sql = formatted_sql.replace("%s", param, 1)

                return formatted_sql

            elif isinstance(parameters, dict):
                # Handle named parameters
                formatted_sql = sql
                for key, value in parameters.items():
                    if value is None:
                        replacement = "NULL"
                    elif isinstance(value, str):
                        escaped = value.replace("'", "''")
                        replacement = f"'{escaped}'"
                    elif isinstance(value, bool):
                        replacement = "TRUE" if value else "FALSE"
                    else:
                        replacement = str(value)

                    # Replace %(key)s or :key patterns
                    formatted_sql = formatted_sql.replace(f"%({key})s", replacement)
                    formatted_sql = formatted_sql.replace(f":{key}", replacement)

                return formatted_sql
            else:
                return f"{sql}\n-- Parameters: {parameters}"

        except Exception as e:
            # If formatting fails, return original SQL with parameters shown separately
            return (
                f"{sql}\n-- Parameters (formatting failed): {parameters}\n-- Error: {e}"
            )

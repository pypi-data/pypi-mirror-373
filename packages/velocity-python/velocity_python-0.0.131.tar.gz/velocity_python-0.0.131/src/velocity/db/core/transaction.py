import traceback

from velocity.db.core.row import Row
from velocity.db.core.table import Table
from velocity.db.core.result import Result
from velocity.db.core.column import Column
from velocity.db.core.database import Database
from velocity.db.core.sequence import Sequence
from velocity.misc.db import randomword

debug = False


class Transaction:
    """
    Encapsulates a single transaction in the database (connection + commit/rollback).
    """

    def __init__(self, engine, connection=None):
        self.engine = engine
        self.connection = connection
        self.__pg_types = {}

    def __str__(self):
        c = self.engine.config
        server = c.get("host", c.get("server"))
        database = c.get("database")
        return f"{self.engine.sql.server}.transaction({server}:{database})"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if debug:
                print("Transaction.__exit__ - an exception occurred.")
                traceback.print_exc()
            self.rollback()
        self.close()

    def cursor(self):
        """
        Retrieves a database cursor, opening a connection if necessary.
        """
        if not self.connection:
            self.connection = self.engine.connect()
        if debug:
            print(f"*** {id(self)} --> transaction.cursor()")
        return self.connection.cursor()

    def close(self):
        """
        Commits (if needed) and closes the connection.
        """
        if self.connection:
            self.commit()
            if debug:
                print(f"<<< {id(self)} close connection.")
            self.connection.close()
            self.connection = None

    def execute(self, sql, parms=None, single=False, cursor=None):
        return self._execute(sql, parms, single, cursor)

    def _execute(self, sql, parms=None, single=False, cursor=None):
        if single:
            cursor = None
        if not self.connection:
            self.connection = self.engine.connect()

        if single:
            self.commit()
            self.connection.autocommit = True

        if not cursor:
            cursor = self.cursor()

        try:
            if parms:
                # print(f"*** {id(self)} --> transaction.execute({sql}, {parms})")
                cursor.execute(sql, parms)
            else:
                cursor.execute(sql)
        except Exception as e:
            raise self.engine.process_error(e, sql, parms)

        if single:
            self.connection.autocommit = False

        return Result(cursor, self, sql, parms)

    def server_execute(self, sql, parms=None):
        """
        Executes SQL using an existing cursor, typically for server-side usage.
        """
        return self._execute(sql, parms, cursor=self.cursor())

    def commit(self):
        """
        Commits the current transaction if there's an open connection.
        """
        if self.connection:
            if debug:
                print(f"{id(self)} --- connection commit.")
            self.connection.commit()

    def rollback(self):
        """
        Rolls back the current transaction if there's an open connection.
        """
        if self.connection:
            if debug:
                print(f"{id(self)} --- connection rollback.")
            self.connection.rollback()

    def create_savepoint(self, sp=None, cursor=None):
        """
        Creates a savepoint named `sp`. If none given, uses a random name.
        """
        if not sp:
            sp = randomword()
        sql, vals = self.engine.sql.create_savepoint(sp)
        if sql:
            self._execute(sql, vals, cursor=cursor)
        return sp

    def release_savepoint(self, sp=None, cursor=None):
        """
        Releases the given savepoint.
        """
        sql, vals = self.engine.sql.release_savepoint(sp)
        if sql:
            self._execute(sql, vals, cursor=cursor)

    def rollback_savepoint(self, sp=None, cursor=None):
        """
        Rolls back to the given savepoint.
        """
        sql, vals = self.engine.sql.rollback_savepoint(sp)
        if sql:
            self._execute(sql, vals, cursor=cursor)

    def database(self, name=None):
        """
        Returns a Database object for the given database name or the current one.
        """
        return Database(self, name)

    def table(self, tablename):
        """
        Returns a Table object for the given table name.
        """
        return Table(self, tablename)

    def sequence(self, name):
        """
        Returns a Sequence object for the given sequence name.
        """
        return Sequence(self, name)

    def row(self, tablename, pk, lock=None):
        """
        Returns a Row for the given table & primary key condition.
        """
        return Row(self.table(tablename), pk, lock=lock)

    def get(self, tablename, where, lock=None):
        """
        Shortcut to table.get().
        """
        return self.table(tablename).get(where, lock=lock)

    def find(self, tablename, where, lock=None):
        """
        Shortcut to table.find().
        """
        return self.table(tablename).find(where, lock=lock)

    def column(self, tablename, colname):
        """
        Returns a Column object for (table=tablename, column=colname).
        """
        return Column(self.table(tablename), colname)

    def current_database(self):
        """
        Returns the current database name from the server.
        """
        sql, vals = self.engine.sql.current_database()
        return self.execute(sql, vals).scalar()

    def tables(self):
        """
        Returns a list of tables in the current database as "schema.table" strings.
        """
        sql, vals = self.engine.sql.tables()
        result = self.execute(sql, vals)
        return [f"{x[0]}.{x[1]}" for x in result.as_tuple()]

    @property
    def pg_types(self):
        """
        Cached mapping of OID -> type name for columns.
        """
        if not self.__pg_types:
            sql = "select oid, typname from pg_type"
            vals = ()
            result = self.execute(sql, vals)
            self.__pg_types = dict(result.as_tuple())
        return self.__pg_types

    def switch_to_database(self, name):
        """
        Closes the current connection, changes config, and lazily reconnects for the new DB.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
        self.engine.switch_to_database(name)
        return self

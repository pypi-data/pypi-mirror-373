import sqlparse
from velocity.db import exceptions
from velocity.db.core.row import Row
from velocity.db.core.result import Result
from velocity.db.core.column import Column
from velocity.db.core.decorators import (
    return_default,
    create_missing,
    reset_id_on_dup_key,
)


class Query:
    """
    A utility class to store raw SQL and parameters without immediately executing.
    """

    def __init__(self, sql, params=()):
        self.sql = sqlparse.format(sql, reindent=True, keyword_case="upper")
        self.params = tuple(params)

    def __str__(self):
        return self.sql


class Table:
    """
    Provides an interface for performing CRUD and metadata operations on a DB table.
    """

    def __init__(self, tx, name):
        self.tx = tx
        self.name = name.lower()
        self.sql = tx.engine.sql

    def __str__(self):
        return (
            f"Table: {self.name}\n"
            f"(table exists) {self.exists()}\n"
            f"Columns: {len(self.columns())}\n"
            f"Rows: {len(self)}\n"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.close()

    def close(self):
        """
        Closes the internal cursor if we have one open.
        """
        try:
            self._cursor.close()
        except Exception:
            pass

    def cursor(self):
        try:
            return self._cursor
        except AttributeError:
            pass
        self._cursor = self.tx.cursor()
        return self._cursor

    def __call__(self, where=None):
        """
        Generator: SELECT rows matching the `where` condition.
        """
        sql, val = self.sql.select(self.tx, table=self.name, where=where)
        for data in self.tx.execute(sql, val):
            yield self.row(data)

    def __iter__(self):
        """
        Iterate over all rows in ascending order by sys_id.
        """
        sql, val = self.sql.select(self.tx, table=self.name, orderby="sys_id")
        for data in self.tx.execute(sql, val):
            yield self.row(data)

    def sys_columns(self, **kwds):
        """
        Returns the raw list of columns, possibly skipping any additional system columns logic.
        """
        sql, vals = self.sql.columns(self.name)
        if kwds.get("sql_only", False):
            return sql, vals
        result = self.tx.execute(sql, vals, cursor=self.cursor())
        return [x[0] for x in result.as_tuple()]

    def columns(self):
        """
        Returns column names, excluding columns that start with 'sys_'.
        """
        return [col for col in self.sys_columns() if not col.startswith("sys_")]

    @return_default(None, (exceptions.DbObjectExistsError,))
    def create_index(
        self, columns, unique=False, direction=None, where=None, lower=None, **kwds
    ):
        """
        Creates an index on the given columns. Returns None on success, or `None` if the index already exists.
        If the object already exists, this function will return without raising an error, but the exisitng
        index may have been created with different parameters.
        """
        sql, vals = self.sql.create_index(
            self.tx,
            table=self.name,
            columns=columns,
            unique=unique,
            direction=direction,
            where=where,
            lower=lower,
        )
        if kwds.get("sql_only", False):
            return sql, vals
        self.tx.execute(sql, vals, cursor=self.cursor())

    @return_default(None)
    def drop_index(self, columns, **kwds):
        """
        Drops an index for the specified columns.
        """
        sql, vals = self.sql.drop_index(self.name, columns)
        if kwds.get("sql_only", False):
            return sql, vals
        self.tx.execute(sql, vals, cursor=self.cursor())

    @return_default(None)
    def drop_column(self, column):
        """
        Drops a column from this table.
        """
        sql, vals = self.sql.drop_column(self.name, column)
        self.tx.execute(sql, vals, cursor=self.cursor())

    def create(self, columns=None, drop=False):
        """
        Creates this table with system columns plus the given `columns` dictionary.
        Optionally drops any existing table first.
        """
        columns = columns or {}
        sql, vals = self.sql.create_table(self.name, columns, drop)
        self.tx.execute(sql, vals, cursor=self.cursor())

    def drop(self):
        """
        Drops this table if it exists.
        """
        sql, vals = self.sql.drop_table(self.name)
        self.tx.execute(sql, vals, cursor=self.cursor())

    def exists(self):
        """
        Returns True if this table already exists in the DB.
        """
        sql, vals = self.sql.tables()
        result = self.tx.execute(sql, vals, cursor=self.cursor())
        if "." in self.name:
            return self.name in [f"{x[0]}.{x[1]}" for x in result.as_tuple()]
        return self.name in [x[1] for x in result.as_tuple()]

    def column(self, name):
        """
        Returns a Column object for the given column name.
        """
        return Column(self, name)

    def row(self, key=None, lock=None):
        """
        Retrieves a Row instance for the given primary key or conditions dict. If `key` is None, returns a new row.
        """
        if key is None:
            return self.new(lock=lock)
        return Row(self, key, lock=lock)

    def dict(self, key):
        """
        Returns a row as a dictionary or empty dict if not found.
        """
        r = self.find(key)
        return r.to_dict() if r else {}

    def rows(self, where=None, orderby=None, qty=None, lock=None, skip_locked=None):
        """
        Generator that yields Row objects matching `where`, up to `qty`.
        """
        for key in self.ids(
            where=where, orderby=orderby, qty=qty, lock=lock, skip_locked=skip_locked
        ):
            yield Row(self, key, lock=lock)

    def ids(
        self,
        where=None,
        orderby=None,
        groupby=None,
        having=None,
        start=None,
        qty=None,
        lock=None,
        skip_locked=None,
    ):
        """
        Returns a generator of sys_id values for rows matching `where`.
        """
        results = self.select(
            "sys_id",
            where=where,
            orderby=orderby,
            groupby=groupby,
            having=having,
            start=start,
            qty=qty,
            lock=lock,
            skip_locked=skip_locked,
        )
        for key in results:
            yield key["sys_id"]

    def set_id(self, start):
        """
        Sets the sequence for this table's sys_id to the given start value.
        """
        sql, vals = self.sql.set_id(self.name, start)
        self.tx.execute(sql, vals, cursor=self.cursor())

    def new(self, data=None, lock=None):
        """
        Inserts a new row with the given data and returns a Row object. If data is None, sets sys_modified automatically.
        """
        if data is None:
            data = {"sys_modified": "@@CURRENT_TIMESTAMP"}
        if len(data) == 1 and "sys_id" in data:
            return self.row(data, lock=lock).touch()
        self.insert(data)
        sql, vals = self.sql.last_id(self.name)
        sys_id = self.tx.execute(sql, vals).scalar()
        return self.row(sys_id, lock=lock)

    def get(self, where, lock=None, use_where=False):
        """
        Gets or creates a row matching `where`. If multiple rows match, raises DuplicateRowsFoundError.
        If none match, a new row is created with the non-operator aspects of `where`.
        """
        if where is None:
            raise Exception("None is not allowed as a primary key.")
        if isinstance(where, int):
            where = {"sys_id": where}
        result = self.select("sys_id", where=where, lock=lock).all()
        if len(result) > 1:
            sql = self.select("sys_id", sql_only=True, where=where, lock=lock)
            raise exceptions.DuplicateRowsFoundError(
                f"More than one entry found. {sql}"
            )
        if not result:
            new_data = where.copy()
            for k in list(new_data.keys()):
                if set("<>!=%").intersection(k):
                    new_data.pop(k)
            return self.new(new_data, lock=lock)
        if use_where:
            return Row(self, where, lock=lock)
        return Row(self, result[0]["sys_id"], lock=lock)

    @return_default(None)
    def find(self, where, lock=None, use_where=False):
        """
        Finds a single row matching `where`, or returns None if none found.
        Raises DuplicateRowsFoundError if multiple rows match.
        """
        if where is None:
            raise Exception("None is not allowed as a primary key.")
        if isinstance(where, int):
            where = {"sys_id": where}
        result = self.select("sys_id", where=where, lock=lock).all()
        if not result:
            return None
        if len(result) > 1:
            sql = self.select("sys_id", sql_only=True, where=where, lock=lock)
            raise exceptions.DuplicateRowsFoundError(
                f"More than one entry found. {sql}"
            )
        if use_where:
            return Row(self, where, lock=lock)
        return Row(self, result[0]["sys_id"], lock=lock)

    one = find

    @return_default(None)
    def first(
        self,
        where,
        orderby=None,
        create_new=False,
        lock=None,
        skip_locked=None,
        use_where=False,
    ):
        """
        Finds the first matching row (by `orderby`) or creates one if `create_new=True` and none found.
        """
        if where is None:
            raise Exception("None is not allowed as a where clause.")
        if isinstance(where, int):
            where = {"sys_id": where}
        results = self.select(
            "sys_id", where=where, orderby=orderby, skip_locked=skip_locked
        ).all()
        if not results:
            if create_new:
                new_data = where.copy()
                for k in list(new_data.keys()):
                    if set("<>!=%").intersection(k):
                        new_data.pop(k)
                return self.new(new_data, lock=lock)
            return None
        if use_where:
            return Row(self, where, lock=lock)
        return Row(self, results[0]["sys_id"], lock=lock)

    def primary_keys(self):
        """
        Returns the list of primary key columns for this table.
        """
        sql, vals = self.sql.primary_keys(self.name)
        result = self.tx.execute(sql, vals, cursor=self.cursor())
        return [x[0] for x in result.as_tuple()]

    def foreign_keys(self):
        """
        Returns the list of foreign key columns for this table (may be incomplete).
        """
        sql, vals = self.sql.primary_keys(self.name)
        result = self.tx.execute(sql, vals, cursor=self.cursor())
        return [x[0] for x in result.as_tuple()]

    def foreign_key_info(self, column, **kwds):
        """
        Returns info about a foreign key for the specified column.
        """
        sql, vals = self.sql.foreign_key_info(table=self.name, column=column)
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals, cursor=self.cursor()).one()

    @return_default()
    def create_foreign_key(
        self, columns, key_to_table, key_to_columns="sys_id", **kwds
    ):
        """
        Creates a foreign key referencing `key_to_table(key_to_columns)`.
        """
        sql, vals = self.sql.create_foreign_key(
            self.name, columns, key_to_table, key_to_columns
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals, cursor=self.cursor())

    def drop_foreign_key(self, columns, key_to_table, key_to_columns="sys_id", **kwds):
        """
        Drops the specified foreign key constraint.
        """
        sql, vals = self.sql.create_foreign_key(
            self.name, columns, key_to_table, key_to_columns
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals, cursor=self.cursor())

    def rename(self, name, **kwds):
        """
        Renames this table.
        """
        sql, vals = self.sql.rename_table(self.name, name)
        if kwds.get("sql_only", False):
            return sql, vals
        self.tx.execute(sql, vals, cursor=self.cursor())
        self.name = name

    def lower_keys(self, arg):
        """
        Returns a copy of the dict `arg` with all keys lowercased.
        """
        new = {}
        if isinstance(arg, dict):
            for key, val in arg.items():
                new[key.lower()] = val
        return new

    @create_missing
    def alter(self, columns, **kwds):
        """
        Adds any missing columns (based on the provided dict) to the table.
        """
        if not isinstance(columns, dict):
            raise Exception("Columns must be a dict.")
        columns = self.lower_keys(columns)
        diff = []
        for k in columns.keys():
            if k not in self.sys_columns():
                diff.append(k)
        if diff:
            newcols = {key: columns[key] for key in diff}
            sql, vals = self.sql.alter_add(self.name, newcols)
            if kwds.get("sql_only", False):
                return sql, vals
            self.tx.execute(sql, vals, cursor=self.cursor())

    @create_missing
    def alter_type(self, column, type_or_value, nullable=True, **kwds):
        """
        Alters the specified column to match a new SQL type (inferred from `type_or_value`).
        """
        sql, vals = self.sql.alter_column_by_type(
            self.name, column, type_or_value, nullable
        )
        if kwds.get("sql_only", False):
            return sql, vals
        self.tx.execute(sql, vals, cursor=self.cursor())

    @create_missing
    def update(self, data, where=None, pk=None, **kwds):
        """
        Performs an UPDATE of rows matching `where` or `pk` with `data`.
        """
        sql, vals = self.sql.update(self.tx, self.name, data, where, pk)
        if kwds.get("sql_only", False):
            return sql, vals
        result = self.tx.execute(sql, vals, cursor=self.cursor())
        return result.cursor.rowcount if result.cursor else 0

    @reset_id_on_dup_key
    @create_missing
    def insert(self, data, **kwds):
        """
        Performs an INSERT of the given data into this table. Resets sys_id on duplicate keys if needed.
        """
        sql, vals = self.sql.insert(self.name, data)
        if kwds.get("sql_only", False):
            return sql, vals
        result = self.tx.execute(sql, vals, cursor=self.cursor())
        return result.cursor.rowcount if result.cursor else 0

    @reset_id_on_dup_key
    @create_missing
    def merge(self, data, pk=None, **kwds):
        """
        Implements an UPSERT (merge) with conflict handling on pk columns.
        """
        sql, vals = self.sql.merge(
            self.tx,
            self.name,
            data,
            pk,
            on_conflict_do_nothing=False,
            on_conflict_update=True,
        )
        if kwds.get("sql_only", False):
            return sql, vals
        result = self.tx.execute(sql, vals, cursor=self.cursor())
        return result.cursor.rowcount if result.cursor else 0

    upsert = merge
    indate = merge

    @return_default(0)
    def count(self, where=None, **kwds):
        """
        Returns the count of rows matching `where`.
        """
        sql, vals = self.sql.select(
            self.tx, columns="count(*)", table=self.name, where=where
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals, cursor=self.cursor()).scalar()

    @return_default(0)
    def sum(self, column, where=None, **kwds):
        """
        Returns the sum of the given column across rows matching `where`.
        """
        sql, vals = self.sql.select(
            self.tx,
            columns=f"coalesce(sum(coalesce({column},0)),0)",
            table=self.name,
            where=where,
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals, cursor=self.cursor()).scalar()

    @return_default(0)
    def __len__(self):
        """
        Returns count of all rows in the table.
        """
        sql, vals = self.sql.select(self.tx, columns="count(*)", table=self.name)
        return self.tx.execute(sql, vals, cursor=self.cursor()).scalar()

    @return_default(Result())
    def select(
        self,
        columns=None,
        where=None,
        orderby=None,
        groupby=None,
        having=None,
        start=None,
        qty=None,
        lock=None,
        skip_locked=None,
        **kwds,
    ):
        """
        Performs a SELECT query, returning a Result object (defaults to as_dict() transform).
        """
        sql, vals = self.sql.select(
            self.tx,
            columns=columns,
            table=self.name,
            where=where,
            orderby=orderby,
            groupby=groupby,
            having=having,
            start=start,
            qty=qty,
            lock=lock,
            skip_locked=skip_locked,
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals)

    def list(self, *args, **kwds):
        """
        Shortcut to run a SELECT and retrieve .all() in a single call.
        """
        if kwds.get("sql_only", False):
            raise Exception("sql_only is not supported for list queries")
        return self.select(*args, **kwds).all()

    def query(
        self,
        columns=None,
        where=None,
        orderby=None,
        groupby=None,
        having=None,
        start=None,
        qty=None,
        lock=None,
        skip_locked=None,
    ):
        """
        Returns a Query object suitable for usage in sub-queries, etc.
        """
        sql, vals = self.sql.select(
            self.tx,
            columns=columns,
            table=self.name,
            where=where,
            orderby=orderby,
            groupby=groupby,
            having=having,
            start=start,
            qty=qty,
            lock=lock,
            skip_locked=skip_locked,
        )
        if vals:
            # Not supporting dictionary-based 'where' in raw Query usage.
            raise Exception("A query generator does not support dictionary-type WHERE.")
        return Query(sql)

    @return_default(Result())
    def server_select(
        self,
        columns=None,
        where=None,
        orderby=None,
        groupby=None,
        having=None,
        start=None,
        qty=None,
        lock=None,
        skip_locked=None,
        **kwds,
    ):
        """
        Similar to select(), but calls server_execute() instead of execute().
        """
        sql, vals = self.sql.select(
            self.tx,
            columns=columns,
            table=self.name,
            where=where,
            orderby=orderby,
            groupby=groupby,
            having=having,
            start=start,
            qty=qty,
            lock=lock,
            skip_locked=skip_locked,
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.server_execute(sql, vals)

    @return_default(Result())
    def batch(self, size=100, *args, **kwds):
        """
        Generator that yields batches of rows (lists) of size `size`.
        """
        if kwds.get("sql_only", False):
            raise Exception("sql_only is not supported for batch queries")
        current = 0
        while True:
            kwds["start"] = current
            kwds["qty"] = size
            results = self.select(*args, **kwds).all()
            if results:
                yield results
                current += len(results)
            else:
                raise StopIteration

    def get_value(self, key, pk):
        """
        Returns a single scalar value of `key` for the row matching `pk`.
        """
        return self.select(columns=key, where=pk).scalar()

    @return_default({})
    def get_row(self, where, lock=None, **kwds):
        """
        Retrieves a single row as dict or an empty dict if none found.
        """
        if not where:
            raise Exception("Unique key for the row to be retrieved is required.")
        sql, vals = self.sql.select(
            self.tx, columns="*", table=self.name, where=where, lock=lock
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals, cursor=self.cursor()).one()

    @return_default(0)
    def delete(self, where, **kwds):
        """
        Deletes rows matching `where`. Raises Exception if `where` is falsy.
        """
        if not where:
            raise Exception(
                "You just tried to delete an entire table. Use `truncate` instead."
            )
        sql, vals = self.sql.delete(tx=self.tx, table=self.name, where=where)
        if kwds.get("sql_only", False):
            return sql, vals
        result = self.tx.execute(sql, vals)
        return result.cursor.rowcount if result.cursor else 0

    def truncate(self, **kwds):
        """
        Truncates this table (removes all rows).
        """
        sql, vals = self.sql.truncate(table=self.name)
        if kwds.get("sql_only", False):
            return sql, vals
        self.tx.execute(sql, vals)

    def duplicate_rows(self, columns=None, where=None, orderby=None, **kwds):
        """
        Returns rows that have duplicates in the specified `columns`.
        TBD: Move code to generate sql to the sql module. it should not be
        here so different sql engines can use this function.
        """
        if not columns:
            raise ValueError(
                "You must specify at least one column to check for duplicates."
            )
        sql, vals = self.sql.select(
            self.tx,
            columns=columns,
            table=self.name,
            where=where,
            groupby=columns,
            having={">count(*)": 1},
        )
        if orderby:
            orderby = [orderby] if isinstance(orderby, str) else orderby
        else:
            orderby = columns
        subjoin = " AND ".join([f"t.{col} = dup.{col}" for col in columns])
        ob = ", ".join(orderby)
        final_sql = f"""
        SELECT t.*
        FROM {self.name} t
        JOIN ({sql}) dup
        ON {subjoin}
        ORDER BY {ob}
        """
        if kwds.get("sql_only", False):
            return final_sql, vals
        return self.tx.execute(final_sql, vals)

    def has_duplicates(self, columns=None, where=None, **kwds):
        """
        Returns True if there are duplicates in the specified columns, else False.
        """
        if not columns:
            raise ValueError(
                "You must specify at least one column to check for duplicates."
            )
        sql, vals = self.sql.select(
            self.tx,
            columns=["1"],
            table=self.name,
            where=where,
            groupby=columns,
            having={">count(*)": 1},
            qty=1,
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return bool(self.tx.execute(sql, vals).scalar())

    def create_view(self, name, query, temp=False, silent=True, **kwds):
        """
        Creates (or replaces) a view.
        """
        sql, vals = self.sql.create_view(
            name=name, query=query, temp=temp, silent=silent
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals)

    def drop_view(self, name, silent=True, **kwds):
        """
        Drops a view.
        """
        sql, vals = self.sql.drop_view(name=name, silent=silent)
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals)

    def alter_trigger(self, name="USER", state="ENABLE", **kwds):
        """
        Alters a trigger's state on this table.
        """
        sql, vals = self.sql.alter_trigger(table=self.name, state=state, name=name)
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals)

    def rename_column(self, orig, new, **kwds):
        """
        Renames a column in this table.
        """
        sql, vals = self.sql.rename_column(table=self.name, orig=orig, new=new)
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals)

    def set_sequence(self, next_value=1000, **kwds):
        """
        Sets the next value of the table's sys_id sequence.
        """
        sql, vals = self.sql.set_sequence(table=self.name, next_value=next_value)
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals).scalar()

    def get_sequence(self, **kwds):
        """
        Returns the current value of the table's sys_id sequence.
        """
        sql, vals = self.sql.current_id(table=self.name)
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals).scalar()

    def missing(self, list_, column="sys_id", where=None, **kwds):
        """
        Given a list of IDs, returns which ones are missing from this table's `column` (defaults to sys_id).
        """
        sql, vals = self.sql.missing(
            tx=self.tx, table=self.name, list=list_, column=column, where=where
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals).as_simple_list().all()

    def lock(self, mode="ACCESS EXCLUSIVE", wait_for_lock=None, **kwds):
        """
        Issues a LOCK TABLE statement for this table.
        TBD: MOve SQL To sql module so we can use this function with other engines.
        """
        sql = f"LOCK TABLE {self.name} IN {mode} MODE"
        if not wait_for_lock:
            sql += " NOWAIT"
        vals = None
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals)

    @return_default(0)
    def max(self, column, where=None, **kwds):
        """
        Returns the MAX() of the specified column.
        """
        sql, vals = self.sql.select(
            self.tx, columns=f"max({column})", table=self.name, where=where
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals, cursor=self.cursor()).scalar()

    @return_default(0)
    def min(self, column, where=None, **kwds):
        """
        Returns the MIN() of the specified column.
        """
        sql, vals = self.sql.select(
            self.tx, columns=f"min({column})", table=self.name, where=where
        )
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals, cursor=self.cursor()).scalar()

    @return_default(None)
    def newest(self, where=None, **kwds):
        """
        Returns the row with the highest sys_created value.
        """
        return self.first(where=where, orderby="sys_modified  DESC, sys_id DESC")

    @return_default(None)
    def oldest(self, where=None, **kwds):
        """
        Returns the row with the lowest sys_created value.
        """
        return self.first(where=where, orderby="sys_modified  ASC, sys_id ASC")

    def indexes(self, **kwds):
        """
        Returns detailed information about all indexes on this table.
        """
        sql, vals = self.sql.indexes(self.name)
        if kwds.get("sql_only", False):
            return sql, vals
        return self.tx.execute(sql, vals, cursor=self.cursor())

    def compare_rows(self, pk1, pk2):
        """
        Compares two rows in the given table identified by their primary keys.

        Parameters:
        table (Table): An instance of the Table class.
        pk1: Primary key of the first row.
        pk2: Primary key of the second row.

        Returns:
        A string that lists differences between the two rows. If no differences,
        returns "Rows are identical."
        """
        # Retrieve rows based on primary keys.
        data1 = self.row(pk1).to_dict()
        data2 = self.row(pk2).to_dict()

        differences = []

        # Iterate through each column in the table (ignoring system columns).
        for col in self.columns():
            val1 = data1.get(col)
            val2 = data2.get(col)

            if val1 != val2:
                differences.append(f"{col}: {val1} vs {val2}")

        # Return a descriptive string of differences.
        if differences:
            differences.insert(0, f"Comparing {self.name}: {pk1} vs {pk2}")
            differences.insert(0, "--------------------------------------")
            differences.append("--------------------------------------")
            return "\n".join(differences)
        else:
            return f"{self.name} rows {pk1} and {pk2} are identical."

    def interactive_merge_rows(self, left_pk, right_pk):
        """
        Interactively merge two rows from this table.

        For each non-primary key column where the two rows differ, you'll be prompted to choose
        whether you want the left or right value. After all choices are made, the merged row
        is displayed for confirmation. If confirmed, the left row is updated with the chosen values.
        Optionally, you can also choose to delete the right row.

        Parameters:
        left_pk: Primary key of the left (destination) row.
        right_pk: Primary key of the right (source) row.
        """
        # Retrieve both rows and convert to dictionaries
        left_row = self.row(left_pk)
        right_row = self.row(right_pk)

        left_data = left_row.to_dict()
        right_data = right_row.to_dict()

        # Get primary key columns to skip them in the merge.
        pk_columns = self.primary_keys()

        merged_values = {}

        print("Comparing rows:\n")
        # Iterate through all non-primary key columns.
        for col in self.columns():
            if col in pk_columns:
                continue  # Do not compare or merge primary key columns.

            left_val = left_data.get(col)
            right_val = right_data.get(col)

            # If values are the same, simply use one of them.
            if left_val == right_val:
                merged_values[col] = left_val
            else:
                print(f"Column: '{col}'")
                print(f"  Left value:  `{left_val}`       Right value: `{right_val}`")
                choice = None
                # Prompt until a valid choice is provided.
                while choice not in ("L", "R"):
                    choice = (
                        input("Choose which value to use (L for left, R for right): ")
                        .strip()
                        .upper()
                    )
                merged_values[col] = left_val if choice == "L" else right_val
                print("")  # Blank line for readability.

        # Display the merged row preview.
        print("\nThe merged row will be:")
        for col, value in merged_values.items():
            print(f"  {col}: {value}")

        # Final confirmation before applying changes.
        confirm = (
            input("\nApply these changes and merge the rows? (y/n): ").strip().lower()
        )
        # Optionally, ask if the right row should be deleted.
        delete_right = (
            input("Do you want to delete the right row? (y/n): ").strip().lower()
        )

        if confirm != "y":
            print("Merge cancelled. No changes made.")
            return

        if delete_right == "y":
            self.delete(where={"sys_id": right_pk})
            print("Right row deleted.")

        # Update the left row with the merged values.
        left_row.update(merged_values)
        print("Merge applied: Left row updated with merged values.")
        print("Merge completed.")

    def find_duplicates(self, columns, sql_only=False):
        """
        Returns duplicate groups from the table based on the specified columns in a case-insensitive way.

        For each column, the subquery computes:
        - lower(column) AS normalized_<column>
        - array_agg(column) AS variations_<column>
        - array_agg(sys_id) AS sys_ids
        - COUNT(*) AS total_count

        The subquery groups by lower(column) values and retains only groups with more than one row.

        Example SQL for a single column "email_address":

            SELECT
            lower(email_address) AS normalized_email_address,
            array_agg(email_address) AS variations_email_address,
            array_agg(sys_id) AS sys_ids,
            COUNT(*) AS total_count
            FROM donor_users
            GROUP BY lower(email_address)
            HAVING COUNT(*) > 1

        Parameters:
        columns (list or str): Column name or list of column names to check duplicates on.
        sql_only (bool): If True, returns the SQL string and an empty tuple; otherwise,
                        executes the query using self.tx.execute.

        Returns:
        A tuple of (SQL string, parameters) if sql_only is True, otherwise the result of executing the query.
        """
        if not columns:
            raise ValueError(
                "You must specify at least one column to check for duplicates."
            )

        if isinstance(columns, str):
            columns = [columns]

        # Build subquery SELECT clause parts for normalized values and variations.
        normalized_cols = [f"lower({col}) AS normalized_{col}" for col in columns]
        variations_cols = [f"array_agg({col}) AS variations_{col}" for col in columns]

        subquery_select = ",\n  ".join(
            normalized_cols
            + variations_cols
            + ["array_agg(sys_id) AS sys_ids", "COUNT(*) AS total_count"]
        )

        groupby_clause = ", ".join([f"lower({col})" for col in columns])

        subquery = f"""
        SELECT
        {subquery_select}
        FROM {self.name}
        GROUP BY {groupby_clause}
        HAVING COUNT(*) > 1
        """

        if sql_only:
            return subquery, ()
        return self.tx.execute(subquery, ())

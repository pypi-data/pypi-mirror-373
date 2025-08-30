from velocity.db import exceptions
from velocity.db.core.decorators import return_default


class Column:
    """
    Represents a column in a database table.
    """

    def __init__(self, table, name):
        if isinstance(table, str):
            raise Exception("Column 'table' parameter must be a Table instance.")
        self.tx = table.tx
        self.sql = table.tx.engine.sql
        self.name = name
        self.table = table

    def __str__(self):
        return (
            f"Table: {self.table.name}\n"
            f"Column: {self.name}\n"
            f"Column Exists: {self.exists()}\n"
            f"Py Type: {self.py_type}\n"
            f"SQL Type: {self.sql_type}\n"
            f"NULL OK: {self.is_nullok}\n"
            f"Foreign Key: {self.foreign_key_to}\n"
        )

    @property
    def info(self):
        """
        Retrieves information about the column from the database, raising DbColumnMissingError if not found.
        """
        sql, vals = self.sql.column_info(self.table.name, self.name)
        result = self.tx.execute(sql, vals).one()
        if not result:
            raise exceptions.DbColumnMissingError
        return result

    @property
    def foreign_key_info(self):
        """
        Retrieves information about any foreign key constraint on this column.
        """
        sql, vals = self.sql.foreign_key_info(table=self.table.name, column=self.name)
        result = self.tx.execute(sql, vals).one()
        if not result:
            raise exceptions.DbColumnMissingError
        return result

    @property
    def foreign_key_to(self):
        """
        Returns a string 'referenced_table_name.referenced_column_name' or None if no foreign key.
        """
        try:
            return "{referenced_table_name}.{referenced_column_name}".format(
                **self.foreign_key_info
            )
        except exceptions.DbColumnMissingError:
            return None

    @property
    def foreign_key_table(self):
        """
        Returns the name of the referenced table for the foreign key, or None if none.
        """
        try:
            return self.foreign_key_info["referenced_table_name"]
        except exceptions.DbColumnMissingError:
            return None

    def exists(self):
        """
        True if this column name is in self.table.columns().
        """
        return self.name in self.table.columns()

    @property
    def py_type(self):
        """
        Returns the Python data type that corresponds to this column's SQL type.
        """
        return self.sql.types.py_type(self.sql_type)

    @property
    def sql_type(self):
        """
        Returns the underlying SQL type name (e.g. 'TEXT', 'INTEGER', etc.).
        """
        return self.info[self.sql.type_column_identifier]

    @property
    def is_nullable(self):
        """
        True if column is nullable.
        """
        return self.info[self.sql.is_nullable]

    is_nullok = is_nullable

    def rename(self, name):
        """
        Renames the column.
        """
        sql, vals = self.sql.rename_column(self.table.name, self.name, name)
        self.tx.execute(sql, vals)
        self.name = name

    @return_default([])
    def distinct(self, order="asc", qty=None):
        """
        Returns the distinct values in this column, optionally ordered and/or limited in quantity.
        """
        sql, vals = self.sql.select(
            columns=f"distinct {self.name}",
            table=self.table.name,
            orderby=f"{self.name} {order}",
            qty=qty,
        )
        return self.tx.execute(sql, vals).as_simple_list().all()

    def max(self, where=None):
        """
        Returns the MAX() of this column, or 0 if table/column is missing.
        """
        try:
            sql, vals = self.sql.select(
                columns=f"max({self.name})", table=self.table.name, where=where
            )
            return self.tx.execute(sql, vals).scalar()
        except (exceptions.DbTableMissingError, exceptions.DbColumnMissingError):
            return 0

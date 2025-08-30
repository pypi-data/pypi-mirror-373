import re
import hashlib
import sqlparse
from psycopg2 import sql as psycopg2_sql

from velocity.db import exceptions

from .reserved import reserved_words
from .types import TYPES
from .operators import OPERATORS
from ..tablehelper import TableHelper
from collections.abc import Mapping, Sequence


# Configure TableHelper for PostgreSQL
TableHelper.reserved = reserved_words
TableHelper.operators = OPERATORS


def _get_table_helper(tx, table):
    """
    Utility function to create a TableHelper instance.
    Ensures consistent configuration across all SQL methods.
    """
    return TableHelper(tx, table)


def _validate_table_name(table):
    """Validate table name format."""
    if not table or not isinstance(table, str):
        raise ValueError("Table name must be a non-empty string")
    # Add more validation as needed
    return table.strip()


def _handle_predicate_errors(predicates, operation="WHERE"):
    """Process a list of predicates with error handling."""
    sql_parts = []
    vals = []

    for pred, val in predicates:
        sql_parts.append(pred)
        if val is None:
            pass
        elif isinstance(val, tuple):
            vals.extend(val)
        else:
            vals.append(val)

    return sql_parts, vals


system_fields = [
    "sys_id",
    "sys_created",
    "sys_modified",
    "sys_modified_by",
    "sys_dirty",
    "sys_table",
    "description",
]


class SQL:
    server = "PostGreSQL"
    type_column_identifier = "data_type"
    is_nullable = "is_nullable"

    default_schema = "public"

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
    DuplicateKeyErrorCodes = [
        "23505"
    ]  # unique_violation - no longer relying only on regex
    RetryTransactionCodes = ["40001", "40P01", "40002"]
    TruncationErrorCodes = ["22001"]
    LockTimeoutErrorCodes = ["55P03"]
    DatabaseObjectExistsErrorCodes = ["42710", "42P07", "42P04"]
    DataIntegrityErrorCodes = ["23503", "23502", "23514", "23P01", "22003"]

    @classmethod
    def get_error(self, e):
        error_code = getattr(e, "pgcode", None)
        error_mesg = getattr(e, "pgerror", None)
        return error_code, error_mesg

    types = TYPES

    @classmethod
    def select(
        cls,
        tx,
        columns=None,
        table=None,
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
        Generate a PostgreSQL SELECT statement with proper table helper integration.
        """
        if not table:
            raise ValueError("Table name is required.")

        # Validate pagination parameters
        if start is not None and not isinstance(start, int):
            raise ValueError("Start (OFFSET) must be an integer.")
        if qty is not None and not isinstance(qty, int):
            raise ValueError("Qty (FETCH) must be an integer.")

        sql_parts = {
            "SELECT": [],
            "FROM": [],
            "WHERE": [],
            "GROUP BY": [],
            "HAVING": [],
            "ORDER BY": [],
        }

        sql = []
        vals = []

        # Create table helper instance
        th = _get_table_helper(tx, table)

        # Handle columns and DISTINCT before aliasing
        if columns is None:
            # No columns specified - select all
            columns = ["*"]
        elif isinstance(columns, str):
            columns = th.split_columns(columns)
        elif not isinstance(columns, Sequence):
            raise TypeError(
                f"Columns must be a string, sequence, or None, but {type(columns)} was found"
            )

        # Clean and validate columns
        columns = [c.strip() for c in columns if c.strip()]  # Remove empty columns
        if not columns:
            raise ValueError("No valid columns specified")

        distinct = False

        # Check for DISTINCT keyword in any column
        if any("distinct" in c.lower() for c in columns):
            distinct = True
            columns = [re.sub(r"(?i)\bdistinct\b", "", c).strip() for c in columns]

        # Process column references
        processed_columns = []
        for col in columns:
            try:
                processed_col = th.resolve_references(
                    col,
                    options={
                        "alias_column": True,
                        "alias_table": True,
                        "bypass_on_error": True,
                    },
                )
                processed_columns.append(processed_col)
            except Exception as e:
                raise ValueError(f"Error processing column '{col}': {e}")

        columns = processed_columns

        # Handle WHERE conditions with better error handling
        if isinstance(where, Mapping):
            new_where = []
            for key, val in where.items():
                try:
                    new_where.append(th.make_predicate(key, val))
                except Exception as e:
                    raise ValueError(f"Error processing WHERE condition '{key}': {e}")
            where = new_where

        # Handle ORDER BY with improved validation
        new_orderby = []
        if isinstance(orderby, str):
            orderby = th.split_columns(orderby)

        # Handle orderby references
        if isinstance(orderby, Sequence):
            for column in orderby:
                try:
                    if " " in column:
                        parts = column.split(" ", 1)
                        if len(parts) == 2:
                            col_name, direction = parts
                            # Validate direction
                            direction = direction.upper()
                            if direction not in ("ASC", "DESC"):
                                raise ValueError(
                                    f"Invalid ORDER BY direction: {direction}"
                                )
                            col_name = th.resolve_references(
                                col_name.strip(), options={"alias_only": True}
                            )
                            new_orderby.append(f"{col_name} {direction}")
                        else:
                            raise ValueError(f"Invalid ORDER BY format: {column}")
                    else:
                        resolved_col = th.resolve_references(
                            column.strip(), options={"alias_only": True}
                        )
                        new_orderby.append(resolved_col)
                except Exception as e:
                    raise ValueError(
                        f"Error processing ORDER BY column '{column}': {e}"
                    )

        elif isinstance(orderby, Mapping):
            for key, val in orderby.items():
                try:
                    # Validate direction
                    direction = str(val).upper()
                    if direction not in ("ASC", "DESC"):
                        raise ValueError(f"Invalid ORDER BY direction: {direction}")
                    parsed_key = th.resolve_references(
                        key, options={"alias_only": True}
                    )
                    new_orderby.append(f"{parsed_key} {direction}")
                except Exception as e:
                    raise ValueError(f"Error processing ORDER BY key '{key}': {e}")

        orderby = new_orderby

        # Handle groupby
        if isinstance(groupby, str):
            groupby = th.split_columns(groupby)
        if isinstance(groupby, (Sequence)):
            new_groupby = []
            for gcol in groupby:
                new_groupby.append(
                    th.resolve_references(gcol, options={"alias_only": True})
                )
            groupby = new_groupby

        # Handle having
        if isinstance(having, Mapping):
            new_having = []
            for key, val in having.items():
                new_having.append(th.make_predicate(key, val))
            having = new_having

        # SELECT clause
        # columns is a list/tuple of already processed references
        sql_parts["SELECT"].extend(columns)
        alias = th.get_table_alias("current_table")
        if not alias:
            raise ValueError("Main table alias resolution failed.")

        # FROM clause
        if th.foreign_keys:
            sql_parts["FROM"].append(
                f"{TableHelper.quote(table)} AS {TableHelper.quote(alias)}"
            )
            # Handle joins
            done = []
            for key, ref_info in th.foreign_keys.items():
                ref_table = ref_info["ref_table"]
                if ref_table in done:
                    continue
                done.append(ref_table)
                if not all(
                    k in ref_info
                    for k in ("alias", "local_column", "ref_table", "ref_column")
                ):
                    raise ValueError(f"Invalid table alias info for {ref_table}.")
                sql_parts["FROM"].append(
                    f"LEFT JOIN {TableHelper.quote(ref_table)} AS {TableHelper.quote(ref_info['alias'])} "
                    f"ON {TableHelper.quote(alias)}.{TableHelper.quote(ref_info['local_column'])} = {TableHelper.quote(ref_info['alias'])}.{TableHelper.quote(ref_info['ref_column'])}"
                )
        else:
            sql_parts["FROM"].append(TableHelper.quote(table))

        # WHERE
        if where:
            if isinstance(where, str):
                sql_parts["WHERE"].append(where)
            else:
                for pred, val in where:
                    sql_parts["WHERE"].append(pred)
                    if val is None:
                        pass
                    elif isinstance(val, tuple):
                        vals.extend(val)
                    else:
                        vals.append(val)

        # GROUP BY
        if groupby:
            sql_parts["GROUP BY"].append(",".join(groupby))

        # HAVING
        if having:
            if isinstance(having, str):
                sql_parts["HAVING"].append(having)
            else:
                for pred, val in having:
                    sql_parts["HAVING"].append(pred)
                    if val is None:
                        pass
                    elif isinstance(val, tuple):
                        vals.extend(val)
                    else:
                        vals.append(val)

        # ORDER BY
        if orderby:
            sql_parts["ORDER BY"].append(",".join(orderby))

        # Construct final SQL
        if sql_parts["SELECT"]:
            sql.append("SELECT")
            if distinct:
                sql.append("DISTINCT")
            sql.append(", ".join(sql_parts["SELECT"]))

        if sql_parts["FROM"]:
            sql.append("FROM")
            sql.append(" ".join(sql_parts["FROM"]))

        if sql_parts["WHERE"]:
            sql.append("WHERE " + " AND ".join(sql_parts["WHERE"]))

        if sql_parts["GROUP BY"]:
            sql.append("GROUP BY " + " ".join(sql_parts["GROUP BY"]))

        if sql_parts["HAVING"]:
            sql.append("HAVING " + " AND ".join(sql_parts["HAVING"]))

        if sql_parts["ORDER BY"]:
            sql.append("ORDER BY " + " ".join(sql_parts["ORDER BY"]))

        # OFFSET/FETCH
        if start is not None:
            if not isinstance(start, int):
                raise ValueError("Start (OFFSET) must be an integer.")
            sql.append(f"OFFSET {start} ROWS")

        if qty is not None:
            if not isinstance(qty, int):
                raise ValueError("Qty (FETCH) must be an integer.")
            sql.append(f"FETCH NEXT {qty} ROWS ONLY")

        # FOR UPDATE and SKIP LOCKED
        if lock or skip_locked:
            sql.append("FOR UPDATE")
        if skip_locked:
            sql.append("SKIP LOCKED")

        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple(vals)

    @classmethod
    def update(cls, tx, table, data, where=None, pk=None, excluded=False):
        """
        Generate a Postgres UPDATE statement, handling the WHERE clause logic similar
        to how the SELECT statement does. If you want to do an ON CONFLICT ... DO UPDATE,
        that logic should generally live in `merge(...)` rather than here.

        :param tx: Database/transaction context object (used by TableHelper)
        :param table: Table name
        :param data: Dictionary of columns to update
        :param where: WHERE clause conditions (dict, list of tuples, or string)
        :param pk: Primary key dict to merge with `where`
        :param excluded: If True, creates `col = EXCLUDED.col` expressions (used in upsert)
        :return: (sql_string, params_tuple)
        """

        if not table:
            raise ValueError("Table name is required.")
        if not pk and not where:
            raise ValueError("Where clause (where) or primary key (pk) is required.")
        if not isinstance(data, Mapping) or not data:
            raise ValueError("data must be a non-empty mapping of column-value pairs.")

        th = _get_table_helper(tx, table)
        set_clauses = []
        vals = []

        # Merge pk into where if pk is provided
        if pk:
            if where:
                # If where is a dict, update it; otherwise raise error
                if isinstance(where, Mapping):
                    where = dict(where)  # copy to avoid mutation
                    where.update(pk)
                else:
                    raise ValueError(
                        "Cannot combine 'pk' with a non-dict 'where' clause."
                    )
            else:
                where = pk

        # Build SET clauses
        for col, val in data.items():
            col_quoted = th.resolve_references(
                col, options={"alias_column": False, "alias_table": False}
            )
            if excluded:
                # For ON CONFLICT DO UPDATE statements, use the EXCLUDED value
                set_clauses.append(f"{col_quoted} = EXCLUDED.{col_quoted}")
            else:
                set_clauses.append(f"{col_quoted} = %s")
                vals.append(val)

        # Build WHERE clauses for a normal update (ignored when excluded is True)
        where_clauses = []
        if not excluded:
            if where:
                if isinstance(where, Mapping):
                    new_where = []
                    for key, val in where.items():
                        new_where.append(th.make_predicate(key, val))
                    where = new_where
                if isinstance(where, str):
                    where_clauses.append(where)
                else:
                    for pred, value in where:
                        where_clauses.append(pred)
                        if value is None:
                            pass
                        elif isinstance(value, tuple):
                            vals.extend(value)
                        else:
                            vals.append(value)
            if not where_clauses:
                raise ValueError(
                    "No WHERE clause could be constructed. Update would affect all rows."
                )

        # Construct final SQL
        if excluded:
            # For an upsert's DO UPDATE, only return the SET clause (no table name, no WHERE)
            sql_parts = []
            sql_parts.append("UPDATE")
            sql_parts.append("SET " + ", ".join(set_clauses))
            final_sql = sqlparse.format(
                " ".join(sql_parts), reindent=True, keyword_case="upper"
            )
            return final_sql, tuple(vals)
        else:
            sql_parts = []
            sql_parts.append("UPDATE")
            sql_parts.append(TableHelper.quote(table))
            sql_parts.append("SET " + ", ".join(set_clauses))
            if where_clauses:
                sql_parts.append("WHERE " + " AND ".join(where_clauses))
            final_sql = sqlparse.format(
                " ".join(sql_parts), reindent=True, keyword_case="upper"
            )
            return final_sql, tuple(vals)

    @classmethod
    def insert(cls, table, data):
        """
        Generate an INSERT statement.
        """
        # Create a temporary TableHelper instance for quoting
        # Note: We pass None for tx since we only need quoting functionality
        temp_helper = TableHelper(None, table)

        keys = []
        vals_placeholders = []
        args = []
        for key, val in data.items():
            keys.append(temp_helper.quote(key.lower()))
            if isinstance(val, str) and len(val) > 2 and val[:2] == "@@" and val[2:]:
                vals_placeholders.append(val[2:])
            else:
                vals_placeholders.append("%s")
                args.append(val)

        sql_parts = []
        sql_parts.append("INSERT INTO")
        sql_parts.append(temp_helper.quote(table))
        sql_parts.append("(")
        sql_parts.append(",".join(keys))
        sql_parts.append(")")
        sql_parts.append("VALUES")
        sql_parts.append("(")
        sql_parts.append(",".join(vals_placeholders))
        sql_parts.append(")")
        sql = sqlparse.format(" ".join(sql_parts), reindent=True, keyword_case="upper")
        return sql, tuple(args)

    @classmethod
    def merge(cls, tx, table, data, pk, on_conflict_do_nothing, on_conflict_update):
        if pk is None:
            pkeys = tx.table(table).primary_keys()
            if not pkeys:
                raise ValueError("Primary key required for merge.")
            # If there are multiple primary keys, use all of them
            if len(pkeys) > 1:
                pk = {pk: data[pk] for pk in pkeys}
            else:
                pk = {pkeys[0]: data[pkeys[0]]}
            # Remove primary keys from data; they will be used in the conflict target
            data = {k: v for k, v in data.items() if k not in pk}

        # Create a merged dictionary for insert (data + primary key columns)
        full_data = {}
        full_data.update(data)
        full_data.update(pk)

        sql, vals = cls.insert(table, full_data)
        sql = [sql]
        vals = list(vals)  # Convert to a mutable list

        if on_conflict_do_nothing != on_conflict_update:
            sql.append("ON CONFLICT")
            sql.append("(")
            sql.append(",".join(pk.keys()))
            sql.append(")")
            sql.append("DO")
            if on_conflict_do_nothing:
                sql.append("NOTHING")
            elif on_conflict_update:
                # Call update() with excluded=True to produce the SET clause for the upsert.
                sql_update, vals_update = cls.update(tx, table, data, pk, excluded=True)
                sql.append(sql_update)
                # Use list.extend to add the update values to vals.
                vals.extend(vals_update)
        else:
            raise Exception(
                "Update on conflict must have one and only one option to complete on conflict."
            )

        import sqlparse

        final_sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return final_sql, tuple(vals)

    @classmethod
    def version(cls):
        return "select version()", tuple()

    @classmethod
    def timestamp(cls):
        return "select current_timestamp", tuple()

    @classmethod
    def user(cls):
        return "select current_user", tuple()

    @classmethod
    def databases(cls):
        return "select datname from pg_database where datistemplate = false", tuple()

    @classmethod
    def schemas(cls):
        return "select schema_name from information_schema.schemata", tuple()

    @classmethod
    def current_schema(cls):
        return "select current_schema", tuple()

    @classmethod
    def current_database(cls):
        return "select current_database()", tuple()

    @classmethod
    def tables(cls, system=False):
        if system:
            return (
                "select table_schema,table_name from information_schema.tables where table_type = 'BASE TABLE' order by table_schema,table_name",
                tuple(),
            )
        else:
            return (
                "select table_schema, table_name from information_schema.tables where table_type = 'BASE TABLE' and table_schema NOT IN ('pg_catalog', 'information_schema')",
                tuple(),
            )

    @classmethod
    def views(cls, system=False):
        if system:
            return (
                "select table_schema, table_name from information_schema.views order by table_schema,table_name",
                tuple(),
            )
        else:
            return (
                "select table_schema, table_name from information_schema.views where table_schema = any (current_schemas(false)) order by table_schema,table_name",
                tuple(),
            )

    @classmethod
    def create_database(cls, name):
        return f"create database {name}", tuple()

    @classmethod
    def last_id(cls, table):
        return "SELECT CURRVAL(PG_GET_SERIAL_SEQUENCE(%s, 'sys_id'))", tuple([table])

    @classmethod
    def current_id(cls, table):
        return (
            "SELECT pg_sequence_last_value(PG_GET_SERIAL_SEQUENCE(%s, 'sys_id'))",
            tuple([table]),
        )

    @classmethod
    def set_id(cls, table, start):
        return "SELECT SETVAL(PG_GET_SERIAL_SEQUENCE(%s, 'sys_id'), %s)", tuple(
            [table, start]
        )

    @classmethod
    def drop_database(cls, name):
        return f"drop database if exists {name}", tuple()

    @classmethod
    def create_table(cls, name, columns={}, drop=False):
        if "." in name:
            fqtn = TableHelper.quote(name)
        else:
            fqtn = f"public.{TableHelper.quote(name)}"
        schema, table = fqtn.split(".")
        name = fqtn.replace(".", "_")
        sql = []
        if drop:
            sql.append(cls.drop_table(fqtn)[0])
        sql.append(
            f"""
            CREATE TABLE {fqtn} (
              sys_id BIGSERIAL PRIMARY KEY,
              sys_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              sys_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              sys_modified_by TEXT,
              sys_dirty BOOLEAN NOT NULL DEFAULT FALSE,
              sys_table TEXT,
              description TEXT
            );

            SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('{fqtn}', 'sys_id'),1000,TRUE);

            CREATE OR REPLACE FUNCTION {schema}.on_sys_modified()
              RETURNS TRIGGER AS
            $BODY$
                        BEGIN
                        -- update sys_modified on each insert/update.
                        NEW.sys_modified := now();
                        if (TG_OP = 'INSERT') THEN
                            NEW.sys_created :=now();
                        ELSEIF (TG_OP = 'UDPATE') THEN
                         -- Do not allow sys_created to be modified.
                            NEW.sys_created := OLD.sys_created;
                        END IF;
                        -- Insert table name to row
                        NEW.sys_table := TG_TABLE_NAME;
                        RETURN NEW;
                        END;
            $BODY$
              LANGUAGE plpgsql VOLATILE
              COST 100;

            CREATE TRIGGER on_update_row_{fqtn.replace('.', '_')}
            BEFORE INSERT OR UPDATE ON {fqtn}
            FOR EACH ROW EXECUTE PROCEDURE {schema}.on_sys_modified();

        """
        )

        for key, val in columns.items():
            key = re.sub("<>!=%", "", key)
            if key in system_fields:
                continue
            sql.append(
                f"ALTER TABLE {TableHelper.quote(fqtn)} ADD COLUMN {TableHelper.quote(key)} {TYPES.get_type(val)};"
            )

        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple()

    @classmethod
    def drop_table(cls, name):
        return f"drop table if exists {TableHelper.quote(name)} cascade;", tuple()

    @classmethod
    def drop_column(cls, table, name, cascade=True):
        if cascade:
            return (
                f"ALTER TABLE {TableHelper.quote(table)} DROP COLUMN {TableHelper.quote(name)} CASCADE",
                tuple(),
            )
        else:
            return (
                f"ALTER TABLE {TableHelper.quote(table)} DROP COLUMN {TableHelper.quote(name)}",
                tuple(),
            )

    @classmethod
    def columns(cls, name):
        if "." in name:
            return """
            select column_name
            from information_schema.columns
            where UPPER(table_schema) = UPPER(%s)
            and UPPER(table_name) = UPPER(%s)
            """, tuple(
                name.split(".")
            )
        else:
            return """
            select column_name
            from information_schema.columns
            where UPPER(table_name) = UPPER(%s)
            """, tuple(
                [
                    name,
                ]
            )

    @classmethod
    def column_info(cls, table, name):
        params = table.split(".")
        params.append(name)
        if "." in table:
            return """
            select *
            from information_schema.columns
            where UPPER(table_schema ) = UPPER(%s)
            and UPPER(table_name) = UPPER(%s)
            and UPPER(column_name) = UPPER(%s)
            """, tuple(
                params
            )
        else:
            return """
            select *
            from information_schema.columns
            where UPPER(table_name) = UPPER(%s)
            and UPPER(column_name) = UPPER(%s)
            """, tuple(
                params
            )

    @classmethod
    def primary_keys(cls, table):
        params = table.split(".")
        params.reverse()
        if "." in table:
            return """
            SELECT
              pg_attribute.attname
            FROM pg_index, pg_class, pg_attribute, pg_namespace
            WHERE
              pg_class.oid = %s::regclass AND
              indrelid = pg_class.oid AND
              nspname = %s AND
              pg_class.relnamespace = pg_namespace.oid AND
              pg_attribute.attrelid = pg_class.oid AND
              pg_attribute.attnum = any(pg_index.indkey)
             AND indisprimary
            """, tuple(
                params
            )
        else:
            return """
            SELECT
              pg_attribute.attname
            FROM pg_index, pg_class, pg_attribute, pg_namespace
            WHERE
              pg_class.oid = %s::regclass AND
              indrelid = pg_class.oid AND
              pg_class.relnamespace = pg_namespace.oid AND
              pg_attribute.attrelid = pg_class.oid AND
              pg_attribute.attnum = any(pg_index.indkey)
             AND indisprimary
            """, tuple(
                params
            )

    @classmethod
    def foreign_key_info(cls, table=None, column=None, schema=None):
        if "." in table:
            schema, table = table.split(".")

        sql = [
            """
        SELECT
             KCU1.CONSTRAINT_NAME AS "FK_CONSTRAINT_NAME"
           , KCU1.CONSTRAINT_SCHEMA AS "FK_CONSTRAINT_SCHEMA"
           , KCU1.CONSTRAINT_CATALOG AS "FK_CONSTRAINT_CATALOG"
           , KCU1.TABLE_NAME AS "FK_TABLE_NAME"
           , KCU1.COLUMN_NAME AS "FK_COLUMN_NAME"
           , KCU1.ORDINAL_POSITION AS "FK_ORDINAL_POSITION"
           , KCU2.CONSTRAINT_NAME AS "UQ_CONSTRAINT_NAME"
           , KCU2.CONSTRAINT_SCHEMA AS "UQ_CONSTRAINT_SCHEMA"
           , KCU2.CONSTRAINT_CATALOG AS "UQ_CONSTRAINT_CATALOG"
           , KCU2.TABLE_NAME AS "UQ_TABLE_NAME"
           , KCU2.COLUMN_NAME AS "UQ_COLUMN_NAME"
           , KCU2.ORDINAL_POSITION AS "UQ_ORDINAL_POSITION"
           , KCU1.CONSTRAINT_NAME AS "CONSTRAINT_NAME"
           , KCU2.CONSTRAINT_SCHEMA AS "REFERENCED_TABLE_SCHEMA"
           , KCU2.TABLE_NAME AS "REFERENCED_TABLE_NAME"
           , KCU2.COLUMN_NAME AS "REFERENCED_COLUMN_NAME"
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS RC
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE KCU1
        ON KCU1.CONSTRAINT_CATALOG = RC.CONSTRAINT_CATALOG
           AND KCU1.CONSTRAINT_SCHEMA = RC.CONSTRAINT_SCHEMA
           AND KCU1.CONSTRAINT_NAME = RC.CONSTRAINT_NAME
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE KCU2
        ON KCU2.CONSTRAINT_CATALOG = RC.UNIQUE_CONSTRAINT_CATALOG
           AND KCU2.CONSTRAINT_SCHEMA = RC.UNIQUE_CONSTRAINT_SCHEMA
           AND KCU2.CONSTRAINT_NAME = RC.UNIQUE_CONSTRAINT_NAME
           AND KCU2.ORDINAL_POSITION = KCU1.ORDINAL_POSITION
        """
        ]
        vals = []
        where = {}
        if schema:
            where["LOWER(KCU1.CONSTRAINT_SCHEMA)"] = schema.lower()
        if table:
            where["LOWER(KCU1.TABLE_NAME)"] = table.lower()
        if column:
            where["LOWER(KCU1.COLUMN_NAME)"] = column.lower()
        sql.append("WHERE")
        connect = ""
        for key, val in where.items():
            if connect:
                sql.append(connect)
            sql.append(f"{key} = %s")
            vals.append(val)
            connect = "AND"

        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple(vals)

    @classmethod
    def create_foreign_key(
        cls, table, columns, key_to_table, key_to_columns, name=None, schema=None
    ):
        if "." not in table and schema:
            table = f"{schema}.{table}"
        if isinstance(key_to_columns, str):
            key_to_columns = [key_to_columns]
        if isinstance(columns, str):
            columns = [columns]
        if not name:
            m = hashlib.md5()
            m.update(table.encode("utf-8"))
            m.update(" ".join(columns).encode("utf-8"))
            m.update(key_to_table.encode("utf-8"))
            m.update(" ".join(key_to_columns).encode("utf-8"))
            name = f"FK_{m.hexdigest()}"
        sql = f"ALTER TABLE {table} ADD CONSTRAINT {name} FOREIGN KEY ({','.join(columns)}) REFERENCES {key_to_table} ({','.join(key_to_columns)});"
        sql = sqlparse.format(sql, reindent=True, keyword_case="upper")
        return sql, tuple()

    @classmethod
    def drop_foreign_key(
        cls,
        table,
        columns,
        key_to_table=None,
        key_to_columns=None,
        name=None,
        schema=None,
    ):
        if "." not in table and schema:
            table = f"{schema}.{table}"
        if isinstance(key_to_columns, str):
            key_to_columns = [key_to_columns]
        if isinstance(columns, str):
            columns = [columns]
        if not name:
            m = hashlib.md5()
            m.update(table.encode("utf-8"))
            m.update(" ".join(columns).encode("utf-8"))
            m.update(key_to_table.encode("utf-8"))
            m.update(" ".join(key_to_columns).encode("utf-8"))
            name = f"FK_{m.hexdigest()}"
        sql = f"ALTER TABLE {table} DROP CONSTRAINT {name};"
        return sql, tuple()

    @classmethod
    def create_index(
        cls,
        tx,
        table=None,
        columns=None,
        unique=False,
        direction=None,
        where=None,
        name=None,
        schema=None,
        trigram=None,
        lower=None,
    ):
        """
        The following statements must be executed on the database instance once to enable respective trigram features.
        CREATE EXTENSION pg_trgm; is required to use  gin.
        CREATE EXTENSION btree_gist; is required to use gist
        """
        if "." not in table and schema:
            table = f"{schema}.{table}"
        if isinstance(columns, (list, set)):
            columns = ",".join([TableHelper.quote(c) for c in columns])
        else:
            columns = TableHelper.quote(columns)
        sql = ["CREATE"]
        if unique:
            sql.append("UNIQUE")
        sql.append("INDEX")
        tablename = TableHelper.quote(table)
        if not name:
            name = re.sub(
                r"\([^)]*\)",
                "",
                columns.replace(" ", "").replace(",", "_").replace('"', ""),
            )
        if trigram:
            sql.append(f"IDX__TRGM_{table.replace('.', '_')}_{trigram}__{name}".upper())
        else:
            sql.append(f"IDX__{table.replace('.', '_')}__{name}".upper())
        sql.append("ON")
        sql.append(TableHelper.quote(tablename))

        if trigram:
            sql.append("USING")
            sql.append(trigram)
        sql.append("(")
        join = ""
        for column_name in columns.split(","):
            column_name = column_name.replace('"', "")
            if join:
                sql.append(join)
            column = tx.table(table).column(column_name)
            if not column.exists():
                raise Exception(
                    f"Column {column_name} does not exist in table {table}."
                )
            if column.py_type == str:
                if lower:
                    sql.append(f"lower({TableHelper.quote(column_name)})")
                else:
                    sql.append(TableHelper.quote(column_name))
            else:
                sql.append(TableHelper.quote(column_name))
            join = ","

        if trigram:
            sql.append(f"{trigram.lower()}_trgm_ops")
        sql.append(")")
        vals = []
        s, v = TableHelper(tx, table).make_where(where)
        sql.append(s)
        vals.extend(v)

        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple(vals)

    @classmethod
    def drop_index(cls, table=None, columns=None, name=None, schema=None, trigram=None):
        if "." not in table and schema:
            table = f"{schema}.{table}"
        if isinstance(columns, (list, set)):
            columns = ",".join([TableHelper.quote(c) for c in columns])
        else:
            columns = TableHelper.quote(columns)
        sql = ["DROP"]
        sql.append("INDEX IF EXISTS")
        _tablename = TableHelper.quote(table)
        if not name:
            name = re.sub(
                r"\([^)]*\)",
                "",
                columns.replace(" ", "").replace(",", "_").replace('"', ""),
            )
        if trigram:
            sql.append(f"IDX__TRGM_{table.replace('.', '_')}_{trigram.upper()}__{name}")
        else:
            sql.append(f"IDX__{table.replace('.', '_')}__{name}")

        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple()

    @classmethod
    def massage_data(cls, data):
        data = {key: val for key, val in data.items()}
        primaryKey = set(cls.GetPrimaryKeyColumnNames())
        if not primaryKey:
            if not cls.Exists():
                raise exceptions.DbTableMissingError
        dataKeys = set(data.keys()).intersection(primaryKey)
        dataColumns = set(data.keys()).difference(primaryKey)
        pk = {}
        pk.update([(k, data[k]) for k in dataKeys])
        d = {}
        d.update([(k, data[k]) for k in dataColumns])
        return d, pk

    @classmethod
    def alter_add(cls, table, columns, null_allowed=True):
        """
        Modify the table to add new columns. If the `value` is 'now()', treat it as a
        TIMESTAMP type (optionally with a DEFAULT now() clause).
        """
        sql = []
        null_clause = "NOT NULL" if not null_allowed else ""

        if isinstance(columns, dict):
            for col_name, val in columns.items():
                col_name_clean = re.sub("<>!=%", "", col_name)
                # If the user wants 'now()' to be recognized as a TIMESTAMP column:
                if isinstance(val, str) and val.strip().lower() == "@@now()":
                    # We assume the user wants the type to be TIMESTAMP
                    # Optionally we can also add `DEFAULT now()` if desired
                    # so that newly added rows use the current timestamp
                    col_type = "TIMESTAMP"
                    sql.append(
                        f"ALTER TABLE {TableHelper.quote(table)} "
                        f"ADD {TableHelper.quote(col_name_clean)} {col_type} {null_clause};"
                    )
                else:
                    # Normal code path: rely on your `TYPES.get_type(...)` logic
                    col_type = TYPES.get_type(val)
                    sql.append(
                        f"ALTER TABLE {TableHelper.quote(table)} "
                        f"ADD {TableHelper.quote(col_name_clean)} {col_type} {null_clause};"
                    )

        final_sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return final_sql, tuple()

    @classmethod
    def alter_drop(cls, table, columns):
        sql = [f"ALTER TABLE {TableHelper.quote(table)} DROP COLUMN"]
        if isinstance(columns, dict):
            for key, val in columns.items():
                key = re.sub("<>!=%", "", key)
                sql.append(f"{key},")
        if sql[-1][-1] == ",":
            sql[-1] = sql[-1][:-1]
        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple()

    @classmethod
    def alter_column_by_type(cls, table, column, value, nullable=True):
        sql = [f"ALTER TABLE {TableHelper.quote(table)} ALTER COLUMN"]
        sql.append(f"{TableHelper.quote(column)} TYPE {TYPES.get_type(value)}")
        sql.append(f"USING {TableHelper.quote(column)}::{TYPES.get_conv(value)}")
        if not nullable:
            sql.append("NOT NULL")
        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple()

    @classmethod
    def alter_column_by_sql(cls, table, column, value):
        sql = [f"ALTER TABLE {TableHelper.quote(table)} ALTER COLUMN"]
        sql.append(f"{TableHelper.quote(column)} {value}")
        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple()

    @classmethod
    def rename_column(cls, table, orig, new):
        return (
            f"ALTER TABLE {TableHelper.quote(table)} RENAME COLUMN {TableHelper.quote(orig)} TO {TableHelper.quote(new)};",
            tuple(),
        )

    @classmethod
    def rename_table(cls, table, new):
        return (
            f"ALTER TABLE {TableHelper.quote(table)} RENAME TO {TableHelper.quote(new)};",
            tuple(),
        )

    @classmethod
    def create_savepoint(cls, sp):
        return f'SAVEPOINT "{sp}"', tuple()

    @classmethod
    def release_savepoint(cls, sp):
        return f'RELEASE SAVEPOINT "{sp}"', tuple()

    @classmethod
    def rollback_savepoint(cls, sp):
        return f'ROLLBACK TO SAVEPOINT "{sp}"', tuple()

    @classmethod
    def delete(cls, tx, table, where):
        sql = [f"DELETE FROM {TableHelper.quote(table)}"]
        vals = []
        if where:
            s, v = TableHelper(tx, table).make_where(where)
            sql.append(s)
            vals.extend(v)
        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple(vals)

    @classmethod
    def truncate(cls, table):
        return f"truncate table {TableHelper.quote(table)}", tuple()

    @classmethod
    def create_view(cls, name, query, temp=False, silent=True):
        sql = ["CREATE"]
        if silent:
            sql.append("OR REPLACE")
        if temp:
            sql.append("TEMPORARY")
        sql.append("VIEW")
        sql.append(name)
        sql.append("AS")
        sql.append(query)
        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple()

    @classmethod
    def drop_view(cls, name, silent=True):
        sql = ["DROP VIEW"]
        if silent:
            sql.append("IF EXISTS")
        sql.append(name)
        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple()

    @classmethod
    def alter_trigger(cls, table, state="ENABLE", name="USER"):
        return f"ALTER TABLE {table} {state} TRIGGER {name}", tuple()

    @classmethod
    def set_sequence(cls, table, next_value):
        return (
            f"SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('{table}', 'sys_id'),{next_value},FALSE)",
            tuple(),
        )

    @classmethod
    def missing(cls, tx, table, list, column="SYS_ID", where=None):
        sql = [
            "SELECT * FROM",
            f"UNNEST('{{{','.join([str(x) for x in list])}}}'::int[]) id",
            "EXCEPT ALL",
            f"SELECT {column} FROM {table}",
        ]
        vals = []
        if where:
            s, v = TableHelper(tx, table).make_where(where)
            sql.append(s)
            vals.extend(v)
        sql = sqlparse.format(" ".join(sql), reindent=True, keyword_case="upper")
        return sql, tuple(vals)

    @classmethod
    def indexes(cls, table):
        """
        Returns SQL for retrieving all indexes on a given table with detailed attributes.
        """
        return (
            """
            SELECT indexname, tablename, schemaname, indexdef
            FROM pg_indexes
            WHERE tablename = %s
            """,
            (table,),
        )

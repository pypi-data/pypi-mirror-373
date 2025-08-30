import re
import hashlib
import decimal
import datetime

from velocity.db import exceptions
from .sqlite_reserved import reserved_words


def initialize(config):
    import sqlite3
    from velocity.db.core.engine import Engine

    return Engine(sqlite3, config, SQL)


def quote(data):
    if isinstance(data, list):
        new = []
        for item in data:
            new.append(quote(item))
        return new
    else:
        parts = data.split(".")
        new = []
        for part in parts:
            if '"' in part:
                new.append(part)
            elif part.upper() in reserved_words:
                new.append('"' + part + '"')
            elif re.findall("[/]", part):
                new.append('"' + part + '"')
            else:
                new.append(part)
        return ".".join(new)


class SQL(object):
    server = "SQLite3"
    type_column_identifier = "data_type"
    is_nullable = "is_nullable"

    default_schema = ""

    ApplicationErrorCodes = []

    DatabaseMissingErrorCodes = []
    TableMissingErrorCodes = []
    ColumnMissingErrorCodes = []
    ForeignKeyMissingErrorCodes = []

    ConnectionErrorCodes = []
    DuplicateKeyErrorCodes = []
    RetryTransactionCodes = []
    TruncationErrorCodes = []
    LockTimeoutErrorCodes = []
    DatabaseObjectExistsErrorCodes = []

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
        return "SELECT name FROM sqlite_master WHERE type='table';", tuple()

    @classmethod
    def views(cls, system=False):
        if system:
            return 'SELECT name FROM sqlite_master WHERE type="view";', tuple()
        else:
            return 'SELECT name FROM sqlite_master WHERE type="view";', tuple()

    @classmethod
    def __has_pointer(cls, columns):
        if columns:
            if isinstance(columns, list):
                columns = ",".join(columns)
            if ">" in columns:
                return True
        return False

    @classmethod
    def select(
        cls,
        columns=None,
        table=None,
        where=None,
        orderby=None,
        groupby=None,
        having=None,
        start=None,
        qty=None,
        tbl=None,
    ):
        is_join = False

        if isinstance(columns, str) and "distinct" in columns.lower():
            sql = [
                "SELECT",
                columns,
                "FROM",
                quote(table),
            ]
        elif cls.__has_pointer(columns):
            if isinstance(columns, str):
                columns = columns.split(",")
            letter = 65
            tables = {table: chr(letter)}
            letter += 1
            __select = []
            __from = ["{} AS {}".format(quote(table), tables.get(table))]
            __left_join = []

            for column in columns:
                if ">" in column:
                    is_join = True
                    parts = column.split(">")
                    foreign = tbl.foreign_key_info(parts[0])
                    if not foreign:
                        raise exceptions.DbApplicationError("Foreign key not defined")
                    ref_table = foreign["referenced_table_name"]
                    ref_schema = foreign["referenced_table_schema"]
                    ref_column = foreign["referenced_column_name"]
                    lookup = "{}:{}".format(ref_table, parts[0])
                    if lookup in tables:
                        __select.append(
                            '{}."{}" as "{}"'.format(
                                tables.get(lookup), parts[1], "_".join(parts)
                            )
                        )
                    else:
                        tables[lookup] = chr(letter)
                        letter += 1
                        __select.append(
                            '{}."{}" as "{}"'.format(
                                tables.get(lookup), parts[1], "_".join(parts)
                            )
                        )
                        __left_join.append(
                            'LEFT OUTER JOIN "{}"."{}" AS {}'.format(
                                ref_schema, ref_table, tables.get(lookup)
                            )
                        )
                        __left_join.append(
                            'ON {}."{}" = {}."{}"'.format(
                                tables.get(table),
                                parts[0],
                                tables.get(lookup),
                                ref_column,
                            )
                        )
                    if orderby and column in orderby:
                        orderby = orderby.replace(
                            column, "{}.{}".format(tables.get(lookup), parts[1])
                        )
                else:
                    if "(" in column:
                        __select.append(column)
                    else:
                        __select.append("{}.{}".format(tables.get(table), column))
            sql = ["SELECT"]
            sql.append(",".join(__select))
            sql.append("FROM")
            sql.extend(__from)
            sql.extend(__left_join)
        else:
            if columns:
                if isinstance(columns, str):
                    columns = columns.split(",")
                if isinstance(columns, list):
                    columns = quote(columns)
                    columns = ",".join(columns)
            else:
                columns = "*"
            sql = [
                "SELECT",
                columns,
                "FROM",
                quote(table),
            ]
        vals = []
        if where:
            sql.append("WHERE")
            if isinstance(where, dict):
                where = [x for x in where.items()]
            if isinstance(where, list):
                join = ""
                for key, val in where:
                    if join:
                        sql.append(join)
                    if is_join:
                        if "." not in key:
                            key = "A." + key
                    if val is None:
                        if "!" in key:
                            key = key.replace("!", "")
                            sql.append("{} is not NULL".format(quote(key.lower())))
                        else:
                            sql.append("{} is NULL".format(quote(key.lower())))
                    elif isinstance(val, (list, tuple)):
                        if "!" in key:
                            key = key.replace("!", "")
                            sql.append("{} not in ?".format(quote(key.lower())))
                            vals.append(tuple(val))
                        else:
                            sql.append("{} in ?".format(quote(key.lower())))
                            vals.append(tuple(val))
                    else:
                        if "<>" in key:
                            key = key.replace("<>", "")
                            op = "<>"
                        elif "!=" in key:
                            key = key.replace("!=", "")
                            op = "<>"
                        elif "!%" in key:
                            key = key.replace("!%", "")
                            op = "not ilike"
                        elif "%%" in key:
                            key = key.replace("%%", "")
                            op = "%"
                        elif "%>" in key:
                            key = key.replace("%>", "")
                            op = "%>"
                        elif "<%" in key:
                            key = key.replace("<%", "")
                            op = "<%"
                        elif "==" in key:
                            key = key.replace("==", "")
                            op = "="
                        elif "<=" in key:
                            key = key.replace("<=", "")
                            op = "<="
                        elif ">=" in key:
                            key = key.replace(">=", "")
                            op = ">="
                        elif "<" in key:
                            key = key.replace("<", "")
                            op = "<"
                        elif ">" in key:
                            key = key.replace(">", "")
                            op = ">"
                        elif "%" in key:
                            key = key.replace("%", "")
                            op = "ilike"
                        elif "!" in key:
                            key = key.replace("!", "")
                            op = "<>"
                        elif "=" in key:
                            key = key.replace("=", "")
                            op = "="
                        else:
                            op = "="
                        if isinstance(val, str) and val[:2] == "@@":
                            sql.append(
                                "{} {} {}".format(quote(key.lower()), op, val[2:])
                            )
                        else:
                            sql.append("{} {} ?".format(quote(key.lower()), op))
                            vals.append(val)
                    join = "AND"
            else:
                sql.append(where)
        if groupby:
            sql.append("GROUP BY")
            if isinstance(groupby, (list, tuple)):
                groupby = ",".join(groupby)
            sql.append(groupby)
        if having:
            sql.append("HAVING")
            if isinstance(having, (list, tuple)):
                having = ",".join(having)
            sql.append(having)
        if orderby:
            sql.append("ORDER BY")
            if isinstance(orderby, (list, tuple)):
                orderby = ",".join(orderby)
            sql.append(orderby)
        if start and qty:
            sql.append("OFFSET {} ROWS FETCH NEXT {} ROWS ONLY".format(start, qty))
        elif start:
            sql.append("OFFSET {} ROWS".format(start))
        elif qty:
            sql.append("FETCH NEXT {} ROWS ONLY".format(qty))
        sql = " ".join(sql)
        return sql, tuple(vals)

    @classmethod
    def create_database(cls, name):
        return "create database " + name, tuple()

    @classmethod
    def last_id(cls, table):
        return "SELECT last_insert_rowid()", tuple()

    @classmethod
    def drop_database(cls, name):
        return "drop database if exists " + name, tuple()

    @classmethod
    def create_table(cls, name, columns={}, drop=False):
        sql = []
        if drop:
            sql.append(cls.drop_table(name))
        sql.append(
            """
            CREATE TABLE {0} (
              sys_id INTEGER PRIMARY KEY,
              sys_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              sys_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        """.format(
                name
            )
        )

        for key, val in columns.items():
            sql.append(",\n{} {}".format(quote(key), cls.get_type(val)))

        sql.append("\n);")
        return "\n\t".join(sql), tuple()

    @classmethod
    def drop_table(cls, name):
        return "drop table if exists {}".format(quote(name)), tuple()

    @classmethod
    def columns(cls, name):
        return "PRAGMA table_info({})".format(name), tuple()

    @classmethod
    def column_info(cls, table, name):
        params = table.split(".")
        params.append(name)
        if "." in table:
            return """
            select *
            from information_schema.columns
            where table_schema = ?
            and table_name = ?
            and column_name = ?
            """, tuple(
                params
            )
        else:
            return """
            select *
            from information_schema.columns
            where table_name = ?
            and column_name = ?
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

        sql = """
        SELECT sql
          FROM (
                SELECT
                    sql sql,
                    type type,
                    tbl_name AS referenced_table_name,
                    name AS referenced_column_name,
                    NULL AS referenced_table_schema
                  FROM sqlite_master
                 UNION ALL
                SELECT
                    sql,
                    type,
                    referenced_table_name,
                    referenced_column_name,
                    referenced_table_schema
                  FROM sqlite_temp_master
               )
         WHERE type != 'meta'
           AND sql NOTNULL
           AND name NOT LIKE 'sqlite_%'
         ORDER BY substr(type, 2, 1), name
        """

        return sql, tuple()

    @classmethod
    def create_index(
        cls,
        table=None,
        columns=None,
        unique=False,
        direction=None,
        name=None,
        schema=None,
        tbl=None,
    ):
        if "." not in table and schema:
            table = "{}.{}".format(schema, table)
        if isinstance(columns, (list, set)):
            columns = ",".join([quote(c.lower()) for c in sorted(columns)])
        else:
            columns = quote(columns)
        sql = ["CREATE"]
        if unique:
            sql.append("UNIQUE")
        sql.append("INDEX")
        tablename = quote(table)
        if not name:
            name = re.sub(r"\([^)]*\)", "", columns.replace(",", "_"))
        sql.append("IDX__{}__{}".format(table.replace(".", "_"), name))
        sql.append("ON")
        sql.append(tablename)
        sql.append("(")
        sql.append(columns)
        sql.append(")")
        return " ".join(sql), tuple()

    # Copied from PostGreSQL
    @classmethod
    def create_foreign_key(
        cls, table, columns, key_to_table, key_to_columns, name=None, schema=None
    ):
        if not name:
            m = hashlib.md5()
            m.update(table.name)
            m.update(" ".join(columns))
            m.update(key_to_table)
            m.update(" ".join(key_to_columns))
            name = "FK_" + m.hexdigest()

        original_name = table.name

        # Get SQL query to generate table
        sql = (
            table.tx.table("sqlite_master")
            .select(columns="sql", where={"name": table.name, "type": "table"})
            .scalar()
        )

        # Rename original table
        table.rename(table.name + "_original_data")

        key_info = ""
        if isinstance(columns, list) and isinstance(key_to_columns, list):
            for c in columns:
                key_info += """,
                    CONSTRAINT {}
                    FOREIGN KEY ({})
                    REFERENCES {}({})
                    """.format(
                    name, c, key_to_table, key_to_columns[columns.index(c)]
                )
        elif isinstance(columns, str) and isinstance(key_to_columns, str):
            key_info += """,
                CONSTRAINT {}
                FOREIGN KEY ({})
                REFERENCES {}({})
                """.format(
                name, columns, key_to_table, key_to_columns
            )
        else:
            print('Error parsing argument "columns" or "key_to_columns"')

        # Splits "CREATE TABLE" portion out to be readded to lines at the end
        sql_data = sql.split("(", 1)

        # Goes through the SQL code to generate table and adds foreign key info
        sql_list = sql_data[1].replace("\n", " ").split(",")
        new_sql_list = []
        for line in sql_list:
            line = line.strip().lower()
        for line in sql_list:
            if sql_list.index(line) == len(sql_list) - 1:
                if ")" in line:
                    if line.index(")") == len(line) - 1:
                        new_sql_list.append(line.replace(")", (key_info + ")")))
            else:
                new_sql_list.append(line)

        # Enable changes to be made to foreign keys
        table.tx.execute("PRAGMA foreign_keys=off;")

        # Add sql code to recreate original table with foreign keys
        create_db = ",".join(new_sql_list)
        # Adds "CREATE TABLE" portion back into sql code for execution
        create_db = "(".join([sql_data[0], create_db])
        table.tx.execute(create_db)

        # Create new table with original table name and copy all data from original table
        table.tx.execute(
            "INSERT INTO {} SELECT * FROM {};".format(original_name, table.name)
        )
        # Enable foreign keys
        create_db = "PRAGMA foreign_keys=on;"

        return create_db, tuple()

    @classmethod
    def drop_index(cls, table=None, columns=None, name=None, schema=None):
        if "." not in table and schema:
            table = "{}.{}".format(schema, table)
        if isinstance(columns, (list, set)):
            columns = ",".join([quote(c.lower()) for c in sorted(columns)])
        else:
            columns = quote(columns)
        sql = ["DROP"]
        sql.append("INDEX IF EXISTS")
        tablename = quote(table)
        if not name:
            name = re.sub(r"\([^)]*\)", "", columns.replace(",", "_"))
        sql.append("IDX__{}__{}".format(table.replace(".", "_"), name))
        return " ".join(sql), tuple()

    @classmethod
    def insert(cls, table, data):
        keys = []
        vals = []
        args = []
        for key, val in data.items():
            keys.append(quote(key.lower()))
            if isinstance(val, str) and len(val) > 2 and val[:2] == "@@":
                vals.append(val[2:])
            elif isinstance(val, bytearray):
                vals.append("?")
                args.append(bytes(val))
            else:
                vals.append("?")
                args.append(val)

        sql = ["INSERT INTO"]
        sql.append(quote(table))
        sql.append("(")
        sql.append(",".join(keys))
        sql.append(")")
        sql.append("VALUES")
        sql.append("(")
        sql.append(",".join(vals))
        sql.append(")")
        sql = " ".join(sql)
        return sql, tuple(args)

    @classmethod
    def update(cls, table, data, pk):
        sql = ["UPDATE"]
        sql.append(quote(table))
        sql.append("SET")
        vals = []
        join = ""
        for key in data.keys():
            val = data[key]
            if join:
                sql.append(join)
            if isinstance(val, str) and val[:2] == "@@":
                sql.append("{} = {}".format(quote(key.lower()), val[2:]))
            elif isinstance(val, bytearray):
                sql.append("{} = ?".format(quote(key.lower())))
                vals.append(bytes(val))
            else:
                sql.append("{} = ?".format(quote(key.lower())))
                vals.append(val)
            join = ","
        if pk:
            if isinstance(pk, list):
                items = pk
            elif isinstance(pk, dict):
                items = pk.items()
            sql.append("\nWHERE")
            join = ""
            for key, val in items:
                if join:
                    sql.append(join)
                if val is None:
                    if "!" in key:
                        key = key.replace("!", "")
                        sql.append("{} is not NULL".format(quote(key.lower())))
                    else:
                        sql.append("{} is NULL".format(quote(key.lower())))
                elif isinstance(val, (tuple, list)):
                    if "!" in key:
                        key = key.replace("!", "")
                        sql.append("{} not in ?".format(quote(key.lower())))
                        vals.append(tuple(val))
                    else:
                        sql.append("{} in ?".format(quote(key.lower())))
                        vals.append(tuple(val))
                else:
                    if "<>" in key:
                        key = key.replace("<>", "")
                        op = "<>"
                    elif "!=" in key:
                        key = key.replace("!=", "")
                        op = "<>"
                    elif "!%" in key:
                        key = key.replace("!%", "")
                        op = "not ilike"
                    elif "%%" in key:
                        key = key.replace("%%", "")
                        op = "%"
                    elif "%>" in key:
                        key = key.replace("%>", "")
                        op = "%>"
                    elif "<%" in key:
                        key = key.replace("<%", "")
                        op = "<%"
                    elif "==" in key:
                        key = key.replace("==", "")
                        op = "="
                    elif "<=" in key:
                        key = key.replace("<=", "")
                        op = "<="
                    elif ">=" in key:
                        key = key.replace(">=", "")
                        op = ">="
                    elif "<" in key:
                        key = key.replace("<", "")
                        op = "<"
                    elif ">" in key:
                        key = key.replace(">", "")
                        op = ">"
                    elif "%" in key:
                        key = key.replace("%", "")
                        op = "ilike"
                    elif "!" in key:
                        key = key.replace("!", "")
                        op = "<>"
                    elif "=" in key:
                        key = key.replace("=", "")
                        op = "="
                    else:
                        op = "="
                    if isinstance(val, str) and val[:2] == "@@":
                        sql.append("{} {} {}".format(quote(key.lower()), op, val[2:]))
                    else:
                        sql.append("{} {} ?".format(quote(key.lower()), op))
                        vals.append(val)
                join = "AND"
        sql = " ".join(sql)
        return sql, tuple(vals)

    @classmethod
    def get_type(cls, v):
        if isinstance(v, str):
            if v[:2] == "@@":
                return v[2:] or cls.TYPES.TEXT
        elif isinstance(v, (str, bytes)) or v is str or v is bytes:
            return cls.TYPES.TEXT
        elif isinstance(v, bool) or v is bool:
            return cls.TYPES.BOOLEAN
        elif isinstance(v, int) or v is int:
            if v is int:
                return cls.TYPES.INTEGER
            if v > 2147483647 or v < -2147483648:
                return cls.TYPES.BIGINT
            else:
                return cls.TYPES.INTEGER
        elif isinstance(v, float) or v is float:
            return cls.TYPES.NUMERIC + "(19, 6)"
        elif isinstance(v, decimal.Decimal) or v is decimal.Decimal:
            return cls.TYPES.NUMERIC + "(19, 6)"
        elif isinstance(v, datetime.datetime) or v is datetime.datetime:
            return cls.TYPES.DATETIME
        elif isinstance(v, datetime.date) or v is datetime.date:
            return cls.TYPES.DATE
        elif isinstance(v, datetime.time) or v is datetime.time:
            return cls.TYPES.TIME
        elif isinstance(v, datetime.timedelta) or v is datetime.timedelta:
            return cls.TYPES.INTERVAL
        elif isinstance(v, bytearray) or v is bytearray:
            return cls.TYPES.BINARY
        # Everything else defaults to TEXT, incl. None
        return cls.TYPES.TEXT

    @classmethod
    def py_type(cls, v):
        v = str(v).upper()
        if v == cls.TYPES.INTEGER:
            return int
        elif v == cls.TYPES.BIGINT:
            return int
        elif v == cls.TYPES.NUMERIC:
            return decimal.Decimal
        elif v == cls.TYPES.TEXT:
            return str
        elif v == cls.TYPES.BOOLEAN:
            return bool
        elif v == cls.TYPES.DATE:
            return datetime.date
        elif v == cls.TYPES.TIME:
            return datetime.time
        elif v == cls.TYPES.DATETIME:
            return datetime.datetime
        elif v == cls.TYPES.INTERVAL:
            return datetime.timedelta
        else:
            raise Exception("unmapped type %s" % v)

    @classmethod
    def massage_data(cls, data):
        """

        :param :
        :param :
        :param :
        :returns:
        """
        data = {key.lower(): val for key, val in data.items()}
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
        sql = []
        null = "NOT NULL" if not null_allowed else ""
        if isinstance(columns, dict):
            for key, val in columns.items():
                sql.append(
                    "ALTER TABLE {} ADD {} {} {};".format(
                        quote(table), quote(key), cls.get_type(val), null
                    )
                )
        return "\n\t".join(sql), tuple()

    @classmethod
    def alter_drop(cls, table, columns):
        sql = ["ALTER TABLE {} DROP COLUMN".format(quote(table))]
        if isinstance(columns, dict):
            for key, val in columns.items():
                sql.append("{},".format(key))
        if sql[-1][-1] == ",":
            sql[-1] = sql[-1][:-1]
        return "\n\t".join(sql), tuple()

    @classmethod
    def alter_column_by_type(cls, table, column, value, null_allowed=True):
        sql = ["ALTER TABLE {} ALTER COLUMN".format(quote(table))]
        sql.append("{} {}".format(quote(column), cls.get_type(value)))
        if not null_allowed:
            sql.append("NOT NULL")
        return "\n\t".join(sql), tuple()

    @classmethod
    def alter_column_by_sql(cls, table, column, value):
        sql = ["ALTER TABLE {} ALTER COLUMN".format(quote(table))]
        sql.append("{} {}".format(quote(column), value))
        return " ".join(sql), tuple()

    # SQLite3 does not support renaming columns, in order to do so the table must be copied to a version with the new column's name
    @classmethod
    def rename_column(cls, table, orig, new):
        # Solves case parity errors
        orig = orig.lower()
        new = new.lower()
        # Get SQL query to generate table
        sql = (
            table.tx.table("sqlite_master")
            .select(columns="sql", where={"name": table.name, "type": "table"})
            .scalar()
        )
        original_name = table.name

        # Splits "CREATE TABLE" portion out to be readded to lines at the end
        sql_data = sql.split("(", 1)

        sql_list = sql_data[1].replace("\n", " ").split(",")
        new_sql_list = []
        for line in sql_list:
            line = line.strip().lower()
            if orig in line:
                if line.index(orig) == 0:
                    new_sql_list.append(line.replace(orig, new, 1))
                elif (line[0] == '"' or line[0] == "'") and line.index(orig) == 1:
                    new_sql_list.append(line.replace(orig, new, 1))
                else:
                    new_sql_list.append(line)
            else:
                new_sql_list.append(line)

        create_db = ",".join(new_sql_list)

        # Adds "CREATE TABLE" portion back into sql code for execution
        create_db = "(".join([sql_data[0], create_db])
        create_db += ";"

        # Rename original table
        table.rename(table.name + "_original_data")

        table.tx.execute(create_db)
        # Create new table with original table name and copy all data from original table
        create_db = "INSERT INTO {} SELECT * FROM {};".format(original_name, table.name)
        return create_db, tuple()

    @classmethod
    def rename_table(cls, table, new):
        return "ALTER TABLE {} RENAME TO {};".format(quote(table), quote(new)), tuple()

    @classmethod
    def create_savepoint(cls, sp):
        return "SAVEPOINT {};".format(sp), tuple()

    @classmethod
    def release_savepoint(cls, sp):
        return "RELEASE SAVEPOINT {};".format(sp), tuple()

    @classmethod
    def rollback_savepoint(cls, sp):
        return "ROLLBACK TO SAVEPOINT {};".format(sp), tuple()

    @classmethod
    def find_duplicates(cls, table, columns, key):
        if isinstance(columns, str):
            columns = [columns]
        return (
            """
        SELECT {2}
        FROM (SELECT {2},
              ROW_NUMBER() OVER (partition BY {1} ORDER BY {2}) AS rnum
            FROM {0}) t
        WHERE t.rnum > 1;
        """.format(
                table, ",".join(quote(columns)), key
            ),
            tuple(),
        )

    @classmethod
    def delete_duplicates(cls, table, columns, key):
        if isinstance(columns, str):
            columns = [columns]
        return (
            """
        DELETE FROM {0}
        WHERE {2} IN (SELECT {2}
              FROM (SELECT {2},
                         ROW_NUMBER() OVER (partition BY {1} ORDER BY {2}) AS rnum
                     FROM {0}) t
              WHERE t.rnum > 1);
        """.format(
                table, ",".join(quote(columns)), key
            ),
            tuple(),
        )

    @classmethod
    def delete(cls, table, where):
        sql = ["DELETE FROM {}".format(table)]
        sql.append("WHERE")
        vals = []
        if isinstance(where, dict):
            join = ""
            for key in sorted(where.keys()):
                if join:
                    sql.append(join)
                if where[key] is None:
                    sql.append("{} is NULL".format(quote(key.lower())))
                else:
                    sql.append("{} = ?".format(quote(key.lower())))
                    vals.append(where[key])
                join = "AND"
        else:
            sql.append(where)
        return " ".join(sql), tuple(vals)

    @classmethod
    def truncate(cls, table):
        return "truncate table {}".format(quote(table)), tuple()

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
        return " ".join(sql), tuple()

    @classmethod
    def drop_view(cls, name, silent=True):
        sql = ["DROP VIEW"]
        if silent:
            sql.append("IF EXISTS")
        sql.append(name)
        return " ".join(sql), tuple()

    class TYPES(object):
        TEXT = "TEXT"
        INTEGER = "INTEGER"
        NUMERIC = "NUMERIC"
        DATETIME = "TIMESTAMP WITHOUT TIME ZONE"
        TIMESTAMP = "TIMESTAMP WITHOUT TIME ZONE"
        DATE = "DATE"
        TIME = "TIME WITHOUT TIME ZONE"
        BIGINT = "BIGINT"
        BOOLEAN = "BOOLEAN"
        BINARY = "BLOB"
        INTERVAL = "INTERVAL"

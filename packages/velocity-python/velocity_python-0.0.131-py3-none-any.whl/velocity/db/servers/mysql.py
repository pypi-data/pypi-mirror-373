import re
import hashlib
import decimal
import datetime
from velocity.db import exceptions
from .mysql_reserved import reserved_words


def initialize(config):
    from velocity.db.core.engine import Engine
    import mysql.connector

    return Engine(mysql.connector, config, SQL)


def make_where(where, sql, vals, is_join=False):
    if not where:
        return
    sql.append("WHERE")
    if isinstance(where, str):
        sql.append(where)
        return
    if isinstance(where, dict):
        where = where.items()
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
                    sql.append("{} not in %s".format(quote(key.lower())))
                    vals.append(tuple(val))
                else:
                    sql.append("{} in %s".format(quote(key.lower())))
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
                    op = "not like"
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
                    op = "like"
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
                    if "like" in op:
                        sql.append(
                            "lower({}) {} lower(%s)".format(quote(key.lower()), op)
                        )
                    else:
                        sql.append("{} {} %s".format(quote(key.lower()), op))
                    vals.append(val)
            join = "AND"


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
            if "`" in part:
                new.append(part)
            elif part.upper() in reserved_words:
                new.append("`" + part + "`")
            elif re.findall("[/]", part):
                new.append("`" + part + "`")
            else:
                new.append(part)
        return ".".join(new)


class SQL:
    server = "MySQL"
    type_column_identifier = "DATA_TYPE"
    is_nullable = "IS_NULLABLE"

    default_schema = "mydb"

    ApplicationErrorCodes = []

    DatabaseMissingErrorCodes = []
    TableMissingErrorCodes = [1146]
    ColumnMissingErrorCodes = [1054]
    ForeignKeyMissingErrorCodes = []

    ConnectionErrorCodes = []
    DuplicateKeyErrorCodes = []  # Handled in regex check.
    RetryTransactionCodes = []
    TruncationErrorCodes = []
    LockTimeoutErrorCodes = []
    DatabaseObjectExistsErrorCodes = []

    def get_error(self, e):
        error_code, error_mesg = e.args[:2]
        return error_code, error_mesg

    @classmethod
    def __has_pointer(cls, columns):
        if columns:
            if isinstance(columns, list):
                columns = ",".join(columns)
            if ">" in columns:
                return True
        return False

    @classmethod
    def alter_add(cls, table, columns, null_allowed=True):
        sql = []
        null = "NOT NULL" if not null_allowed else ""
        if isinstance(columns, dict):
            for key, val in columns.items():
                key = re.sub("<>!=%", "", key.lower())
                sql.append(
                    "ALTER TABLE {} ADD {} {} {};".format(
                        quote(table), quote(key), cls.get_type(val), null
                    )
                )
        return "\n\t".join(sql), tuple()

    @classmethod
    def columns(cls, name):
        if "." in name:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.columns
            WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = %s
            """, tuple(
                name.split(".")
            )
        else:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.columns
            WHERE TABLE_SCHEMA = %s
            """, tuple(
                [
                    name,
                ]
            )

    @classmethod
    def create_foreign_key(
        cls, table, columns, key_to_table, key_to_columns, name=None, schema=None
    ):
        if "." not in table and schema:
            if schema is None:
                schema = cls.default_schema
            table = "{}.{}".format(schema, table)
        if isinstance(key_to_columns, str):
            key_to_columns = [key_to_columns]
        if isinstance(columns, str):
            columns = [columns]
        if not name:
            m = hashlib.md5()
            m.update(table)
            m.update(" ".join(columns))
            m.update(key_to_table)
            m.update(" ".join(key_to_columns))
            name = "FK_" + m.hexdigest()
        sql = "ALTER TABLE {} ADD CONSTRAINT {} FOREIGN KEY ({}) REFERENCES {} ({}) ON DELETE CASCADE ON UPDATE CASCADE;".format(
            table, name, ",".join(columns), key_to_table, ",".join(key_to_columns)
        )

        return sql, tuple()

    @classmethod
    def create_index(
        cls,
        table=None,
        columns=None,
        unique=False,
        direction=None,
        where=None,
        name=None,
        schema=None,
        trigram=None,
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

    @classmethod
    def create_table(cls, name, columns={}, drop=False):
        sql = []
        if drop:
            sql.append(cls.drop_table(name))
        sql.append(
            """
            CREATE TABLE {0} (
              sys_id SERIAL PRIMARY KEY AUTO_INCREMENT,
              sys_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              sys_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )ENGINE=InnoDB AUTO_INCREMENT=1000;
        """.format(
                quote(name)
            )
        )

        for key, val in columns.items():
            key = re.sub("<>!=%", "", key.lower())
            if key in ["sys_id", "sys_created", "sys_modified"]:
                continue
            sql.append(
                "ALTER TABLE {} ADD COLUMN {} {};".format(
                    quote(name), quote(key), cls.get_type(val)
                )
            )
        return "\n\t".join(sql), tuple()

    @classmethod
    def delete(cls, table, where):
        sql = ["DELETE FROM {}".format(table)]
        vals = []
        make_where(where, sql, vals)
        return " ".join(sql), tuple(vals)

    @classmethod
    def drop_table(cls, name):
        return "DROP TABLE IF EXISTS %s CASCADE;" % quote(name), tuple()

    @classmethod
    def foreign_key_info(cls, table=None, column=None, schema=None):
        if "." in table:
            schema, table = table.split(".")

        sql = [
            """
        SELECT
          TABLE_NAME AS FK_TABLE_NAME
          ,COLUMN_NAME AS FK_COLUMN_NAME
          ,CONSTRAINT_NAME AS REFERENCED_CONSTRAINT_NAME
          ,REFERENCED_TABLE_NAME
          ,REFERENCED_COLUMN_NAME
        FROM
          INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        """
        ]
        vals = []
        where = {}
        if schema:
            where["LOWER(REFERENCED_TABLE_SCHEMA)"] = schema.lower()
        if table:
            where["LOWER(REFERENCED_TABLE_NAME)"] = table.lower()
        if column:
            where["LOWER(REFERENCED_COLUMN_NAME)"] = column.lower()
        make_where(where, sql, vals)
        return " ".join(sql), tuple(vals)

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
    def insert(cls, table, data):
        keys = []
        vals = []
        args = []
        for key, val in data.items():
            keys.append(quote(key.lower()))
            if isinstance(val, str) and len(val) > 2 and val[:2] == "@@":
                vals.append(val[2:])
            else:
                vals.append("%s")
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
    def last_id(cls, table):
        return "SELECT LAST_INSERT_ID();", tuple()

    @classmethod
    def create_savepoint(cls, sp):
        return None, tuple()

    @classmethod
    def rollback_savepoint(cls, sp):
        return None, tuple()

    @classmethod
    def release_savepoint(cls, sp):
        return None, tuple()

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

    @classmethod
    def rename_column(cls, table, orig, new):
        return (
            "ALTER TABLE {} RENAME COLUMN {} TO {};".format(
                quote(table), quote(orig), quote(new)
            ),
            tuple(),
        )

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
            is_join = True
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
                    if tables.has_key(lookup):
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
        make_where(where, sql, vals, is_join)
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
            else:
                sql.append("{} = %s".format(quote(key.lower())))
                vals.append(val)
            join = ","
        make_where(pk, sql, vals)
        return " ".join(sql), tuple(vals)

    @classmethod
    def upsert(cls, table, data, pk):
        keys = []
        vals = []
        args = []
        for key, val in data.items():
            keys.append(quote(key.lower()))
            if isinstance(val, str) and len(val) > 2 and val[:2] == "@@":
                vals.append(val[2:])
            else:
                vals.append("%s")
                args.append(val)
        for key, val in pk.items():
            keys.append(quote(key.lower()))
            if isinstance(val, str) and len(val) > 2 and val[:2] == "@@":
                vals.append(val[2:])
            else:
                vals.append("%s")
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
        sql.append("ON DUPLICATE KEY UPDATE")
        join = ""
        for key in data.keys():
            val = data[key]
            if join:
                sql.append(join)
            if isinstance(val, str) and val[:2] == "@@":
                sql.append("{} = {}".format(quote(key.lower()), val[2:]))
            else:
                sql.append("{} = %s".format(quote(key.lower())))
                args.append(val)
            join = ","
        return " ".join(sql), tuple(args)

    @classmethod
    def views(cls, system=False):
        if system:
            return (
                "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables WHERE TABLE_TYPE LIKE 'VIEW';",
                tuple(),
            )
        else:
            return (
                "SELECT TABLE_SCHEMA, TABLE_NAME FROM information_schema.tables WHERE TABLE_TYPE LIKE 'VIEW';",
                tuple(),
            )

    class TYPES(object):
        TEXT = "TEXT"
        INTEGER = "INTEGER"
        NUMERIC = "NUMERIC"
        DATETIME = "DATETIME"
        TIMESTAMP = "TIMESTAMP"
        DATE = "DATE"
        TIME = "TIME"
        BIGINT = "BIGINT"
        SMALLINT = "SMALLINT"
        BOOLEAN = "BIT"
        BINARY = "BLOB"
        INTERVAL = "INTERVAL"

import decimal
import hashlib
import datetime
import re
from velocity.db import exceptions
from .sqlserver_reserved import reserved_words


def initialize(config):
    import pytds
    from velocity.db.core.engine import Engine

    return Engine(pytds, config, SQL)


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
    # for index, value in enumerate(vals):
    #     print "In loop..."
    #     if isinstance(value, (bytearray,buffer)):
    #         print "Converting bytearray to pytds.Binary..."
    #         print value
    #         vals[index] = pytds.Binary(str(value))


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
            if "[" in part:
                new.append(part)
            elif part.upper() in reserved_words:
                new.append("[" + part + "]")
            elif re.findall("[/]", part):
                new.append("[" + part + "]")
            else:
                new.append(part)
        return ".".join(new)


class SQL:
    server = "SQL Server"
    type_column_identifier = "data_type"
    default_schema = "dbo"

    ApplicationErrorCodes = []

    DatabaseMissingErrorCodes = []
    TableMissingErrorCodes = [
        208,
    ]
    ColumnMissingErrorCodes = [207, 1911]
    ForeignKeyMissingErrorCodes = []

    ConnectionErrorCodes = []
    DuplicateKeyErrorCodes = []
    RetryTransactionCodes = []
    TruncationErrorCodes = [
        8152,
    ]
    LockTimeoutErrorCodes = []
    DatabaseObjectExistsErrorCodes = []

    @classmethod
    def version(cls):
        return "select @@version", tuple()

    @classmethod
    def timestamp(cls):
        return "select current_timestamp", tuple()

    @classmethod
    def user(cls):
        return "select current_user", tuple()

    @classmethod
    def databases(cls):
        return "select name from master.dbo.sysdatabases", tuple()

    @classmethod
    def schemas(cls):
        return "select schema_name from information_schema.schemata", tuple()

    @classmethod
    def current_schema(cls):
        return "select schema_name()", tuple()

    @classmethod
    def current_database(cls):
        return "select db_name() as current_database", tuple()

    @classmethod
    def tables(cls, system=False):
        return (
            """
        select table_schema, table_name
        from information_schema.tables
        where table_type = 'BASE TABLE'
        order by table_schema,table_name
        """,
            tuple(),
        )

    @classmethod
    def views(cls, system=False):
        return (
            "SELECT s.name , v.name FROM sys.views v inner join sys.schemas s on s.schema_id = v.schema_id",
            tuple(),
        )

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
    def create_database(cls, name):
        return "create database " + name, tuple()

    @classmethod
    def last_id(cls, table):
        return "SELECT @@IDENTITY", tuple()

    @classmethod
    def drop_database(cls, name):
        return "drop database " + name, tuple()

    @classmethod
    def foreign_key_info(cls, table=None, column=None, schema=None):
        if "." in table:
            schema, table = table.split(".")

        sql = [
            """
        SELECT
             KCU1.CONSTRAINT_NAME AS FK_CONSTRAINT_NAME
            ,KCU1.TABLE_NAME AS FK_TABLE_NAME
            ,KCU1.COLUMN_NAME AS FK_COLUMN_NAME
            ,KCU1.ORDINAL_POSITION AS FK_ORDINAL_POSITION
            ,KCU2.CONSTRAINT_NAME AS REFERENCED_CONSTRAINT_NAME
            ,KCU2.TABLE_NAME AS referenced_table_name
            ,KCU2.COLUMN_NAME AS referenced_column_name
            ,KCU2.ORDINAL_POSITION AS REFERENCED_ORDINAL_POSITION
            ,KCU2.CONSTRAINT_SCHEMA AS referenced_table_schema
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS AS RC

        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KCU1
            ON KCU1.CONSTRAINT_CATALOG = RC.CONSTRAINT_CATALOG
            AND KCU1.CONSTRAINT_SCHEMA = RC.CONSTRAINT_SCHEMA
            AND KCU1.CONSTRAINT_NAME = RC.CONSTRAINT_NAME

        INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KCU2
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
        make_where(where, sql, vals)
        return " ".join(sql), tuple(vals)

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
    def create_table(cls, name, columns={}, drop=False):
        if "." in name:
            fqtn = name
        else:
            fqtn = cls.default_schema + "." + name
        schema, table = fqtn.split(".")
        name = fqtn.replace(".", "_")
        trigger = "on_update_row_{0}".format(name)
        sql = []
        sql.append("DECLARE @script1 nVarChar(MAX);")
        sql.append("DECLARE @script2 nVarChar(MAX);")
        if drop:
            sql.append(cls.drop_table(fqtn))
        sql.append(
            """
            SET @script1 = '
            CREATE TABLE {0} (
              sys_id int identity(1000,1) primary key,
              sys_modified datetime not null default(getdate()),
              sys_created datetime not null default(getdate())
            )'
        """.format(
                fqtn, table, trigger
            )
        )
        sql.append(
            """
            SET @script2 = '
            CREATE TRIGGER {2}
            ON {0}
            AFTER UPDATE
            AS
            BEGIN
                UPDATE t
                SET t.sys_modified = CURRENT_TIMESTAMP,
                    t.sys_created = d.sys_created
                FROM {0} AS t
                INNER JOIN deleted AS d on t.sys_id=i.sys_id
            END'
        """.format(
                fqtn, table, trigger
            )
        )
        sql.append("EXEC (@script1);")
        sql.append("EXEC (@script2);")
        for key, val in columns.items():
            sql.append("ALTER TABLE {} ADD {} {};".format(fqtn, key, cls.get_type(val)))
        return "\n\t".join(sql), tuple()

    @classmethod
    def drop_table(cls, name):
        return (
            "IF OBJECT_ID('%s', 'U') IS NOT NULL DROP TABLE %s;"
            % (
                quote(cls.default_schema + "." + name),
                quote(cls.default_schema + "." + name),
            ),
            tuple(),
        )

    @classmethod
    def columns(cls, name):
        if "." in name:
            return """
            select column_name
            from information_schema.columns
            where table_schema = %s
            and table_name = %s
            """, tuple(
                name.split(".")
            )
        else:
            return """
            select column_name
            from information_schema.columns
            where table_name = %s
            """, tuple(
                [name]
            )

    @classmethod
    def column_info(cls, table, name):
        params = table.split(".")
        params.append(name)
        if "." in table:
            return """
            select *
            from information_schema.columns
            where table_schema = %s
            and table_name = %s
            and column_name = %s
            """, tuple(
                params
            )
        else:
            return """
            select *
            from information_schema.columns
            where table_name = %s
            and column_name = %s
            """, tuple(
                params
            )

    @classmethod
    def primary_keys(cls, table):
        params = table.split(".")
        if "." in table:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
            AND TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, tuple(
                params
            )
        else:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
            AND TABLE_NAME = %s
            """, tuple(
                params
            )

    @classmethod
    def xforeign_keys(cls, table):
        params = table.split(".")
        if "." in table:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
            AND TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, tuple(
                params
            )
        else:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
            AND TABLE_NAME = %s
            """, tuple(
                params
            )

    @classmethod
    def insert(cls, table, data):
        import pytds

        keys = []
        vals = []
        args = []
        for key, val in data.items():
            keys.append(quote(key.lower()))
            if isinstance(val, str) and len(val) > 2 and val[:2] == "@@":
                vals.append(val[2:])
            elif isinstance(val, (bytearray, bytes)):
                vals.append("%s")
                args.append(pytds.Binary(str(val)))
            else:
                vals.append("%s")
                args.append(val)

        sql = []
        if "sys_id" in data:
            sql.append("SET IDENTITY_INSERT {} ON;".format(table))
        sql.append("INSERT INTO")
        sql.append(quote(table))
        sql.append("(")
        sql.append(",".join(keys))
        sql.append(")")
        sql.append("VALUES")
        sql.append("(")
        sql.append(",".join(vals))
        sql.append(");")
        if "sys_id" in data:
            sql.append("SET IDENTITY_INSERT {} OFF;".format(table))
        sql = " ".join(sql)
        return sql, tuple(args)

    @classmethod
    def update(cls, table, data, pk):
        import pytds

        sql = ["UPDATE"]
        sql.append(quote(table))
        sql.append("SET")
        vals = []
        join = ""
        for key in sorted(data.keys()):
            val = data[key]
            if join:
                sql.append(join)
            sql.append("{} = %s".format(quote(key.lower())))
            if isinstance(val, (bytearray, bytes)):
                vals.append(pytds.Binary(str(val)))
            else:
                vals.append(val)
            join = ","
        if pk:
            sql.append("\nWHERE")
            join = ""
            for key in sorted(pk.keys()):
                val = pk[key]
                if join:
                    sql.append(join)
                if val is None:
                    sql.append("{} is null".format(quote(key.lower())))
                else:
                    sql.append("{} = %s".format(quote(key.lower())))
                    vals.append(val)
                join = "AND"
        sql = " ".join(sql)
        return sql, tuple(vals)

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
        print(" ".join(sql))
        return " ".join(sql), tuple()

    @classmethod
    def get_type(cls, v):
        if isinstance(v, str):
            if v[:2] == "@@":
                return v[2:]
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
        elif isinstance(v, (bytearray, bytes)) or v is bytearray or v is bytes:
            return cls.TYPES.BINARY
        # Everything else defaults to TEXT, incl. None
        return cls.TYPES.TEXT

    @classmethod
    def py_type(cls, v):
        v = str(v).upper()
        if v == cls.TYPES.INTEGER:
            return int
        elif v in cls.TYPES.TEXT:
            return str
        elif v == cls.TYPES.BOOLEAN:
            return bool
        elif v == cls.TYPES.DATE:
            return datetime.date
        elif v == cls.TYPES.TIME:
            return datetime.time
        elif v == cls.TYPES.DATETIME:
            return datetime.datetime
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

    @classmethod
    def rename_column(cls, table, orig, new):
        if "." in table:
            schema, table = table.split(".")
        else:
            schema = cls.default_schema
        return (
            "sp_rename '{}.{}.{}', '{}', 'COLUMN';".format(
                quote(schema), quote(table), quote(orig), new
            ),
            tuple(),
        )

    @classmethod
    def rename_table(cls, table, name, new):
        if "." in table:
            schema, table = table.split(".")
        else:
            schema = cls.default_schema
        return (
            "sp_rename '{}.{}', '{}';".format(quote(schema), quote(name), new),
            tuple(),
        )

    @classmethod
    def create_savepoint(cls, sp):
        return None, tuple()

    @classmethod
    def release_savepoint(cls, sp):
        return None, tuple()

    @classmethod
    def rollback_savepoint(cls, sp):
        return None, tuple()

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
                    sql.append("{} = %s".format(quote(key.lower())))
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
        sql.append(cls.default_schema + "." + name)
        sql.append("AS")
        sql.append(query)
        return " ".join(sql), tuple()

    @classmethod
    def drop_view(cls, name, silent=True):
        sql = ["DROP VIEW"]
        if silent:
            sql.append("IF EXISTS")
        sql.append(cls.default_schema + "." + name)
        return " ".join(sql), tuple()

    class TYPES(object):
        TEXT = "VARCHAR(MAX)"
        INTEGER = "INT"
        NUMERIC = "NUMERIC"
        DATETIME = "DATETIME"
        TIMESTAMP = "DATETIME"
        DATE = "DATE"
        TIME = "TIME"
        BIGINT = "BIGINT"
        BOOLEAN = "BIT"
        BINARY = "VARBINARY(MAX)"

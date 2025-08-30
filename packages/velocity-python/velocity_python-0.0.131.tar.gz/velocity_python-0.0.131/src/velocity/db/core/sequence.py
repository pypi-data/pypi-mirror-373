import psycopg2


class Sequence:
    """
    Represents a database sequence in PostgreSQL.
    """

    def __init__(self, tx, name, start=1000):
        self.tx = tx
        self.name = name.lower()
        self.sql = tx.engine.sql
        self.start = start

    def __str__(self):
        return f"Sequence: {self.name} (current val: {self.current()})"

    def create(self, start=None):
        """
        Creates the sequence if it does not already exist.
        """
        val = start if start is not None else self.start
        sql = f"CREATE SEQUENCE IF NOT EXISTS {self.name} START {val};"
        vals = ()
        return self.tx.execute(sql, vals)

    def next(self):
        """
        Retrieves the next value in this sequence.
        """
        sql = f"SELECT nextval('{self.name}');"
        vals = ()
        return self.tx.execute(sql, vals).scalar()

    def current(self):
        """
        Retrieves the current value of the sequence.
        """
        sql = f"SELECT currval('{self.name}');"
        vals = ()
        return self.tx.execute(sql, vals).scalar()

    def safe_current(self):
        """
        Returns the current value of the sequence if one has been generated
        in this session, or None otherwise.
        """
        sql = f"SELECT currval('{self.name}');"
        try:
            return self.tx.execute(sql, ()).scalar()
        except psycopg2.ProgrammingError:
            return None

    def set_value(self, start=None):
        """
        Resets the sequence to the given start value (defaults to initial `self.start`).
        """
        val = start if start is not None else self.start
        sql = f"ALTER SEQUENCE {self.name} RESTART WITH {val};"
        vals = ()
        return self.tx.execute(sql, vals).scalar()

    reset = set_value

    def drop(self):
        """
        Drops the sequence if it exists.
        """
        sql = f"DROP SEQUENCE IF EXISTS {self.name};"
        vals = ()
        return self.tx.execute(sql, vals)

    def exists(self):
        """
        Checks whether the sequence exists in the database.
        Returns True if it exists, False otherwise.
        """
        sql = f"""
            SELECT EXISTS (
                SELECT 1
                FROM pg_class
                WHERE relname = '{self.name}'
                AND relkind = 'S'
            );
        """
        return self.tx.execute(sql, ()).scalar()

    def configure(self, increment=None, minvalue=None, maxvalue=None, cycle=None):
        """
        Alter the sequence with the given settings (any of which may be None to skip).
        """
        parts = []
        if increment is not None:
            parts.append(f"INCREMENT BY {increment}")
        if minvalue is not None:
            parts.append(f"MINVALUE {minvalue}")
        if maxvalue is not None:
            parts.append(f"MAXVALUE {maxvalue}")
        if cycle is True:
            parts.append("CYCLE")
        elif cycle is False:
            parts.append("NO CYCLE")

        if not parts:
            return None  # no-op

        sql = f"ALTER SEQUENCE {self.name} {' '.join(parts)};"
        return self.tx.execute(sql, ()).scalar()

    def info(self):
        """
        Returns a dictionary of metadata about the sequence, or None if it doesn't exist.
        """
        sql = f"""
            SELECT *
            FROM pg_sequences
            WHERE schemaname = current_schema()
            AND sequencename = '{self.name}'
        """
        row = self.tx.execute(sql, ()).fetchone()
        if row is None:
            return None
        return dict(row)

    def rename(self, new_name):
        """
        Renames this sequence to `new_name`. Updates self.name to the new name.
        """
        sql = f"ALTER SEQUENCE {self.name} RENAME TO {new_name.lower()};"
        self.tx.execute(sql, ())
        self.name = new_name.lower()

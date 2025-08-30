class Database:
    """
    Represents a database within a transaction context.
    """

    def __init__(self, tx, name=None):
        self.tx = tx
        self.name = name or self.tx.engine.config["database"]
        self.sql = tx.engine.sql

    def __str__(self):
        return (
            f"Engine: {self.tx.engine.sql.server}\n"
            f"Database: {self.name}\n"
            f"(db exists) {self.exists()}\n"
            f"Tables: {len(self.tables)}\n"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.close()

    def close(self):
        """
        Closes the cursor if it exists.
        """
        try:
            self._cursor.close()
        except AttributeError:
            pass

    def cursor(self):
        """
        Lazy-initialize the cursor on first use.
        """
        try:
            return self._cursor
        except AttributeError:
            self._cursor = self.tx.cursor()
        return self._cursor

    def drop(self):
        """
        Drops this database.
        """
        sql, vals = self.tx.engine.sql.drop_database(self.name)
        self.tx.execute(sql, vals, single=True, cursor=self.cursor())

    def create(self):
        """
        Creates this database.
        """
        sql, vals = self.tx.engine.sql.create_database(self.name)
        self.tx.execute(sql, vals, single=True, cursor=self.cursor())

    def exists(self):
        """
        Returns True if the database exists, else False.
        """
        sql, vals = self.sql.databases()
        result = self.tx.execute(sql, vals, cursor=self.cursor())
        return bool(self.name in [x[0] for x in result.as_tuple()])

    @property
    def tables(self):
        """
        Returns a list of 'schema.table' strings representing tables in this database.
        """
        sql, vals = self.sql.tables()
        result = self.tx.execute(sql, vals, cursor=self.cursor())
        return [f"{x[0]}.{x[1]}" for x in result.as_tuple()]

    def reindex(self):
        """
        Re-indexes this database.
        """
        sql = f"REINDEX DATABASE {self.name}"
        vals = ()
        self.tx.execute(sql, vals, cursor=self.cursor())

    def switch(self):
        """
        Switches the parent transaction to this database.
        """
        self.tx.switch_to_database(self.name)
        return self

    def vacuum(self, analyze=True, full=False, reindex=True):
        """
        Performs VACUUM on this database, optionally FULL, optionally ANALYZE,
        optionally REINDEX.
        """
        # Manually open a separate connection to run VACUUM in isolation_level=0
        conn = self.tx.engine.connect()
        old_isolation_level = conn.isolation_level
        try:
            # Postgres requires VACUUM to run outside a normal transaction block
            conn.set_isolation_level(0)

            # Build up the VACUUM command
            parts = ["VACUUM"]
            if full:
                parts.append("FULL")
            if analyze:
                parts.append("ANALYZE")

            # Execute VACUUM
            with conn.cursor() as cur:
                cur.execute(" ".join(parts))

                # Optionally REINDEX the database
                if reindex:
                    cur.execute(f"REINDEX DATABASE {self.name}")

        finally:
            # Restore isolation level and close the connection
            conn.set_isolation_level(old_isolation_level)
            conn.close()

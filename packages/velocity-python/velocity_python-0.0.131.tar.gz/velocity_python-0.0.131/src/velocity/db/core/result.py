from velocity.misc.format import to_json


class Result:
    """
    Wraps a database cursor to provide various convenience transformations
    (dict, list, tuple, etc.) and helps iterate over query results.

    Features:
    - Pre-fetches first row for immediate boolean evaluation
    - Boolean state changes as rows are consumed: bool(result) tells you if MORE rows are available
    - Supports __bool__, is_empty(), has_results() for checking remaining results
    - Efficient iteration without unnecessary fetchall() calls
    - Caches next row to maintain accurate state without redundant database calls

    Boolean Behavior:
    - Initially: bool(result) = True if query returned any rows
    - After each row: bool(result) = True if more rows are available to fetch
    - After last row: bool(result) = False (no more rows)
    - After one() or scalar(): bool(result) = False (marked as exhausted)
    """

    def __init__(self, cursor=None, tx=None, sql=None, params=None):
        self._cursor = cursor
        # Safely extract headers from cursor description
        try:
            description = getattr(cursor, "description", []) or []
            self._headers = []
            for col in description:
                if hasattr(col, "__getitem__"):  # Tuple-like (col[0])
                    self._headers.append(col[0].lower())
                elif hasattr(col, "name"):  # Object with name attribute
                    self._headers.append(col.name.lower())
                else:
                    self._headers.append(f"column_{len(self._headers)}")
        except (AttributeError, TypeError, IndexError):
            self._headers = []

        self.__as_strings = False
        self.__enumerate = False
        self.__count = -1
        self.__columns = {}
        self.__tx = tx
        self.__sql = sql
        self.__params = params
        self.transform = lambda row: dict(zip(self.headers, row))  # Default transform
        self._cached_first_row = None
        self._first_row_fetched = False
        self._exhausted = False

        # Pre-fetch the first row to enable immediate boolean evaluation
        self._fetch_first_row()

    def _fetch_first_row(self):
        """
        Pre-fetch the first row from the cursor to enable immediate boolean evaluation.
        Only attempts to fetch for SELECT-like operations that return rows.
        """
        if self._first_row_fetched or not self._cursor:
            return

        # Don't try to fetch from INSERT/UPDATE/DELETE operations
        # These operations don't return rows, only rowcount
        if self.__sql and self.__sql.strip().upper().startswith(
            ("INSERT", "UPDATE", "DELETE", "TRUNCATE")
        ):
            self._exhausted = True
            self._first_row_fetched = True
            return

        try:
            raw_row = self._cursor.fetchone()
            if raw_row:
                self._cached_first_row = raw_row
            else:
                self._exhausted = True
        except Exception:
            # If there's an error fetching (e.g., cursor closed), assume no results
            self._exhausted = True
            self._cursor = None  # Mark cursor as invalid
        finally:
            self._first_row_fetched = True

    def __str__(self):
        return repr(self.all())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.close()

    def __bool__(self):
        """
        Return True if there are more rows available to fetch.
        This changes as rows are consumed - after the last row is fetched, this becomes False.
        """
        return self.has_results()

    def is_empty(self):
        """
        Return True if there are no more rows available to fetch.
        """
        return not self.has_results()

    def has_results(self):
        """
        Return True if there are more rows available to fetch.
        This is based on whether we have a cached row or the cursor isn't exhausted.
        """
        return self._cached_first_row is not None or (
            not self._exhausted and self._cursor
        )

    def __next__(self):
        """
        Iterator interface to retrieve the next row.
        """
        # If we have a cached first row, return it and clear the cache
        if self._cached_first_row is not None:
            row = self._cached_first_row
            self._cached_first_row = None
            # Try to pre-fetch the next row to update our state
            self._try_cache_next_row()
        elif not self._exhausted and self._cursor:
            try:
                row = self._cursor.fetchone()
                if not row:
                    self._exhausted = True
                    raise StopIteration
                # Try to pre-fetch the next row to update our state
                self._try_cache_next_row()
            except Exception as e:
                # Handle cursor errors (e.g., closed cursor)
                self._exhausted = True
                self._cursor = None
                if isinstance(e, StopIteration):
                    raise
                raise StopIteration
        else:
            raise StopIteration

        # Apply transformations
        if self.__as_strings:
            row = ["" if x is None else str(x) for x in row]
        if self.__enumerate:
            self.__count += 1
            return (self.__count, self.transform(row))
        return self.transform(row)

    def _try_cache_next_row(self):
        """
        Try to cache the next row to maintain accurate boolean state.
        This is called after we return a row to check if there are more.
        """
        if not self._cursor or self._cached_first_row is not None:
            return

        try:
            next_row = self._cursor.fetchone()
            if next_row:
                self._cached_first_row = next_row
            else:
                self._exhausted = True
        except Exception:
            # If cursor is closed or has error, mark as exhausted
            self._exhausted = True
            self._cursor = None

    def batch(self, qty=1):
        """
        Yields lists (batches) of rows with size = qty until no rows remain.
        """
        results = []
        while True:
            try:
                results.append(next(self))
            except StopIteration:
                if results:
                    yield results
                break
            if len(results) == qty:
                yield results
                results = []

    def all(self):
        """
        Retrieves all rows at once into a list.
        """
        results = []
        while True:
            try:
                results.append(next(self))
            except StopIteration:
                break
        return results

    def __iter__(self):
        return self

    @property
    def headers(self):
        """
        Retrieves column headers from the cursor if not already set.
        """
        if not self._headers and self._cursor and hasattr(self._cursor, "description"):
            self._headers = [x[0].lower() for x in self._cursor.description]
        return self._headers

    @property
    def columns(self):
        """
        Retrieves detailed column information from the cursor.
        Gracefully handles different database types.
        """
        if not self.__columns and self._cursor and hasattr(self._cursor, "description"):
            for column in self._cursor.description:
                data = {"type_name": "unknown"}  # Default value

                # Try to get type information (PostgreSQL specific)
                try:
                    if (
                        hasattr(column, "type_code")
                        and self.__tx
                        and hasattr(self.__tx, "pg_types")
                    ):
                        data["type_name"] = self.__tx.pg_types.get(
                            column.type_code, "unknown"
                        )
                except (AttributeError, KeyError):
                    # Keep default value
                    pass

                # Get all other column attributes safely
                for key in dir(column):
                    if not key.startswith("__"):
                        try:
                            data[key] = getattr(column, key)
                        except (AttributeError, TypeError):
                            # Skip attributes that can't be accessed
                            continue

                column_name = getattr(column, "name", f"column_{len(self.__columns)}")
                self.__columns[column_name] = data
        return self.__columns

    @property
    def cursor(self):
        return self._cursor

    def close(self):
        """
        Closes the underlying cursor if it exists and marks result as exhausted.
        """
        if self._cursor:
            try:
                self._cursor.close()
            except Exception:
                # Ignore errors when closing cursor
                pass
            finally:
                self._cursor = None
        # Mark as exhausted and clear cached data
        self._exhausted = True
        self._cached_first_row = None

    def as_dict(self):
        """
        Transform each row into a dictionary keyed by column names.
        """
        self.transform = lambda row: dict(zip(self.headers, row))
        return self

    def as_json(self):
        """
        Transform each row into JSON (string).
        """
        self.transform = lambda row: to_json(dict(zip(self.headers, row)))
        return self

    def as_named_tuple(self):
        """
        Transform each row into a list of (column_name, value) pairs.
        """
        self.transform = lambda row: list(zip(self.headers, row))
        return self

    def as_list(self):
        """
        Transform each row into a list of values.
        """
        self.transform = lambda row: list(row)
        return self

    def as_tuple(self):
        """
        Transform each row into a tuple of values.
        """
        self.transform = lambda row: row
        return self

    def as_simple_list(self, pos=0):
        """
        Transform each row into the single value at position `pos`.
        """
        self.transform = lambda row: row[pos]
        return self

    def strings(self, as_strings=True):
        """
        Indicate whether retrieved rows should be coerced to string form.
        """
        self.__as_strings = as_strings
        return self

    def scalar(self, default=None):
        """
        Return the first column of the first row, or `default` if no rows.
        After calling this method, the result is marked as exhausted.
        """
        if self._cached_first_row is not None:
            val = self._cached_first_row
            self._cached_first_row = None
            self._exhausted = True  # Mark as exhausted since we only want one value
            return val[0] if val else default
        elif not self._exhausted and self._cursor:
            try:
                val = self._cursor.fetchone()
                self._exhausted = True
                return val[0] if val else default
            except Exception:
                # If cursor error, return default
                self._exhausted = True
                self._cursor = None
                return default
        return default

    def one(self, default=None):
        """
        Return the first row or `default` if no rows.
        After calling this method, the result is marked as exhausted.
        """
        try:
            row = next(self)
            # Mark as exhausted since we only want one row
            self._exhausted = True
            self._cached_first_row = None  # Clear any cached row
            return row
        except StopIteration:
            return default

    def get_table_data(self, headers=True):
        """
        Builds a two-dimensional list: first row is column headers, subsequent rows are data.
        """
        self.as_list()
        rows = []
        for row in self:
            row = ["" if x is None else str(x) for x in row]
            rows.append(row)
        if isinstance(headers, list):
            rows.insert(0, [x.replace("_", " ").title() for x in headers])
        elif headers:
            rows.insert(0, [x.replace("_", " ").title() for x in self.headers])
        return rows

    def enum(self):
        """
        Yields each row as (row_index, transformed_row).
        """
        self.__enumerate = True
        return self

    @property
    def sql(self):
        return self.__sql

    @property
    def params(self):
        return self.__params

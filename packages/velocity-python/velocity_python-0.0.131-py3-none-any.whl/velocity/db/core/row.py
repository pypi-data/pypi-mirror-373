import pprint
from velocity.db.exceptions import DbColumnMissingError


class Row:
    """
    Represents a single row in a given table, identified by a primary key or a dictionary of conditions.
    """

    def __init__(self, table, key, lock=None):
        if isinstance(table, str):
            raise Exception("Table parameter must be a `table` instance.")
        self.table = table

        if isinstance(key, (dict, Row)):
            pk = {}
            try:
                for k in self.key_cols:
                    pk[k] = key[k]
            except KeyError:
                pk = key
        else:
            pk = {self.key_cols[0]: key}

        self.pk = pk
        self.cache = key
        if lock:
            self.lock()

    def __repr__(self):
        return repr(self.to_dict())

    def __str__(self):
        return pprint.pformat(self.to_dict())

    def __len__(self):
        return int(self.table.count(self.pk))

    def __getitem__(self, key):
        if key in self.pk:
            return self.pk[key]
        return self.table.get_value(key, self.pk)

    def __setitem__(self, key, val):
        if key in self.pk:
            raise Exception("Cannot update a primary key.")
        self.table.upsert({key: val}, self.pk)

    def __delitem__(self, key):
        if key in self.pk:
            raise Exception("Cannot delete a primary key.")
        if key not in self:
            return
        self[key] = None

    def __contains__(self, key):
        return key.lower() in [x.lower() for x in self.keys()]

    def clear(self):
        """
        Deletes this row from the database.
        """
        self.table.delete(where=self.pk)
        return self

    def keys(self):
        """
        Returns the column names in the table (including sys_ columns).
        """
        return self.table.sys_columns()

    def values(self, *args):
        """
        Returns values from this row, optionally restricted to columns in `args`.
        """
        d = self.table.select(where=self.pk).as_dict().one()
        if args:
            return [d[arg] for arg in args]
        return list(d.values())

    def items(self):
        """
        Returns (key, value) pairs for all columns.
        """
        d = self.table.select(where=self.pk).as_dict().one()
        return list(d.items())

    def get(self, key, failobj=None):
        try:
            data = self[key]
            if data is None:
                return failobj
            return data
        except DbColumnMissingError:
            # Column doesn't exist in the table, return the default value
            return failobj
        except Exception as e:
            # Check if the error message indicates a missing column
            error_msg = str(e).lower()
            if "column" in error_msg and (
                "does not exist" in error_msg or "not found" in error_msg
            ):
                return failobj
            # Re-raise other exceptions
            raise

    def setdefault(self, key, default=None):
        data = self[key]
        if data is None:
            self[key] = default
            return default
        return data

    def update(self, dict_=None, **kwds):
        """
        Updates columns in this row.
        """
        data = {}
        if dict_:
            data.update(dict_)
        if kwds:
            data.update(kwds)
        if data:
            self.table.upsert(data, self.pk)
        return self

    def __cmp__(self, other):
        """
        Legacy comparison method; returns 0 if self and other share keys/values, else -1.
        """
        diff = -1
        if hasattr(other, "keys"):
            k1 = list(self.keys())
            k2 = list(other.keys())
            if k1 == k2:
                diff = 0
                for k in k1:
                    if self[k] != other[k]:
                        diff = -1
                        break
        return diff

    def __bool__(self):
        return bool(len(self))

    def copy(self, lock=None):
        """
        Makes a copy of this row with a new sys_id, dropping sys_-prefixed columns from the new dict.
        """
        old = self.to_dict()
        for k in list(old.keys()):
            if "sys_" in k:
                old.pop(k)
        return self.table.new(old, lock=lock)

    def pop(self):
        raise NotImplementedError

    def popitem(self):
        raise NotImplementedError

    def __lt__(self, other):
        raise NotImplementedError

    def __gt__(self, other):
        raise NotImplementedError

    def __le__(self, other):
        raise NotImplementedError

    def __ge__(self, other):
        raise NotImplementedError

    @classmethod
    def fromkeys(cls, iterable, value=None):
        raise NotImplementedError

    def to_dict(self):
        """
        Returns the row as a dictionary via a SELECT on self.pk.
        """
        return self.table.select(where=self.pk).as_dict().one()

    def extract(self, *args):
        """
        Returns a dict containing only the specified columns from this row.
        """
        data = {}
        for key in args:
            if isinstance(key, (tuple, list)):
                data.update(self.extract(*key))
            else:
                data[key] = self[key]
        return data

    @property
    def key_cols(self):
        """
        Returns the primary key columns for the underlying table, defaulting to ['sys_id'] if missing.
        """
        return ["sys_id"]

    def split(self):
        """
        Splits data from PK references into (non_sys_data, pk).
        """
        old = self.to_dict()
        for k in list(old.keys()):
            if "sys_" in k:
                old.pop(k)
        return old, self.pk

    @property
    def data(self):
        """
        Returns the 'non-sys' data dictionary for this row.
        """
        return self.split()[0]

    def row(self, key, lock=None):
        """
        Retrieve a row from a foreign key column if present. E.g. row.row('fk_column').
        """
        value = self[key]
        if value is None:
            return None
        fk = self.table.foreign_key_info(key)
        if not fk:
            raise Exception(
                f"Column `{key}` is not a foreign key in `{self.table.name}`"
            )
        return self.table.tx.Row(fk["referenced_table_name"], value, lock=lock)

    def match(self, other):
        """
        Returns True if the columns in 'other' match this row's columns for the same keys.
        """
        for k in other:
            if self[k] != other[k]:
                return False
        return True

    def touch(self):
        """
        Update sys_modified to current timestamp.
        """
        self["sys_modified"] = "@@CURRENT_TIMESTAMP"
        return self

    delete = clear

    def lock(self):
        """
        SELECT ... FOR UPDATE on this row.
        """
        self.table.select(where=self.pk, lock=True)
        return self

    def notBlank(self, key, failobj=None):
        """
        Returns the value if it is not blank, else failobj.
        """
        data = self[key]
        return data if data else failobj

    getBlank = notBlank

    @property
    def sys_id(self):
        return self.pk["sys_id"]

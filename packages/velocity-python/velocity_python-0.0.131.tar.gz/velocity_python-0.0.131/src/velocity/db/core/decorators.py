import time
import random
from functools import wraps
from velocity.db import exceptions


def retry_on_dup_key(func):
    """
    Retries a function call if it raises DbDuplicateKeyError, up to max_retries.
    """

    @wraps(func)
    def retry_decorator(self, *args, **kwds):
        max_retries = 10
        retries = 0
        while retries < max_retries:
            sp = self.tx.create_savepoint(cursor=self.cursor())
            try:
                result = func(self, *args, **kwds)
                self.tx.release_savepoint(sp, cursor=self.cursor())
                return result
            except exceptions.DbDuplicateKeyError:
                self.tx.rollback_savepoint(sp, cursor=self.cursor())
                if "sys_id" in kwds.get("data", {}):
                    raise
                retries += 1
                if retries >= max_retries:
                    raise
                backoff_time = (2**retries) * 0.01 + random.uniform(0, 0.02)
                time.sleep(backoff_time)
        raise exceptions.DbDuplicateKeyError("Max retries reached.")

    return retry_decorator


def reset_id_on_dup_key(func):
    """
    Wraps an INSERT/UPSERT to reset the sys_id sequence on duplicate key collisions.
    """

    @wraps(func)
    def reset_decorator(self, *args, retries=0, **kwds):
        sp = self.tx.create_savepoint(cursor=self.cursor())
        try:
            result = func(self, *args, **kwds)
            self.tx.release_savepoint(sp, cursor=self.cursor())
            return result
        except exceptions.DbDuplicateKeyError:
            self.tx.rollback_savepoint(sp, cursor=self.cursor())
            if "sys_id" in kwds.get("data", {}):
                raise
            if retries < 3:
                backoff_time = (2**retries) * 0.01 + random.uniform(0, 0.02)
                time.sleep(backoff_time)
                self.set_sequence(self.max("sys_id") + 1)
                return reset_decorator(self, *args, retries=retries + 1, **kwds)
        raise exceptions.DbDuplicateKeyError("Max retries reached.")

    return reset_decorator


def return_default(
    default=None,
    exceptions=(
        StopIteration,
        exceptions.DbApplicationError,
        exceptions.DbTableMissingError,
        exceptions.DbColumnMissingError,
        exceptions.DbTruncationError,
        exceptions.DbObjectExistsError,
    ),
):
    """
    If the wrapped function raises one of the specified exceptions, or returns None,
    this decorator returns the `default` value instead.
    """

    def decorator(func):
        func.default = default
        func.exceptions = exceptions

        @wraps(func)
        def wrapper(self, *args, **kwds):
            sp = self.tx.create_savepoint(cursor=self.cursor())
            try:
                result = func(self, *args, **kwds)
                if result is None:
                    result = default
            except func.exceptions:
                self.tx.rollback_savepoint(sp, cursor=self.cursor())
                return default
            self.tx.release_savepoint(sp, cursor=self.cursor())
            return result

        return wrapper

    return decorator


def create_missing(func):
    """
    If the function call fails with DbColumnMissingError or DbTableMissingError, tries to create them and re-run.
    """

    @wraps(func)
    def wrapper(self, *args, **kwds):
        sp = self.tx.create_savepoint(cursor=self.cursor())
        try:
            result = func(self, *args, **kwds)
            self.tx.release_savepoint(sp, cursor=self.cursor())
            return result
        except exceptions.DbColumnMissingError:
            self.tx.rollback_savepoint(sp, cursor=self.cursor())
            data = {}
            if "pk" in kwds:
                data.update(kwds["pk"])
            if "data" in kwds:
                data.update(kwds["data"])
            for i, arg in enumerate(args):
                if isinstance(arg, dict):
                    data.update(arg)
            self.alter(data)
            return func(self, *args, **kwds)
        except exceptions.DbTableMissingError:
            self.tx.rollback_savepoint(sp, cursor=self.cursor())
            data = {}
            if "pk" in kwds:
                data.update(kwds["pk"])
            if "data" in kwds:
                data.update(kwds["data"])
            for i, arg in enumerate(args):
                if isinstance(arg, dict):
                    data.update(arg)
            self.create(data)
            return func(self, *args, **kwds)

    return wrapper

import numbers
import random
import string
from functools import wraps
from velocity.db import exceptions


# TBD implement or delete all this code. It is not used anywhere.
def NotSupported(*args, **kwds):
    raise Exception("Sorry, the driver for this database is not installed")


def NOTNULL(x):
    """Helper function to filter out NULL values from keys/values functions"""
    return len(x) == 2 and x[1] is not None


def pipe(func, primary, secondary, *args, **kwds):
    with primary.transaction() as pri:
        with secondary.transaction() as sec:
            func(pri, sec, *args, **kwds)


class join(object):
    @classmethod
    def _or(cls, *args, **kwargs):
        return "(" + " or ".join(cls._list(*args, **kwargs)) + ")"

    @classmethod
    def _and(cls, *args, **kwargs):
        return "(" + " and ".join(cls._list(*args, **kwargs)) + ")"

    @classmethod
    def _list(cls, *args, **kwargs):
        vals = []
        vals.extend(args)
        for key, val in kwargs.items():
            if isinstance(val, numbers.Number):
                vals.append(f"{key}={val}")
            else:
                vals.append(f"{key}='{val}'")
        return vals


def return_default(default=None):
    """
    Decorator that sets a default value for a function.
    If an exception is raised within the function, the decorator
    catches the exception and returns the default value instead.
    """

    def decorator(f):
        f.default = default

        @wraps(f)
        def return_default(self, *args, **kwds):
            sp = self.tx.create_savepoint(cursor=self.table.cursor)
            try:
                result = f(self, *args, **kwds)
            except (
                exceptions.DbApplicationError,
                exceptions.DbTableMissingError,
                exceptions.DbColumnMissingError,
                exceptions.DbTruncationError,
                StopIteration,
                exceptions.DbObjectExistsError,
            ):
                self.tx.rollback_savepoint(sp, cursor=self.table.cursor)
                return f.default
            self.tx.release_savepoint(sp, cursor=self.table.cursor)
            return result

        return return_default

    return decorator


def randomword(length=None):
    """
    Generate a random word consisting of lowercase letters. This is used to generate random savepoint names.
    The length of the word can be specified, otherwise a random length between 5 and 15 will be used.

    Parameters:
        length (int, optional): The length of the random word. If not provided, a random length between 5 and 15 will be used.

    Returns:
        str: The randomly generated word.
    """
    if length is None:
        length = random.randint(5, 15)
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))

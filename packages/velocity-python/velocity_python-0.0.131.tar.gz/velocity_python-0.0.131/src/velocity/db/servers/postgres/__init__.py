import os
import psycopg2
from .sql import SQL
from velocity.db.core import engine


def initialize(config=None, **kwargs):
    konfig = {
        "database": os.environ["DBDatabase"],
        "host": os.environ["DBHost"],
        "port": os.environ["DBPort"],
        "user": os.environ["DBUser"],
        "password": os.environ["DBPassword"],
    }
    konfig.update(config or {})
    konfig.update(kwargs)
    return engine.Engine(psycopg2, konfig, SQL)

"""Database-related objects and logic."""

from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from ..models.base import Base

Session = sessionmaker()


@event.listens_for(Engine, "connect")
def sqlite_enable_foreign_key_constraints(dbapi_connection, connection_record):
    """Runs the DB commands required to enable foreign key cascades and
    constraints to work in SQLite3.

    """

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init(database_path):
    engine = create_engine("sqlite:///{0}".format(database_path))
    Base.metadata.create_all(bind=engine)
    Session.configure(bind=engine)


@contextmanager
def get_session():
    """Provide a context manager to assist with managing database sessions."""

    s = Session()

    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise

"""Database-related objects and logic."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models.base import Base

Session = sessionmaker()


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

"""Database-related objects and logic."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models.base import Base

engine = create_engine("sqlite:////tmp/posts.db")
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


@contextmanager
def get_session():
    """Provide a context manager to assist with managing database sessions."""

    s = Session()
    yield s

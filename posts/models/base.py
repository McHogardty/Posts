"""Constructs the Base class used by all models."""

from sqlalchemy.ext.declarative import declarative_base


class BaseModel(object):
    def to_dict(self):
        """Generate a dictionary representation of the model instance."""

        return {c.key: getattr(self, c.key) for c in self.__table__.columns
                if not c.foreign_keys}


Base = declarative_base(cls=BaseModel)

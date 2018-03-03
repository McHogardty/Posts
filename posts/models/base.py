"""Constructs the Base class used by all models."""

from sqlalchemy.ext.declarative import declarative_base

from .errors import ModelError


class BaseModel(object):
    def to_dict(self):
        """Generate a dictionary representation of the model instance."""

        return {c.key: getattr(self, c.key) for c in self.__table__.columns
                if not c.foreign_keys}

    @classmethod
    def get(cls, DB, id_):
        return DB.query(cls).filter(cls.id == id_).one()

    @classmethod
    def all(cls, DB):
        return DB.query(cls).all()

    @classmethod
    def create(cls, DB, save=True, **kwargs):
        instance = cls(**kwargs)

        if save:
            DB.add(instance)

        return instance

    @classmethod
    def prepare_updates(cls, **kwargs):
        updates = {}

        for key, value in kwargs.items():
            try:
                updates[getattr(cls, key)] = value
            except AttributeError:
                raise ModelError("{0} model does not have a field named "
                                 "'{1}'".format(cls.__name__, key))

        return updates

    @classmethod
    def update(cls, DB, id_, **kwargs):
        updates = cls.prepare_updates(**kwargs)
        DB.query(cls).filter(cls.id == id_).update(updates)

        return cls.get(DB, id_)

    @classmethod
    def delete(cls, DB, id_):
        DB.query(cls).filter(cls.id == id_).delete()

    @classmethod
    def exists(cls, DB, id_):
        return DB.query(DB.query(cls).filter(cls.id == id_).exists()).scalar()


Base = declarative_base(cls=BaseModel)

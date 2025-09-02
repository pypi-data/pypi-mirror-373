from sqlalchemy.orm import declarative_base

from .session import get_db_session


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, commit=True, db=None, **kwargs):
        """Create a new record and save it the database."""

        def __create(_instance):
            if commit:
                db.add(_instance)
                db.commit()
                return _instance
            else:
                db.add(_instance)
                db.flush()
                return _instance

        instance = cls(**kwargs)
        if db:
            return __create(_instance=instance)
        else:
            with get_db_session() as db:
                return __create(_instance=instance)

    def update(self, commit=True, db=None, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)

        def _update(_obj, _db):
            if _db:
                _db.add(_obj)
                if commit:
                    _db.commit()
                else:
                    _db.flush()
                return self
            else:
                with get_db_session() as _db:
                    _db.add(_obj)
                    if commit:
                        _db.commit()
                    else:
                        _db.flush()
                    return _obj

        return _update(self, _db=db)

    def delete(self, commit=True, db=None):
        """Remove the record from the database."""
        if db:
            db.delete(self)
            return commit and db.commit()
        else:
            with get_db_session() as db:
                db.delete(self)
                return commit and db.commit()

    def soft_delete(self, commit=True, db=None):
        """Remove the record from the database."""
        return self.update(commit=commit, db=db, **{
            'active': False
        })


Base = declarative_base()


class Model(CRUDMixin, Base):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

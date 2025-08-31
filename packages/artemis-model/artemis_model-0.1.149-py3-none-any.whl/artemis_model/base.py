import re
from datetime import datetime
from typing import Any

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    object_session,
    relationship,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Column, Uuid, event, inspect, TypeDecorator
from sqlalchemy.dialects.postgresql import TSVECTOR


def resolve_table_name(name: str) -> str:
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


class CustomBase(DeclarativeBase, AsyncAttrs):
    __repr_attrs__: list[Any] = []
    __repr_max_length__ = 15

    @declared_attr
    def __tablename__(self) -> str:
        return resolve_table_name(self.__name__)

    def dict(self) -> dict:
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @property
    def _id_str(self) -> str:
        ids = inspect(self).identity
        if ids:
            return "-".join([str(x) for x in ids]) if len(ids) > 1 else str(ids[0])
        else:
            return "None"

    @property
    def _repr_attrs_str(self) -> str:
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError(
                    "{} has incorrect attribute '{}' in " "__repr__attrs__".format(
                        self.__class__, key
                    )
                )
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, str)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."

            if wrap_in_quote:
                value = "'{}'".format(value)
            values.append(value if single else "{}:{}".format(key, value))

        return " ".join(values)

    def __repr__(self) -> str:
        # get id like '#123'
        id_str = ("#" + self._id_str) if self._id_str else ""
        # join class name, id and repr_attrs
        return "<{} {}{}>".format(
            self.__class__.__name__,
            id_str,
            " " + self._repr_attrs_str if self._repr_attrs_str else "",
        )


class AuditMixin(object):
    created_by = Column(Uuid, nullable=True)
    updated_by = Column(Uuid, nullable=True)

    @declared_attr
    def created_by_user(cls):
        return relationship(
            "User",
            foreign_keys=[cls.created_by],
            primaryjoin="User.id==%s.created_by" % cls.__name__,
        )

    @declared_attr
    def updated_by_user(cls):
        return relationship(
            "User",
            foreign_keys=[cls.updated_by],
            primaryjoin="User.id==%s.updated_by" % cls.__name__,
        )

    @staticmethod
    def _updated_info(mapper: Any, connection: Any, target: Any) -> None:
        s = object_session(target)
        target.updated_at = datetime.utcnow()
        if user_id := getattr(s, "user_id", None):
            target.updated_by = user_id

    @staticmethod
    def _created_info(mapper: Any, connection: Any, target: Any) -> None:
        s = object_session(target)
        if user_id := getattr(s, "user_id", None):
            target.created_by = user_id

    @classmethod
    def get_session_user_id(cls, connection):
        return connection.info.get("user_id")

    @classmethod
    def __declare_last__(cls) -> None:
        event.listen(cls, "before_insert", cls._created_info)
        event.listen(cls, "before_update", cls._updated_info)


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)


# class InheritanceMixin(object):
#     @declared_attr
#     def __mapper_args__(cls):
#         return {
#             'polymorphic_identity': cls.__name__.lower(),
#         }


# class CustomBase(Base, AsyncAttrs):
#     pass


# class SyncInheritanceMixin(object):
#     type = Column(String(50))

#     @declared_attr
#     def __mapper_args__(cls):
#         return {
#             'polymorphic_identity': cls.__name__.lower(),
#             'polymorphic_on': 'type',
#         }


class CustomSyncBase(DeclarativeBase):
    __repr_attrs__: list[Any] = []
    __repr_max_length__ = 15
    __abstract__ = True

    @declared_attr
    def __tablename__(self) -> str:
        return resolve_table_name(self.__name__)

    """ Is this missed here or not moved intentionally?"""

    # def serializable_dict(self) -> Dict[str, Any]:
    #     d = {col.name: getattr(self, col.name) for col in self.__table__.columns}
    #     return orjson.loads(orjson.dumps(jsonable_encoder(d)))

    def dict(self) -> dict:
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @property
    def _id_str(self) -> str:
        ids = inspect(self).identity
        if ids:
            return "-".join([str(x) for x in ids]) if len(ids) > 1 else str(ids[0])
        else:
            return "None"

    @property
    def _repr_attrs_str(self) -> str:
        max_length = self.__repr_max_length__

        values = []
        single = len(self.__repr_attrs__) == 1
        for key in self.__repr_attrs__:
            if not hasattr(self, key):
                raise KeyError(
                    "{} has incorrect attribute '{}' in " "__repr__attrs__".format(
                        self.__class__, key
                    )
                )
            value = getattr(self, key)
            wrap_in_quote = isinstance(value, str)

            value = str(value)
            if len(value) > max_length:
                value = value[:max_length] + "..."

            if wrap_in_quote:
                value = "'{}'".format(value)
            values.append(value if single else "{}:{}".format(key, value))

        return " ".join(values)

    def __repr__(self) -> str:
        # get id like '#123'
        id_str = ("#" + self._id_str) if self._id_str else ""
        # join class name, id and repr_attrs
        return "<{} {}{}>".format(
            self.__class__.__name__,
            id_str,
            " " + self._repr_attrs_str if self._repr_attrs_str else "",
        )


class TSVector(TypeDecorator):
    impl = TSVECTOR

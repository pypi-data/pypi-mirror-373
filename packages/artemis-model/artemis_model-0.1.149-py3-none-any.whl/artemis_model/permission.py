import uuid
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import TimeStampMixin, CustomSyncBase, CustomBase

from sqlalchemy.ext.declarative import declared_attr


class PermissionMixin(TimeStampMixin):
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(
        nullable=False
    )  # music-management, player-management, user-management

    @declared_attr
    def user_permission_associations(cls) -> Mapped[List["UserPermissionAssoc"]]:
        return relationship(back_populates="permission", cascade="all, delete-orphan")


class UserPermissionAssocMixin(TimeStampMixin):
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    permission_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("permission.id"), primary_key=True)

    @declared_attr
    def permission(cls) -> Mapped["Permission"]:
        return relationship(back_populates="user_permission_associations")


class UserPermissionAssocSync(CustomSyncBase, UserPermissionAssocMixin):
    pass


class UserPermissionAssoc(CustomBase, UserPermissionAssocMixin):
    pass


class PermissionSync(CustomSyncBase, PermissionMixin):
    pass


class Permission(CustomBase, PermissionMixin):
    pass

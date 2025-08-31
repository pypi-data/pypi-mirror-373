import uuid
from typing import List

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from artemis_model.base import TimeStampMixin, CustomSyncBase, CustomBase
from artemis_model.permission import UserPermissionAssoc
from sqlalchemy.ext.declarative import declared_attr


class UserMixin(TimeStampMixin):
    """
    This table is used to store the user itself.
    """

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_account.id"), nullable=False, index=True
    )

    @declared_attr
    def user_location_associations(cls) -> Mapped[List["UserLocationAssoc"]]:
        return relationship(
            back_populates="user",
            cascade="all, delete-orphan",
        )

    @declared_attr
    def user_permission_associations(cls) -> Mapped[List["UserPermissionAssoc"]]:
        return relationship(
            cascade="all, delete-orphan",
        )

    @declared_attr
    def account(cls) -> Mapped["UserAccount"]:
        return relationship("UserAccount", back_populates="user")

    @declared_attr
    def organizations(cls) -> Mapped[List["Organization"]]:
        return relationship(secondary="organization_user_assoc", back_populates="users")

    @declared_attr
    def locations(cls) -> Mapped[List["Location"]]:
        return relationship(secondary="user_location_assoc", viewonly=True)

    @declared_attr
    def permission_ids(cls) -> AssociationProxy[List["Permission"] | None]:
        return association_proxy(
            "user_permission_associations",
            "permission",
            creator=lambda permission_id: UserPermissionAssoc(permission_id=permission_id),
        )

    @declared_attr
    def permissions(cls) -> Mapped[list["Permission"]]:
        return relationship(secondary="user_permission_assoc", viewonly=True)


class UserSync(CustomSyncBase, UserMixin):
    pass


class User(CustomBase, UserMixin):
    pass

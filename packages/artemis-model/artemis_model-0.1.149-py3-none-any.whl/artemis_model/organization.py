import uuid
from typing import Any, List

from slugify import slugify
from sqlalchemy import UUID, ForeignKey
from sqlalchemy.event import listen
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomSyncBase, TimeStampMixin, CustomBase

from sqlalchemy.ext.declarative import declared_attr


class OrganizationMixin(TimeStampMixin):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    slug: Mapped[str] = mapped_column(nullable=False, index=True)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)

    @declared_attr
    def locations(cls) -> Mapped[List["Location"]]:
        return relationship(back_populates="organization")

    @declared_attr
    def dj_sets(cls) -> Mapped[List["DjSet"]]:
        return relationship(back_populates="organization")

    @declared_attr
    def users(cls) -> Mapped[List["User"]]:
        return relationship(secondary="organization_user_assoc", back_populates="organizations")

    @declared_attr
    def messages(cls) -> Mapped[List["Message"]]:
        return relationship(back_populates="organization")

    @declared_attr
    def message_groups(cls) -> Mapped[List["MessageGroup"]]:
        return relationship(back_populates="organization")


def generate_slug(target: Any, value: Any, old_value: Any, initiator: Any) -> None:
    """Creates a reasonable slug based on organization name."""
    if value and (not target.slug or value != old_value):
        target.slug = slugify(value, separator="_")


class OrganizationSync(CustomSyncBase, OrganizationMixin):
    pass


listen(OrganizationSync.name, "set", generate_slug)


class Organization(CustomBase, OrganizationMixin):
    pass


listen(Organization.name, "set", generate_slug)


class OrganizationUserAssocMixin(TimeStampMixin):
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organization.id"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)


class OrganizationUserAssocSync(CustomSyncBase, OrganizationUserAssocMixin):
    pass


class OrganizationUserAssoc(CustomBase, OrganizationUserAssocMixin):
    pass

import uuid
from typing import Any, List

from slugify import slugify
from sqlalchemy import UUID, ForeignKey
from sqlalchemy.event import listen
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import TimeStampMixin, CustomSyncBase, CustomBase

from sqlalchemy.ext.declarative import declared_attr


class AddressMixin:
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    street: Mapped[str] = mapped_column(nullable=False)
    street2: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)
    zip_code: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=False)

    @declared_attr
    def location(cls) -> Mapped["Location"]:
        return relationship(
            uselist=False,
            back_populates="address",
        )


class AddressSync(CustomSyncBase, AddressMixin):
    pass


class Address(CustomBase, AddressMixin):
    pass


class LocationMixin(TimeStampMixin):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organization.id"), nullable=False, index=True
    )
    location_type: Mapped[str] = mapped_column(nullable=True)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("location_group.id"), nullable=True, index=True
    )

    address_id = mapped_column(ForeignKey("address.id"), nullable=True)
    legacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)

    @declared_attr
    def organization(cls) -> Mapped["Organization"]:
        return relationship(back_populates="locations")

    @declared_attr
    def group(cls) -> Mapped["LocationGroup"]:
        return relationship(back_populates="locations")

    @declared_attr
    def zones(cls) -> Mapped[list["Zone"]]:
        return relationship(back_populates="location")

    @declared_attr
    def users(cls) -> AssociationProxy[list["User"]]:
        return association_proxy(
            "user_location_associations",
            "user",
            creator=lambda user_id: UserLocationAssoc(user_id=user_id),
        )

    @declared_attr
    def address(cls) -> Mapped["Address"]:
        return relationship(
            uselist=False,
            back_populates="location",
        )

    @declared_attr
    def user_location_associations(cls) -> Mapped[list["UserLocationAssoc"]]:
        return relationship(
            cascade="all, delete-orphan",
        )

    @declared_attr
    def genre_exclusions(cls) -> Mapped[list["LocationGenreExclusion"]]:
        return relationship(
            "LocationGenreExclusion",
            back_populates="location",
            cascade="all, delete-orphan",
        )

    timezone: Mapped[str] = mapped_column(nullable=False, default="America/New_York")


def generate_slug(target: Any, value: Any, old_value: Any, initiator: Any) -> None:
    """Creates a reasonable slug based on location name."""
    if value and (not target.slug or value != old_value):
        target.slug = slugify(value, separator="_")


class LocationSync(CustomSyncBase, LocationMixin):
    pass


listen(LocationSync.name, "set", generate_slug)


class Location(CustomBase, LocationMixin):
    pass


listen(Location.name, "set", generate_slug)


class LocationGroupMixin(TimeStampMixin):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    organization_id = mapped_column(ForeignKey("organization.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)

    @declared_attr
    def locations(cls) -> Mapped[List["Location"]]:
        return relationship(
            back_populates="group",
        )


class LocationGroupSync(CustomSyncBase, LocationGroupMixin):
    pass


class LocationGroup(CustomBase, LocationGroupMixin):
    pass


class UserLocationAssocMixin(TimeStampMixin):
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("location.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship(back_populates="user_location_associations")


class UserLocationAssocSync(CustomSyncBase, UserLocationAssocMixin):
    pass


class UserLocationAssoc(CustomBase, UserLocationAssocMixin):
    pass

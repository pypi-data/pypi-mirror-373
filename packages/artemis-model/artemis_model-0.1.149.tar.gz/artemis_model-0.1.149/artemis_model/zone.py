import uuid

from sqlalchemy import UUID, Boolean, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomBase, TimeStampMixin, CustomSyncBase

from sqlalchemy.ext.declarative import declared_attr


class ZoneMixin(TimeStampMixin):
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Player relations will be added later.
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("location.id"), index=True
    )
    message_frequency: Mapped[int] = mapped_column(nullable=False, default=1)
    legacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)

    @declared_attr
    def location(cls) -> Mapped["Location"]:
        return relationship(back_populates="zones")

    @declared_attr
    def schedules(cls) -> Mapped[list["Schedule"]]:
        return relationship(back_populates="zone")

    @declared_attr
    def message_play_details(cşs) -> Mapped[list["MessagePlayDetail"]]:
        return relationship(back_populates="zone")

    @declared_attr
    def license(cls) -> Mapped["License"]:
        return relationship(back_populates="zone", uselist=False)

    @declared_attr
    def setting(cls) -> Mapped["Setting"]:
        return relationship(back_populates="zone", uselist=False)


class ZoneSync(CustomSyncBase, ZoneMixin):
    pass


class Zone(CustomBase, ZoneMixin):
    pass


class LicenseMixin(TimeStampMixin):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zone.id"), nullable=False)
    license_type: Mapped[str] = mapped_column(nullable=False, default="FREE")
    valid_until: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    expired: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    @declared_attr
    def zone(cls) -> Mapped["Zone"]:
        return relationship(back_populates="license", uselist=False)


class LicenseSync(CustomSyncBase, LicenseMixin):
    pass


class License(CustomBase, LicenseMixin):
    pass

from datetime import datetime
from typing import Annotated, NotRequired
from typing_extensions import TypedDict
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, UUID
from pydantic import Field, RootModel, BaseModel

from artemis_model.base import CustomBase, TimeStampMixin, AuditMixin, CustomSyncBase

from sqlalchemy.ext.declarative import declared_attr


class ScheduleMixin(TimeStampMixin, AuditMixin):
    """
    This table is used to store the schedule of a zone.
    """

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zone.id"), index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    timesheet: Mapped[JSON] = mapped_column(JSON, nullable=True)
    locked_by: Mapped[str] = mapped_column(default=None, nullable=True)
    legacy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)

    @declared_attr
    def zone(cls) -> Mapped["Zone"]:
        return relationship(back_populates="schedules")


class ScheduleSync(CustomSyncBase, ScheduleMixin):
    pass


class Schedule(CustomBase, ScheduleMixin):
    pass


class SchedulePresetMixin(TimeStampMixin, AuditMixin):
    """
    This table is used to store preset schedules regarding location type.
    """

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    type: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    timesheet: Mapped[JSON] = mapped_column(JSON, nullable=True)


class SchedulePresetSync(CustomSyncBase, SchedulePresetMixin):
    pass


class SchedulePreset(CustomBase, SchedulePresetMixin):
    pass


class TimeslotData(TypedDict):
    """Timeslot data schema."""

    p: NotRequired[list[int]]
    d: NotRequired[list[int]]
    scheduled_at: NotRequired[datetime]


class Timesheet(RootModel):
    """Timesheet schema."""

    root: dict[Annotated[str, Field(pattern=r"^\d{2}:\d{2}$")], TimeslotData]


class ScheduleItem(BaseModel):
    """Schedule item schema."""

    zone_id: int
    timesheet: Timesheet


__all__ = [
    "ScheduleItem",
    "Timesheet",
    "TimeslotData",
    "SchedulePreset",
    "SchedulePresetSync",
    "ScheduleSync",
    "Schedule",
]

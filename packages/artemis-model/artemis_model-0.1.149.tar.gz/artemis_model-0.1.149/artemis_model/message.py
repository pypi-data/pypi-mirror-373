import uuid
from typing import List
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomSyncBase, TimeStampMixin, AuditMixin, CustomBase

from sqlalchemy.ext.declarative import declared_attr


class MessageMixin(TimeStampMixin, AuditMixin):
    """
    This table is used to store the message.
    """

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    s3_link: Mapped[str] = mapped_column(nullable=False)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organization.id"), nullable=False, index=True
    )
    message_group_id: Mapped[int] = mapped_column(
        ForeignKey("message_group.id"), nullable=True, index=True, default=None
    )

    @declared_attr
    def organization(cls) -> Mapped["Organization"]:
        return relationship("Organization", back_populates="messages")

    @declared_attr
    def message_group(cls) -> Mapped["MessageGroup"]:
        return relationship("MessageGroup", back_populates="messages")

    @declared_attr
    def play_details(cls) -> Mapped[List["MessagePlayDetail"]]:
        return relationship("MessagePlayDetail", back_populates="message")


class MessageSync(CustomSyncBase, MessageMixin):
    pass


class Message(CustomBase, MessageMixin):
    pass


class MessagePlayDetailMixin(TimeStampMixin, AuditMixin):
    """
    This table is used to store the message play details.
    Frequency is used only for rotated messages.
    Timesheet is used only for scheduled messages.
    """

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("message.id"), nullable=False, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zone.id"), index=True)

    type: Mapped[str] = mapped_column(nullable=False)

    timesheet: Mapped[JSON] = mapped_column(JSON, nullable=True)

    @declared_attr
    def message(cls) -> Mapped["Message"]:
        return relationship("Message", back_populates="play_details")

    @declared_attr
    def zone(cls) -> Mapped["Zone"]:
        return relationship("Zone", back_populates="message_play_details")


class MessagePlayDetailSync(CustomSyncBase, MessagePlayDetailMixin):
    pass


class MessagePlayDetail(CustomBase, MessagePlayDetailMixin):
    pass


class MessageGroupMixin(TimeStampMixin, AuditMixin):
    """
    This table is used to store the message group.
    """

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organization.id"), nullable=False, index=True
    )

    @declared_attr
    def organization(cls) -> Mapped["Organization"]:
        return relationship("Organization", back_populates="message_groups")

    @declared_attr
    def messages(cls) -> Mapped[List["Message"]]:
        return relationship(back_populates="message_group")


class MessageGroupSync(CustomSyncBase, MessageGroupMixin):
    pass


class MessageGroup(CustomBase, MessageGroupMixin):
    pass

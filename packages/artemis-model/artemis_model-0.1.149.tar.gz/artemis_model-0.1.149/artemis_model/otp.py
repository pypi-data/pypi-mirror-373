import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from artemis_model.base import TimeStampMixin, CustomBase, CustomSyncBase


class OtpMixin(TimeStampMixin):
    """
    This table is used to store the OTPs.
    requested_by can be an UserAccount or UserUnverifiedAccount id.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    purpose: Mapped[str] = mapped_column(nullable=False)
    requested_by_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    method: Mapped[str] = mapped_column(nullable=False, index=True)
    secret: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class OtpSync(CustomSyncBase, OtpMixin):
    pass


class Otp(CustomBase, OtpMixin):
    pass

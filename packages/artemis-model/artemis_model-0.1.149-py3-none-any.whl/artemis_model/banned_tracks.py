"""Banned Tracks per Zone Model"""

from sqlalchemy import UUID, Integer
from sqlalchemy.orm import Mapped, mapped_column
from artemis_model.base import AuditMixin, TimeStampMixin, CustomSyncBase, CustomBase


class BannedTracksMixin(TimeStampMixin, AuditMixin):
    """Banned Tracks per Zone Model"""

    zone_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    track_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)


class BannedTracksSync(CustomSyncBase, BannedTracksMixin):
    """Banned Tracks per Zone Model"""

    pass


class BannedTracks(CustomBase, BannedTracksMixin):
    """Banned Tracks per Zone Model"""

    pass

"""Zone Activity Model"""

from enum import StrEnum
from sqlalchemy import Integer, String, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from artemis_model.base import AuditMixin, TimeStampMixin, CustomSyncBase, CustomBase


class ZoneActivityType(StrEnum):
    """Zone activity type"""

    CONNECTED = "connected"
    CONNECTION_MODE_CHANGED = "connection_mode_changed"
    DISCONNECTED = "disconnected"
    PLAYER_PAUSED = "player_paused"
    PLAYER_RESUMED = "player_resumed"
    TRACK_SKIPPED = "track_skipped"
    TRACK_LIKED = "track_liked"
    TRACK_BANNED = "track_banned"
    TRACK_UNBANNED = "track_unbanned"
    PLAYLIST_PUSHED = "playlist_pushed"
    PLAYLIST_EXPIRED = "playlist_expired"
    ACTIVE_PLAYLIST_CHANGED = "active_playlist_changed"


class PlayerActivityMixin(TimeStampMixin, AuditMixin):
    """User activity log, sorted by created_at DESC for retrieval"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer, nullable=False)
    activity_type: Mapped[str] = mapped_column(String, nullable=False)
    activity_data: Mapped[dict] = mapped_column(JSON, nullable=True)


Index("idx_player_activity_player_created", "player_id", PlayerActivityMixin.created_at.desc())
Index("idx_player_activity_created", PlayerActivityMixin.created_at.desc())


class PlayerActivitySync(CustomSyncBase, PlayerActivityMixin):
    """Sync model for Player Activity"""

    pass


class PlayerActivity(CustomBase, PlayerActivityMixin):
    """Base model for Player Activity"""

    pass

"""Redis track buckets"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from datetime import datetime, timezone
import uuid


TrackId = Annotated[uuid.UUID, Field(description="Track ID (UUID)")]

PlaylistId = Annotated[int, Field(description="Playlist ID (integer)")]

Timestamp = Annotated[int, Field(description="Unix timestamp")]


class RedisTrackBucketItem(BaseModel):
    """
    Represents a composite Redis key along with a timestamp.
    The Redis entry will be:
    { '{"track_id": "...", "playlist_id": ...}': ts }
    ts is the timestamp of utc now.
    """

    track_id: TrackId
    playlist_id: PlaylistId
    ts: Timestamp = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))

    model_config = ConfigDict(json_encoders={uuid.UUID: str}, populate_by_name=True)

    def as_redis_entry(self) -> dict[str, int]:
        """
        Generate a Redis-ready dictionary:
        { '{"track_id": "...", "playlist_id": ...}': ts }
        """
        key = self.model_dump_json(include={"track_id", "playlist_id"})
        return {key: self.ts}

    @classmethod
    def from_redis_entry(cls, entry: dict[str, int]) -> "RedisTrackBucketItem":
        """
        Parse a Redis entry into a RedisTrackBucketItem.
        """
        return cls.model_validate_json(list(entry.keys())[0])


class RedisTrackBucketItemValue(BaseModel):
    """JSON string format for Redis keys: '{"track_id": "...", "playlist_id": ...}'"""

    track_id: TrackId
    playlist_id: PlaylistId

"""Redis play history"""

from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime, timezone


TrackId = Annotated[str, Field(description="Track ID (UUID or string)")]

Timestamp = Annotated[int, Field(description="Unix timestamp")]


class RedisTrackPlayHistoryItem(BaseModel):
    """
    Represents the value stored in Redis sorted set:
    A string like "track_id#timestamp"
    """

    track_id: TrackId
    ts: Timestamp = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))

    def as_redis_entry(self) -> str:
        """
        Generate a Redis-ready string:
        "track_id#timestamp"
        """
        return f"{self.track_id}#{self.ts}"

    @classmethod
    def from_redis_entry(cls, value: str) -> "RedisTrackPlayHistoryItem":
        """
        Parse a Redis entry into a TrackPlayHistoryValue.
        """
        try:
            value = value.decode("utf-8") if isinstance(value, bytes) else value
            track_id, ts = value.rsplit("#", 1)
            return cls(track_id=track_id, ts=int(ts))
        except Exception as e:
            raise ValueError(f"Invalid format for TrackPlayHistoryValue: {value}") from e


__all__ = [
    "RedisTrackPlayHistoryItem",
]

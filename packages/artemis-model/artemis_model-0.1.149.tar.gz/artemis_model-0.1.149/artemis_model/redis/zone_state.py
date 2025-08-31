"""Zone state schema."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


class NowPlaying(BaseModel):
    """Now playing schema."""

    name: str = Field(description="The name of the track", default="UNKNOWN")
    artist_name: str = Field(description="The artist name of the track", default="UNKNOWN")
    album_name: str = Field(description="The album name of the track", default="UNKNOWN")
    playlist_id: int | None = Field(description="The playlist id of the track", default=None)


SessionId = Annotated[
    int,
    Field(
        description="The session id of the pushed playlist. It's generated as a timestamp value of the current time."
    ),
]
BucketTS = Annotated[
    int | None,
    Field(
        description="The bucket id of the pushed playlist. It's calculated as the timestamp value of the timeslot."
    ),
]


class PlaylistSimple(BaseModel):
    """Simple playlist schema."""

    id: int = Field(
        description="The id of the pushed playlist. It's generated as a timestamp value of the current time."
    )
    name: str = Field(
        description="The name of the pushed playlist",
    )


class ScheduleDetails(BaseModel):
    """Schedule details schema."""

    start_at: datetime | None = Field(
        default=None,
        description="The date and time value of the schedule in local timezone.",
    )
    playlists: list[PlaylistSimple] | None = Field(
        default=None,
        description="The playlist of the schedule",
    )


class PushedPlaylistDetails(BaseModel):
    """Player details schema."""

    bucket_ts: BucketTS | None = Field(
        default_factory=dict,
        description="""Pushed playlists does exist in Redis with a timestamp.
        Example: zone_{zone_id}_pp_bucket_{ts}
        """,
    )
    playlists: list[PlaylistSimple] | None = Field(
        default=None,
        description="The playlists of the pushed playlist",
    )
    expire_at: datetime | None = Field(
        default=None,
        description="The expire time of the pushed playlist",
    )
    expiry_type: Literal["infinite", "auto_expire"] | None = Field(
        default=None,
        description="The expiry type of the pushed playlist",
    )


class ZoneState(BaseModel):
    """Zone state schema."""

    player_mode: Literal["scheduled", "pushplaylist"] = Field(
        default="scheduled",
        description="The mode of the player",
    )
    player_state: Literal["playing", "paused", "stopped", "ready"] = Field(
        default="ready",
        description="The state of the player",
    )
    now_playing: NowPlaying | None = Field(
        default=None,
        description="The currently playing track",
    )
    pp_details: PushedPlaylistDetails | None = Field(
        default=None,
        description="The details of the pushed playlist",
    )
    schedule_details: ScheduleDetails | None = Field(
        default=None,
        description="The details of the schedule",
    )


__all__ = [
    "ZoneState",
    "NowPlaying",
    "SessionId",
    "BucketTS",
    "PlaylistSimple",
    "PushedPlaylistDetails",
    "ScheduleDetails",
]

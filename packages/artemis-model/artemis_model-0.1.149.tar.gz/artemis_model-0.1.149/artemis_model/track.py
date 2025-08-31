import uuid
from datetime import datetime
from typing import List

from sqlalchemy import UUID, Computed, ForeignKey, func, literal, text, ARRAY, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomBase, CustomSyncBase, TSVector, TimeStampMixin

from sqlalchemy.ext.declarative import declared_attr


def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector(literal("english"), text(s))


class TrackMixin(TimeStampMixin):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    album_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("album.id"), nullable=False)
    artist_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("artist.id"), nullable=False)
    entry_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    legacy_id: Mapped[str] = mapped_column(nullable=False)
    is_internal: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_parental_advisory: Mapped[bool] = mapped_column(nullable=False, default=False)
    decade: Mapped[int] = mapped_column(nullable=True)
    mood: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    duration: Mapped[int] = mapped_column(nullable=True)

    name_tsv = mapped_column(
        TSVector(),
        Computed("to_tsvector('english', name)", persisted=True),
    )

    @declared_attr
    def track_playlist_associations(cls) -> Mapped[list["PlaylistTrackAssoc"]]:
        return relationship(back_populates="track", cascade="all, delete-orphan")

    @declared_attr
    def dj_set_track_associations(cls) -> Mapped[list["DjSetTrackAssoc"]]:
        return relationship(back_populates="track", cascade="all, delete-orphan")

    @declared_attr
    def album(cls) -> Mapped["Album"]:
        return relationship("Album", back_populates="tracks")

    @declared_attr
    def artist(cls) -> Mapped["Artist"]:
        return relationship("Artist", back_populates="tracks")

    @declared_attr
    def genres(cls) -> Mapped[List["Genre"]]:
        return relationship("Genre", secondary="track_genre_assoc", back_populates="tracks")

    @declared_attr
    def label(cls) -> Mapped["TrackLabel"]:
        return relationship(
            "TrackLabel",
            back_populates="track",
            cascade="all, delete-orphan",
        )

    # __table_args__ = (
    #     Index("fts_ix_track_name_tsv", to_tsvector_ix("name"), postgresql_using="gin"),
    # )


class TrackSync(CustomSyncBase, TrackMixin):
    pass


class Track(CustomBase, TrackMixin):
    pass


class TrackGenreAssocMixin:
    track_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("track.id"), primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(ForeignKey("genre.id"), primary_key=True)


class TrackGenreAssocSync(CustomSyncBase, TrackGenreAssocMixin):
    pass


class TrackGenreAssoc(CustomBase, TrackGenreAssocMixin):
    pass


class TrackLabelMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    track_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("track.id"), primary_key=True
    )
    name: Mapped[str] = mapped_column(nullable=False)
    isrc: Mapped[str] = mapped_column(nullable=False)
    legacy_id: Mapped[str] = mapped_column(nullable=False)

    @declared_attr
    def track(cls) -> Mapped[Track]:
        return relationship("Track", back_populates="label")


class TrackLabelSync(CustomSyncBase, TrackLabelMixin):
    pass


class TrackLabel(CustomBase, TrackLabelMixin):
    pass

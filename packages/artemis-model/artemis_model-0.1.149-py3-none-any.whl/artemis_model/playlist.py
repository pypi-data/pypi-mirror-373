import uuid
from datetime import date, datetime

from sqlalchemy import Computed, ForeignKey, func, literal, text, ARRAY, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomBase, CustomSyncBase, TSVector, TimeStampMixin
from sqlalchemy.ext.declarative import declared_attr


def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector(literal("english"), text(s))


class FavoritePlaylistMixin:
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlist.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)


class FavoritePlaylistSync(CustomSyncBase, FavoritePlaylistMixin):
    pass


class FavoritePlaylist(CustomBase, FavoritePlaylistMixin):
    pass


class PlaylistMixin(TimeStampMixin):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    entry_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    legacy_id: Mapped[str] = mapped_column(nullable=True)
    is_published: Mapped[bool] = mapped_column(default=False)  # legacy isTest
    description: Mapped[str | None] = mapped_column(nullable=True)
    cover_image: Mapped[str | None] = mapped_column(nullable=True)
    is_ordered: Mapped[bool] = mapped_column(default=False)
    legacy_prepared_by: Mapped[str | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(nullable=True)
    published_at: Mapped[date | None] = mapped_column(nullable=True)
    is_private: Mapped[bool] = mapped_column(default=False)
    total_duration: Mapped[int] = mapped_column(default=0)
    track_count: Mapped[int] = mapped_column(default=0)
    artist_names: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=[])

    name_tsv = mapped_column(
        TSVector(),
        Computed("to_tsvector('english', name)", persisted=True),
    )

    @declared_attr
    def favorite_playlist_associations(cls):
        return relationship(
            "FavoritePlaylist",
            primaryjoin="and_(FavoritePlaylist.playlist_id == Playlist.id)",
            viewonly=True,
            lazy="select",
        )

    @hybrid_property
    def is_favorite(self):
        return bool(self.favorite_playlist_associations)

    @declared_attr
    def category_playlist_associations(cls) -> Mapped[list["PlaylistCategoryAssoc"]]:
        return relationship(cascade="all, delete-orphan")

    @declared_attr
    def track_playlist_associations(cls) -> Mapped[list["PlaylistTrackAssoc"]]:
        return relationship(cascade="all, delete-orphan")

    @declared_attr
    def organization_playlist_associations(cls) -> Mapped[list["PlaylistOrganizationAssoc"]]:
        return relationship(cascade="all, delete-orphan")

    @declared_attr
    def organization_ids(cls) -> AssociationProxy[list["Organization"] | None]:
        return association_proxy(
            "organization_playlist_associations",
            "organization",
            creator=lambda o: PlaylistOrganizationAssoc(organization_id=o),
        )

    @declared_attr
    def category_ids(cls) -> AssociationProxy[list["Category"] | None]:
        return association_proxy(
            "category_playlist_associations",
            "category",
            creator=lambda c: PlaylistCategoryAssoc(category_id=c),
        )

    @declared_attr
    def track_ids(cls) -> AssociationProxy[list["Track"] | None]:
        return association_proxy(
            "track_playlist_associations",
            "track",
            creator=lambda t: PlaylistTrackAssoc(track_id=t),
        )

    @declared_attr
    def tracks(cls) -> Mapped[list["Track"]]:
        return relationship(secondary="playlist_track_assoc", viewonly=True)

    @declared_attr
    def categories(cls) -> Mapped[list["Category"]]:
        return relationship(secondary="playlist_category_assoc", viewonly=True)

    # __table_args__ = (
    #     Index(
    #         "fts_ix_playlist_name_tsv",
    #         to_tsvector_ix("name"),
    #         postgresql_using="gin",
    #     ),
    # )


class PlaylistSync(CustomSyncBase, PlaylistMixin):
    pass


class Playlist(CustomBase, PlaylistMixin):
    pass


class PlaylistOrganizationAssocMixin(TimeStampMixin):
    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlist.id"), primary_key=True, nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organization.id"), primary_key=True, nullable=False
    )


class PlaylistOrganizationkAssocSync(CustomSyncBase, PlaylistOrganizationAssocMixin):
    pass


class PlaylistOrganizationAssoc(CustomBase, PlaylistOrganizationAssocMixin):
    pass


class PlaylistTrackAssocMixin(TimeStampMixin):
    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlist.id"), primary_key=True, nullable=False
    )
    track_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("track.id"), primary_key=True, nullable=False
    )

    @declared_attr
    def track(cls) -> Mapped["Track"]:
        return relationship(back_populates="track_playlist_associations")


class PlaylistTrackAssocSync(CustomSyncBase, PlaylistTrackAssocMixin):
    pass


class PlaylistTrackAssoc(CustomBase, PlaylistTrackAssocMixin):
    pass


class PlaylistCategoryAssocMixin(TimeStampMixin):
    playlist_id = mapped_column(ForeignKey("playlist.id"), primary_key=True, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id"), primary_key=True, nullable=False
    )

    @declared_attr
    def category(cls) -> Mapped["Category"]:
        return relationship(back_populates="category_playlist_associations")


class PlaylistCategoryAssocSync(CustomSyncBase, PlaylistCategoryAssocMixin):
    pass


class PlaylistCategoryAssoc(CustomBase, PlaylistCategoryAssocMixin):
    pass


class PlaylistCounterMixin:
    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlist.id"), primary_key=True, nullable=False
    )
    play_count: Mapped[int] = mapped_column(default=0)
    schedule_count: Mapped[int] = mapped_column(default=0)


class PlaylistCounterSync(CustomSyncBase, PlaylistCounterMixin):
    pass


class PlaylistCounter(CustomBase, PlaylistCounterMixin):
    pass

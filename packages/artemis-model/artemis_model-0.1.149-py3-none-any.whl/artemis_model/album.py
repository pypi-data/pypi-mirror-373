"""Album models"""

from datetime import datetime

from sqlalchemy import Computed, ForeignKey, func, literal, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomSyncBase, CustomBase, TSVector, TimeStampMixin

from sqlalchemy.ext.declarative import declared_attr


def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector(literal("english"), text(s))


class AlbumMixin(TimeStampMixin):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    entry_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    legacy_id: Mapped[str] = mapped_column(nullable=False)
    is_internal: Mapped[bool] = mapped_column(nullable=False, default=False)

    name_tsv = mapped_column(
        TSVector(),
        Computed("to_tsvector('english', name)", persisted=True),
    )

    # __table_args__ = (
    #     Index("fts_ix_album_name_tsv", to_tsvector_ix("name"), postgresql_using="gin"),
    # )

    @declared_attr
    def artists(cls) -> Mapped[list["Artist"]]:
        return relationship(secondary="album_artist_assoc", back_populates="albums")

    @declared_attr
    def tracks(cls) -> Mapped[list["Track"]]:
        return relationship(
            "Track",
            back_populates="album",
            cascade="all, delete-orphan",
        )


class AlbumSync(CustomSyncBase, AlbumMixin):
    pass


class Album(CustomBase, AlbumMixin):
    pass


class AlbumArtistAssocMixin:
    album_id: Mapped[int] = mapped_column(ForeignKey("album.id"), primary_key=True, nullable=False)
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artist.id"), primary_key=True, nullable=False
    )


class AlbumArtistAssocSync(CustomSyncBase, AlbumArtistAssocMixin):
    pass


class AlbumArtistAssoc(CustomBase, AlbumArtistAssocMixin):
    pass

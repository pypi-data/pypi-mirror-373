"""Artist models"""

from datetime import datetime

from sqlalchemy import Computed, func, literal, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomBase, CustomSyncBase, TSVector, TimeStampMixin

from sqlalchemy.ext.declarative import declared_attr


def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector(literal("english"), text(s))


class ArtistMixin(TimeStampMixin):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    entry_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_internal: Mapped[bool] = mapped_column(nullable=False, default=False)
    legacy_id: Mapped[str] = mapped_column(nullable=False)

    name_tsv = mapped_column(
        TSVector(),
        Computed("to_tsvector('english', name)", persisted=True),
    )

    # __table_args__ = (
    #     Index("fts_ix_artist_name_tsv", to_tsvector_ix("name"), postgresql_using="gin"),
    # )

    @declared_attr
    def albums(cls) -> Mapped[list["Album"]]:
        return relationship(secondary="album_artist_assoc", back_populates="artists")

    @declared_attr
    def tracks(cls) -> Mapped[list["Track"]]:
        return relationship("Track", back_populates="artist", cascade="all, delete-orphan")


class ArtistSync(CustomSyncBase, ArtistMixin):
    pass


class Artist(CustomBase, ArtistMixin):
    pass

from sqlalchemy import Computed, func, literal, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomBase, CustomSyncBase, TSVector, TimeStampMixin

from sqlalchemy.ext.declarative import declared_attr


def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector(literal("english"), text(s))


class GenreMixin(TimeStampMixin):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    parent_id: Mapped[int | None] = mapped_column(nullable=True)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    legacy_id: Mapped[str] = mapped_column(nullable=False)

    name_tsv = mapped_column(
        TSVector(),
        Computed("to_tsvector('english', name)", persisted=True),
    )

    @declared_attr
    def tracks(cls) -> Mapped[list["Track"]]:
        return relationship("Track", secondary="track_genre_assoc", back_populates="genres")

    @declared_attr
    def dj_set_genre_associations(cls) -> Mapped[list["DjSetGenreAssoc"]]:
        return relationship(back_populates="genre", cascade="all, delete-orphan")

    def dj_sets(cls) -> Mapped[list["DjSet"]]:
        return relationship("DjSet", secondary="dj_set_genre_assoc", back_populates="genre")

    # __table_args__ = (
    #     Index("fts_ix_genre_name_tsv", to_tsvector_ix("name"), postgresql_using="gin"),
    # )


class GenreSync(CustomSyncBase, GenreMixin):
    pass


class Genre(CustomBase, GenreMixin):
    pass

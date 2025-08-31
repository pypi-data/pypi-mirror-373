from sqlalchemy import Computed, func, literal, text
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomSyncBase, TimeStampMixin, TSVector, CustomBase

from sqlalchemy.ext.declarative import declared_attr

from artemis_model.playlist import PlaylistCategoryAssoc


def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector(literal("english"), text(s))


class CategoryMixin(TimeStampMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    main_category: Mapped[str] = mapped_column(nullable=False)
    sub_category: Mapped[str] = mapped_column(nullable=False)

    name_tsv = mapped_column(
        TSVector(),
        Computed("to_tsvector('english', main_category || ' ' || sub_category)", persisted=True),
    )

    @declared_attr
    def category_playlist_associations(cls) -> Mapped[list["PlaylistCategoryAssoc"]]:
        return relationship(back_populates="category", cascade="all, delete-orphan")

    @declared_attr
    def playlists(cls) -> AssociationProxy[list["Playlist"]]:
        return association_proxy(
            "playlist_category_assoc",
            "playlist",
            creator=lambda p: PlaylistCategoryAssoc(playlist_id=p),
        )

    # __table_args__ = (
    #     Index(
    #         "fts_ix_category_name_tsv",
    #         to_tsvector_ix("main_category", "sub_category"),
    #         postgresql_using="gin",
    #     ),
    # )


class CategorySync(CustomSyncBase, CategoryMixin):
    pass


class Category(CustomBase, CategoryMixin):
    pass

import uuid
from datetime import datetime

from sqlalchemy import Computed, ForeignKey, ARRAY, Integer
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import CustomBase, CustomSyncBase, TSVector, TimeStampMixin, AuditMixin
from sqlalchemy.ext.declarative import declared_attr


class DjSetGenreAssocMixin(TimeStampMixin):
    dj_set_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dj_set.id"), primary_key=True, nullable=False
    )
    genre_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("genre.id"), primary_key=True, nullable=False
    )
    weight: Mapped[int] = mapped_column(nullable=False, default=0)

    @declared_attr
    def genre(cls) -> Mapped["Genre"]:
        return relationship(back_populates="dj_set_genre_associations")


class DjSetGenreAssocSync(CustomSyncBase, DjSetGenreAssocMixin):
    pass


class DjSetGenreAssoc(CustomBase, DjSetGenreAssocMixin):
    pass


class DjSetMixin(TimeStampMixin, AuditMixin):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organization.id"), nullable=True, index=True
    )
    entry_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    cover_image: Mapped[str] = mapped_column(nullable=True)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    legacy_id: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
    mood: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, default=[0, 0])
    decades: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    total_duration: Mapped[int] = mapped_column(nullable=False, default=0)

    name_tsv = mapped_column(
        TSVector(),
        Computed("to_tsvector('english', name)", persisted=True),
    )

    @declared_attr
    def organization(cls) -> Mapped["Organization"]:
        return relationship(back_populates="dj_sets")

    @declared_attr
    def genre_ids(cls) -> AssociationProxy[list["Genre"] | None]:
        return association_proxy(
            "dj_set_genre_associations",
            "genre",
            creator=lambda genre: DjSetGenreAssoc(
                genre_id=genre.get("id"), weight=genre.get("weight", 0)
            ),
        )

    @declared_attr
    def dj_set_genre_associations(cls) -> Mapped[list["DjSetGenreAssoc"]]:
        return relationship(cascade="all, delete-orphan")

    @declared_attr
    def dj_set_track_associations(cls) -> Mapped[list["DjSetTrackAssoc"]]:
        return relationship(cascade="all, delete-orphan")

    @declared_attr
    def genres(cls) -> Mapped[list["Genre"]]:
        return relationship(secondary="dj_set_genre_assoc", lazy="joined", viewonly=True)


@declared_attr
def tracks(cls) -> Mapped[list["Track"]]:
    return relationship(secondary="dj_set_track_assoc", viewonly=True)


class DjSetSync(CustomSyncBase, DjSetMixin):
    pass


class DjSet(CustomBase, DjSetMixin):
    pass


class DjSetTrackAssocMixin(TimeStampMixin):
    dj_set_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dj_set.id"), primary_key=True, nullable=False
    )
    track_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("track.id"), primary_key=True, nullable=False
    )

    @declared_attr
    def track(cls) -> Mapped["Track"]:
        return relationship(back_populates="dj_set_track_associations")


class DjSetTrackAssocSync(CustomSyncBase, DjSetTrackAssocMixin):
    pass


class DjSetTrackAssoc(CustomBase, DjSetTrackAssocMixin):
    pass

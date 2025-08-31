import uuid
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

from artemis_model.base import TimeStampMixin, CustomSyncBase, CustomBase


class LocationGenreExclusionMixin(TimeStampMixin):
    """Association table for tracking which genres are excluded at the location level."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("location.id", ondelete="CASCADE"), nullable=False, index=True
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genre.id", ondelete="CASCADE"), nullable=False, index=True
    )

    @declared_attr
    def location(cls) -> Mapped["Location"]:
        return relationship(back_populates="genre_exclusions")

    @declared_attr
    def genre(cls) -> Mapped["Genre"]:
        return relationship()

    __table_args__ = (
        UniqueConstraint("location_id", "genre_id", name="unique_location_genre_exclusion"),
    )


class LocationGenreExclusionSync(CustomSyncBase, LocationGenreExclusionMixin):
    pass


class LocationGenreExclusion(CustomBase, LocationGenreExclusionMixin):
    pass
from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from artemis_model.base import TimeStampMixin, CustomSyncBase, CustomBase

from sqlalchemy.ext.declarative import declared_attr


class SettingMixin(TimeStampMixin):
    """
    Exclusion Schema
    {
        "genres": {
            "<genre_id>": "<genre_name>",
            "<genre_id>": "<genre_name>",
            ...
        },
        "artists": {
            "<artist_id>": "<artist_name>",
            "<artist_id>": "<artist_name>",
            ...
        },
        "tracks": {
            "<track_id>": "<track_name>",
            "<track_id>": "<track_name>",
            ...
        },
        "exclude_pal": True/False
    }
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zone.id"), index=True)
    exclusion: Mapped[JSON] = mapped_column(JSON, nullable=True)

    @declared_attr
    def zone(cls) -> Mapped["Zone"]:
        return relationship(back_populates="setting")


class SettingSync(CustomSyncBase, SettingMixin):
    pass


class Setting(CustomBase, SettingMixin):
    pass

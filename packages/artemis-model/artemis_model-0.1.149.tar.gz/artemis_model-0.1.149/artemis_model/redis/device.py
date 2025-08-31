"""Active device redis model."""

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ActiveDevice(BaseModel):
    """Active device schema."""

    user_id: UUID
    client_id: str
    device_id: str
    mode: Literal["player-mode", "controller-mode"]
    connected_at: datetime | str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


__all__ = ["ActiveDevice"]

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ChatMute(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_muted: bool = Field(alias="isMuted")
    muted_end_time: datetime | None = Field(alias="mutedEndTime", default=None)

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CallOfferEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    caller: str
    chat_id: str = Field(alias="chatId")
    is_group: bool = Field(alias="isGroup")
    time: datetime
    is_video: bool = Field(alias="isVideo")

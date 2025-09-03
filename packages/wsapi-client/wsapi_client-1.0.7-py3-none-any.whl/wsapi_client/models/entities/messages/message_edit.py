from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MessageEdit(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    original_message_id: str = Field(alias="originalMessageId")
    original_message_time: datetime = Field(alias="originalMessageTime")

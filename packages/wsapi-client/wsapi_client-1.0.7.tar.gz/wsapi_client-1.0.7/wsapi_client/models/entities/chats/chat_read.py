from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class ChatRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_read: bool = Field(alias="isRead")

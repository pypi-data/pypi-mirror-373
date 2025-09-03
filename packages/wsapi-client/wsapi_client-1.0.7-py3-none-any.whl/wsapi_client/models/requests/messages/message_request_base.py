from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MessageRequestBase(BaseModel):
    to: str = Field(alias="to")
    mentions: Optional[list[str]] = Field(default=None, alias="mentions")
    reply_to: Optional[str] = Field(default=None, alias="replyTo")
    is_forwarded: Optional[bool] = Field(default=False, alias="isForwarded")

    model_config = ConfigDict(populate_by_name=True)

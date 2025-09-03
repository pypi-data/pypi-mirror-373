from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from .message_event import MessageEvent


class MessageHistorySyncEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    messages: list[MessageEvent]

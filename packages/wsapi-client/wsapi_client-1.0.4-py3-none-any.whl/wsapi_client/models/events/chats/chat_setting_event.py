from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from ...entities.chats.chat_archive import ChatArchive
from ...entities.chats.chat_pin import ChatPin
from ...entities.chats.chat_read import ChatRead
from ...entities.chats.chat_mute import ChatMute
from ...entities.chats.chat_ephemeral import ChatEphemeral


class ChatSettingEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    settting_type: str = Field(alias="settingType")
    archive: ChatArchive | None = None
    pin: ChatPin | None = None
    read: ChatRead | None = None
    mute: ChatMute | None = None
    ephemeral: ChatEphemeral | None = None

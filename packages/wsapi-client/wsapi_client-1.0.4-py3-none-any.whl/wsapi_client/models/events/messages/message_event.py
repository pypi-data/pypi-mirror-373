from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from ...entities.users.sender import Sender
from ...entities.messages.message_reply_to import MessageReplyTo
from ...entities.messages.message_extended_text import MessageExtendedText
from ...entities.messages.message_edit import MessageEdit
from ...entities.messages.message_media import MessageMedia
from ...entities.messages.message_reaction import MessageReaction
from ...entities.messages.message_contact import MessageContact
from ...entities.messages.message_pin import MessagePin


class MessageEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    chat_id: str = Field(alias="chatId")
    sender: Sender
    sender_name: str = Field(alias="senderName")
    time: datetime
    is_group: bool = Field(alias="isGroup")
    is_status: bool = Field(alias="isStatus")
    mentions: list[str] | None = None
    ephemeral_expiration: str = Field(alias="expiration")
    type: str

    text: str | None = None
    reply_to: MessageReplyTo | None = Field(alias="replyTo", default=None)
    extended_text: MessageExtendedText | None = Field(alias="extendedText", default=None)
    edit_message: MessageEdit | None = Field(alias="editMessage", default=None)
    media: MessageMedia | None = None
    reaction: MessageReaction | None = None
    contact: str | None = None
    contacts: list[str] | None = Field(alias="contactArray", default=None)
    pin: MessagePin | None = Field(alias="pinInChat", default=None)

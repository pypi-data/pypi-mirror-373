from __future__ import annotations
from typing import Optional
from pydantic import Field, ConfigDict

from .message_request_base import MessageRequestBase


class MessageSendAudioRequest(MessageRequestBase):
    audio_base64: Optional[str] = Field(default=None, alias="audioBase64")
    audio_url: Optional[str] = Field(default=None, alias="audioUrl")
    mime_type: str = Field(alias="mimeType")
    view_once: bool = Field(default=False, alias="viewOnce")

    model_config = ConfigDict(populate_by_name=True)

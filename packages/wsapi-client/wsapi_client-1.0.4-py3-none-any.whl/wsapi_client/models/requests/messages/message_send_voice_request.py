from __future__ import annotations
from typing import Optional
from pydantic import Field, ConfigDict

from .message_request_base import MessageRequestBase


class MessageSendVoiceRequest(MessageRequestBase):
    voice_base64: Optional[str] = Field(default=None, alias="voiceBase64")
    voice_url: Optional[str] = Field(default=None, alias="voiceUrl")
    view_once: bool = Field(default=False, alias="viewOnce")

    model_config = ConfigDict(populate_by_name=True)

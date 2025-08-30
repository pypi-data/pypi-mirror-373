from __future__ import annotations
from typing import Optional
from pydantic import Field, ConfigDict

from .message_request_base import MessageRequestBase


class MessageSendVideoRequest(MessageRequestBase):
    video_base64: Optional[str] = Field(default=None, alias="videoBase64")
    video_url: Optional[str] = Field(default=None, alias="videoUrl")
    mime_type: str = Field(alias="mimeType")
    caption: Optional[str] = Field(default=None, alias="caption")
    view_once: bool = Field(default=False, alias="viewOnce")

    model_config = ConfigDict(populate_by_name=True)

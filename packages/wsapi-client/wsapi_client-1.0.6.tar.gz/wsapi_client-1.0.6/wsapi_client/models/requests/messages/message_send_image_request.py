from __future__ import annotations
from typing import Optional
from pydantic import Field, ConfigDict

from .message_request_base import MessageRequestBase


class MessageSendImageRequest(MessageRequestBase):
    image_base64: Optional[str] = Field(default=None, alias="imageBase64")
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    mime_type: Optional[str] = Field(default=None, alias="mimeType")
    caption: Optional[str] = Field(default=None, alias="caption")
    view_once: bool = Field(default=False, alias="viewOnce")

    model_config = ConfigDict(populate_by_name=True)

from __future__ import annotations
from typing import Optional
from pydantic import Field, ConfigDict

from .message_request_base import MessageRequestBase


class MessageSendDocumentRequest(MessageRequestBase):
    document_base64: Optional[str] = Field(default=None, alias="documentBase64")
    document_url: Optional[str] = Field(default=None, alias="documentUrl")
    file_name: str = Field(alias="fileName")
    caption: Optional[str] = Field(default=None, alias="caption")

    model_config = ConfigDict(populate_by_name=True)

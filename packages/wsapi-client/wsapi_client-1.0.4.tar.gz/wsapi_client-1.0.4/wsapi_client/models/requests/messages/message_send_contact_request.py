from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class MessageSendContactRequest(BaseModel):
    to: str = Field(alias="to")
    v_card: str = Field(alias="vCard")
    display_name: str = Field(alias="displayName")

    model_config = ConfigDict(populate_by_name=True)

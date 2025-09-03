from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class MessageContact(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    display_name: str = Field(alias="displayName")
    v_card: str = Field(alias="vCard")

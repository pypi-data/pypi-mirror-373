from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ContactBusinessProfile(BaseModel):
    description: Optional[str] = Field(default=None, alias="description")
    email: Optional[str] = Field(default=None, alias="email")
    website: Optional[str] = Field(default=None, alias="website")

    model_config = ConfigDict(populate_by_name=True)

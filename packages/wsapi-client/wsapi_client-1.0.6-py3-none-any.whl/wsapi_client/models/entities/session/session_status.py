from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class SessionStatus(BaseModel):
    status: str = Field(alias="status")
    message: Optional[str] = Field(default=None, alias="message")

    model_config = ConfigDict(populate_by_name=True)

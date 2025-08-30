from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class RejectCallRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    caller: str = Field(alias="caller")

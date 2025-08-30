from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class InstanceSettings(BaseModel):
    name: str = Field(alias="name")
    description: Optional[str] = Field(default=None, alias="description")
    webhook_url: Optional[str] = Field(default=None, alias="webhookUrl")
    webhook_auth_header: Optional[str] = Field(default=None, alias="webhookAuthHeader")
    webhook_auth_value: Optional[str] = Field(default=None, alias="webhookAuthValue")
    pull_mode: bool = Field(alias="pullMode")

    model_config = ConfigDict(populate_by_name=True)

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class GroupParticipantInfo(BaseModel):
    id: str = Field(alias="id")

    model_config = ConfigDict(populate_by_name=True)


class GroupInfo(BaseModel):
    id: str = Field(alias="id")
    owner_id: str = Field(alias="ownerId")
    name: str = Field(alias="name")
    created: str = Field(alias="created")  # ISO string; switch to datetime if needed
    description: str = Field(alias="description")
    is_announce: bool = Field(alias="isAnnounce")
    is_locked: bool = Field(alias="isLocked")
    is_ephemeral: bool = Field(alias="isEphemeral")
    ephemeral_expiration: int = Field(alias="ephemeralExpiration")
    participants: list[GroupParticipantInfo] = Field(alias="participants")

    model_config = ConfigDict(populate_by_name=True)

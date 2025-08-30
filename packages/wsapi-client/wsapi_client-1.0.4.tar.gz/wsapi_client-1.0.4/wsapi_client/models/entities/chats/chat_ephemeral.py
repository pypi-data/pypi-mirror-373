from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from ..users.sender import Sender


class ChatEphemeral(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    expiration: str
    sender: Sender

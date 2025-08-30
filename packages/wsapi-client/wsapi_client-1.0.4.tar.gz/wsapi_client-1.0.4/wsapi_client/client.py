from __future__ import annotations
from typing import Optional

from .http import WSApiHttp
from .api.instance import InstanceClient
from .api.account import AccountClient
from .api.messages import MessagesClient
from .api.media import MediaClient
from .api.session import SessionClient
from .api.contacts import ContactsClient
from .api.groups import GroupsClient
from .api.chats import ChatsClient
from .api.users import UsersClient
from .api.calls import CallsClient


class WSApiClient:
    def __init__(
        self,
        api_key: str,
        instance_id: str,
        *,
        base_url: str = "https://api.wsapi.chat",
        timeout: float = 30.0,
    ) -> None:
        self._http = WSApiHttp(api_key=api_key, instance_id=instance_id, base_url=base_url, timeout=timeout)

        # Surface parity with .NET: expose sub-clients
        self.instance = InstanceClient(self._http)
        self.account = AccountClient(self._http)
        self.messages = MessagesClient(self._http)
        self.media = MediaClient(self._http)
        self.session = SessionClient(self._http)
        self.contacts = ContactsClient(self._http)
        self.groups = GroupsClient(self._http)
        self.chats = ChatsClient(self._http)
        self.users = UsersClient(self._http)
        self.calls = CallsClient(self._http)

    def close(self) -> None:
        self._http.close()

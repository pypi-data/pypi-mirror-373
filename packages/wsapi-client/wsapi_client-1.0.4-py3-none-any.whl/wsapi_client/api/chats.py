from __future__ import annotations
from ..http import WSApiHttp, ApiResponse
from ..models.entities.chats.chat_info import ChatInfo
from ..models.requests.chats.chat_update_presence_request import ChatUpdatePresenceRequest
from ..models.requests.chats.chat_update_ephemeral_expiration_request import ChatUpdateEphemeralExpirationRequest
from ..models.requests.chats.chat_update_mute_request import ChatUpdateMuteRequest
from ..models.requests.chats.chat_update_pin_request import ChatUpdatePinRequest
from ..models.requests.chats.chat_update_archive_request import ChatUpdateArchiveRequest
from ..models.requests.chats.chat_update_read_request import ChatUpdateReadRequest


class ChatsClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    # Standard methods
    def list(self) -> list[ChatInfo]:
        return self._http.send_json("GET", "/chats", model=list[ChatInfo])

    def get(self, chat_id: str) -> ChatInfo:
        return self._http.send_json("GET", f"/chats/{chat_id}", model=ChatInfo)

    def update_presence(self, chat_id: str, request: ChatUpdatePresenceRequest) -> None:
        self._http.send_json("PUT", f"/chats/{chat_id}/presence", model=None, json=request.model_dump(by_alias=True))

    def update_ephemeral(self, chat_id: str, request: ChatUpdateEphemeralExpirationRequest) -> None:
        self._http.send_json("PUT", f"/chats/{chat_id}/ephemeral", model=None, json=request.model_dump(by_alias=True))

    def update_mute(self, chat_id: str, request: ChatUpdateMuteRequest) -> None:
        self._http.send_json("PUT", f"/chats/{chat_id}/mute", model=None, json=request.model_dump(by_alias=True))

    def update_pin(self, chat_id: str, request: ChatUpdatePinRequest) -> None:
        self._http.send_json("PUT", f"/chats/{chat_id}/pin", model=None, json=request.model_dump(by_alias=True))

    def update_archive(self, chat_id: str, request: ChatUpdateArchiveRequest) -> None:
        self._http.send_json("PUT", f"/chats/{chat_id}/archive", model=None, json=request.model_dump(by_alias=True))

    def update_read(self, chat_id: str, request: ChatUpdateReadRequest) -> None:
        self._http.send_json("PUT", f"/chats/{chat_id}/read", model=None, json=request.model_dump(by_alias=True))

    def delete_chat(self, chat_id: str) -> None:
        self._http.send_json("DELETE", f"/chats/{chat_id}", model=None)

    # Try methods
    def try_list(self) -> ApiResponse[list[ChatInfo]]:
        return self._http.try_send_json("GET", "/chats", model=list[ChatInfo])

    def try_get(self, chat_id: str) -> ApiResponse[ChatInfo]:
        return self._http.try_send_json("GET", f"/chats/{chat_id}", model=ChatInfo)

    def try_update_presence(self, chat_id: str, request: ChatUpdatePresenceRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/chats/{chat_id}/presence", model=None, json=request.model_dump(by_alias=True))

    def try_update_ephemeral(self, chat_id: str, request: ChatUpdateEphemeralExpirationRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/chats/{chat_id}/ephemeral", model=None, json=request.model_dump(by_alias=True))

    def try_update_mute(self, chat_id: str, request: ChatUpdateMuteRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/chats/{chat_id}/mute", model=None, json=request.model_dump(by_alias=True))

    def try_update_pin(self, chat_id: str, request: ChatUpdatePinRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/chats/{chat_id}/pin", model=None, json=request.model_dump(by_alias=True))

    def try_update_archive(self, chat_id: str, request: ChatUpdateArchiveRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/chats/{chat_id}/archive", model=None, json=request.model_dump(by_alias=True))

    def try_update_read(self, chat_id: str, request: ChatUpdateReadRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/chats/{chat_id}/read", model=None, json=request.model_dump(by_alias=True))

    def try_delete_chat(self, chat_id: str) -> ApiResponse[object]:
        return self._http.try_send_json("DELETE", f"/chats/{chat_id}", model=None)

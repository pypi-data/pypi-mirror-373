from __future__ import annotations
from ..http import WSApiHttp, ApiResponse
from ..models.entities.groups.group_info import GroupInfo
from ..models.entities.groups.group_created import GroupCreated
from ..models.entities.groups.group_picture_info import GroupPictureInfo
from ..models.entities.groups.group_picture_updated import GroupPictureUpdated
from ..models.requests.groups.group_create_request import GroupCreateRequest
from ..models.requests.groups.group_update_description_request import GroupUpdateDescriptionRequest
from ..models.requests.groups.group_update_name_request import GroupUpdateNameRequest
from ..models.requests.groups.group_update_picture_request import GroupUpdatePictureRequest


class GroupsClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    # Standard methods
    def list(self) -> list[GroupInfo]:
        return self._http.send_json("GET", "/groups", model=list[GroupInfo])

    def get(self, group_id: str) -> GroupInfo:
        return self._http.send_json("GET", f"/groups/{group_id}", model=GroupInfo)

    def get_picture(self, group_id: str) -> GroupPictureInfo:
        return self._http.send_json("GET", f"/groups/{group_id}/picture", model=GroupPictureInfo)

    def create(self, request: GroupCreateRequest) -> GroupCreated:
        return self._http.send_json("POST", "/groups", model=GroupCreated, json=request.model_dump(by_alias=True))

    def update_description(self, group_id: str, request: GroupUpdateDescriptionRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/description", model=None, json=request.model_dump(by_alias=True))

    def update_name(self, group_id: str, request: GroupUpdateNameRequest) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/name", model=None, json=request.model_dump(by_alias=True))

    def update_picture(self, group_id: str, request: GroupUpdatePictureRequest) -> GroupPictureUpdated:
        return self._http.send_json("POST", f"/groups/{group_id}/picture", model=GroupPictureUpdated, json=request.model_dump(by_alias=True))

    def leave_group(self, group_id: str) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}", model=None)

    # Try variants
    def try_list(self) -> ApiResponse[list[GroupInfo]]:
        return self._http.try_send_json("GET", "/groups", model=list[GroupInfo])

    def try_get(self, group_id: str) -> ApiResponse[GroupInfo]:
        return self._http.try_send_json("GET", f"/groups/{group_id}", model=GroupInfo)

    def try_get_picture(self, group_id: str) -> ApiResponse[GroupPictureInfo]:
        return self._http.try_send_json("GET", f"/groups/{group_id}/picture", model=GroupPictureInfo)

    def try_create(self, request: GroupCreateRequest) -> ApiResponse[GroupCreated]:
        return self._http.try_send_json("POST", "/groups", model=GroupCreated, json=request.model_dump(by_alias=True))

    def try_update_description(self, group_id: str, request: GroupUpdateDescriptionRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/description", model=None, json=request.model_dump(by_alias=True))

    def try_update_name(self, group_id: str, request: GroupUpdateNameRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/name", model=None, json=request.model_dump(by_alias=True))

    def try_update_picture(self, group_id: str, request: GroupUpdatePictureRequest) -> ApiResponse[GroupPictureUpdated]:
        return self._http.try_send_json("POST", f"/groups/{group_id}/picture", model=GroupPictureUpdated, json=request.model_dump(by_alias=True))

    def try_leave_group(self, group_id: str) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/leave", model=None)

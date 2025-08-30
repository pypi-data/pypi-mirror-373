from __future__ import annotations

from ..http import WSApiHttp, ApiResponse
from ..models.entities.accounts.account_info import AccountInfo
from ..models.requests.account.account_update_name_request import AccountUpdateNameRequest
from ..models.requests.account.account_update_status_request import AccountUpdateStatusRequest
from ..models.requests.account.account_update_picture_request import AccountUpdatePictureRequest
from ..models.requests.account.account_update_picture_response import AccountUpdatePictureResponse
from ..models.requests.account.account_update_presence_request import AccountUpdatePresenceRequest


class AccountClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    # Standard methods (raise ApiException)
    def get_info(self) -> AccountInfo:
        return self._http.send_json("GET", "/account/info", model=AccountInfo)

    def update_name(self, request: AccountUpdateNameRequest) -> None:
        self._http.send_json("PUT", "/account/name", model=None, json=request.model_dump(by_alias=True))

    def update_status(self, request: AccountUpdateStatusRequest) -> None:
        self._http.send_json("PUT", "/account/status", model=None, json=request.model_dump(by_alias=True))

    def update_picture(self, request: AccountUpdatePictureRequest) -> AccountUpdatePictureResponse:
        return self._http.send_json("POST", "/account/picture", model=AccountUpdatePictureResponse, json=request.model_dump(by_alias=True))

    def update_presence(self, request: AccountUpdatePresenceRequest) -> None:
        self._http.send_json("PUT", "/account/presence", model=None, json=request.model_dump(by_alias=True))

    # Try methods (no exceptions)
    def try_get_info(self) -> ApiResponse[AccountInfo]:
        return self._http.try_send_json("GET", "/account/info", model=AccountInfo)

    def try_update_name(self, request: AccountUpdateNameRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", "/account/name", model=None, json=request.model_dump(by_alias=True))

    def try_update_status(self, request: AccountUpdateStatusRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", "/account/status", model=None, json=request.model_dump(by_alias=True))

    def try_update_picture(self, request: AccountUpdatePictureRequest) -> ApiResponse[AccountUpdatePictureResponse]:
        return self._http.try_send_json("POST", "/account/picture", model=AccountUpdatePictureResponse, json=request.model_dump(by_alias=True))

    def try_update_presence(self, request: AccountUpdatePresenceRequest) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", "/account/presence", model=None, json=request.model_dump(by_alias=True))
from __future__ import annotations
from typing import Optional

from ..http import WSApiHttp
from ..models.entities.users.user_info import UserInfo


class UsersClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    def get_by_id(self, user_id: str) -> Optional[UserInfo]:
        return self._http.send_json("GET", f"/users/{user_id}", model=UserInfo)

    def try_get_by_id(self, user_id: str):
        return self._http.try_send_json("GET", f"/users/{user_id}", model=UserInfo)

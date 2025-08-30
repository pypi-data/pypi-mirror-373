from __future__ import annotations
from typing import Optional

from pydantic import BaseModel, Field

from ..http import WSApiHttp, ApiResponse
from ..models.entities.instance.instance_settings import InstanceSettings


class InstanceClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    # Standard methods (raise ApiException)
    def get_settings(self) -> InstanceSettings:
        return self._http.send_json("GET", "/instance/settings", model=InstanceSettings)

    def update_settings(self, settings: InstanceSettings) -> None:
        self._http.send_json("PUT", "/instance/settings", model=dict, json=settings.model_dump(by_alias=True))

    def restart(self) -> None:
        self._http.send_json("PUT", "/instance/restart", model=dict)

    def update_api_key(self) -> str:
        return self._http.send_json("PUT", "/instance/apikey", model=str)

    # Try methods (no exceptions)
    def try_get_settings(self) -> ApiResponse[InstanceSettings]:
        return self._http.try_send_json("GET", "/instance/settings", model=InstanceSettings)

    def try_update_settings(self, settings: InstanceSettings) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", "/instance/settings", model=dict, json=settings.model_dump(by_alias=True))

    def try_restart(self) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", "/instance/restart", model=dict)

    def try_update_api_key(self) -> ApiResponse[str]:
        return self._http.try_send_json("PUT", "/instance/apikey", model=str)

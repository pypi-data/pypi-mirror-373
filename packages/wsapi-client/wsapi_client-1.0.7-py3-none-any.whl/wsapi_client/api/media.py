from __future__ import annotations

from ..http import WSApiHttp, ApiResponse


class MediaClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    def download(self, media_id: str) -> bytes:
        return self._http.send_bytes("GET", f"/media/download?id={media_id}")

    def try_download(self, media_id: str) -> ApiResponse[bytes]:
        return self._http.try_send_bytes("GET", f"/media/download?id={media_id}")

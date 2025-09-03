from __future__ import annotations
from ..http import WSApiHttp, ApiResponse
from ..models.entities.session.session_status import SessionStatus
from ..models.entities.session.session_pair_code import SessionPairCode


class SessionClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    # Standard methods
    def get_login_qr_image(self) -> bytes:
        # C# returned byte[] via JSON helper, but Python will treat it as bytes if endpoint returns bytes.
        # If API actually returns base64 JSON, we can add decoding later.
        return self._http.send_bytes("GET", "/session/login/qr/image")

    def get_login_qr_code(self) -> str:
        return self._http.send_json("GET", "/session/login/qr/code", model=str)

    def get_login_pair_code(self, phone_number: str) -> SessionPairCode:
        return self._http.send_json("GET", f"/session/login/code/{phone_number}", model=SessionPairCode)

    def logout(self) -> None:
        self._http.send_json("POST", "/session/logout", model=dict)

    def get_session_status(self) -> SessionStatus:
        return self._http.send_json("GET", "/session/status", model=SessionStatus)

    # Try methods
    def try_get_login_qr_image(self) -> ApiResponse[bytes]:
        return self._http.try_send_bytes("GET", "/session/login/qr/image")

    def try_get_login_qr_code(self) -> ApiResponse[str]:
        return self._http.try_send_json("GET", "/session/login/qr/code", model=str)

    def try_get_login_pair_code(self, phone_number: str) -> ApiResponse[SessionPairCode]:
        return self._http.try_send_json("GET", f"/session/login/code/{phone_number}", model=SessionPairCode)

    def try_logout(self) -> ApiResponse[object]:
        return self._http.try_send_json("POST", "/session/logout", model=dict)

    def try_get_session_status(self) -> ApiResponse[SessionStatus]:
        return self._http.try_send_json("GET", "/session/status", model=SessionStatus)

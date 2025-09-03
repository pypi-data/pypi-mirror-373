from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Generic, Optional, Type, TypeVar, cast

import httpx
from pydantic import BaseModel, ValidationError, TypeAdapter

from .exceptions import ApiException
from .models.problem_details import ProblemDetails

T = TypeVar("T")


@dataclass
class ApiResponse(Generic[T]):
    result: Optional[T] = None
    error: Optional[ProblemDetails] = None

    @property
    def is_success(self) -> bool:
        return self.error is None


class WSApiHttp:
    def __init__(
        self,
        api_key: str,
        instance_id: str,
        base_url: str = "https://api.wsapi.chat",
        timeout: float = 30.0,
        client: Optional[httpx.Client] = None,
    ) -> None:
        headers = {
            "X-Api-Key": api_key,
            "X-Instance-Id": instance_id,
        }
        self._client = client or httpx.Client(base_url=base_url, headers=headers, timeout=timeout)

    def close(self) -> None:
        self._client.close()

    # --- core request helpers ---
    def _handle_error(self, resp: httpx.Response) -> None:
        # Try to parse ProblemDetails
        problem: Optional[ProblemDetails] = None
        try:
            data = resp.json()
            problem = ProblemDetails.model_validate(data)
        except Exception:
            # non-JSON body
            problem = ProblemDetails(status=resp.status_code, detail=resp.text)
        raise ApiException(problem)

    def _handle_exception_to_api_response(self, exc: Exception) -> ProblemDetails:
        # Map timeouts to 408, others to 500-like behavior
        if isinstance(exc, httpx.TimeoutException):
            return ProblemDetails(status=408, title="Request Timeout", detail="The request timed out")
        if isinstance(exc, httpx.TransportError):
            return ProblemDetails(status=500, title="Request Failed", detail=str(exc))
        return ProblemDetails(status=500, title="Request Failed", detail=str(exc))

    def _parse_json(self, data: Any, model: Type[T] | Any) -> T:
        if isinstance(model, type) and issubclass(model, BaseModel):
            return cast(T, model.model_validate(data))
        adapter = TypeAdapter(model)  # type: ignore[arg-type]
        return adapter.validate_python(data)  # type: ignore[return-value]

    def _has_body(self, resp: httpx.Response) -> bool:
        if resp.status_code == 204:
            return False
        # Some servers return 200 with empty body; if content attr is missing (mock), assume body exists
        if hasattr(resp, "content"):
            return resp.content is not None and len(resp.content) > 0
        return True

    # JSON response
    def send_json(self, method: str, url: str, *, model: Type[T] | Any | None, json: Any | None = None) -> Optional[T]:
        resp = self._client.request(method, url, json=json)
        if 200 <= resp.status_code < 300:
            if model is None or not self._has_body(resp):
                return None
            data = resp.json()
            return self._parse_json(data, model)
        self._handle_error(resp)
        raise AssertionError("Unreachable")

    def try_send_json(self, method: str, url: str, *, model: Type[T] | Any | None, json: Any | None = None) -> ApiResponse[Optional[T]]:
        try:
            resp = self._client.request(method, url, json=json)
            if 200 <= resp.status_code < 300:
                if model is None or not self._has_body(resp):
                    return ApiResponse(result=None)
                data = resp.json()
                return ApiResponse(result=self._parse_json(data, model))
            # !2xx -> map to ProblemDetails
            try:
                problem = ProblemDetails.model_validate(resp.json())
            except Exception:
                problem = ProblemDetails(status=resp.status_code, detail=resp.text)
            return ApiResponse(error=problem)
        except Exception as exc:
            return ApiResponse(error=self._handle_exception_to_api_response(exc))

    # Bytes response
    def send_bytes(self, method: str, url: str, *, json: Any | None = None) -> bytes:
        resp = self._client.request(method, url, json=json)
        if 200 <= resp.status_code < 300:
            return resp.content
        self._handle_error(resp)
        raise AssertionError("Unreachable")

    def try_send_bytes(self, method: str, url: str, *, json: Any | None = None) -> ApiResponse[bytes]:
        try:
            resp = self._client.request(method, url, json=json)
            if 200 <= resp.status_code < 300:
                return ApiResponse(result=resp.content)
            try:
                problem = ProblemDetails.model_validate(resp.json())
            except Exception:
                problem = ProblemDetails(status=resp.status_code, detail=resp.text)
            return ApiResponse(error=problem)
        except Exception as exc:
            return ApiResponse(error=self._handle_exception_to_api_response(exc))

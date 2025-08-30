from __future__ import annotations
import threading
import time
from typing import Callable, Optional, Any

import httpx
from enum import Enum

from ..events.factory import parse_event


class SSEConnectionState(str, Enum):
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class SSEClient:
    def __init__(
        self,
        api_key: str,
        instance_id: str,
        *,
        base_url: str = "https://ws.wsapi.chat",
        reconnect_delay: float = 5.0,
        auto_reconnect: bool = True,
        timeout: float = 30.0,
    ) -> None:
        self._headers = {"X-Api-Key": api_key, "X-Instance-Id": instance_id}
        self._base_url = base_url.rstrip("/")
        self._reconnect_delay = reconnect_delay
        self._auto_reconnect = auto_reconnect
        self._timeout = timeout

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # callbacks
        self.on_raw_event: Optional[Callable[[str], None]] = None
        self.on_event: Optional[Callable[[Any], None]] = None
        self.on_connection_state_changed: Optional[Callable[[SSEConnectionState, Optional[Exception]], None]] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="wsapi-sse", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    # --- internals ---
    def _emit_state(self, state: SSEConnectionState, exc: Optional[Exception] = None) -> None:
        if self.on_connection_state_changed:
            try:
                self.on_connection_state_changed(state, exc)
            except Exception:
                pass

    def _emit_event(self, data: str) -> None:
        # raw dispatch
        if self.on_raw_event:
            try:
                self.on_raw_event(data)
            except Exception:
                pass
        # parsed dispatch
        if self.on_event:
            try:
                evt = parse_event(data)
                self.on_event(evt)
            except Exception:
                # swallow parsing or handler errors
                pass

    def _run(self) -> None:
        with httpx.Client(base_url=self._base_url, headers=self._headers, timeout=self._timeout) as client:
            while not self._stop_event.is_set():
                self._emit_state(SSEConnectionState.CONNECTING)
                try:
                    with client.stream("GET", "/events/stream") as resp:
                        if resp.status_code // 100 != 2:
                            self._emit_state(SSEConnectionState.ERROR)
                            # drain text for some context (not raising)
                            _ = resp.text
                            raise RuntimeError(f"SSE connection failed: {resp.status_code}")
                        self._emit_state(SSEConnectionState.CONNECTED)
                        for line in resp.iter_lines():
                            if self._stop_event.is_set():
                                break
                            if not line:
                                continue
                            # Only process lines starting with 'data:'
                            if line.startswith("data:"):
                                payload = line[len("data:"):].strip()
                                if payload:
                                    self._emit_event(payload)
                except Exception as exc:
                    self._emit_state(SSEConnectionState.ERROR, exc)
                    if not self._auto_reconnect or self._stop_event.is_set():
                        break
                    self._emit_state(SSEConnectionState.RECONNECTING)
                    time.sleep(self._reconnect_delay)
                finally:
                    self._emit_state(SSEConnectionState.DISCONNECTED)

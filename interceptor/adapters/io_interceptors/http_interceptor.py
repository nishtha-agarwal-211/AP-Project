from __future__ import annotations

import base64
import datetime
from typing import Any, Callable

import httpx

from .recorder import IORecorder

_SECRET_HEADERS = {"authorization", "proxy-authorization", "x-api-key", "api-key",
                   "cookie", "set-cookie"}
_REBUILD_DROP = {"content-encoding", "content-length", "transfer-encoding"}


def _safe_headers(headers: httpx.Headers, drop: set[str] = frozenset()) -> dict[str, str]:
    blocked = _SECRET_HEADERS | drop
    return {k.lower(): v for k, v in headers.items() if k.lower() not in blocked}


def _encode_body(raw: bytes) -> dict[str, str]:
    try:
        return {"body": raw.decode("utf-8")}
    except UnicodeDecodeError:
        return {"body_b64": base64.b64encode(raw).decode("ascii")}


def _decode_body(data: dict[str, Any]) -> bytes:
    if "body_b64" in data:
        return base64.b64decode(data["body_b64"])
    return data.get("body", "").encode("utf-8")


def _describe_request(request: httpx.Request) -> dict[str, Any]:
    try:
        body = request.content
    except httpx.RequestNotRead:
        body = b""
    return {"method": request.method, "url": str(request.url),
            "headers": _safe_headers(request.headers), **_encode_body(body)}


def _describe_response(resp: httpx.Response) -> dict[str, Any]:
    return {"status": resp.status_code,
            "headers": _safe_headers(resp.headers, _REBUILD_DROP),
            **_encode_body(resp.content)}


def _rebuild(data: dict[str, Any], request: httpx.Request) -> httpx.Response:
    resp = httpx.Response(status_code=data["status"], headers=data["headers"],
                          content=_decode_body(data), request=request)
    resp.elapsed = datetime.timedelta(0)
    return resp


def install_httpx(recorder: IORecorder) -> Callable[[], None]:
    original_send = httpx.Client.send
    original_asend = httpx.AsyncClient.send

    def send(self, request, **kwargs):
        def live() -> dict[str, Any]:
            resp = original_send(self, request, **kwargs)
            resp.read()
            return _describe_response(resp)
        return _rebuild(recorder.intercept("http", _describe_request(request), live), request)

    async def asend(self, request, **kwargs):
        async def live() -> dict[str, Any]:
            resp = await original_asend(self, request, **kwargs)
            await resp.aread()
            return _describe_response(resp)
        data = await recorder.aintercept("http", _describe_request(request), live)
        return _rebuild(data, request)

    httpx.Client.send = send  # type: ignore[method-assign]
    httpx.AsyncClient.send = asend  # type: ignore[method-assign]

    def uninstall() -> None:
        httpx.Client.send = original_send  # type: ignore[method-assign]
        httpx.AsyncClient.send = original_asend  # type: ignore[method-assign]

    return uninstall
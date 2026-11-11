import asyncio

import httpx

from interceptor.adapters.io_interceptors.http_interceptor import install_httpx
from interceptor.adapters.io_interceptors.recorder import IORecorder
from interceptor.config import Mode
from interceptor.controllers.replay_controller import ReplayController
from interceptor.tests.adapters.helpers import trace_from

URL = "https://api.example.com/x"


def _handler(counter):
    def handler(request):
        counter["n"] += 1
        return httpx.Response(200, json={"answer": 42},
                              headers={"x-test": "1", "set-cookie": "s=1"})
    return handler


def test_record_then_replay_makes_no_network_call():
    calls = {"n": 0}
    rec = IORecorder(Mode.RECORD, lambda: 1)
    uninstall = install_httpx(rec)
    try:
        with httpx.Client(transport=httpx.MockTransport(_handler(calls))) as c:
            r = c.get(URL, headers={"Authorization": "Bearer secret"})
        assert r.json() == {"answer": 42}
    finally:
        uninstall()

    logs = rec.drain()
    assert calls["n"] == 1 and logs[0].kind == "http"
    assert "secret" not in str(logs[0].req_payload)
    assert "set-cookie" not in logs[0].res_payload["headers"]

    replay = IORecorder(Mode.REPLAY, lambda: 1, ReplayController(trace_from(logs)))
    uninstall = install_httpx(replay)
    try:
        with httpx.Client(transport=httpx.MockTransport(_handler(calls))) as c:
            assert c.get(URL).json() == {"answer": 42}
    finally:
        uninstall()
    assert calls["n"] == 1  # no second network call

def test_async_client_is_intercepted():
    calls = {"n": 0}
    rec = IORecorder(Mode.RECORD, lambda: 1)

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(_handler(calls))) as c:
            return (await c.get(URL)).json()

    uninstall = install_httpx(rec)
    try:
        assert asyncio.run(go()) == {"answer": 42}
    finally:
        uninstall()
    assert len(rec.drain()) == 1
    
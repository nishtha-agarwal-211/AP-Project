from __future__ import annotations

from threading import Lock
from typing import Any, Awaitable, Callable

from interceptor.config import Mode
from interceptor.controllers.replay_controller import ReplayController
from interceptor.models.step import IOLog


class IORecorder:
    """Numbers every intercepted call and, in replay, answers from the trace.

    RECORD and LIVE both call the real thing and log it. REPLAY never calls it.
    Satisfies the IOCollector port via drain().
    """

    def __init__(
        self,
        mode: Mode,
        tick_provider: Callable[[], int],
        replay: ReplayController | None = None,
    ) -> None:
        if mode is Mode.REPLAY and replay is None:
            raise ValueError("replay mode needs a ReplayController")
        self._mode = mode
        self._tick = tick_provider
        self._replay = replay
        self._seq = 0
        self._logs: list[IOLog] = []
        self._lock = Lock()

    def _reserve(self) -> int:
        with self._lock:
            seq = self._seq
            self._seq += 1
            return seq

    def _store(self, seq: int, kind: str, request: dict, response: dict) -> None:
        with self._lock:
            self._logs.append(
                IOLog(io_seq_no=seq, kind=kind, req_payload=request, res_payload=response)
            )

    def intercept(self, kind: str, request: dict[str, Any],
                  live_call: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        seq = self._reserve()
        if self._mode is Mode.REPLAY:
            response = self._replay.response_for(self._tick(), seq)  # type: ignore[union-attr]
        else:
            response = live_call()
        self._store(seq, kind, request, response)
        return response

    async def aintercept(self, kind: str, request: dict[str, Any],
                         live_call: Callable[[], Awaitable[dict[str, Any]]]) -> dict[str, Any]:
        seq = self._reserve()
        if self._mode is Mode.REPLAY:
            response = self._replay.response_for(self._tick(), seq)  # type: ignore[union-attr]
        else:
            response = await live_call()
        self._store(seq, kind, request, response)
        return response

    def drain(self) -> list[IOLog]:
        """Return this step's logs and restart numbering at 0 for the next step."""
        with self._lock:
            logs = sorted(self._logs, key=lambda log: log.io_seq_no)
            self._logs = []
            self._seq = 0
            return logs
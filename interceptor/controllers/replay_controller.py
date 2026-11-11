from __future__ import annotations

from collections import defaultdict

from interceptor.models.trace import Trace


class ReplayMiss(Exception):
    """A live call happened that the recorded trace has no answer for."""


class ReplayController:
    """Serves recorded I/O responses so replay needs no network."""

    def __init__(self, trace: Trace) -> None:
        self._trace = trace
        self._cursor: dict[int, int] = defaultdict(int)

    @property
    def locked_seed(self) -> int:
        return self._trace.locked_seed

    def response_for(self, tick: int, io_seq_no: int) -> dict:
        resp = self._trace.recorded_response(tick, io_seq_no)
        if resp is None:
            raise ReplayMiss(f"no recorded response for tick={tick} io_seq_no={io_seq_no}")
        return resp

    def next_response(self, tick: int) -> dict:
        """The Nth intercepted call in this step gets the Nth recorded response."""
        seq = self._cursor[tick]
        resp = self.response_for(tick, seq)
        self._cursor[tick] += 1
        return resp
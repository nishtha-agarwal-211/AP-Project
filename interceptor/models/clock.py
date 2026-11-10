from __future__ import annotations

from threading import Lock


class LamportClock:
    """Strictly monotonic logical clock: L0, L1, L2, ..."""

    def __init__(self, start: int = 0) -> None:
        if start < 0:
            raise ValueError("start must be >= 0")
        self._value = start
        self._lock = Lock()

    @property
    def value(self) -> int:
        return self._value

    def tick(self) -> int:
        """Advance on a discrete agent event and return the new tick."""
        with self._lock:
            self._value += 1
            return self._value

    def observe(self, other: int) -> int:
        """Merge a remote/recorded tick: max(local, other) + 1."""
        with self._lock:
            self._value = max(self._value, other) + 1
            return self._value

    def as_float(self) -> float:
        """Value handed back by the patched time.time()."""
        return float(self._value)
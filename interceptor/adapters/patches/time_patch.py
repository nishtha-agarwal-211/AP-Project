from __future__ import annotations

import time
from typing import Callable

from interceptor.models.clock import LamportClock


def install_time_patch(clock: LamportClock) -> Callable[[], None]:
    """time.time() / time_ns() now return the logical clock. Returns an uninstall function."""
    original_time, original_time_ns = time.time, time.time_ns
    time.time = clock.as_float
    time.time_ns = lambda: clock.value * 1_000_000_000

    def uninstall() -> None:
        time.time, time.time_ns = original_time, original_time_ns

    return uninstall
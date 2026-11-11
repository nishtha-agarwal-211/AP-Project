import time
from interceptor.adapters.patches.time_patch import install_time_patch
from interceptor.models.clock import LamportClock


def test_time_returns_logical_clock_and_restores():
    clock = LamportClock()
    uninstall = install_time_patch(clock)
    try:
        assert time.time() == 0.0
        clock.tick()
        assert time.time() == 1.0
        assert time.time_ns() == 1_000_000_000
    finally:
        uninstall()
    assert time.time() > 1_000_000_000
import datetime
from interceptor.adapters.patches.datetime_patch import install_datetime_patch
from interceptor.models.clock import LamportClock


def test_now_is_logical_and_advances():
    real = datetime.datetime
    clock = LamportClock()
    uninstall = install_datetime_patch(clock)
    try:
        a = datetime.datetime.now()
        clock.tick()
        b = datetime.datetime.now()
        assert (b - a).total_seconds() == 1
        assert datetime.datetime.now() == b
        assert datetime.datetime.now(datetime.timezone.utc).tzinfo is not None
    finally:
        uninstall()
    assert datetime.datetime is real
    
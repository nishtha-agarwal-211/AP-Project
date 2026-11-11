from __future__ import annotations

import datetime as _dt
from typing import Callable

from interceptor.models.clock import LamportClock

LOGICAL_EPOCH = _dt.datetime(2026, 1, 1, tzinfo=_dt.timezone.utc)


def install_datetime_patch(clock: LamportClock) -> Callable[[], None]:
    real = _dt.datetime

    class LogicalDatetime(real):  # type: ignore[valid-type, misc]
        @classmethod
        def now(cls, tz=None):
            moment = LOGICAL_EPOCH + _dt.timedelta(seconds=clock.value)
            moment = moment.replace(tzinfo=None) if tz is None else moment.astimezone(tz)
            return cls(moment.year, moment.month, moment.day, moment.hour,
                       moment.minute, moment.second, moment.microsecond, moment.tzinfo)

        @classmethod
        def utcnow(cls):
            return cls.now()

        @classmethod
        def today(cls):
            return cls.now()

    _dt.datetime = LogicalDatetime

    def uninstall() -> None:
        _dt.datetime = real

    return uninstall
import pytest
from interceptor.adapters.io_interceptors.recorder import IORecorder
from interceptor.config import Mode
from interceptor.controllers.replay_controller import ReplayController
from interceptor.tests.adapters.helpers import trace_from


def test_record_numbers_calls_and_drain_resets():
    rec = IORecorder(Mode.RECORD, lambda: 1)
    rec.intercept("http", {"u": 1}, lambda: {"r": "a"})
    rec.intercept("http", {"u": 2}, lambda: {"r": "b"})
    assert [log.io_seq_no for log in rec.drain()] == [0, 1]
    assert rec.drain() == []
    rec.intercept("http", {}, lambda: {})
    assert rec.drain()[0].io_seq_no == 0

def test_replay_never_calls_live():
    rec = IORecorder(Mode.RECORD, lambda: 1)
    rec.intercept("http", {}, lambda: {"r": "recorded"})
    replay = IORecorder(Mode.REPLAY, lambda: 1, ReplayController(trace_from(rec.drain())))

    def boom():
        raise AssertionError("live call during replay")

    assert replay.intercept("http", {}, boom) == {"r": "recorded"}

def test_replay_requires_controller():
    with pytest.raises(ValueError):
        IORecorder(Mode.REPLAY, lambda: 1)
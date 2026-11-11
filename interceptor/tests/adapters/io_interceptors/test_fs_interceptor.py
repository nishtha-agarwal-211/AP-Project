from interceptor.adapters.io_interceptors.fs_interceptor import install_fs_read
from interceptor.adapters.io_interceptors.recorder import IORecorder
from interceptor.config import Mode
from interceptor.controllers.replay_controller import ReplayController
from interceptor.tests.adapters.helpers import trace_from


def test_read_inside_root_is_recorded_and_replayed(tmp_path):
    f = tmp_path / "note.txt"
    f.write_text("hello")
    rec = IORecorder(Mode.RECORD, lambda: 1)
    undo = install_fs_read(rec, [tmp_path])
    try:
        with open(f) as fh:
            assert fh.read() == "hello"
    finally:
        undo()
    logs = rec.drain()
    assert logs[0].kind == "fs_read"

    f.unlink()  # file gone: replay must not need it
    replay = IORecorder(Mode.REPLAY, lambda: 1, ReplayController(trace_from(logs)))
    undo = install_fs_read(replay, [tmp_path])
    try:
        with open(f) as fh:
            assert fh.read() == "hello"
    finally:
        undo()

def test_reads_outside_root_are_untouched(tmp_path):
    other = tmp_path / "other.txt"
    other.write_text("x")
    rec = IORecorder(Mode.RECORD, lambda: 1)
    undo = install_fs_read(rec, [tmp_path / "sandbox"])
    try:
        with open(other) as fh:
            fh.read()
    finally:
        undo()
    assert rec.drain() == []
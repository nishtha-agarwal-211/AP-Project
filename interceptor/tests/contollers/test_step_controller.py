# test_step_controller.py
import pytest
from interceptor.controllers.guardrail_controller import GuardrailController
from interceptor.controllers.step_controller import ExecutionPaused, StepController
from interceptor.models.clock import LamportClock
from interceptor.models.contract import ChangeContract
from interceptor.models.step import ASTMetrics, IOLog
from interceptor.views.commit_view import CommitResponse


class FakeSink:
    def __init__(self): self.steps = []
    def commit(self, step):
        self.steps.append(step)
        return CommitResponse(node_id="n", state_hash="h", gate_passed=True, cumulative_cost=0.0)

class FakeEmbedder:
    def embed(self, text): return [0.0] * 1536

class FakeIO:
    def drain(self):
        return [IOLog(io_seq_no=0, kind="http", req_payload={"url": "x"}, res_payload={"ok": 1})]

class FakeAnalyzer:
    def __init__(self, m=None): self.m = m or ASTMetrics()
    def analyze(self, code): return self.m

class FakeJail:
    def files_created_delta(self): return 0


def _make(analyzer=None):
    sink = FakeSink()
    guard = GuardrailController(ChangeContract(), analyzer or FakeAnalyzer(), FakeJail())
    ctrl = StepController("b1", "a1", LamportClock(), sink, FakeEmbedder(), FakeIO(), guard)
    return ctrl, sink


def test_commits_with_increasing_ticks():
    ctrl, sink = _make()
    ctrl.handle_event("p1", "o1", {"s": 1})
    ctrl.handle_event("p2", "o2", {"s": 2})
    assert [s.lamport_tick for s in sink.steps] == [1, 2]
    assert sink.steps[0].io_logs[0].io_seq_no == 0

def test_failed_gate_commits_then_pauses():
    ctrl, sink = _make(FakeAnalyzer(ASTMetrics(dead_ast_nodes=1)))
    with pytest.raises(ExecutionPaused) as exc:
        ctrl.handle_event("p", "o", {"s": 1}, proposed_code="def f(): pass")
    assert len(sink.steps) == 1                      # committed before pausing
    assert sink.steps[0].ast_metrics.gate_passed is False
    assert exc.value.tick == 1
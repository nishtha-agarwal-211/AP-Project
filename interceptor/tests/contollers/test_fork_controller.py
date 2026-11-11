import pytest
from interceptor.controllers.fork_controller import (
    CachedStepLeak, ForkController, ForkError,
)
from interceptor.views.fork_view import ForkResponse


class FakeClient:
    def __init__(self, cost=0.0): self.cost, self.requests = cost, []
    def fork(self, req):
        self.requests.append(req)
        return ForkResponse(new_branch_id="b2", cached_steps_copied=req.fork_lamport_tick - 1,
                            replay_token_cost=self.cost)

class FakeLoader:
    def __init__(self): self.asked = None
    def load_state(self, branch_id, tick):
        self.asked = (branch_id, tick)
        return {"memory": "old", "step": tick}

class FakeRuntime:
    def __init__(self): self.hydrated = None; self.resumed = None
    def hydrate(self, state): self.hydrated = state
    def resume(self, branch_id, from_tick, edited_prompt):
        self.resumed = (branch_id, from_tick, edited_prompt)

class FakeCallLog:
    def __init__(self, n=0): self.n = n
    def live_calls_before(self, tick): return self.n


def _make(cost=0.0, leaked=0):
    client, loader, runtime = FakeClient(cost), FakeLoader(), FakeRuntime()
    return ForkController(client, loader, runtime, FakeCallLog(leaked)), client, loader, runtime


def test_hydrates_from_k_minus_1_and_resumes_at_k():
    ctrl, _, loader, runtime = _make()
    result = ctrl.fork_and_resume("b1", 5, 99, edited_prompt="new prompt")
    assert loader.asked == ("b2", 4)
    assert runtime.hydrated == {"memory": "old", "step": 4}
    assert runtime.resumed == ("b2", 5, "new prompt")
    assert result.live_from_tick == 5

def test_edited_state_overrides_loaded_state():
    ctrl, _, _, runtime = _make()
    ctrl.fork_and_resume("b1", 3, 1, edited_state={"memory": "edited"})
    assert runtime.hydrated["memory"] == "edited"

def test_fork_without_edit_is_rejected():
    ctrl, *_ = _make()
    with pytest.raises(Exception):
        ctrl.fork_and_resume("b1", 3, 1)

def test_k_below_one_rejected():
    ctrl, *_ = _make()
    with pytest.raises(ForkError):
        ctrl.fork_and_resume("b1", 0, 1, edited_prompt="x")

def test_nonzero_replay_cost_rejected():
    ctrl, *_ = _make(cost=0.02)
    with pytest.raises(ForkError):
        ctrl.fork_and_resume("b1", 3, 1, edited_prompt="x")

def test_verify_cached_prefix_flags_leaks():
    ctrl, *_ = _make(leaked=2)
    with pytest.raises(CachedStepLeak):
        ctrl.verify_cached_prefix(5)

def test_verify_cached_prefix_ok_when_clean():
    ctrl, *_ = _make(leaked=0)
    ctrl.verify_cached_prefix(5)
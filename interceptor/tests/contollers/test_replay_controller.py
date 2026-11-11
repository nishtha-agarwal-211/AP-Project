# test_replay_controller.py
import pytest
from interceptor.controllers.replay_controller import ReplayController, ReplayMiss
from interceptor.models.step import IOLog, StepCommit
from interceptor.models.trace import Trace


def _trace():
    step = StepCommit(
        branch_id="b1", lamport_tick=1, agent_id="a1", prompt_input="p", llm_output="o",
        state_blob={}, embedding=[0.0] * 1536,
        io_logs=[
            IOLog(io_seq_no=0, kind="http", req_payload={}, res_payload={"r": "first"}),
            IOLog(io_seq_no=1, kind="http", req_payload={}, res_payload={"r": "second"}),
        ],
    )
    return Trace(locked_seed=42, steps=[step])


def test_serves_recorded_responses_in_order():
    r = ReplayController(_trace())
    assert r.next_response(1) == {"r": "first"}
    assert r.next_response(1) == {"r": "second"}

def test_missing_response_raises():
    r = ReplayController(_trace())
    with pytest.raises(ReplayMiss):
        r.response_for(1, 5)

def test_exposes_locked_seed():
    assert ReplayController(_trace()).locked_seed == 42
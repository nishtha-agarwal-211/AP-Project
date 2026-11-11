# test_commit_view.py
import json
from interceptor.models.step import StepCommit
from interceptor.views.commit_view import (
    canonical_json, render_commit_body, render_state_blob, parse_commit_response,
)

def _step(**kw):
    d = dict(branch_id="b1", lamport_tick=0, agent_id="a1", prompt_input="p",
             llm_output="o", state_blob={"b": 2, "a": 1}, embedding=[0.0] * 1536)
    return StepCommit(**{**d, **kw})

def test_canonical_json_sorted_and_compact():
    assert canonical_json({"b": 2, "a": {"d": 1, "c": 2}}) == '{"a":{"c":2,"d":1},"b":2}'

def test_key_order_does_not_change_bytes():
    a = _step(state_blob={"a": 1, "b": 2})
    b = _step(state_blob={"b": 2, "a": 1})
    assert render_commit_body(a) == render_commit_body(b)
    assert render_state_blob(a) == '{"a":1,"b":2}'

def test_body_is_valid_json_with_all_fields():
    body = json.loads(render_commit_body(_step()))
    assert {"branch_id", "lamport_tick", "embedding", "io_logs", "ast_metrics"} <= body.keys()

def test_nan_rejected():
    import pytest
    with pytest.raises(ValueError):
        canonical_json({"x": float("nan")})

def test_parse_commit_response():
    r = parse_commit_response(
        {"node_id": "n1", "state_hash": "abc", "gate_passed": True, "cumulative_cost": 0.5})
    assert r.gate_passed is True
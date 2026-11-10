# test_fork_view.py
import json
import pytest
from pydantic import ValidationError
from interceptor.views.fork_view import ForkRequest, render_fork_body, parse_fork_response

def test_fork_requires_an_edit():
    with pytest.raises(ValidationError):
        ForkRequest(parent_branch_id="b1", fork_lamport_tick=5, locked_prng_seed=1)

def test_fork_body_omits_none_and_is_sorted():
    req = ForkRequest(parent_branch_id="b1", fork_lamport_tick=5,
                      locked_prng_seed=1, edited_prompt="new")
    body = render_fork_body(req)
    assert "edited_state" not in json.loads(body)
    assert body.startswith('{"edited_prompt"')

def test_parse_fork_response_zero_cost():
    r = parse_fork_response(
        {"new_branch_id": "b2", "cached_steps_copied": 5, "replay_token_cost": 0.0})
    assert r.replay_token_cost == 0.0
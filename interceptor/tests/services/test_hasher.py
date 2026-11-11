from interceptor.models.step import StepCommit
from interceptor.services.hasher import state_hash, state_hash_sequence

def _step(tick, state):
    return StepCommit(branch_id="b", lamport_tick=tick, agent_id="a", prompt_input="p",
                      llm_output="o", state_blob=state, embedding=[0.0] * 1536)

def test_key_order_does_not_change_hash():
    assert state_hash({"a": 1, "b": 2}) == state_hash({"b": 2, "a": 1})

def test_different_state_different_hash():
    assert state_hash({"a": 1}) != state_hash({"a": 2})

def test_hash_is_64_hex_chars():
    assert len(state_hash({})) == 64

def test_sequence_is_ordered_by_tick():
    steps = [_step(2, {"n": 2}), _step(1, {"n": 1})]
    assert state_hash_sequence(steps) == [state_hash({"n": 1}), state_hash({"n": 2})]
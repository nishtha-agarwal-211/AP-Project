# test_step.py
import pytest
from pydantic import ValidationError
from interceptor.models.step import StepCommit

def _base(**kw):
    d = dict(branch_id="b1", lamport_tick=0, agent_id="a1", prompt_input="p",
             llm_output="o", state_blob={"k": 1}, embedding=[0.0] * 1536)
    return {**d, **kw}

def test_valid_commit():
    assert StepCommit(**_base()).lamport_tick == 0

def test_wrong_embedding_size_rejected():
    with pytest.raises(ValidationError):
        StepCommit(**_base(embedding=[0.0] * 10))
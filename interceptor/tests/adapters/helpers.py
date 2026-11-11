from interceptor.models.step import StepCommit
from interceptor.models.trace import Trace


def trace_from(logs, tick=1):
    step = StepCommit(branch_id="b", lamport_tick=tick, agent_id="a", prompt_input="p",
                      llm_output="o", state_blob={}, embedding=[0.0] * 1536, io_logs=logs)
    return Trace(locked_seed=1, steps=[step])
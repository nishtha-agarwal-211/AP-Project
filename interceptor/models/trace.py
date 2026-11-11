from __future__ import annotations

from pydantic import BaseModel, Field

from .step import StepCommit


class Trace(BaseModel):
    """A recorded run, used by replay mode."""
    locked_seed: int
    steps: list[StepCommit] = Field(default_factory=list)

    def step_at(self, tick: int) -> StepCommit | None:
        return next((s for s in self.steps if s.lamport_tick == tick), None)

    def recorded_response(self, tick: int, io_seq_no: int) -> dict | None:
        step = self.step_at(tick)
        if step is None:
            return None
        for log in step.io_logs:
            if log.io_seq_no == io_seq_no:
                return log.res_payload
        return None
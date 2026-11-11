from __future__ import annotations

from typing import Any

from interceptor.models.clock import LamportClock
from interceptor.models.contract import GateResult
from interceptor.models.step import StepCommit
from interceptor.views.commit_view import CommitResponse
from interceptor.views.events_view import render_gate_pause_message

from .guardrail_controller import GuardrailController
from .ports import CommitSink, Embedder, IOCollector


class ExecutionPaused(Exception):
    """Raised after a gate-failed step is committed, so the agent stops."""

    def __init__(self, tick: int, result: GateResult) -> None:
        super().__init__(render_gate_pause_message(tick, result))
        self.tick = tick
        self.result = result


class StepController:
    def __init__(
        self,
        branch_id: str,
        agent_id: str,
        clock: LamportClock,
        sink: CommitSink,
        embedder: Embedder,
        io: IOCollector,
        guardrails: GuardrailController,
    ) -> None:
        self._branch_id = branch_id
        self._agent_id = agent_id
        self._clock = clock
        self._sink = sink
        self._embedder = embedder
        self._io = io
        self._guardrails = guardrails

    def handle_event(
        self,
        prompt_input: str,
        llm_output: str,
        state_blob: dict[str, Any],
        token_cost: float = 0.0,
        proposed_code: str | None = None,
    ) -> CommitResponse:
        tick = self._clock.tick()
        io_logs = self._io.drain()
        embedding = self._embedder.embed(llm_output)
        metrics, result = self._guardrails.check(proposed_code)

        step = StepCommit(
            branch_id=self._branch_id,
            lamport_tick=tick,
            agent_id=self._agent_id,
            prompt_input=prompt_input,
            llm_output=llm_output,
            token_cost=token_cost,
            state_blob=state_blob,
            embedding=embedding,
            io_logs=io_logs,
            ast_metrics=metrics,
        )
        response = self._sink.commit(step)  # commit first so the UI can show the red node

        if not result.passed:
            raise ExecutionPaused(tick, result)
        return response
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from interceptor.views.fork_view import ForkRequest

from .ports import AgentRuntime, ForkClient, LLMCallLog, StateLoader


class CachedStepLeak(Exception):
    """A cached prefix step made a live LLM call (breaks the $0.00 fork KPI)."""


class ForkError(Exception):
    pass


@dataclass(frozen=True)
class ForkResult:
    new_branch_id: str
    cached_steps_copied: int
    live_from_tick: int


class ForkController:
    """Runtime router: hydrate from Step K-1, apply the edit at K, go live from K."""

    def __init__(
        self,
        client: ForkClient,
        loader: StateLoader,
        runtime: AgentRuntime,
        call_log: LLMCallLog,
    ) -> None:
        self._client = client
        self._loader = loader
        self._runtime = runtime
        self._call_log = call_log

    def fork_and_resume(
        self,
        parent_branch_id: str,
        k: int,
        locked_seed: int,
        edited_prompt: str | None = None,
        edited_state: dict[str, Any] | None = None,
    ) -> ForkResult:
        if k < 1:
            raise ForkError("cannot fork before step 1: there is no K-1 to hydrate from")

        req = ForkRequest(
            parent_branch_id=parent_branch_id,
            fork_lamport_tick=k,
            locked_prng_seed=locked_seed,
            edited_prompt=edited_prompt,
            edited_state=edited_state,
        )
        resp = self._client.fork(req)
        if resp.replay_token_cost != 0.0:
            raise ForkError(f"fork reported replay cost {resp.replay_token_cost}, expected 0.0")

        state = dict(self._loader.load_state(resp.new_branch_id, k - 1))
        if edited_state:
            state.update(edited_state)  # shallow merge, edit wins

        self._runtime.hydrate(state)
        self._runtime.resume(resp.new_branch_id, from_tick=k, edited_prompt=edited_prompt)

        return ForkResult(resp.new_branch_id, resp.cached_steps_copied, live_from_tick=k)

    def verify_cached_prefix(self, k: int) -> None:
        """Call after the resumed run: no live LLM call may belong to ticks before K."""
        leaked = self._call_log.live_calls_before(k)
        if leaked:
            raise CachedStepLeak(f"{leaked} live LLM call(s) happened before tick {k}")
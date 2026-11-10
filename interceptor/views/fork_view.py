from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from .commit_view import canonical_json


class ForkRequest(BaseModel):
    """Body for POST /api/branches/fork."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    parent_branch_id: str
    fork_lamport_tick: int  # K
    locked_prng_seed: int
    edited_prompt: str | None = None
    edited_state: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _needs_an_edit(self) -> "ForkRequest":
        if self.edited_prompt is None and self.edited_state is None:
            raise ValueError("a fork needs edited_prompt or edited_state")
        return self


class ForkResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    new_branch_id: str
    cached_steps_copied: int
    replay_token_cost: float


def render_fork_body(req: ForkRequest) -> str:
    return canonical_json(req.model_dump(mode="json", exclude_none=True))


def parse_fork_response(data: dict[str, Any]) -> ForkResponse:
    return ForkResponse(**data)
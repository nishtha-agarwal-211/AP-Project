from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict

from interceptor.models.step import StepCommit


def canonical_json(obj: Any) -> str:
    """Sorted keys, no whitespace, UTF-8 friendly.

    This is the single serialization format for payloads. Person 2 hashes
    the state with SHA-256, so every byte here must be deterministic.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,  # NaN/Infinity would break cross-language hashing
    )


def render_commit(step: StepCommit) -> dict[str, Any]:
    """StepCommit -> plain JSON-safe dict for POST /api/steps/commit."""
    return step.model_dump(mode="json")


def render_commit_body(step: StepCommit) -> str:
    """The exact request body string sent to the API."""
    return canonical_json(render_commit(step))


def render_state_blob(step: StepCommit) -> str:
    """Canonical form of the state alone (the part Person 2 hashes)."""
    return canonical_json(step.state_blob)


class CommitResponse(BaseModel):
    """Shape returned by /api/steps/commit."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str
    state_hash: str
    gate_passed: bool
    cumulative_cost: float


def parse_commit_response(data: dict[str, Any]) -> CommitResponse:
    return CommitResponse(**data)
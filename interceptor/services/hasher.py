from __future__ import annotations

import hashlib
from typing import Any

from interceptor.models.step import StepCommit
from interceptor.views.commit_view import canonical_json


def sha256_hex(obj: Any) -> str:
    """SHA-256 of the canonical JSON form of obj."""
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def state_hash(state_blob: dict[str, Any]) -> str:
    """Local twin of the hash Person 2 computes server-side (FR-1.4)."""
    return sha256_hex(state_blob)


def state_hash_sequence(steps: list[StepCommit]) -> list[str]:
    """Ordered hashes of a run, used to compare two replays."""
    ordered = sorted(steps, key=lambda s: s.lamport_tick)
    return [state_hash(s.state_blob) for s in ordered]
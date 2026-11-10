from __future__ import annotations

from typing import Any

from interceptor.models.contract import GateResult


def render_gate_pause(tick: int, result: GateResult) -> dict[str, Any]:
    """Structured pause signal the controller raises/logs when a gate fails."""
    return {
        "event": "gate_pause",
        "lamport_tick": tick,
        "gate_passed": result.passed,
        "violations": list(result.violations),
    }


def render_gate_pause_message(tick: int, result: GateResult) -> str:
    """Human-readable line for the terminal."""
    if result.passed:
        return f"[tick {tick}] gate passed"
    return f"[tick {tick}] PAUSED, gate failed: " + "; ".join(result.violations)


def render_step_log(tick: int, agent_id: str, gate_passed: bool) -> str:
    status = "ok" if gate_passed else "blocked"
    return f"[tick {tick}] agent={agent_id} commit={status}"
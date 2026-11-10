# test_events_view.py
from interceptor.models.contract import GateResult
from interceptor.views.events_view import render_gate_pause, render_gate_pause_message

def test_pause_payload():
    p = render_gate_pause(7, GateResult(passed=False, violations=["dead_ast_nodes 2 > 0"]))
    assert p["gate_passed"] is False and p["violations"] == ["dead_ast_nodes 2 > 0"]

def test_pause_message():
    msg = render_gate_pause_message(7, GateResult(passed=False, violations=["x", "y"]))
    assert "PAUSED" in msg and "x; y" in msg
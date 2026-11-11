# test_guardrail_controller.py
from interceptor.controllers.guardrail_controller import GuardrailController
from interceptor.models.contract import ChangeContract
from interceptor.models.step import ASTMetrics


class FakeAnalyzer:
    def __init__(self, metrics): self.metrics = metrics
    def analyze(self, code): return self.metrics

class FakeJail:
    def __init__(self, n=0): self.n = n
    def files_created_delta(self): return self.n


def test_clean_step_passes():
    g = GuardrailController(ChangeContract(), FakeAnalyzer(ASTMetrics()), FakeJail(0))
    metrics, result = g.check("x = 1")
    assert result.passed and metrics.gate_passed

def test_dead_code_blocks():
    g = GuardrailController(ChangeContract(), FakeAnalyzer(ASTMetrics(dead_ast_nodes=2)), FakeJail(0))
    metrics, result = g.check("def unused(): pass")
    assert not result.passed and metrics.gate_passed is False

def test_unauthorized_file_blocks():
    g = GuardrailController(ChangeContract(), FakeAnalyzer(ASTMetrics()), FakeJail(1))
    metrics, _ = g.check("x = 1")
    assert metrics.gate_passed is False and metrics.files_created_delta == 1

def test_no_code_skips_analyzer():
    g = GuardrailController(ChangeContract(), FakeAnalyzer(ASTMetrics(dead_ast_nodes=9)), FakeJail(0))
    _, result = g.check(None)
    assert result.passed
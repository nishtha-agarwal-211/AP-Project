from __future__ import annotations

from interceptor.models.contract import ChangeContract, GateResult
from interceptor.models.step import ASTMetrics

from .ports import CodeAnalyzer, FileJail


class GuardrailController:
    def __init__(self, contract: ChangeContract, analyzer: CodeAnalyzer, jail: FileJail) -> None:
        self._contract = contract
        self._analyzer = analyzer
        self._jail = jail

    def check(self, proposed_code: str | None) -> tuple[ASTMetrics, GateResult]:
        """Measure the step, compare to the Change Contract, set gate_passed."""
        code_metrics = self._analyzer.analyze(proposed_code) if proposed_code else ASTMetrics()
        measured = ASTMetrics(
            net_loc_delta=code_metrics.net_loc_delta,
            dead_ast_nodes=code_metrics.dead_ast_nodes,
            files_created_delta=self._jail.files_created_delta(),
        )
        result = self._contract.evaluate(measured)
        return measured.model_copy(update={"gate_passed": result.passed}), result
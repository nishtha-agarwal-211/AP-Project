from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .step import ASTMetrics


class GateResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    passed: bool
    violations: list[str] = Field(default_factory=list)


class ChangeContract(BaseModel):
    model_config = ConfigDict(frozen=True)
    max_allowed_files: int = 0
    max_net_loc: int | None = None
    max_dead_nodes: int = 0

    def evaluate(self, m: ASTMetrics) -> GateResult:
        v: list[str] = []
        if m.files_created_delta > self.max_allowed_files:
            v.append(f"files_created_delta {m.files_created_delta} > {self.max_allowed_files}")
        if self.max_net_loc is not None and m.net_loc_delta > self.max_net_loc:
            v.append(f"net_loc_delta {m.net_loc_delta} > {self.max_net_loc}")
        if m.dead_ast_nodes > self.max_dead_nodes:
            v.append(f"dead_ast_nodes {m.dead_ast_nodes} > {self.max_dead_nodes}")
        return GateResult(passed=not v, violations=v)
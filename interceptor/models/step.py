from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

EMBEDDING_DIM = 1536


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class IOLog(_Frozen):
    io_seq_no: int = Field(ge=0)
    kind: Literal["http", "fs_read"]
    req_payload: dict[str, Any]
    res_payload: dict[str, Any] | None = None


class ASTMetrics(_Frozen):
    net_loc_delta: int = 0
    dead_ast_nodes: int = Field(default=0, ge=0)
    files_created_delta: int = Field(default=0, ge=0)
    gate_passed: bool = True


class StepCommit(_Frozen):
    """Payload for POST /api/steps/commit."""
    branch_id: str
    lamport_tick: int = Field(ge=0)
    agent_id: str
    prompt_input: str
    llm_output: str
    token_cost: float = Field(default=0.0, ge=0)
    state_blob: dict[str, Any]
    embedding: list[float] = Field(min_length=EMBEDDING_DIM, max_length=EMBEDDING_DIM)
    io_logs: list[IOLog] = Field(default_factory=list)
    ast_metrics: ASTMetrics = Field(default_factory=ASTMetrics)
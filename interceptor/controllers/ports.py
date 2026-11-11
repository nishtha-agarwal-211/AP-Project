from __future__ import annotations

from typing import Any, Protocol

from interceptor.models.step import ASTMetrics, IOLog, StepCommit
from interceptor.views.commit_view import CommitResponse
from interceptor.views.fork_view import ForkRequest, ForkResponse


class CommitSink(Protocol):
    """Sends a step to the API (or the mock). Adapter: api_client."""
    def commit(self, step: StepCommit) -> CommitResponse: ...


class Embedder(Protocol):
    """Returns a 1536-dim vector. Service: embedder."""
    def embed(self, text: str) -> list[float]: ...


class IOCollector(Protocol):
    """Hands over the I/O captured since the last step. Adapter: io_interceptors."""
    def drain(self) -> list[IOLog]: ...


class CodeAnalyzer(Protocol):
    """Static analysis of proposed code. Service: ast_analyzer."""
    def analyze(self, code: str) -> ASTMetrics: ...


class FileJail(Protocol):
    """Reports files created in the overlay this step. Adapter: vfs."""
    def files_created_delta(self) -> int: ...


class ForkClient(Protocol):
    """Calls POST /api/branches/fork. Adapter: api_client."""
    def fork(self, req: ForkRequest) -> ForkResponse: ...


class StateLoader(Protocol):
    """Loads the saved state at a tick of a branch. Adapter: api_client."""
    def load_state(self, branch_id: str, tick: int) -> dict[str, Any]: ...


class AgentRuntime(Protocol):
    """The running agent. Adapter: frameworks (LangGraph / CrewAI)."""
    def hydrate(self, state: dict[str, Any]) -> None: ...
    def resume(self, branch_id: str, from_tick: int, edited_prompt: str | None) -> None: ...


class LLMCallLog(Protocol):
    """Records outbound LLM calls by tick. Adapter: io_interceptors."""
    def live_calls_before(self, tick: int) -> int: ...
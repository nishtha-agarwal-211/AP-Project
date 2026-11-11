from __future__ import annotations

import ast

from interceptor.models.step import ASTMetrics


class CodeParseError(Exception):
    """The proposed code is not valid Python."""


def count_loc(code: str) -> int:
    """Non-blank, non-comment lines."""
    return sum(
        1 for line in code.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )


def _referenced_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            names.add(n.id)
        elif isinstance(n, ast.Attribute):
            names.add(n.attr)
    return names


def _exported_names(tree: ast.Module) -> set[str]:
    """Names listed in __all__ count as used."""
    exported: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            if isinstance(node.value, (ast.List, ast.Tuple)):
                exported |= {
                    e.value for e in node.value.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                }
    return exported


def count_dead_functions(tree: ast.Module) -> int:
    """Top-level functions that nothing else in the snippet references."""
    exported = _exported_names(tree)
    dead = 0
    for i, node in enumerate(tree.body):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        name = node.name
        if (
            node.decorator_list                       # may be registered elsewhere
            or name == "main"
            or (name.startswith("__") and name.endswith("__"))
            or name in exported
        ):
            continue
        used = any(
            name in _referenced_names(other)
            for j, other in enumerate(tree.body) if j != i
        )
        if not used:
            dead += 1
    return dead


class AstAnalyzer:
    """Satisfies the CodeAnalyzer port (FR-4.2)."""

    def analyze(self, code: str, previous: str | None = None) -> ASTMetrics:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise CodeParseError(str(e)) from e
        baseline = count_loc(previous) if previous else 0
        return ASTMetrics(
            net_loc_delta=count_loc(code) - baseline,
            dead_ast_nodes=count_dead_functions(tree),
        )
import pytest
from interceptor.services.ast_analyzer import AstAnalyzer, CodeParseError, count_loc

def test_count_loc_ignores_blank_and_comments():
    assert count_loc("x = 1\n\n# note\ny = 2\n") == 2

def test_flags_unreferenced_function():
    code = "def used(): pass\ndef unused(): pass\nused()\n"
    assert AstAnalyzer().analyze(code).dead_ast_nodes == 1

def test_referenced_function_is_alive():
    assert AstAnalyzer().analyze("def f(): pass\nf()\n").dead_ast_nodes == 0

def test_recursion_alone_is_still_dead():
    code = "def f(n):\n    return f(n - 1)\n"
    assert AstAnalyzer().analyze(code).dead_ast_nodes == 1

def test_decorated_main_and_dunder_are_skipped():
    code = "@app.route('/')\ndef index(): pass\ndef main(): pass\ndef __repr__(): pass\n"
    assert AstAnalyzer().analyze(code).dead_ast_nodes == 0

def test_exported_function_is_alive():
    code = "__all__ = ['helper']\ndef helper(): pass\n"
    assert AstAnalyzer().analyze(code).dead_ast_nodes == 0

def test_net_loc_delta_against_previous():
    a = AstAnalyzer()
    assert a.analyze("x = 1\ny = 2\nz = 3\n", previous="x = 1\n").net_loc_delta == 2
    assert a.analyze("x = 1\n", previous="x = 1\ny = 2\n").net_loc_delta == -1

def test_syntax_error_raises_parse_error():
    with pytest.raises(CodeParseError):
        AstAnalyzer().analyze("def broken(:\n")
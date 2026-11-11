from interceptor.models.contract import ChangeContract
from interceptor.models.step import ASTMetrics

def test_blocks_unauthorized_file_and_dead_code():
    r = ChangeContract().evaluate(ASTMetrics(files_created_delta=1, dead_ast_nodes=2))
    assert not r.passed and len(r.violations) == 2

def test_passes_clean_step():
    assert ChangeContract(max_allowed_files=1).evaluate(ASTMetrics(files_created_delta=1)).passed
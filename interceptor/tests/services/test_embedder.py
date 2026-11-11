import math
from interceptor.services.embedder import CachedEmbedder, HashEmbedder

def test_dimension_and_unit_length():
    v = HashEmbedder().embed("hello")
    assert len(v) == 1536
    assert math.isclose(math.sqrt(sum(x * x for x in v)), 1.0, rel_tol=1e-9)

def test_deterministic_and_text_specific():
    e = HashEmbedder()
    assert e.embed("a") == e.embed("a")
    assert e.embed("a") != e.embed("b")

def test_cache_calls_inner_once():
    class Counting:
        n = 0
        def embed(self, text):
            Counting.n += 1
            return [0.0]
    c = CachedEmbedder(Counting())
    c.embed("x"); c.embed("x")
    assert Counting.n == 1
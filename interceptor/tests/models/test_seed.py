# test_seed.py
import pytest
from interceptor.models.seed import LockedSeed

def test_derive_is_deterministic_and_label_specific():
    s = LockedSeed(42)
    assert s.derive("random") == s.derive("random")
    assert s.derive("random") != s.derive("numpy")

def test_rejects_over_64_bits():
    with pytest.raises(ValueError):
        LockedSeed(1 << 64)

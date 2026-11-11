import random
from interceptor.adapters.patches.random_patch import install_seed, llm_sampling_params
from interceptor.models.seed import LockedSeed


def test_seed_makes_sequence_repeatable():
    seed = LockedSeed(42)
    undo = install_seed(seed)
    a = [random.random() for _ in range(3)]
    undo()
    undo = install_seed(seed)
    b = [random.random() for _ in range(3)]
    undo()
    assert a == b

def test_uninstall_restores_previous_state():
    random.seed(7)
    expected = random.random()
    random.seed(7)
    undo = install_seed(LockedSeed(42))
    random.random()
    undo()
    assert random.random() == expected

def test_llm_params_are_deterministic():
    p = llm_sampling_params(LockedSeed(42))
    assert p == llm_sampling_params(LockedSeed(42))
    assert p["temperature"] == 0.0
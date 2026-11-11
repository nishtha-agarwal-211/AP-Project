from __future__ import annotations

import random
from typing import Any, Callable

from interceptor.models.seed import LockedSeed


def install_seed(seed: LockedSeed) -> Callable[[], None]:
    """Seed `random` and numpy (if present). Uninstall restores the previous RNG state."""
    py_state = random.getstate()
    random.seed(seed.derive("random"))

    np: Any = None
    np_state = None
    try:
        import numpy as np  # type: ignore[no-redef]
        np_state = np.random.get_state()
        np.random.seed(seed.derive("numpy") % (2**32))  # numpy seeds are 32-bit
    except ImportError:
        pass

    def uninstall() -> None:
        random.setstate(py_state)
        if np is not None and np_state is not None:
            np.random.set_state(np_state)

    return uninstall


def llm_sampling_params(seed: LockedSeed, temperature: float = 0.0) -> dict[str, Any]:
    """Merge into every LLM call's kwargs so sampling is pinned (FR-1.2)."""
    return {"seed": seed.derive("llm") % (2**31), "temperature": temperature}
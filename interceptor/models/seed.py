from __future__ import annotations

import hashlib
from dataclasses import dataclass

MASK_64 = (1 << 64) - 1


@dataclass(frozen=True)
class LockedSeed:
    value: int

    def __post_init__(self) -> None:
        if not 0 <= self.value <= MASK_64:
            raise ValueError("seed must fit in 64 bits")

    def derive(self, label: str) -> int:
        """Deterministic sub-seed per consumer ('random', 'numpy', 'llm')."""
        digest = hashlib.sha256(f"{self.value}:{label}".encode()).digest()
        return int.from_bytes(digest[:8], "big")
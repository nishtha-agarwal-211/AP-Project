from __future__ import annotations

import hashlib
import math

from interceptor.models.step import EMBEDDING_DIM


class HashEmbedder:
    """Deterministic, offline, fake embedding: same text -> same unit vector.

    It carries no meaning, so cosine scores are only useful for plumbing and
    tests. The real model goes in adapters/ because it needs the network.
    """

    def embed(self, text: str) -> list[float]:
        values: list[float] = []
        block = 0
        while len(values) < EMBEDDING_DIM:
            digest = hashlib.sha256(f"{text}:{block}".encode("utf-8")).digest()
            values.extend((b - 127.5) / 127.5 for b in digest)
            block += 1
        values = values[:EMBEDDING_DIM]
        norm = math.sqrt(sum(v * v for v in values))
        return [v / norm for v in values]


class CachedEmbedder:
    """Wraps any embedder so repeated text is embedded once (replay needs this)."""

    def __init__(self, inner) -> None:
        self._inner = inner
        self._cache: dict[str, list[float]] = {}

    def embed(self, text: str) -> list[float]:
        if text not in self._cache:
            self._cache[text] = self._inner.embed(text)
        return self._cache[text]
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class Mode(str, Enum):
    RECORD = "record"
    REPLAY = "replay"
    LIVE = "live"


@dataclass(frozen=True)
class Config:
    mode: Mode = Mode.RECORD
    api_base_url: str = "http://localhost:8000"
    locked_seed: int | None = None
    max_allowed_files: int = 0
    max_net_loc: int | None = None
    max_dead_nodes: int = 0


def load_config() -> Config:
    return Config(
        mode=Mode(os.getenv("CHRONO_MODE", "record")),
        api_base_url=os.getenv("CHRONO_API_URL", "http://localhost:8000"),
        locked_seed=int(os.environ["CHRONO_SEED"]) if "CHRONO_SEED" in os.environ else None,
    )
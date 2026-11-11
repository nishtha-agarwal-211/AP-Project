from __future__ import annotations

import base64
import builtins
import io
import os
from pathlib import Path
from typing import Callable, Iterable

from .recorder import IORecorder


def _is_read_only(mode: str) -> bool:
    return not set(mode) & set("wax+")


def install_fs_read(recorder: IORecorder, roots: Iterable[str | Path]) -> Callable[[], None]:
    """Intercept read-only open() calls for paths under `roots` only."""
    original_open = builtins.open
    resolved = [Path(r).resolve() for r in roots]

    def inside(path: str | os.PathLike) -> bool:
        p = Path(path).resolve()
        return any(p == root or root in p.parents for root in resolved)

    def tracked_open(file, mode="r", *args, **kwargs):
        if (not isinstance(file, (str, os.PathLike))
                or not _is_read_only(mode) or not inside(file)):
            return original_open(file, mode, *args, **kwargs)

        binary = "b" in mode

        def live() -> dict[str, str]:
            with original_open(file, mode, *args, **kwargs) as f:
                data = f.read()
            if binary:
                return {"b64": base64.b64encode(data).decode("ascii")}
            return {"text": data}

        request = {"path": str(Path(file).resolve()), "mode": mode}
        res = recorder.intercept("fs_read", request, live)
        if binary:
            return io.BytesIO(base64.b64decode(res["b64"]))
        return io.StringIO(res["text"])

    builtins.open = tracked_open  # type: ignore[assignment]

    def uninstall() -> None:
        builtins.open = original_open

    return uninstall
"""Config resolver — loads defaults.toml, returns the dict."""

from __future__ import annotations

import tomllib
from functools import cache
from pathlib import Path

_TOML = Path(__file__).with_name("defaults.toml")


@cache
def resolve() -> dict:
    return tomllib.loads(_TOML.read_text())


def paths() -> dict[str, Path]:
    p = resolve()["paths"]
    return {k: Path(v) for k, v in p.items()}

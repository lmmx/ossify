"""Rule protocol shared by all rule modules."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class RepoContext:
    slug: str
    owner: str
    name: str
    packages: tuple[str, ...]
    clone_dir: Path                 # data/repos/<slug>/clone
    commits_path: Path | None       # cache/commits/<slug>.parquet (may not exist)
    pypi_paths: dict[str, Path]     # package_name -> cache/pypi/packages/<pkg>.json


@dataclass(frozen=True)
class RuleResult:
    category: str                   # one of the seven category keys
    fields: dict[str, Any]          # field name(s) on that category model


class Rule(Protocol):
    name: str
    def __call__(self, ctx: RepoContext) -> RuleResult | None: ...
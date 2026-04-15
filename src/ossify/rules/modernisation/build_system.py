from __future__ import annotations
import tomllib
from .._base import RepoContext, RuleResult
from ossify.models.enums import BuildSystem

name = "modernisation.build_system"

_BACKEND_MAP = {
    "uv_build": BuildSystem.uv,
    "hatchling": BuildSystem.hatch,
    "pdm.backend": BuildSystem.pdm,
    "poetry.core.masonry.api": BuildSystem.poetry,
    "setuptools": BuildSystem.setuptools,
    "flit_core": BuildSystem.flit,
}


def rule(ctx: RepoContext) -> RuleResult | None:
    f = ctx.clone_dir / "pyproject.toml"
    if not f.exists():
        return RuleResult("modernisation", {"build_system": BuildSystem.unknown})
    try:
        data = tomllib.loads(f.read_text())
    except tomllib.TOMLDecodeError:
        return RuleResult("modernisation", {"build_system": BuildSystem.unknown})
    backend = ((data.get("build-system") or {}).get("build-backend") or "").lower()
    bs = next((v for k, v in _BACKEND_MAP.items() if k in backend), BuildSystem.unknown)
    return RuleResult("modernisation", {"build_system": bs})

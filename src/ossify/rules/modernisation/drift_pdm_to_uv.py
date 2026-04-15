from __future__ import annotations
import tomllib
from .._base import RepoContext, RuleResult

name = "modernisation.drift_pdm_to_uv"


def rule(ctx: RepoContext) -> RuleResult | None:
    f = ctx.clone_dir / "pyproject.toml"
    if not f.exists():
        return None
    try:
        data = tomllib.loads(f.read_text())
    except tomllib.TOMLDecodeError:
        return None
    backend = ((data.get("build-system") or {}).get("build-backend") or "").lower()
    return RuleResult("modernisation", {"drift_pdm_to_uv": "pdm" in backend})

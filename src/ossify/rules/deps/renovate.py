from __future__ import annotations
from .._base import RepoContext, RuleResult
from ossify.models.enums import DepBot

name = "deps.renovate"


def rule(ctx: RepoContext) -> RuleResult | None:
    cd = ctx.clone_dir
    present = (cd / "renovate.json").exists() or (
        cd / ".github" / "renovate.json"
    ).exists()
    if not present:
        return None
    return RuleResult("deps", {"bots": frozenset({DepBot.renovate})})

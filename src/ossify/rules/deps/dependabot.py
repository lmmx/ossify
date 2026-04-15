from __future__ import annotations
from .._base import RepoContext, RuleResult
from ossify.models.enums import DepBot

name = "deps.dependabot"


def rule(ctx: RepoContext) -> RuleResult | None:
    f = ctx.clone_dir / ".github" / "dependabot.yml"
    if not f.exists():
        return None
    return RuleResult("deps", {"bots": frozenset({DepBot.dependabot})})

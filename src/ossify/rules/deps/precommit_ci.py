from __future__ import annotations
from .._base import RepoContext, RuleResult
from ossify.models.enums import DepBot

name = "deps.precommit_ci"


def rule(ctx: RepoContext) -> RuleResult | None:
    f = ctx.clone_dir / ".pre-commit-config.yaml"
    if not f.exists():
        return None
    text = f.read_text(encoding="utf-8", errors="replace")
    if "ci:" in text or "pre-commit.ci" in text:
        return RuleResult("deps", {"bots": frozenset({DepBot.precommit_ci})})
    return None

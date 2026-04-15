from __future__ import annotations
from .._base import RepoContext, RuleResult

name = "verification.precommit"


def rule(ctx: RepoContext) -> RuleResult | None:
    f = ctx.clone_dir / ".pre-commit-config.yaml"
    return RuleResult("verification", {"precommit_configured": f.exists()})

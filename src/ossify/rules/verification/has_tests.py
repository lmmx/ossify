from __future__ import annotations
from .._base import RepoContext, RuleResult

name = "verification.has_tests"


def rule(ctx: RepoContext) -> RuleResult | None:
    cd = ctx.clone_dir
    if not cd.exists():
        return None
    has = (cd / "tests").is_dir() or any(cd.rglob("test_*.py"))
    return RuleResult("verification", {"has_tests": has})

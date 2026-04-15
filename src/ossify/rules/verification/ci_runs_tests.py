"""Detect GitHub Actions CI and whether it invokes pytest/unittest.

STUB — port the workflow_parser pattern from trusty-pub here.
"""

from __future__ import annotations
from .._base import RepoContext, RuleResult

name = "verification.ci_runs_tests"


def rule(ctx: RepoContext) -> RuleResult | None:
    wf_dir = ctx.clone_dir / ".github" / "workflows"
    if not wf_dir.exists():
        return RuleResult("verification", {"has_ci": False, "ci_runs_tests": False})
    has_ci = any(wf_dir.glob("*.y*ml"))
    runs_tests = False
    for f in wf_dir.glob("*.y*ml"):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "pytest" in text or "unittest" in text or "python -m pytest" in text:
            runs_tests = True
            break
    return RuleResult("verification", {"has_ci": has_ci, "ci_runs_tests": runs_tests})

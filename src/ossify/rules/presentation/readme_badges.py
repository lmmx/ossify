from __future__ import annotations
import re
from .._base import RepoContext, RuleResult

name = "presentation.readme_badges"

_BADGE_RE = re.compile(
    r"!\[[^\]]*\]\(https?://(img\.shields\.io|badge\.fury\.io|github\.com/[^/]+/[^/]+/actions)",
)


def rule(ctx: RepoContext) -> RuleResult | None:
    cd = ctx.clone_dir
    candidate = next(
        (cd / n for n in ("README.md", "README.rst") if (cd / n).exists()),
        None,
    )
    if candidate is None:
        return RuleResult("presentation", {"has_readme": False, "readme_badges": 0})
    text = candidate.read_text(encoding="utf-8", errors="replace")
    return RuleResult(
        "presentation",
        {
            "has_readme": True,
            "readme_badges": len(_BADGE_RE.findall(text)),
        },
    )

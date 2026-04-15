from __future__ import annotations
from .._base import RepoContext, RuleResult

name = "modernisation.drift_token_to_trusted"


def rule(ctx: RepoContext) -> RuleResult | None:
    wf_dir = ctx.clone_dir / ".github" / "workflows"
    if not wf_dir.exists():
        return None
    blob = ""
    for f in wf_dir.glob("*.y*ml"):
        try:
            blob += f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    uses_token = ("PYPI_TOKEN" in blob) or ("TWINE_PASSWORD" in blob)
    uses_trusted = "id-token: write" in blob
    drift = uses_token and not uses_trusted
    return RuleResult("modernisation", {"drift_token_to_trusted": drift})

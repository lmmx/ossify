"""Detect Trusted Publishing — port the rules from trusty-pub here."""

from __future__ import annotations
from .._base import RepoContext, RuleResult
from ossify.models.enums import PublishMode, PublishAuth

name = "release.trusted_publishing"


def rule(ctx: RepoContext) -> RuleResult | None:
    wf_dir = ctx.clone_dir / ".github" / "workflows"
    if not wf_dir.exists():
        return RuleResult(
            "release",
            {
                "publish_mode": PublishMode.unknown,
                "publish_auth": PublishAuth.unknown,
            },
        )
    text_blob = ""
    for f in wf_dir.glob("*.y*ml"):
        try:
            text_blob += f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

    mode = (
        PublishMode.ci
        if ("pypa/gh-action-pypi-publish" in text_blob or "uv publish" in text_blob)
        else PublishMode.unknown
    )
    if "id-token: write" in text_blob:
        auth = PublishAuth.trusted
    elif "PYPI_TOKEN" in text_blob or "TWINE_PASSWORD" in text_blob:
        auth = PublishAuth.token
    else:
        auth = PublishAuth.unknown
    return RuleResult("release", {"publish_mode": mode, "publish_auth": auth})

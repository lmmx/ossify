from __future__ import annotations
import json
from datetime import datetime
from .._base import RepoContext, RuleResult

name = "release.version_count"


def rule(ctx: RepoContext) -> RuleResult | None:
    counts: list[int] = []
    last: datetime | None = None
    for pkg, path in ctx.pypi_paths.items():
        if not path.exists():
            continue
        meta = json.loads(path.read_text())
        releases = meta.get("releases") or {}
        counts.append(sum(1 for v in releases.values() if v))
        # find latest upload time across releases
        for files in releases.values():
            for f in files or []:
                ts = f.get("upload_time_iso_8601") or f.get("upload_time")
                if not ts:
                    continue
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if last is None or dt > last:
                    last = dt
    if not counts:
        return None
    return RuleResult(
        "release",
        {
            "version_count": max(counts),  # if monorepo, use the max
            "last_release_at": last,
        },
    )

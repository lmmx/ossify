"""Build static site: copy assets + emit data.json from repos.parquet."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


from ossify.defaults import resolve, paths
from ossify.models.derived import derive
from ossify.persist import _load_record  # internal, fine for now

_STATIC_SRC = Path(__file__).parent / "static_site"


def build() -> Path:
    p = paths()
    out = p["site_dir"]
    out.mkdir(parents=True, exist_ok=True)

    for f in _STATIC_SRC.iterdir():
        if f.is_file():
            shutil.copy2(f, out / f.name)

    cfg = resolve()["derive"]
    now = datetime.now(timezone.utc)

    rows: list[dict] = []
    for slug_dir in sorted(p["repos_dir"].iterdir()):
        if not (slug_dir / "identity.toml").exists():
            continue
        rec = _load_record(slug_dir)
        if rec is None:
            continue
        ds = derive(
            rec,
            unmaintained_after_days=cfg["unmaintained_after_days"],
            inactive_after_days=cfg["inactive_after_days"],
            now=now,
        )
        rows.append(
            {
                "repo": rec.identity.repo,
                "owner": rec.identity.owner,
                "name": rec.identity.name,
                "packages": list(rec.identity.packages),
                "url": str(rec.identity.url) if rec.identity.url else None,
                "archived": rec.identity.archived,
                "priority": rec.identity.priority,
                "last_commit_at": rec.activity.last_commit_at.isoformat()
                if rec.activity.last_commit_at
                else None,
                "last_human_commit_at": rec.activity.last_human_commit_at.isoformat()
                if rec.activity.last_human_commit_at
                else None,
                "human_ratio_window": rec.activity.human_ratio_window,
                "window_days": rec.activity.window_days,
                "has_tests": rec.verification.has_tests,
                "has_ci": rec.verification.has_ci,
                "ci_runs_tests": rec.verification.ci_runs_tests,
                "ci_passing": rec.verification.ci_passing,
                "precommit_configured": rec.verification.precommit_configured,
                "version_count": rec.release.version_count,
                "last_release_at": rec.release.last_release_at.isoformat()
                if rec.release.last_release_at
                else None,
                "release_cadence_days": rec.release.release_cadence_days,
                "publish_mode": rec.release.publish_mode.value,
                "publish_auth": rec.release.publish_auth.value,
                "bots": sorted(b.value for b in rec.deps.bots),
                "pinning": rec.deps.pinning.value,
                "build_system": rec.modernisation.build_system.value,
                "drift_pdm_to_uv": rec.modernisation.drift_pdm_to_uv,
                "drift_token_to_trusted": rec.modernisation.drift_token_to_trusted,
                "has_readme": rec.presentation.has_readme,
                "readme_badges": rec.presentation.readme_badges,
                "state_ok": ds.ok,
                "state_unmaintained": ds.unmaintained,
                "state_inactive": ds.inactive,
                "state_failing": ds.failing,
            },
        )

    blob = json.dumps(
        {"generated_at": now.isoformat(), "repos": rows},
        separators=(",", ":"),
    )
    (out / "data.json").write_text(blob)
    print(f"✓ {len(rows)} repos → {out / 'data.json'} ({len(blob) // 1024}KB)")
    return out

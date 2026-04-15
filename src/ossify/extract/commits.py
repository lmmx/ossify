"""Fetch commit log via `gh api`, write to cache/commits/<slug>.parquet.

Stub: real implementation should paginate /repos/{owner}/{name}/commits,
extract author/committer email + name + date, store as parquet, then on
re-run only fetch since the latest cached SHA.
"""

from __future__ import annotations

import asyncio
import json
import tomllib
from pathlib import Path

import polars as pl
from tqdm import tqdm

from ossify.defaults import resolve, paths
from ossify.idem import is_fresh


async def _gh_commits(owner: str, name: str, max_commits: int) -> list[dict]:
    proc = await asyncio.create_subprocess_exec(
        "gh",
        "api",
        f"/repos/{owner}/{name}/commits",
        "--paginate",
        "-q",
        ".[] | {sha, author: .commit.author, committer: .commit.committer}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    if proc.returncode != 0:
        return []
    # gh -q with --paginate emits one JSON object per line
    rows = []
    for line in out.decode().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
        if len(rows) >= max_commits:
            break
    return rows


def _flatten(rows: list[dict]) -> pl.DataFrame:
    if not rows:
        return pl.DataFrame(
            schema={
                "sha": pl.Utf8,
                "author_name": pl.Utf8,
                "author_email": pl.Utf8,
                "author_date": pl.Utf8,
                "committer_name": pl.Utf8,
                "committer_email": pl.Utf8,
                "committer_date": pl.Utf8,
            },
        )
    flat = []
    for r in rows:
        a = r.get("author") or {}
        c = r.get("committer") or {}
        flat.append(
            {
                "sha": r.get("sha"),
                "author_name": a.get("name"),
                "author_email": a.get("email"),
                "author_date": a.get("date"),
                "committer_name": c.get("name"),
                "committer_email": c.get("email"),
                "committer_date": c.get("date"),
            },
        )
    return pl.DataFrame(flat)


async def _run() -> dict[str, int]:
    cfg = resolve()["commits"]
    p = paths()
    out_dir = p["cache_dir"] / "commits"
    out_dir.mkdir(parents=True, exist_ok=True)

    repos = []
    for d in sorted(p["repos_dir"].iterdir()):
        f = d / "identity.toml"
        if f.exists():
            rec = tomllib.loads(f.read_text())
            repos.append((rec["repo"], rec["owner"], rec["name"]))

    counts: dict[str, int] = {}
    pbar = tqdm(total=len(repos), desc="Commits", unit="repo")

    for slug, owner, name in repos:
        out = out_dir / f"{slug}.parquet"
        if is_fresh(out, 1):  # 1 day cache
            counts["cached"] = counts.get("cached", 0) + 1
            pbar.update(1)
            continue
        rows = await _gh_commits(owner, name, cfg["max_commits"])
        _flatten(rows).write_parquet(out)
        counts["ok" if rows else "empty"] = counts.get("ok" if rows else "empty", 0) + 1
        pbar.update(1)

    pbar.close()
    return counts


def fetch_all() -> Path:
    counts = asyncio.run(_run())
    print("Commits:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return paths()["cache_dir"] / "commits"

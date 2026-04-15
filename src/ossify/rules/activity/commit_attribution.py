"""Compute human/bot commit counts and last-commit timestamps."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import polars as pl

from ossify.defaults import resolve
from .._base import RepoContext, RuleResult

name = "activity.commit_attribution"


def _is_bot(
    name: str | None, email: str | None, name_pats: list[str], email_pats: list[str]
) -> bool:
    n = (name or "").lower()
    e = (email or "").lower()
    return any(p in n for p in name_pats) or any(p in e for p in email_pats)


def rule(ctx: RepoContext) -> RuleResult | None:
    if ctx.commits_path is None or not ctx.commits_path.exists():
        return None
    df = pl.read_parquet(ctx.commits_path)
    if df.height == 0:
        return RuleResult("activity", {})

    cfg = resolve()["commits"]
    name_pats = [p.lower() for p in cfg["bot_name_patterns"]]
    email_pats = [p.lower() for p in cfg["bot_email_patterns"]]
    window_days = cfg["window_days"]
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

    # GitHub returns ISO-8601 with Z suffix, e.g. 2024-03-15T12:34:56Z.
    # Parse eagerly with explicit format; coerce errors to null.
    df = df.with_columns(
        pl.col("author_date")
        .str.to_datetime(
            format="%Y-%m-%dT%H:%M:%S%#z",
            strict=False,
            time_zone="UTC",
        )
        .alias("dt"),
    ).drop_nulls(subset=["dt"])

    if df.height == 0:
        return RuleResult("activity", {})

    bot_flags = [
        _is_bot(n, e, name_pats, email_pats)
        for n, e in zip(df["author_name"].to_list(), df["author_email"].to_list())
    ]
    df = df.with_columns(pl.Series("is_bot", bot_flags))

    last_commit_at = df["dt"].max()
    last_human = df.filter(~pl.col("is_bot"))["dt"].max()
    last_bot = df.filter(pl.col("is_bot"))["dt"].max()

    in_window = df.filter(pl.col("dt") >= cutoff)
    h = int(in_window.filter(~pl.col("is_bot")).height)
    b = int(in_window.filter(pl.col("is_bot")).height)
    total = h + b
    ratio = (h / total) if total > 0 else None

    return RuleResult(
        "activity",
        {
            "last_commit_at": last_commit_at,
            "last_human_commit_at": last_human,
            "last_bot_commit_at": last_bot,
            "human_commits_window": h,
            "bot_commits_window": b,
            "human_ratio_window": ratio,
            "window_days": window_days,
        },
    )

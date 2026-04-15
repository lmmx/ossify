"""Non-exclusive state flags computed from a RepoRecord."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from .record import RepoRecord


@dataclass(frozen=True)
class DerivedState:
    ok: bool
    unmaintained: bool
    inactive: bool
    failing: bool
    archived: bool
    since_last_commit: timedelta | None
    since_last_human_commit: timedelta | None


def _age(dt: datetime | None, now: datetime) -> timedelta | None:
    return None if dt is None else now - dt


def derive(
    rec: RepoRecord,
    *,
    unmaintained_after_days: int,
    inactive_after_days: int,
    now: datetime | None = None,
) -> DerivedState:
    now = now or datetime.now(timezone.utc)
    since_commit = _age(rec.activity.last_commit_at, now)
    since_human = _age(rec.activity.last_human_commit_at, now)

    inactive = since_commit is not None and since_commit.days >= inactive_after_days
    unmaintained = (
        not inactive
        and since_human is not None
        and since_human.days >= unmaintained_after_days
    )
    failing = rec.verification.ci_passing is False
    archived = rec.identity.archived
    ok = not (inactive or unmaintained or failing or archived)

    return DerivedState(
        ok=ok,
        unmaintained=unmaintained,
        inactive=inactive,
        failing=failing,
        archived=archived,
        since_last_commit=since_commit,
        since_last_human_commit=since_human,
    )

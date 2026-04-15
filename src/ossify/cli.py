"""Run all stages in order. Each stage is independently idempotent."""

from __future__ import annotations

from ossify.extract.pypi_user import discover
from ossify.extract.pypi_json import fetch_all as fetch_pypi
from ossify.extract.repos import derive
from ossify.extract.clone import clone_all
from ossify.extract.commits import fetch_all as fetch_commits
from ossify.compose import classify_all
from ossify.persist import build_parquet
from ossify.site.build import build as build_site


STAGES = [
    ("discover", discover),
    ("pypi-json", fetch_pypi),
    ("repos", derive),
    ("clone", clone_all),
    ("commits", fetch_commits),
    ("classify", classify_all),
    ("parquet", build_parquet),
    ("site", build_site),
]


def run_all() -> None:
    for name, fn in STAGES:
        print(f"\n── {name} ──")
        fn()

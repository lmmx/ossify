"""Run all stages in order, or a single stage. Each stage is idempotent."""

from __future__ import annotations

import argparse
import sys
import time

from ossify.extract.pypi_user import discover
from ossify.extract.pypi_json import fetch_all as fetch_pypi
from ossify.extract.repos import derive
from ossify.extract.commits import fetch_all as fetch_commits
from ossify.compose import classify_all
from ossify.persist import build_parquet
from ossify.site.build import build as build_site


STAGES = {
    "discover": ("Scrape PyPI user page → package names", discover),
    "pypi-json": ("Fetch /pypi/{pkg}/json for each package", fetch_pypi),
    "repos": ("Derive repo set from PyPI metadata", derive),
    "commits": ("Fetch commit logs via gh api", fetch_commits),
    "classify": ("Sparse-clone, run rules, delete clone", classify_all),
    "parquet": ("Compose TOMLs → data/repos.parquet", build_parquet),
    "site": ("Build static site from parquet", build_site),
}


def _run_stage(key: str) -> None:
    desc, fn = STAGES[key]
    print(f"\n── {key} ──  {desc}", flush=True)
    t0 = time.monotonic()
    try:
        fn()
    except KeyboardInterrupt:
        print(f"\n  ✗ {key} interrupted by user", flush=True)
        raise
    except Exception as exc:
        print(f"  ✗ {key} failed: {exc.__class__.__name__}: {exc}", flush=True)
        raise
    print(f"  ✓ {key} done in {time.monotonic() - t0:.1f}s", flush=True)


def run_all() -> None:
    parser = argparse.ArgumentParser(
        prog="ossify",
        description="Open Source Software Intelligence For You.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Stages:\n"
        + "\n".join(f"  {k:10s} {desc}" for k, (desc, _) in STAGES.items()),
    )
    parser.add_argument("--only", choices=list(STAGES), action="append")
    parser.add_argument("--from", dest="start", choices=list(STAGES))
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for k, (desc, _) in STAGES.items():
            print(f"  {k:10s} {desc}")
        return

    keys = list(STAGES)
    if args.only:
        keys = [k for k in keys if k in args.only]
    elif args.start:
        keys = keys[keys.index(args.start) :]

    print(f"ossify: running {len(keys)} stage(s): {', '.join(keys)}", flush=True)
    try:
        for k in keys:
            _run_stage(k)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        sys.exit(1)

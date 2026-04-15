"""Run rules against each repo, write per-category TOML files.

Per repo: sparse-clone into a tempdir, run all rules against it, write
TOMLs, delete the tempdir. Nothing about the clone persists on disk.
A `.extracted` sentinel records when extraction last completed, so
re-runs skip repos that haven't changed (delete the sentinel to force).
"""

from __future__ import annotations

import asyncio
import tempfile
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import tomli_w
from tqdm import tqdm

from ossify.defaults import resolve, paths
from ossify.extract.clone import sparse_clone
from ossify.idem import atomic_write_text
from ossify.models import CATEGORY_MODELS, Identity
from ossify.rules import ALL_RULES
from ossify.rules._base import RepoContext

_SENTINEL = ".extracted"


def _load_identity(slug_dir: Path) -> Identity:
    rec = tomllib.loads((slug_dir / "identity.toml").read_text())
    rec["packages"] = tuple(rec.get("packages") or ())
    rec["description"] = rec.get("description") or None
    rec["url"] = rec.get("url") or None
    return Identity(**rec)


def _is_fresh(slug_dir: Path, max_age_days: float) -> bool:
    s = slug_dir / _SENTINEL
    if not s.exists():
        return False
    return (time.time() - s.stat().st_mtime) < max_age_days * 86400


def _stamp(slug_dir: Path) -> None:
    (slug_dir / _SENTINEL).write_text(
        datetime.now(timezone.utc).isoformat() + "\n",
        encoding="utf-8",
    )


def _build_context(ident: Identity, clone_dir: Path) -> RepoContext:
    p = paths()
    pypi_dir = p["cache_dir"] / "pypi" / "packages"
    pypi_paths = {pkg: pypi_dir / f"{pkg}.json" for pkg in ident.packages}
    commits_path = p["cache_dir"] / "commits" / f"{ident.repo}.parquet"
    return RepoContext(
        slug=ident.repo,
        owner=ident.owner,
        name=ident.name,
        packages=ident.packages,
        clone_dir=clone_dir,
        commits_path=commits_path if commits_path.exists() else None,
        pypi_paths=pypi_paths,
    )


def _merge(
    into: dict[str, dict[str, Any]],
    category: str,
    fields: dict[str, Any],
) -> None:
    bucket = into.setdefault(category, {})
    for k, v in fields.items():
        if isinstance(v, frozenset) and isinstance(bucket.get(k), frozenset):
            bucket[k] = bucket[k] | v
        else:
            bucket[k] = v


def _toml_safe(v: Any) -> Any:
    if isinstance(v, frozenset):
        return sorted(str(x) for x in v)
    if hasattr(v, "value"):
        return v.value
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return v


def _dump_category(payload: dict[str, Any]) -> str:
    return tomli_w.dumps(
        {k: _toml_safe(v) for k, v in payload.items() if v is not None},
    )


def _run_rules(ctx: RepoContext, slug: str) -> dict[str, dict[str, Any]]:
    accum: dict[str, dict[str, Any]] = {}
    for rule in ALL_RULES:
        try:
            result = rule(ctx)
        except Exception as exc:
            tqdm.write(
                f"  rule {getattr(rule, '__module__', rule)} failed on {slug}: {exc}",
            )
            continue
        if result is None:
            continue
        _merge(accum, result.category, result.fields)
    return accum


async def _process_repo(
    ident: Identity,
    slug_dir: Path,
    force: bool,
    sem: asyncio.Semaphore,
) -> str:
    if not force and _is_fresh(slug_dir, max_age_days=7):
        return "cached"

    async with sem:
        with tempfile.TemporaryDirectory(prefix=f"ossify-{ident.repo}-") as tmp:
            clone_dir = Path(tmp)
            ok, tag = await sparse_clone(ident.owner, ident.name, clone_dir)
            if not ok:
                return tag

            ctx = _build_context(ident, clone_dir)
            accum = _run_rules(ctx, ident.repo)

    # Tempdir is gone here — nothing more should touch the clone.
    for category, payload in accum.items():
        instance = CATEGORY_MODELS[category](**payload)
        atomic_write_text(
            slug_dir / f"{category}.toml",
            _dump_category(instance.model_dump(mode="python")),
        )
    _stamp(slug_dir)
    return "ok"


async def _run(force: bool) -> dict[str, int]:
    p = paths()
    repos_dir = p["repos_dir"]
    slugs = [
        d
        for d in sorted(repos_dir.iterdir())
        if not d.name.startswith(".") and (d / "identity.toml").exists()
    ]
    if not slugs:
        raise FileNotFoundError(f"No repos under {repos_dir} — run `ossify-repos`")

    cfg = resolve()["clone"]
    sem = asyncio.Semaphore(cfg["concurrency"])
    counts: dict[str, int] = {}
    failures: list[tuple[str, str]] = []
    pbar = tqdm(total=len(slugs), desc="Classifying", unit="repo")

    async def go(slug_dir: Path) -> None:
        ident = _load_identity(slug_dir)
        res = await _process_repo(ident, slug_dir, force, sem)
        counts[res] = counts.get(res, 0) + 1
        if res not in ("ok", "cached"):
            failures.append((ident.repo, res))
        pbar.update(1)

    await asyncio.gather(*(go(s) for s in slugs))
    pbar.close()

    if failures:
        print("  failures:", flush=True)
        for slug, why in failures[:20]:
            print(f"    {slug:40s} {why}", flush=True)
        if len(failures) > 20:
            print(f"    … and {len(failures) - 20} more", flush=True)

    return counts


def classify_all() -> Path:
    """Re-extract any repo whose .extracted sentinel is missing or >7d old."""
    counts = asyncio.run(_run(force=False))
    print(
        "  Classify:",
        ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        flush=True,
    )
    return paths()["repos_dir"]

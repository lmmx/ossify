"""Compose per-category TOMLs into RepoRecord; write data/repos.parquet."""
from __future__ import annotations

import tomllib
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import polars as pl

from ossify.defaults import paths
from ossify.models import (
    CATEGORY_MODELS, RepoRecord,
)


def _load_category(slug_dir: Path, category: str):
    f = slug_dir / f"{category}.toml"
    cls = CATEGORY_MODELS[category]
    if not f.exists():
        return cls() if category != "identity" else None
    data = tomllib.loads(f.read_text())
    if category == "identity":
        data["packages"] = tuple(data.get("packages") or ())
        data["description"] = data.get("description") or None
        data["url"] = data.get("url") or None
    if category == "deps":
        data["bots"] = frozenset(data.get("bots") or ())
    return cls(**data)


def _load_record(slug_dir: Path) -> RepoRecord | None:
    ident = _load_category(slug_dir, "identity")
    if ident is None:
        return None
    return RepoRecord(
        identity=ident,
        activity=_load_category(slug_dir, "activity"),
        verification=_load_category(slug_dir, "verification"),
        release=_load_category(slug_dir, "release"),
        deps=_load_category(slug_dir, "deps"),
        modernisation=_load_category(slug_dir, "modernisation"),
        presentation=_load_category(slug_dir, "presentation"),
    )


def _scalar(v: Any) -> Any:
    """Coerce a value into something Polars can store natively."""
    if v is None:
        return None
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, (set, frozenset)):
        return sorted(_scalar(x) for x in v)
    if isinstance(v, tuple):
        return [_scalar(x) for x in v]
    if isinstance(v, list):
        return [_scalar(x) for x in v]
    if isinstance(v, datetime):
        return v
    # Pydantic HttpUrl, Path, etc — stringify.
    if not isinstance(v, (str, int, float, bool, bytes)):
        return str(v)
    return v


def _flatten(rec: RepoRecord) -> dict[str, Any]:
    """Flatten a RepoRecord to a single row for parquet."""
    d: dict[str, Any] = {}
    for cat_key in ("identity", "activity", "verification", "release",
                    "deps", "modernisation", "presentation"):
        cat = getattr(rec, cat_key)
        for fname, fval in cat.model_dump(mode="python").items():
            d[f"{cat_key}.{fname}"] = _scalar(fval)
    return d


def build_parquet() -> Path:
    p = paths()
    slugs = [d for d in sorted(p["repos_dir"].iterdir()) if (d / "identity.toml").exists()]
    rows = []
    for slug_dir in slugs:
        rec = _load_record(slug_dir)
        if rec is None:
            continue
        rows.append(_flatten(rec))
    if not rows:
        raise RuntimeError("No records to persist")

    df = pl.DataFrame(rows)
    out = p["parquet_path"]
    out.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out)
    print(f"  wrote {df.height} records → {out}", flush=True)
    return out
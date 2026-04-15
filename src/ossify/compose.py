"""Run rules against each repo, write per-category TOML files."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from ossify.defaults import paths
from ossify.idem import atomic_write_text
from ossify.models import (
    CATEGORY_MODELS,
    Identity,
)
from ossify.rules import ALL_RULES
from ossify.rules._base import RepoContext


def _load_identity(slug_dir: Path) -> Identity:
    rec = tomllib.loads((slug_dir / "identity.toml").read_text())
    rec["packages"] = tuple(rec.get("packages") or ())
    rec["description"] = rec.get("description") or None
    rec["url"] = rec.get("url") or None
    return Identity(**rec)


def _build_context(slug_dir: Path, ident: Identity) -> RepoContext:
    p = paths()
    pypi_dir = p["cache_dir"] / "pypi" / "packages"
    pypi_paths = {pkg: pypi_dir / f"{pkg}.json" for pkg in ident.packages}
    commits_path = p["cache_dir"] / "commits" / f"{ident.repo}.parquet"
    return RepoContext(
        slug=ident.repo,
        owner=ident.owner,
        name=ident.name,
        packages=ident.packages,
        clone_dir=slug_dir / "clone",
        commits_path=commits_path if commits_path.exists() else None,
        pypi_paths=pypi_paths,
    )


def _merge(
    into: dict[str, dict[str, Any]],
    category: str,
    fields: dict[str, Any],
) -> None:
    """Merge rule output into the per-category accumulator.

    For frozenset fields (e.g. deps.bots), union; otherwise overwrite.
    """
    bucket = into.setdefault(category, {})
    for k, v in fields.items():
        if isinstance(v, frozenset) and isinstance(bucket.get(k), frozenset):
            bucket[k] = bucket[k] | v
        else:
            bucket[k] = v


def _toml_safe(v: Any) -> Any:
    if isinstance(v, frozenset):
        return sorted(str(x) for x in v)
    if hasattr(v, "value"):  # StrEnum
        return v.value
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return v


def _dump_category(payload: dict[str, Any]) -> str:
    out = {k: _toml_safe(v) for k, v in payload.items() if v is not None}
    return tomli_w.dumps(out)


def classify_all() -> Path:
    p = paths()
    repos_dir = p["repos_dir"]
    slugs = [d for d in sorted(repos_dir.iterdir()) if (d / "identity.toml").exists()]
    if not slugs:
        raise FileNotFoundError(f"No repos under {repos_dir} — run `ossify-repos`")

    for slug_dir in slugs:
        ident = _load_identity(slug_dir)
        ctx = _build_context(slug_dir, ident)

        accum: dict[str, dict[str, Any]] = {}
        for rule in ALL_RULES:
            try:
                result = rule(ctx)
            except Exception as exc:
                print(
                    f"  rule {getattr(rule, '__module__', rule)} failed on {ident.repo}: {exc}",
                )
                continue
            if result is None:
                continue
            _merge(accum, result.category, result.fields)

        # Validate via Pydantic, then dump to TOML
        for category, payload in accum.items():
            model_cls = CATEGORY_MODELS[category]
            instance = model_cls(**payload)  # raises on contract drift
            atomic_write_text(
                slug_dir / f"{category}.toml",
                _dump_category(instance.model_dump(mode="python")),
            )

    print(f"Classified {len(slugs)} repos")
    return repos_dir

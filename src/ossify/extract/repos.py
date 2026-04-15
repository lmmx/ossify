"""Derive repo set from cached PyPI JSON; write identity.toml per repo."""

from __future__ import annotations

import json
import re
from pathlib import Path

import tomli_w

from ossify.defaults import paths
from ossify.idem import atomic_write_text
from ossify.models import Identity

_GH_RE = re.compile(r"https?://github\.com/([^/\s,#]+)/([^/\s,#]+)")


def _normalise_url(u: str) -> tuple[str, str] | None:
    m = _GH_RE.search(u or "")
    if not m:
        return None
    owner, name = m.group(1), m.group(2)
    name = re.sub(r"\.git$", "", name).rstrip("/")
    return owner, name


def _extract_repo(meta: dict) -> tuple[str, str] | None:
    info = meta.get("info") or {}
    project_urls = info.get("project_urls") or {}
    candidates: list[str] = []
    for v in project_urls.values():
        if isinstance(v, str):
            candidates.append(v)
    if isinstance(info.get("home_page"), str):
        candidates.append(info["home_page"])
    for c in candidates:
        r = _normalise_url(c)
        if r:
            return r
    return None


def _slug(owner: str, name: str) -> str:
    return f"{owner}__{name}"


def derive() -> Path:
    p = paths()
    pkg_dir = p["cache_dir"] / "pypi" / "packages"
    if not pkg_dir.exists():
        raise FileNotFoundError(f"{pkg_dir} — run `ossify-pypi` first")

    repos_dir = p["repos_dir"]
    pkgs_dir = p["packages_dir"]
    repos_dir.mkdir(parents=True, exist_ok=True)
    pkgs_dir.mkdir(parents=True, exist_ok=True)

    # repo slug -> { owner, name, packages, description, url, archived }
    repos: dict[str, dict] = {}
    orphans: list[str] = []

    for f in sorted(pkg_dir.glob("*.json")):
        name = f.stem
        try:
            meta = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        rr = _extract_repo(meta)
        if rr is None:
            orphans.append(name)
            continue
        owner, repo_name = rr
        slug = _slug(owner, repo_name)
        rec = repos.setdefault(
            slug,
            {
                "owner": owner,
                "name": repo_name,
                "packages": [],
                "description": (meta.get("info") or {}).get("summary"),
                "url": f"https://github.com/{owner}/{repo_name}",
            },
        )
        if name not in rec["packages"]:
            rec["packages"].append(name)

    # write identity.toml per repo, plus package symlinks
    for slug, rec in repos.items():
        rec["packages"].sort()
        identity = Identity(
            repo=slug,
            owner=rec["owner"],
            name=rec["name"],
            packages=tuple(rec["packages"]),
            description=rec["description"],
            url=rec["url"],
        )
        out = repos_dir / slug / "identity.toml"
        atomic_write_text(out, tomli_w.dumps(_dump_identity(identity)))

        for pkg in rec["packages"]:
            link = pkgs_dir / pkg
            target = Path("..") / "repos" / slug
            if link.is_symlink() or link.exists():
                link.unlink()
            link.symlink_to(target)

    print(
        f"{len(repos)} repos, {sum(len(r['packages']) for r in repos.values())} packages",
    )
    if orphans:
        print(
            f"  {len(orphans)} packages with no GitHub URL: {', '.join(orphans[:5])}…",
        )
    return repos_dir


def _dump_identity(i: Identity) -> dict:
    """Identity → plain dict for tomli_w (HttpUrl → str, tuple → list)."""
    return {
        "repo": i.repo,
        "owner": i.owner,
        "name": i.name,
        "packages": list(i.packages),
        "archived": i.archived,
        "priority": i.priority,
        "description": i.description or "",
        "url": str(i.url) if i.url else "",
    }

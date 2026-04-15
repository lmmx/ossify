"""Derive repo set from cached PyPI JSON; write identity.toml per repo.

Resolution strategy per package:
  1. Extract any GitHub URL from PyPI metadata (project_urls / home_page).
  2. If the extracted URL's owner == your github_username → accept.
  3. Otherwise (wrong owner OR none extracted) → check whether
     github.com/{your_username}/{name-variant} exists. If so, prefer it.
     This catches wrapper packages whose project_urls point at the
     upstream library, and packages whose authors didn't fill in URLs.
  4. Last resort: keep the extracted URL even if owner-mismatched.
  5. If still nothing → unresolved.

Existence checks use `gh api /repos/{owner}/{name}` (uses your auth,
5000 calls/hr, well within budget for ~70 packages).

User-set flags on existing identity.toml files (priority, archived)
are preserved across re-runs. Stale repo dirs (slugs no longer in
the resolution) are moved to data/repos/.stale/ rather than deleted.
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import tomllib
from pathlib import Path

import tomli_w
from tqdm import tqdm

from ossify.defaults import paths, resolve
from ossify.idem import atomic_write_text
from ossify.models import Identity

_GH_RE = re.compile(r"https?://github\.com/([^/\s,#]+)/([^/\s,#]+)")


# ── URL extraction ─────────────────────────────────────────────────────


def _normalise_url(u: str) -> tuple[str, str] | None:
    m = _GH_RE.search(u or "")
    if not m:
        return None
    owner, name = m.group(1), m.group(2)
    name = re.sub(r"\.git$", "", name).rstrip("/")
    return owner, name


def _extract_repo_from_meta(meta: dict) -> tuple[str, str] | None:
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


# ── Fallback: try lmmx/{name-variants} ─────────────────────────────────


def _name_variants(name: str) -> list[str]:
    """Generate name variants to try under github.com/{user}/."""
    cands = [name]
    for sfx in ("-py", "_py"):
        if name.endswith(sfx):
            cands.append(name[: -len(sfx)])
    extras = []
    for c in cands:
        extras.append(c.replace("-", "_"))
        extras.append(c.replace("_", "-"))
    cands.extend(extras)
    seen: list[str] = []
    for c in cands:
        if c not in seen:
            seen.append(c)
    return seen


async def _gh_repo_exists(owner: str, name: str) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "gh",
        "api",
        f"/repos/{owner}/{name}",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    rc = await proc.wait()
    return rc == 0


async def _find_user_repo(username: str, package_name: str) -> tuple[str, str] | None:
    for variant in _name_variants(package_name):
        if await _gh_repo_exists(username, variant):
            return username, variant
    return None


# ── Resolution ─────────────────────────────────────────────────────────


async def _resolve_one(
    pkg_name: str,
    meta: dict,
    github_username: str,
) -> tuple[tuple[str, str] | None, str]:
    """Return ((owner, name) or None, source_tag).

    Tags:
      pypi                    — extracted URL, self-owned, verified to exist
      fallback                — no URL extracted, found self-owned repo
      fallback_overrode       — extracted URL was upstream wrapper, found self-owned
      fallback_stale_metadata — extracted URL was self-owned but DEAD; found at name
      pypi_upstream           — kept upstream URL (no self-owned alternative)
      unresolved              — nothing found
    """
    extracted = _extract_repo_from_meta(meta)
    user = github_username.lower()
    extracted_is_self = extracted is not None and extracted[0].lower() == user

    # If extracted is self-owned, verify it actually exists.
    if extracted_is_self:
        if await _gh_repo_exists(*extracted):
            return extracted, "pypi"
        # Dead URL — fall through to fallback.

    # Try to find a self-owned repo matching the package name.
    fallback = await _find_user_repo(github_username, pkg_name)
    if fallback:
        if extracted is None:
            return fallback, "fallback"
        if extracted_is_self:
            return fallback, "fallback_stale_metadata"
        return fallback, "fallback_overrode"

    # No self-owned alternative. Keep upstream URL if it verifies.
    if extracted and not extracted_is_self:
        if await _gh_repo_exists(*extracted):
            return extracted, "pypi_upstream"

    return None, "unresolved"


async def _resolve_all(
    pkg_metas: list[tuple[str, dict]],
    github_username: str,
) -> dict[str, tuple[tuple[str, str] | None, str]]:
    sem = asyncio.Semaphore(8)
    results: dict[str, tuple[tuple[str, str] | None, str]] = {}
    pbar = tqdm(total=len(pkg_metas), desc="Resolving", unit="pkg")

    async def go(pkg_name: str, meta: dict) -> None:
        async with sem:
            results[pkg_name] = await _resolve_one(pkg_name, meta, github_username)
        pbar.update(1)

    await asyncio.gather(*(go(n, m) for n, m in pkg_metas))
    pbar.close()
    return results


# ── Preservation of user-set flags + stale cleanup ─────────────────────


def _read_existing_flags(repos_dir: Path) -> dict[str, dict]:
    flags: dict[str, dict] = {}
    if not repos_dir.exists():
        return flags
    for d in repos_dir.iterdir():
        f = d / "identity.toml"
        if not f.exists():
            continue
        try:
            data = tomllib.loads(f.read_text())
        except tomllib.TOMLDecodeError:
            continue
        flags[d.name] = {
            "priority": bool(data.get("priority", False)),
            "archived": bool(data.get("archived", False)),
        }
    return flags


def _cleanup_stale(repos_dir: Path, current_slugs: set[str]) -> list[str]:
    """Move repo dirs not in the new resolution to repos/.stale/."""
    if not repos_dir.exists():
        return []
    stale_dir = repos_dir / ".stale"
    stale: list[str] = []
    for d in sorted(repos_dir.iterdir()):
        if d.name.startswith(".") or d.name in current_slugs:
            continue
        if not (d / "identity.toml").exists():
            continue
        stale_dir.mkdir(exist_ok=True)
        target = stale_dir / d.name
        if target.exists():
            shutil.rmtree(target)
        d.rename(target)
        stale.append(d.name)
    return stale


# ── Main entrypoint ────────────────────────────────────────────────────


def _slug(owner: str, name: str) -> str:
    return f"{owner}__{name}"


def _dump_identity(i: Identity) -> dict:
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


def _write_resolution_log(
    log_path: Path,
    resolutions: dict[str, tuple[tuple[str, str] | None, str]],
    pkg_metas: list[tuple[str, dict]],
) -> None:
    """Per-package transparency: what we extracted, what we resolved to, why."""
    meta_by_name = dict(pkg_metas)
    sections: dict[str, dict] = {}
    for pkg_name, (rr, src) in resolutions.items():
        meta = meta_by_name.get(pkg_name, {})
        extracted = _extract_repo_from_meta(meta)
        sections[pkg_name] = {
            "source": src,
            "extracted": f"{extracted[0]}/{extracted[1]}" if extracted else "",
            "resolved": f"{rr[0]}/{rr[1]}" if rr else "",
        }
    atomic_write_text(log_path, tomli_w.dumps(sections))


def derive() -> Path:
    cfg = resolve()
    p = paths()
    pkg_dir = p["cache_dir"] / "pypi" / "packages"
    if not pkg_dir.exists():
        raise FileNotFoundError(f"{pkg_dir} — run `ossify-pypi` first")

    repos_dir = p["repos_dir"]
    pkgs_dir = p["packages_dir"]
    repos_dir.mkdir(parents=True, exist_ok=True)
    pkgs_dir.mkdir(parents=True, exist_ok=True)

    github_username = cfg["user"]["github_username"]
    existing_flags = _read_existing_flags(repos_dir)

    # Load all PyPI metadata
    pkg_metas: list[tuple[str, dict]] = []
    for f in sorted(pkg_dir.glob("*.json")):
        try:
            pkg_metas.append((f.stem, json.loads(f.read_text())))
        except json.JSONDecodeError:
            print(f"  skipping malformed {f.name}", flush=True)

    # Resolve every package
    resolutions = asyncio.run(_resolve_all(pkg_metas, github_username))

    # Group into repos
    repos: dict[str, dict] = {}
    sources: dict[str, list[str]] = {
        "pypi": [],
        "fallback": [],
        "fallback_overrode": [],
        "fallback_stale_metadata": [],
        "pypi_upstream": [],
        "unresolved": [],
    }

    for pkg_name, meta in pkg_metas:
        rr, src = resolutions[pkg_name]
        sources[src].append(pkg_name)
        if rr is None:
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
        if pkg_name not in rec["packages"]:
            rec["packages"].append(pkg_name)

    # Move stale repo dirs out of the way
    stale = _cleanup_stale(repos_dir, set(repos.keys()))

    # Write identity.toml + symlinks (preserving user-set flags)
    for slug, rec in repos.items():
        rec["packages"].sort()
        flags = existing_flags.get(slug, {})
        identity = Identity(
            repo=slug,
            owner=rec["owner"],
            name=rec["name"],
            packages=tuple(rec["packages"]),
            description=rec["description"],
            url=rec["url"],
            archived=flags.get("archived", False),
            priority=flags.get("priority", False),
        )
        atomic_write_text(
            repos_dir / slug / "identity.toml",
            tomli_w.dumps(_dump_identity(identity)),
        )
        for pkg in rec["packages"]:
            link = pkgs_dir / pkg
            target = Path("..") / "repos" / slug
            if link.is_symlink() or link.exists():
                link.unlink()
            link.symlink_to(target)

    # Resolution log
    _write_resolution_log(p["cache_dir"] / "resolution.toml", resolutions, pkg_metas)

    # Report
    total_pkgs = sum(len(r["packages"]) for r in repos.values())
    print(f"  {len(repos)} repos, {total_pkgs} packages", flush=True)
    order = (
        "pypi",
        "fallback",
        "fallback_overrode",
        "fallback_stale_metadata",
        "pypi_upstream",
        "unresolved",
    )
    for src in order:
        names = sources[src]
        if not names:
            continue
        sample = ", ".join(names[:5])
        more = f" (+{len(names)-5} more)" if len(names) > 5 else ""
        print(f"    {src:24s} {len(names):3d}  {sample}{more}", flush=True)

    # Loud warning for stale PyPI metadata — these need a fix at the source
    stale_meta = sources["fallback_stale_metadata"]
    if stale_meta:
        print(
            f"\n  ⚠ {len(stale_meta)} package(s) have stale GitHub URLs in PyPI metadata.",
            flush=True,
        )
        print(
            f"    Update project_urls in each package's pyproject.toml and re-publish:",
            flush=True,
        )
        for pkg_name in stale_meta:
            rr, _ = resolutions[pkg_name]
            extracted = _extract_repo_from_meta(dict(pkg_metas)[pkg_name])
            ext_str = f"{extracted[0]}/{extracted[1]}" if extracted else "<none>"
            res_str = f"{rr[0]}/{rr[1]}" if rr else "<none>"
            print(
                f"      {pkg_name:30s} metadata says {ext_str} → actually {res_str}",
                flush=True,
            )
        print(flush=True)

    if stale:
        print(
            f"  moved {len(stale)} stale repo dir(s) → {repos_dir / '.stale'}: {', '.join(stale[:5])}",
            flush=True,
        )
    print(f"  resolution log → {p['cache_dir'] / 'resolution.toml'}", flush=True)

    return repos_dir

"""Sparse clone each repo into data/repos/<slug>/clone/."""

from __future__ import annotations

import asyncio
import shutil
import tomllib
from pathlib import Path

from tqdm import tqdm

from ossify.defaults import resolve, paths


def _identity_repos() -> list[tuple[str, str, str]]:
    """Return [(slug, owner, name), ...] from data/repos/*/identity.toml."""
    out = []
    for d in sorted(paths()["repos_dir"].iterdir()):
        f = d / "identity.toml"
        if not f.exists():
            continue
        rec = tomllib.loads(f.read_text())
        out.append((rec["repo"], rec["owner"], rec["name"]))
    return out


async def _sparse_clone(
    owner: str,
    name: str,
    dest: Path,
    sparse_paths: list[str],
    timeout: float,
) -> str:
    if (dest / ".cloned").exists():
        return "cached"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    url = f"https://github.com/{owner}/{name}.git"
    try:
        # init + sparse-checkout cone mode + fetch depth 1
        cmds = [
            ["git", "init", "-q"],
            ["git", "remote", "add", "origin", url],
            ["git", "config", "core.sparseCheckout", "true"],
            ["git", "sparse-checkout", "init", "--cone"],
            ["git", "sparse-checkout", "set", *sparse_paths],
            ["git", "fetch", "--depth=1", "-q", "origin", "HEAD"],
            ["git", "checkout", "-q", "FETCH_HEAD"],
        ]
        for cmd in cmds:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=dest,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                _, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                return "timeout"
            if proc.returncode != 0:
                return f"git fail: {err.decode(errors='replace')[:80]}"
        # Drop .git to keep cache slim
        shutil.rmtree(dest / ".git", ignore_errors=True)
        (dest / ".cloned").touch()
        return "ok"
    except Exception as exc:
        return f"err {exc.__class__.__name__}"


async def _run(repos: list[tuple[str, str, str]]) -> dict[str, int]:
    cfg = resolve()["clone"]
    p = paths()
    sem = asyncio.Semaphore(cfg["concurrency"])
    counts: dict[str, int] = {}
    pbar = tqdm(total=len(repos), desc="Cloning", unit="repo")

    async def go(slug: str, owner: str, name: str) -> None:
        async with sem:
            dest = p["repos_dir"] / slug / "clone"
            res = await _sparse_clone(
                owner,
                name,
                dest,
                cfg["paths"],
                cfg["timeout_seconds"],
            )
        counts[res] = counts.get(res, 0) + 1
        pbar.update(1)

    await asyncio.gather(*(go(s, o, n) for s, o, n in repos))
    pbar.close()
    return counts


def clone_all() -> Path:
    repos = _identity_repos()
    if not repos:
        raise FileNotFoundError("No identity.toml files — run `ossify-repos` first")
    counts = asyncio.run(_run(repos))
    print("Clone:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return paths()["repos_dir"]

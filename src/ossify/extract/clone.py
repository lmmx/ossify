"""Sparse clone each repo into data/repos/<slug>/clone/."""

from __future__ import annotations

import asyncio
import os
import shutil
import tomllib
from pathlib import Path

from tqdm import tqdm

from ossify.defaults import paths, resolve

# Force git to fail fast instead of prompting for credentials on stdin,
# AND make `gh` the credential helper so authenticated repos work.
_GIT_ENV = {
    **os.environ,
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_ASKPASS": "/bin/echo",
    "SSH_ASKPASS": "/bin/echo",
    "GCM_INTERACTIVE": "Never",
    # Use gh as credential helper for github.com.
    # This is additive — it doesn't override any helpers the user already has set.
    "GIT_CONFIG_COUNT": "1",
    "GIT_CONFIG_KEY_0": "credential.https://github.com.helper",
    "GIT_CONFIG_VALUE_0": "!gh auth git-credential",
}


def _identity_repos() -> list[tuple[str, str, str]]:
    out = []
    for d in sorted(paths()["repos_dir"].iterdir()):
        f = d / "identity.toml"
        if not f.exists():
            continue
        rec = tomllib.loads(f.read_text())
        out.append((rec["repo"], rec["owner"], rec["name"]))
    return out


async def _run_git(cmd: list[str], cwd: Path, timeout: float) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.DEVNULL,  # belt + braces: no stdin to read from
        env=_GIT_ENV,
    )
    try:
        _, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        try:
            await proc.communicate()
        except Exception:
            pass
        return -1, "timeout"
    return proc.returncode, err.decode(errors="replace")


async def _sparse_clone(
    owner: str,
    name: str,
    dest: Path,
    sparse_paths: list[str],
    timeout: float,
) -> str:
    sentinel = dest / ".cloned"
    if sentinel.exists():
        return "cached"

    # Wipe any half-finished previous attempt.
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    url = f"https://github.com/{owner}/{name}.git"
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
        rc, err = await _run_git(cmd, dest, timeout)
        if rc != 0:
            # Common failure modes we want to label clearly.
            low = err.lower()
            if rc == -1:
                tag = "timeout"
            elif (
                "could not read" in low
                or "authentication" in low
                or "terminal prompts disabled" in low
            ):
                tag = "no-access"  # private, deleted, or renamed
            elif "repository not found" in low or "not found" in low:
                tag = "not-found"
            else:
                tag = f"git-fail-{rc}"
            # Leave dest empty (no sentinel) so next run retries cleanly.
            shutil.rmtree(dest, ignore_errors=True)
            return tag

    shutil.rmtree(dest / ".git", ignore_errors=True)
    sentinel.touch()
    return "ok"


async def _run(repos: list[tuple[str, str, str]]) -> dict[str, int]:
    cfg = resolve()["clone"]
    p = paths()
    sem = asyncio.Semaphore(cfg["concurrency"])
    counts: dict[str, int] = {}
    failures: list[tuple[str, str]] = []
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
        if res != "ok" and res != "cached":
            failures.append((slug, res))
        pbar.update(1)

    await asyncio.gather(*(go(s, o, n) for s, o, n in repos))
    pbar.close()

    if failures:
        print("  failures:", flush=True)
        for slug, why in failures[:20]:
            print(f"    {slug:40s} {why}", flush=True)
        if len(failures) > 20:
            print(f"    … and {len(failures) - 20} more", flush=True)

    return counts


def clone_all() -> Path:
    repos = _identity_repos()
    if not repos:
        raise FileNotFoundError("No identity.toml files — run `ossify-repos` first")
    counts = asyncio.run(_run(repos))
    print(
        "  Clone:",
        ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        flush=True,
    )
    return paths()["repos_dir"]

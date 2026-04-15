"""Sparse clone helper. No longer a pipeline stage — called per-repo
from compose.py during classify, into a tempdir that gets cleaned up
immediately after rules read it."""

from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path

from ossify.defaults import resolve

_GIT_ENV = {
    **os.environ,
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_ASKPASS": "/bin/echo",
    "SSH_ASKPASS": "/bin/echo",
    "GCM_INTERACTIVE": "Never",
    "GIT_CONFIG_COUNT": "1",
    "GIT_CONFIG_KEY_0": "credential.https://github.com.helper",
    "GIT_CONFIG_VALUE_0": "!gh auth git-credential",
}


async def _run_git(cmd: list[str], cwd: Path, timeout: float) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.DEVNULL,
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


async def sparse_clone(owner: str, name: str, dest: Path) -> tuple[bool, str]:
    """Sparse-clone into `dest` (which should be empty). Returns (ok, tag)."""
    cfg = resolve()["clone"]
    sparse_paths = cfg["paths"]
    timeout = cfg["timeout_seconds"]

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
            low = err.lower()
            if rc == -1:
                tag = "timeout"
            elif (
                "could not read" in low
                or "authentication" in low
                or "terminal prompts disabled" in low
            ):
                tag = "no-access"
            elif "repository not found" in low or "not found" in low:
                tag = "not-found"
            else:
                tag = f"git-fail-{rc}"
            return False, tag

    shutil.rmtree(dest / ".git", ignore_errors=True)
    return True, "ok"


def clone_all() -> None:
    """Vestigial entrypoint — clone is now part of classify. Kept so that
    `ossify-clone` doesn't hard-error if anyone has it in muscle memory."""
    print("  clone is now part of classify (clones are ephemeral)", flush=True)

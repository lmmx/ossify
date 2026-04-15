"""Fetch /pypi/{pkg}/json into cache/pypi/packages/<pkg>.json."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
from tqdm import tqdm

from ossify.defaults import resolve, paths
from ossify.idem import is_fresh, atomic_write_bytes


def _list_path() -> Path:
    cfg = resolve()
    return (
        paths()["cache_dir"] / "pypi" / "users" / f"{cfg['user']['pypi_username']}.txt"
    )


def _read_packages() -> list[str]:
    path = _list_path()
    if not path.exists():
        raise FileNotFoundError(f"{path} — run `ossify-discover` first")
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


async def _fetch_one(
    client: httpx.AsyncClient,
    name: str,
    out: Path,
    max_age_days: float,
    sem: asyncio.Semaphore,
    delay: float,
) -> str:
    if is_fresh(out, max_age_days):
        return "cached"
    async with sem:
        try:
            r = await client.get(
                f"https://pypi.org/pypi/{name}/json",
                follow_redirects=True,
            )
            await asyncio.sleep(delay)
            if r.status_code != 200:
                return f"http {r.status_code}"
            atomic_write_bytes(out, r.content)
            return "ok"
        except Exception as exc:
            return f"err {exc.__class__.__name__}"


async def _run(packages: list[str]) -> dict[str, int]:
    cfg = resolve()
    p = paths()
    out_dir = p["cache_dir"] / "pypi" / "packages"
    out_dir.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": cfg["pypi"]["user_agent"]}
    sem = asyncio.Semaphore(cfg["scrape"]["concurrency"])
    delay = cfg["scrape"]["request_delay_seconds"]
    max_age = cfg["pypi"]["json_max_age_days"]

    counts: dict[str, int] = {}
    pbar = tqdm(total=len(packages), desc="PyPI JSON", unit="pkg")

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:

        async def go(name: str) -> None:
            res = await _fetch_one(
                client,
                name,
                out_dir / f"{name}.json",
                max_age,
                sem,
                delay,
            )
            counts[res] = counts.get(res, 0) + 1
            pbar.update(1)

        await asyncio.gather(*(go(n) for n in packages))

    pbar.close()
    return counts


def fetch_all() -> Path:
    pkgs = _read_packages()
    counts = asyncio.run(_run(pkgs))
    print("PyPI JSON fetch:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return paths()["cache_dir"] / "pypi" / "packages"

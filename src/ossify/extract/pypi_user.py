"""Scrape PyPI user page → list of package names."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx
from selectolax.parser import HTMLParser

from ossify.defaults import resolve, paths
from ossify.idem import atomic_write_text


def _extract_package_names(html: str, selector: str) -> list[str]:
    tree = HTMLParser(html)
    return [n.text(strip=True) for n in tree.css(selector)]


def _log(msg: str) -> None:
    print(f"  {msg}", flush=True)


async def _fetch_page(client: httpx.AsyncClient, url: str) -> str:
    r = await client.get(url, follow_redirects=True)
    r.raise_for_status()
    return r.text


async def _scrape(username: str, cfg: dict, cache_html: Path) -> list[str]:
    headers = {"User-Agent": cfg["user_agent"]}
    base_url = cfg["user_url"].format(username=username)
    timeout = httpx.Timeout(connect=10, read=20, write=10, pool=10)

    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        all_names: list[str] = []
        page = 1
        while True:
            url = base_url if page == 1 else f"{base_url}?page={page}"
            _log(f"fetching page {page}: {url}")
            try:
                html = await _fetch_page(client, url)
            except httpx.HTTPError as exc:
                _log(f"page {page} failed: {exc.__class__.__name__}: {exc}")
                if page == 1:
                    raise
                break

            names = _extract_package_names(html, cfg["package_selector"])
            _log(f"page {page}: {len(names)} package(s) found")
            if not names:
                break
            if page == 1:
                atomic_write_text(cache_html, html)
                _log(f"cached HTML → {cache_html}")
            all_names.extend(names)
            page += 1

        return sorted(set(all_names))


def discover() -> Path:
    cfg = resolve()
    username = cfg["user"]["pypi_username"]
    p = paths()
    cache_html = p["cache_dir"] / "pypi" / "users" / f"{username}.html"
    list_path = cache_html.with_suffix(".txt")

    _log(f"username = {username}")
    names = asyncio.run(_scrape(username, {**cfg["pypi"], **cfg["scrape"]}, cache_html))
    atomic_write_text(list_path, "\n".join(names) + "\n")

    _log(f"{len(names)} unique package(s) total")
    _log(f"wrote {list_path}")
    return list_path
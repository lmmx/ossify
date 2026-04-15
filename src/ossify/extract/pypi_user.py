"""Scrape PyPI user page → list of package names."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
from selectolax.parser import HTMLParser

from ossify.defaults import resolve, paths
from ossify.idem import atomic_write_text


def _extract_package_names(html: str, selector: str) -> list[str]:
    tree = HTMLParser(html)
    return [n.text(strip=True) for n in tree.css(selector)]


async def _fetch_page(client: httpx.AsyncClient, url: str) -> str:
    r = await client.get(url, follow_redirects=True)
    r.raise_for_status()
    return r.text


async def _scrape(username: str, cfg: dict, cache_html: Path) -> list[str]:
    headers = {"User-Agent": cfg["user_agent"]}
    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        all_names: list[str] = []
        page = 1
        # Naïve pagination: walk ?page=N until a page returns nothing
        while True:
            url = cfg["user_url"].format(username=username)
            if page > 1:
                url = f"{url}?page={page}"
            html = await _fetch_page(client, url)
            names = _extract_package_names(html, cfg["package_selector"])
            if not names:
                break
            if page == 1:
                atomic_write_text(cache_html, html)
            all_names.extend(names)
            page += 1
        return sorted(set(all_names))


def discover() -> Path:
    cfg = resolve()
    username = cfg["user"]["pypi_username"]
    p = paths()
    cache_html = p["cache_dir"] / "pypi" / "users" / f"{username}.html"
    list_path = cache_html.with_suffix(".txt")

    names = asyncio.run(_scrape(username, {**cfg["pypi"], **cfg["scrape"]}, cache_html))
    atomic_write_text(list_path, "\n".join(names) + "\n")

    print(f"{len(names)} packages found for {username}")
    print(f"  → {list_path}")
    return list_path

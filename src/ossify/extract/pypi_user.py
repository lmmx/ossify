"""Scrape PyPI user page → list of package names.

The user page (https://pypi.org/user/{name}/) is a single HTML document
listing every project.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
from selectolax.parser import HTMLParser

from ossify.defaults import paths, resolve
from ossify.idem import atomic_write_text


def _log(msg: str) -> None:
    print(f"  {msg}", flush=True)


def _extract_package_names(html: str, selector: str) -> list[str]:
    tree = HTMLParser(html)
    return [n.text(strip=True) for n in tree.css(selector)]


async def _fetch(username: str, cfg: dict) -> str:
    headers = {"User-Agent": cfg["user_agent"]}
    timeout = httpx.Timeout(connect=10, read=20, write=10, pool=10)
    url = cfg["user_url"].format(username=username)

    _log(f"GET {url}")
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
    _log(f"  {len(r.content)} bytes, status {r.status_code}")
    return r.text


def discover() -> Path:
    cfg = resolve()
    username = cfg["user"]["pypi_username"]
    p = paths()
    cache_html = p["cache_dir"] / "pypi" / "users" / f"{username}.html"
    list_path = cache_html.with_suffix(".txt")

    _log(f"username = {username}")
    html = asyncio.run(_fetch(username, {**cfg["pypi"], **cfg["scrape"]}))

    atomic_write_text(cache_html, html)
    _log(f"cached HTML → {cache_html}")

    names = sorted(set(_extract_package_names(html, cfg["pypi"]["package_selector"])))
    atomic_write_text(list_path, "\n".join(names) + "\n")

    _log(f"{len(names)} unique package(s)")
    _log(f"wrote {list_path}")
    return list_path

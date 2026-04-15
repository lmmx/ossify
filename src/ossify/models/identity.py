from pydantic import HttpUrl
from ._base import Frozen


class Identity(Frozen):
    repo: str  # owner__name slug
    owner: str
    name: str
    packages: tuple[str, ...]  # PyPI names hosted in this repo
    archived: bool = False
    priority: bool = False  # discreet CV-relevance flag
    description: str | None = None
    url: HttpUrl | None = None

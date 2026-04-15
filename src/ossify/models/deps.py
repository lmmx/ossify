from ._base import Frozen
from .enums import DepBot, Pinning


class Deps(Frozen):
    bots: frozenset[DepBot] = frozenset()
    pinning: Pinning = Pinning.unknown
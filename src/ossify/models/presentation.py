from ._base import Frozen, NonNegInt


class Presentation(Frozen):
    has_readme: bool = False
    readme_badges: NonNegInt = 0

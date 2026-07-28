from .activity import Activity
from .deps import Deps
from .enums import (
    BuildSystem,
    DepBot,
    Pinning,
    PublishAuth,
    PublishMode,
)
from .identity import Identity
from .modernisation import Modernisation
from .presentation import Presentation
from .record import RepoRecord
from .release import Release
from .verification import Verification

CATEGORY_MODELS = {
    "identity": Identity,
    "activity": Activity,
    "verification": Verification,
    "release": Release,
    "deps": Deps,
    "modernisation": Modernisation,
    "presentation": Presentation,
}

__all__ = [
    "CATEGORY_MODELS",
    "Activity",
    "BuildSystem",
    "DepBot",
    "Deps",
    "Identity",
    "Modernisation",
    "Pinning",
    "Presentation",
    "PublishAuth",
    "PublishMode",
    "Release",
    "RepoRecord",
    "Verification",
]

from .identity import Identity
from .activity import Activity
from .verification import Verification
from .release import Release
from .deps import Deps
from .modernisation import Modernisation
from .presentation import Presentation
from .record import RepoRecord
from .enums import (
    BuildSystem,
    PublishMode,
    PublishAuth,
    DepBot,
    Pinning,
)

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
    "Identity",
    "Activity",
    "Verification",
    "Release",
    "Deps",
    "Modernisation",
    "Presentation",
    "RepoRecord",
    "BuildSystem",
    "PublishMode",
    "PublishAuth",
    "DepBot",
    "Pinning",
    "CATEGORY_MODELS",
]

from ._base import Frozen
from .activity import Activity
from .deps import Deps
from .identity import Identity
from .modernisation import Modernisation
from .presentation import Presentation
from .release import Release
from .verification import Verification


class RepoRecord(Frozen):
    identity: Identity
    activity: Activity = Activity()
    verification: Verification = Verification()
    release: Release = Release()
    deps: Deps = Deps()
    modernisation: Modernisation = Modernisation()
    presentation: Presentation = Presentation()

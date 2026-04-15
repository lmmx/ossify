from ._base import Frozen
from .identity import Identity
from .activity import Activity
from .verification import Verification
from .release import Release
from .deps import Deps
from .modernisation import Modernisation
from .presentation import Presentation


class RepoRecord(Frozen):
    identity: Identity
    activity: Activity = Activity()
    verification: Verification = Verification()
    release: Release = Release()
    deps: Deps = Deps()
    modernisation: Modernisation = Modernisation()
    presentation: Presentation = Presentation()

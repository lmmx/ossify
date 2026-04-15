from datetime import datetime
from ._base import Frozen, NonNegInt
from .enums import PublishMode, PublishAuth


class Release(Frozen):
    version_count: NonNegInt = 0
    last_release_at: datetime | None = None
    release_cadence_days: float | None = None
    publish_mode: PublishMode = PublishMode.unknown
    publish_auth: PublishAuth = PublishAuth.unknown

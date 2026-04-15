from datetime import datetime, timedelta
from ._base import Frozen, Ratio, NonNegInt


class Activity(Frozen):
    last_commit_at: datetime | None = None
    last_human_commit_at: datetime | None = None
    last_bot_commit_at: datetime | None = None
    human_commits_window: NonNegInt = 0
    bot_commits_window: NonNegInt = 0
    human_ratio_window: Ratio | None = None
    window_days: NonNegInt = 90

    @property
    def zombie_for(self) -> timedelta | None:
        if (
            self.last_human_commit_at
            and self.last_bot_commit_at
            and self.last_bot_commit_at > self.last_human_commit_at
        ):
            return self.last_bot_commit_at - self.last_human_commit_at
        return None

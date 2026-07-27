"""Rule registry — one module per signal, grouped by category.

A rule writes one (or a small bundle of) field(s) on one category model.
Adding a signal: drop a new module here and import it below.
"""

from __future__ import annotations

from ._base import RepoContext, Rule

# Activity
from .activity import commit_attribution

# Deps
from .deps import dependabot, precommit_ci, renovate

# Modernisation
from .modernisation import build_system, drift_pdm_to_uv, drift_token_to_trusted

# Presentation
from .presentation import readme_badges

# Release
from .release import trusted_publishing, version_count

# Verification
from .verification import ci_runs_tests, has_tests, precommit

ALL_RULES: list[Rule] = [
    commit_attribution.rule,
    has_tests.rule,
    ci_runs_tests.rule,
    precommit.rule,
    version_count.rule,
    trusted_publishing.rule,
    renovate.rule,
    dependabot.rule,
    precommit_ci.rule,
    build_system.rule,
    drift_pdm_to_uv.rule,
    drift_token_to_trusted.rule,
    readme_badges.rule,
]

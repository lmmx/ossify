"""Rule registry — one module per signal, grouped by category.

A rule writes one (or a small bundle of) field(s) on one category model.
Adding a signal: drop a new module here and import it below.
"""

from __future__ import annotations

from ._base import Rule, RepoContext

# Activity
from .activity import commit_attribution

# Verification
from .verification import has_tests, ci_runs_tests, precommit

# Release
from .release import version_count, trusted_publishing

# Deps
from .deps import renovate, dependabot, precommit_ci

# Modernisation
from .modernisation import build_system, drift_pdm_to_uv, drift_token_to_trusted

# Presentation
from .presentation import readme_badges

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

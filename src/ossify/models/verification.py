from ._base import Frozen


class Verification(Frozen):
    has_tests: bool = False
    has_ci: bool = False
    ci_runs_tests: bool = False
    ci_passing: bool | None = None
    precommit_configured: bool = False
    precommit_passing: bool | None = None

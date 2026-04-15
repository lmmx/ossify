from ._base import Frozen
from .enums import BuildSystem


class Modernisation(Frozen):
    build_system: BuildSystem = BuildSystem.unknown
    drift_pdm_to_uv: bool = False
    drift_local_to_ci_publish: bool = False
    drift_token_to_trusted: bool = False

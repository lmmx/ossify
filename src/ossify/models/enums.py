from enum import StrEnum


class BuildSystem(StrEnum):
    uv = "uv"
    pdm = "pdm"
    poetry = "poetry"
    hatch = "hatch"
    setuptools = "setuptools"
    flit = "flit"
    unknown = "unknown"


class PublishMode(StrEnum):
    ci = "ci"
    local = "local"
    none = "none"
    unknown = "unknown"


class PublishAuth(StrEnum):
    trusted = "trusted"
    token = "token"
    none = "none"
    unknown = "unknown"


class DepBot(StrEnum):
    renovate = "renovate"
    dependabot = "dependabot"
    precommit_ci = "precommit_ci"


class Pinning(StrEnum):
    strict = "strict"
    loose = "loose"
    unknown = "unknown"

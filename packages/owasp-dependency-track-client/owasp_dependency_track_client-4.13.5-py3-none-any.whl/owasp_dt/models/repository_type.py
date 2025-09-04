from enum import Enum


class RepositoryType(str, Enum):
    CARGO = "CARGO"
    COMPOSER = "COMPOSER"
    CPAN = "CPAN"
    GEM = "GEM"
    GITHUB = "GITHUB"
    GO_MODULES = "GO_MODULES"
    HACKAGE = "HACKAGE"
    HEX = "HEX"
    MAVEN = "MAVEN"
    NIXPKGS = "NIXPKGS"
    NPM = "NPM"
    NUGET = "NUGET"
    PYPI = "PYPI"
    UNSUPPORTED = "UNSUPPORTED"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class AffectedVersionAttributionSource(str, Enum):
    GITHUB = "GITHUB"
    INTERNAL = "INTERNAL"
    NPM = "NPM"
    NVD = "NVD"
    OSSINDEX = "OSSINDEX"
    OSV = "OSV"
    RETIREJS = "RETIREJS"
    SNYK = "SNYK"
    TRIVY = "TRIVY"
    UNKNOWN = "UNKNOWN"
    VULNDB = "VULNDB"

    def __str__(self) -> str:
        return str(self.value)

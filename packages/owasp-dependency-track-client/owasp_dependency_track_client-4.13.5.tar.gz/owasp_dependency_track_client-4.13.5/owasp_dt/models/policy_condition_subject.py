from enum import Enum


class PolicyConditionSubject(str, Enum):
    AGE = "AGE"
    COMPONENT_HASH = "COMPONENT_HASH"
    COORDINATES = "COORDINATES"
    CPE = "CPE"
    CWE = "CWE"
    EPSS = "EPSS"
    LICENSE = "LICENSE"
    LICENSE_GROUP = "LICENSE_GROUP"
    PACKAGE_URL = "PACKAGE_URL"
    SEVERITY = "SEVERITY"
    SWID_TAGID = "SWID_TAGID"
    VERSION = "VERSION"
    VERSION_DISTANCE = "VERSION_DISTANCE"
    VULNERABILITY_ID = "VULNERABILITY_ID"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class FindingAttribAnalyzerIdentity(str, Enum):
    INTERNAL_ANALYZER = "INTERNAL_ANALYZER"
    NONE = "NONE"
    NPM_AUDIT_ANALYZER = "NPM_AUDIT_ANALYZER"
    OSSINDEX_ANALYZER = "OSSINDEX_ANALYZER"
    SNYK_ANALYZER = "SNYK_ANALYZER"
    TRIVY_ANALYZER = "TRIVY_ANALYZER"
    VULNDB_ANALYZER = "VULNDB_ANALYZER"

    def __str__(self) -> str:
        return str(self.value)

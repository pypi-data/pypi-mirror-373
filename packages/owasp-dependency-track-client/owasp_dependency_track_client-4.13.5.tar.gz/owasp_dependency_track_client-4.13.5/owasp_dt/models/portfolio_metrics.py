from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PortfolioMetrics")


@_attrs_define
class PortfolioMetrics:
    """
    Attributes:
        critical (int):
        high (int):
        medium (int):
        low (int):
        first_occurrence (int): UNIX epoch timestamp in milliseconds
        last_occurrence (int): UNIX epoch timestamp in milliseconds
        unassigned (Union[Unset, int]):
        vulnerabilities (Union[Unset, int]):
        projects (Union[Unset, int]):
        vulnerable_projects (Union[Unset, int]):
        components (Union[Unset, int]):
        vulnerable_components (Union[Unset, int]):
        suppressed (Union[Unset, int]):
        findings_total (Union[Unset, int]):
        findings_audited (Union[Unset, int]):
        findings_unaudited (Union[Unset, int]):
        inherited_risk_score (Union[Unset, float]):
        policy_violations_fail (Union[Unset, int]):
        policy_violations_warn (Union[Unset, int]):
        policy_violations_info (Union[Unset, int]):
        policy_violations_total (Union[Unset, int]):
        policy_violations_audited (Union[Unset, int]):
        policy_violations_unaudited (Union[Unset, int]):
        policy_violations_security_total (Union[Unset, int]):
        policy_violations_security_audited (Union[Unset, int]):
        policy_violations_security_unaudited (Union[Unset, int]):
        policy_violations_license_total (Union[Unset, int]):
        policy_violations_license_audited (Union[Unset, int]):
        policy_violations_license_unaudited (Union[Unset, int]):
        policy_violations_operational_total (Union[Unset, int]):
        policy_violations_operational_audited (Union[Unset, int]):
        policy_violations_operational_unaudited (Union[Unset, int]):
    """

    critical: int
    high: int
    medium: int
    low: int
    first_occurrence: int
    last_occurrence: int
    unassigned: Union[Unset, int] = UNSET
    vulnerabilities: Union[Unset, int] = UNSET
    projects: Union[Unset, int] = UNSET
    vulnerable_projects: Union[Unset, int] = UNSET
    components: Union[Unset, int] = UNSET
    vulnerable_components: Union[Unset, int] = UNSET
    suppressed: Union[Unset, int] = UNSET
    findings_total: Union[Unset, int] = UNSET
    findings_audited: Union[Unset, int] = UNSET
    findings_unaudited: Union[Unset, int] = UNSET
    inherited_risk_score: Union[Unset, float] = UNSET
    policy_violations_fail: Union[Unset, int] = UNSET
    policy_violations_warn: Union[Unset, int] = UNSET
    policy_violations_info: Union[Unset, int] = UNSET
    policy_violations_total: Union[Unset, int] = UNSET
    policy_violations_audited: Union[Unset, int] = UNSET
    policy_violations_unaudited: Union[Unset, int] = UNSET
    policy_violations_security_total: Union[Unset, int] = UNSET
    policy_violations_security_audited: Union[Unset, int] = UNSET
    policy_violations_security_unaudited: Union[Unset, int] = UNSET
    policy_violations_license_total: Union[Unset, int] = UNSET
    policy_violations_license_audited: Union[Unset, int] = UNSET
    policy_violations_license_unaudited: Union[Unset, int] = UNSET
    policy_violations_operational_total: Union[Unset, int] = UNSET
    policy_violations_operational_audited: Union[Unset, int] = UNSET
    policy_violations_operational_unaudited: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        critical = self.critical

        high = self.high

        medium = self.medium

        low = self.low

        first_occurrence = self.first_occurrence

        last_occurrence = self.last_occurrence

        unassigned = self.unassigned

        vulnerabilities = self.vulnerabilities

        projects = self.projects

        vulnerable_projects = self.vulnerable_projects

        components = self.components

        vulnerable_components = self.vulnerable_components

        suppressed = self.suppressed

        findings_total = self.findings_total

        findings_audited = self.findings_audited

        findings_unaudited = self.findings_unaudited

        inherited_risk_score = self.inherited_risk_score

        policy_violations_fail = self.policy_violations_fail

        policy_violations_warn = self.policy_violations_warn

        policy_violations_info = self.policy_violations_info

        policy_violations_total = self.policy_violations_total

        policy_violations_audited = self.policy_violations_audited

        policy_violations_unaudited = self.policy_violations_unaudited

        policy_violations_security_total = self.policy_violations_security_total

        policy_violations_security_audited = self.policy_violations_security_audited

        policy_violations_security_unaudited = self.policy_violations_security_unaudited

        policy_violations_license_total = self.policy_violations_license_total

        policy_violations_license_audited = self.policy_violations_license_audited

        policy_violations_license_unaudited = self.policy_violations_license_unaudited

        policy_violations_operational_total = self.policy_violations_operational_total

        policy_violations_operational_audited = (
            self.policy_violations_operational_audited
        )

        policy_violations_operational_unaudited = (
            self.policy_violations_operational_unaudited
        )

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "firstOccurrence": first_occurrence,
                "lastOccurrence": last_occurrence,
            }
        )
        if unassigned is not UNSET:
            field_dict["unassigned"] = unassigned
        if vulnerabilities is not UNSET:
            field_dict["vulnerabilities"] = vulnerabilities
        if projects is not UNSET:
            field_dict["projects"] = projects
        if vulnerable_projects is not UNSET:
            field_dict["vulnerableProjects"] = vulnerable_projects
        if components is not UNSET:
            field_dict["components"] = components
        if vulnerable_components is not UNSET:
            field_dict["vulnerableComponents"] = vulnerable_components
        if suppressed is not UNSET:
            field_dict["suppressed"] = suppressed
        if findings_total is not UNSET:
            field_dict["findingsTotal"] = findings_total
        if findings_audited is not UNSET:
            field_dict["findingsAudited"] = findings_audited
        if findings_unaudited is not UNSET:
            field_dict["findingsUnaudited"] = findings_unaudited
        if inherited_risk_score is not UNSET:
            field_dict["inheritedRiskScore"] = inherited_risk_score
        if policy_violations_fail is not UNSET:
            field_dict["policyViolationsFail"] = policy_violations_fail
        if policy_violations_warn is not UNSET:
            field_dict["policyViolationsWarn"] = policy_violations_warn
        if policy_violations_info is not UNSET:
            field_dict["policyViolationsInfo"] = policy_violations_info
        if policy_violations_total is not UNSET:
            field_dict["policyViolationsTotal"] = policy_violations_total
        if policy_violations_audited is not UNSET:
            field_dict["policyViolationsAudited"] = policy_violations_audited
        if policy_violations_unaudited is not UNSET:
            field_dict["policyViolationsUnaudited"] = policy_violations_unaudited
        if policy_violations_security_total is not UNSET:
            field_dict["policyViolationsSecurityTotal"] = (
                policy_violations_security_total
            )
        if policy_violations_security_audited is not UNSET:
            field_dict["policyViolationsSecurityAudited"] = (
                policy_violations_security_audited
            )
        if policy_violations_security_unaudited is not UNSET:
            field_dict["policyViolationsSecurityUnaudited"] = (
                policy_violations_security_unaudited
            )
        if policy_violations_license_total is not UNSET:
            field_dict["policyViolationsLicenseTotal"] = policy_violations_license_total
        if policy_violations_license_audited is not UNSET:
            field_dict["policyViolationsLicenseAudited"] = (
                policy_violations_license_audited
            )
        if policy_violations_license_unaudited is not UNSET:
            field_dict["policyViolationsLicenseUnaudited"] = (
                policy_violations_license_unaudited
            )
        if policy_violations_operational_total is not UNSET:
            field_dict["policyViolationsOperationalTotal"] = (
                policy_violations_operational_total
            )
        if policy_violations_operational_audited is not UNSET:
            field_dict["policyViolationsOperationalAudited"] = (
                policy_violations_operational_audited
            )
        if policy_violations_operational_unaudited is not UNSET:
            field_dict["policyViolationsOperationalUnaudited"] = (
                policy_violations_operational_unaudited
            )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        critical = d.pop("critical")

        high = d.pop("high")

        medium = d.pop("medium")

        low = d.pop("low")

        first_occurrence = d.pop("firstOccurrence")

        last_occurrence = d.pop("lastOccurrence")

        unassigned = d.pop("unassigned", UNSET)

        vulnerabilities = d.pop("vulnerabilities", UNSET)

        projects = d.pop("projects", UNSET)

        vulnerable_projects = d.pop("vulnerableProjects", UNSET)

        components = d.pop("components", UNSET)

        vulnerable_components = d.pop("vulnerableComponents", UNSET)

        suppressed = d.pop("suppressed", UNSET)

        findings_total = d.pop("findingsTotal", UNSET)

        findings_audited = d.pop("findingsAudited", UNSET)

        findings_unaudited = d.pop("findingsUnaudited", UNSET)

        inherited_risk_score = d.pop("inheritedRiskScore", UNSET)

        policy_violations_fail = d.pop("policyViolationsFail", UNSET)

        policy_violations_warn = d.pop("policyViolationsWarn", UNSET)

        policy_violations_info = d.pop("policyViolationsInfo", UNSET)

        policy_violations_total = d.pop("policyViolationsTotal", UNSET)

        policy_violations_audited = d.pop("policyViolationsAudited", UNSET)

        policy_violations_unaudited = d.pop("policyViolationsUnaudited", UNSET)

        policy_violations_security_total = d.pop("policyViolationsSecurityTotal", UNSET)

        policy_violations_security_audited = d.pop(
            "policyViolationsSecurityAudited", UNSET
        )

        policy_violations_security_unaudited = d.pop(
            "policyViolationsSecurityUnaudited", UNSET
        )

        policy_violations_license_total = d.pop("policyViolationsLicenseTotal", UNSET)

        policy_violations_license_audited = d.pop(
            "policyViolationsLicenseAudited", UNSET
        )

        policy_violations_license_unaudited = d.pop(
            "policyViolationsLicenseUnaudited", UNSET
        )

        policy_violations_operational_total = d.pop(
            "policyViolationsOperationalTotal", UNSET
        )

        policy_violations_operational_audited = d.pop(
            "policyViolationsOperationalAudited", UNSET
        )

        policy_violations_operational_unaudited = d.pop(
            "policyViolationsOperationalUnaudited", UNSET
        )

        portfolio_metrics = cls(
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            first_occurrence=first_occurrence,
            last_occurrence=last_occurrence,
            unassigned=unassigned,
            vulnerabilities=vulnerabilities,
            projects=projects,
            vulnerable_projects=vulnerable_projects,
            components=components,
            vulnerable_components=vulnerable_components,
            suppressed=suppressed,
            findings_total=findings_total,
            findings_audited=findings_audited,
            findings_unaudited=findings_unaudited,
            inherited_risk_score=inherited_risk_score,
            policy_violations_fail=policy_violations_fail,
            policy_violations_warn=policy_violations_warn,
            policy_violations_info=policy_violations_info,
            policy_violations_total=policy_violations_total,
            policy_violations_audited=policy_violations_audited,
            policy_violations_unaudited=policy_violations_unaudited,
            policy_violations_security_total=policy_violations_security_total,
            policy_violations_security_audited=policy_violations_security_audited,
            policy_violations_security_unaudited=policy_violations_security_unaudited,
            policy_violations_license_total=policy_violations_license_total,
            policy_violations_license_audited=policy_violations_license_audited,
            policy_violations_license_unaudited=policy_violations_license_unaudited,
            policy_violations_operational_total=policy_violations_operational_total,
            policy_violations_operational_audited=policy_violations_operational_audited,
            policy_violations_operational_unaudited=policy_violations_operational_unaudited,
        )

        portfolio_metrics.additional_properties = d
        return portfolio_metrics

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

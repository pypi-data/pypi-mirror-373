from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.finding_analysis import FindingAnalysis
    from ..models.finding_attrib import FindingAttrib
    from ..models.finding_component import FindingComponent
    from ..models.finding_vulnerability import FindingVulnerability


T = TypeVar("T", bound="Finding")


@_attrs_define
class Finding:
    """
    Attributes:
        component (Union[Unset, FindingComponent]):
        vulnerability (Union[Unset, FindingVulnerability]):
        analysis (Union[Unset, FindingAnalysis]):
        attribution (Union[Unset, FindingAttrib]):
        matrix (Union[Unset, str]):
    """

    component: Union[Unset, "FindingComponent"] = UNSET
    vulnerability: Union[Unset, "FindingVulnerability"] = UNSET
    analysis: Union[Unset, "FindingAnalysis"] = UNSET
    attribution: Union[Unset, "FindingAttrib"] = UNSET
    matrix: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        component: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.component, Unset):
            component = self.component.to_dict()

        vulnerability: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vulnerability, Unset):
            vulnerability = self.vulnerability.to_dict()

        analysis: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.analysis, Unset):
            analysis = self.analysis.to_dict()

        attribution: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attribution, Unset):
            attribution = self.attribution.to_dict()

        matrix = self.matrix

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if component is not UNSET:
            field_dict["component"] = component
        if vulnerability is not UNSET:
            field_dict["vulnerability"] = vulnerability
        if analysis is not UNSET:
            field_dict["analysis"] = analysis
        if attribution is not UNSET:
            field_dict["attribution"] = attribution
        if matrix is not UNSET:
            field_dict["matrix"] = matrix

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finding_analysis import FindingAnalysis
        from ..models.finding_attrib import FindingAttrib
        from ..models.finding_component import FindingComponent
        from ..models.finding_vulnerability import FindingVulnerability

        d = dict(src_dict)
        _component = d.pop("component", UNSET)
        component: Union[Unset, FindingComponent]
        if isinstance(_component, Unset):
            component = UNSET
        else:
            component = FindingComponent.from_dict(_component)

        _vulnerability = d.pop("vulnerability", UNSET)
        vulnerability: Union[Unset, FindingVulnerability]
        if isinstance(_vulnerability, Unset):
            vulnerability = UNSET
        else:
            vulnerability = FindingVulnerability.from_dict(_vulnerability)

        _analysis = d.pop("analysis", UNSET)
        analysis: Union[Unset, FindingAnalysis]
        if isinstance(_analysis, Unset):
            analysis = UNSET
        else:
            analysis = FindingAnalysis.from_dict(_analysis)

        _attribution = d.pop("attribution", UNSET)
        attribution: Union[Unset, FindingAttrib]
        if isinstance(_attribution, Unset):
            attribution = UNSET
        else:
            attribution = FindingAttrib.from_dict(_attribution)

        matrix = d.pop("matrix", UNSET)

        finding = cls(
            component=component,
            vulnerability=vulnerability,
            analysis=analysis,
            attribution=attribution,
            matrix=matrix,
        )

        finding.additional_properties = d
        return finding

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

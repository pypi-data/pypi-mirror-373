from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.finding_attrib_analyzer_identity import FindingAttribAnalyzerIdentity
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.component import Component
    from ..models.vulnerability import Vulnerability


T = TypeVar("T", bound="FindingAttrib")


@_attrs_define
class FindingAttrib:
    """
    Attributes:
        attributed_on (Union[Unset, int]): UNIX epoch timestamp in milliseconds
        analyzer_identity (Union[Unset, FindingAttribAnalyzerIdentity]):
        component (Union[Unset, Component]):
        vulnerability (Union[Unset, Vulnerability]):
        alternate_identifier (Union[Unset, str]):
        reference_url (Union[Unset, str]):
        uuid (Union[Unset, UUID]):
    """

    attributed_on: Union[Unset, int] = UNSET
    analyzer_identity: Union[Unset, FindingAttribAnalyzerIdentity] = UNSET
    component: Union[Unset, "Component"] = UNSET
    vulnerability: Union[Unset, "Vulnerability"] = UNSET
    alternate_identifier: Union[Unset, str] = UNSET
    reference_url: Union[Unset, str] = UNSET
    uuid: Union[Unset, UUID] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attributed_on = self.attributed_on

        analyzer_identity: Union[Unset, str] = UNSET
        if not isinstance(self.analyzer_identity, Unset):
            analyzer_identity = self.analyzer_identity.value

        component: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.component, Unset):
            component = self.component.to_dict()

        vulnerability: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vulnerability, Unset):
            vulnerability = self.vulnerability.to_dict()

        alternate_identifier = self.alternate_identifier

        reference_url = self.reference_url

        uuid: Union[Unset, str] = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if attributed_on is not UNSET:
            field_dict["attributedOn"] = attributed_on
        if analyzer_identity is not UNSET:
            field_dict["analyzerIdentity"] = analyzer_identity
        if component is not UNSET:
            field_dict["component"] = component
        if vulnerability is not UNSET:
            field_dict["vulnerability"] = vulnerability
        if alternate_identifier is not UNSET:
            field_dict["alternateIdentifier"] = alternate_identifier
        if reference_url is not UNSET:
            field_dict["referenceUrl"] = reference_url
        if uuid is not UNSET:
            field_dict["uuid"] = uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.component import Component
        from ..models.vulnerability import Vulnerability

        d = dict(src_dict)
        attributed_on = d.pop("attributedOn", UNSET)

        _analyzer_identity = d.pop("analyzerIdentity", UNSET)
        analyzer_identity: Union[Unset, FindingAttribAnalyzerIdentity]
        if isinstance(_analyzer_identity, Unset):
            analyzer_identity = UNSET
        else:
            analyzer_identity = FindingAttribAnalyzerIdentity(_analyzer_identity)

        _component = d.pop("component", UNSET)
        component: Union[Unset, Component]
        if isinstance(_component, Unset):
            component = UNSET
        else:
            component = Component.from_dict(_component)

        _vulnerability = d.pop("vulnerability", UNSET)
        vulnerability: Union[Unset, Vulnerability]
        if isinstance(_vulnerability, Unset):
            vulnerability = UNSET
        else:
            vulnerability = Vulnerability.from_dict(_vulnerability)

        alternate_identifier = d.pop("alternateIdentifier", UNSET)

        reference_url = d.pop("referenceUrl", UNSET)

        _uuid = d.pop("uuid", UNSET)
        uuid: Union[Unset, UUID]
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        finding_attrib = cls(
            attributed_on=attributed_on,
            analyzer_identity=analyzer_identity,
            component=component,
            vulnerability=vulnerability,
            alternate_identifier=alternate_identifier,
            reference_url=reference_url,
            uuid=uuid,
        )

        finding_attrib.additional_properties = d
        return finding_attrib

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

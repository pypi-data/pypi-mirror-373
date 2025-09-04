from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_classification import DataClassification
    from ..models.external_reference import ExternalReference
    from ..models.organizational_entity import OrganizationalEntity
    from ..models.project import Project
    from ..models.vulnerability import Vulnerability


T = TypeVar("T", bound="ServiceComponent")


@_attrs_define
class ServiceComponent:
    """
    Attributes:
        project (Project):
        uuid (UUID):
        provider (Union[Unset, OrganizationalEntity]):
        group (Union[Unset, str]):
        name (Union[Unset, str]):
        version (Union[Unset, str]):
        description (Union[Unset, str]):
        endpoints (Union[Unset, list[str]]):
        authenticated (Union[Unset, bool]):
        crosses_trust_boundary (Union[Unset, bool]):
        data (Union[Unset, list['DataClassification']]):
        external_references (Union[Unset, list['ExternalReference']]):
        parent (Union[Unset, ServiceComponent]):
        children (Union[Unset, list['ServiceComponent']]):
        vulnerabilities (Union[Unset, list['Vulnerability']]):
        last_inherited_risk_score (Union[Unset, float]):
        notes (Union[Unset, str]):
        bom_ref (Union[Unset, str]):
    """

    project: "Project"
    uuid: UUID
    provider: Union[Unset, "OrganizationalEntity"] = UNSET
    group: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    endpoints: Union[Unset, list[str]] = UNSET
    authenticated: Union[Unset, bool] = UNSET
    crosses_trust_boundary: Union[Unset, bool] = UNSET
    data: Union[Unset, list["DataClassification"]] = UNSET
    external_references: Union[Unset, list["ExternalReference"]] = UNSET
    parent: Union[Unset, "ServiceComponent"] = UNSET
    children: Union[Unset, list["ServiceComponent"]] = UNSET
    vulnerabilities: Union[Unset, list["Vulnerability"]] = UNSET
    last_inherited_risk_score: Union[Unset, float] = UNSET
    notes: Union[Unset, str] = UNSET
    bom_ref: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project.to_dict()

        uuid = str(self.uuid)

        provider: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.provider, Unset):
            provider = self.provider.to_dict()

        group = self.group

        name = self.name

        version = self.version

        description = self.description

        endpoints: Union[Unset, list[str]] = UNSET
        if not isinstance(self.endpoints, Unset):
            endpoints = self.endpoints

        authenticated = self.authenticated

        crosses_trust_boundary = self.crosses_trust_boundary

        data: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.data, Unset):
            data = []
            for data_item_data in self.data:
                data_item = data_item_data.to_dict()
                data.append(data_item)

        external_references: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.external_references, Unset):
            external_references = []
            for external_references_item_data in self.external_references:
                external_references_item = external_references_item_data.to_dict()
                external_references.append(external_references_item)

        parent: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.parent, Unset):
            parent = self.parent.to_dict()

        children: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.children, Unset):
            children = []
            for children_item_data in self.children:
                children_item = children_item_data.to_dict()
                children.append(children_item)

        vulnerabilities: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.vulnerabilities, Unset):
            vulnerabilities = []
            for vulnerabilities_item_data in self.vulnerabilities:
                vulnerabilities_item = vulnerabilities_item_data.to_dict()
                vulnerabilities.append(vulnerabilities_item)

        last_inherited_risk_score = self.last_inherited_risk_score

        notes = self.notes

        bom_ref = self.bom_ref

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "uuid": uuid,
            }
        )
        if provider is not UNSET:
            field_dict["provider"] = provider
        if group is not UNSET:
            field_dict["group"] = group
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if description is not UNSET:
            field_dict["description"] = description
        if endpoints is not UNSET:
            field_dict["endpoints"] = endpoints
        if authenticated is not UNSET:
            field_dict["authenticated"] = authenticated
        if crosses_trust_boundary is not UNSET:
            field_dict["crossesTrustBoundary"] = crosses_trust_boundary
        if data is not UNSET:
            field_dict["data"] = data
        if external_references is not UNSET:
            field_dict["externalReferences"] = external_references
        if parent is not UNSET:
            field_dict["parent"] = parent
        if children is not UNSET:
            field_dict["children"] = children
        if vulnerabilities is not UNSET:
            field_dict["vulnerabilities"] = vulnerabilities
        if last_inherited_risk_score is not UNSET:
            field_dict["lastInheritedRiskScore"] = last_inherited_risk_score
        if notes is not UNSET:
            field_dict["notes"] = notes
        if bom_ref is not UNSET:
            field_dict["bomRef"] = bom_ref

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_classification import DataClassification
        from ..models.external_reference import ExternalReference
        from ..models.organizational_entity import OrganizationalEntity
        from ..models.project import Project
        from ..models.vulnerability import Vulnerability

        d = dict(src_dict)
        project = Project.from_dict(d.pop("project"))

        uuid = UUID(d.pop("uuid"))

        _provider = d.pop("provider", UNSET)
        provider: Union[Unset, OrganizationalEntity]
        if isinstance(_provider, Unset):
            provider = UNSET
        else:
            provider = OrganizationalEntity.from_dict(_provider)

        group = d.pop("group", UNSET)

        name = d.pop("name", UNSET)

        version = d.pop("version", UNSET)

        description = d.pop("description", UNSET)

        endpoints = cast(list[str], d.pop("endpoints", UNSET))

        authenticated = d.pop("authenticated", UNSET)

        crosses_trust_boundary = d.pop("crossesTrustBoundary", UNSET)

        data = []
        _data = d.pop("data", UNSET)
        for data_item_data in _data or []:
            data_item = DataClassification.from_dict(data_item_data)

            data.append(data_item)

        external_references = []
        _external_references = d.pop("externalReferences", UNSET)
        for external_references_item_data in _external_references or []:
            external_references_item = ExternalReference.from_dict(
                external_references_item_data
            )

            external_references.append(external_references_item)

        _parent = d.pop("parent", UNSET)
        parent: Union[Unset, ServiceComponent]
        if isinstance(_parent, Unset):
            parent = UNSET
        else:
            parent = ServiceComponent.from_dict(_parent)

        children = []
        _children = d.pop("children", UNSET)
        for children_item_data in _children or []:
            children_item = ServiceComponent.from_dict(children_item_data)

            children.append(children_item)

        vulnerabilities = []
        _vulnerabilities = d.pop("vulnerabilities", UNSET)
        for vulnerabilities_item_data in _vulnerabilities or []:
            vulnerabilities_item = Vulnerability.from_dict(vulnerabilities_item_data)

            vulnerabilities.append(vulnerabilities_item)

        last_inherited_risk_score = d.pop("lastInheritedRiskScore", UNSET)

        notes = d.pop("notes", UNSET)

        bom_ref = d.pop("bomRef", UNSET)

        service_component = cls(
            project=project,
            uuid=uuid,
            provider=provider,
            group=group,
            name=name,
            version=version,
            description=description,
            endpoints=endpoints,
            authenticated=authenticated,
            crosses_trust_boundary=crosses_trust_boundary,
            data=data,
            external_references=external_references,
            parent=parent,
            children=children,
            vulnerabilities=vulnerabilities,
            last_inherited_risk_score=last_inherited_risk_score,
            notes=notes,
            bom_ref=bom_ref,
        )

        service_component.additional_properties = d
        return service_component

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

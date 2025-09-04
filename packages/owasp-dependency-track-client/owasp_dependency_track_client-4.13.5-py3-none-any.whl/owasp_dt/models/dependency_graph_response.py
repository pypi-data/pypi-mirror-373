from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DependencyGraphResponse")


@_attrs_define
class DependencyGraphResponse:
    """
    Attributes:
        uuid (Union[Unset, UUID]):
        name (Union[Unset, str]):
        version (Union[Unset, str]):
        purl (Union[Unset, str]):
        direct_dependencies (Union[Unset, str]):
        latest_version (Union[Unset, str]):
    """

    uuid: Union[Unset, UUID] = UNSET
    name: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    purl: Union[Unset, str] = UNSET
    direct_dependencies: Union[Unset, str] = UNSET
    latest_version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid: Union[Unset, str] = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        name = self.name

        version = self.version

        purl = self.purl

        direct_dependencies = self.direct_dependencies

        latest_version = self.latest_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if purl is not UNSET:
            field_dict["purl"] = purl
        if direct_dependencies is not UNSET:
            field_dict["directDependencies"] = direct_dependencies
        if latest_version is not UNSET:
            field_dict["latestVersion"] = latest_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _uuid = d.pop("uuid", UNSET)
        uuid: Union[Unset, UUID]
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        name = d.pop("name", UNSET)

        version = d.pop("version", UNSET)

        purl = d.pop("purl", UNSET)

        direct_dependencies = d.pop("directDependencies", UNSET)

        latest_version = d.pop("latestVersion", UNSET)

        dependency_graph_response = cls(
            uuid=uuid,
            name=name,
            version=version,
            purl=purl,
            direct_dependencies=direct_dependencies,
            latest_version=latest_version,
        )

        dependency_graph_response.additional_properties = d
        return dependency_graph_response

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

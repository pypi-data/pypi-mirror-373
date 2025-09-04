from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FindingComponent")


@_attrs_define
class FindingComponent:
    """
    Attributes:
        uuid (Union[Unset, str]):
        group (Union[Unset, str]):
        name (Union[Unset, str]):
        version (Union[Unset, str]):
        purl (Union[Unset, str]):
        project (Union[Unset, str]):
        project_name (Union[Unset, str]):
        project_version (Union[Unset, str]):
        latest_version (Union[Unset, str]):
    """

    uuid: Union[Unset, str] = UNSET
    group: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    purl: Union[Unset, str] = UNSET
    project: Union[Unset, str] = UNSET
    project_name: Union[Unset, str] = UNSET
    project_version: Union[Unset, str] = UNSET
    latest_version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = self.uuid

        group = self.group

        name = self.name

        version = self.version

        purl = self.purl

        project = self.project

        project_name = self.project_name

        project_version = self.project_version

        latest_version = self.latest_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if group is not UNSET:
            field_dict["group"] = group
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if purl is not UNSET:
            field_dict["purl"] = purl
        if project is not UNSET:
            field_dict["project"] = project
        if project_name is not UNSET:
            field_dict["projectName"] = project_name
        if project_version is not UNSET:
            field_dict["projectVersion"] = project_version
        if latest_version is not UNSET:
            field_dict["latestVersion"] = latest_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = d.pop("uuid", UNSET)

        group = d.pop("group", UNSET)

        name = d.pop("name", UNSET)

        version = d.pop("version", UNSET)

        purl = d.pop("purl", UNSET)

        project = d.pop("project", UNSET)

        project_name = d.pop("projectName", UNSET)

        project_version = d.pop("projectVersion", UNSET)

        latest_version = d.pop("latestVersion", UNSET)

        finding_component = cls(
            uuid=uuid,
            group=group,
            name=name,
            version=version,
            purl=purl,
            project=project,
            project_name=project_name,
            project_version=project_version,
            latest_version=latest_version,
        )

        finding_component.additional_properties = d
        return finding_component

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

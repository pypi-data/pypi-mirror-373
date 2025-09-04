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
    from ..models.tag import Tag


T = TypeVar("T", bound="BomSubmitRequest")


@_attrs_define
class BomSubmitRequest:
    """
    Attributes:
        project (str):  Example: 38640b33-4ba9-4733-bdab-cbfc40c6f8aa.
        bom (str): Base64 encoded BOM Example: ewogICJib21Gb3JtYXQiOiAiQ3ljbG9uZURYIiwKICAic3BlY1ZlcnNpb24iOiAiMS40IiwKI
            CAiY29tcG9uZW50cyI6IFsKICAgIHsKICAgICAgInR5cGUiOiAibGlicmFyeSIsCiAgICAgICJuYW1lIjogImFjbWUtbGliIiwKICAgICAgInZlc
            nNpb24iOiAiMS4wLjAiCiAgICB9CiAgXQp9.
        project_name (Union[Unset, str]):  Example: Example Application.
        project_version (Union[Unset, str]):  Example: 1.0.0.
        project_tags (Union[Unset, list['Tag']]): Overwrite project tags. Modifying the tags of an existing project
            requires the PORTFOLIO_MANAGEMENT permission.
        auto_create (Union[Unset, bool]):
        parent_uuid (Union[Unset, str]):  Example: 5341f53c-611b-4388-9d9c-731026dc5eec.
        parent_name (Union[Unset, str]):  Example: Example Application Parent.
        parent_version (Union[Unset, str]):  Example: 1.0.0.
        is_latest_project_version (Union[Unset, bool]):
    """

    project: str
    bom: str
    project_name: Union[Unset, str] = UNSET
    project_version: Union[Unset, str] = UNSET
    project_tags: Union[Unset, list["Tag"]] = UNSET
    auto_create: Union[Unset, bool] = UNSET
    parent_uuid: Union[Unset, str] = UNSET
    parent_name: Union[Unset, str] = UNSET
    parent_version: Union[Unset, str] = UNSET
    is_latest_project_version: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project

        bom = self.bom

        project_name = self.project_name

        project_version = self.project_version

        project_tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.project_tags, Unset):
            project_tags = []
            for project_tags_item_data in self.project_tags:
                project_tags_item = project_tags_item_data.to_dict()
                project_tags.append(project_tags_item)

        auto_create = self.auto_create

        parent_uuid = self.parent_uuid

        parent_name = self.parent_name

        parent_version = self.parent_version

        is_latest_project_version = self.is_latest_project_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "bom": bom,
            }
        )
        if project_name is not UNSET:
            field_dict["projectName"] = project_name
        if project_version is not UNSET:
            field_dict["projectVersion"] = project_version
        if project_tags is not UNSET:
            field_dict["projectTags"] = project_tags
        if auto_create is not UNSET:
            field_dict["autoCreate"] = auto_create
        if parent_uuid is not UNSET:
            field_dict["parentUUID"] = parent_uuid
        if parent_name is not UNSET:
            field_dict["parentName"] = parent_name
        if parent_version is not UNSET:
            field_dict["parentVersion"] = parent_version
        if is_latest_project_version is not UNSET:
            field_dict["isLatestProjectVersion"] = is_latest_project_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tag import Tag

        d = dict(src_dict)
        project = d.pop("project")

        bom = d.pop("bom")

        project_name = d.pop("projectName", UNSET)

        project_version = d.pop("projectVersion", UNSET)

        project_tags = []
        _project_tags = d.pop("projectTags", UNSET)
        for project_tags_item_data in _project_tags or []:
            project_tags_item = Tag.from_dict(project_tags_item_data)

            project_tags.append(project_tags_item)

        auto_create = d.pop("autoCreate", UNSET)

        parent_uuid = d.pop("parentUUID", UNSET)

        parent_name = d.pop("parentName", UNSET)

        parent_version = d.pop("parentVersion", UNSET)

        is_latest_project_version = d.pop("isLatestProjectVersion", UNSET)

        bom_submit_request = cls(
            project=project,
            bom=bom,
            project_name=project_name,
            project_version=project_version,
            project_tags=project_tags,
            auto_create=auto_create,
            parent_uuid=parent_uuid,
            parent_name=parent_name,
            parent_version=parent_version,
            is_latest_project_version=is_latest_project_version,
        )

        bom_submit_request.additional_properties = d
        return bom_submit_request

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

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, Unset

T = TypeVar("T", bound="UploadBomBody")


@_attrs_define
class UploadBomBody:
    """
    Attributes:
        project (Union[Unset, str]):
        auto_create (Union[Unset, bool]):  Default: False.
        project_name (Union[Unset, str]):
        project_version (Union[Unset, str]):
        project_tags (Union[Unset, str]):
        parent_name (Union[Unset, str]):
        parent_version (Union[Unset, str]):
        parent_uuid (Union[Unset, str]):
        is_latest (Union[Unset, bool]):  Default: False.
        bom (Union[Unset, str]):
    """

    project: Union[Unset, str] = UNSET
    auto_create: Union[Unset, bool] = False
    project_name: Union[Unset, str] = UNSET
    project_version: Union[Unset, str] = UNSET
    project_tags: Union[Unset, str] = UNSET
    parent_name: Union[Unset, str] = UNSET
    parent_version: Union[Unset, str] = UNSET
    parent_uuid: Union[Unset, str] = UNSET
    is_latest: Union[Unset, bool] = False
    bom: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project

        auto_create = self.auto_create

        project_name = self.project_name

        project_version = self.project_version

        project_tags = self.project_tags

        parent_name = self.parent_name

        parent_version = self.parent_version

        parent_uuid = self.parent_uuid

        is_latest = self.is_latest

        bom = self.bom

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if project is not UNSET:
            field_dict["project"] = project
        if auto_create is not UNSET:
            field_dict["autoCreate"] = auto_create
        if project_name is not UNSET:
            field_dict["projectName"] = project_name
        if project_version is not UNSET:
            field_dict["projectVersion"] = project_version
        if project_tags is not UNSET:
            field_dict["projectTags"] = project_tags
        if parent_name is not UNSET:
            field_dict["parentName"] = parent_name
        if parent_version is not UNSET:
            field_dict["parentVersion"] = parent_version
        if parent_uuid is not UNSET:
            field_dict["parentUUID"] = parent_uuid
        if is_latest is not UNSET:
            field_dict["isLatest"] = is_latest
        if bom is not UNSET:
            field_dict["bom"] = bom

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.project, Unset):
            files.append(("project", (None, str(self.project).encode(), "text/plain")))

        if not isinstance(self.auto_create, Unset):
            files.append(
                ("autoCreate", (None, str(self.auto_create).encode(), "text/plain"))
            )

        if not isinstance(self.project_name, Unset):
            files.append(
                ("projectName", (None, str(self.project_name).encode(), "text/plain"))
            )

        if not isinstance(self.project_version, Unset):
            files.append(
                (
                    "projectVersion",
                    (None, str(self.project_version).encode(), "text/plain"),
                )
            )

        if not isinstance(self.project_tags, Unset):
            files.append(
                ("projectTags", (None, str(self.project_tags).encode(), "text/plain"))
            )

        if not isinstance(self.parent_name, Unset):
            files.append(
                ("parentName", (None, str(self.parent_name).encode(), "text/plain"))
            )

        if not isinstance(self.parent_version, Unset):
            files.append(
                (
                    "parentVersion",
                    (None, str(self.parent_version).encode(), "text/plain"),
                )
            )

        if not isinstance(self.parent_uuid, Unset):
            files.append(
                ("parentUUID", (None, str(self.parent_uuid).encode(), "text/plain"))
            )

        if not isinstance(self.is_latest, Unset):
            files.append(
                ("isLatest", (None, str(self.is_latest).encode(), "text/plain"))
            )

        if not isinstance(self.bom, Unset):
            files.append(("bom", (None, str(self.bom).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project = d.pop("project", UNSET)

        auto_create = d.pop("autoCreate", UNSET)

        project_name = d.pop("projectName", UNSET)

        project_version = d.pop("projectVersion", UNSET)

        project_tags = d.pop("projectTags", UNSET)

        parent_name = d.pop("parentName", UNSET)

        parent_version = d.pop("parentVersion", UNSET)

        parent_uuid = d.pop("parentUUID", UNSET)

        is_latest = d.pop("isLatest", UNSET)

        bom = d.pop("bom", UNSET)

        upload_bom_body = cls(
            project=project,
            auto_create=auto_create,
            project_name=project_name,
            project_version=project_version,
            project_tags=project_tags,
            parent_name=parent_name,
            parent_version=parent_version,
            parent_uuid=parent_uuid,
            is_latest=is_latest,
            bom=bom,
        )

        upload_bom_body.additional_properties = d
        return upload_bom_body

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

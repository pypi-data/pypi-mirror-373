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

T = TypeVar("T", bound="UploadVex1Body")


@_attrs_define
class UploadVex1Body:
    """
    Attributes:
        project (Union[Unset, str]):
        project_name (Union[Unset, str]):
        project_version (Union[Unset, str]):
        vex (Union[Unset, str]):
    """

    project: Union[Unset, str] = UNSET
    project_name: Union[Unset, str] = UNSET
    project_version: Union[Unset, str] = UNSET
    vex: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project

        project_name = self.project_name

        project_version = self.project_version

        vex = self.vex

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if project is not UNSET:
            field_dict["project"] = project
        if project_name is not UNSET:
            field_dict["projectName"] = project_name
        if project_version is not UNSET:
            field_dict["projectVersion"] = project_version
        if vex is not UNSET:
            field_dict["vex"] = vex

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.project, Unset):
            files.append(("project", (None, str(self.project).encode(), "text/plain")))

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

        if not isinstance(self.vex, Unset):
            files.append(("vex", (None, str(self.vex).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project = d.pop("project", UNSET)

        project_name = d.pop("projectName", UNSET)

        project_version = d.pop("projectVersion", UNSET)

        vex = d.pop("vex", UNSET)

        upload_vex_1_body = cls(
            project=project,
            project_name=project_name,
            project_version=project_version,
            vex=vex,
        )

        upload_vex_1_body.additional_properties = d
        return upload_vex_1_body

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

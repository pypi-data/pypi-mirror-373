from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VexSubmitRequest")


@_attrs_define
class VexSubmitRequest:
    """
    Attributes:
        project (str):
        vex (str):
        project_name (Union[Unset, str]):
        project_version (Union[Unset, str]):
    """

    project: str
    vex: str
    project_name: Union[Unset, str] = UNSET
    project_version: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project

        vex = self.vex

        project_name = self.project_name

        project_version = self.project_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "vex": vex,
            }
        )
        if project_name is not UNSET:
            field_dict["projectName"] = project_name
        if project_version is not UNSET:
            field_dict["projectVersion"] = project_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project = d.pop("project")

        vex = d.pop("vex")

        project_name = d.pop("projectName", UNSET)

        project_version = d.pop("projectVersion", UNSET)

        vex_submit_request = cls(
            project=project,
            vex=vex,
            project_name=project_name,
            project_version=project_version,
        )

        vex_submit_request.additional_properties = d
        return vex_submit_request

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

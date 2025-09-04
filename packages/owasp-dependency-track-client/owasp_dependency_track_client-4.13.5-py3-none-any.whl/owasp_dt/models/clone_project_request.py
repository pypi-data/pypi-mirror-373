from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CloneProjectRequest")


@_attrs_define
class CloneProjectRequest:
    """
    Attributes:
        project (str):
        version (str):
        include_tags (Union[Unset, bool]):
        include_properties (Union[Unset, bool]):
        include_dependencies (Union[Unset, bool]):
        include_components (Union[Unset, bool]):
        include_services (Union[Unset, bool]):
        include_audit_history (Union[Unset, bool]):
        include_acl (Union[Unset, bool]):
        include_policy_violations (Union[Unset, bool]):
        make_clone_latest (Union[Unset, bool]):
    """

    project: str
    version: str
    include_tags: Union[Unset, bool] = UNSET
    include_properties: Union[Unset, bool] = UNSET
    include_dependencies: Union[Unset, bool] = UNSET
    include_components: Union[Unset, bool] = UNSET
    include_services: Union[Unset, bool] = UNSET
    include_audit_history: Union[Unset, bool] = UNSET
    include_acl: Union[Unset, bool] = UNSET
    include_policy_violations: Union[Unset, bool] = UNSET
    make_clone_latest: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project

        version = self.version

        include_tags = self.include_tags

        include_properties = self.include_properties

        include_dependencies = self.include_dependencies

        include_components = self.include_components

        include_services = self.include_services

        include_audit_history = self.include_audit_history

        include_acl = self.include_acl

        include_policy_violations = self.include_policy_violations

        make_clone_latest = self.make_clone_latest

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "version": version,
            }
        )
        if include_tags is not UNSET:
            field_dict["includeTags"] = include_tags
        if include_properties is not UNSET:
            field_dict["includeProperties"] = include_properties
        if include_dependencies is not UNSET:
            field_dict["includeDependencies"] = include_dependencies
        if include_components is not UNSET:
            field_dict["includeComponents"] = include_components
        if include_services is not UNSET:
            field_dict["includeServices"] = include_services
        if include_audit_history is not UNSET:
            field_dict["includeAuditHistory"] = include_audit_history
        if include_acl is not UNSET:
            field_dict["includeACL"] = include_acl
        if include_policy_violations is not UNSET:
            field_dict["includePolicyViolations"] = include_policy_violations
        if make_clone_latest is not UNSET:
            field_dict["makeCloneLatest"] = make_clone_latest

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project = d.pop("project")

        version = d.pop("version")

        include_tags = d.pop("includeTags", UNSET)

        include_properties = d.pop("includeProperties", UNSET)

        include_dependencies = d.pop("includeDependencies", UNSET)

        include_components = d.pop("includeComponents", UNSET)

        include_services = d.pop("includeServices", UNSET)

        include_audit_history = d.pop("includeAuditHistory", UNSET)

        include_acl = d.pop("includeACL", UNSET)

        include_policy_violations = d.pop("includePolicyViolations", UNSET)

        make_clone_latest = d.pop("makeCloneLatest", UNSET)

        clone_project_request = cls(
            project=project,
            version=version,
            include_tags=include_tags,
            include_properties=include_properties,
            include_dependencies=include_dependencies,
            include_components=include_components,
            include_services=include_services,
            include_audit_history=include_audit_history,
            include_acl=include_acl,
            include_policy_violations=include_policy_violations,
            make_clone_latest=make_clone_latest,
        )

        clone_project_request.additional_properties = d
        return clone_project_request

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

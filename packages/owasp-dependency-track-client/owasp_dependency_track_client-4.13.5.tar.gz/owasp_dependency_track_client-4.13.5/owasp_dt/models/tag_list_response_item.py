from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TagListResponseItem")


@_attrs_define
class TagListResponseItem:
    """
    Attributes:
        name (str): Name of the tag
        project_count (int): Number of projects assigned to this tag
        collection_project_count (int): Number of collection projects assigned to this tag
        policy_count (int): Number of policies assigned to this tag
        notification_rule_count (int): Number of notification rules assigned to this tag
    """

    name: str
    project_count: int
    collection_project_count: int
    policy_count: int
    notification_rule_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        project_count = self.project_count

        collection_project_count = self.collection_project_count

        policy_count = self.policy_count

        notification_rule_count = self.notification_rule_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "projectCount": project_count,
                "collectionProjectCount": collection_project_count,
                "policyCount": policy_count,
                "notificationRuleCount": notification_rule_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        project_count = d.pop("projectCount")

        collection_project_count = d.pop("collectionProjectCount")

        policy_count = d.pop("policyCount")

        notification_rule_count = d.pop("notificationRuleCount")

        tag_list_response_item = cls(
            name=name,
            project_count=project_count,
            collection_project_count=collection_project_count,
            policy_count=policy_count,
            notification_rule_count=notification_rule_count,
        )

        tag_list_response_item.additional_properties = d
        return tag_list_response_item

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

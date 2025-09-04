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

from ..models.policy_operator import PolicyOperator
from ..models.policy_violation_state import PolicyViolationState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.policy_condition import PolicyCondition
    from ..models.project import Project
    from ..models.tag import Tag


T = TypeVar("T", bound="Policy")


@_attrs_define
class Policy:
    """
    Attributes:
        uuid (UUID):
        name (Union[Unset, str]):
        operator (Union[Unset, PolicyOperator]):
        violation_state (Union[Unset, PolicyViolationState]):
        policy_conditions (Union[Unset, list['PolicyCondition']]):
        projects (Union[Unset, list['Project']]):
        tags (Union[Unset, list['Tag']]):
        include_children (Union[Unset, bool]):
        only_latest_project_version (Union[Unset, bool]):
        global_ (Union[Unset, bool]):
    """

    uuid: UUID
    name: Union[Unset, str] = UNSET
    operator: Union[Unset, PolicyOperator] = UNSET
    violation_state: Union[Unset, PolicyViolationState] = UNSET
    policy_conditions: Union[Unset, list["PolicyCondition"]] = UNSET
    projects: Union[Unset, list["Project"]] = UNSET
    tags: Union[Unset, list["Tag"]] = UNSET
    include_children: Union[Unset, bool] = UNSET
    only_latest_project_version: Union[Unset, bool] = UNSET
    global_: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        name = self.name

        operator: Union[Unset, str] = UNSET
        if not isinstance(self.operator, Unset):
            operator = self.operator.value

        violation_state: Union[Unset, str] = UNSET
        if not isinstance(self.violation_state, Unset):
            violation_state = self.violation_state.value

        policy_conditions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.policy_conditions, Unset):
            policy_conditions = []
            for policy_conditions_item_data in self.policy_conditions:
                policy_conditions_item = policy_conditions_item_data.to_dict()
                policy_conditions.append(policy_conditions_item)

        projects: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.projects, Unset):
            projects = []
            for projects_item_data in self.projects:
                projects_item = projects_item_data.to_dict()
                projects.append(projects_item)

        tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)

        include_children = self.include_children

        only_latest_project_version = self.only_latest_project_version

        global_ = self.global_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if operator is not UNSET:
            field_dict["operator"] = operator
        if violation_state is not UNSET:
            field_dict["violationState"] = violation_state
        if policy_conditions is not UNSET:
            field_dict["policyConditions"] = policy_conditions
        if projects is not UNSET:
            field_dict["projects"] = projects
        if tags is not UNSET:
            field_dict["tags"] = tags
        if include_children is not UNSET:
            field_dict["includeChildren"] = include_children
        if only_latest_project_version is not UNSET:
            field_dict["onlyLatestProjectVersion"] = only_latest_project_version
        if global_ is not UNSET:
            field_dict["global"] = global_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.policy_condition import PolicyCondition
        from ..models.project import Project
        from ..models.tag import Tag

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        name = d.pop("name", UNSET)

        _operator = d.pop("operator", UNSET)
        operator: Union[Unset, PolicyOperator]
        if isinstance(_operator, Unset):
            operator = UNSET
        else:
            operator = PolicyOperator(_operator)

        _violation_state = d.pop("violationState", UNSET)
        violation_state: Union[Unset, PolicyViolationState]
        if isinstance(_violation_state, Unset):
            violation_state = UNSET
        else:
            violation_state = PolicyViolationState(_violation_state)

        policy_conditions = []
        _policy_conditions = d.pop("policyConditions", UNSET)
        for policy_conditions_item_data in _policy_conditions or []:
            policy_conditions_item = PolicyCondition.from_dict(
                policy_conditions_item_data
            )

            policy_conditions.append(policy_conditions_item)

        projects = []
        _projects = d.pop("projects", UNSET)
        for projects_item_data in _projects or []:
            projects_item = Project.from_dict(projects_item_data)

            projects.append(projects_item)

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in _tags or []:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        include_children = d.pop("includeChildren", UNSET)

        only_latest_project_version = d.pop("onlyLatestProjectVersion", UNSET)

        global_ = d.pop("global", UNSET)

        policy = cls(
            uuid=uuid,
            name=name,
            operator=operator,
            violation_state=violation_state,
            policy_conditions=policy_conditions,
            projects=projects,
            tags=tags,
            include_children=include_children,
            only_latest_project_version=only_latest_project_version,
            global_=global_,
        )

        policy.additional_properties = d
        return policy

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

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

from ..models.policy_violation_type import PolicyViolationType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.component import Component
    from ..models.policy_condition import PolicyCondition
    from ..models.project import Project
    from ..models.violation_analysis import ViolationAnalysis


T = TypeVar("T", bound="PolicyViolation")


@_attrs_define
class PolicyViolation:
    """
    Attributes:
        timestamp (int): UNIX epoch timestamp in milliseconds
        uuid (UUID):
        type_ (Union[Unset, PolicyViolationType]):
        project (Union[Unset, Project]):
        component (Union[Unset, Component]):
        policy_condition (Union[Unset, PolicyCondition]):
        text (Union[Unset, str]):
        analysis (Union[Unset, ViolationAnalysis]):
    """

    timestamp: int
    uuid: UUID
    type_: Union[Unset, PolicyViolationType] = UNSET
    project: Union[Unset, "Project"] = UNSET
    component: Union[Unset, "Component"] = UNSET
    policy_condition: Union[Unset, "PolicyCondition"] = UNSET
    text: Union[Unset, str] = UNSET
    analysis: Union[Unset, "ViolationAnalysis"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timestamp = self.timestamp

        uuid = str(self.uuid)

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        project: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.project, Unset):
            project = self.project.to_dict()

        component: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.component, Unset):
            component = self.component.to_dict()

        policy_condition: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.policy_condition, Unset):
            policy_condition = self.policy_condition.to_dict()

        text = self.text

        analysis: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.analysis, Unset):
            analysis = self.analysis.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timestamp": timestamp,
                "uuid": uuid,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if project is not UNSET:
            field_dict["project"] = project
        if component is not UNSET:
            field_dict["component"] = component
        if policy_condition is not UNSET:
            field_dict["policyCondition"] = policy_condition
        if text is not UNSET:
            field_dict["text"] = text
        if analysis is not UNSET:
            field_dict["analysis"] = analysis

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.component import Component
        from ..models.policy_condition import PolicyCondition
        from ..models.project import Project
        from ..models.violation_analysis import ViolationAnalysis

        d = dict(src_dict)
        timestamp = d.pop("timestamp")

        uuid = UUID(d.pop("uuid"))

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, PolicyViolationType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = PolicyViolationType(_type_)

        _project = d.pop("project", UNSET)
        project: Union[Unset, Project]
        if isinstance(_project, Unset):
            project = UNSET
        else:
            project = Project.from_dict(_project)

        _component = d.pop("component", UNSET)
        component: Union[Unset, Component]
        if isinstance(_component, Unset):
            component = UNSET
        else:
            component = Component.from_dict(_component)

        _policy_condition = d.pop("policyCondition", UNSET)
        policy_condition: Union[Unset, PolicyCondition]
        if isinstance(_policy_condition, Unset):
            policy_condition = UNSET
        else:
            policy_condition = PolicyCondition.from_dict(_policy_condition)

        text = d.pop("text", UNSET)

        _analysis = d.pop("analysis", UNSET)
        analysis: Union[Unset, ViolationAnalysis]
        if isinstance(_analysis, Unset):
            analysis = UNSET
        else:
            analysis = ViolationAnalysis.from_dict(_analysis)

        policy_violation = cls(
            timestamp=timestamp,
            uuid=uuid,
            type_=type_,
            project=project,
            component=component,
            policy_condition=policy_condition,
            text=text,
            analysis=analysis,
        )

        policy_violation.additional_properties = d
        return policy_violation

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

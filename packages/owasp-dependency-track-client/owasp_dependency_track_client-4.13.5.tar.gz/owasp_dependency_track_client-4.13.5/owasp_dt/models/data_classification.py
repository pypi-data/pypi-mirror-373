from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_classification_direction import DataClassificationDirection
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataClassification")


@_attrs_define
class DataClassification:
    """
    Attributes:
        direction (Union[Unset, DataClassificationDirection]):
        name (Union[Unset, str]):
    """

    direction: Union[Unset, DataClassificationDirection] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        direction: Union[Unset, str] = UNSET
        if not isinstance(self.direction, Unset):
            direction = self.direction.value

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if direction is not UNSET:
            field_dict["direction"] = direction
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _direction = d.pop("direction", UNSET)
        direction: Union[Unset, DataClassificationDirection]
        if isinstance(_direction, Unset):
            direction = UNSET
        else:
            direction = DataClassificationDirection(_direction)

        name = d.pop("name", UNSET)

        data_classification = cls(
            direction=direction,
            name=name,
        )

        data_classification.additional_properties = d
        return data_classification

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

from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.component_property_property_type import ComponentPropertyPropertyType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ComponentProperty")


@_attrs_define
class ComponentProperty:
    """
    Attributes:
        property_type (ComponentPropertyPropertyType):
        uuid (UUID):
        group_name (Union[Unset, str]):
        property_name (Union[Unset, str]):
        property_value (Union[Unset, str]):
        description (Union[Unset, str]):
    """

    property_type: ComponentPropertyPropertyType
    uuid: UUID
    group_name: Union[Unset, str] = UNSET
    property_name: Union[Unset, str] = UNSET
    property_value: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        property_type = self.property_type.value

        uuid = str(self.uuid)

        group_name = self.group_name

        property_name = self.property_name

        property_value = self.property_value

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "propertyType": property_type,
                "uuid": uuid,
            }
        )
        if group_name is not UNSET:
            field_dict["groupName"] = group_name
        if property_name is not UNSET:
            field_dict["propertyName"] = property_name
        if property_value is not UNSET:
            field_dict["propertyValue"] = property_value
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        property_type = ComponentPropertyPropertyType(d.pop("propertyType"))

        uuid = UUID(d.pop("uuid"))

        group_name = d.pop("groupName", UNSET)

        property_name = d.pop("propertyName", UNSET)

        property_value = d.pop("propertyValue", UNSET)

        description = d.pop("description", UNSET)

        component_property = cls(
            property_type=property_type,
            uuid=uuid,
            group_name=group_name,
            property_name=property_name,
            property_value=property_value,
            description=description,
        )

        component_property.additional_properties = d
        return component_property

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

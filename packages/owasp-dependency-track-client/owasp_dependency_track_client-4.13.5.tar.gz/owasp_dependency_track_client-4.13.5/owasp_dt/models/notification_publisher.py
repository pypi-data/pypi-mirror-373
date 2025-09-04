from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NotificationPublisher")


@_attrs_define
class NotificationPublisher:
    """
    Attributes:
        name (str):
        publisher_class (str):
        template_mime_type (str):
        uuid (UUID):
        description (Union[Unset, str]):
        template (Union[Unset, str]):
        default_publisher (Union[Unset, bool]):
    """

    name: str
    publisher_class: str
    template_mime_type: str
    uuid: UUID
    description: Union[Unset, str] = UNSET
    template: Union[Unset, str] = UNSET
    default_publisher: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        publisher_class = self.publisher_class

        template_mime_type = self.template_mime_type

        uuid = str(self.uuid)

        description = self.description

        template = self.template

        default_publisher = self.default_publisher

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "publisherClass": publisher_class,
                "templateMimeType": template_mime_type,
                "uuid": uuid,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if template is not UNSET:
            field_dict["template"] = template
        if default_publisher is not UNSET:
            field_dict["defaultPublisher"] = default_publisher

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        publisher_class = d.pop("publisherClass")

        template_mime_type = d.pop("templateMimeType")

        uuid = UUID(d.pop("uuid"))

        description = d.pop("description", UNSET)

        template = d.pop("template", UNSET)

        default_publisher = d.pop("defaultPublisher", UNSET)

        notification_publisher = cls(
            name=name,
            publisher_class=publisher_class,
            template_mime_type=template_mime_type,
            uuid=uuid,
            description=description,
            template=template,
            default_publisher=default_publisher,
        )

        notification_publisher.additional_properties = d
        return notification_publisher

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

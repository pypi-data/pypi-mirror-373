from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organizational_contact import OrganizationalContact


T = TypeVar("T", bound="OrganizationalEntity")


@_attrs_define
class OrganizationalEntity:
    """
    Attributes:
        name (Union[Unset, str]):
        urls (Union[Unset, list[str]]):
        contacts (Union[Unset, list['OrganizationalContact']]):
    """

    name: Union[Unset, str] = UNSET
    urls: Union[Unset, list[str]] = UNSET
    contacts: Union[Unset, list["OrganizationalContact"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        urls: Union[Unset, list[str]] = UNSET
        if not isinstance(self.urls, Unset):
            urls = self.urls

        contacts: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.contacts, Unset):
            contacts = []
            for contacts_item_data in self.contacts:
                contacts_item = contacts_item_data.to_dict()
                contacts.append(contacts_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if urls is not UNSET:
            field_dict["urls"] = urls
        if contacts is not UNSET:
            field_dict["contacts"] = contacts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organizational_contact import OrganizationalContact

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        urls = cast(list[str], d.pop("urls", UNSET))

        contacts = []
        _contacts = d.pop("contacts", UNSET)
        for contacts_item_data in _contacts or []:
            contacts_item = OrganizationalContact.from_dict(contacts_item_data)

            contacts.append(contacts_item)

        organizational_entity = cls(
            name=name,
            urls=urls,
            contacts=contacts,
        )

        organizational_entity.additional_properties = d
        return organizational_entity

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

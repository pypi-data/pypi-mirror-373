from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organizational_contact import OrganizationalContact
    from ..models.organizational_entity import OrganizationalEntity


T = TypeVar("T", bound="ProjectMetadata")


@_attrs_define
class ProjectMetadata:
    """
    Attributes:
        supplier (Union[Unset, OrganizationalEntity]):
        authors (Union[Unset, list['OrganizationalContact']]):
    """

    supplier: Union[Unset, "OrganizationalEntity"] = UNSET
    authors: Union[Unset, list["OrganizationalContact"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        supplier: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.supplier, Unset):
            supplier = self.supplier.to_dict()

        authors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.authors, Unset):
            authors = []
            for authors_item_data in self.authors:
                authors_item = authors_item_data.to_dict()
                authors.append(authors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if supplier is not UNSET:
            field_dict["supplier"] = supplier
        if authors is not UNSET:
            field_dict["authors"] = authors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organizational_contact import OrganizationalContact
        from ..models.organizational_entity import OrganizationalEntity

        d = dict(src_dict)
        _supplier = d.pop("supplier", UNSET)
        supplier: Union[Unset, OrganizationalEntity]
        if isinstance(_supplier, Unset):
            supplier = UNSET
        else:
            supplier = OrganizationalEntity.from_dict(_supplier)

        authors = []
        _authors = d.pop("authors", UNSET)
        for authors_item_data in _authors or []:
            authors_item = OrganizationalContact.from_dict(authors_item_data)

            authors.append(authors_item)

        project_metadata = cls(
            supplier=supplier,
            authors=authors,
        )

        project_metadata.additional_properties = d
        return project_metadata

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

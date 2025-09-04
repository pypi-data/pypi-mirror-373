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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.oidc_group import OidcGroup


T = TypeVar("T", bound="MappedOidcGroup")


@_attrs_define
class MappedOidcGroup:
    """
    Attributes:
        uuid (UUID):
        group (Union[Unset, OidcGroup]):
    """

    uuid: UUID
    group: Union[Unset, "OidcGroup"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        group: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.group, Unset):
            group = self.group.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
            }
        )
        if group is not UNSET:
            field_dict["group"] = group

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.oidc_group import OidcGroup

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        _group = d.pop("group", UNSET)
        group: Union[Unset, OidcGroup]
        if isinstance(_group, Unset):
            group = UNSET
        else:
            group = OidcGroup.from_dict(_group)

        mapped_oidc_group = cls(
            uuid=uuid,
            group=group,
        )

        mapped_oidc_group.additional_properties = d
        return mapped_oidc_group

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

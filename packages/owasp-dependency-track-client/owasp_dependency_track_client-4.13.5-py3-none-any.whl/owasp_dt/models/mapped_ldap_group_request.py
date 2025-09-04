from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MappedLdapGroupRequest")


@_attrs_define
class MappedLdapGroupRequest:
    """
    Attributes:
        team (str):
        dn (str):
    """

    team: str
    dn: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team = self.team

        dn = self.dn

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "team": team,
                "dn": dn,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team = d.pop("team")

        dn = d.pop("dn")

        mapped_ldap_group_request = cls(
            team=team,
            dn=dn,
        )

        mapped_ldap_group_request.additional_properties = d
        return mapped_ldap_group_request

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

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
    from ..models.api_key import ApiKey
    from ..models.ldap_user import LdapUser
    from ..models.managed_user import ManagedUser
    from ..models.mapped_ldap_group import MappedLdapGroup
    from ..models.mapped_oidc_group import MappedOidcGroup
    from ..models.oidc_user import OidcUser
    from ..models.permission import Permission


T = TypeVar("T", bound="Team")


@_attrs_define
class Team:
    """
    Attributes:
        uuid (UUID):
        name (Union[Unset, str]):
        api_keys (Union[Unset, list['ApiKey']]):
        ldap_users (Union[Unset, list['LdapUser']]):
        managed_users (Union[Unset, list['ManagedUser']]):
        oidc_users (Union[Unset, list['OidcUser']]):
        mapped_ldap_groups (Union[Unset, list['MappedLdapGroup']]):
        mapped_oidc_groups (Union[Unset, list['MappedOidcGroup']]):
        permissions (Union[Unset, list['Permission']]):
    """

    uuid: UUID
    name: Union[Unset, str] = UNSET
    api_keys: Union[Unset, list["ApiKey"]] = UNSET
    ldap_users: Union[Unset, list["LdapUser"]] = UNSET
    managed_users: Union[Unset, list["ManagedUser"]] = UNSET
    oidc_users: Union[Unset, list["OidcUser"]] = UNSET
    mapped_ldap_groups: Union[Unset, list["MappedLdapGroup"]] = UNSET
    mapped_oidc_groups: Union[Unset, list["MappedOidcGroup"]] = UNSET
    permissions: Union[Unset, list["Permission"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        name = self.name

        api_keys: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.api_keys, Unset):
            api_keys = []
            for api_keys_item_data in self.api_keys:
                api_keys_item = api_keys_item_data.to_dict()
                api_keys.append(api_keys_item)

        ldap_users: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.ldap_users, Unset):
            ldap_users = []
            for ldap_users_item_data in self.ldap_users:
                ldap_users_item = ldap_users_item_data.to_dict()
                ldap_users.append(ldap_users_item)

        managed_users: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.managed_users, Unset):
            managed_users = []
            for managed_users_item_data in self.managed_users:
                managed_users_item = managed_users_item_data.to_dict()
                managed_users.append(managed_users_item)

        oidc_users: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.oidc_users, Unset):
            oidc_users = []
            for oidc_users_item_data in self.oidc_users:
                oidc_users_item = oidc_users_item_data.to_dict()
                oidc_users.append(oidc_users_item)

        mapped_ldap_groups: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.mapped_ldap_groups, Unset):
            mapped_ldap_groups = []
            for mapped_ldap_groups_item_data in self.mapped_ldap_groups:
                mapped_ldap_groups_item = mapped_ldap_groups_item_data.to_dict()
                mapped_ldap_groups.append(mapped_ldap_groups_item)

        mapped_oidc_groups: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.mapped_oidc_groups, Unset):
            mapped_oidc_groups = []
            for mapped_oidc_groups_item_data in self.mapped_oidc_groups:
                mapped_oidc_groups_item = mapped_oidc_groups_item_data.to_dict()
                mapped_oidc_groups.append(mapped_oidc_groups_item)

        permissions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = []
            for permissions_item_data in self.permissions:
                permissions_item = permissions_item_data.to_dict()
                permissions.append(permissions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if api_keys is not UNSET:
            field_dict["apiKeys"] = api_keys
        if ldap_users is not UNSET:
            field_dict["ldapUsers"] = ldap_users
        if managed_users is not UNSET:
            field_dict["managedUsers"] = managed_users
        if oidc_users is not UNSET:
            field_dict["oidcUsers"] = oidc_users
        if mapped_ldap_groups is not UNSET:
            field_dict["mappedLdapGroups"] = mapped_ldap_groups
        if mapped_oidc_groups is not UNSET:
            field_dict["mappedOidcGroups"] = mapped_oidc_groups
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key import ApiKey
        from ..models.ldap_user import LdapUser
        from ..models.managed_user import ManagedUser
        from ..models.mapped_ldap_group import MappedLdapGroup
        from ..models.mapped_oidc_group import MappedOidcGroup
        from ..models.oidc_user import OidcUser
        from ..models.permission import Permission

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        name = d.pop("name", UNSET)

        api_keys = []
        _api_keys = d.pop("apiKeys", UNSET)
        for api_keys_item_data in _api_keys or []:
            api_keys_item = ApiKey.from_dict(api_keys_item_data)

            api_keys.append(api_keys_item)

        ldap_users = []
        _ldap_users = d.pop("ldapUsers", UNSET)
        for ldap_users_item_data in _ldap_users or []:
            ldap_users_item = LdapUser.from_dict(ldap_users_item_data)

            ldap_users.append(ldap_users_item)

        managed_users = []
        _managed_users = d.pop("managedUsers", UNSET)
        for managed_users_item_data in _managed_users or []:
            managed_users_item = ManagedUser.from_dict(managed_users_item_data)

            managed_users.append(managed_users_item)

        oidc_users = []
        _oidc_users = d.pop("oidcUsers", UNSET)
        for oidc_users_item_data in _oidc_users or []:
            oidc_users_item = OidcUser.from_dict(oidc_users_item_data)

            oidc_users.append(oidc_users_item)

        mapped_ldap_groups = []
        _mapped_ldap_groups = d.pop("mappedLdapGroups", UNSET)
        for mapped_ldap_groups_item_data in _mapped_ldap_groups or []:
            mapped_ldap_groups_item = MappedLdapGroup.from_dict(
                mapped_ldap_groups_item_data
            )

            mapped_ldap_groups.append(mapped_ldap_groups_item)

        mapped_oidc_groups = []
        _mapped_oidc_groups = d.pop("mappedOidcGroups", UNSET)
        for mapped_oidc_groups_item_data in _mapped_oidc_groups or []:
            mapped_oidc_groups_item = MappedOidcGroup.from_dict(
                mapped_oidc_groups_item_data
            )

            mapped_oidc_groups.append(mapped_oidc_groups_item)

        permissions = []
        _permissions = d.pop("permissions", UNSET)
        for permissions_item_data in _permissions or []:
            permissions_item = Permission.from_dict(permissions_item_data)

            permissions.append(permissions_item)

        team = cls(
            uuid=uuid,
            name=name,
            api_keys=api_keys,
            ldap_users=ldap_users,
            managed_users=managed_users,
            oidc_users=oidc_users,
            mapped_ldap_groups=mapped_ldap_groups,
            mapped_oidc_groups=mapped_oidc_groups,
            permissions=permissions,
        )

        team.additional_properties = d
        return team

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

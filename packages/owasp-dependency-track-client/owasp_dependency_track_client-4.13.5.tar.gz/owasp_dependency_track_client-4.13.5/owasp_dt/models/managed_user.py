import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.permission import Permission
    from ..models.team import Team


T = TypeVar("T", bound="ManagedUser")


@_attrs_define
class ManagedUser:
    """
    Attributes:
        last_password_change (datetime.datetime):
        username (Union[Unset, str]):
        fullname (Union[Unset, str]):
        email (Union[Unset, str]):
        suspended (Union[Unset, bool]):
        force_password_change (Union[Unset, bool]):
        non_expiry_password (Union[Unset, bool]):
        teams (Union[Unset, list['Team']]):
        permissions (Union[Unset, list['Permission']]):
        new_password (Union[Unset, str]):
        confirm_password (Union[Unset, str]):
    """

    last_password_change: datetime.datetime
    username: Union[Unset, str] = UNSET
    fullname: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    suspended: Union[Unset, bool] = UNSET
    force_password_change: Union[Unset, bool] = UNSET
    non_expiry_password: Union[Unset, bool] = UNSET
    teams: Union[Unset, list["Team"]] = UNSET
    permissions: Union[Unset, list["Permission"]] = UNSET
    new_password: Union[Unset, str] = UNSET
    confirm_password: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        last_password_change = self.last_password_change.isoformat()

        username = self.username

        fullname = self.fullname

        email = self.email

        suspended = self.suspended

        force_password_change = self.force_password_change

        non_expiry_password = self.non_expiry_password

        teams: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.teams, Unset):
            teams = []
            for teams_item_data in self.teams:
                teams_item = teams_item_data.to_dict()
                teams.append(teams_item)

        permissions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = []
            for permissions_item_data in self.permissions:
                permissions_item = permissions_item_data.to_dict()
                permissions.append(permissions_item)

        new_password = self.new_password

        confirm_password = self.confirm_password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "lastPasswordChange": last_password_change,
            }
        )
        if username is not UNSET:
            field_dict["username"] = username
        if fullname is not UNSET:
            field_dict["fullname"] = fullname
        if email is not UNSET:
            field_dict["email"] = email
        if suspended is not UNSET:
            field_dict["suspended"] = suspended
        if force_password_change is not UNSET:
            field_dict["forcePasswordChange"] = force_password_change
        if non_expiry_password is not UNSET:
            field_dict["nonExpiryPassword"] = non_expiry_password
        if teams is not UNSET:
            field_dict["teams"] = teams
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if new_password is not UNSET:
            field_dict["newPassword"] = new_password
        if confirm_password is not UNSET:
            field_dict["confirmPassword"] = confirm_password

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.permission import Permission
        from ..models.team import Team

        d = dict(src_dict)
        last_password_change = isoparse(d.pop("lastPasswordChange"))

        username = d.pop("username", UNSET)

        fullname = d.pop("fullname", UNSET)

        email = d.pop("email", UNSET)

        suspended = d.pop("suspended", UNSET)

        force_password_change = d.pop("forcePasswordChange", UNSET)

        non_expiry_password = d.pop("nonExpiryPassword", UNSET)

        teams = []
        _teams = d.pop("teams", UNSET)
        for teams_item_data in _teams or []:
            teams_item = Team.from_dict(teams_item_data)

            teams.append(teams_item)

        permissions = []
        _permissions = d.pop("permissions", UNSET)
        for permissions_item_data in _permissions or []:
            permissions_item = Permission.from_dict(permissions_item_data)

            permissions.append(permissions_item)

        new_password = d.pop("newPassword", UNSET)

        confirm_password = d.pop("confirmPassword", UNSET)

        managed_user = cls(
            last_password_change=last_password_change,
            username=username,
            fullname=fullname,
            email=email,
            suspended=suspended,
            force_password_change=force_password_change,
            non_expiry_password=non_expiry_password,
            teams=teams,
            permissions=permissions,
            new_password=new_password,
            confirm_password=confirm_password,
        )

        managed_user.additional_properties = d
        return managed_user

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

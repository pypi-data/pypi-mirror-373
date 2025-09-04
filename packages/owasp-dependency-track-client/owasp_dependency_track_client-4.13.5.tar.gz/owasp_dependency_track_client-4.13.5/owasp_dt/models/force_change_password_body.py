from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ForceChangePasswordBody")


@_attrs_define
class ForceChangePasswordBody:
    """
    Attributes:
        username (Union[Unset, str]):
        password (Union[Unset, str]):
        new_password (Union[Unset, str]):
        confirm_password (Union[Unset, str]):
    """

    username: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    new_password: Union[Unset, str] = UNSET
    confirm_password: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        password = self.password

        new_password = self.new_password

        confirm_password = self.confirm_password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if password is not UNSET:
            field_dict["password"] = password
        if new_password is not UNSET:
            field_dict["newPassword"] = new_password
        if confirm_password is not UNSET:
            field_dict["confirmPassword"] = confirm_password

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username", UNSET)

        password = d.pop("password", UNSET)

        new_password = d.pop("newPassword", UNSET)

        confirm_password = d.pop("confirmPassword", UNSET)

        force_change_password_body = cls(
            username=username,
            password=password,
            new_password=new_password,
            confirm_password=confirm_password,
        )

        force_change_password_body.additional_properties = d
        return force_change_password_body

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

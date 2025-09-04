import datetime
from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiKey")


@_attrs_define
class ApiKey:
    """
    Attributes:
        comment (Union[Unset, str]):
        created (Union[Unset, datetime.datetime]):
        last_used (Union[Unset, datetime.datetime]):
        public_id (Union[Unset, str]):
        key (Union[Unset, str]):
        legacy (Union[Unset, bool]):
        masked_key (Union[Unset, str]):
    """

    comment: Union[Unset, str] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    last_used: Union[Unset, datetime.datetime] = UNSET
    public_id: Union[Unset, str] = UNSET
    key: Union[Unset, str] = UNSET
    legacy: Union[Unset, bool] = UNSET
    masked_key: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        comment = self.comment

        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        last_used: Union[Unset, str] = UNSET
        if not isinstance(self.last_used, Unset):
            last_used = self.last_used.isoformat()

        public_id = self.public_id

        key = self.key

        legacy = self.legacy

        masked_key = self.masked_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if comment is not UNSET:
            field_dict["comment"] = comment
        if created is not UNSET:
            field_dict["created"] = created
        if last_used is not UNSET:
            field_dict["lastUsed"] = last_used
        if public_id is not UNSET:
            field_dict["publicId"] = public_id
        if key is not UNSET:
            field_dict["key"] = key
        if legacy is not UNSET:
            field_dict["legacy"] = legacy
        if masked_key is not UNSET:
            field_dict["maskedKey"] = masked_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        comment = d.pop("comment", UNSET)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = isoparse(_created)

        _last_used = d.pop("lastUsed", UNSET)
        last_used: Union[Unset, datetime.datetime]
        if isinstance(_last_used, Unset):
            last_used = UNSET
        else:
            last_used = isoparse(_last_used)

        public_id = d.pop("publicId", UNSET)

        key = d.pop("key", UNSET)

        legacy = d.pop("legacy", UNSET)

        masked_key = d.pop("maskedKey", UNSET)

        api_key = cls(
            comment=comment,
            created=created,
            last_used=last_used,
            public_id=public_id,
            key=key,
            legacy=legacy,
            masked_key=masked_key,
        )

        api_key.additional_properties = d
        return api_key

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
